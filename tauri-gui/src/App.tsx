import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
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
  overwrite: boolean;
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
  overwrite: false,
  verbose: false,
};

function App() {
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [config, setConfig] = useState<DownloadConfig>(DEFAULT_CONFIG);
  const [songs, setSongs] = useState<SongProgress[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isDownloading, setIsDownloading] = useState(false);
  const [showLogs, setShowLogs] = useState(false);
  const [statusMessage, setStatusMessage] = useState("Ready");
  const [pythonInfo, setPythonInfo] = useState<PythonInfo | null>(null);

  const addLog = (level: "INFO" | "WARNING" | "ERROR" | "DEBUG", message: string) => {
    const now = new Date();
    const timestamp = now.toLocaleTimeString("en-US", { hour12: false });
    setLogs((prev) => [...prev, { timestamp, level, message }]);
  };

  // Load Python environment info on mount
  useEffect(() => {
    invoke<PythonInfo>("get_python_info")
      .then(setPythonInfo)
      .catch((err) => {
        console.error("Failed to get Python info:", err);
        setStatusMessage("Warning: Python environment not found");
      });
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
      const result = await invoke<string>("download_album", {
        url,
        outputDir: config.outputDir,
        limit: config.limit ? parseInt(config.limit) : null,
        timeout: parseInt(config.timeout),
        retries: parseInt(config.retries),
        overwrite: config.overwrite,
        verbose: config.verbose,
        pythonInfo,
      });

      // Parse CLI output and add to logs
      const lines = result.split("\n");
      lines.forEach((line) => {
        if (line.trim()) {
          // Try to parse log level from Python log format
          const logMatch = line.match(/(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - (\w+) - (.+)/);
          if (logMatch) {
            const [, timestamp, , level, message] = logMatch;
            addLog(level as "INFO" | "WARNING" | "ERROR" | "DEBUG", message);
          } else {
            addLog("INFO", line);
          }
        }
      });

      setStatusMessage("Download completed");
      addLog("INFO", "Download completed successfully");
    } catch (error) {
      const errorMsg = String(error);
      setStatusMessage(`Error: ${errorMsg}`);
      addLog("ERROR", errorMsg);
    } finally {
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
      const result = await invoke<string>("download_song", {
        url,
        outputDir: config.outputDir,
        timeout: parseInt(config.timeout),
        retries: parseInt(config.retries),
        verbose: config.verbose,
        pythonInfo,
      });

      // Parse CLI output and add to logs
      const lines = result.split("\n");
      lines.forEach((line) => {
        if (line.trim()) {
          const logMatch = line.match(/(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - (\w+) - (.+)/);
          if (logMatch) {
            const [, timestamp, , level, message] = logMatch;
            addLog(level as "INFO" | "WARNING" | "ERROR" | "DEBUG", message);
          } else {
            addLog("INFO", line);
          }
        }
      });

      setStatusMessage("Download completed");
      addLog("INFO", "Download completed successfully");
    } catch (error) {
      const errorMsg = String(error);
      setStatusMessage(`Error: ${errorMsg}`);
      addLog("ERROR", errorMsg);
    } finally {
      setIsDownloading(false);
    }
  };

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
          <ProgressDisplay songs={songs} total={songs.length} current={0} />
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
