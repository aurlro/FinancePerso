# FinancePerso - Application Electron

Application de gestion financière de couple, migration depuis Streamlit vers Electron + React.

## Architecture

- **Electron** : Framework desktop (via electron-forge)
- **React 18** : UI library
- **TypeScript** : Typage
- **Vite** : Build tool
- **Tailwind CSS** : Styling
- **shadcn/ui** : Composants UI

## Structure

```
src/
  ├── main.js              # Processus principal Electron
  ├── preload.js           # Pont sécurisé IPC
  ├── renderer.tsx         # Point d'entrée React
  ├── App.tsx              # Composant racine
  ├── components/ui/       # Composants shadcn/ui
  │   ├── button.tsx
  │   └── card.tsx
  └── lib/
      └── utils.ts         # Utilitaires (cn, etc.)
```

## Scripts

```bash
# Développement
npm start

# Build
npm run package

# Créer les installers
npm run make
```

## Résolution du problème ESM/CJS

Le problème `Cannot read properties of undefined (reading 'handle')` était dû à :
1. Le package npm `electron` exporte le chemin de l'exécutable
2. Les imports ESM nommés (`import { app } from 'electron'`) ne fonctionnent pas
3. `require('electron')` retourne une chaîne, pas l'objet module

**Solution** : Utiliser `electron-forge` qui gère correctement :
- Le bundling du main process avec les bonnes externalisations
- Le chargement des modules natifs Electron
- Le hot reload en développement

## Prochaines étapes

- [ ] Ajouter better-sqlite3
- [ ] Créer les services (auth, database)
- [ ] Implémenter les pages (login, dashboard, etc.)
- [ ] Migrer la logique depuis le projet Streamlit
