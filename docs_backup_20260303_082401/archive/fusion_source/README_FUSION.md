# 📚 Documentation - Fusion FinCouple Pro

> Guide de navigation vers la documentation de fusion

---

## 🎯 Contexte

Le projet FinancePerso évolue vers une **fusion** avec FinCouple pour créer **FinCouple Pro**.

**Architecture cible**:
- Frontend: React + TypeScript (basé sur FinCouple)
- Backend: FastAPI + Python (basé sur FinancePerso)
- Database: SQLite locale (privacy-first)
- Admin: Streamlit (parties avancées FinancePerso)

---

## 📁 Organisation des Documents

### Documentation Fusion (Nouveau)

Dossier: `docs/Plan de migration fusion/`

| Document | Description | Priorité |
|----------|-------------|----------|
| `FUSION_INDEX.md` | Point d'entrée, vue d'ensemble | ⭐⭐⭐ |
| `FUSION_MASTERPLAN.md` | Plan stratégique 12 mois | ⭐⭐⭐ |
| `FUSION_TECHNICAL_SPEC.md` | Specs techniques FastAPI/React | ⭐⭐⭐ |
| `FUSION_UI_UX_ROADMAP.md` | Design system, parcours UX | ⭐⭐⭐ |
| `FUSION_GETTING_STARTED.md` | Checklist démarrage concret | ⭐⭐ |

### Documentation Qualité (Terminée)

| Document | Description | Status |
|----------|-------------|--------|
| `CODE_QUALITY_ROADMAP.md` | ~~Plan qualité FinancePerso~~ | ✅ Archivé |
| `FUSION_ACTION_PLAN.md` | Plan d'action fusion | 🔄 Actif |

### Documentation Technique (FinancePerso)

| Document | Description |
|----------|-------------|
| `AGENTS.md` | Guide agents AI ( FinancePerso) |
| `adr/001-sqlite-choice.md` | ADR SQLite |
| `adr/002-ia-architecture.md` | ADR Architecture IA |

---

## 🚀 Par où commencer ?

### Si vous découvrez le projet:

1. **Lire** `FUSION_INDEX.md` (vue d'ensemble)
2. **Lire** `FUSION_MASTERPLAN.md` (stratégie)
3. **Lire** `FUSION_GETTING_STARTED.md` (actions concrètes)

### Si vous êtes développeur:

1. **Lire** `FUSION_TECHNICAL_SPEC.md` (architecture)
2. **Lire** `FUSION_UI_UX_ROADMAP.md` (design system)
3. **Suivre** `FUSION_ACTION_PLAN.md` (plan d'action)

### Si vous êtes designer:

1. **Lire** `FUSION_UI_UX_ROADMAP.md` (design system)
2. **Lire** `FUSION_MASTERPLAN.md` (parcours utilisateur)

---

## 📊 Status

### ✅ Terminé (FinancePerso)
- Qualité code: Ruff 0 erreurs
- Sécurité: Bandit 0 High/Medium
- Documentation: 6 fichiers créés
- Tests: 13/13 essentiels passent

### 🔄 En cours (Fusion)
- Phase 1: Setup & Fondations
- Repository: À créer
- Architecture: À implémenter

---

## 🔗 Liens Rapides

```bash
# Documentation fusion
cd "docs/Plan de migration fusion/"

# Plan d'action
cat docs/FUSION_ACTION_PLAN.md

# Code source FinancePerso
# /Users/aurelien/Documents/Projets/FinancePerso

# Code source FinCouple  
# /Users/aurelien/Documents/Projets/FinancePerso/Ideas/couple-cashflow-clever-main
```

---

## ❓ Questions Fréquentes

**Q: Pourquoi cette fusion ?**
R: Combiner les forces des deux projets - UX moderne de FinCouple + fonctionnalités avancées de FinancePerso.

**Q: Que devient FinancePerso ?**
R: La logique métier est réutilisée dans l'API FastAPI. L'UI Streamlit devient l'interface admin.

**Q: Timeline ?**
R: 6-12 mois selon l'équipe. Voir `FUSION_MASTERPLAN.md`.

**Q: Où est le nouveau code ?**
R: Repository `fincouple-pro` à créer. Voir `FUSION_GETTING_STARTED.md`.

---

*Dernière mise à jour: 2026-03-02*
