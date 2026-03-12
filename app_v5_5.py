"""FinancePerso V5.5 - Nouvelle interface maquette FinCouple.

Point d'entrée principal avec:
- Thème light mode
- Welcome screen pour nouveaux utilisateurs
- Dashboard pour utilisateurs avec données
- Navigation fluide entre les vues

Usage:
    streamlit run app_v5_5.py

Ou via feature flag dans app.py:
    USE_V5_6_INTERFACE = True
"""

import streamlit as st

# Configuration de la page (DOIT être la première commande Streamlit)
st.set_page_config(
    page_title="FinancePerso",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "FinancePerso V5.5 - Gestion financière personnelle"
    }
)

# Imports
from modules.ui.feedback import toast_success
from modules.ui.v5_5 import (
    apply_light_theme,
    get_user_name,
    render_welcome_or_dashboard,
)


def render_sidebar():
    """Rend la sidebar de navigation."""
    
    with st.sidebar:
        # Logo et titre
        st.markdown("""
        <div style="
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 1rem 0;
            margin-bottom: 1rem;
            border-bottom: 1px solid #E5E7EB;
        ">
            <span style="font-size: 1.5rem;">💰</span>
            <span style="
                font-size: 1.25rem;
                font-weight: 700;
                color: #1F2937;
            ">FinancePerso</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation principale
        st.markdown("### Navigation")
        
        nav_items = [
            ("🏠", "Dashboard", "app_v5_5.py"),
            ("💳", "Opérations", "pages/1_Opérations.py"),
            ("📊", "Synthèse", "pages/3_Synthèse.py"),
            ("🧠", "Intelligence", "pages/4_Intelligence.py"),
            ("💰", "Budgets", "pages/5_Budgets.py"),
            ("🎯", "Objectifs", "pages/6_Objectifs.py"),
            ("⚙️", "Configuration", "pages/9_Configuration.py"),
        ]
        
        for icon, label, page in nav_items:
            if st.button(
                f"{icon} {label}",
                key=f"nav_{label.lower()}",
                use_container_width=True,
                type="secondary" if label != "Dashboard" else "primary"
            ):
                if label == "Dashboard":
                    st.rerun()
                else:
                    st.switch_page(page)
        
        # Footer
        st.divider()
        st.markdown("""
        <div style="
            font-size: 0.75rem;
            color: #9CA3AF;
            text-align: center;
        ">
            FinancePerso V5.5<br>
            Interface moderne
        </div>
        """, unsafe_allow_html=True)


def check_first_visit():
    """Vérifie si c'est la première visite et affiche un toast de bienvenue."""
    if "first_visit_v55" not in st.session_state:
        st.session_state.first_visit_v55 = True
        toast_success("✨ Bienvenue sur la nouvelle interface FinancePerso V5.5 !")


def main():
    """Fonction principale de l'application V5.5."""
    
    # 1. Appliquer le thème light mode
    apply_light_theme()
    
    # 2. Vérifier première visite
    check_first_visit()
    
    # 3. Rendre la sidebar
    render_sidebar()
    
    # 4. Afficher welcome ou dashboard selon les données
    user_name = get_user_name()
    render_welcome_or_dashboard(user_name=user_name)


if __name__ == "__main__":
    main()
