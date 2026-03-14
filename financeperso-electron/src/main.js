const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('node:path');
const started = require('electron-squirrel-startup');
const { DatabaseService } = require('./services/database.js');
const { FileImportService } = require('./services/file-import.cjs');
const { AIService } = require('./services/ai-service.cjs');
const { UpdateService } = require('./services/updater.cjs');

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (started) {
  app.quit();
}

// Instances des services
let dbService = null;
let fileImportService = null;
let aiService = null;
let updateService = null;
let mainWindow = null;

// Initialize database
async function initializeServices() {
  try {
    const userDataPath = app.getPath('userData');
    const dbPath = path.join(userDataPath, 'finance.db');
    
    console.log('[Main] Initializing database at:', dbPath);
    
    dbService = new DatabaseService(dbPath);
    await dbService.initialize();
    
    // Initialize file import service
    fileImportService = new FileImportService(dbService);
    
    // Initialize AI service
    const aiSettings = await dbService.getAISettings();
    aiService = new AIService(aiSettings);
    
    console.log('[Main] Services initialized successfully');
    return true;
  } catch (error) {
    console.error('[Main] Failed to initialize services:', error);
    return false;
  }
}

// Initialize update service (après création de la fenêtre)
function initializeUpdater() {
  try {
    updateService = new UpdateService(mainWindow);
    
    // Vérifier les mises à jour au démarrage (après 5s)
    setTimeout(() => {
      updateService.checkForUpdates();
    }, 5000);
    
    console.log('[Main] Updater initialized');
  } catch (error) {
    console.error('[Main] Failed to initialize updater:', error);
  }
}

// IPC Handlers - App
ipcMain.handle('app:get-version', () => {
  return app.getVersion();
});

ipcMain.handle('app:get-path', (_, name) => {
  return app.getPath(name);
});

// IPC Handlers - Database
ipcMain.handle('db:get-all-transactions', async (_, limit, offset) => {
  return dbService.getAllTransactions(limit, offset);
});

ipcMain.handle('db:get-transaction', async (_, id) => {
  return dbService.getTransactionById(id);
});

ipcMain.handle('db:create-transaction', async (_, data) => {
  return dbService.createTransaction(data);
});

ipcMain.handle('db:update-transaction', async (_, id, data) => {
  return dbService.updateTransaction(id, data);
});

ipcMain.handle('db:delete-transaction', async (_, id) => {
  return dbService.deleteTransaction(id);
});

ipcMain.handle('db:get-stats-by-month', async (_, year, month) => {
  return dbService.getStatsByMonth(year, month);
});

ipcMain.handle('db:get-categories-stats', async (_, year, month) => {
  return dbService.getCategoriesStats(year, month);
});

ipcMain.handle('db:get-categories', async () => {
  return dbService.getAllCategories();
});

// IPC Handlers - Budgets
ipcMain.handle('db:get-budgets', async () => {
  return dbService.getAllBudgets();
});

ipcMain.handle('db:create-budget', async (_, data) => {
  return dbService.createBudget(data);
});

ipcMain.handle('db:update-budget', async (_, id, data) => {
  return dbService.updateBudget(id, data);
});

ipcMain.handle('db:delete-budget', async (_, id) => {
  return dbService.deleteBudget(id);
});

ipcMain.handle('db:get-budget-status', async (_, year, month) => {
  return dbService.getBudgetStatus(year, month);
});

ipcMain.handle('db:get-pending-transactions', async () => {
  return dbService.getPendingTransactions();
});

ipcMain.handle('db:validate-batch', async (_, ids, category) => {
  return dbService.updateMultipleTransactions(ids, category);
});

ipcMain.handle('db:ignore-transactions', async (_, ids) => {
  return dbService.ignoreTransactions(ids);
});

// IPC Handlers - AI
ipcMain.handle('db:categorize-with-ai', async (_, label, amount) => {
  if (!aiService) {
    return { category: 'Autre', confidence: 0, source: 'fallback' };
  }
  return aiService.categorize(label, amount);
});

ipcMain.handle('db:get-ai-settings', async () => {
  return dbService.getAISettings();
});

ipcMain.handle('db:save-ai-settings', async (_, settings) => {
  // Met à jour le service AI
  if (aiService) {
    aiService.updateConfig(settings);
  }
  return dbService.saveAISettings(settings);
});

ipcMain.handle('db:test-ai-connection', async () => {
  if (!aiService) {
    return { success: false, message: 'Service AI non initialisé' };
  }
  return aiService.testConnection();
});

ipcMain.handle('db:get-learning-rules', async () => {
  return dbService.getAllRules();
});

ipcMain.handle('db:create-learning-rule', async (_, pattern, category, confidence) => {
  return dbService.createRule(pattern, category, confidence);
});

// IPC Handlers - Members
ipcMain.handle('db:get-members', async () => {
  return dbService.getAllMembers();
});

ipcMain.handle('db:get-member', async (_, id) => {
  return dbService.getMemberById(id);
});

