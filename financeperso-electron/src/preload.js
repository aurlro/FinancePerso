/**
 * Preload Script
 * Expose une API sécurisée au renderer process
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose l'API au renderer
contextBridge.exposeInMainWorld('electronAPI', {
  // Database
  db: {
    query: (sql, params) => ipcRenderer.invoke('db:query', sql, params),
    transaction: (operations) => ipcRenderer.invoke('db:transaction', operations),
    getTransactions: (options) => ipcRenderer.invoke('db:getTransactions', options),
    getTransactionsByMonth: (year, month) => ipcRenderer.invoke('db:getTransactionsByMonth', year, month),
    getDashboardStats: (year, month) => ipcRenderer.invoke('db:getDashboardStats', year, month),
    insertTransaction: (data) => ipcRenderer.invoke('db:insertTransaction', data),
    updateTransaction: (id, data) => ipcRenderer.invoke('db:updateTransaction', id, data),
    deleteTransaction: (id) => ipcRenderer.invoke('db:deleteTransaction', id),
    getCategories: () => ipcRenderer.invoke('db:getCategories'),
  },

  // File operations
  file: {
    selectCSV: () => ipcRenderer.invoke('file:selectCSV'),
    importCSV: (filePath, options) => ipcRenderer.invoke('file:importCSV', filePath, options),
  },

  // App info
  app: {
    getVersion: () => ipcRenderer.invoke('app:getVersion'),
    getPath: (name) => ipcRenderer.invoke('app:getPath', name),
  },

  // Theme
  theme: {
    set: (theme) => ipcRenderer.invoke('theme:set', theme),
    get: () => ipcRenderer.invoke('theme:get'),
    onChanged: (callback) => {
      ipcRenderer.on('theme:changed', (_, theme) => callback(theme));
    },
  },

  // Legacy compatibility
  getVersion: () => ipcRenderer.invoke('app:getVersion'),
  getPath: (name) => ipcRenderer.invoke('app:getPath', name),
  ping: () => 'pong',
  platform: process.platform,
});

console.log('[Preload] API exposed to renderer');
