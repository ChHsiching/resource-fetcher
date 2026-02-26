import { check } from '@tauri-apps/plugin-updater';
import { relaunch } from '@tauri-apps/plugin-process';
import type { Update } from '@tauri-apps/plugin-updater';

export interface UpdateInfo {
  version: string;
  body: string;
  date: string;
  available: boolean;
}

export class UpdateService {
  private static instance: UpdateService;
  private currentUpdate: Update | null = null;

  static getInstance(): UpdateService {
    if (!UpdateService.instance) {
      UpdateService.instance = new UpdateService();
    }
    return UpdateService.instance;
  }

  async checkForUpdates(): Promise<UpdateInfo | null> {
    try {
      const update = await check();

      if (!update) {
        return null;
      }

      this.currentUpdate = update;

      return {
        version: update.version,
        body: update.body || '',
        date: update.date || '',
        available: true
      };
    } catch (error) {
      console.error('Failed to check for updates:', error);
      return null;
    }
  }

  async downloadAndInstall(
    onProgress?: (progress: number, total: number) => void
  ): Promise<void> {
    if (!this.currentUpdate) {
      throw new Error('No update available');
    }

    let downloaded = 0;
    let total = 0;

    await this.currentUpdate.downloadAndInstall((event) => {
      switch (event.event) {
        case 'Started':
          total = event.data.contentLength || 0;
          if (onProgress) onProgress(0, total);
          break;
        case 'Progress':
          downloaded += event.data.chunkLength || 0;
          if (onProgress) onProgress(downloaded, total);
          break;
        case 'Finished':
          console.log('Update downloaded and installed');
          break;
      }
    });
  }

  async relaunchApp(): Promise<void> {
    await relaunch();
  }
}

export const updateService = UpdateService.getInstance();
