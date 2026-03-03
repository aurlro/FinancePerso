# Référence Technique - FinancePerso

> Documentation technique stable et validée

---

## 📂 Contenu de ce Dossier

Ce dossier contient la documentation de référence technique:
- Architecture Decision Records (ADRs)
- Documentation d'architecture
- Personas utilisateurs
- Spécifications techniques

Ces documents sont **stables** et **validés**. Ils ne changent que lors de décisions architecturales majeures.

---

## 📁 Sous-dossiers

### [adr/](adr/) - Architecture Decision Records
Enregistrement des décisions d'architecture significatives.

| Fichier | Description | Statut |
|---------|-------------|--------|
| [001-sqlite-choice.md](adr/001-sqlite-choice.md) | Choix de SQLite comme base de données | ✅ Accepté |
| [002-ia-architecture.md](adr/002-ia-architecture.md) | Architecture du système IA | ✅ Accepté |

Format des ADRs:
```
001-titre-decision.md
```

Structure standard:
- Contexte
- Décision
- Conséquences
- Alternatives considérées

### [architecture/](architecture/) - Documentation d'Architecture
Documentation sur l'architecture du système.

| Fichier | Description |
|---------|-------------|
| [v6-target.md](architecture/v6-target.md) | Architecture cible V6 |

### [personas/](personas/) - Personas Utilisateurs
Profils des utilisateurs cibles.

| Fichier | Description |
|---------|-------------|
| [personas-et-parcours.md](personas/personas-et-parcours.md) | Personas et parcours utilisateurs |

### [specifications/](specifications/) - Spécifications Techniques
Spécifications détaillées du système.

| Fichier | Description |
|---------|-------------|
| [memoire.md](specifications/memoire.md) | Spécifications mémoire |

---

## 🏛️ Processus ADR

### Quand créer un ADR ?
- Changement de technologie majeur
- Modification d'architecture
- Choix impactant la scalabilité
- Décision difficilement réversible

### Format
```markdown
# ADR-XXX: Titre de la décision

## Statut
- Proposé / Accepté / Déprécié / Supplanté par ADR-YYY

## Contexte
Description du problème et contraintes.

## Décision
Description de la décision prise.

## Conséquences
- Positives: ...
- Négatives: ...

## Alternatives
Autres options considérées et pourquoi rejetées.
```

---

## 🔗 Liens

- [../adr/](../adr/) - ADRs legacy (redirection)
- [../../AGENTS.md](../../AGENTS.md) - Guide agents AI
- [../../ARCHITECTURE.md](../../ARCHITECTURE.md) - Architecture (racine)

---

[Voir l'index global](../INDEX.md) | [Retour à l'accueil docs](../README.md)
