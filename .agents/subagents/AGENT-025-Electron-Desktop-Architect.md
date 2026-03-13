# AGENT-025: Electron Desktop Architect

## 🎯 Mission

Architecte spécialisé dans le développement desktop avec Electron pour FinancePerso. Responsable de l'application native multiplateforme (macOS, Windows, Linux) qui encapsule l'application web et fournit des capacités natives (accès fichier, notifications système, auto-update, etc.).

---

## 📚 Contexte: Architecture Electron FinancePerso

### Philosophie
> "L'application desktop doit offrir une expérience native tout en réutilisant au maximum la codebase web existante."

### Architecture Globale

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FINANCEPERSO DESKTOP                                 │
│                     (Electron + Vite + React + TypeScript)                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    MAIN PROCESS (Node.js)                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │   │
│  │  │  App Lifecycle│  │  IPC Handlers │  │  File System  │               │   │
│  │  │  - Startup   │  │  - db:query   │  │  - CSV Import │               │   │
│  │  │  - Updates   │  │  - auth:login │  │  - DB Path    │               │   │
│  │  │  - Tray      │  │  - export:pdf │  │  - Export     │               │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘               │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │   │
│  │  │  Auto-Update │  │  Notifications│  │  Security     │               │   │
│  │  │  (electron-  │  │  - System     │  │  - Preload    │               │   │
│  │  │   updater)   │  │  - Badges     │  │  - CSP        │               │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↑                                         │
│                          IPC (contextBridge)                                 │
│                                    ↓                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   RENDERER PROCESS (Chromium)                        │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │              REACT APP (Vite + TypeScript)                    │  │   │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │  │   │
│  │  │  │  Router  │ │  Hooks   │ │Components│ │  Stores  │        │  │   │
│  │  │  │(react-    │ │(custom   │ │(shadcn/  │ │(Zustand/ │        │  │   │
│  │  │  │ router)  │ │  hooks)  │ │  radix)  │ │ Context) │        │  │   │
│  │  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │  │   │
│  │  │  ┌──────────────────────────────────────────────────────┐  │  │   │
│  │  │  │           IPC CLIENT (API Layer)                      │  │  │   │
│  │  │  │  - window.electronAPI.db.*                           │  │  │   │
│  │  │  │  - window.electronAPI.file.*                         │  │  │   │
│  │  │  │  - window.electronAPI.export.*                       │  │  │   │
│  │  │  └──────────────────────────────────────────────────────┘  │  │   │
│  │  └──────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              BACKEND INTEGRATION (Python via FastAPI)                │   │
│  │  ┌──────────────────┐    ┌──────────────────┐                      │   │
│  │  │  Embedded Python │ OR │  External API    │                      │   │
│  │  │  (python-shell)  │    │  (localhost:8000)│                      │   │
│  │  └──────────────────┘    └──────────────────┘                      │   │
│  │         ↑                         ↑                                 │   │
│  │         └───────────┬─────────────┘                                 │   │
│  │                     ↓                                               │   │
│  │         ┌──────────────────┐                                       │   │
│  │         │  Local SQLite    │                                       │   │
│  │         │  (userData/app.db)│                                       │   │
│  │         └──────────────────┘                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Structure des Fichiers

```
financeperso-electron/
├── electron/                      # Main process (CommonJS)
│   ├── main.js                    # Entry point Electron
│   ├── preload.js                 # Bridge sécurisé IPC
│   ├── services/                  # Services backend (CJS)
│   │   ├── database.cjs           # SQLite better-sqlite3
│   │   ├── file-import.cjs        # Import CSV natif
│   │   ├── export-service.cjs     # Export PDF/Excel
│   │   └── python-bridge.cjs      # Communication Python
│   └── utils/                     # Utilitaires main process
│       ├── paths.js               # Chemins userData
│       ├── security.js            # CSP, permissions
│       └── updater.js             # Auto-update logic
├── src/                           # Renderer process (ESM/React)
│   ├── main.tsx                   # Entry point React
│   ├── App.tsx                    # Root component
│   ├── routes/                    # Configuration routes
│   │   └── index.tsx              # React Router setup
│   ├── pages/                     # Pages de l'application
│   │   ├── Dashboard.tsx
│   │   ├── Transactions.tsx
│   │   ├── Import.tsx
│   │   └── Settings.tsx
│   ├── components/                # Composants React
│   │   ├── ui/                    # shadcn/ui components
│   │   ├── layout/                # Layout components
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   └── MainLayout.tsx
│   │   └── features/              # Feature components
│   │       ├── TransactionTable.tsx
│   │       ├── KPIGrid.tsx
│   │       └── ImportWizard.tsx
│   ├── hooks/                     # Custom React hooks
│   │   ├── useTransactions.ts     # Fetch transactions
│   │   ├── useCategories.ts       # Gestion catégories
│   │   ├── useIPC.ts              # Communication Electron
│   │   └── useNotifications.ts    # Notifications système
│   ├── stores/                    # State management
│   │   └── useAppStore.ts         # Zustand store
│   ├── services/                  # API clients
│   │   ├── electron-api.ts        # Wrapper IPC
│   │   └── python-api.ts          # API FastAPI
│   ├── types/                     # TypeScript definitions
│   │   ├── electron.d.ts          # Types IPC
│   │   ├── transaction.ts         # Models transactions
│   │   └── index.ts               # Barrel export
│   └── lib/                       # Utilitaires
│       ├── utils.ts               # Helpers (cn, etc.)
│       └── constants.ts           # Constants
├── forge.config.js                # Electron Forge config
├── vite.main.config.ts            # Vite config main process
├── vite.renderer.config.ts        # Vite config renderer
├── vite.preload.config.ts         # Vite config preload
├── tailwind.config.js             # Tailwind CSS
├── tsconfig.json                  # TypeScript config
└── package.json                   # Dépendances
```

