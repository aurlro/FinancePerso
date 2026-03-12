# Electron + Vite Expert Skill

> Configuration robuste pour applications Electron avec Vite, React et TypeScript sans les problèmes d'import ESM/CJS.

## 🎯 Objectif

Créer des applications Electron modernes avec :
- ✅ Vite (build rapide)
- ✅ React + TypeScript
- ✅ SQLite (better-sqlite3)
- ✅ Pas de problèmes d'import ESM/CJS
- ✅ Hot reload fonctionnel

---

## 🏗️ Architecture Recommandée

### Structure des fichiers

```
project/
├── electron/               # Main process (CommonJS)
│   ├── main.js            # Entry point (CJS)
│   ├── preload.js         # Preload script (CJS)
│   └── services/          # Backend services
│       └── database.cjs   # SQLite (CJS)
├── src/                   # Renderer (ESM/React)
│   ├── main.tsx
│   ├── App.tsx
│   └── ...
├── package.json
└── vite.config.ts
```

### Règles d'or

1. **Main process** : Toujours en `.js` ou `.cjs` (CommonJS)
2. **Renderer process** : Toujours en `.tsx` (ESM/React)
3. **Services backend** : `.cjs` pour compatibilité Node.js
4. **Pas de `.ts` dans electron/** : Évite les problèmes de transpilation

---

## 📦 Configuration package.json

```json
{
  "name": "app-electron",
  "version": "1.0.0",
  "type": "module",
  "main": "electron/main.js",
  "scripts": {
    "dev": "concurrently \"vite\" \"wait-on http://localhost:5173 && electron electron/main.js\"",
    "build": "tsc && vite build && electron-builder",
    "build:mac": "tsc && vite build && electron-builder --mac",
    "build:win": "tsc && vite build && electron-builder --win"
  },
  "dependencies": {
    "better-sqlite3": "^9.4.3",
    "bcryptjs": "^2.4.3",
    "jsonwebtoken": "^9.0.2",
    "uuid": "^9.0.1"
  },
  "devDependencies": {
    "@types/better-sqlite3": "^7.6.9",
    "@types/bcryptjs": "^2.4.6",
    "concurrently": "^8.2.2",
    "electron": "^29.1.0",
    "electron-builder": "^24.13.3",
    "vite": "^5.1.5",
    "wait-on": "^7.2.0"
  }
}
```

---

## ⚡ Configuration Vite

### vite.config.ts

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})
```

**Important** : Ne pas utiliser `vite-plugin-electron` (source de problèmes).

---

## 🔧 Electron Main Process

### electron/main.js (CommonJS)

```javascript
const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')

// Database services
let dbService
let authService

const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']
const RENDERER_DIST = path.join(__dirname, '../dist')

// Init services
async function initServices() {
  // Dynamic import for ESM modules
  const { DatabaseService } = await import('./services/database.cjs')
  const { AuthService } = await import('./services/auth.cjs')
  
  const dbPath = path.join(app.getPath('userData'), 'app.db')
  dbService = new DatabaseService(dbPath)
  authService = new AuthService(dbService)
  
  console.log('Database initialized:', dbPath)
}

let mainWindow = null

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    show: false,
  })

  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
  })

  if (VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(VITE_DEV_SERVER_URL)
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(RENDERER_DIST, 'index.html'))
  }
}

// IPC Handlers - Define after app ready
function setupIpcHandlers() {
  ipcMain.handle('db:init', () => dbService.init())
  ipcMain.handle('db:query', (_, sql, params) => dbService.query(sql, params))
  ipcMain.handle('auth:login', (_, email, password) => authService.login(email, password))
  // ... autres handlers
}

// App lifecycle
app.whenReady().then(async () => {
  await initServices()
  setupIpcHandlers()
  createWindow()
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})
```

---

## 🔌 Preload Script

### electron/preload.js (CommonJS)

```javascript
const { contextBridge, ipcRenderer } = require('electron')

const api = {
  // Database
  db: {
    init: () => ipcRenderer.invoke('db:init'),
    query: (sql, params) => ipcRenderer.invoke('db:query', sql, params),
  },
  
  // Auth
  auth: {
    login: (email, password) => ipcRenderer.invoke('auth:login', email, password),
    register: (email, password, name) => ipcRenderer.invoke('auth:register', email, password, name),
  }
}

contextBridge.exposeInMainWorld('electronAPI', api)
```

---

## 🗄️ Backend Services (CJS)

### electron/services/database.cjs

```javascript
const Database = require('better-sqlite3')
const path = require('path')
const fs = require('fs')

class DatabaseService {
  constructor(dbPath) {
    this.dbPath = dbPath
    this.db = null
    
    // Ensure directory exists
    const dir = path.dirname(dbPath)
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true })
    }
  }

  init() {
    try {
      this.db = new Database(this.dbPath)
      this.db.pragma('journal_mode = WAL')
      this.createTables()
      return true
    } catch (error) {
      console.error('DB init error:', error)
      return false
    }
  }

  createTables() {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `)
    // ... autres tables
  }

  query(sql, params) {
    if (!this.db) throw new Error('Database not initialized')
    
    const stmt = this.db.prepare(sql)
    if (sql.trim().toLowerCase().startsWith('select')) {
      return params ? stmt.all(...params) : stmt.all()
    } else {
      return params ? stmt.run(...params) : stmt.run()
    }
  }
}

module.exports = { DatabaseService }
```

### electron/services/auth.cjs

```javascript
const bcrypt = require('bcryptjs')
const jwt = require('jsonwebtoken')
const { v4: uuidv4 } = require('uuid')

const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret-change-in-prod'
const SALT_ROUNDS = 10

class AuthService {
  constructor(db) {
    this.db = db
  }

  async register(email, password, displayName) {
    const existing = this.db.query('SELECT id FROM users WHERE email = ?', [email])
    if (existing.length > 0) {
      return { success: false, error: 'Email exists' }
    }

    const passwordHash = await bcrypt.hash(password, SALT_ROUNDS)
    const userId = uuidv4()
    
    this.db.query(
      'INSERT INTO users (id, email, password_hash, display_name) VALUES (?, ?, ?, ?)',
      [userId, email, passwordHash, displayName]
    )

    const token = jwt.sign({ userId, email }, JWT_SECRET, { expiresIn: '7d' })
    return { success: true, token, user: { id: userId, email, display_name: displayName } }
  }

  async login(email, password) {
    const users = this.db.query(
      'SELECT id, email, password_hash, display_name FROM users WHERE email = ?',
      [email]
    )

    if (users.length === 0) {
      return { success: false, error: 'Invalid credentials' }
    }

    const user = users[0]
    const valid = await bcrypt.compare(password, user.password_hash)
    
    if (!valid) {
      return { success: false, error: 'Invalid credentials' }
    }

    const token = jwt.sign({ userId: user.id, email }, JWT_SECRET, { expiresIn: '7d' })
    return { success: true, token, user: { id: user.id, email, display_name: user.display_name } }
  }
}

module.exports = { AuthService }
```

---

## ⚛️ Frontend (React + TypeScript)

### Types pour IPC

```typescript
// src/types/electron.d.ts
declare global {
  interface Window {
    electronAPI: {
      db: {
        init: () => Promise<boolean>
        query: (sql: string, params?: any[]) => Promise<any>
      }
      auth: {
        login: (email: string, password: string) => Promise<any>
        register: (email: string, password: string, name: string) => Promise<any>
      }
    }
  }
}

export {}
```

### Exemple d'utilisation

```typescript
// src/App.tsx
import { useState, useEffect } from 'react'

function App() {
  const [dbReady, setDbReady] = useState(false)

  useEffect(() => {
    window.electronAPI.db.init().then(setDbReady)
  }, [])

  const handleLogin = async () => {
    const result = await window.electronAPI.auth.login('test@test.com', 'password')
    console.log(result)
  }

  return (
    <div>
      <h1>My Electron App</h1>
      <p>DB Ready: {dbReady ? 'Yes' : 'No'}</p>
      <button onClick={handleLogin}>Login</button>
    </div>
  )
}
```

---

## 🚀 Commandes de démarrage

```bash
# Installation
npm install

# Développement (Vite + Electron)
npm run dev

# Build production
npm run build
```

---

## 🐛 Dépannage

### Erreur : "Cannot read properties of undefined (reading 'handle')"
**Cause** : Import ESM de Electron dans du CJS  
**Solution** : Utiliser `require('electron')` dans main.js

### Erreur : "module is not defined"
**Cause** : Fichier tailwind.config.js en ESM  
**Solution** : Renommer en `tailwind.config.cjs`

### Erreur : "Unexpected identifier 'Promise'"
**Cause** : PostCSS config en ESM  
**Solution** : Renommer en `postcss.config.cjs`

### Erreur : "Identifier '__dirname' has already been declared"
**Cause** : Redéfinition de `__dirname`  
**Solution** : Enlever `const __dirname = ...` dans les fichiers .cjs

---

## ✅ Checklist création projet

- [ ] `package.json` avec `"type": "module"`
- [ ] `electron/main.js` en CommonJS (pas .ts)
- [ ] `electron/preload.js` en CommonJS
- [ ] Services backend en `.cjs`
- [ ] Frontend React en `.tsx`
- [ ] `vite.config.ts` simple (sans electron-plugin)
- [ ] `tailwind.config.cjs` (pas .js)
- [ ] `postcss.config.cjs` (pas .js)
- [ ] Dépendances `concurrently` et `wait-on`
- [ ] Script `dev` avec `wait-on`

---

## 📚 Ressources

- [Electron Documentation](https://www.electronjs.org/docs/latest)
- [Vite Documentation](https://vitejs.dev/guide/)
- [better-sqlite3](https://github.com/WiseLibs/better-sqlite3)

---

**Version** : 1.0  
**Dernière mise à jour** : Mars 2026
