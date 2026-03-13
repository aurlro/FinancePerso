# FinancePerso Electron

> Application de gestion financière personnelle pour couples et familles

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Electron](https://img.shields.io/badge/Electron-33.3.2-47848F)
![React](https://img.shields.io/badge/React-18-61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6)

---

## 📸 Screenshots

*Dashboard avec graphiques et KPIs*

*Validation batch des transactions*

*Gestion des budgets par catégorie*

---

## ✨ Fonctionnalités

### Core
- ✅ **Dashboard** - Vue d'ensemble avec KPIs et graphiques (Recharts)
- ✅ **Import CSV** - Import intelligent avec détection de colonnes
- ✅ **Validation Batch** - Catégorisation rapide par groupe
- ✅ **Budgets** - Suivi budgétaire avec alertes visuelles
- ✅ **Multi-membres** - Gestion des dépenses par personne (couple/famille)

### Intelligence Artificielle
- 🤖 **Catégorisation IA** - Gemini (gratuit) ou OpenAI
- 🧠 **Apprentissage** - Règles personnalisées qui s'améliorent
- 📊 **Suggestions** - Basées sur l'historique

### UX/UI
- 🔍 **Recherche globale** - Cmd+K pour tout trouver instantanément
- 📱 **Responsive** - Desktop et mobile
- 🎨 **Design System** - Composants réutilisables shadcn/ui
- 🌓 **Thème** - Mode clair (par défaut)

### Technique
- 🔄 **Auto-update** - Mises à jour automatiques
- 💾 **Offline** - SQLite local, 100% offline
- 🔒 **Sécurité** - Données chiffrées, clés API locales
- 🧪 **Tests** - 29 tests E2E avec Playwright

---

## 🚀 Installation

### Téléchargement

Téléchargez la dernière version pour votre plateforme :

- **macOS** : `FinancePerso-1.0.0.dmg` (Intel & Apple Silicon)
- **Windows** : `FinancePerso-1.0.0.exe` (Installateur)
- **Linux** : `FinancePerso-1.0.0.AppImage` ou `.deb`

### Build depuis les sources

```bash
# Cloner le repository
git clone https://github.com/votre-username/financeperso-electron.git
cd financeperso-electron

# Installer les dépendances
npm install

# Lancer en mode développement
npm run dev

# Build pour production
npm run build

# Package pour toutes les plateformes
npm run package

# Package pour une plateforme spécifique
npm run package:mac
npm run package:win
npm run package:linux
```

---

## 📖 Guide d'utilisation

### Premiers pas

1. **Lancer l'application** - Double-cliquez sur l'icône FinancePerso
2. **Importer des transactions** - Allez dans "Import" et sélectionnez votre relevé CSV
3. **Valider les transactions** - Utilisez "Validation" pour catégoriser rapidement
4. **Suivre vos budgets** - Créez des budgets dans l'onglet "Budgets"

### Import CSV

Formats supportés :
- Date (JJ/MM/AAAA, AAAA-MM-JJ, etc.)
- Description/Libellé
- Montant (positif = revenu, négatif = dépense)
- Catégorie (optionnel)

Séparateurs supportés :
- Point-virgule (;) - format français par défaut
- Virgule (,) - format anglais
- Tabulation

### Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| `Cmd/Ctrl + K` | Ouvrir la recherche globale |
| `Esc` | Fermer la recherche / Annuler |
| `↑/↓` | Navigation dans les listes |
| `Enter` | Sélectionner / Valider |
| `Tab` | Navigation entre champs |

### Multi-membres

Pour les couples et familles :

1. Allez dans "Membres"
2. Ajoutez les membres de votre foyer
3. Assignez chaque transaction à un membre
4. Visualisez la répartition des dépenses par personne

### Intelligence Artificielle

Configuration dans "Paramètres" > "Intelligence Artificielle" :

1. Choisissez votre provider (Gemini gratuit recommandé)
2. Entrez votre clé API (stockée localement)
3. Activez la catégorisation automatique
4. Testez la connexion

**Gemini (Gratuit)** :
- Allez sur [makersuite.google.com](https://makersuite.google.com)
- Créez une clé API gratuite
- Copiez-la dans les paramètres

---

## 🏗️ Architecture

```
financeperso-electron/
├── electron/              # Main process (Node.js)
│   ├── services/          # Services backend
│   │   ├── database.cjs   # SQLite
│   │   ├── ai-service.cjs # IA (Gemini/OpenAI)
│   │   ├── file-import.cjs # Import CSV
│   │   └── updater.cjs    # Auto-update
│   └── main.js            # Entry point Electron
├── src/
│   ├── components/        # Composants React
│   │   ├── ui/           # shadcn/ui components
│   │   ├── charts/       # Recharts graphiques
│   │   └── ...           # Composants métier
│   ├── hooks/            # Custom React hooks
│   ├── pages/            # Pages de l'application
│   ├── services/         # Services renderer
│   └── types/            # TypeScript definitions
├── tests/e2e/            # Tests Playwright
└── assets/               # Icônes et images
```

---

## 🧪 Tests

```bash
# Lancer tous les tests E2E
npm run test:e2e

# Lancer avec interface graphique
npm run test:e2e:ui

# Lancer en mode debug
npm run test:e2e:debug

# Lancer uniquement les smoke tests
npm run test:e2e:smoke
```

---

## 📝 Changelog

### v1.0.0 (2025-03-13)

- ✨ Initial release
- 📊 Dashboard avec graphiques
- 📥 Import CSV intelligent
- ✅ Validation batch
- 💰 Gestion des budgets
- 👥 Multi-membres
- 🤖 IA Gemini/OpenAI
- 🔍 Recherche globale Cmd+K
- 🔄 Auto-updater

---

## 🤝 Contribution

Les contributions sont les bienvenues ! 

1. Fork le projet
2. Créez une branche (`git checkout -b feature/amazing`)
3. Committez vos changements (`git commit -m 'Add amazing'`)
4. Push sur la branche (`git push origin feature/amazing`)
5. Ouvrez une Pull Request

---

## 📄 License

MIT License - voir [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- [Electron](https://www.electronjs.org/)
- [React](https://react.dev/)
- [shadcn/ui](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Recharts](https://recharts.org/)
- [SQLite](https://sqlite.org/)

---

<p align="center">
  Fait avec ❤️ pour une meilleure gestion financière familiale
</p>
