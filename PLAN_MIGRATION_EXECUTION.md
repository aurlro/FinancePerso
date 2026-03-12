# 🚀 PLAN D'EXÉCUTION - Migration FinancePerso

> **Date** : Mars 2026  
> **Durée estimée** : 12-16 semaines (3-4 mois)  
> **Objectif** : App Electron + React + IA (API KIM)

---

## 📋 Résumé de tes choix

| Aspect | Choix | Impact |
|--------|-------|--------|
| **Architecture** | Electron + SQLite | App desktop native, offline |
| **Auth** | Multi-utilisateurs (foyer) | Complexité ++ |
| **Timeline** | 3+ mois (tout porter) | Complet mais long |
| **Données** | Repartir à zéro + base test | Pas de migration historique |
| **IA** | Toutes features + temps réel | API KIM intensive |
| **Tests** | Unit + E2E obligatoires | Qualité garantie |

---

## 🏗️ Architecture cible

```
┌─────────────────────────────────────────────┐
│  ELECTRON APP                               │
│  ┌──────────────────────────────────────┐  │
│  │  React 18 + TypeScript               │  │
│  │  ├── UI: shadcn/ui + Tailwind        │  │
│  │  ├── State: Zustand + TanStack Query │  │
│  │  ├── Charts: Recharts                │  │
│  │  └── IA: API KIM integration         │  │
│  └──────────────────────────────────────┘  │
│              │                              │
│              ▼ IPC                           │
│  ┌──────────────────────────────────────┐  │
│  │  NODE.JS MAIN PROCESS                │  │
│  │  ├── SQLite (better-sqlite3)         │  │
│  │  ├── File system access              │  │
│  │  ├── Auto-updater                    │  │
│  │  └── Native notifications            │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

---

## 📅 ROADMAP PAR PHASES

### PHASE 0 : Fondations (Semaines 1-2)
**Objectif** : Setup technique et architecture de base

#### Semaine 1 : Setup Electron
- [ ] Initialiser projet Electron + Vite + React + TS
- [ ] Configurer ESLint + Prettier
- [ ] Setup TailwindCSS + shadcn/ui
- [ ] Structure dossiers (main/renderer/shared)
- [ ] Configuration IPC (communication main/renderer)
- [ ] Setup SQLite (better-sqlite3)
- [ ] Créer schéma DB (users, households, accounts, categories, transactions, rules)

**Livrable** : App Electron vide qui démarre avec DB connectée

#### Semaine 2 : Auth & Multi-utilisateurs
- [ ] Système d'auth local (bcrypt + JWT)
- [ ] Création foyer (household)
- [ ] Invitations par email (local, pas d'envoi réel)
- [ ] Gestion membres (owner, member, viewer)
- [ ] Contexte React auth
- [ ] Guards de routes
- [ ] Tests unitaires auth

**Livrable** : Login/Register fonctionnel avec système foyer

---

### PHASE 1 : Core - Import & Transactions (Semaines 3-5)
**Objectif** : Portage complet depuis v5.6

#### Semaine 3 : Import CSV
- [ ] Parser CSV (détection séparateur, encodage)
- [ ] Presets banques (BNP, SG, CA, etc.)
- [ ] Mapping colonnes dynamique
- [ ] Preview avant import
- [ ] Détection doublons (hash)
- [ ] Catégorisation auto (regex depuis v5.6)
- [ ] Détection virements internes
- [ ] Tests E2E import

**Livrable** : Import CSV complet avec preview

#### Semaine 4 : Transactions CRUD
- [ ] Liste transactions (table virtuelle pour perf)
- [ ] Filtres (date, compte, catégorie, statut)
- [ ] Recherche full-text
- [ ] Tri multi-colonnes
- [ ] Édition transaction
- [ ] Validation (pending → validated)
- [ ] Suppression (soft delete)
- [ ] Pagination

**Livrable** : Gestion transactions complète

#### Semaine 5 : Catégories & Règles
- [ ] CRUD catégories (emoji, couleur)
- [ ] Catégories par défaut
- [ ] Règles regex (CRUD + testeur)
- [ ] Priorité des règles
- [ ] Application batch aux transactions existantes
- [ ] Suggestions auto basées sur historique

**Livrable** : Système catégorisation complet

---

### PHASE 2 : Dashboard & Analytics (Semaines 6-7)
**Objectif** : Vue d'ensemble et visualisations

#### Semaine 6 : Dashboard Core
- [ ] KPIs cards (solde, revenus, dépenses, épargne)
- [ ] Calculs périodes (mois en cours, vs mois-1, vs année)
- [ ] Graphique donut (répartition catégories)
- [ ] Graphique line (évolution mensuelle)
- [ ] Breakdown par type de compte
- [ ] Top dépenses du mois
- [ ] Transactions récentes

**Livrable** : Dashboard fonctionnel avec charts

#### Semaine 7 : Analytics avancés
- [ ] Comparaison périodes (M vs M-1, M vs M-12)
- [ ] Heatmap dépenses (calendrier)
- [ ] Tendance catégories
- [ ] Anomalies détectées (stats)
- [ ] Export données (CSV/Excel)

**Livrable** : Analytics complètes

---

### PHASE 3 : Features Couple (Semaines 8-9)
**Objectif** : Gestion multi-utilisateurs avancée

#### Semaine 8 : Répartition & Équilibre
- [ ] Vue séparée par membre
- [ ] Répartition dépenses (qui paie quoi)
- [ ] Calcul équilibre (qui doit à qui)
- [ ] Historique équilibre
- [ ] Simulation scénarios

**Livrable** : Système équilibre fonctionnel

#### Semaine 9 : Validation croisée
- [ ] Détection transactions > 500€
- [ ] Workflow validation (pending → approved)
- [ ] Notifications in-app
- [ ] Commentaires sur transactions
- [ ] Historique validations

**Livrable** : Validation croisée complète

---

### PHASE 4 : IA & Intelligence (Semaines 10-12)
**Objectif** : Intégration API KIM

#### Semaine 10 : Setup IA
- [ ] Service API KIM (client HTTP)
- [ ] Cache résultats IA (SQLite)
- [ ] Queue traitements (offline capable)
- [ ] Configuration clé API (settings)
- [ ] Gestion erreurs/retry
- [ ] Limite coût (compteur requêtes)

**Livrable** : Infrastructure IA prête

#### Semaine 11 : Features IA Core
- [ ] Catégorisation intelligente (complément regex)
- [ ] Détection anomalies (transactions suspectes)
- [ ] Analyse dépenses (insights période)
- [ ] Bouton "Analyser" (sur demande)
- [ ] Analyse temps réel (post-import)

**Livrable** : IA intégrée aux workflows

#### Semaine 12 : Assistant IA
- [ ] Chat interface (UI)
- [ ] Contexte données utilisateur
- [ ] Questions prédéfinies
- [ ] Génération rapports (hebdo/mensuel)
- [ ] Conseils personnalisés
- [ ] Aide réserves/projets

**Livrable** : Assistant conversationnel

---

### PHASE 5 : Polish & Features avancées (Semaines 13-16)
**Objectif** : Budgets, export, notifications, gamification

#### Semaine 13 : Budgets
- [ ] Création budgets par catégorie
- [ ] Suivi vs réel (barres progression)
- [ ] Alertes dépassement (seuils)
- [ ] Prévisions (tendance)
- [ ] Vue annuelle

**Livrable** : Système budgets

#### Semaine 14 : Export & Reporting
- [ ] Export PDF (rapports mensuels)
- [ ] Templates rapports
- [ ] Export Excel (données brutes)
- [ ] Export CSV
- [ ] Programmation envoi (email local)

**Livrable** : Exports complets

#### Semaine 15 : Notifications & Open Banking
- [ ] Système notifications in-app
- [ ] Historique notifications
- [ ] Rappels (batch mensuel)
- [ ] Setup Open Banking (GoCardless)
- [ ] Sync auto comptes

**Livrable** : Notifications + import auto

#### Semaine 16 : Gamification & Finalisation
- [ ] Objectifs épargne (visuels)
- [ ] Streaks (consécutivité)
- [ ] Badges (milestones)
- [ ] Tests E2E complets
- [ ] Documentation utilisateur
- [ ] Build production

**Livrable** : App complète prête

---

## 📊 Estimations détaillées

| Phase | Durée | Features | Complexité |
|-------|-------|----------|------------|
| 0 - Fondations | 2 sem | Auth, DB, Electron setup | 🟡 Moyenne |
| 1 - Core | 3 sem | Import, Transactions, Catégories | 🔴 Élevée |
| 2 - Dashboard | 2 sem | KPIs, Charts, Analytics | 🟡 Moyenne |
| 3 - Couple | 2 sem | Équilibre, Validation | 🔴 Élevée |
| 4 - IA | 3 sem | API KIM, Assistant, Insights | 🔴 Élevée |
| 5 - Polish | 4 sem | Budgets, Export, Notifs | 🟡 Moyenne |
| **TOTAL** | **16 sem** | **Tout** | **Complexe** |

---

## 🎯 Points de contrôle (Milestones)

### 🏁 M1 - Fin Phase 0 (Semaine 2)
**Critères d'acceptation :**
- [ ] App Electron démarre
- [ ] Login/Register fonctionnel
- [ ] Multi-utilisateurs (foyer) opérationnel
- [ ] Tests auth passent

**Démonstration** : Créer un foyer, inviter un membre, login

### 🏁 M2 - Fin Phase 1 (Semaine 5)
**Critères d'acceptation :**
- [ ] Import CSV avec preview
- [ ] Transactions listables/éditables
- [ ] Catégorisation auto fonctionnelle
- [ ] Tests E2E import passent

**Démonstration** : Importer un CSV, voir transactions catégorisées

### 🏁 M3 - Fin Phase 2 (Semaine 7)
**Critères d'acceptation :**
- [ ] Dashboard avec KPIs
- [ ] Charts donut + line
- [ ] Comparaisons périodes

**Démonstration** : Dashboard complet avec données

### 🏁 M4 - Fin Phase 3 (Semaine 9)
**Critères d'acceptation :**
- [ ] Calcul équilibre couple
- [ ] Validation croisée workflow
- [ ] Commentaires transactions

**Démonstration** : Transaction 500€ → validation requise

### 🏁 M5 - Fin Phase 4 (Semaine 12)
**Critères d'acceptation :**
- [ ] IA catégorise correctement
- [ ] Assistant chat fonctionnel
- [ ] Rapports auto générés

**Démonstration** : Chat "Analyse mes dépenses ce mois"

### 🏁 M6 - Release (Semaine 16)
**Critères d'acceptation :**
- [ ] Toutes features listées
- [ ] Tests E2E > 80% passent
- [ ] Build production fonctionnel
- [ ] Documentation complète

**Démonstration** : App complète avec toutes features

---

## 🛠️ Stack technique détaillée

### Frontend (Renderer)
```json
{
  "framework": "React 18.3+",
  "language": "TypeScript 5.3+",
  "build": "Vite 5.0+",
  "ui": "shadcn/ui + Radix UI",
  "styling": "TailwindCSS 3.4+",
  "state": "Zustand + TanStack Query",
  "forms": "React Hook Form + Zod",
  "charts": "Recharts",
  "icons": "Lucide React",
  "notifications": "Sonner",
  "testing": "Vitest + RTL + Playwright"
}
```

### Backend (Main Process)
```json
{
  "runtime": "Node.js 20+",
  "database": "better-sqlite3 (sync)",
  "crypto": "bcrypt (auth)",
  "ipc": "Electron IPC",
  "fs": "Node fs + path",
  "updates": "electron-updater"
}
```

### Outils
- **Lint** : ESLint + Prettier
- **Test** : Vitest (unit) + Playwright (E2E)
- **Build** : electron-builder
- **Type** : TypeScript strict

---

## 📁 Structure du projet

```
financeperso-electron/
├── electron/                   # Main process
│   ├── main.ts                 # Entry point
│   ├── preload.ts              # IPC preload
│   ├── db/                     # SQLite
│   │   ├── connection.ts
│   │   ├── schema.ts
│   │   └── migrations/
│   └── services/               # Business logic
│       ├── auth.ts
│       ├── import.ts
│       └── ia.ts
├── src/                        # Renderer (React)
│   ├── App.tsx
│   ├── main.tsx
│   ├── pages/                  # 8 pages
│   ├── components/             # UI components
│   ├── hooks/                  # Custom hooks
│   ├── services/               # API calls (IPC)
│   ├── stores/                 # Zustand stores
│   └── lib/                    # Utils
├── shared/                     # Types partagés
├── tests/                      # Tests E2E
├── docs/                       # Documentation
├── package.json
├── electron-builder.json
└── vite.config.ts
```

---

## 💰 Budget API KIM (estimation)

| Feature | Requêtes/mois | Coût estimé |
|---------|--------------|-------------|
| Catégorisation auto | 100 | ~2-5€ |
| Anomalies | 50 | ~1-2€ |
| Insights | 30 | ~1-2€ |
| Assistant chat | 200 | ~5-10€ |
| Rapports | 20 | ~1€ |
| **TOTAL** | **~400** | **~10-20€/mois** |

**Optimisations** :
- Cache résultats (évite requêtes doublons)
- Traitement batch (pas temps réel pour tout)
- Limite quotidienne configurable

---

## ⚠️ Risques & Mitigations

| Risque | Probabilité | Impact | Mitigation |
|--------|------------|--------|------------|
| Electron trop complexe | Moyenne | Élevé | Prototype semaine 1, fallback web |
| API KIM instable/coûteuse | Moyenne | Moyen | Cache agressif, mode offline |
| Perf SQLite (10k+ tx) | Faible | Moyen | Indexation, pagination, virtual scroll |
| Delai (16 sem trop long) | Moyenne | Élevé | Phases indépendantes, MVP M2 |
| Tests E2E fragiles | Moyenne | Moyen | Page Object Pattern, retries |

---

## 🚀 Prochaine action immédiate

### Cette semaine (Setup) :

1. **Créer repo** `financeperso-electron`
2. **Init Electron + Vite + React**
   ```bash
   npm create electron-vite@latest
   ```
3. **Setup Tailwind + shadcn**
   ```bash
   npx shadcn-ui@latest init
   ```
4. **Setup SQLite** (better-sqlite3)
5. **Créer schéma DB**
6. **Premier commit**

### Validation fin semaine 1 :
- [ ] App démarre en dev
- [ ] Hot reload fonctionne
- [ ] DB créée et accessible
- [ ] Premier composant UI (Button shadcn)

---

## 📞 Questions avant démarrage

1. **Nom de l'app** : "FinancePerso" ou nouveau nom ?
2. **Repo** : Nouveau repo GitHub ou dans existant ?
3. **Tests** : CI/CD GitHub Actions dès le début ?
4. **Design** : Maquettes Figma ou improviser ?

---

**Prêt à démarrer la Phase 0 ?** 🚀
