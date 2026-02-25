import { describe, it, expect, beforeEach, vi } from "vitest";
import { invoke } from "@tauri-apps/api/core";

// Mock Tauri API
vi.mock("@tauri-apps/api/core", () => ({
  invoke: vi.fn(),
}));

describe("Download Commands Integration Tests", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("get_python_info", () => {
    it("should return Python environment information", async () => {
      const mockPythonInfo = {
        python_path: "/path/to/.venv/bin/python",
        cli_path: "/path/to/dist/resource-fetcher",
        venv_path: "/path/to/.venv",
      };

      vi.mocked(invoke).mockResolvedValueOnce(mockPythonInfo);

      const result = await invoke<Record<string, string>>("get_python_info");

      expect(result).toEqual(mockPythonInfo);
      expect(invoke).toHaveBeenCalledWith("get_python_info");
    });

    it("should handle errors when Python environment is not found", async () => {
      vi.mocked(invoke).mockRejectedValueOnce(new Error("Python not found"));

      await expect(invoke("get_python_info")).rejects.toThrow("Python not found");
    });
  });

  describe("download_album", () => {
    it("should download album with valid parameters", async () => {
      const mockResult = "Album downloaded successfully";
      const mockPythonInfo = {
        python_path: "/path/to/.venv/bin/python",
        cli_path: "/path/to/dist/resource-fetcher",
        venv_path: "/path/to/.venv",
      };

      vi.mocked(invoke).mockResolvedValueOnce(mockResult);

      const result = await invoke<string>("download_album", {
        url: "https://example.com/album",
        outputDir: "./downloads",
        limit: 5,
        pythonInfo: mockPythonInfo,
      });

      expect(result).toBe(mockResult);
      expect(invoke).toHaveBeenCalledWith("download_album", {
        url: "https://example.com/album",
        outputDir: "./downloads",
        limit: 5,
        pythonInfo: mockPythonInfo,
      });
    });

    it("should handle download errors", async () => {
      const mockPythonInfo = {
        python_path: "/path/to/.venv/bin/python",
        cli_path: "/path/to/dist/resource-fetcher",
        venv_path: "/path/to/.venv",
      };

      vi.mocked(invoke).mockRejectedValueOnce(new Error("Download failed"));

      await expect(
        invoke("download_album", {
          url: "https://example.com/album",
          outputDir: "./downloads",
          limit: 5,
          pythonInfo: mockPythonInfo,
        })
      ).rejects.toThrow("Download failed");
    });

    it("should handle optional limit parameter", async () => {
      const mockResult = "Album downloaded successfully";
      const mockPythonInfo = {
        python_path: "/path/to/.venv/bin/python",
        cli_path: "/path/to/dist/resource-fetcher",
        venv_path: "/path/to/.venv",
      };

      vi.mocked(invoke).mockResolvedValueOnce(mockResult);

      const result = await invoke<string>("download_album", {
        url: "https://example.com/album",
        outputDir: "./downloads",
        limit: null,
        pythonInfo: mockPythonInfo,
      });

      expect(result).toBe(mockResult);
    });
  });

  describe("download_song", () => {
    it("should download song with valid parameters", async () => {
      const mockResult = "Song downloaded successfully";
      const mockPythonInfo = {
        python_path: "/path/to/.venv/bin/python",
        cli_path: "/path/to/dist/resource-fetcher",
        venv_path: "/path/to/.venv",
      };

      vi.mocked(invoke).mockResolvedValueOnce(mockResult);

      const result = await invoke<string>("download_song", {
        url: "https://example.com/song",
        outputDir: "./downloads",
        pythonInfo: mockPythonInfo,
      });

      expect(result).toBe(mockResult);
      expect(invoke).toHaveBeenCalledWith("download_song", {
        url: "https://example.com/song",
        outputDir: "./downloads",
        pythonInfo: mockPythonInfo,
      });
    });

    it("should handle download errors", async () => {
      const mockPythonInfo = {
        python_path: "/path/to/.venv/bin/python",
        cli_path: "/path/to/dist/resource-fetcher",
        venv_path: "/path/to/.venv",
      };

      vi.mocked(invoke).mockRejectedValueOnce(new Error("Download failed"));

      await expect(
        invoke("download_song", {
          url: "https://example.com/song",
          outputDir: "./downloads",
          pythonInfo: mockPythonInfo,
        })
      ).rejects.toThrow("Download failed");
    });
  });
});
