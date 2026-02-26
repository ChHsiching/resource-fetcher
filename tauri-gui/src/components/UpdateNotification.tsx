import React, { useState } from 'react';
import { updateService } from '../services/updateService';

interface UpdateNotificationProps {
  update: {
    version: string;
    body: string;
    date: string;
  };
  onUpdateComplete: () => void;
  onDismiss: () => void;
}

export const UpdateNotification: React.FC<UpdateNotificationProps> = ({
  update,
  onUpdateComplete,
  onDismiss
}) => {
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [isReadyToInstall, setIsReadyToInstall] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpdate = async () => {
    setIsDownloading(true);
    setError(null);

    try {
      await updateService.downloadAndInstall((progress, total) => {
        const percentage = Math.round((progress / total) * 100);
        setDownloadProgress(percentage);
      });

      setIsDownloading(false);
      setIsReadyToInstall(true);
      onUpdateComplete();
    } catch (err) {
      setIsDownloading(false);
      setError('更新下载失败，请稍后重试');
      console.error('Update failed:', err);
    }
  };

  const handleRelaunch = async () => {
    try {
      await updateService.relaunchApp();
    } catch (err) {
      setError('重启失败，请手动重启应用');
    }
  };

  return (
    <div className="update-notification">
      <div className="update-content">
        <h3>发现新版本 {update.version}</h3>
        <p className="update-date">{update.date}</p>
        <div className="update-notes">
          <h4>更新内容：</h4>
          <p>{update.body || '性能优化和 Bug 修复'}</p>
        </div>

        {error && <div className="update-error">{error}</div>}

        {isDownloading && (
          <div className="download-progress">
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${downloadProgress}%` }}
              />
            </div>
            <p>下载中... {downloadProgress}%</p>
          </div>
        )}

        {isReadyToInstall && (
          <div className="update-ready">
            <p>✅ 更新已下载完成，点击下方按钮重启应用以完成安装</p>
          </div>
        )}

        <div className="update-actions">
          {isReadyToInstall ? (
            <button onClick={handleRelaunch} className="btn-primary">
              立即重启
            </button>
          ) : (
            <>
              <button
                onClick={handleUpdate}
                disabled={isDownloading}
                className="btn-primary"
              >
                {isDownloading ? '下载中...' : '立即更新'}
              </button>
              <button
                onClick={onDismiss}
                disabled={isDownloading}
                className="btn-secondary"
              >
                稍后提醒
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
