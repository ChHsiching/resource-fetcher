import { useState } from "react";
import { open } from "@tauri-apps/plugin-dialog";
import { FolderOpen, Settings2, ChevronDown, ChevronRight } from "lucide-react";

interface DownloadConfig {
  outputDir: string;
  limit: string;
  timeout: string;
  retries: string;
  overwrite: boolean;
  verbose: boolean;
}

interface ConfigurationProps {
  config: DownloadConfig;
  onChange: (config: DownloadConfig) => void;
}

export default function Configuration({ config, onChange }: ConfigurationProps) {
  const [advancedOpen, setAdvancedOpen] = useState(false);

  const updateConfig = (updates: Partial<DownloadConfig>) => {
    onChange({ ...config, ...updates });
  };

  const handleBrowse = async () => {
    try {
      const selected = await open({
        directory: true,
        multiple: false,
      });

      if (selected) {
        updateConfig({ outputDir: selected as string });
      }
    } catch (err) {
      console.error("Failed to open directory dialog:", err);
    }
  };

  return (
    <section className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-border-light dark:border-border-dark p-6">
      <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Settings2 className="w-5 h-5" />
        Configuration
      </h2>

      <div className="space-y-4">
        {/* Output Directory */}
        <div>
          <label className="block text-sm font-medium mb-1">Output Directory</label>
          <div className="flex gap-2">
            <input
              type="text"
              value={config.outputDir}
              onChange={(e) => updateConfig({ outputDir: e.target.value })}
              className="flex-1 px-4 py-2 rounded-md border border-border-light dark:border-border-dark bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
            />
            <button
              onClick={handleBrowse}
              className="px-4 py-2 rounded-md border border-border-light dark:border-border-dark hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-2"
            >
              <FolderOpen className="w-4 h-4" />
              Browse...
            </button>
          </div>
        </div>

        {/* Download Limit */}
        <div>
          <label className="block text-sm font-medium mb-1">Download Limit (Optional)</label>
          <input
            type="number"
            placeholder="Leave empty to download all songs"
            value={config.limit}
            onChange={(e) => updateConfig({ limit: e.target.value })}
            className="w-full px-4 py-2 rounded-md border border-border-light dark:border-border-dark bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
          />
        </div>

        {/* Advanced Settings (Collapsible) */}
        <div className="border border-border-light dark:border-border-dark rounded-md overflow-hidden">
          <button
            onClick={() => setAdvancedOpen(!advancedOpen)}
            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <span className="font-medium text-sm">Advanced Settings</span>
            {advancedOpen ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </button>

          {advancedOpen && (
            <div className="p-4 space-y-4 border-t border-border-light dark:border-border-dark">
              {/* Timeout */}
              <div>
                <label className="block text-sm font-medium mb-1">Timeout (seconds)</label>
                <input
                  type="number"
                  value={config.timeout}
                  onChange={(e) => updateConfig({ timeout: e.target.value })}
                  className="w-full px-4 py-2 rounded-md border border-border-light dark:border-border-dark bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                />
              </div>

              {/* Retries */}
              <div>
                <label className="block text-sm font-medium mb-1">Retries</label>
                <input
                  type="number"
                  value={config.retries}
                  onChange={(e) => updateConfig({ retries: e.target.value })}
                  className="w-full px-4 py-2 rounded-md border border-border-light dark:border-border-dark bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                />
              </div>

              {/* Checkboxes */}
              <div className="space-y-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={config.overwrite}
                    onChange={(e) => updateConfig({ overwrite: e.target.checked })}
                    className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm">Overwrite existing files</span>
                </label>

                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={config.verbose}
                    onChange={(e) => updateConfig({ verbose: e.target.checked })}
                    className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm">Verbose output</span>
                </label>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
