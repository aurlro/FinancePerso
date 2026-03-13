# Skill: Electron-Python Synchronization

> Guide de synchronisation entre l'application Electron (frontend) et le backend Python (FastAPI/ML) pour FinancePerso.

---

## 🎯 Objectif

Assurer une communication fluide et sécurisée entre :
- **Electron Main Process** (Node.js) - Accès natif au système
- **Renderer Process** (React/TypeScript) - Interface utilisateur
- **Backend Python** (FastAPI) - Logique métier et ML

---

## 🏗️ Architecture de Communication

### Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COMMUNICATION FLOW                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐         ┌─────────────────┐         ┌───────────────┐ │
│  │  React Renderer │ ←─────→ │  Electron Main  │ ←─────→ │  Python API   │ │
│  │  (TypeScript)   │   IPC   │  (Node.js)      │  HTTP   │  (FastAPI)    │ │
│  └────────┬────────┘         └────────┬────────┘         └───────┬───────┘ │
│           │                           │                          │         │
│           │  window.electronAPI.*     │  fetch/axios             │         │
│           │                           │                          │         │
│           ▼                           ▼                          ▼         │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    COMMUNICATION PATTERNS                            │  │
│  │                                                                      │  │
│  │  Pattern A: Direct IPC (Renderer ↔ Main)                            │  │
│  │  ┌──────────┐    contextBridge    ┌──────────┐                      │  │
│  │  │ Renderer │ ←────────────────→  │  Main    │                      │  │
│  │  └──────────┘                     └──────────┘                      │  │
│  │         ↑                                          │                │  │
│  │         └──────────────────────────────────────────┘                │  │
│  │                    Accès fichier natif, DB locale                   │  │
│  │                                                                      │  │
│  │  Pattern B: HTTP API (Renderer/Main ↔ Python)                       │  │
│  │  ┌──────────┐         ┌──────────┐         ┌──────────┐            │  │
│  │  │ Renderer │ ──────→ │   Main   │ ──────→ │  Python  │            │  │
│  │  │          │  fetch  │ (proxy)  │  HTTP   │  FastAPI │            │  │
│  │  └──────────┘         └──────────┘         └──────────┘            │  │
│  │         ↑                                              │            │  │
│  │         └──────────────────────────────────────────────┘            │  │
│  │                    Appels API REST standards                        │  │
│  │                                                                      │  │
│  │  Pattern C: Hybrid (Recommandé)                                     │  │
│  │  ┌──────────┐         ┌──────────┐         ┌──────────┐            │  │
│  │  │ Renderer │ ←─────→ │   Main   │ ←─────→ │  Python  │            │  │
│  │  │          │   IPC   │          │   IPC   │  (spawn)  │            │  │
│  │  └──────────┘         └──────────┘         └──────────┘            │  │
│  │                    Scripts ML/Python embarqués                      │  │
│  │                                                                      │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Pattern A: IPC Direct (Renderer ↔ Main)

### Use Cases
- Accès au système de fichiers natif
- Base de données SQLite locale (better-sqlite3)
- Notifications système
- Auto-updater
- Barre de menu / Tray

### Implémentation

#### 1. Preload Script (exposition sécurisée)

```typescript
// electron/preload.ts
import { contextBridge, ipcRenderer } from 'electron';

export interface ElectronAPI {
  // Database
  db: {
    query: (sql: string, params?: unknown[]) => Promise<unknown[]>;
    transaction: (operations: SQLOperation[]) => Promise<unknown[]>;
  };
  
  // File System
  file: {
    selectCSV: () => Promise<string | null>;
    readCSV: (path: string) => Promise<CSVRow[]>;
    exportPDF: (data: ExportData, filename: string) => Promise<boolean>;
  };
  
  // App
  app: {
    getVersion: () => Promise<string>;
    getPath: (name: 'home' | 'userData' | 'downloads') => Promise<string>;
  };
  
  // Theme
  theme: {
    set: (theme: 'light' | 'dark' | 'system') => Promise<void>;
    get: () => Promise<'light' | 'dark'>;
    onChanged: (callback: (theme: 'light' | 'dark') => void) => void;
  };
}

const api: ElectronAPI = {
  db: {
    query: (sql, params) => ipcRenderer.invoke('db:query', sql, params),
    transaction: (operations) => ipcRenderer.invoke('db:transaction', operations),
  },
  file: {
    selectCSV: () => ipcRenderer.invoke('file:selectCSV'),
    readCSV: (path) => ipcRenderer.invoke('file:readCSV', path),
    exportPDF: (data, filename) => ipcRenderer.invoke('file:exportPDF', data, filename),
  },
  app: {
    getVersion: () => ipcRenderer.invoke('app:getVersion'),
    getPath: (name) => ipcRenderer.invoke('app:getPath', name),
  },
  theme: {
    set: (theme) => ipcRenderer.invoke('theme:set', theme),
    get: () => ipcRenderer.invoke('theme:get'),
    onChanged: (callback) => {
      ipcRenderer.on('theme:changed', (_, theme) => callback(theme));
    },
  },
};

contextBridge.exposeInMainWorld('electronAPI', api);
```

