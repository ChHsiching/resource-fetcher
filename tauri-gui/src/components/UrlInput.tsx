import { useState } from "react";
import { Download, Link2 } from "lucide-react";

interface UrlInputProps {
  onDownloadAlbum: (url: string) => void;
  onDownloadSong: (url: string) => void;
  isDownloading: boolean;
}

export default function UrlInput({ onDownloadAlbum, onDownloadSong, isDownloading }: UrlInputProps) {
  const [url, setUrl] = useState("");

  const isValidUrl = (urlString: string) => {
    try {
      const urlObj = new URL(urlString);
      return urlObj.protocol === "http:" || urlObj.protocol === "https:";
    } catch {
      return false;
    }
  };

  const handleAlbumDownload = () => {
    if (isValidUrl(url)) {
      onDownloadAlbum(url);
    }
  };

  const handleSongDownload = () => {
    if (isValidUrl(url)) {
      onDownloadSong(url);
    }
  };

  return (
    <section className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-border-light dark:border-border-dark p-6">
      <h2 className="text-lg font-semibold mb-4">Download URL</h2>
      <div className="space-y-4">
        <div className="relative">
          <Link2 className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Enter album or song URL..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-md border border-border-light dark:border-border-dark bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
          />
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleAlbumDownload}
            disabled={!url || !isValidUrl(url) || isDownloading}
            className="flex items-center gap-2 px-6 py-2 rounded-md bg-primary-600 text-white hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
          >
            <Download className="w-4 h-4" />
            {isDownloading ? "Downloading..." : "Download Album"}
          </button>
          <button
            onClick={handleSongDownload}
            disabled={!url || !isValidUrl(url) || isDownloading}
            className="flex items-center gap-2 px-6 py-2 rounded-md bg-primary-600 text-white hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
          >
            <Download className="w-4 h-4" />
            {isDownloading ? "Downloading..." : "Download Song"}
          </button>
        </div>
      </div>
    </section>
  );
}
