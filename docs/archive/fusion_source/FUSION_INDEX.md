# 📚 Index - Documentation Fusion FinCouple Pro

> Point d'entrée pour toute la documentation de fusion

---

## 📖 Documents principaux

| Document | Description | Audience | Priorité |
|----------|-------------|----------|----------|
| **[FUSION_MASTERPLAN.md](./FUSION_MASTERPLAN.md)** | Plan stratégique complet | Tous | ⭐⭐⭐ |
| **[FUSION_TECHNICAL_SPEC.md](./FUSION_TECHNICAL_SPEC.md)** | Spécifications techniques | Développeurs | ⭐⭐⭐ |
| **[FUSION_UI_UX_ROADMAP.md](./FUSION_UI_UX_ROADMAP.md)** | Design system & parcours UX | Designers/Dev | ⭐⭐⭐ |
| **[FUSION_GETTING_STARTED.md](./FUSION_GETTING_STARTED.md)** | Checklist démarrage | Développeurs | ⭐⭐ |

---

## 🗺️ Vue d'ensemble du plan

```
┌─────────────────────────────────────────────────────────────────┐
│                    PLAN DE FUSION - 12 MOIS                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Q1: FONDATIONS                                                 │
│  ├── M1: Setup API + React + Auth                              │
│  ├── M2: Database + CRUD                                       │
│  └── M3: Import CSV + Migration données                        │
│                                                                 │
│  Q2: CORE FEATURES                                              │
│  ├── M4: Dashboard React                                       │
│  ├── M5: Budgets & Objectifs                                   │
│  └── M6: Gestion Couple (basique)                              │
│                                                                 │
│  Q3: INTELLIGENCE                                               │
│  ├── M7: Catégorisation IA                                     │
│  ├── M8: Projections patrimoine                                │
│  └── M9: Admin Streamlit                                       │
│                                                                 │
│  Q4: RELEASE                                                    │
│  ├── M10: Gamification                                         │
│  ├── M11: Tests & Optimisation                                 │
│  └── M12: Migration & Documentation                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Architecture cible

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  React App   │     │  Streamlit   │     │   Mobile     │
│  (Dashboard) │     │   (Admin)    │     │    (PWA)     │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │ HTTP / WebSocket
                            ▼
              ┌─────────────────────────┐
              │    FastAPI (Python)     │
              │  • REST API             │
              │  • WebSocket            │
              │  • Auth JWT             │
              │  • IA / ML              │
              └───────────┬─────────────┘
                          │
                          ▼
              ┌─────────────────────────┐
              │    SQLite (Local)       │
              │  • Chiffrement option   │
              │  • Backup automatique   │
              └─────────────────────────┘
```

---

## 📊 Comparaison des projets

| Aspect | FinancePerso | FinCouple | Fusion |
|--------|-------------|-----------|--------|
| **Stack** | Python/Streamlit | React/TS/Vite | React + Python API |
| **DB** | SQLite | Supabase | SQLite (privacy) |
| **Lignes de code** | ~65,000 | ~7,000 | ~40,000 (optimisé) |
| **UI/UX** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ (objectif) |
| **Features** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ (objectif) |
| **Mobile** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ (objectif) |

---

## 📁 Structure du nouveau projet

```
fincouple-pro/                          # Monorepo
├── 📁 apps/
│   ├── 📁 web/                        # React + Vite
│   │   ├── src/features/              # Dashboard, Transactions, Import...
│   │   └── package.json
│   │
│   └── 📁 admin/                      # Streamlit Admin
│       ├── pages/                     # Audit, Config, Projections
│       └── requirements.txt
│
├── 📁 api/                            # FastAPI
│   ├── src/
│   │   ├── routers/                   # Endpoints REST
│   │   ├── services/                  # Logique métier
│   │   │   ├── ai/                    # Catégorisation IA
│   │   │   ├── wealth/                # Projections
│   │   │   └── couple/                # Gestion couple
│   │   └── models/                    # SQLAlchemy
│   └── tests/
│
├── 📁 database/
│   └── migrations/
│
├── 📁 docs/                           # Documentation
│   ├── FUSION_MASTERPLAN.md
│   ├── FUSION_TECHNICAL_SPEC.md
│   ├── FUSION_UI_UX_ROADMAP.md
│   └── FUSION_GETTING_STARTED.md
│
└── docker-compose.yml                 # Orchestration
```

---

## 🚀 Démarrage rapide

### 1. Lecture (30 min)
Lisez dans cet ordre:
1. [FUSION_MASTERPLAN.md](./FUSION_MASTERPLAN.md) - Vision globale
2. [FUSION_GETTING_STARTED.md](./FUSION_GETTING_STARTED.md) - Actions concrètes

### 2. Setup (2h)
```bash
# Créer structure
mkdir fincouple-pro && cd fincouple-pro

# Copier ce template
git clone <template> .

# Démarrer
docker-compose up
```

### 3. Développement (Mois 1)
Suivez le [FUSION_GETTING_STARTED.md](./FUSION_GETTING_STARTED.md) - Section "Sprint 1"

---

## 📝 Checklist de validation

### Avant de commencer:
- [ ] Avoir lu les 4 documents
- [ ] Avoir accès aux 2 projets source
- [ ] Avoir validé l'approche hybride
- [ ] Avoir identifié l'équipe

### Chaque mois:
- [ ] Réunion de revue
- [ ] Mise à jour des KPIs
- [ ] Documentation à jour
- [ ] Tests passent

### À la fin:
- [ ] Tous les P0 implémentés
- [ ] Documentation complète
- [ ] Migration des utilisateurs
- [ ] Archive de l'ancien projet

---

## 🔗 Liens utiles

### Projets source
- **FinancePerso**: `/Users/aurelien/Documents/Projets/FinancePerso`
- **FinCouple**: `/Users/aurelien/Documents/Projets/FinancePerso/Ideas/couple-cashflow-clever-main`

### Technologies
- [FastAPI](https://fastapi.tiangolo.com)
- [React](https://react.dev)
- [shadcn/ui](https://ui.shadcn.com)
- [SQLAlchemy](https://docs.sqlalchemy.org)

### Documentation projet
- [AGENTS.md](../AGENTS.md) - Guide FinancePerso existant
- [README.md](../README.md) - Vue d'ensemble FinancePerso

---

## ❓ FAQ

**Q: Pourquoi ne pas garder Streamlit uniquement?**
R: Streamlit est limité pour l'UX moderne (mobile, interactions temps réel). React offre une meilleure expérience utilisateur.

**Q: Pourquoi garder Streamlit alors?**
R: Parfait pour les outils admin complexes (audit, configuration, debug) sans réécriture complète.

**Q: Pourquoi SQLite et pas PostgreSQL?**
R: Privacy-first - les données restent locales. Pas de dépendance cloud obligatoire.

**Q: Combien de temps ça prend vraiment?**
R: 6-12 mois selon l'équipe. 3.5 FTE = ~6 mois. 1-2 FTE = ~12 mois.

**Q: Et les utilisateurs existants?**
R: Migration progressive avec parallel run. Pas de downtime forcé.

---

## 📞 Support

En cas de questions:
1. Relire les documents concernés
2. Vérifier les exemples de code
3. Consulter la documentation des technologies
4. Demander une clarification

---

**Version:** 1.0  
**Date:** 2026-03-02  
**Status:** ✅ Prêt pour démarrage

---

*Let's build FinCouple Pro! 💰💚*
