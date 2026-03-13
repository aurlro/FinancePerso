const { autoUpdater } = require('electron-updater');
const { dialog, BrowserWindow } = require('electron');
const path = require('path');

class UpdateService {
  constructor(mainWindow) {
    this.mainWindow = mainWindow;
    this.setupAutoUpdater();
  }

  setupAutoUpdater() {
    // Configuration de l'auto-updater
    autoUpdater.logger = console;
    autoUpdater.autoDownload = false; // On demande d'abord à l'utilisateur
    autoUpdater.autoInstallOnAppQuit = true;

    // Événements
    autoUpdater.on('checking-for-update', () => {
      console.log('[Updater] Checking for updates...');
      this.sendToRenderer('update:checking');
    });

    autoUpdater.on('update-available', (info) => {
      console.log('[Updater] Update available:', info.version);
      this.sendToRenderer('update:available', info);
      this.showUpdateDialog(info);
    });

    autoUpdater.on('update-not-available', () => {
      console.log('[Updater] No updates available');
      this.sendToRenderer('update:not-available');
    });

    autoUpdater.on('error', (err) => {
      console.error('[Updater] Error:', err);
      this.sendToRenderer('update:error', err.message);
    });

    autoUpdater.on('download-progress', (progressObj) => {
      const percent = Math.round(progressObj.percent);
      console.log(`[Updater] Download progress: ${percent}%`);
      this.sendToRenderer('update:progress', percent);
    });

    autoUpdater.on('update-downloaded', (info) => {
      console.log('[Updater] Update downloaded');
      this.sendToRenderer('update:downloaded', info);
      this.showInstallDialog(info);
    });
  }

  sendToRenderer(channel, data) {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.webContents.send(channel, data);
    }
  }

  async showUpdateDialog(info) {
    const result = await dialog.showMessageBox(this.mainWindow, {
      type: 'info',
      title: 'Mise à jour disponible',
      message: `Une nouvelle version ${info.version} est disponible.`,
      detail: `Version actuelle: ${autoUpdater.currentVersion}\nNouvelle version: ${info.version}\n\nVoulez-vous télécharger la mise à jour maintenant ?`,
      buttons: ['Télécharger', 'Plus tard'],
      defaultId: 0,
      cancelId: 1
    });

    if (result.response === 0) {
      autoUpdater.downloadUpdate();
    }
  }

  async showInstallDialog(info) {
    const result = await dialog.showMessageBox(this.mainWindow, {
      type: 'info',
      title: 'Mise à jour prête',
      message: `La version ${info.version} a été téléchargée.`,
      detail: 'L\'application va redémarrer pour installer la mise à jour.',
      buttons: ['Redémarrer maintenant', 'Redémarrer plus tard'],
      defaultId: 0,
      cancelId: 1
    });

    if (result.response === 0) {
      autoUpdater.quitAndInstall(false, true);
    }
  }

  // Méthodes publiques
  checkForUpdates() {
    autoUpdater.checkForUpdates();
  }

  downloadUpdate() {
    return autoUpdater.downloadUpdate();
  }

  quitAndInstall() {
    autoUpdater.quitAndInstall(false, true);
  }
}

module.exports = { UpdateService };
