// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::path::PathBuf;
use std::process::Command;
use std::env;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![
            greet,
            get_python_info,
            download_album,
            download_song,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

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

    // Get CLI executable path
    let cli_dir = if cfg!(debug_assertions) {
        let exe_dir = std::env::current_exe()
            .map_err(|e| format!("Failed to get exe path: {}", e))?

            .and_then(|p| p.parent())
            .and_then(|p| p.parent())
            .ok_or("Failed to get project root")?
            .join("dist")
    } else {
        let exe_dir = std::env::current_exe()
            .map_err(|e| format!("Failed to get exe path: {}", e))?;

        exe_dir.parent()
            .ok_or("Failed to get app directory")?
            .join("Resources")
            .join("cli")
    };

    let cli_exec = if cfg!(windows) {
        cli_dir.join("resource-fetcher.exe")
    } else {
        cli_dir.join("resource-fetcher")
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
    overwrite: bool,
    verbose: bool,
    python_info: PythonInfo,
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
        .arg(retries.to_string());

    if let Some(n) = limit {
        cmd.arg("--limit").arg(n.to_string());
    }

    if overwrite {
        cmd.arg("--overwrite");
    }

    if verbose {
        cmd.arg("--verbose");
    }

    // Execute CLI and capture output
    let output = cmd
        .output()
        .map_err(|e| format!("Failed to execute CLI: {}", e))?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr).to_string();
        let stdout = String::from_utf8_lossy(&output.stdout).to_string();
        if stderr.is_empty() {
            Err(stdout)
        } else {
            Err(stderr)
        }
    }
}

#[tauri::command]
fn download_song(
    url: String,
    output_dir: String,
    timeout: u32,
    retries: u32,
    verbose: bool,
    python_info: PythonInfo,
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
        .arg(retries.to_string());

    if verbose {
        cmd.arg("--verbose");
    }

    // Execute CLI and capture output
    let output = cmd
        .output()
        .map_err(|e| format!("Failed to execute CLI: {}", e))?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr).to_string();
        let stdout = String::from_utf8_lossy(&output.stdout).to_string();
        if stderr.is_empty() {
            Err(stdout)
        } else {
            Err(stderr)
        }
    }
}

#[derive(serde::Serialize)]
pub struct PythonInfo {
    python_path: String,
    cli_path: String,
    venv_path: String,
}
