# Guide du Design System FinancePerso

> Ce guide explique comment utiliser le nouveau Design System pour créer des interfaces cohérentes.

---

## 📁 Structure Atomic Design

```
modules/ui/
├── tokens/          # 🔵 Design Tokens (source de vérité)
│   ├── colors.py    # Palette de couleurs
│   ├── typography.py # Typographie
│   ├── spacing.py   # Espacements
│   └── radius.py    # Border-radius & ombres
├── atoms/           # ⚛️ Éléments de base
│   ├── button.py    # Boutons standardisés
│   ├── badge.py     # Badges
│   └── icon.py      # Icônes
├── molecules/       # 🧪 Compositions simples
│   ├── card.py      # Carte unifiée
│   ├── empty_state.py # États vides
│   └── metric.py    # Métriques
├── organisms/       # 🦠 Sections complexes
├── templates/       # 📐 Layouts de pages
└── feedback_v2.py   # Système de feedback modernisé
```

---

## 🎨 Design Tokens

### Couleurs

```python
from modules.ui.tokens import Colors, ColorPalette, SemanticColors

# Couleurs directes
primary = Colors.PRIMARY          # "#0F172A"
success = Colors.SUCCESS          # "#10B981"
danger = Colors.DANGER            # "#EF4444"

# Palette complète
palette = ColorPalette()
bg_color = palette.bg_primary

# Couleurs sémantiques
semantic = SemanticColors()
text_color, bg_color, border_color = semantic.danger
```

### Typographie

```python
from modules.ui.tokens import Typography, get_text_style

# Tailles
font_size = Typography.SIZE_LG    # "1.125rem"
font_weight = Typography.WEIGHT_BOLD  # "700"

# Styles prédéfinis
h2_style = get_text_style("h2")
# -> {"font_size": "1.5rem", "font_weight": "600", "line_height": "1.25"}
```

### Espacements

```python
from modules.ui.tokens import Spacing, LayoutSpacing

# Espacements de base
padding = Spacing.MD              # "1rem"
margin = Spacing.LG               # "1.5rem"

# Espacements de layout
section_gap = LayoutSpacing.SECTION  # "3rem"
component_gap = LayoutSpacing.COMPONENT  # "1.5rem"
```

---

## ⚛️ Atomes

### Button

```python
from modules.ui.atoms import Button

# Bouton primaire
if Button.primary("Sauvegarder", key="save"):
    save_data()

# Bouton secondaire
if Button.secondary("Annuler", key="cancel"):
    go_back()

# Bouton danger avec confirmation
if Button.danger("Supprimer", key="delete", confirm=True):
    delete_item()

# Bouton avec icône
Button.primary("Importer", icon="📥", key="import")
```

### Badge

```python
from modules.ui.atoms import Badge

# Badges simples
Badge.success("Validé")
Badge.warning("En attente")
Badge.danger("Erreur", count=3)

# Badge de statut
Badge.status("active")    # Vert "Actif"
Badge.status("pending")   # Orange "En attente"
Badge.status("error")     # Rouge "Erreur"

# Badge avec compteur
Badge.info("Messages", count=5)
```

### Icon

```python
from modules.ui.atoms import Icon

# Icônes de statut
Icon.success()    # "✓"
Icon.error()      # "✕"
Icon.warning()    # "⚠"

# Icônes par catégorie
Icon.for_category("alimentation")  # "🍽️"
Icon.for_category("transport")     # "🚗"

# Icônes par sévérité
Icon.for_severity("high")    # "🔴"
Icon.for_severity("medium")  # "🟠"
```

---

## 🧪 Molécules

### Card (La plus importante!)

Remplace **toutes** les anciennes fonctions de cartes.

```python
from modules.ui.molecules import Card

# Carte simple
Card.render(
    title="Titre",
    content="Contenu de la carte",
    icon="💰"
)

# Carte métrique (KPI)
Card.metric(
    title="Dépenses",
    value="1 234 €",
    trend="+12%",
    trend_up=False,
    icon="💸"
)

# Carte action
Card.action(
    title="Importer",
    description="Importez vos transactions",
    button_text="Importer",
    on_click=import_handler,
    icon="📥"
)

# Carte d'alerte
Card.alert(
    title="Attention",
    message="Votre budget est dépassé",
    severity="warning",
    action_text="Voir",
    on_action=show_budget
)

# État vide
Card.empty(
    title="Aucune transaction",
    message="Commencez par importer vos données",
    icon="📄",
    action_text="Importer",
    on_action=import_handler
)
```

### EmptyState

```python
from modules.ui.molecules import EmptyState

# État vide générique
EmptyState.render(
    title="Aucune donnée",
    message="Il n'y a rien à afficher pour l'instant.",
    icon="📭",
    action_text="Créer",
    on_action=create_handler
)

# États vides prédéfinis
EmptyState.no_transactions(on_import=import_handler)
EmptyState.no_budgets(on_create=create_budget)
EmptyState.no_search_results(search_term="restaurant", on_clear=clear_search)
```

### Metric

```python
from modules.ui.molecules import Metric, MetricTrend

# Métrique simple
Metric.render(
    label="Dépenses",
    value="1 234 €",
    trend=MetricTrend.down("-5%"),
    icon="💸"
)

# Métrique avec comparaison
Metric.comparison(
    label="Revenus",
    current_value="3 000 €",
    previous_value="2 800 €"
)

# Version mini (pour tableaux)
Metric.mini("Total", "123", "+5", trend_positive=True)
```

---

## 📐 Templates