ipcMain.handle('db:create-member', async (_, data) => {
  return dbService.createMember(data);
});

ipcMain.handle('db:update-member', async (_, id, data) => {
  return dbService.updateMember(id, data);
});

ipcMain.handle('db:delete-member', async (_, id) => {
  return dbService.deleteMember(id);
});

ipcMain.handle('db:get-transactions-by-member', async (_, memberId, year, month) => {
  return dbService.getTransactionsByMember(memberId, year, month);
});

ipcMain.handle('db:assign-transaction-member', async (_, transactionId, memberId, splitAmount) => {
  return dbService.assignTransactionToMember(transactionId, memberId, splitAmount);
});

ipcMain.handle('db:get-member-stats', async (_, year, month) => {
  return dbService.getMemberStats(year, month);
});

ipcMain.handle('db:get-transaction-member', async (_, transactionId) => {
  return dbService.getTransactionMember(transactionId);
});

// IPC Handlers - Wealth Accounts
ipcMain.handle('db:get-wealth-accounts', async () => {
  return dbService.getAllWealthAccounts();
});

ipcMain.handle('db:create-wealth-account', async (_, data) => {
  return dbService.createWealthAccount(data);
});

ipcMain.handle('db:update-wealth-account', async (_, id, data) => {
  return dbService.updateWealthAccount(id, data);
});

ipcMain.handle('db:delete-wealth-account', async (_, id) => {
  return dbService.deleteWealthAccount(id);
});

// IPC Handlers - Savings Goals
ipcMain.handle('db:get-savings-goals', async () => {
  return dbService.getAllSavingsGoals();
});

ipcMain.handle('db:create-savings-goal', async (_, data) => {
  return dbService.createSavingsGoal(data);
});

ipcMain.handle('db:update-savings-goal', async (_, id, data) => {
  return dbService.updateSavingsGoal(id, data);
});

ipcMain.handle('db:delete-savings-goal', async (_, id) => {
  return dbService.deleteSavingsGoal(id);
});

// IPC Handlers - Subscriptions
ipcMain.handle('db:get-subscriptions', async () => {
  return dbService.getAllSubscriptions();
});

ipcMain.handle('db:create-subscription', async (_, data) => {
  return dbService.createSubscription(data);
});

ipcMain.handle('db:update-subscription', async (_, id, data) => {
  return dbService.updateSubscription(id, data);
});

ipcMain.handle('db:delete-subscription', async (_, id) => {
  return dbService.deleteSubscription(id);
});

ipcMain.handle('db:detect-subscriptions', async () => {
  return dbService.detectSubscriptions();
});

ipcMain.handle('db:get-upcoming-payments', async (_, days) => {
  return dbService.getUpcomingPayments(days);
});

// IPC Handlers - File Import
ipcMain.handle('file:select-csv', async () => {
  if (!mainWindow) return null;
  
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'Fichiers CSV', extensions: ['csv'] },
      { name: 'Tous les fichiers', extensions: ['*'] }
    ],
    title: 'Sélectionner un fichier de transactions'
  });
  
  return result.canceled ? null : result.filePaths[0];
});

ipcMain.handle('file:import-csv', async (_, filePath, options) => {
  if (!fileImportService) {
    return {
      success: false,
      error: 'Service d\'import non initialisé',
      total: 0,
      imported: 0,
      errors: 0,
      fileName: ''
    };
  }
  
  return fileImportService.importCSV(filePath, options);
});

// IPC Handlers - Updates
ipcMain.handle('update:check', () => {
  if (updateService) {
    updateService.checkForUpdates();
  }
});

ipcMain.handle('update:download', () => {
  if (updateService) {
    updateService.downloadUpdate();
  }
});

ipcMain.handle('update:install', () => {
  if (updateService) {
    updateService.quitAndInstall();
  }
});

const createWindow = () => {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 600,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  // Load the app - utilise l'URL de dev ou le fichier de production
  const devServerUrl = process.env.VITE_DEV_SERVER_URL;
  if (devServerUrl) {
    console.log('[Main] Loading dev server URL:', devServerUrl);
    mainWindow.loadURL(devServerUrl);
    mainWindow.webContents.openDevTools();
  } else {
    console.log('[Main] Loading production build...');
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Initialize updater après que la fenêtre soit prête
    initializeUpdater();
  });

  // Log renderer console messages
  mainWindow.webContents.on('console-message', (_, level, message) => {
    console.log(`[Renderer] ${message}`);
  });
  
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
};

app.whenReady().then(async () => {
  console.log('[Main] App ready');
  
  // Initialize services
  const servicesInitialized = await initializeServices();
  if (!servicesInitialized) {
    console.error('[Main] Warning: Services initialization failed');
  }
  
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    // Close database before quitting
    if (dbService) {
      dbService.close();
    }
    if (aiService) {
      aiService = null;
    }
    app.quit();
  }
});

console.log('[Main] Main process started');
