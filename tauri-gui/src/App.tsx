import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { Moon, Sun } from "lucide-react";
import UrlInput from "./components/UrlInput";
import Configuration from "./components/Configuration";
import ProgressDisplay, { SongProgress } from "./components/ProgressDisplay";
import LogDisplay from "./components/LogDisplay";

interface PythonInfo {
  python_path: string;
  cli_path: string;
  venv_path: string;
}

interface DownloadConfig {
  outputDir: string;
  limit: string;
  timeout: string;
  retries: string;
  delay: string;
  overwrite: boolean;
  renumber: boolean;
  verbose: boolean;
}

interface LogEntry {
  timestamp: string;
  level: "INFO" | "WARNING" | "ERROR" | "DEBUG";
  message: string;
}

const DEFAULT_CONFIG: DownloadConfig = {
  outputDir: "./downloads",
  limit: "",
  timeout: "60",
  retries: "3",
  delay: "0.5",
  overwrite: false,
  renumber: false,
  verbose: false,
};

function App() {
  console.log("App component rendering...");

  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [config, setConfig] = useState<DownloadConfig>(DEFAULT_CONFIG);
  const [songs, setSongs] = useState<SongProgress[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isDownloading, setIsDownloading] = useState(false);
  const [showLogs, setShowLogs] = useState(false);
  const [statusMessage, setStatusMessage] = useState("Ready");
  const [pythonInfo, setPythonInfo] = useState<PythonInfo | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  const addLog = (level: "INFO" | "WARNING" | "ERROR" | "DEBUG", message: string) => {
    const now = new Date();
    const timestamp = now.toLocaleTimeString("en-US", { hour12: false });
    setLogs((prev) => [...prev, { timestamp, level, message }]);
  };

  // Apply theme to HTML element
  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  }, [theme]);

  // Load Python environment info on mount
  useEffect(() => {
    console.log("App mounted, checking Tauri context...");
    console.log("Window object:", typeof window);
    console.log("__TAURI__:", typeof window !== 'undefined' && '__TAURI__' in window);

    const loadPythonInfo = async () => {
      try {
        console.log("Loading Python info...");
        // Check if running in Tauri context
        if (typeof window !== 'undefined' && '__TAURI__' in window) {
          const info = await invoke<PythonInfo>("get_python_info");
          setPythonInfo(info);
          console.log("Python info loaded:", info);
          setStatusMessage("Ready");
        } else {
          console.warn("Not running in Tauri context");
          setStatusMessage("Development mode - Tauri API not available");
        }
      } catch (err) {
        console.error("Failed to get Python info:", err);
        setStatusMessage("Warning: Python environment not found");
      } finally {
        // Always mark as initialized, even if Python info loading failed
        setIsInitialized(true);
      }
    };

    loadPythonInfo();
  }, []);

  // Setup Tauri event listeners for real-time progress updates
  useEffect(() => {
    // 检查是否在 Tauri 环境中
    if (typeof window === 'undefined' || !('__TAURI__' in window)) {
      console.warn("Not in Tauri environment, skipping event listeners");
      return;
    }

    const unlisteners: Array<() => void> = [];

    // 设置事件监听器
    const setupListeners = async () => {
      try {
        const unlisten1 = await listen("download-progress", (event) => {
          const payload = event.payload as {
            type: string;
            index?: number;
            total?: number;
            title?: string;
            status?: string;
            size?: number;
            message?: string;
          };

          switch (payload.type) {
            case "album_start":
              addLog("INFO", `Album: ${payload.title} (${payload.total} songs)`);
              setSongs([]);
              break;

            case "song_start":
              setSongs((prev) => [
                ...prev,
                {
                  index: payload.index!,
                  title: payload.title || "",
                  status: "downloading",
                },
              ]);
              addLog("INFO", `[${payload.index}/${payload.total}] Starting: ${payload.title}`);
              break;

            case "song_complete":
              setSongs((prev) =>
                prev.map((song) =>
                  song.index === payload.index
                    ? {
                        ...song,
                        status: payload.status === "success" ? "success" : "failed",
                        size: payload.size
                          ? `${(payload.size / 1024).toFixed(1)} KB`
                          : undefined,
                      }
                    : song
                )
              );
              addLog(
                payload.status === "success" ? "INFO" : "ERROR",
                `[${payload.index}] ${payload.title}: ${payload.message}`
              );
              break;
          }
        });

        const unlisten2 = await listen("download-complete", (event) => {
          const payload = event.payload as {
            type: string;
            success: number;
            failed: number;
            skipped: number;
            total: number;
          };

          setStatusMessage(`Download complete: ${payload.success} success, ${payload.failed} failed`);
          setIsDownloading(false);
          addLog(
            "INFO",
            `Album complete: ${payload.success} success, ${payload.failed} failed, ${payload.skipped} skipped`
          );
        });

        const unlisten3 = await listen("download-error", (event) => {
          const payload = event.payload as {
            type: string;
            message: string;
          };

          setStatusMessage(`Error: ${payload.message}`);
          setIsDownloading(false);
          addLog("ERROR", payload.message);
        });

        // 保存 unlisten 函数
        unlisteners.push(unlisten1, unlisten2, unlisten3);
      } catch (error) {
        console.error("Failed to setup event listeners:", error);
      }
    };

    setupListeners();

    // Cleanup function
    return () => {
      unlisteners.forEach((unlisten) => {
        try {
          unlisten();
        } catch (error) {
          console.error("Error unlistening:", error);
        }
      });
    };
  }, []);

  useEffect(() => {
    // Load theme from localStorage
    const savedTheme = localStorage.getItem("theme") as "light" | "dark" | null;
    if (savedTheme) {
      setTheme(savedTheme);
    }

    // Load config from localStorage
    const savedConfig = localStorage.getItem("download-config");
    if (savedConfig) {
      try {
        const parsedConfig = JSON.parse(savedConfig);
        setConfig({ ...DEFAULT_CONFIG, ...parsedConfig });
      } catch (err) {
        console.error("Failed to parse saved config:", err);
      }
    }
  }, []);

  useEffect(() => {
    // Apply theme to document
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
    // Save theme to localStorage
    localStorage.setItem("theme", theme);
  }, [theme]);

  useEffect(() => {
    // Save config to localStorage when changed
    localStorage.setItem("download-config", JSON.stringify(config));
  }, [config]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  const handleDownloadAlbum = async (url: string) => {
    if (!pythonInfo) {
      setStatusMessage("Error: Python environment not ready");
      addLog("ERROR", "Python environment not ready");
      return;
    }

    setIsDownloading(true);
    setSongs([]);
    addLog("INFO", `Starting album download from: ${url}`);
    setShowLogs(true);
    setStatusMessage("Starting album download...");

    try {
      // Invoke download command (returns immediately, updates via events)
      await invoke("download_album", {
        url,
        outputDir: config.outputDir,
        limit: config.limit ? parseInt(config.limit) : null,
        timeout: parseInt(config.timeout),
        retries: parseInt(config.retries),
        delay: parseFloat(config.delay),
        overwrite: config.overwrite,
        renumber: config.renumber,
        verbose: config.verbose,
        pythonInfo,
      });

      // Note: Progress updates will come via Tauri events
    } catch (error) {
      const errorMsg = String(error);
      setStatusMessage(`Error: ${errorMsg}`);
      addLog("ERROR", errorMsg);
      setIsDownloading(false);
    }
  };

  const handleDownloadSong = async (url: string) => {
    if (!pythonInfo) {
      setStatusMessage("Error: Python environment not ready");
      addLog("ERROR", "Python environment not ready");
      return;
    }

    setIsDownloading(true);
    setSongs([]);
    addLog("INFO", `Starting song download from: ${url}`);
    setShowLogs(true);
    setStatusMessage("Starting song download...");

    try {
      // Invoke download command (returns immediately, updates via events)
      await invoke("download_song", {
        url,
        outputDir: config.outputDir,
        timeout: parseInt(config.timeout),
        retries: parseInt(config.retries),
        delay: parseFloat(config.delay),
        renumber: config.renumber,
        verbose: config.verbose,
        pythonInfo,
      });

      // Note: Progress updates will come via Tauri events
    } catch (error) {
      const errorMsg = String(error);
      setStatusMessage(`Error: ${errorMsg}`);
      addLog("ERROR", errorMsg);
      setIsDownloading(false);
    }
  };

  // Show loading state while initializing
  if (!isInitialized) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-white dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-700 dark:text-gray-300">Loading Resource Fetcher...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background-light dark:bg-background-dark text-foreground-light dark:text-foreground-dark transition-colors duration-200">
      {/* Header */}
      <header className="border-b border-border-light dark:border-border-dark bg-white dark:bg-gray-800">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-600 to-primary-800 rounded-lg flex items-center justify-center text-white font-bold text-sm">
                RF
              </div>
              <h1 className="text-xl font-semibold">Resource Fetcher</h1>
            </div>
            <button
              onClick={toggleTheme}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary-600 text-white hover:bg-primary-700 transition-colors"
            >
              {theme === "light" ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
              {theme === "light" ? "Dark" : "Light"}
            </button>
          </div>
        </div>
      </header>

      {/* Status Bar */}
      <div className="bg-gray-50 dark:bg-gray-900 border-b border-border-light dark:border-border-dark">
        <div className="container mx-auto px-4 py-2">
          <p className="text-sm text-gray-600 dark:text-gray-400">{statusMessage}</p>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          <UrlInput
            onDownloadAlbum={handleDownloadAlbum}
            onDownloadSong={handleDownloadSong}
            isDownloading={isDownloading}
          />
          <Configuration config={config} onChange={setConfig} />
          <ProgressDisplay songs={songs} total={songs.length} current={songs.filter(s => s.status === "success").length} />
          <LogDisplay
            logs={logs}
            isVisible={showLogs}
            onToggle={() => setShowLogs(!showLogs)}
          />
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border-light dark:border-border-dark bg-white dark:bg-gray-800 mt-auto">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center text-sm text-gray-600 dark:text-gray-400">
            <span>Resource Fetcher v0.2.0</span>
            <span>Built with Tauri + React</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
