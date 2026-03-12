# 🎯 Stratégie de Développement - FinancePerso

> **Date** : Mars 2026  
> **Décision** : Développer FinCouple React en utilisant v5.6 Streamlit comme base de référence

---

## 📁 Structure des Projets

```
FinancePerso/
│
├── 📱 v5.6 STREAMLIT (BASE DE RÉFÉRENCE)
│   ├── app.py                    ← Point d'entrée
│   ├── app_v5_5.py               ← Version light
│   ├── modules/                  ← 28k lignes de logique métier
│   │   ├── db/                   ← SQLite, modèles, migrations
│   │   ├── categorization.py     ← Logique de catégorisation
│   │   ├── couple/               ← Gestion couple
│   │   ├── export/               ← Export PDF
│   │   ├── open_banking/         ← Import bancaire
│   │   └── ...
│   ├── pages/                    ← Interface Streamlit
│   ├── tests/                    ← 33 tests
│   └── Data/finance.db           ← 471 transactions
│
│   ✅ À CONSERVER : Toute la logique métier
│   ❌ À NE PAS MODIFIER : Sauf bug fixes critiques
│
├── ⚛️ FINCOUPLE REACT (DÉVELOPPEMENT ACTIF)
│   └── Ideas/couple-cashflow-clever-main/
│       ├── src/
│       │   ├── pages/            ← Dashboard, Transactions...
│       │   ├── components/       ← UI components
│       │   ├── hooks/            ← React hooks
│       │   └── integrations/     ← Supabase (à remplacer)
│       ├── supabase/             ← Config (à migrer vers local)
│       └── package.json
│
│   🚀 PROJET EN COURS DE DÉVELOPPEMENT
│   📋 À FAIRE : Porter la logique métier depuis v5.6
│
└── 📦 web/                       ← Ancien frontend (archive potentielle)
    └── frontend/                 ← React + node_modules
```

---

## 🎯 Objectifs

### 1. FinCouple React devient l'application principale
- **UI moderne** : React + TypeScript + Tailwind
- **UX fluide** : SPA sans rechargement
- **Responsive** : Mobile-first

### 2. v5.6 Streamlit reste la référence
- **Logique métier** : Copier/adapter les algorithmes
- **Modèles de données** : Répliquer la structure
- **Features** : Tout ce qui existe dans v5.6 doit exister dans React

### 3. Migration progressive
| Étape | Action | Priorité |
|-------|--------|----------|
| 1 | Setup FinCouple React local | 🔴 Haute |
| 2 | Remplacer Supabase par SQLite local | 🔴 Haute |
| 3 | Porter modèles données (v5.6 → React) | 🔴 Haute |
| 4 | Réimplémenter logique métier | 🟡 Moyenne |
| 5 | UI/UX : Reprendre écrans v5.6 | 🟡 Moyenne |
| 6 | Tests et validation | 🟢 Basse |

---

## 📋 Ce qu'il faut porter de v5.6 vers React

### 🗃️ Modèles de données (copier depuis `modules/db/`)

```typescript
// À créer dans FinCouple React
interface Transaction {
  id: string;
  date: string;
  label: string;
  amount: number;
  category: string;
  account: string;
  status: 'pending' | 'validated';
  member?: string;
  beneficiary?: string;
  notes?: string;
  tx_hash: string;
}

interface Category {
  id: string;
  name: string;
  emoji: string;
  is_fixed: boolean;
}

interface Account {
  id: string;
  name: string;
  account_type: 'personal_a' | 'personal_b' | 'joint';
  owner?: string;
}
```

### 🧠 Logique métier (copier depuis `modules/`)

| Feature | Fichier source v5.6 | À implémenter dans React |
|---------|---------------------|--------------------------|
| **Catégorisation** | `categorization.py` | Service + hooks |
| **Import CSV** | `ingestion/` | Parser + mapping |
| **Détection virements** | `transfer_detection.py` | Algorithmes |
| **Validation croisée** | `couple/cross_validation.py` | Workflow |
| **Export PDF** | `export/pdf_exporter.py` | Génération PDF |
| **Open Banking** | `open_banking/` | API bancaires |
| **Budgets** | `budgets_dynamic.py` | Calculs |
| **Analytics** | `analytics.py` | Graphiques |

### 🎨 Écrans à reproduire (depuis `pages/`)

```
v5.6 Streamlit          →    FinCouple React
─────────────────────────────────────────────
01_Import.py            →    /import
02_Dashboard.py         →    /dashboard  
03_Intelligence.py      →    /rules
04_Budgets.py           →    /budgets
05_Audit.py             →    /audit
06_Assistant.py         →    /assistant
07_Recherche.py         →    /search
08_Configuration.py     →    /settings
09_Badges.py            →    /gamification
10_Projections.py       →    /projections
11_Abonnements.py       →    /subscriptions
12_Patrimoine.py        →    /accounts
```

---

## ⚠️ Défauts de v5.6 à corriger dans React

| Problème v5.6 | Solution dans React |
|---------------|---------------------|
| Trop lourd (28k lignes) | Architecture modulaire, lazy loading |
| Difficile à maintenir | TypeScript strict, tests unitaires |
| Incohérences design | Design system unique (shadcn/ui) |
| Incohérences logique | Architecture propre, patterns cohérents |
| Performance Streamlit | React optimisé, state management |

---

## 🚀 Prochaines étapes immédiates

### 1. Setup FinCouple React local
```bash
cd Ideas/couple-cashflow-clever-main
pnpm install
pnpm dev
```

### 2. Analyser la structure existante
- [ ] Comprendre l'architecture actuelle
- [ ] Identifier ce qui utilise Supabase
- [ ] Lister les composants existants

### 3. Plan de migration Supabase → Local
- [ ] Choisir : SQLite locale vs IndexedDB vs autre
- [ ] Créer couche d'abstraction DB
- [ ] Migrer schémas

### 4. Commencer le portage
- [ ] Modèles de données
- [ ] Service de catégorisation
- [ ] Import CSV

---

## 📝 Règles d'or

1. **v5.6 est la source de vérité** : Si une feature existe dans v5.6, elle doit exister dans React
2. **Ne pas modifier v5.6** : Sauf bug critique, c'est la référence stable
3. **Documenter les choix** : Quand on change une logique, expliquer pourquoi
4. **Tests** : Chaque feature portée doit avoir des tests

---

## 💡 Philosophie

> "v5.6 Streamlit c'est le cerveau, FinCouple React c'est le corps.  
> On garde le cerveau, on change le corps pour qu'il soit plus agile."

**v5.6** = Référence fonctionnelle, logique métier validée  
**FinCouple React** = Nouvelle interface, meilleure architecture, même intelligence

---

*Dernière mise à jour : Mars 2026*
