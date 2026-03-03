# 📘 MÉMOIRE - FinancePerso (MyFinance Companion)

> **Document unique de référence** - État actuel, historique et évolutions
> 
> **Version applicative** : 5.5.0  
> **Date de mise à jour** : 2026-02-28  
> **Lignes de code** : ~21,000+  
> **Statut global** : ✅ Stable et maintenue

---

## 📋 SOMMAIRE

1. [Vue d'ensemble](#1-vue-densemble)
2. [Stack technique](#2-stack-technique)
3. [Historique des évolutions majeures](#3-historique-des-évolutions-majeures)
4. [État actuel par module](#4-état-actuel-par-module)
5. [Roadmap future](#5-roadmap-future)
6. [Métriques et KPIs](#6-métriques-et-kpis)
7. [Personas utilisateurs](#7-personas-utilisateurs)
8. [Annexes](#8-annexes)

---

## 1. VUE D'ENSEMBLE

### 🎯 Mission
FinancePerso est une application de gestion financière personnelle qui aide les utilisateurs à :
- Importer et catégoriser automatiquement leurs transactions bancaires
- Suivre leurs budgets et dépenses
- Obtenir des insights intelligents via l'IA
- Planifier leur épargne et projet d'achat

### 📊 Chiffres clés
| Métrique | Valeur |
|----------|--------|
| Modules Python | 185+ |
| Pages Streamlit | 13 |
| Tests automatisés | 13 essentiels (100% pass) |
| Couverture tests | ~65% |
| Temps de chargement dashboard | < 2s |
| Score qualité code | A |

### 🏆 Scores d'évolution
| Dimension | Score Initial | Score Actuel | Évolution |
|-----------|---------------|--------------|-----------|
| **Sécurité** | 75/100 | 95/100 | ✅ +20 |
| **Performance** | 72/100 | 88/100 | ✅ +16 |
| **Architecture** | 78/100 | 90/100 | ✅ +12 |
| **Indispensabilité** | 58/100 | 82/100 | ✅ +24 |

---

## 2. STACK TECHNIQUE

### Core
| Composant | Technologie | Version |
|-----------|-------------|---------|
| Langage | Python | 3.12+ |
| Framework Web | Streamlit | 1.47.0 |
| Base de données | SQLite | 3.x |
| Data Science | pandas, plotly | 2.3.1, 6.2.0 |

### IA & ML
| Composant | Technologie | Usage |
|-----------|-------------|-------|
| IA Cloud | Google GenAI | Catégorisation, assistant |
| ML Local | scikit-learn | Catégorisation offline |
| Alternative | Ollama, DeepSeek | Fallback IA |

### Infrastructure
| Composant | Technologie | Usage |
|-----------|-------------|-------|
| Chiffrement | cryptography (AES-256) | Données sensibles |
| Monitoring | sentry-sdk | Error tracking |
| Cache | st.cache_data + disque | Performance |
| Tests | pytest | Qualité |

---

## 3. HISTORIQUE DES ÉVOLUTIONS MAJEURES

### Phase 1 : Fondations (Février 2026)
**Objectif** : Stabiliser et sécuriser l'application

| Feature | Statut | Impact |
|---------|--------|--------|
| Protection injection SQL | ✅ | Sécurité renforcée |
| Optimisation N+1 Query | ✅ | Performance +99.97% |
| Exceptions spécifiques | ✅ | Meilleure traçabilité |
| Repository Pattern | ✅ | Architecture propre |
| Schéma test/prod sync | ✅ | Tests fiables |

### Phase 2 : Stabilisation (Février 2026)
**Objectif** : Qualité et cohérence

| Feature | Statut | Impact |
|---------|--------|--------|
| Fusion fonctions dupliquées | ✅ | Code maintenable |
| merge_utils.py | ✅ | Factorisation |
| Salt chiffrement obligatoire | ✅ | Sécurité production |
| README à jour | ✅ | Onboarding |

### Phase 3 : Amélioration (Février 2026)
**Objectif** : UX et accessibilité

| Feature | Statut | Impact |
|---------|--------|--------|
| Circuit Breaker IA | ✅ | Fiabilité IA |
| Daily Widget | ✅ | Rétention quotidienne |
| Templates import bancaires | ✅ | Réduction friction (6 banques) |
| Support PWA | ✅ | Mobile-friendly |

### Phase 4 : Innovation (Février 2026)
**Objectif** : Indispensabilité

| Feature | Statut | Impact |
|---------|--------|--------|
| Notifications V3 | ✅ | 20+ types, 6 détecteurs |
| Système cashflow | ✅ | Prévisions 3+ mois |
| Gamification | ✅ | 11 badges, streaks, challenges |
| Design System V2 | ✅ | Cohérence UI |

### Versions récentes (CHANGELOG)

#### [5.5.0] - 2026-02-27
- **Notifications V3** : Système unifié avec 20+ types, 6 détecteurs automatiques
- **Design System V2** : Tokens, atomes, molécules, templates
- **Corrections** : DailyWidget, scroll-to-top, audit actions

#### [5.2.1] - 2026-02-25
- **Repository Pattern** complet
- **Daily Widget** avec insights personnalisés
- **Templates bancaires** (Boursorama, ING, etc.)
- **Circuit Breaker** IA

---

## 4. ÉTAT ACTUEL PAR MODULE

### 4.1 Core (Database)
**Statut** : ✅ Stable

| Composant | État | Notes |
|-----------|------|-------|
| `modules/db/connection.py` | ✅ | Protection SQL injection |
| `modules/db/transactions.py` | ✅ | Repository Pattern |
| `modules/db/members.py` | ✅ | Optimisé N+1 |
| `modules/db/categories.py` | ✅ | Utilise merge_utils |
| `modules/db/migrations.py` | ✅ | À jour |

### 4.2 IA & ML
**Statut** : ✅ Fonctionnel

| Composant | État | Notes |
|-----------|------|-------|
| `modules/ai_manager_v2.py` | ✅ | Circuit Breaker |
| `modules/ai/` (12 modules) | ✅ | Suite IA complète |
| Catégorisation cascade | ✅ | Règles → ML → IA Cloud |

### 4.3 UI & Frontend
**Statut** : ✅ Modernisé

| Composant | État | Notes |
|-----------|------|-------|
| `modules/ui/tokens/` | ✅ | Design System V2 |
| `modules/ui/atoms/` | ✅ | Boutons, badges, icônes |
| `modules/ui/molecules/` | ✅ | Cards, metrics |
| Daily Widget | ✅ | Hook quotidien |

### 4.4 Features Métier
**Statut** : ✅ Complets

| Feature | État | Notes |
|---------|------|-------|
| Import CSV | ✅ | 6 templates banques |
| Validation transactions | ✅ | Regroupement intelligent |
| Budgets | ✅ | Alertes 80% |
| Abonnements | ✅ | Détection auto |
| Cashflow | ✅ | Prévisions |
| Gamification | ✅ | Badges, streaks |
| Notifications | ✅ | V3 avec persistance |

### 4.5 Pages Streamlit
**Statut** : ✅ Toutes fonctionnelles

| Page | Statut | Fonction |
|------|--------|----------|
| `1_Opérations.py` | ✅ | Import + Validation |
| `3_Synthèse.py` | ✅ | Dashboard |
| `4_Intelligence.py` | ✅ | IA + Audit + Règles |
| `5_Budgets.py` | ✅ | Gestion budgétaire |
| `7_Assistant.py` | ✅ | Chat IA |
| `8_Recherche.py` | ✅ | Recherche globale |
| `9_Configuration.py` | ✅ | Paramètres |
| `12_Abonnements.py` | ✅ | Suivi abonnements |
| `13_Patrimoine.py` | ✅ | Vue patrimoine |

---

## 5. ROADMAP FUTURE

### 🔴 Priorité P0 (Prochaines semaines)

| Feature | Description | Impact |
|---------|-------------|--------|
| Tests complémentaires | Unit tests nouveaux modules | Qualité |
| Icônes PWA | Multi-tailles pour iOS/Android | Mobile |
| Documentation API | Cashflow + Gamification | Développeur |

### 🟡 Priorité P1 (Ce mois)

| Feature | Description | Impact |
|---------|-------------|--------|
| Templates internationaux | Banques hors France | Expansion |
| Feedback gamification | Collecte métriques usage | Optimisation |
| Affinage détecteurs | Alertes plus pertinentes | UX |

### 🟢 Priorité P2 (3 mois)

| Feature | Description | Impact |
|---------|-------------|--------|
| API ouverte | Webhooks pour extensions | Intégrations |
| Connexion bancaire | Bridge/Budget Insight | Friction ↓ |
| Export PDF | Rapports automatisés | Partage |

### 🔮 Vision long terme

| Feature | Description | Horizon |
|---------|-------------|---------|
| Sync multi-device | Cloud + réplication | 6 mois |
| App native | React Native ou Tauri | 6-12 mois |
| Open Banking | PSD2 direct | 12 mois |

---

## 6. MÉTRIQUES ET KPIs

### Objectifs atteints ✅

| KPI | Cible | Actuel | Statut |
|-----|-------|--------|--------|
| Score sécurité | > 90 | 95 | ✅ |
| Score performance | > 85 | 88 | ✅ |
| Score architecture | > 85 | 90 | ✅ |
| Tests essentiels | 100% | 100% | ✅ |
| Temps chargement | < 2s | < 2s | ✅ |

### KPIs à suivre 📊

| KPI | Cible | Horizon |
|-----|-------|---------|
| Couverture tests | 80% | 3 mois |
| Rétention D30 | > 40% | 6 mois |
| NPS | > 40 | 6 mois |
| Usage mobile | 30% | 6 mois |

---

## 7. PERSONAS UTILISATEURS

### 👤 Marie - La Contrôleuse (35 ans, salariée)
- **Usage** : 2-3 fois/semaine, sessions courtes
- **Besoins** : Explorer anomalies, comprendre dépenses
- **Pain points résolus** : Dashboard rapide, preview import, feedback

### 👤 Thomas - L'Optimiseur (42 ans, cadre)
- **Usage** : Quotidien, sessions longues
- **Besoins** : Suivre abonnements, identifier économies
- **Pain points résolus** : Analyses rapides, backup auto, fiabilité

### 👤 Sophie - La Débutante (28 ans, freelance)
- **Usage** : Irrégulier, besoin de guidance
- **Besoins** : Guidance pas à pas, explications simples
- **Pain points résolus** : Corbeille (undo), preview, documentation

### 👤 Pierre - Le Couple (45 ans, famille)
- **Usage** : Hebdomadaire, focus répartition
- **Besoins** : Attribution facile, vue consolidée
- **Pain points résolus** : Performance générale, multi-membres

---

## 8. ANNEXES

### 8.1 Risques et mitigations

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Performance à long terme | Élevée | Élevé | Pagination, caching, archivage |
| Perte de données | Moyenne | Critique | Backup auto, corbeille, export |
| Changement format banques | Moyenne | Élevé | Templates + fallback |

### 8.2 Commandes essentielles

```bash
# Démarrage
make run

# Tests
make test          # Essentiels (~5s)
make test-all      # Complets (~30s)

# Qualité
make lint
make format
make check

# Docker
docker-compose up -d
```

### 8.3 Structure des fichiers clés

```
FinancePerso/
├── docs/MEMOIRE.md          ← Vous êtes ici
├── app.py                    # Entry point
├── modules/                  # Core business
│   ├── ai/                   # Suite IA
│   ├── db/                   # Couche données
│   ├── ui/                   # Composants UI
│   ├── cashflow/             # Prévisions
│   └── gamification/         # Badges, streaks
├── pages/                    # 13 pages Streamlit
└── tests/                    # Tests pytest
```

### 8.4 Documentation associée

| Document | Description |
|----------|-------------|
| `README.md` | Guide d'installation et usage |
| `AGENTS.md` | Guide développement |
| `CHANGELOG.md` | Historique détaillé versions |
| `docs/archive/` | Documentation historique |

---

## 📝 NOTES DE MAINTENANCE

**Règles pour ce document :**
- Mettre à jour après chaque release majeure
- Archiver les features obsolètes dans `docs/archive/`
- Maintenir les scores à jour après audit
- Ajouter les nouveaux personas si identifiés

**Dernière mise à jour** : 2026-02-28 (v5.5.0)

---

*Document unique de référence - Ne pas dupliquer l'information ailleurs*
