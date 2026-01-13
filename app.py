import streamlit as st

# Config de la page doit être la première commande Streamlit
st.set_page_config(
    page_title="MyFinance Companion",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

from modules.ui import load_css

load_css()

st.title("Bienvenue sur MyFinance Companion")

st.markdown("""
### Votre assistant personnel de finances
Cette application vous aide à transformer vos relevés bancaires en insights clairs.

#### Commencez par :
1. **Importer** vos relevés dans l'onglet **Import**.
2. **Valider** les catégorisations proposées par l'IA dans l'onglet **Validation**.
3. **Explorer** vos dépenses dans l'onglet **Synthèse**.

*Les données restent locales sur votre machine.*
""")

# Sidebar
st.sidebar.title("Navigation")
st.sidebar.info("v0.1 - MVP")