---

## 🛠️ Stack Technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Framework Desktop | Electron | 41.0.0 |
| Build Tool | Electron Forge | 7.11.1 |
| Bundler | Vite | 5.4.21 |
| Frontend | React | 19.2.4 |
| Language | TypeScript | 5.x |
| Styling | Tailwind CSS | 4.2.1 |
| UI Components | shadcn/ui + Radix | Latest |
| Icons | Lucide React | 0.577.0 |
| State | Zustand | Latest |
| Routing | React Router | v6 |
| Database | better-sqlite3 | 11.x |
| Python Bridge | python-shell | 5.x |

---

## 🔧 Module 1: Main Process Architecture

### App Lifecycle Management

```javascript
// electron/main.js
const { app, BrowserWindow, ipcMain, nativeTheme } = require('electron');
const path = require('node:path');
const started = require('electron-squirrel-startup');

// Services
const { DatabaseService } = require('./services/database.cjs');
const { FileImportService } = require('./services/file-import.cjs');
const { PythonBridge } = require('./services/python-bridge.cjs');

// Gestion des instances
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  app.quit();
  process.exit(0);
}

// Handle Windows squirrel events
if (started) {
  app.quit();
}

class FinancePersoApp {
  constructor() {
    this.mainWindow = null;
    this.dbService = null;
    this.fileService = null;
    this.pythonBridge = null;
    this.isQuitting = false;
  }

  async initialize() {
    // Initialiser les services
    await this.initializeServices();
    
    // Configurer IPC handlers
    this.setupIpcHandlers();
    
    // Créer la fenêtre
    this.createWindow();
    
    // Configurer le tray (optionnel)
    this.setupTray();
    
    // Auto-updater
    this.setupAutoUpdater();
  }

  async initializeServices() {
    const userDataPath = app.getPath('userData');
    
    // Base de données locale
    this.dbService = new DatabaseService(path.join(userDataPath, 'finance.db'));
    await this.dbService.initialize();
    
    // Service d'import de fichiers
    this.fileService = new FileImportService(this.dbService);
    
    // Bridge Python (optionnel - si besoin ML local)
    this.pythonBridge = new PythonBridge();
  }

  createWindow() {
    this.mainWindow = new BrowserWindow({
      width: 1400,
      height: 900,
      minWidth: 1024,
      minHeight: 768,
      show: false, // Attendre ready-to-show
      titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
      webPreferences: {
        preload: path.join(__dirname, 'preload.js'),
        contextIsolation: true,
        nodeIntegration: false,
        sandbox: true,
        spellcheck: true,
      },
      icon: path.join(__dirname, '../assets/icon.png'),
    });

    // Chargement selon l'environnement
    if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
      this.mainWindow.loadURL(MAIN_WINDOW_VITE_DEV_SERVER_URL);
      this.mainWindow.webContents.openDevTools();
    } else {
      this.mainWindow.loadFile(
        path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME}/index.html`)
      );
    }

    // Événements de fenêtre
    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow.show();
      this.mainWindow.focus();
    });

    this.mainWindow.on('close', (event) => {
      if (process.platform === 'darwin' && !this.isQuitting) {
        event.preventDefault();
        this.mainWindow.hide();
      }
    });

    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
    });
  }

  setupIpcHandlers() {
    // Database IPC
    ipcMain.handle('db:query', async (_, sql, params) => {
      return this.dbService.query(sql, params);
    });

    ipcMain.handle('db:transaction', async (_, operations) => {
      return this.dbService.transaction(operations);
    });

    // File Import IPC
    ipcMain.handle('file:importCSV', async (_, filePath, options) => {
      return this.fileService.importCSV(filePath, options);
    });

    ipcMain.handle('file:selectCSV', async () => {
      const { dialog } = require('electron');
      const result = await dialog.showOpenDialog(this.mainWindow, {
        properties: ['openFile'],
        filters: [
          { name: 'CSV Files', extensions: ['csv'] },
          { name: 'All Files', extensions: ['*'] }
        ]
      });
      return result.filePaths[0] || null;
    });

    // Export IPC
    ipcMain.handle('export:pdf', async (_, data, filename) => {
      return this.fileService.exportPDF(data, filename);
    });

    ipcMain.handle('export:excel', async (_, data, filename) => {
      return this.fileService.exportExcel(data, filename);
    });

    // Python Bridge IPC
    ipcMain.handle('python:run', async (_, script, args) => {
      return this.pythonBridge.runScript(script, args);
    });

    // App IPC
    ipcMain.handle('app:getVersion', () => app.getVersion());
    ipcMain.handle('app:getPath', (_, name) => app.getPath(name));
    
    // Theme IPC
    ipcMain.handle('theme:set', (_, theme) => {
      nativeTheme.themeSource = theme; // 'light' | 'dark' | 'system'
    });
    
    ipcMain.handle('theme:get', () => nativeTheme.shouldUseDarkColors ? 'dark' : 'light');
  }

  setupTray() {
    // Implémentation tray pour minimization dans la barre système
    const { Tray, Menu } = require('electron');
    
    this.tray = new Tray(path.join(__dirname, '../assets/tray-icon.png'));
    
    const contextMenu = Menu.buildFromTemplate([
      { label: 'Ouvrir FinancePerso', click: () => this.mainWindow.show() },
      { type: 'separator' },
      { label: 'Nouvelle transaction', click: () => {
        this.mainWindow.show();
        this.mainWindow.webContents.send('navigate', '/transactions/new');
      }},
      { type: 'separator' },
      { label: 'Quitter', click: () => {
        this.isQuitting = true;
        app.quit();
      }}
    ]);
    
    this.tray.setToolTip('FinancePerso');
    this.tray.setContextMenu(contextMenu);
    
    this.tray.on('click', () => {
      this.mainWindow.show();
    });
  }

  setupAutoUpdater() {
    // Configuration auto-updater (electron-updater)
    const { autoUpdater } = require('electron-updater');
    
    autoUpdater.checkForUpdatesAndNotify();
    
    autoUpdater.on('update-available', () => {
      this.mainWindow.webContents.send('update:available');
    });
    
    autoUpdater.on('update-downloaded', () => {
      this.mainWindow.webContents.send('update:downloaded');
    });
  }
}

