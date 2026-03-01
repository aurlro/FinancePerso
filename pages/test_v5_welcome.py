"""
Page de test pour le Welcome Component V5.5

Usage:
    streamlit run pages/test_v5_welcome.py
"""

import streamlit as st
from modules.ui.v5_5 import apply_light_theme
from modules.ui.v5_5.components import WelcomeCard

# Configuration
st.set_page_config(
    page_title="Test Welcome V5.5",
    page_icon="👋",
    layout="wide",
)

# Appliquer le thème
apply_light_theme()

st.sidebar.title("🔧 Configuration")
user_name = st.sidebar.text_input("Nom d'utilisateur", value="Alex")
show_secondary = st.sidebar.checkbox("Afficher bouton secondaire", value=True)

st.sidebar.divider()
st.sidebar.caption("FinancePerso V5.5")

# Main content
st.title("👋 Test Welcome Card V5.5")

st.markdown("""
Cette page teste le composant **WelcomeCard** qui s'affiche quand l'utilisateur 
n'a pas encore de transactions.

**Features:**
- Card centrée avec ombre
- Icône 💰 dans cercle vert
- Titre "Bonjour [Nom] !"
- Description
- Boutons primaire et secondaire
""")

st.divider()

# Afficher la card
if show_secondary:
    WelcomeCard.render(
        user_name=user_name if user_name else None,
        on_primary=lambda: st.success("🚀 Clic sur 'Importer' !"),
        on_secondary=lambda: st.info("📖 Clic sur 'Guide' !"),
    )
else:
    WelcomeCard.render(
        user_name=user_name if user_name else None,
        on_primary=lambda: st.success("🚀 Clic sur 'Importer' !"),
        primary_text="▶️ Commencer",
    )

st.divider()

# Variantes
st.header("🎨 Variantes")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Sans nom")
    WelcomeCard.render(
        on_primary=lambda: None,
        on_secondary=lambda: None,
        key_prefix="variant_no_name",
    )

with col2:
    st.subheader("Avec nom personnalisé")
    WelcomeCard.render(
        user_name="Marie",
        on_primary=lambda: None,
        on_secondary=lambda: None,
        key_prefix="variant_name",
    )

st.divider()
st.caption("FinancePerso V5.5 - Welcome Component")
