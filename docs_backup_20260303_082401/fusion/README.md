# 🚀 FinCouple Pro - Documentation Fusion

> Fusion de FinancePerso + FinCouple vers React + FastAPI + SQLite

---

## 📚 Documents

| Document | Description | Quand le lire |
|----------|-------------|---------------|
| **[01_VISION.md](./01_VISION.md)** | Pourquoi et quoi | Découverte du projet |
| **[02_PLAN.md](./02_PLAN.md)** | Roadmap 9 mois détaillée | Planning & suivi |
| **[03_SPECS.md](./03_SPECS.md)** | Specs techniques | Développement |
| **[04_UI_UX.md](./04_UI_UX.md)** | Design system & UX | Design & Frontend |
| **[05_START.md](./05_START.md)** | Guide démarrage immédiat | Premier jour |

---

## 🎯 Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                    FINCOUPLE PRO                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   React App (Dashboard)          Streamlit (Admin)         │
│   ├── Transactions               ├── Audit données         │
│   ├── Import CSV                 ├── Config règles IA      │
│   ├── Budgets                    ├── Projections avancées  │
│   └── Vue Couple                 └── Export comptable       │
│                                                             │
│                      ↕ HTTP/WebSocket                       │
│                                                             │
│              FastAPI (Python 3.12)                         │
│              ├── Auth JWT                                  │
│              ├── CRUD + Business Logic                     │
│              ├── IA (categorization)                       │
│              └── WebSocket (notifications)                 │
│                                                             │
│                      ↕ SQLAlchemy                           │
│                                                             │
│              SQLite (local, chiffré)                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Chiffres clés

| | FinancePerso | FinCouple | Fusion |
|---|---|---|---|
| **Stack** | Streamlit + SQLite | React + Supabase | React + FastAPI + SQLite |
| **Lignes** | ~65k Python | ~7k TypeScript | ~40k (optimisé) |
| **Fonctionnalités** | 50+ | 8 | 35+ essentielles |
| **Timeline** | 2+ ans | 2 mois | 6-9 mois |

---

## 🗓️ Timeline

```
2026
├── Q1 (M1-M3): FONDATIONS
│   ├── Setup React + FastAPI
│   ├── Auth + CRUD
│   └── Import CSV + Dashboard
│
├── Q2 (M4-M6): INTELLIGENCE
│   ├── IA Categorization
│   ├── Budgets dynamiques
│   └── Projections patrimoine
│
└── Q3 (M7-M9): RELEASE
    ├── Gamification
    ├── Tests + Optimisations
    └── Migration utilisateurs
```

---

## ✅ Checklist démarrage

- [ ] Lire [01_VISION.md](./01_VISION.md)
- [ ] Lire [05_START.md](./05_START.md)
- [ ] Créer repository `fincouple-pro`
- [ ] Setup Docker Compose
- [ ] Hello World API + React

---

*Documentation consolidée - 2026-03-02*
