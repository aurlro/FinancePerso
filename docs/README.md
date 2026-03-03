# Documentation FinancePerso

> Bienvenue dans la documentation de FinancePerso (MyFinance Companion)

---

## 🎯 Navigation Rapide

Choisissez votre profil pour trouver rapidement ce dont vous avez besoin:

### 👤 Utilisateur
- **[Guide de démarrage](ACTIVE/user-guide/getting-started.md)** - Première utilisation
- **[Migration V5.5](ACTIVE/migration/v5-5-dashboard.md)** - Nouveau dashboard
- **[Guide utilisateur complet](USER_GUIDE.md)** - Toutes les fonctionnalités

### 👨‍💻 Développeur
- **[Architecture](REFERENCE/architecture/v6-target.md)** - Structure du projet
- **[Contribution](../CONTRIBUTING.md)** - Comment contribuer
- **[AGENTS.md](../AGENTS.md)** - Guide agents AI

### 📊 Architecte / PO
- **[ADRs](REFERENCE/adr/)** - Décisions d'architecture
- **[Personas](REFERENCE/personas/personas-et-parcours.md)** - Utilisateurs cibles
- **[Planning](PLANNING/)** - Roadmaps et spécifications

---

## 📚 Organisation de la Documentation

```
docs/
├── 📖 ACTIVE/        Documentation à jour et maintenue
├── 🎯 PLANNING/      Plans et spécifications futures  
├── 📋 REFERENCE/     Documentation technique stable
└── 📦 archive/       Historique et documents obsolètes
```

### [📖 ACTIVE/](ACTIVE/)
Documentation maintenue à jour pour la version actuelle (5.5.x).

- **user-guide/** - Guides d'utilisation
- **migration/** - Guides de migration entre versions
- **development/** - Documentation développeur
- **api/** - Documentation API

### [🎯 PLANNING/](PLANNING/)
Plans, roadmaps et spécifications pour les évolutions.

- **current/** - Implémentation en cours
- **fusion/** - Projet Fusion (futur)
- **v5-5/** - Archives du projet V5.5 (réalisé)

### [📋 REFERENCE/](REFERENCE/)
Documentation de référence stable.

- **adr/** - Architecture Decision Records
- **architecture/** - Documentation architecture
- **personas/** - Profils utilisateurs
- **specifications/** - Spécifications détaillées

### [📦 archive/](archive/)
Documentation historique conservée pour référence.

Organisée par période et par type de document.

---

## 🚀 Démarrage Rapide

### Installation
```bash
# Cloner le repo
git clone <repo-url>
cd FinancePerso

# Installer les dépendances
make setup

# Lancer l'application
make run
```

### Accès Application
Par défaut: http://localhost:8501

---

## 📖 Documentation Externe

- [README principal](../README.md) - Vue d'ensemble du projet
- [CHANGELOG](../CHANGELOG.md) - Historique des versions
- [CODE OF CONDUCT](../CODE_OF_CONDUCT.md) - Code de conduite

---

## 🔄 Cycle de Vie de la Documentation

| Statut | Emplacement | Description |
|--------|-------------|-------------|
| 🟢 Active | `ACTIVE/` | Maintenue à jour, référence actuelle |
| 🟡 Planning | `PLANNING/` | En cours de rédaction, sujet à changement |
| 🔵 Reference | `REFERENCE/` | Stable, validée, historisée |
| ⚪ Archive | `archive/` | Obsolète mais conservée |

---

## 🆘 Besoin d'Aide ?

- 🔍 Consultez l'[INDEX.md](INDEX.md) pour une navigation détaillée
- 🐛 Signalez un bug via les Issues GitHub
- 💡 Proposez une amélioration via une PR

---

*Documentation FinancePerso - Version 5.5*