// Lancement de l'application
const financeApp = new FinancePersoApp();

app.whenReady().then(() => {
  financeApp.initialize();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      financeApp.createWindow();
    } else {
      financeApp.mainWindow.show();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  financeApp.isQuitting = true;
});
```

### Preload Script (Sécurité)

```javascript
// electron/preload.js
const { contextBridge, ipcRenderer } = require('electron');

// API exposée au renderer de façon sécurisée
const electronAPI = {
  // Database
  db: {
    query: (sql, params) => ipcRenderer.invoke('db:query', sql, params),
    transaction: (operations) => ipcRenderer.invoke('db:transaction', operations),
  },

  // File operations
  file: {
    importCSV: (filePath, options) => ipcRenderer.invoke('file:importCSV', filePath, options),
    selectCSV: () => ipcRenderer.invoke('file:selectCSV'),
  },

  // Export
  export: {
    toPDF: (data, filename) => ipcRenderer.invoke('export:pdf', data, filename),
    toExcel: (data, filename) => ipcRenderer.invoke('export:excel', data, filename),
  },

  // Python bridge
  python: {
    run: (script, args) => ipcRenderer.invoke('python:run', script, args),
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

  // Updates
  update: {
    onAvailable: (callback) => {
      ipcRenderer.on('update:available', callback);
    },
    onDownloaded: (callback) => {
      ipcRenderer.on('update:downloaded', callback);
    },
    install: () => ipcRenderer.send('update:install'),
  },

  // Navigation (depuis main)
  onNavigate: (callback) => {
    ipcRenderer.on('navigate', (_, path) => callback(path));
  },
};

// Exposer l'API
contextBridge.exposeInMainWorld('electronAPI', electronAPI);

// Types pour TypeScript (dans le renderer)
// declare global {
//   interface Window {
//     electronAPI: typeof electronAPI;
//   }
// }
```

---

## 🔧 Module 2: Services Backend (Main Process)

### Database Service (SQLite)

```javascript
// electron/services/database.cjs
const Database = require('better-sqlite3');
const fs = require('node:fs');
const path = require('node:path');

class DatabaseService {
  constructor(dbPath) {
    this.dbPath = dbPath;
    this.db = null;
    
    // S'assurer que le répertoire existe
    const dir = path.dirname(dbPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  }

  async initialize() {
    try {
      this.db = new Database(this.dbPath);
      
      // Mode WAL pour meilleures performances
      this.db.pragma('journal_mode = WAL');
      this.db.pragma('foreign_keys = ON');
      
      // Créer les tables si elles n'existent pas
      this.createTables();
      
      console.log('[Database] Initialized:', this.dbPath);
      return true;
    } catch (error) {
      console.error('[Database] Initialization error:', error);
      throw error;
    }
  }

  createTables() {
    // Transactions
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        label TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT,
        subcategory TEXT,
        type TEXT CHECK(type IN ('debit', 'credit')),
        account TEXT,
        notes TEXT,
        beneficiary TEXT,
        is_recurring BOOLEAN DEFAULT 0,
        is_validated BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );
      CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
      CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
    `);

    // Categories
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        emoji TEXT DEFAULT '📁',
        color TEXT DEFAULT '#64748B',
        type TEXT CHECK(type IN ('fixed', 'variable', 'income')),
        budget_amount REAL,
        is_active BOOLEAN DEFAULT 1
      );
    `);

    // Members
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        type TEXT CHECK(type IN ('primary', 'secondary')),
        email TEXT,
        color TEXT,
        is_active BOOLEAN DEFAULT 1
      );
    `);

    // Budgets
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        period TEXT DEFAULT 'monthly',
        year INTEGER,
        month INTEGER,
        UNIQUE(category, year, month)
      );
    `);

    // Settings
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );
    `);
  }

  query(sql, params = []) {
    if (!this.db) throw new Error('Database not initialized');
    
    const stmt = this.db.prepare(sql);
    
    if (sql.trim().toLowerCase().startsWith('select')) {
      return params.length > 0 ? stmt.all(...params) : stmt.all();
    } else {
      return params.length > 0 ? stmt.run(...params) : stmt.run();
    }
  }

  transaction(operations) {
    if (!this.db) throw new Error('Database not initialized');
    
    const transaction = this.db.transaction((ops) => {
      const results = [];
      for (const op of ops) {
        const stmt = this.db.prepare(op.sql);
        results.push(op.params ? stmt.run(...op.params) : stmt.run());
      }
      return results;
    });
    
    return transaction(operations);
  }

  close() {
    if (this.db) {
      this.db.close();
      this.db = null;
    }
  }
}

module.exports = { DatabaseService };
```

