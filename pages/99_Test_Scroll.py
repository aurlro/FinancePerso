"""
Page de test pour le bouton Scroll-to-Top
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

st.set_page_config(
    page_title="Test Scroll",
    page_icon="⬆️",
    layout="wide",
)

from modules.ui.feedback import render_scroll_to_top

st.title("⬆️ Test Scroll-to-Top")
st.markdown("""
## Instructions :
1. **Défilez vers le bas** de cette page
2. Le bouton ⬆️ doit apparaître après avoir scrollé de 300px
3. **Cliquez sur le bouton** pour remonter en haut de la page
""")

st.divider()

# Créer beaucoup de contenu pour pouvoir scroller
for section in range(20):
    with st.expander(f"Section {section + 1}", expanded=True):
        st.write(f"Contenu de la section {section + 1}")
        for i in range(10):
            st.write(f"  - Ligne {i}: " + "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 3)

st.divider()
st.success("Si vous voyez ce message, vous êtes en bas de la page!")

# Bouton scroll to top
render_scroll_to_top()
