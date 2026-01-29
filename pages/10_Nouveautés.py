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
        st.markdown("### `v2.3.0`")
        st.caption("29 Janvier 2026")
        st.caption("🧠 AI & Intelligence")
    with col_date:
        st.markdown("""
        **Intelligence Artificielle & Audit :**
        - **Assistant Conversationnel** : Dialogue intelligent capable de lancer des outils d'analyse et de correction.
        - **Audit de Qualité** : Analyseur de règles IA pour détecter conflits et doublons.
        - **Anomalies Persistantes** : Possibilité de marquer des montants comme normaux (mémorisation durable par tag).
        
        **Analyses & UX :**
        - **Drill-down Interactif** : Exploration et modification en masse des transactions directement depuis les tendances.
        - **Apprentissage Actif** : Création automatique de règles de catégorisation à partir de vos corrections.
        - **Virements Internes** : Détection automatique et option d'exclusion pour des analyses plus précises.
        
        **Stabilité :**
        - Suite de tests étendue (tests AI) et correction d'encodage UTF-8.
        """)

st.markdown("---")

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