### File Import Service

```javascript
// electron/services/file-import.cjs
const fs = require('node:fs');
const path = require('node:path');
const { parse } = require('csv-parse/sync');

class FileImportService {
  constructor(dbService) {
    this.dbService = dbService;
  }

  async importCSV(filePath, options = {}) {
    try {
      // Lire le fichier
      const content = fs.readFileSync(filePath, 'utf-8');
      
      // Parser le CSV
      const records = parse(content, {
        columns: true,
        skip_empty_lines: true,
        delimiter: options.delimiter || ';',
        encoding: options.encoding || 'utf-8',
      });

      // Mapping des colonnes
      const mappings = options.mappings || this.detectMappings(records[0]);
      
      // Transformer et valider
      const transactions = records.map((record, index) => {
        return this.transformRecord(record, mappings, index);
      }).filter(t => t !== null);

      // Insérer dans la base
      const imported = this.insertTransactions(transactions);

      return {
        success: true,
        total: records.length,
        imported: imported.length,
        errors: records.length - imported.length,
        fileName: path.basename(filePath),
      };
    } catch (error) {
      console.error('[Import] Error:', error);
      return {
        success: false,
        error: error.message,
      };
    }
  }

  detectMappings(firstRow) {
    // Détection automatique des colonnes
    const columns = Object.keys(firstRow).map(c => c.toLowerCase());
    
    return {
      date: columns.find(c => c.includes('date') || c.includes('date')) || columns[0],
      label: columns.find(c => c.includes('libelle') || c.includes('label') || c.includes('description')) || columns[1],
      amount: columns.find(c => c.includes('montant') || c.includes('amount') || c.includes('credit') || c.includes('debit')) || columns[2],
      category: columns.find(c => c.includes('categorie') || c.includes('category')) || null,
    };
  }

  transformRecord(record, mappings, index) {
    try {
      const amount = this.parseAmount(record[mappings.amount]);
      
      return {
        date: this.parseDate(record[mappings.date]),
        label: record[mappings.label]?.trim() || 'Sans libellé',
        amount: Math.abs(amount),
        type: amount >= 0 ? 'credit' : 'debit',
        category: mappings.category ? record[mappings.category]?.trim() : null,
      };
    } catch (error) {
      console.warn(`[Import] Error on row ${index}:`, error.message);
      return null;
    }
  }

  parseAmount(value) {
    if (!value) return 0;
    // Gérer les formats: "1 234,56" ou "1,234.56" ou "1234.56"
    const cleaned = value.toString()
      .replace(/\s/g, '')
      .replace(',', '.');
    return parseFloat(cleaned) || 0;
  }

  parseDate(value) {
    if (!value) return new Date().toISOString().split('T')[0];
    
    // Formats supportés: DD/MM/YYYY, YYYY-MM-DD, DD-MM-YYYY
    const formats = [
      { regex: /(\d{2})\/(\d{2})\/(\d{4})/, fn: (m) => `${m[3]}-${m[2]}-${m[1]}` },
      { regex: /(\d{2})-(\d{2})-(\d{4})/, fn: (m) => `${m[3]}-${m[2]}-${m[1]}` },
      { regex: /(\d{4})-(\d{2})-(\d{2})/, fn: (m) => `${m[1]}-${m[2]}-${m[3]}` },
    ];

    for (const format of formats) {
      const match = value.toString().match(format.regex);
      if (match) return format.fn(match);
    }

    return new Date().toISOString().split('T')[0];
  }

  insertTransactions(transactions) {
    const inserted = [];
    
    for (const tx of transactions) {
      try {
        const result = this.dbService.query(`
          INSERT INTO transactions (date, label, amount, type, category)
          VALUES (?, ?, ?, ?, ?)
          ON CONFLICT DO NOTHING
          RETURNING id
        `, [tx.date, tx.label, tx.amount, tx.type, tx.category]);
        
        if (result.length > 0) {
          inserted.push({ ...tx, id: result[0].id });
        }
      } catch (error) {
        console.warn('[Import] Insert error:', error.message);
      }
    }
    
    return inserted;
  }
}

module.exports = { FileImportService };
```

