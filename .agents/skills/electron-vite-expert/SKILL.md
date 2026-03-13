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

## 🔧 Solution Recommandée : electron-forge

**Pourquoi electron-forge ?**

Le problème classique avec Electron + Vite :
```
TypeError: Cannot read properties of undefined (reading 'handle')
```

Cela arrive car :
1. Le package npm `electron` exporte le chemin de l'exécutable
2. Les imports ESM nommés (`import { app } from 'electron'`) échouent
3. `require('electron')` retourne une chaîne, pas l'objet module

**electron-forge résout tout ça** en gérant correctement le bundling et les externalisations.

---

## 🚀 Création d'un projet

```bash
# Créer un projet avec le template Vite
npm create electron-app@latest my-app -- --template=vite

# Ou avec TypeScript
npm create electron-app@latest my-app -- --template=vite-typescript
```

---

## 📁 Structure du projet

```
my-app/
├── src/
│   ├── main.js              # Processus principal (CommonJS)
│   ├── preload.js           # Pont IPC
│   ├── renderer.tsx         # Entry point React
│   ├── App.tsx              # Composant racine
│   ├── components/ui/       # Composants shadcn/ui
│   └── lib/
│       └── utils.ts         # Utilitaires
├── index.html               # HTML template
├── package.json
├── forge.config.js          # Config electron-forge
├── vite.renderer.config.mjs # Config Vite renderer
├── vite.main.config.mjs     # Config Vite main
└── vite.preload.config.mjs  # Config Vite preload
```

---

## ⚙️ Configuration

### 1. Ajouter React

```bash
npm install react react-dom
npm install -D @types/react @types/react-dom
```

### 2. Configurer Vite pour React

```javascript
// vite.renderer.config.mjs
import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  esbuild: {
    jsx: 'transform',
    jsxFactory: 'React.createElement',
    jsxFragment: 'React.Fragment',
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

### 3. Configurer Tailwind CSS

```bash
npm install -D tailwindcss postcss autoprefixer tailwindcss-animate
npm install class-variance-authority clsx tailwind-merge lucide-react
npx tailwindcss init -p
```

```javascript
// tailwind.config.js
module.exports = {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

### 4. Créer le composant racine

```typescript
// src/renderer.tsx
import * as React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  React.createElement(React.StrictMode, {},
    React.createElement(App, {})
  )
)
```

---

## 🔌 Ajouter better-sqlite3

```bash
npm install better-sqlite3
npm install -D @types/better-sqlite3
```

```javascript
// src/main.js
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const Database = require('better-sqlite3');

// Database initialization
const db = new Database(path.join(app.getPath('userData'), 'app.db'));

// IPC handlers
ipcMain.handle('db:query', (event, sql, params) => {
  return db.prepare(sql).all(params);
});
```

---

## 🚫 Ce qu'il faut éviter

1. **Ne PAS utiliser** `import { app } from 'electron'` dans le main process
   - ✅ `const { app } = require('electron')`
   - ❌ `import { app } from 'electron'`

2. **Ne PAS utiliser** `.ts` pour le main process
   - ✅ `.js` ou `.cjs`
   - ❌ `.ts`

3. **Ne PAS installer** `electron` globalement
   - ✅ Utiliser la version locale dans node_modules
   - ❌ `npm install -g electron`

4. **Ne PAS essayer** de bundler `electron` avec Vite
   - ✅ Laisser electron-forge gérer
   - ❌ Configurer Vite pour bundler electron

---

## 📜 Scripts utiles

```json
{
  "scripts": {
    "start": "electron-forge start",
    "package": "electron-forge package",
    "make": "electron-forge make",
    "publish": "electron-forge publish"
  }
}
```

---

## 🐛 Débogage

### Voir les logs du main process

```bash
DEBUG=* npm start
```

### Ouvrir DevTools automatiquement

```javascript
// main.js
mainWindow.webContents.openDevTools();
```

### Logs dans la console système

```javascript
console.log('Message from main process');
```

---

## 📚 Ressources

- [electron-forge](https://www.electronforge.io/)
- [Electron documentation](https://www.electronjs.org/docs/latest)
- [Vite documentation](https://vitejs.dev/)

---

## ✅ Checklist de validation

- [ ] `npm start` lance l'application sans erreur
- [ ] Le main process démarre (voir logs)
- [ ] La fenêtre s'affiche
- [ ] React s'hydrate correctement
- [ ] Les imports `@/` fonctionnent
- [ ] Le hot reload fonctionne
