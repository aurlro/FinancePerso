# Code Quality Roadmap

> Plan d'amélioration adapté vers la fusion FinCouple Pro

---

## 📋 Contexte

Ce document a évolué depuis la qualité code de FinancePerso vers le **Plan de Fusion FinCouple Pro**.

**Nouveau contexte**: Fusion de FinancePerso (Streamlit/Python) + FinCouple (React/TS) → FinCouple Pro (React + FastAPI + SQLite)

📁 **Documentation fusion détaillée**: `docs/Plan de migration fusion/`

---

## ✅ Phases Terminées (FinancePerso)

### Phase 1: Stabilisation ✅
- Syntaxe corrigée, CI passe
- Erreurs f-string corrigées
- Ruff configuration stable

### Phase 2: Qualité Code ✅
- Ruff 0 erreurs (line-length: 120)
- E741, F811, F821 corrigés
- 13/13 tests essentiels passent

### Phase 3: Sécurité ✅
- Bandit 0 High/Medium
- B324 corrigé (usedforsecurity=False)
- B608/B301 configurés

### Phase 4: Documentation ✅
- 4 README modules créés
- 2 ADRs créés
- `.bandit.yaml` configuré

---

## 🚀 Phase 5: Fusion FinCouple Pro 🔄 NEXT

### 5.1 Setup & Fondations (Mois 1)

#### Semaine 1: Infrastructure
- [ ] Créer monorepo `fincouple-pro`
- [ ] Setup Docker Compose
- [ ] CI/CD GitHub Actions
- [ ] Structure dossiers

#### Semaine 2: Backend FastAPI
- [ ] Setup FastAPI + SQLAlchemy
- [ ] Modèles de données
- [ ] Auth JWT
- [ ] CRUD de base

#### Semaine 3: Frontend React
- [ ] React 18 + TypeScript + Vite
- [ ] shadcn/ui + Tailwind
- [ ] React Query + Router
- [ ] Structure features

#### Semaine 4: Database
- [ ] Schéma SQLite
- [ ] Migrations Alembic
- [ ] Scripts migration

### 5.2 Core Features (Mois 2-3)
- [ ] Import CSV
- [ ] Dashboard React
- [ ] Transactions CRUD
- [ ] Vue couple basique

### 5.3 Intelligence (Mois 4-6)
- [ ] IA Catégorisation
- [ ] Budgets dynamiques
- [ ] Projections patrimoine
- [ ] Admin Streamlit

### 5.4 Release (Mois 7-9)
- [ ] Gamification
- [ ] Tests & Optimisations
- [ ] Documentation
- [ ] Migration utilisateurs

---

## 📁 Documents de Référence

### Documentation Fusion (dossier complet)
| Document | Description |
|----------|-------------|
| `FUSION_INDEX.md` | Point d'entrée documentation |
| `FUSION_MASTERPLAN.md` | Plan stratégique 12 mois |
| `FUSION_TECHNICAL_SPEC.md` | Spécifications techniques |
| `FUSION_UI_UX_ROADMAP.md` | Design system & UX |
| `FUSION_GETTING_STARTED.md` | Checklist démarrage |

### Documents Créés
| Document | Description |
|----------|-------------|
| `FUSION_ACTION_PLAN.md` | Plan d'action détaillé (ce document) |

---

## 🔧 Stack Technique

### Frontend
- React 18 + TypeScript
- Vite + Tailwind CSS
- shadcn/ui
- React Query + Zustand

### Backend
- FastAPI (Python 3.12)
- SQLAlchemy 2.0
- Alembic
- Pydantic

### Database
- SQLite (privacy-first)
- Chiffrement optionnel

---

## 📊 Métriques

### Qualité Code Actuelle (FinancePerso)
| Métrique | Valeur |
|----------|--------|
| Ruff errors | 0 ✅ |
| Bandit High/Medium | 0 ✅ |
| Tests passants | 13/13 ✅ |
| Documentation | 6 fichiers ✅ |

### Objectifs FinCouple Pro
| Métrique | Cible |
|----------|-------|
| Test coverage | > 80% |
| Lighthouse | > 90 |
| Bundle size | < 500KB |
| API latency | < 100ms |

---

## 🗓️ Timeline

```
2026
├── Q1: FONDATIONS (M1-M3)
│   ├── Setup + Auth
│   ├── Import + Dashboard
│   └── Transactions + Couple
│
├── Q2: INTELLIGENCE (M4-M6)
│   ├── IA + Catégorisation
│   ├── Budgets + Projections
│   └── Admin Streamlit
│
└── Q3: RELEASE (M7-M9)
    ├── Gamification
    ├── Tests + Optimisations
    └── Migration + Launch
```

---

## ✅ Prochaines Actions Immédiates

1. **Lire** la documentation fusion complète
2. **Valider** l'approche technique avec stakeholders
3. **Créer** le repository `fincouple-pro`
4. **Commencer** Phase 5.1 (Setup Infrastructure)

---

*Dernière mise à jour: 2026-03-02*
*Status: Phases 1-4 ✅ - Phase 5 🚀 Démarrage*
