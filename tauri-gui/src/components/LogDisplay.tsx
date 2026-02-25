import { useState, useRef, useEffect } from "react";
import { ChevronDown, ChevronUp, Copy, Check } from "lucide-react";

interface LogEntry {
  timestamp: string;
  level: "INFO" | "WARNING" | "ERROR" | "DEBUG";
  message: string;
}

interface LogDisplayProps {
  logs: LogEntry[];
  isVisible: boolean;
  onToggle: () => void;
}

export default function LogDisplay({ logs, isVisible, onToggle }: LogDisplayProps) {
  const [copied, setCopied] = useState(false);
  const logEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when logs update
  useEffect(() => {
    if (isVisible) {
      logEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs, isVisible]);

  const handleCopy = async () => {
    const logText = logs.map(log => `[${log.timestamp}] [${log.level}] ${log.message}`).join("\n");
    try {
      await navigator.clipboard.writeText(logText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy logs:", err);
    }
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case "ERROR":
        return "text-red-600 dark:text-red-400";
      case "WARNING":
        return "text-yellow-600 dark:text-yellow-400";
      case "INFO":
        return "text-blue-600 dark:text-blue-400";
      case "DEBUG":
        return "text-gray-600 dark:text-gray-400";
      default:
        return "text-gray-700 dark:text-gray-300";
    }
  };

  if (!isVisible) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-border-light dark:border-border-dark">
        <button
          onClick={onToggle}
          className="w-full px-4 py-2 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          <span className="text-sm font-medium">Show Logs ({logs.length} entries)</span>
          <ChevronDown className="w-4 h-4" />
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-border-light dark:border-border-dark overflow-hidden">
      {/* Header */}
      <div className="px-4 py-2 border-b border-border-light dark:border-border-dark flex items-center justify-between bg-gray-50 dark:bg-gray-900">
        <div className="flex items-center gap-3">
          <button
            onClick={onToggle}
            className="flex items-center gap-2 text-sm font-medium hover:text-primary-600 transition-colors"
          >
            <ChevronUp className="w-4 h-4" />
            Hide Logs
          </button>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            ({logs.length} entries)
          </span>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 px-2 py-1 text-sm rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
          title="Copy all logs"
        >
          {copied ? (
            <>
              <Check className="w-3 h-3 text-green-600" />
              Copied!
            </>
          ) : (
            <>
              <Copy className="w-3 h-3" />
              Copy
            </>
          )}
        </button>
      </div>

      {/* Log Content */}
      <div className="p-4 bg-gray-900 dark:bg-gray-950 max-h-96 overflow-y-auto font-mono text-xs">
        {logs.length === 0 ? (
          <p className="text-gray-500 dark:text-gray-400 italic">No logs yet...</p>
        ) : (
          <div className="space-y-1">
            {logs.map((log, index) => (
              <div key={index} className="flex gap-2">
                <span className="text-gray-500 dark:text-gray-400 shrink-0">
                  {log.timestamp}
                </span>
                <span className={`font-semibold shrink-0 ${getLevelColor(log.level)}`}>
                  [{log.level}]
                </span>
                <span className="text-gray-300 dark:text-gray-200 break-all">
                  {log.message}
                </span>
              </div>
            ))}
            <div ref={logEndRef} />
          </div>
        )}
      </div>
    </div>
  );
}