#### 2. TypeScript Types (Renderer)

```typescript
// src/types/electron.d.ts
export interface SQLOperation {
  sql: string;
  params?: unknown[];
}

export interface CSVRow {
  [key: string]: string;
}

export interface ExportData {
  title: string;
  transactions: Transaction[];
  summary: {
    totalIncome: number;
    totalExpense: number;
    balance: number;
  };
}

export interface Transaction {
  id: number;
  date: string;
  label: string;
  amount: number;
  category?: string;
  type: 'debit' | 'credit';
}

// Déclaration globale
declare global {
  interface Window {
    electronAPI: import('../electron/preload').ElectronAPI;
  }
}

export {};
```

#### 3. Main Process Handlers

```typescript
// electron/main.ts
import { app, ipcMain, dialog, BrowserWindow } from 'electron';
import { DatabaseService } from './services/database';
import { FileService } from './services/file';

// Services
let dbService: DatabaseService;
let fileService: FileService;

// Initialize services
async function initializeServices() {
  const userDataPath = app.getPath('userData');
  
  dbService = new DatabaseService(`${userDataPath}/finance.db`);
  await dbService.initialize();
  
  fileService = new FileService();
}

// IPC Handlers
function setupIpcHandlers() {
  // Database handlers
  ipcMain.handle('db:query', async (_, sql: string, params?: unknown[]) => {
    try {
      return await dbService.query(sql, params);
    } catch (error) {
      console.error('[IPC] DB Query error:', error);
      throw error;
    }
  });

  ipcMain.handle('db:transaction', async (_, operations: SQLOperation[]) => {
    return await dbService.transaction(operations);
  });

  // File handlers
  ipcMain.handle('file:selectCSV', async () => {
    const window = BrowserWindow.getFocusedWindow();
    if (!window) return null;
    
    const result = await dialog.showOpenDialog(window, {
      properties: ['openFile'],
      filters: [
        { name: 'Fichiers CSV', extensions: ['csv'] },
        { name: 'Tous les fichiers', extensions: ['*'] }
      ]
    });
    
    return result.canceled ? null : result.filePaths[0];
  });

  ipcMain.handle('file:readCSV', async (_, filePath: string) => {
    return await fileService.readCSV(filePath);
  });

  ipcMain.handle('file:exportPDF', async (_, data: ExportData, filename: string) => {
    return await fileService.exportPDF(data, filename);
  });

  // App handlers
  ipcMain.handle('app:getVersion', () => app.getVersion());
  ipcMain.handle('app:getPath', (_, name: string) => app.getPath(name));

  // Theme handlers
  ipcMain.handle('theme:set', async (_, theme: 'light' | 'dark' | 'system') => {
    nativeTheme.themeSource = theme;
  });

  ipcMain.handle('theme:get', () => {
    return nativeTheme.shouldUseDarkColors ? 'dark' : 'light';
  });

  // Notify renderer when system theme changes
  nativeTheme.on('updated', () => {
    BrowserWindow.getAllWindows().forEach(window => {
      window.webContents.send('theme:changed', 
        nativeTheme.shouldUseDarkColors ? 'dark' : 'light'
      );
    });
  });
}
```

#### 4. React Hook (utilisation côté renderer)

```typescript
// src/hooks/useElectron.ts
import { useCallback } from 'react';

export function useElectron() {
  const api = window.electronAPI;

  const queryDB = useCallback(async (sql: string, params?: unknown[]) => {
    return api.db.query(sql, params);
  }, []);

  const selectCSV = useCallback(async () => {
    return api.file.selectCSV();
  }, []);

  const readCSV = useCallback(async (path: string) => {
    return api.file.readCSV(path);
  }, []);

  const exportPDF = useCallback(async (data: ExportData, filename: string) => {
    return api.file.exportPDF(data, filename);
  }, []);

  const getAppVersion = useCallback(async () => {
    return api.app.getVersion();
  }, []);

  return {
    queryDB,
    selectCSV,
    readCSV,
    exportPDF,
    getAppVersion,
    setTheme: api.theme.set,
    getTheme: api.theme.get,
    onThemeChanged: api.theme.onChanged,
  };
}
```

