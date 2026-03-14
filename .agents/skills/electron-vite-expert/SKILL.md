# Electron + Vite Expert Skill

> Configuration pour applications Electron avec Vite, React, TypeScript et SQLite (sqlite3). Basé sur l'architecture réelle de financeperso-electron.

---

## 🎯 Architecture Réelle du Projet

Le projet utilise **@electron-forge** avec plugin Vite (pas electron-forge standard) :

```
financeperso-electron/
├── src/
│   ├── main.js              # Main process (CommonJS)
│   ├── preload.js           # Preload script (CommonJS)
│   ├── App.tsx              # Root React
│   ├── pages/               # 11 pages React
│   ├── components/          # Composants React/shadcn
│   ├── hooks/               # Hooks personnalisés
│   ├── services/            # Services métier
│   ├── lib/                 # Utilitaires
│   └── types/               # Types TypeScript
├── src/services/
│   ├── database.js          # SQLite service (sqlite3 async)
│   ├── file-import.cjs      # Import CSV
│   └── ai-service.cjs       # Service IA
├── tests/e2e/               # Tests Playwright
├── forge.config.js          # Config Electron Forge
├── vite.main.config.mjs     # Vite config main
├── vite.preload.config.mjs  # Vite config preload
├── vite.renderer.config.mjs # Vite config renderer
└── package.json
```

---

## 🏗️ Stack Technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Electron | @electron-forge | 33.3.2 |
| React | React | 18.3.1 |
| TypeScript | TypeScript | 5.6.2 |
| Build | Vite (via forge) | 5.4.11 |
| UI | Tailwind CSS + shadcn/ui | 3.4.15 |
| Charts | Recharts | 2.13.3 |
| Database | SQLite (sqlite3) | 5.1.7 |
| Icons | Lucide React | 0.460.0 |
| Tests | Playwright | 1.49.0 |

---

## ⚙️ Configuration Clé

### forge.config.js

```javascript
const { FusesPlugin } = require('@electron-forge/plugin-fuses');
const { FuseV1Options, FuseVersion } = require('@electron/fuses');

module.exports = {
  packagerConfig: {
    asar: true,
    icon: './assets/icon',
  },
  rebuildConfig: {},
  makers: [
    {
      name: '@electron-forge/maker-squirrel',
      config: {},
    },
    {
      name: '@electron-forge/maker-zip',
      platforms: ['darwin'],
    },
    {
      name: '@electron-forge/maker-deb',
      config: {},
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
            entry: 'src/main.js',
            config: 'vite.main.config.mjs',
          },
          {
            entry: 'src/preload.js',
            config: 'vite.preload.config.mjs',
          },
        ],
        renderer: [
          {
            name: 'main_window',
            config: 'vite.renderer.config.mjs',
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
};
```

### vite.renderer.config.mjs

```javascript
import { defineConfig } from 'vite';
import path from 'path';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'recharts-vendor': ['recharts'],
        },
      },
    },
  },
});
```

### vite.main.config.mjs

```javascript
import { defineConfig } from 'vite';
import path from 'path';
import fs from 'fs';

const copyFilesPlugin = () => ({
  name: 'copy-files',
  writeBundle() {
    const srcDir = path.resolve(__dirname, 'src/services');
    const destDir = path.resolve(__dirname, '.vite/build/services');
    
    if (!fs.existsSync(destDir)) {
      fs.mkdirSync(destDir, { recursive: true });
    }
    
    ['database.js', 'file-import.cjs', 'ai-service.cjs', 'updater.cjs'].forEach(file => {
      if (fs.existsSync(path.join(srcDir, file))) {
        fs.copyFileSync(path.join(srcDir, file), path.join(destDir, file));
      }
    });
  }
});

export default defineConfig({
  plugins: [copyFilesPlugin()],
  build: {
    rollupOptions: {
      external: ['electron', 'sqlite3', 'node:*'],
    },
  },
});
```

---

## 🗄️ SQLite avec sqlite3 (Async)

### Pourquoi sqlite3 et pas better-sqlite3 ?

- **better-sqlite3**: Synchrone, plus rapide, mais nécessite compilation native (C++20)
- **sqlite3**: Asynchrone, plus simple, pas de compilation native requise

### Pattern DatabaseService

```javascript
// src/services/database.js
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const { app } = require('electron');

class DatabaseService {
  constructor(dbPath) {
    this.dbPath = dbPath;
    this.db = null;
  }

  initialize() {
    return new Promise((resolve, reject) => {
      this.db = new sqlite3.Database(this.dbPath, (err) => {
        if (err) reject(err);
        else this.createTables().then(() => resolve(true)).catch(reject);
      });
    });
  }

  // Pattern: Promisify tous les appels sqlite3
  async getAllTransactions(limit = 100, offset = 0) {
    return new Promise((resolve, reject) => {
      this.db.all(
        `SELECT * FROM transactions ORDER BY date DESC LIMIT ? OFFSET ?`,
        [limit, offset],
        (err, rows) => err ? reject(err) : resolve(rows)
      );
    });
  }

  async run(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.run(sql, params, function(err) {
        if (err) reject(err);
        else resolve({ id: this.lastID, changes: this.changes });
      });
    });
  }
}

module.exports = { DatabaseService };
```

### Initialisation dans main.js

