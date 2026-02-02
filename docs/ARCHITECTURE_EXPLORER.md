# Architecture - Explorateur de Catégories & Tags

## 🎯 Objectif
Permettre à l'utilisateur d'explorer toutes les transactions d'une catégorie ou d'un tag, avec des filtres avancés, depuis n'importe quel endroit de l'application.

## 🏗️ Architecture Technique

### 1. Composants Principaux

```
modules/ui/explorer/
├── __init__.py                    # Export des composants publics
├── explorer_main.py               # Vue principale d'exploration
├── explorer_filters.py            # Filtres avancés (période, montant, etc.)
├── explorer_results.py            # Affichage des résultats
└── explorer_launcher.py           # Boutons de lancement depuis autres pages
```

### 2. Navigation (Query Params)

```python
# Depuis n'importe quelle page, on navigue vers l'explorateur avec:
st.switch_page("pages/6_Explorer.py")
st.query_params['type'] = 'category'  # ou 'tag'
st.query_params['value'] = 'Alimentation'  # nom de la catégorie/tag
st.query_params['from'] = 'dashboard'  # page d'origine (pour retour)
```

### 3. Filtres Disponibles

| Filtre | Type | Description |
|--------|------|-------------|
| **Période** | Date range | Du / Au |
| **Montant** | Range | Min / Max |
| **Type** | Select | Tous / Dépenses / Revenus |
| **Compte** | Multi-select | Comptes bancaires |
| **Membre** | Multi-select | Membres du foyer |
| **Statut** | Multi-select | Validé / En attente |
| **Tags** | Multi-select | Tags associés |

### 4. Intégrations dans l'App Existante

#### A. Tableau de Bord (KPI Cards)
```python
# Sur chaque carte catégorie, ajouter:
if st.button("🔍 Explorer", key=f"explore_{category}"):
    launch_explorer('category', category, from_page='dashboard')
```

#### B. Graphiques (Click Handler)
```python
# Utilisation de st.plotly_chart avec click events
# ou boutons sous chaque section du graphique
```

#### C. Page Validation
```python
# Dans les expanders de catégories:
st.link_button("📊 Voir toutes les transactions", 
               f"/Explorer?type=category&value={category}")
```

#### D. Page Synthèse
```python
# Dans les listes de top catégories:
for cat in top_categories:
    cols = st.columns([3, 1, 1])
    cols[0].write(cat['name'])
    cols[1].write(f"{cat['amount']:.2f} €")
    cols[2].button("🔍", key=f"explore_{cat['name']}", 
                   on_click=launch_explorer, 
                   args=('category', cat['name']))
```

### 5. Structure de la Page Explorer

```
┌─────────────────────────────────────────────────────────────────┐
│  🔍 Explorateur                                    [⬅️ Retour]  │
│  Transactions : Alimentation (Catégorie)                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  🎛️ FILTRES                                            │   │
│  │  ┌──────────┬──────────┬──────────┬──────────┐         │   │
│  │  │ 📅 Du    │ 📅 Au    │ 💰 Min   │ 💰 Max   │         │   │
│  │  └──────────┴──────────┴──────────┴──────────┘         │   │
│  │  ┌──────────┬──────────┬──────────┬──────────┐         │   │
│  │  │ 🏦 Comptes│ 👤 Membres│ 🏷️ Tags   │ 📊 Statut│         │   │
│  │  └──────────┴──────────┴──────────┴──────────┘         │   │
│  │            [🔄 Réinitialiser]  [✅ Appliquer]           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  📊 RÉSULTATS (47 transactions - Total: 1,234.56 €)    │   │
│  │  ┌──────────┬──────────┬──────────┬──────────┐         │   │
│  │  │ Date     │ Libellé  │ Montant  │ Compte   │         │   │
│  │  ├──────────┼──────────┼──────────┼──────────┤         │   │
│  │  │ 15/01    │ CARREFOUR│ -45.20   │ Bourso   │         │   │
│  │  │ 12/01    │ LIDL     │ -23.50   │ Bourso   │         │   │
│  │  └──────────┴──────────┴──────────┴──────────┘         │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 📱 Implémentation Technique

### A. Nouvelle Page : `pages/6_Explorer.py`

```python
import streamlit as st
from modules.ui.explorer.explorer_main import render_explorer_page

st.set_page_config(page_title="Explorateur", page_icon="🔍", layout="wide")

# Récupérer les paramètres d'URL
explorer_type = st.query_params.get('type', 'category')  # 'category' ou 'tag'
explorer_value = st.query_params.get('value', '')
from_page = st.query_params.get('from', 'dashboard')