---

## 🔧 Module 3: Renderer Process (React)

### IPC Hook

```typescript
// src/hooks/useIPC.ts
import { useCallback } from 'react';

// Types de l'API Electron
declare global {
  interface Window {
    electronAPI: {
      db: {
        query: (sql: string, params?: any[]) => Promise<any[]>;
        transaction: (operations: any[]) => Promise<any[]>;
      };
      file: {
        importCSV: (filePath: string, options?: any) => Promise<ImportResult>;
        selectCSV: () => Promise<string | null>;
      };
      export: {
        toPDF: (data: any, filename: string) => Promise<boolean>;
        toExcel: (data: any, filename: string) => Promise<boolean>;
      };
      app: {
        getVersion: () => Promise<string>;
        getPath: (name: string) => Promise<string>;
      };
      theme: {
        set: (theme: 'light' | 'dark' | 'system') => Promise<void>;
        get: () => Promise<'light' | 'dark'>;
      };
    };
  }
}

interface ImportResult {
  success: boolean;
  total?: number;
  imported?: number;
  errors?: number;
  fileName?: string;
  error?: string;
}

export function useIPC() {
  const api = window.electronAPI;

  const queryDB = useCallback(async (sql: string, params?: any[]) => {
    return api.db.query(sql, params);
  }, []);

  const importCSV = useCallback(async (options?: any) => {
    const filePath = await api.file.selectCSV();
    if (!filePath) return null;
    return api.file.importCSV(filePath, options);
  }, []);

  const exportToPDF = useCallback(async (data: any, filename: string) => {
    return api.export.toPDF(data, filename);
  }, []);

  return {
    queryDB,
    importCSV,
    exportToPDF,
    getVersion: api.app.getVersion,
    getPath: api.app.getPath,
    setTheme: api.theme.set,
    getTheme: api.theme.get,
  };
}
```

### Transactions Hook