```javascript
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { DatabaseService } = require('./services/database.js');

let dbService;

async function initializeServices() {
  const dbPath = path.join(app.getPath('userData'), 'finance.db');
  dbService = new DatabaseService(dbPath);
  await dbService.initialize();
}

app.whenReady().then(async () => {
  await initializeServices();
  createWindow();
});

// IPC Handlers
ipcMain.handle('db:get-all-transactions', async (_, limit, offset) => {
  return await dbService.getAllTransactions(limit, offset);
});
```

---

## 🔌 IPC Communication

### Preload Script (preload.js)

```javascript
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Database
  db: {
    getAllTransactions: (limit, offset) => 
      ipcRenderer.invoke('db:get-all-transactions', limit, offset),
    addTransaction: (transaction) => 
      ipcRenderer.invoke('db:add-transaction', transaction),
    // ... autres méthodes
  },
  
  // File operations
  file: {
    selectCSV: () => ipcRenderer.invoke('file:select-csv'),
    importCSV: (filePath, options) => 
      ipcRenderer.invoke('file:import-csv', filePath, options),
  },
  
  // AI
  ai: {
    categorize: (label, amount) => 
      ipcRenderer.invoke('ai:categorize', label, amount),
    getSettings: () => ipcRenderer.invoke('ai:get-settings'),
    saveSettings: (settings) => ipcRenderer.invoke('ai:save-settings', settings),
  },
  
  // App info
  app: {
    getVersion: () => ipcRenderer.invoke('app:get-version'),
    getPath: (name) => ipcRenderer.invoke('app:get-path', name),
  },
});
```

### Types TypeScript (types/electron.d.ts)

```typescript
export interface ElectronAPI {
  db: {
    getAllTransactions: (limit?: number, offset?: number) => Promise<Transaction[]>;
    addTransaction: (transaction: Partial<Transaction>) => Promise<{ id: number }>;
    // ...
  };
  file: {
    selectCSV: () => Promise<string | null>;
    importCSV: (filePath: string, options: ImportOptions) => Promise<ImportResult>;
  };
  ai: {
    categorize: (label: string, amount: number) => Promise<CategorizationResult>;
    getSettings: () => Promise<AISettings>;
    saveSettings: (settings: AISettings) => Promise<void>;
  };
  app: {
    getVersion: () => Promise<string>;
    getPath: (name: string) => Promise<string>;
  };
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}

export {};
```

---

## 🧪 Tests Playwright

### Configuration playwright.config.ts

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
```

### Pattern de test E2E

```typescript
// tests/e2e/dashboard.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
  });

  test('affiche les KPIs', async ({ page }) => {
    await expect(page.getByText('Revenus du mois')).toBeVisible();
    await expect(page.getByText('Dépenses du mois')).toBeVisible();
  });

  test('navigation vers transactions', async ({ page }) => {
    await page.getByRole('link', { name: /transactions/i }).click();
    await expect(page).toHaveURL(/.*transactions/);
  });
});
```

---

## 📦 Build & Distribution

### Scripts package.json

```json
{
  "scripts": {
    "start": "electron-forge start",
    "package": "electron-forge package",
    "make": "electron-forge make",
    "publish": "electron-forge publish",
    "build": "npm run package",
    "test": "playwright test",
    "test:ui": "playwright test --ui",
    "lint": "eslint . --ext .ts,.tsx",
    "lint:fix": "eslint . --ext .ts,.tsx --fix"
  }
}
```

### CI GitHub Actions

```yaml
# .github/workflows/build.yml
name: Build and Test

on: [push, pull_request]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [macos-latest, windows-latest, ubuntu-latest]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Build application
        run: npm run make
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.os }}-build
          path: out/
```

---

## 🚫 Ce qu'il faut éviter

1. **Ne PAS utiliser** `import { app } from 'electron'` dans main.js
   - ✅ `const { app } = require('electron')`
   - ❌ `import { app } from 'electron'`

2. **Ne PAS utiliser** `.ts` pour main/preload
   - ✅ `.js` ou `.cjs`
   - ❌ `.ts`

3. **Ne PAS appeler sqlite3 depuis renderer**
   - ✅ Toujours passer par IPC
   - ❌ `new sqlite3.Database()` dans React

4. **Ne PAS oublier external dans vite.main.config**
   - ✅ `external: ['electron', 'sqlite3', 'node:*']`
   - ❌ Bundler sqlite3 avec Vite

5. **Ne PAS utiliser better-sqlite3 sans build natif**
   - ✅ Utiliser sqlite3 pour éviter les problèmes de compilation
   - ❌ better-sqlite3 sans config native correcte

---

## ✅ Checklist Validation

- [ ] `npm start` lance l'application
- [ ] Main process démarre (logs console)
- [ ] Preload script chargé (`window.electronAPI` défini)
- [ ] Database initialisée
- [ ] IPC communication fonctionne
- [ ] React s'hydrate correctement
- [ ] Hot reload fonctionne
- [ ] Build production réussit
- [ ] Tests E2E passent

---

## 📚 Ressources

- [Electron Forge](https://www.electronforge.io/)
- [Vite Plugin Electron](https://github.com/electron/forge/tree/main/packages/plugin/vite)
- [sqlite3](https://github.com/TryGhost/node-sqlite3)
- [Playwright](https://playwright.dev/)

---

**Version**: 2.0 - Mis à jour pour financeperso-electron  
**Date**: 2026-03-13