render_explorer_page(
    explorer_type=explorer_type,
    explorer_value=explorer_value,
    from_page=from_page
)
```

### B. Composant Principal : `explorer_main.py`

```python
def render_explorer_page(explorer_type: str, explorer_value: str, from_page: str):
    # Header avec bouton retour
    col1, col2 = st.columns([6, 1])
    with col1:
        icon = "📂" if explorer_type == 'category' else "🏷️"
        st.title(f"{icon} Explorateur : {explorer_value}")
    with col2:
        if st.button("⬅️ Retour"):
            st.switch_page(f"pages/{from_page}.py")
    
    # Charger les données
    df = load_data_for_explorer(explorer_type, explorer_value)
    
    # Filtres
    filtered_df = render_explorer_filters(df)
    
    # Résultats
    render_explorer_results(filtered_df, explorer_type, explorer_value)
```

### C. Système de Filtres : `explorer_filters.py`

```python
@st.fragment  # Pour éviter les reruns complets
def render_explorer_filters(df: pd.DataFrame) -> pd.DataFrame:
    with st.container(border=True):
        st.subheader("🎛️ Filtres")
        
        # Row 1: Date & Amount
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            start_date = st.date_input("📅 Du", value=df['date'].min())
        with col2:
            end_date = st.date_input("📅 Au", value=df['date'].max())
        with col3:
            min_amount = st.number_input("💰 Min (€)", value=0.0)
        with col4:
            max_amount = st.number_input("💰 Max (€)", value=float(df['amount'].max()))
        
        # Row 2: Type, Accounts, Members
        col5, col6, col7 = st.columns(3)
        with col5:
            tx_type = st.selectbox("Type", ["Tous", "Dépenses", "Revenus"])
        with col6:
            accounts = st.multiselect("🏦 Comptes", df['account'].unique())
        with col7:
            members = st.multiselect("👤 Membres", df['member'].unique())
        
        # Apply filters
        mask = (
            (df['date'] >= start_date) &
            (df['date'] <= end_date) &
            (df['amount'] >= min_amount) &
            (df['amount'] <= max_amount)
        )
        
        if tx_type == "Dépenses":
            mask &= df['amount'] < 0
        elif tx_type == "Revenus":
            mask &= df['amount'] > 0
        
        if accounts:
            mask &= df['account'].isin(accounts)
        if members:
            mask &= df['member'].isin(members)
        
        return df[mask]
```

### D. Composant de Lancement : `explorer_launcher.py`

```python
def launch_explorer(explorer_type: str, value: str, from_page: str = '3_Synthese'):
    """Launch explorer with given parameters."""
    st.query_params['type'] = explorer_type
    st.query_params['value'] = value
    st.query_params['from'] = from_page
    st.switch_page("pages/6_Explorer.py")

def render_explore_button(
    explorer_type: str, 
    value: str, 
    from_page: str = '3_Synthese',
    **button_kwargs
):
    """Render a button that launches the explorer."""
    icon = "📂" if explorer_type == 'category' else "🏷️"
    label = button_kwargs.pop('label', f"{icon} Explorer")
    
    if st.button(label, key=f"explore_{explorer_type}_{value}", **button_kwargs):
        launch_explorer(explorer_type, value, from_page)
```

## 🔄 Modifications des Pages Existantes

### 1. `pages/3_Synthese.py`
```python
from modules.ui.explorer.explorer_launcher import render_explore_button

# Dans la section catégories:
for category in top_categories:
    col1, col2, col3 = st.columns([2, 1, 0.5])
    col1.write(category['name'])
    col2.write(f"{category['amount']:.2f} €")
    with col3:
        render_explore_button('category', category['name'], from_page='3_Synthese')
```

### 2. `pages/2_Validation.py`
```python
# Dans chaque carte de catégorie:
with st.container():
    st.subheader(f"📂 {category_name}")
    render_explore_button('category', category_name, from_page='2_Validation', 
                         label="📊 Voir tout", use_container_width=True)
```

### 3. `pages/5_Assistant.py`
```python
# Dans les insights de tendances:
if st.button(f"🔍 Explorer {insight['category']}"):
    launch_explorer('category', insight['category'], from_page='5_Assistant')
```

## 📊 Avantages de cette Architecture

1. **✅ Réutilisable** : Un seul composant pour toute l'app
2. **✅ URL Shareable** : Les filtres sont dans l'URL (bookmarkable)
3. **✅ Performant** : Utilisation de `@st.fragment` pour les filtres
4. **✅ Intuitif** : Navigation naturelle depuis n'importe où
5. **✅ Extensible** : Facile d'ajouter de nouveaux filtres

## 🎯 Prochaines Étapes d'Implémentation

1. Créer la structure `modules/ui/explorer/`
2. Implémenter `explorer_filters.py` (filtres avancés)
3. Implémenter `explorer_results.py` (tableau + stats)
4. Créer la page `pages/6_Explorer.py`
5. Ajouter les boutons dans les pages existantes

---

Tu valides cette architecture ? Je peux commencer l'implémentation si tu es OK.