```typescript
// src/hooks/useTransactions.ts
import { useState, useEffect, useCallback } from 'react';
import { useIPC } from './useIPC';

export interface Transaction {
  id: number;
  date: string;
  label: string;
  amount: number;
  category?: string;
  type: 'debit' | 'credit';
  is_validated?: boolean;
}

export function useTransactions(limit = 100) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { queryDB } = useIPC();

  const fetchTransactions = useCallback(async () => {
    try {
      setLoading(true);
      const results = await queryDB(
        `SELECT * FROM transactions ORDER BY date DESC LIMIT ?`,
        [limit]
      );
      setTransactions(results);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [queryDB, limit]);

  const addTransaction = useCallback(async (transaction: Omit<Transaction, 'id'>) => {
    try {
      await queryDB(`
        INSERT INTO transactions (date, label, amount, category, type)
        VALUES (?, ?, ?, ?, ?)
      `, [transaction.date, transaction.label, transaction.amount, transaction.category, transaction.type]);
      
      await fetchTransactions();
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add transaction');
      return false;
    }
  }, [queryDB, fetchTransactions]);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  return {
    transactions,
    loading,
    error,
    refresh: fetchTransactions,
    addTransaction,
  };
}
```

---

## 🔧 Module 4: Intégration avec Backend Python

### Stratégies d'Intégration

```
┌─────────────────────────────────────────────────────────────────┐
│              STRATÉGIES D'INTÉGRATION PYTHON                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  OPTION A: FastAPI Externe (Recommandé pour le développement)    │
│  ┌──────────────┐         ┌──────────────┐                      │
│  │   Electron   │ ←────→  │  FastAPI     │                      │
│  │   (Renderer) │  HTTP   │  (localhost) │                      │
│  └──────────────┘         └──────────────┘                      │
│                                  ↓                              │
│                           ┌──────────────┐                      │
│                           │   SQLite     │                      │
│                           └──────────────┘                      │
│                                                                  │
│  OPTION B: Python Embarqué (Pour la production packagée)        │
│  ┌──────────────────────────────────────────────┐              │
│  │              Electron App                     │              │
│  │  ┌──────────┐      ┌──────────────────────┐  │              │
│  │  │ Renderer │ ←──→ │  Python (embedded)   │  │              │
│  │  └──────────┘ IPC  │  - python-shell      │  │              │
│  │                    │  - spawn process     │  │              │
│  │                    └──────────────────────┘  │              │
│  │                              ↓               │              │
│  │                       ┌──────────────┐       │              │
│  │                       │   SQLite     │       │              │
│  │                       └──────────────┘       │              │
│  └──────────────────────────────────────────────┘              │
│                                                                  │
│  OPTION C: Hybrid (Recommandé pour FinancePerso)                │
│  ┌──────────────┐         ┌──────────────┐                      │
│  │   Electron   │ ←────→  │  FastAPI     │  ← Mode dev         │
│  │              │  HTTP   │  (dev server)│                      │
│  │  ┌──────────┐         └──────────────┘                      │
│  │  │ Python   │ ←────→  ┌──────────────┐  ← Mode prod         │
│  │  │ embedded │  IPC    │  Local ML    │                      │
│  │  └──────────┘         └──────────────┘                      │
│  └──────────────┘                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Python Bridge Service

```javascript
// electron/services/python-bridge.cjs
const { PythonShell } = require('python-shell');
const path = require('node:path');
const { spawn } = require('node:child_process');

class PythonBridge {
  constructor() {
    this.fastAPIProcess = null;
    this.apiPort = 8000;
    this.apiUrl = `http://localhost:${this.apiPort}`;
  }

  // Mode développement: FastAPI externe
  async startFastAPIDev() {
    return new Promise((resolve, reject) => {
      const pythonPath = path.join(__dirname, '../../../.venv/bin/python');
      const mainPy = path.join(__dirname, '../../../modules/api/main.py');
      
      this.fastAPIProcess = spawn(pythonPath, [
        '-m', 'uvicorn', 'modules.api.main:app',
        '--host', '0.0.0.0',
        '--port', this.apiPort.toString(),
        '--reload'
      ], {
        cwd: path.join(__dirname, '../../..'),
        env: { ...process.env, PYTHONPATH: path.join(__dirname, '../../..') }
      });

      this.fastAPIProcess.stdout.on('data', (data) => {
        console.log('[FastAPI]', data.toString());
        if (data.toString().includes('Application startup complete')) {
          resolve(true);
        }
      });

      this.fastAPIProcess.stderr.on('data', (data) => {
        console.error('[FastAPI Error]', data.toString());
      });

      this.fastAPIProcess.on('error', reject);
      
      // Timeout de sécurité
      setTimeout(() => resolve(true), 5000);
    });
  }

