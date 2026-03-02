# Module `modules/ui`

> Composants d'interface utilisateur pour Streamlit.

## Vue d'ensemble

Ce module fournit des composants UI réutilisables pour construire l'interface Streamlit de FinancePerso.

## Architecture

```
modules/ui/
├── __init__.py              # Exports et utilitaires
├── theme.py                 # Gestion du thème
├── feedback.py              # Messages et toasts
├── layout.py                # Layouts de page
├── accessibility.py         # Accessibilité (WCAG)
├── components/              # Composants atomiques
│   ├── empty_states.py     # États vides
│   ├── loading_states.py   # États de chargement
│   ├── daily_widget.py     # Widget quotidien
│   └── ...
├── dashboard/               # Widgets dashboard
├── molecules/               # Composants moléculaires
├── notifications/           # UI notifications V3
└── assistant/               # UI Assistant IA
```

## Utilisation

### Composants basiques

```python
from modules.ui import toast_success, show_error

toast_success("Opération réussie!")
show_error("Titre", "Message d'erreur")
```

### Thème

```python
from modules.ui.theme import init_theme, ThemeManager

init_theme()  # Initialise le thème clair/sombre
```

### Empty States

```python
from modules.ui.components.empty_states import render_no_data_state

render_no_data_state(
    icon="📊",
    title="Aucune donnée",
    message="Importez des transactions pour commencer"
)
```

## Design System

### Couleurs

- **Primaire**: `#10B981` (Emerald)
- **Succès**: `#10B981`
- **Warning**: `#F59E0B`
- **Erreur**: `#EF4444`
- **Info**: `#3B82F6`

### Typographie

- Titres: `Inter`, `sans-serif`
- Corps: Système par défaut

## Bonnes pratiques

1. **Isoler le CSS** dans des fonctions dédiées
2. **Utiliser les composants** plutôt que du HTML inline
3. **Respecter l'accessibilité** - aria-labels, contrastes
