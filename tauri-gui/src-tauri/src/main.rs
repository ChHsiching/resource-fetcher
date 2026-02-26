// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::io::{BufRead, BufReader};
use std::process::{Command, Stdio};
use std::sync::mpsc;
use std::thread;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .invoke_handler(tauri::generate_handler![
            greet,
            get_python_info,
            download_album,
            download_song,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

// Import the Emitter trait for event emission
use tauri::Emitter;

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
fn get_python_info() -> Result<PythonInfo, String> {
    // Get the path to the Python venv
    let venv_path = if cfg!(debug_assertions) {
        // Development: relative to the Tauri app
        let exe_dir = std::env::current_exe()
            .map_err(|e| format!("Failed to get exe path: {}", e))?;

        exe_dir.parent()
            .and_then(|p| p.parent())
            .ok_or("Failed to get project root")?
            .join(".venv")
    } else {
        // Production: will be in the app's Resources directory
        let exe_dir = std::env::current_exe()
            .map_err(|e| format!("Failed to get exe path: {}", e))?;

        exe_dir.parent()
            .ok_or("Failed to get app directory")?
            .join("Resources")
            .join("python")
    };

    // Get platform-specific python executable
    let python_exec = if cfg!(windows) {
        venv_path.join("Scripts").join("python.exe")
    } else {
        venv_path.join("bin").join("python")
    };

    // Get CLI executable path with support for multiple deployment scenarios
    let cli_exec = if cfg!(debug_assertions) {
        // Development: look in dist directory
        let exe_dir = std::env::current_exe()
            .map_err(|e| format!("Failed to get exe path: {}", e))?;

        let project_root = exe_dir
            .parent()
            .and_then(|p| p.parent())
            .ok_or("Failed to get project root")?;

        let cli_dir = project_root.join("dist");
        if cfg!(windows) {
            cli_dir.join("resource-fetcher.exe")
        } else {
            cli_dir.join("resource-fetcher")
        }
    } else {
        // Production: try multiple locations
        let exe_dir = std::env::current_exe()
            .map_err(|e| format!("Failed to get exe path: {}", e))?;

        let app_dir = exe_dir
            .parent()
            .ok_or("Failed to get app directory")?;

        // Scenario 1: Portable package - CLI in same directory as GUI
        let portable_cli = if cfg!(windows) {
            app_dir.join("resource-fetcher.exe")
        } else {
            app_dir.join("resource-fetcher")
        };

        if portable_cli.exists() {
            portable_cli
        } else {
            // Scenario 2: Installed version - CLI in Resources/cli/
            let cli_dir = app_dir.join("Resources").join("cli");
            if cfg!(windows) {
                cli_dir.join("resource-fetcher.exe")
            } else {
                cli_dir.join("resource-fetcher")
            }
        }
    };

    Ok(PythonInfo {
        python_path: python_exec.to_string_lossy().to_string(),
        cli_path: cli_exec.to_string_lossy().to_string(),
        venv_path: venv_path.to_string_lossy().to_string(),
    })
}

#[tauri::command]
fn download_album(
    url: String,
    output_dir: String,
    limit: Option<usize>,
    timeout: u32,
    retries: u32,
    delay: f64,
    overwrite: bool,
    renumber: bool,
    verbose: bool,
    python_info: PythonInfo,
    app: tauri::AppHandle,
) -> Result<String, String> {
    let mut cmd = Command::new(&python_info.python_path);

    // Build CLI command arguments
    cmd.arg("-m")
        .arg("resource_fetcher_cli")
        .arg("--url")
        .arg(&url)
        .arg("--output")
        .arg(&output_dir)
        .arg("--timeout")
        .arg(timeout.to_string())
        .arg("--retries")
        .arg(retries.to_string())
        .arg("--delay")
        .arg(delay.to_string());

    if let Some(n) = limit {
        cmd.arg("--limit").arg(n.to_string());
    }

    if overwrite {
        cmd.arg("--overwrite");
    }

    if renumber {
        cmd.arg("--renumber");
    }

    if verbose {
        cmd.arg("--verbose");
    }

    // Setup for streaming output
    cmd.stdout(Stdio::piped())
        .stderr(Stdio::piped());

    // Spawn the subprocess
    let mut child = cmd
        .spawn()
        .map_err(|e| format!("Failed to spawn CLI process: {}", e))?;

    // Get stdout and stderr handles
    let stdout = child
        .stdout
        .take()
        .ok_or("Failed to capture stdout")?;
    let stderr = child
        .stderr
        .take()
        .ok_or("Failed to capture stderr")?;

    // Create channels for sending events back to main thread
    let (tx, rx) = mpsc::channel::<ProgressEvent>();

    // Spawn thread to read stdout
    let stdout_reader = BufReader::new(stdout);
    let tx_clone = tx.clone();
    thread::spawn(move || {
        for line in stdout_reader.lines() {
            if let Ok(line) = line {
                // Check for progress markers
                if line.starts_with(">>>PROGRESS:") {
                    if let Some(json_str) = line.strip_prefix(">>>PROGRESS:") {
                        if let Ok(event) = parse_progress_event(json_str) {
                            tx_clone.send(event).ok();
                        }
                    }
                }
            }
        }
    });

    // Spawn thread to read stderr (where progress markers are written)
    let stderr_reader = BufReader::new(stderr);
    thread::spawn(move || {
        for line in stderr_reader.lines() {
            if let Ok(line) = line {
                // Check for progress markers
                if line.starts_with(">>>PROGRESS:") {
                    if let Some(json_str) = line.strip_prefix(">>>PROGRESS:") {
                        if let Ok(event) = parse_progress_event(json_str) {
                            tx.send(event).ok();
                        }
                    }
                }
            }
        }
    });

    // Listen for progress events and emit to frontend
    let app_clone = app.clone();
    thread::spawn(move || {
        while let Ok(event) = rx.recv() {
            match event {
                ProgressEvent::AlbumStart { title, source, total } => {
                    app_clone.emit("download-progress", serde_json::json!({
                        "type": "album_start",
                        "title": title,
                        "source": source,
                        "total": total
                    })).ok();
                }
                ProgressEvent::SongStart { index, total, title } => {
                    app_clone.emit("download-progress", serde_json::json!({
                        "type": "song_start",
                        "index": index,
                        "total": total,
                        "title": title
                    })).ok();
                }
                ProgressEvent::SongComplete { index, title, status, size, message } => {
                    app_clone.emit("download-progress", serde_json::json!({
                        "type": "song_complete",
                        "index": index,
                        "title": title,
                        "status": status,
                        "size": size,
                        "message": message
                    })).ok();
                }
                ProgressEvent::AlbumComplete { success, failed, skipped, total } => {
                    app_clone.emit("download-complete", serde_json::json!({
                        "type": "album_complete",
                        "success": success,
                        "failed": failed,
                        "skipped": skipped,
                        "total": total
                    })).ok();
                }
                ProgressEvent::Error { message } => {
                    app_clone.emit("download-error", serde_json::json!({
                        "type": "error",
                        "message": message
                    })).ok();
                }
            }
        }
    });

    // Wait for process to complete
    let status = child
        .wait()
        .map_err(|e| format!("Failed to wait for CLI process: {}", e))?;

    if status.success() {
        Ok("Download completed".to_string())
    } else {
        Err(format!("Download failed with exit code: {:?}", status.code()))
    }
}

#[tauri::command]
fn download_song(
    url: String,
    output_dir: String,
    timeout: u32,
    retries: u32,
    delay: f64,
    renumber: bool,
    verbose: bool,
    python_info: PythonInfo,
    app: tauri::AppHandle,
) -> Result<String, String> {
    let mut cmd = Command::new(&python_info.python_path);

    // Build CLI command arguments
    cmd.arg("-m")
        .arg("resource_fetcher_cli")
        .arg("--url")
        .arg(&url)
        .arg("--output")
        .arg(&output_dir)
        .arg("--timeout")
        .arg(timeout.to_string())
        .arg("--retries")
        .arg(retries.to_string())
        .arg("--delay")
        .arg(delay.to_string());

    if renumber {
        cmd.arg("--renumber");
    }

    if verbose {
        cmd.arg("--verbose");
    }

    // Setup for streaming output
    cmd.stdout(Stdio::piped())
        .stderr(Stdio::piped());

    // Spawn the subprocess
    let mut child = cmd
        .spawn()
        .map_err(|e| format!("Failed to spawn CLI process: {}", e))?;

    // Get stdout and stderr handles
    let stdout = child
        .stdout
        .take()
        .ok_or("Failed to capture stdout")?;
    let stderr = child
        .stderr
        .take()
        .ok_or("Failed to capture stderr")?;

    // Create channels for sending events back to main thread
    let (tx, rx) = mpsc::channel::<ProgressEvent>();

    // Spawn thread to read stdout
    let stdout_reader = BufReader::new(stdout);
    let tx_clone = tx.clone();
    thread::spawn(move || {
        for line in stdout_reader.lines() {
            if let Ok(line) = line {
                if line.starts_with(">>>PROGRESS:") {
                    if let Some(json_str) = line.strip_prefix(">>>PROGRESS:") {
                        if let Ok(event) = parse_progress_event(json_str) {
                            tx_clone.send(event).ok();
                        }
                    }
                }
            }
        }
    });

    // Spawn thread to read stderr
    let stderr_reader = BufReader::new(stderr);
    thread::spawn(move || {
        for line in stderr_reader.lines() {
            if let Ok(line) = line {
                if line.starts_with(">>>PROGRESS:") {
                    if let Some(json_str) = line.strip_prefix(">>>PROGRESS:") {
                        if let Ok(event) = parse_progress_event(json_str) {
                            tx.send(event).ok();
                        }
                    }
                }
            }
        }
    });

    // Listen for progress events and emit to frontend
    let app_clone = app.clone();
    thread::spawn(move || {
        while let Ok(event) = rx.recv() {
            match event {
                ProgressEvent::AlbumStart { title, source, total } => {
                    app_clone.emit("download-progress", serde_json::json!({
                        "type": "album_start",
                        "title": title,
                        "source": source,
                        "total": total
                    })).ok();
                }
                ProgressEvent::SongStart { index, total, title } => {
                    app_clone.emit("download-progress", serde_json::json!({
                        "type": "song_start",
                        "index": index,
                        "total": total,
                        "title": title
                    })).ok();
                }
                ProgressEvent::SongComplete { index, title, status, size, message } => {
                    app_clone.emit("download-progress", serde_json::json!({
                        "type": "song_complete",
                        "index": index,
                        "title": title,
                        "status": status,
                        "size": size,
                        "message": message
                    })).ok();
                }
                ProgressEvent::AlbumComplete { success, failed, skipped, total } => {
                    app_clone.emit("download-complete", serde_json::json!({
                        "type": "album_complete",
                        "success": success,
                        "failed": failed,
                        "skipped": skipped,
                        "total": total
                    })).ok();
                }
                ProgressEvent::Error { message } => {
                    app_clone.emit("download-error", serde_json::json!({
                        "type": "error",
                        "message": message
                    })).ok();
                }
            }
        }
    });

    // Wait for process to complete
    let status = child
        .wait()
        .map_err(|e| format!("Failed to wait for CLI process: {}", e))?;

    if status.success() {
        Ok("Download completed".to_string())
    } else {
        Err(format!("Download failed with exit code: {:?}", status.code()))
    }
}

/// Parse a progress event JSON string
fn parse_progress_event(json_str: &str) -> Result<ProgressEvent, String> {
    use serde_json::Value;

    let v: Value = serde_json::from_str(json_str)
        .map_err(|e| format!("Failed to parse JSON: {}", e))?;

    let event_type = v.get("type")
        .and_then(|t| t.as_str())
        .ok_or("Missing event type")?;

    match event_type {
        "album_start" => {
            let title = v.get("title").and_then(|t| t.as_str()).unwrap_or("").to_string();
            let source = v.get("source").and_then(|s| s.as_str()).unwrap_or("").to_string();
            let total = v.get("total").and_then(|t| t.as_u64()).unwrap_or(0) as usize;
            Ok(ProgressEvent::AlbumStart { title, source, total })
        }
        "song_start" => {
            let index = v.get("index").and_then(|i| i.as_u64()).unwrap_or(0) as usize;
            let total = v.get("total").and_then(|t| t.as_u64()).unwrap_or(0) as usize;
            let title = v.get("title").and_then(|t| t.as_str()).unwrap_or("").to_string();
            Ok(ProgressEvent::SongStart { index, total, title })
        }
        "song_complete" => {
            let index = v.get("index").and_then(|i| i.as_u64()).unwrap_or(0) as usize;
            let title = v.get("title").and_then(|t| t.as_str()).unwrap_or("").to_string();
            let status = v.get("status").and_then(|s| s.as_str()).unwrap_or("").to_string();
            let size = v.get("size").and_then(|s| s.as_u64()).unwrap_or(0) as usize;
            let message = v.get("message").and_then(|m| m.as_str()).unwrap_or("").to_string();
            Ok(ProgressEvent::SongComplete { index, title, status, size, message })
        }
        "album_complete" => {
            let success = v.get("success").and_then(|s| s.as_u64()).unwrap_or(0) as usize;
            let failed = v.get("failed").and_then(|f| f.as_u64()).unwrap_or(0) as usize;
            let skipped = v.get("skipped").and_then(|s| s.as_u64()).unwrap_or(0) as usize;
            let total = v.get("total").and_then(|t| t.as_u64()).unwrap_or(0) as usize;
            Ok(ProgressEvent::AlbumComplete { success, failed, skipped, total })
        }
        "error" => {
            let message = v.get("message").and_then(|m| m.as_str()).unwrap_or("").to_string();
            Ok(ProgressEvent::Error { message })
        }
        _ => Err(format!("Unknown event type: {}", event_type))
    }
}

/// Progress event types
#[derive(Debug)]
enum ProgressEvent {
    AlbumStart { title: String, source: String, total: usize },
    SongStart { index: usize, total: usize, title: String },
    SongComplete { index: usize, title: String, status: String, size: usize, message: String },
    AlbumComplete { success: usize, failed: usize, skipped: usize, total: usize },
    Error { message: String },
}

#[derive(serde::Serialize, serde::Deserialize)]
pub struct PythonInfo {
    python_path: String,
    cli_path: String,
    venv_path: String,
}
