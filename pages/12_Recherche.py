"""
Page de recherche globale pour FinancePerso.
Recherche avancée dans les transactions, catégories et membres.
"""

import streamlit as st
from modules.ui import load_css
from modules.ui.global_search import render_global_search_full

st.set_page_config(
    page_title="Recherche",
    page_icon="🔍",
    layout="wide"
)

load_css()

# Rendre la recherche complète
render_global_search_full()
