# Index de la Documentation - FinancePerso

> Navigation centrale vers toute la documentation du projet

---

## 📚 Structure de la Documentation

```
docs/
├── README.md              ← Commencez ici
├── INDEX.md               ← Vous êtes ici
├── ACTIVE/                📖 Documentation active et maintenue
├── PLANNING/              🎯 Plans, roadmaps et spécifications futures
├── REFERENCE/             📋 Référence technique et ADRs
├── adr/                   🏛️ Architecture Decision Records (legacy)
└── archive/               📦 Documentation historique et obsolète
```

---

## 🚀 Par où commencer ?

| Si vous cherchez... | Allez dans... |
|---------------------|---------------|
| Comment utiliser l'application | [ACTIVE/user-guide/getting-started.md](ACTIVE/user-guide/getting-started.md) |
| Comprendre l'architecture | [REFERENCE/architecture/v6-target.md](REFERENCE/architecture/v6-target.md) |
| Voir les décisions techniques | [REFERENCE/adr/](REFERENCE/adr/) |
| Migrer vers une nouvelle version | [ACTIVE/migration/](ACTIVE/migration/) |
| Contribuer au projet | [../CONTRIBUTING.md](../CONTRIBUTING.md) |

---

## 📖 Documentation Active (ACTIVE/)

Documentation maintenue à jour et pertinente pour la version actuelle.

### Guides Utilisateur
- [getting-started.md](ACTIVE/user-guide/getting-started.md) - Guide de démarrage rapide

### Guides de Migration
- [v5-5-dashboard.md](ACTIVE/migration/v5-5-dashboard.md) - Migration Dashboard V5.5
- [notifications-v3.md](ACTIVE/migration/notifications-v3.md) - Migration Notifications V3

### Développement
- [Développement](ACTIVE/development/) - Guides pour développeurs

### API
- [API](ACTIVE/api/) - Documentation des APIs internes

---

## 🎯 Planification (PLANNING/)

Plans, spécifications et roadmaps pour les évolutions futures.

### En Cours
- [implementation-summary.md](PLANNING/current/implementation-summary.md) - Résumé de l'implémentation
- [synthese-reutilisation.md](PLANNING/current/synthese-reutilisation.md) - Synthèse de réutilisation

### Fusion (Projet Futur)
- [README.md](PLANNING/fusion/README.md) - Vue d'ensemble du projet Fusion
- [01-vision.md](PLANNING/fusion/01-vision.md) - Vision produit
- [02-plan.md](PLANNING/fusion/02-plan.md) - Plan d'implémentation
- [03-specs.md](PLANNING/fusion/03-specs.md) - Spécifications techniques
- [04-ui-ux.md](PLANNING/fusion/04-ui-ux.md) - Roadmap UI/UX
- [05-start.md](PLANNING/fusion/05-start.md) - Guide de démarrage

### V5.5 (Réalisé)
- [audit-comparatif.md](PLANNING/v5-5/audit-comparatif.md) - Audit comparatif
- [comparaison-html.md](PLANNING/v5-5/comparaison-html.md) - Comparaison avec HTML
- [plan-maquette.md](PLANNING/v5-5/plan-maquette.md) - Plan de maquette

---

## 📋 Référence Technique (REFERENCE/)

Documentation technique stable et historisée.

### Architecture
- [v6-target.md](REFERENCE/architecture/v6-target.md) - Architecture cible V6

### ADRs (Architecture Decision Records)
- [001-sqlite-choice.md](REFERENCE/adr/001-sqlite-choice.md) - Choix de SQLite
- [002-ia-architecture.md](REFERENCE/adr/002-ia-architecture.md) - Architecture IA

### Personas
- [personas-et-parcours.md](REFERENCE/personas/personas-et-parcours.md) - Personas utilisateurs

### Spécifications
- [memoire.md](REFERENCE/specifications/memoire.md) - Spécifications mémoire

---

## 🏛️ ADRs Legacy (adr/)

*Note: Les ADRs ont été déplacés vers REFERENCE/adr/. Ces liens sont conservés pour la compatibilité.*

- [001-sqlite-choice.md](adr/001-sqlite-choice.md)
- [002-ia-architecture.md](adr/002-ia-architecture.md)

---

## 📦 Archive (archive/)

Documentation historique, obsolète mais conservée pour référence.

- [README.md](archive/README.md) - Vue d'ensemble de l'archive
- [2024-H2/](archive/2024-H2/) - Documents de la seconde moitié 2024
- [2025-Q1/](archive/2025-Q1/) - Documents du premier trimestre 2025
- [audits/](archive/audits/) - Rapports d'audit historiques
- [guides/](archive/guides/) - Anciens guides utilisateur
- [plans/](archive/plans/) - Anciens plans et roadmaps

---

## 🔗 Liens Rapides

### Documents Racine
- [README.md](README.md) - Guide principal de la documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture (résumé)
- [USER_GUIDE.md](USER_GUIDE.md) - Guide utilisateur (résumé)

### Projet
- [../README.md](../README.md) - README principal du projet
- [../AGENTS.md](../AGENTS.md) - Guide pour les agents AI
- [../CHANGELOG.md](../CHANGELOG.md) - Historique des versions
- [../CONTRIBUTING.md](../CONTRIBUTING.md) - Guide de contribution

---

## 📝 Convention de Nommage

| Préfixe | Signification | Exemple |
|---------|---------------|---------|
| `01-`, `02-`... | Ordre séquentiel | `01-vision.md` |
| `README.md` | Point d'entrée d'un dossier | `PLANNING/fusion/README.md` |
| `INDEX.md` | Index de navigation | Ce fichier |
| `ADR-XXX` | Architecture Decision Record | `001-sqlite-choice.md` |

---

## 🔄 Maintenance

Cet index est maintenu par la Phase 5 de la migration de documentation.
Dernière mise à jour: 2026-03-03

Pour ajouter une entrée:
1. Créer le fichier dans le dossier approprié
2. Mettre à jour l'INDEX.md correspondant
3. Mettre à jour ce fichier si c'est une section majeure
