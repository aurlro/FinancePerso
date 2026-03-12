# 🚀 Guide de Migration - FinancePerso

> **v5.6 Streamlit** → **FinCouple React** (local, sans Supabase)

---

## 📚 Documents disponibles

| Document | Contenu | Taille |
|----------|---------|--------|
| **STRATEGIE.md** | Vision globale et structure des projets | 6.4 KB |
| **COMPARAISON_MIGRATION.md** | Analyse détaillée v5.6 vs FinCouple | 9.4 KB |
| **QUESTIONNAIRE_MIGRATION.md** | Questions pour définir le plan | 7.4 KB |
| **MIGRATION_GUIDE.md** (ce doc) | Guide d'utilisation | - |

---

## 🎯 Résumé de la situation

### Ce que tu as actuellement :

```
📱 v5.6 Streamlit (TON APP FONCTIONNELLE)
├── 28 000 lignes de Python
├── 287 fichiers
├── 471 transactions dans SQLite
├── 33 tests qui passent
└── TOUTES les features (budgets, IA, audit...)

⚛️ FinCouple React (DANS Ideas/)
├── 4 000 lignes de TypeScript/React
├── 81 fichiers
├── UI moderne (shadcn/ui)
├── Mobile-first
└── Dépendance Supabase (à remplacer)
```

### La décision :

✅ **Garder v5.6** comme base de référence (logique métier)  
🚀 **Développer FinCouple React** comme application principale  
❌ **Supprimer v6** (créée aujourd'hui, expérimentale)

---

## 📊 Analyse comparative (extrait)

### Ce qui existe dans les deux
- ✅ Import CSV + catégorisation
- ✅ Dashboard avec charts
- ✅ Gestion comptes/catégories
- ✅ Détection virements internes
- ✅ Dark/Light mode

### Ce qui est uniquement dans v5.6 (à porter)
| Feature | Priorité | Effort |
|---------|----------|--------|
| Budgets dynamiques | 🔴 Haute | 2 jours |
| Validation croisée couple | 🔴 Haute | 2 jours |
| Audit transactions | 🟡 Moyenne | 3 jours |
| Assistant IA | 🟡 Moyenne | 3 jours |
| Export PDF | 🟡 Moyenne | 1 jour |
| Projections | 🟢 Basse | 3 jours |
| Gamification | 🟢 Basse | 4 jours |

### Ce qui est uniquement dans FinCouple (à garder)
- ✅ UI moderne (35 composants shadcn)
- ✅ Système foyer/invitations
- ✅ Mobile-first
- ✅ TypeScript strict
- ✅ TanStack Query

---

## 🔧 Les défis techniques

### 1. Backend (CRITIQUE)
**Problème** : FinCouple utilise Supabase (cloud)  
**Solution** : Remplacer par API Python + SQLite locale

Options :
- **A** : FastAPI + SQLite (comme v5.6) ⭐ Recommandé
- **B** : IndexedDB uniquement (100% frontend)
- **C** : Electron/Tauri (app desktop)

### 2. Auth (CRITIQUE)
**Problème** : Supabase Auth  
**Solution** : Auth locale (JWT ou session simple)

Options :
- Pas d'auth (usage perso)
- Auth simple (1 utilisateur)
- Auth multi-utilisateurs (foyer)

### 3. Migration données
**Problème** : 471 transactions à migrer  
**Solution** : Script de migration SQLite → nouveau schéma

---

## 📋 Prochaines étapes

### Étape 1 : Répondre au questionnaire
Ouvre `QUESTIONNAIRE_MIGRATION.md` et remplis tes choix.

Cela définira :
- Architecture technique
- Features à porter en priorité
- Timeline acceptable

### Étape 2 : Génération du Plan
Une fois le questionnaire rempli, je crée :
- `PLAN_MIGRATION.md` avec roadmap détaillée
- Architecture technique choisie
- Estimations précises
- Tâches par phase

### Étape 3 : Développement
Exécution du plan phase par phase.

---

## 🎨 Exemple de réponses (à adapter)

```markdown
### Mes choix (exemple)

**1. Objectifs**
- 1.1 : UI moderne + Performance
- 1.2 : Remplacement complet
- 1.3 : 1-2 mois acceptable

**2. Architecture**
- 2.1 : A (FastAPI + SQLite)
- 2.2 : Auth simple (1 utilisateur)
- 2.3 : Une seule base

**3. Features Core**
- [x] Import CSV
- [x] Catégorisation auto
- [x] Dashboard
- [x] Validation transactions

**3. Features Avancées**
- [x] Budgets
- [x] Validation croisée
- [ ] IA (phase 2)

**4. IA**
- 4.1 : Catégorisation + Assistant
- 4.2 : Sur demande
- 4.3 : Offline first

**5. UX**
- 5.1 : Desktop first
- 5.2 : Toggle light/dark
- 5.3 : Batch mensuel
- 5.4 : In-app only

**6. Données**
- 6.1 : Oui, tout migrer
- 6.2 : Transactions + Catégories + Règles
- 6.3 : Exporter backup

**7. Développement**
- 7.1 : Par features
- 7.2 MVP : 1) Import 2) Dashboard 3) Transactions 4) Catégories 5) Budgets
- 7.3 : Tests manuels
- 7.4 : Minimaliste

**8. Déploiement**
- 8.1 : Local uniquement
- 8.2 : Couple (2 personnes)
- 8.3 : Standard

**9. Contraintes**
- 9.1 : Gratuit
- 9.2 : Mix apprendre + utiliser
- 9.3 : Low-maintenance

**10. Priorités**
- Performance : 8
- UI moderne : 9
- Features : 7
- Rapidité dev : 6
```

---

## 💡 Ma recommandation préliminaire

Basée sur l'analyse des deux projets :

### Option recommandée : **Core d'abord (3-4 semaines)**

**Phase 1 : Fondations (1 semaine)**
1. Setup API Python (FastAPI) + SQLite
2. Schéma de données (simplifié depuis v5.6)
3. Auth locale simple
4. Migration données (471 transactions)

**Phase 2 : MVP (2 semaines)**
1. Dashboard avec KPIs
2. Import CSV (porter depuis v5.6)
3. Liste transactions
4. Catégories + règles

**Phase 3 : Features couple (1-2 semaines)**
1. Budgets
2. Validation croisée
3. Système foyer (depuis FinCouple)

**Phase 4+ : Avancées (plus tard)**
- IA avec API KIM
- Export PDF
- Audit
- etc.

---

## 📞 Prochaine action

**Pour avancer, j'ai besoin que tu :**

1. **Lis** `COMPARAISON_MIGRATION.md` pour comprendre les différences
2. **Remplis** `QUESTIONNAIRE_MIGRATION.md` avec tes choix
3. **Envoies-moi** tes réponses
4. **Je génère** le plan détaillé

---

## 🗂️ Fichiers créés aujourd'hui

```
FinancePerso/
├── STRATEGIE.md                    ✅ Vision globale
├── COMPARAISON_MIGRATION.md        ✅ Analyse détaillée
├── QUESTIONNAIRE_MIGRATION.md      ✅ Questions à répondre
├── MIGRATION_GUIDE.md              ✅ Ce document
│
├── v5.6 Streamlit (conservé)
│   ├── app.py
│   ├── modules/ (287 fichiers)
│   └── Data/finance.db (471 tx)
│
└── FinCouple React (développement)
    └── Ideas/couple-cashflow-clever-main/
```

---

**Prêt à répondre au questionnaire ?** 🚀
