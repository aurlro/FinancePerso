/**
 * Electron Preload Script
 * Pont sécurisé entre main et renderer
 */

// Import Electron - méthode compatible
const electron = require('electron')
const contextBridge = electron.contextBridge
const ipcRenderer = electron.ipcRenderer

// API exposée au renderer
const electronAPI = {
  getVersion: () => ipcRenderer.invoke('app:get-version'),
  getPath: (name) => ipcRenderer.invoke('app:get-path', name),
  platform: process.platform,
  ping: () => 'pong',
}

// Exposer l'API
contextBridge.exposeInMainWorld('electronAPI', electronAPI)

console.log('🔌 Electron preload script loaded')
