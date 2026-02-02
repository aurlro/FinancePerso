"""
🔍 Explorateur - Exploration de catégories et tags avec filtres avancés.

Cette page permet d'explorer toutes les transactions d'une catégorie ou d'un tag,
avec des filtres avancés (période, montant, compte, etc.).

Navigation:
- Depuis n'importe quelle page, utiliser launch_explorer() ou render_explore_button()
- Les paramètres sont passés via URL : ?type=category&value=Alimentation&from=3_Synthese
"""
import streamlit as st
from modules.db.migrations import init_db
from modules.ui import load_css, render_scroll_to_top
from modules.ui.layout import render_app_info
from modules.ui.explorer import render_explorer_page

# Page config
st.set_page_config(
    page_title="Explorateur",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load styles
load_css()
init_db()

# Get parameters from URL
explorer_type = st.query_params.get('type', 'category')
explorer_value = st.query_params.get('value', '')
from_page = st.query_params.get('from', '3_Synthese')

# Validate parameters
if not explorer_value:
    st.warning("⚠️ Aucune catégorie ou tag spécifié.")
    st.info("""
    **Comment utiliser l'explorateur :**
    1. Depuis le **tableau de bord** ou la **synthèse**, cliquez sur 🔍 Explorer
    2. Ou accédez directement via : `/Explorer?type=category&value=Alimentation`
    """)
    
    # Show quick links to common categories
    st.subheader("📂 Catégories populaires")
    
    from modules.db.categories import get_categories
    categories = get_categories()[:6]  # First 6 categories
    
    cols = st.columns(3)
    for i, cat in enumerate(categories):
        with cols[i % 3]:
            if st.button(f"📂 {cat}", key=f"quick_cat_{i}", use_container_width=True):
                st.query_params['type'] = 'category'
                st.query_params['value'] = cat
                st.query_params['from'] = '6_Explorer'
                st.rerun()
    
    st.stop()

# Render the explorer page
render_explorer_page(
    explorer_type=explorer_type,
    explorer_value=explorer_value,
    from_page=from_page
)

render_scroll_to_top()
render_app_info()
