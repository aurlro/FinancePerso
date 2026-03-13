const { contextBridge, ipcRenderer } = require('electron');

// API exposée au renderer de façon sécurisée
const electronAPI = {
  // App info
  app: {
    getVersion: () => ipcRenderer.invoke('app:get-version'),
    getPath: (name) => ipcRenderer.invoke('app:get-path', name),
  },
  
  // Database
  db: {
    getAllTransactions: (limit, offset) => ipcRenderer.invoke('db:get-all-transactions', limit, offset),
    getTransaction: (id) => ipcRenderer.invoke('db:get-transaction', id),
    createTransaction: (data) => ipcRenderer.invoke('db:create-transaction', data),
    updateTransaction: (id, data) => ipcRenderer.invoke('db:update-transaction', id, data),
    deleteTransaction: (id) => ipcRenderer.invoke('db:delete-transaction', id),
    getStatsByMonth: (year, month) => ipcRenderer.invoke('db:get-stats-by-month', year, month),
    getCategoriesStats: (year, month) => ipcRenderer.invoke('db:get-categories-stats', year, month),
    getCategories: () => ipcRenderer.invoke('db:get-categories'),
    getBudgets: () => ipcRenderer.invoke('db:get-budgets'),
    createBudget: (data) => ipcRenderer.invoke('db:create-budget', data),
    updateBudget: (id, data) => ipcRenderer.invoke('db:update-budget', id, data),
    deleteBudget: (id) => ipcRenderer.invoke('db:delete-budget', id),
    getBudgetStatus: (year, month) => ipcRenderer.invoke('db:get-budget-status', year, month),
    getPendingTransactions: () => ipcRenderer.invoke('db:get-pending-transactions'),
    validateBatch: (ids, category) => ipcRenderer.invoke('db:validate-batch', ids, category),
    ignoreTransactions: (ids) => ipcRenderer.invoke('db:ignore-transactions', ids),
    // AI-related methods
    categorizeWithAI: (label, amount) => ipcRenderer.invoke('db:categorize-with-ai', label, amount),
    getAISettings: () => ipcRenderer.invoke('db:get-ai-settings'),
    saveAISettings: (settings) => ipcRenderer.invoke('db:save-ai-settings', settings),
    testAIConnection: () => ipcRenderer.invoke('db:test-ai-connection'),
    getLearningRules: () => ipcRenderer.invoke('db:get-learning-rules'),
    createLearningRule: (pattern, category, confidence) => ipcRenderer.invoke('db:create-learning-rule', pattern, category, confidence),
    // Members
    getMembers: () => ipcRenderer.invoke('db:get-members'),
    getMember: (id) => ipcRenderer.invoke('db:get-member', id),
    createMember: (data) => ipcRenderer.invoke('db:create-member', data),
    updateMember: (id, data) => ipcRenderer.invoke('db:update-member', id, data),
    deleteMember: (id) => ipcRenderer.invoke('db:delete-member', id),
    getTransactionsByMember: (memberId, year, month) => ipcRenderer.invoke('db:get-transactions-by-member', memberId, year, month),
    assignTransactionMember: (transactionId, memberId, splitAmount) => ipcRenderer.invoke('db:assign-transaction-member', transactionId, memberId, splitAmount),
    getMemberStats: (year, month) => ipcRenderer.invoke('db:get-member-stats', year, month),
    getTransactionMember: (transactionId) => ipcRenderer.invoke('db:get-transaction-member', transactionId),
  },
  
  // File operations
  file: {
    selectCSV: () => ipcRenderer.invoke('file:select-csv'),
    importCSV: (filePath, options) => ipcRenderer.invoke('file:import-csv', filePath, options),
  },
  
  // Updates
  update: {
    check: () => ipcRenderer.invoke('update:check'),
    download: () => ipcRenderer.invoke('update:download'),
    install: () => ipcRenderer.invoke('update:install'),
    onChecking: (callback) => ipcRenderer.on('update:checking', callback),
    onAvailable: (callback) => ipcRenderer.on('update:available', (_, info) => callback(info)),
    onNotAvailable: (callback) => ipcRenderer.on('update:not-available', callback),
    onProgress: (callback) => ipcRenderer.on('update:progress', (_, percent) => callback(percent)),
    onDownloaded: (callback) => ipcRenderer.on('update:downloaded', (_, info) => callback(info)),
    onError: (callback) => ipcRenderer.on('update:error', (_, message) => callback(message)),
  },
  
  // Platform info (synchrone, safe)
  platform: process.platform,
};

// Exposer l'API
contextBridge.exposeInMainWorld('electronAPI', electronAPI);

console.log('[Preload] API exposed to renderer');