### PageLayout

```python
from modules.ui.templates import PageLayout

def render_content():
    st.write("Contenu de la page")
    Card.metric("Total", "1000 €")

PageLayout.render(
    title="Ma Page",
    subtitle="Description de la page",
    icon="📊",
    content=render_content,
    actions=[
        {"label": "Sauver", "on_click": save, "variant": "primary"},
        {"label": "Annuler", "on_click": cancel, "variant": "secondary"},
    ]
)
```

---

## 🔔 Feedback (V2)

```python
from modules.ui.feedback_v2 import Feedback, Toast, Banner

# Toasts éphémères
Feedback.toast.success("Sauvegardé !")
Feedback.toast.error("Erreur de connexion")
Feedback.toast.warning("Vérifier les données")
Feedback.toast.info("Nouvelle version disponible")

# Banners persistants
Feedback.banner.success("Succès", "Opération réussie")
Feedback.banner.error("Erreur", "Une erreur s'est produite")
Feedback.banner.warning("Attention", "Budget dépassé", action_text="Voir", on_action=show_budget)

# Confirmations
if Feedback.confirm("Supprimer cette transaction ?"):
    delete_transaction()

# Confirmation dangereuse
if Feedback.confirm.danger.render("Supprimer définitivement ?"):
    delete_permanent()
```

---

## 🔄 Migration depuis l'ancien code

### Avant (Ancien code)

```python
# Avant: Couleurs hardcodées
st.markdown(f"<div style='color: #22c55e;'>Succès</div>", unsafe_allow_html=True)

# Avant: Bouton avec style inline
if st.button("Valider", type="primary", use_container_width=True):
    save()

# Avant: Carte custom
st.markdown("""
<div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px;">
    <h3>💰 Total</h3>
    <p style="font-size: 24px; font-weight: bold;">1234 €</p>
</div>
""", unsafe_allow_html=True)
```

### Après (Nouveau code)

```python
from modules.ui.tokens import Colors, Typography, Spacing, BorderRadius
from modules.ui.atoms import Button
from modules.ui.molecules import Card

# Après: Couleurs via tokens
st.markdown(f"<div style='color: {Colors.SUCCESS};'>Succès</div>", unsafe_allow_html=True)

# Après: Bouton atomique
Button.primary("Valider", on_click=save)

# Après: Carte unifiée
Card.metric(
    title="Total",
    value="1 234 €",
    icon="💰"
)
```

---

## ✅ Checklist de développement

Avant de soumettre du code UI, vérifier :

- [ ] Aucune couleur hardcodée (utiliser `Colors`)
- [ ] Aucune taille de police hardcodée (utiliser `Typography`)
- [ ] Aucun espacement hardcodée (utiliser `Spacing`)
- [ ] Boutons via `Button` (pas `st.button` directement)
- [ ] Cartes via `Card` (pas HTML custom)
- [ ] Badges via `Badge` (pas HTML custom)
- [ ] États vides via `EmptyState`
- [ ] Feedback via `Feedback` V2

---

## 🎯 Exemple complet

```python
import streamlit as st
from modules.ui.tokens import Colors, Typography, Spacing
from modules.ui.atoms import Button, Badge, Icon
from modules.ui.molecules import Card, EmptyState, Metric
from modules.ui.templates import PageLayout
from modules.ui.feedback_v2 import Feedback

def render_page():
    """Page d'exemple utilisant le Design System."""
    
    # Header
    PageLayout.render(
        title="Dashboard",
        subtitle="Vue d'ensemble de vos finances",
        icon=Icon.CHART,
        content=render_dashboard,
        actions=[
            {"label": "Importer", "on_click": import_data, "variant": "primary"},
        ]
    )

def render_dashboard():
    # Métriques
    col1, col2, col3 = st.columns(3)
    with col1:
        Card.metric(
            title="Solde",
            value="5 000 €",
            trend=MetricTrend.up("+2%"),
            icon=Icon.WALLET
        )
    with col2:
        Card.metric(
            title="Dépenses",
            value="1 234 €",
            trend=MetricTrend.down("-5%"),
            icon=Icon.MONEY
        )
    with col3:
        Card.metric(
            title="Budget restant",
            value="766 €",
            trend=MetricTrend.neutral("stable"),
            icon=Icon.PIGGY_BANK
        )
    
    # Alertes
    Card.alert(
        title="Budget Alimentation",
        message="Vous avez dépensé 85% de votre budget",
        severity="warning",
        action_text="Voir détails",
        on_action=show_budget
    )
    
    # Liste vide
    if not has_transactions():
        EmptyState.no_transactions(on_import=import_data)
    else:
        # Tableau
        for tx in get_transactions():
            render_transaction_row(tx)

def render_transaction_row(tx):
    """Rend une ligne de transaction."""
    with st.container():
        cols = st.columns([3, 2, 2, 1])
        with cols[0]:
            st.write(tx["label"])
        with cols[1]:
            Badge.status(tx["status"])
        with cols[2]:
            st.write(f"{tx['amount']} €")
        with cols[3]:
            Button.icon_button(Icon.EDIT, key=f"edit_{tx['id']}")

# Lancer la page
if __name__ == "__main__":
    render_page()
```

---

## 📚 Ressources

- **Tokens** : `modules/ui/tokens/`
- **Atomes** : `modules/ui/atoms/`
- **Molécules** : `modules/ui/molecules/`
- **Feedback V2** : `modules/ui/feedback_v2.py`

---

*Dernière mise à jour : 2026-02-27*