  // Mode production: Exécution script simple
  async runScript(scriptName, args = []) {
    const options = {
      mode: 'json',
      pythonPath: path.join(__dirname, '../../../.venv/bin/python'),
      pythonOptions: ['-u'],
      scriptPath: path.join(__dirname, '../../../scripts'),
      args: args,
    };

    return new Promise((resolve, reject) => {
      PythonShell.run(scriptName, options, (err, results) => {
        if (err) reject(err);
        else resolve(results ? results[0] : null);
      });
    });
  }

  // Catégorisation IA via Python
  async categorizeTransaction(label, amount) {
    return this.runScript('categorize.py', [label, amount.toString()]);
  }

  // Prédictions ML
  async predictCashflow(months = 3) {
    return this.runScript('predict_cashflow.py', [months.toString()]);
  }

  stop() {
    if (this.fastAPIProcess) {
      this.fastAPIProcess.kill();
      this.fastAPIProcess = null;
    }
  }
}

module.exports = { PythonBridge };
```

---

## 🔧 Module 5: Build et Distribution

### Configuration Forge

```javascript
// forge.config.js
const { FusesPlugin } = require('@electron-forge/plugin-fuses');
const { FuseV1Options, FuseVersion } = require('@electron/fuses');

module.exports = {
  packagerConfig: {
    asar: true,
    icon: './assets/icon',
    appBundleId: 'com.financeperso.app',
    appCategoryType: 'public.app-category.finance',
    osxSign: {},
    osxNotarize: {
      tool: 'notarytool',
      appleId: process.env.APPLE_ID,
      appleIdPassword: process.env.APPLE_PASSWORD,
      teamId: process.env.APPLE_TEAM_ID,
    },
  },
  rebuildConfig: {},
  makers: [
    {
      name: '@electron-forge/maker-squirrel',
      config: {
        name: 'FinancePerso',
        authors: 'FinancePerso Team',
        exe: 'FinancePerso.exe',
        setupExe: 'FinancePerso-Setup.exe',
      },
    },
    {
      name: '@electron-forge/maker-zip',
      platforms: ['darwin'],
    },
    {
      name: '@electron-forge/maker-deb',
      config: {
        options: {
          maintainer: 'FinancePerso Team',
          homepage: 'https://financeperso.app',
          categories: ['Office', 'Finance'],
        },
      },
    },
    {
      name: '@electron-forge/maker-rpm',
      config: {},
    },
  ],
  plugins: [
    {
      name: '@electron-forge/plugin-vite',
      config: {
        build: [
          {
            entry: 'electron/main.js',
            config: 'vite.main.config.ts',
          },
          {
            entry: 'electron/preload.js',
            config: 'vite.preload.config.ts',
          },
        ],
        renderer: [
          {
            name: 'main_window',
            config: 'vite.renderer.config.ts',
          },
        ],
      },
    },
    new FusesPlugin({
      version: FuseVersion.V1,
      [FuseV1Options.RunAsNode]: false,
      [FuseV1Options.EnableCookieEncryption]: true,
      [FuseV1Options.EnableNodeOptionsEnvironmentVariable]: false,
      [FuseV1Options.EnableNodeCliInspectArguments]: false,
      [FuseV1Options.EnableEmbeddedAsarIntegrityValidation]: true,
      [FuseV1Options.OnlyLoadAppFromAsar]: true,
    }),
  ],
  publishers: [
    {
      name: '@electron-forge/publisher-github',
      config: {
        repository: {
          owner: 'votre-org',
          name: 'financeperso',
        },
        prerelease: false,
        draft: true,
      },
    },
  ],
};
```

### Scripts NPM

```json
{
  "scripts": {
    "start": "electron-forge start",
    "package": "electron-forge package",
    "make": "electron-forge make",
    "make:mac": "electron-forge make --platform=darwin",
    "make:win": "electron-forge make --platform=win32",
    "make:linux": "electron-forge make --platform=linux",
    "publish": "electron-forge publish",
    "lint": "eslint . --ext .ts,.tsx",
    "typecheck": "tsc --noEmit"
  }
}
```

---

## 📋 Checklist Développement Electron

### Phase 1: Setup Initial

- [ ] Créer structure dossiers (electron/, src/)
- [ ] Configurer vite.main.config.ts
- [ ] Configurer vite.renderer.config.ts
- [ ] Configurer vite.preload.config.ts
- [ ] Créer main.js avec gestion cycle de vie
- [ ] Créer preload.js avec contextBridge
- [ ] Créer renderer.tsx (entry React)
- [ ] Configurer Tailwind CSS v4
- [ ] Tester `npm run start`

### Phase 2: Services Core

- [ ] Implémenter DatabaseService (better-sqlite3)
- [ ] Créer schéma DB (transactions, categories, budgets)
- [ ] Implémenter FileImportService (CSV)
- [ ] Configurer IPC handlers
- [ ] Créer hooks React (useIPC, useTransactions)
- [ ] Tester import CSV end-to-end

### Phase 3: UI Components

- [ ] Configurer shadcn/ui
- [ ] Créer layout principal (sidebar + main)
- [ ] Page Dashboard avec KPIs
- [ ] Page Transactions (table + filtres)
- [ ] Page Import (wizard)
- [ ] Page Settings

### Phase 4: Python Integration

- [ ] Choisir stratégie (FastAPI externe ou embedded)
- [ ] Implémenter PythonBridge
- [ ] Créer endpoints catégorisation
- [ ] Intégrer prédictions ML
- [ ] Tester intégration complète

### Phase 5: Packaging

- [ ] Configurer forge.config.js
- [ ] Ajouter icônes pour toutes les plateformes
- [ ] Configurer auto-updater
- [ ] Tester build local (`npm run make`)
- [ ] Tester sur Windows/macOS/Linux

### Phase 6: Distribution

- [ ] Configurer GitHub Actions pour build
- [ ] Configurer code signing (Apple, Windows)
- [ ] Tester auto-update
- [ ] Créer release notes
- [ ] Publier v1.0.0

---

## 🔗 Coordination avec Autres Agents

### Dépendances

| Agent | Rôle | Interaction |
|-------|------|-------------|
| AGENT-023 (FastAPI) | Backend API | Electron appelle API pour features avancées |
| AGENT-009 (UI) | Design System | Réutiliser tokens couleurs, composants |
| AGENT-024 (React) | Frontend React | Partager hooks, patterns React |
| AGENT-001 (Database) | Schéma DB | Aligner schéma SQLite avec PostgreSQL |
| AGENT-003 (DevOps) | CI/CD | Build et distribution Electron |
| AGENT-005 (AI) | Catégorisation | Appeler via PythonBridge |

### Protocole: Desktop App Launch

```python
"""
Quand AGENT-025 lance l'app Electron.
"""

