import streamlit as st
from modules.ui import load_css
from modules.ui.layout import render_app_info

st.set_page_config(page_title="Nouveautés", page_icon="🎁", layout="wide")
load_css()

st.title("🎁 Nouveautés & Mises à jour")

# Layout timeline
st.markdown("### Historique des versions")

with st.container(border=True):
    col_ver, col_date = st.columns([1, 4])
    with col_ver:
        st.markdown("### `v0.2.0`")
        st.caption("27 Janvier 2026")
        st.caption("✨ Validation & UX")
    with col_date:
        st.markdown("""
        **Améliorations Majeures :**
        - **Validation Intelligente** : Nouvelle interface de validation par "piles" (Pills) pour les tags suggérés.
        - **Sélection Unique** : Correction du bug de duplication des boutons dans la liste de validation.
        - **Configuration** : Correction des crashs liés aux DataFrames vides dans la gestion des règles.
        
        **Autres :**
        - Ajout de cette page de suivi des mises à jour.
        - Affichage de la version en bas de la barre latérale.
        """)

st.divider()

render_app_info()
