# Tests E2E - Playwright (PR #10)

Cette suite de tests end-to-end utilise [Playwright](https://playwright.dev/) pour tester les parcours utilisateurs critiques.

## Installation

```bash
# Installer Playwright
npm install -D @playwright/test
npx playwright install
```

## Structure des tests

```
e2e/
├── playwright.config.ts    # Configuration Playwright
├── tests/
│   ├── auth.spec.ts        # Tests authentification
│   ├── dashboard.spec.ts   # Tests dashboard
│   ├── transactions.spec.ts # Tests transactions
│   └── import.spec.ts      # Tests import CSV
└── README.md
```

## Scénarios testés

### Authentification (`auth.spec.ts`)
- ✅ Affichage page login
- ✅ Connexion avec identifiants valides
- ✅ Erreur avec identifiants invalides
- ✅ Navigation vers inscription
- ✅ Création de compte
- ✅ Déconnexion
- ✅ Redirection vers login si non authentifié

### Dashboard (`dashboard.spec.ts`)
- ✅ Affichage des KPIs (revenus, dépenses, épargne)
- ✅ Rendu des graphiques
- ✅ Changement de période
- ✅ Répartition par catégorie
- ✅ Navigation vers transactions
- ✅ Liste des transactions récentes

### Transactions (`transactions.spec.ts`)
- ✅ Affichage liste transactions
- ✅ Filtrage par catégorie
- ✅ Filtrage par statut
- ✅ Recherche de transactions
- ✅ Mise à jour catégorie
- ✅ Validation de transaction
- ✅ Catégorisation en masse
- ✅ Pagination

### Import CSV (`import.spec.ts`)
- ✅ Affichage formulaire import
- ✅ Upload fichier CSV
- ✅ Mapping des colonnes
- ✅ Aperçu avant import
- ✅ Import réussi
- ✅ Détection doublons
- ✅ Gestion erreurs format

## Exécution des tests

```bash
# Lancer tous les tests
npx playwright test

# Lancer en mode headed (voir le navigateur)
npx playwright test --headed

# Lancer un fichier spécifique
npx playwright test auth.spec.ts

# Lancer avec UI de debug
npx playwright test --ui

# Générer rapport HTML
npx playwright test --reporter=html
n```

## Configuration

Variables d'environnement :
- `FRONTEND_URL` : URL du frontend (défaut: http://localhost:8080)
- `API_URL` : URL de l'API (défaut: http://localhost:8000/api)
- `CI` : Mode CI (désactive le watch mode)

## Bonnes pratiques

1. **Isoler les tests** : Chaque test doit être indépendant
2. **Utiliser des données de test** : Ne pas dépendre des données réelles
3. **Nettoyer après** : Supprimer les données créées pendant les tests
4. **Sélecteurs robustes** : Utiliser `getByRole` plutôt que les sélecteurs CSS
5. **Attentes explicites** : Attendre que les éléments soient visibles

## CI/CD

Les tests sont configurés pour s'exécuter sur :
- Chromium (Desktop)
- Firefox (Desktop)
- WebKit (Safari)
- Mobile Chrome
- Mobile Safari

En mode CI (`CI=true`), les tests sont exécutés en série avec retry.
