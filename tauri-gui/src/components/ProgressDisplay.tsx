import { Clock, CheckCircle, XCircle, Loader2 } from "lucide-react";

export interface SongProgress {
  index: number;
  title: string;
  status: "pending" | "downloading" | "success" | "failed";
  size?: string;
  speed?: string;
}

interface ProgressDisplayProps {
  songs: SongProgress[];
  total: number;
  current: number;
}

export default function ProgressDisplay({ songs, total, current }: ProgressDisplayProps) {
  const progress = total > 0 ? (current / total) * 100 : 0;

  const getStatusIcon = (status: SongProgress["status"]) => {
    switch (status) {
      case "pending":
        return <Clock className="w-5 h-5 text-gray-400" />;
      case "downloading":
        return <Loader2 className="w-5 h-5 text-primary-600 animate-spin" />;
      case "success":
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case "failed":
        return <XCircle className="w-5 h-5 text-red-600" />;
    }
  };

  return (
    <section className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-border-light dark:border-border-dark p-6">
      <h2 className="text-lg font-semibold mb-4">Download Progress</h2>

      {songs.length === 0 ? (
        <div className="text-center text-gray-500 dark:text-gray-400 py-8">
          Ready to download...
        </div>
      ) : (
        <div className="space-y-4">
          {/* Progress Bar */}
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Progress</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
              <div
                className="bg-primary-600 h-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          {/* Song List */}
          <div className="space-y-2">
            {songs.map((song, index) => (
              <div
                key={index}
                className="flex items-center gap-3 p-3 rounded-md border border-border-light dark:border-border-dark bg-gray-50 dark:bg-gray-900"
              >
                <div className="flex-shrink-0">
                  {getStatusIcon(song.status)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">{song.title}</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {song.index + 1} of {total}
                    {song.size && ` • ${song.size}`}
                    {song.speed && ` • ${song.speed}`}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Statistics */}
          <div className="flex justify-between text-sm pt-4 border-t border-border-light dark:border-border-dark">
            <div className="flex gap-4">
              <span>{songs.filter((s) => s.status === "success").length} ✓ Complete</span>
              <span>{songs.filter((s) => s.status === "downloading").length} ↓ Downloading</span>
              <span>{songs.filter((s) => s.status === "failed").length} ✗ Failed</span>
            </div>
            <span className="text-gray-600 dark:text-gray-400">
              {current} / {total}
            </span>
          </div>
        </div>
      )}
    </section>
  );
}