def on_desktop_app_launch():
    """
    Handler lancement application desktop.
    """
    # Vérifier si FastAPI doit démarrer
    if is_dev_mode():
        notify_agent('023', {
            'event': 'START_FASTAPI_SERVER',
            'port': 8000
        })
    
    # Initialiser base de données locale
    notify_agent('001', {
        'event': 'INIT_SQLITE_DB',
        'path': '${userData}/finance.db'
    })
    
    # Mettre à jour UI agent
    notify_agent('009', {
        'event': 'ADAPT_FOR_DESKTOP',
        'constraints': ['electron', 'local_db', 'offline_capable']
    })
```

### Protocole: Data Sync

```python
"""
Synchronisation entre SQLite locale et backend cloud.
"""

def on_sync_requested(direction: str):
    """
    Handler synchronisation données.
    
    Args:
        direction: 'local_to_cloud' | 'cloud_to_local' | 'bidirectional'
    """
    if direction in ['local_to_cloud', 'bidirectional']:
        # Envoyer transactions locales vers cloud
        local_tx = get_local_transactions(unsynced_only=True)
        notify_agent('023', {
            'event': 'BULK_IMPORT_TRANSACTIONS',
            'transactions': local_tx
        })
    
    if direction in ['cloud_to_local', 'bidirectional']:
        # Récupérer transactions cloud
        notify_agent('023', {
            'event': 'FETCH_TRANSACTIONS',
            'callback': 'import_to_sqlite'
        })
```

---

## 🚀 Mode d'Emploi

### Commandes Essentielles

```bash
# Installation
cd financeperso-electron
npm install

# Développement (hot reload)
npm run start

# Build pour toutes les plateformes
npm run make

# Build spécifique
npm run make:mac
npm run make:win
npm run make:linux

# Publication
npm run publish
```

### Débogage

```bash
# Ouvrir DevTools
# Dans main.js: mainWindow.webContents.openDevTools()

# Logs main process
# Consulter terminal où `npm run start` est exécuté

# Logs renderer
# Consulter Console dans DevTools
```

---

## 📚 Ressources

- [Electron Documentation](https://www.electronjs.org/docs/latest)
- [Electron Forge](https://www.electronforge.io/)
- [better-sqlite3](https://github.com/WiseLibs/better-sqlite3)
- [Vite Plugin Electron](https://github.com/electron-vite/vite-plugin-electron)
- [shadcn/ui](https://ui.shadcn.com/)

---

**Version**: 1.0  
**Date**: 2026-03-12  
**Agent ID**: AGENT-025  
**Status**: PRÊT À L'EMPLOI