---

## 📦 Pattern B: HTTP API (FastAPI)

### Use Cases
- Opérations complexes métier
- Catégorisation IA (ML)
- Prédictions cashflow
- Authentification JWT
- Synchronisation cloud

### Implémentation

#### 1. Démarrage FastAPI depuis Electron

```typescript
// electron/services/python-bridge.ts
import { spawn, ChildProcess } from 'child_process';
import path from 'node:path';
import { app } from 'electron';

export class PythonBridge {
  private fastAPIProcess: ChildProcess | null = null;
  private readonly port = 8000;
  private readonly apiUrl = `http://localhost:${this.port}`;

  async startFastAPI(): Promise<boolean> {
    return new Promise((resolve, reject) => {
      // Détecter l'environnement
      const isDev = !app.isPackaged;
      
      // Chemins
      const pythonPath = isDev 
        ? path.join(app.getAppPath(), '../.venv/bin/python')
        : path.join(process.resourcesPath, 'python', 'python');
      
      const apiModule = isDev
        ? 'modules.api.main:app'
        : 'api.main:app';

      // Démarrer uvicorn
      this.fastAPIProcess = spawn(pythonPath, [
        '-m', 'uvicorn',
        apiModule,
        '--host', '0.0.0.0',
        '--port', this.port.toString(),
        '--log-level', 'info'
      ], {
        cwd: isDev ? app.getAppPath() : process.resourcesPath,
        env: {
          ...process.env,
          PYTHONPATH: isDev ? app.getAppPath() : process.resourcesPath
        }
      });

      // Logs
      this.fastAPIProcess.stdout?.on('data', (data) => {
        console.log('[FastAPI]', data.toString());
      });

      this.fastAPIProcess.stderr?.on('data', (data) => {
        console.error('[FastAPI Error]', data.toString());
      });

      // Attendre le démarrage
      this.fastAPIProcess.stdout?.on('data', (data) => {
        if (data.toString().includes('Application startup complete')) {
          console.log('[PythonBridge] FastAPI started on', this.apiUrl);
          resolve(true);
        }
      });

      // Timeout de sécurité
      setTimeout(() => {
        if (this.fastAPIProcess?.pid) {
          resolve(true);
        } else {
          reject(new Error('FastAPI startup timeout'));
        }
      }, 10000);
    });
  }

  stopFastAPI(): void {
    if (this.fastAPIProcess) {
      this.fastAPIProcess.kill('SIGTERM');
      this.fastAPIProcess = null;
    }
  }

  getApiUrl(): string {
    return this.apiUrl;
  }
}
```

#### 2. API Client TypeScript

```typescript
// src/services/api-client.ts
import { Transaction, Category, Budget } from '@/types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

class APIClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  setToken(token: string) {
    this.token = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new APIError(response.status, error.detail || 'Request failed');
    }

    return response.json();
  }

  // Transactions
  async getTransactions(params?: { limit?: number; category?: string }) {
    const query = new URLSearchParams();
    if (params?.limit) query.set('limit', params.limit.toString());
    if (params?.category) query.set('category', params.category);
    
    return this.request<Transaction[]>(`/transactions?${query}`);
  }

  async createTransaction(data: Omit<Transaction, 'id'>) {
    return this.request<Transaction>('/transactions', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  // Catégorisation IA
  async categorizeTransaction(label: string, amount: number) {
    return this.request<{ category: string; confidence: number }>('/ai/categorize', {
      method: 'POST',
      body: JSON.stringify({ label, amount })
    });
  }

  // Prédictions
  async predictCashflow(months: number = 3) {
    return this.request<{
      predictions: Array<{ month: string; amount: number }>;
      confidence: number;
    }>(`/ai/predict/cashflow?months=${months}`);
  }

  // Dashboard stats
  async getDashboardStats(period?: string) {
    const query = period ? `?period=${period}` : '';
    return this.request<{
      totalIncome: number;
      totalExpense: number;
      balance: number;
      byCategory: Record<string, number>;
    }>(`/dashboard/stats${query}`);
  }
}

export class APIError extends Error {
  constructor(
    public statusCode: number,
    message: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export const apiClient = new APIClient();
```

#### 3. React Query Integration

```typescript
// src/hooks/useAPI.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/services/api-client';

// Transactions
export function useTransactions(params?: { limit?: number }) {
  return useQuery({
    queryKey: ['transactions', params],
    queryFn: () => apiClient.getTransactions(params),
  });
}

export function useCreateTransaction() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: apiClient.createTransaction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

// AI Categorization
export function useCategorize() {
  return useMutation({
    mutationFn: ({ label, amount }: { label: string; amount: number }) =>
      apiClient.categorizeTransaction(label, amount),
  });
}

// Dashboard
export function useDashboardStats(period?: string) {
  return useQuery({
    queryKey: ['dashboard', 'stats', period],
    queryFn: () => apiClient.getDashboardStats(period),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
```

---

## 📦 Pattern C: Scripts Python Embarqués

### Use Cases
- Scripts ML simples (catégorisation offline)
- Traitement de données rapide
- Utilitaires Python sans démarrer FastAPI

### Implémentation

```typescript
// electron/services/python-scripts.ts
import { PythonShell } from 'python-shell';
import path from 'node:path';
import { app } from 'electron';

export class PythonScripts {
  private getPythonPath(): string {
    return app.isPackaged
      ? path.join(process.resourcesPath, 'python', 'python')
      : path.join(app.getAppPath(), '../.venv/bin/python');
  }

  private getScriptsPath(): string {
    return app.isPackaged
      ? path.join(process.resourcesPath, 'scripts')
      : path.join(app.getAppPath(), 'scripts');
  }

  async runScript<T>(scriptName: string, args: string[] = []): Promise<T> {
    const options = {
      mode: 'json' as const,
      pythonPath: this.getPythonPath(),
      pythonOptions: ['-u'],
      scriptPath: this.getScriptsPath(),
      args
    };

    return new Promise((resolve, reject) => {
      PythonShell.run(scriptName, options, (err, results) => {
        if (err) {
          reject(err);
        } else {
          resolve(results?.[0] as T);
        }
      });
    });
  }

  // Catégorisation offline
  async categorize(label: string, amount: number): Promise<{
    category: string;
    confidence: number;
  }> {
    return this.runScript('categorize.py', [label, amount.toString()]);
  }

  // Analyse de données
  async analyzeTransactions(dataPath: string): Promise<{
    totalIncome: number;
    totalExpense: number;
    topCategories: Array<{ name: string; amount: number }>;
  }> {
    return this.runScript('analyze.py', [dataPath]);
  }
}
```

---

## 🔧 Stratégie de Synchronisation des Données

### Local-First avec Sync Cloud

```
┌─────────────────────────────────────────────────────────────────┐
│           SYNCHRONISATION LOCAL ↔ CLOUD                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────┐│
│  │  Electron    │ ←─────→ │   Sync       │ ←─────→ │  FastAPI ││
│  │  (SQLite)    │  local  │   Engine     │  HTTP   │  (Cloud) ││
│  └──────────────┘         └──────────────┘         └──────────┘│
│         ↑                                                      │
│         │                                                      │
│  ┌──────┴──────┐                                               │
│  │  Conflict   │                                               │
│  │  Resolution │                                               │
│  └─────────────┘                                               │
│                                                                  │
│  Stratégies:                                                    │
│  1. Local-first (écritures locales immédiates)                  │
│  2. Sync asynchrone (background)                                │
│  3. Conflict resolution (timestamp + règles)                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Implémentation

```typescript
// electron/services/sync-engine.ts
import { DatabaseService } from './database';
import { APIClient } from './api-client';

interface SyncStatus {
  lastSync: Date;
  pendingChanges: number;
  isOnline: boolean;
}

export class SyncEngine {
  private db: DatabaseService;
  private api: APIClient;
  private syncInterval: NodeJS.Timeout | null = null;

  constructor(db: DatabaseService, api: APIClient) {
    this.db = db;
    this.api = api;
  }

  startAutoSync(intervalMs: number = 60000) {
    this.syncInterval = setInterval(() => {
      this.sync();
    }, intervalMs);
  }

  stopAutoSync() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }

  async sync(): Promise<void> {
    try {
      // 1. Envoyer les modifications locales vers le cloud
      await this.pushLocalChanges();
      
      // 2. Récupérer les modifications du cloud
      await this.pullCloudChanges();
      
      // 3. Mettre à jour le timestamp de dernière sync
      this.db.query(
        `INSERT OR REPLACE INTO settings (key, value) VALUES ('last_sync', ?)`,
        [new Date().toISOString()]
      );
      
    } catch (error) {
      console.error('[Sync] Error:', error);
      // Marquer comme offline, retry plus tard
    }
  }

  private async pushLocalChanges(): Promise<void> {
    // Récupérer les transactions non synchronisées
    const pending = this.db.query(
      `SELECT * FROM transactions WHERE sync_status = 'pending' LIMIT 100`
    );

    if (pending.length === 0) return;

    // Envoyer au cloud
    const result = await this.api.pushTransactions(pending);
    
    // Marquer comme synchronisées
    const ids = pending.map((t: any) => t.id);
    this.db.query(
      `UPDATE transactions SET sync_status = 'synced' WHERE id IN (${ids.map(() => '?').join(',')})`,
      ids
    );
  }

  private async pullCloudChanges(): Promise<void> {
    const lastSync = this.db.query(
      `SELECT value FROM settings WHERE key = 'last_sync'`
    )[0]?.value;

    const changes = await this.api.getChangesSince(lastSync);
    
    for (const change of changes) {
      await this.applyChange(change);
    }
  }

  private async applyChange(change: any): Promise<void> {
    // Conflict resolution: dernier écrit gagne basé sur timestamp
    const local = this.db.query(
      `SELECT updated_at FROM transactions WHERE id = ?`,
      [change.id]
    )[0];

    if (!local || new Date(local.updated_at) < new Date(change.updated_at)) {
      // Appliquer la modification du cloud
      this.db.query(
        `INSERT OR REPLACE INTO transactions (id, date, label, amount, category, updated_at, sync_status)
         VALUES (?, ?, ?, ?, ?, ?, 'synced')`,
        [change.id, change.date, change.label, change.amount, change.category, change.updated_at]
      );
    }
  }
}
```

---

## ✅ Checklist Intégration

### Phase 1: Setup Initial

- [ ] Configurer `contextBridge` dans preload.ts
- [ ] Définir tous les types TypeScript
- [ ] Créer le hook `useElectron()`
- [ ] Implémenter les handlers IPC dans main.ts
- [ ] Tester communication basique (ping/pong)

### Phase 2: Services Core

- [ ] Implémenter `DatabaseService` (better-sqlite3)
- [ ] Créer schéma SQLite (sync avec PostgreSQL)
- [ ] Implémenter `PythonBridge` (démarrage FastAPI)
- [ ] Créer `APIClient` TypeScript
- [ ] Configurer React Query

### Phase 3: Sync Engine

- [ ] Implémenter `SyncEngine`
- [ ] Ajouter table `sync_status` dans SQLite
- [ ] Créer endpoints sync dans FastAPI
- [ ] Tester sync bidirectionnelle
- [ ] Gérer les conflits

### Phase 4: Production

- [ ] Packager Python avec Electron (electron-builder)
- [ ] Configurer auto-updater
- [ ] Tester offline mode
- [ ] Optimiser taille bundle
- [ ] Documentation utilisateur

---

## 🐛 Dépannage

### Problème: "window.electronAPI is undefined"

**Cause**: Preload script non chargé ou mal configuré  
**Solution**:
```javascript
// Vérifier dans webPreferences
webPreferences: {
  preload: path.join(__dirname, 'preload.js'), // .js pas .ts
  contextIsolation: true,
  nodeIntegration: false,
}
```

### Problème: "Cannot read properties of undefined (reading 'handle')"

**Cause**: Import ESM de Electron dans CommonJS  
**Solution**: Utiliser `require('electron')` dans main.js

### Problème: FastAPI ne démarre pas

**Cause**: Python non trouvé ou modules manquants  
**Solution**:
```bash
# Vérifier Python
which python3

# En dev: venv actif
source .venv/bin/activate

# En prod: packager avec electron-builder
```

### Problème: CORS errors avec FastAPI

**Solution**:
```python
# FastAPI main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Dev server Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📚 Ressources

- [Electron IPC](https://www.electronjs.org/docs/latest/tutorial/ipc)
- [FastAPI](https://fastapi.tiangolo.com/)
- [better-sqlite3](https://github.com/WiseLibs/better-sqlite3)
- [React Query](https://tanstack.com/query/latest)

---

**Version**: 1.0  
**Date**: 2026-03-12  
**Skill ID**: electron-python-sync
