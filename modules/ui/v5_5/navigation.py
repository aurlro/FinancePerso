"""Navigation V5.6 - Sidebar style FinCouple.

Composant de navigation latérale avec logo et menu items.
"""

import streamlit as st

from modules.constants import APP_VERSION

# Menu items par défaut (peut être surchargé)
DEFAULT_MENU_ITEMS = [
    ("🏠", "Dashboard", "pages/02_Dashboard.py"),
    ("💳", "Transactions", "pages/01_Import.py"),
    ("📥", "Import", "pages/01_Import.py"),
    ("🏦", "Comptes", "pages/12_Patrimoine.py"),
    ("📋", "Règles", "pages/03_Intelligence.py"),
    ("📊", "Analytics", "pages/02_Dashboard.py"),
    ("📈", "Bilan mensuel", "pages/02_Dashboard.py"),
    ("⚖️", "Équilibre", "pages/04_Budgets.py"),
    ("🔄", "Abonnements", "pages/11_Abonnements.py"),
    ("⚙️", "Paramètres", "pages/08_Configuration.py"),
]


def render_sidebar_logo():
    """Rend le logo FinCouple dans la sidebar."""
    st.sidebar.markdown(
        """
        <div style="
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.5rem 0.75rem 1.5rem 0.5rem;
            margin-bottom: 0.5rem;
        ">
            <div style="
                width: 32px;
                height: 32px;
                background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: 700;
                font-size: 1.1rem;
            ">
                💰
            </div>
            <span style="
                font-size: 1.25rem;
                font-weight: 700;
                color: #0F172A;
                letter-spacing: -0.025em;
            ">
                FinCouple
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_nav_item(icon: str, label: str, page: str, is_active: bool = False):
    """Rend un item de navigation."""
    # Utiliser st.button avec style custom
    if st.sidebar.button(
        f"{icon} {label}",
        key=f"nav_{label}",
        use_container_width=True,
        type="secondary" if not is_active else "primary"
    ):
        st.switch_page(page)


def render_navigation_menu(current_page: str = None):
    """Rend le menu de navigation complet."""
    # Déterminer la page active
    if current_page is None:
        # Essayer de détecter la page courante
        try:
            current_page = st.query_params.get("page", [""])[0]
        except Exception:
            current_page = ""
    
    # Rendre chaque item
    for icon, label, page in DEFAULT_MENU_ITEMS:
        is_active = current_page in page or page in st.session_state.get("current_page", "")
        render_nav_item(icon, label, page, is_active)


def render_user_section():
    """Rend la section utilisateur en bas de sidebar."""
    st.sidebar.markdown("---")
    
    # Info utilisateur
    col1, col2 = st.sidebar.columns([3, 1])
    
    with col1:
        st.markdown(
            """
            <div style="
                color: #64748B;
                font-size: 0.75rem;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            ">
                demo@financeperso.app
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            """
            <div style="
                display: flex;
                gap: 0.5rem;
                justify-content: flex-end;
            ">
                <span style="cursor: pointer;">🔔</span>
                <span style="cursor: pointer;">↗️</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Version
    st.sidebar.markdown(
        f"""
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 0.5rem;
            color: #94A3B8;
            font-size: 0.75rem;
        ">
            <span>v{APP_VERSION}</span>
            <span style="cursor: pointer;">⚙️</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_finouple_sidebar(current_page: str = None):
    """Rend la sidebar complète style FinCouple.
    
    Usage:
        from modules.ui.v5_5.navigation import render_finouple_sidebar
        
        render_finouple_sidebar("Dashboard")
    """
    with st.sidebar:
        render_sidebar_logo()
        render_navigation_menu(current_page)
        render_user_section()


def render_page_header(title: str, actions: list = None):
    """Rend l'en-tête de page style FinCouple.
    
    Args:
        title: Titre de la page
        actions: Liste de tuples (label, callback) pour les boutons d'action
    """
    cols = st.columns([6, 4])
    
    with cols[0]:
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1.5rem;
        ">
            <span style="
                color: #64748B;
                font-size: 1.25rem;
            ">📄</span>
            <h1 style="
                font-size: 1.25rem;
                font-weight: 600;
                color: #0F172A;
                margin: 0;
            ">{title}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        if actions:
            cols_actions = st.columns(len(actions))
            for i, (label, callback, button_type) in enumerate(actions):
                with cols_actions[i]:
                    if st.button(label, type=button_type, use_container_width=True):
                        callback()


def render_content_card(title: str, content_func):
    """Rend une card de contenu style FinCouple.
    
    Usage:
        def my_content():
            st.write("Contenu ici")
        
        render_content_card("Titre", my_content)
    """
    with st.container():
        # Header de la card
        st.markdown(f"""
        <div style="
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        ">
            <h2 style="
                font-size: 1rem;
                font-weight: 600;
                color: #0F172A;
                margin: 0 0 1.5rem 0;
            ">{title}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Contenu
        content_func()


def render_tabs(tabs: list, default_index: int = 0):
    """Rend des onglets style FinCouple (pills).
    
    Args:
        tabs: Liste de tuples (id, label)
        default_index: Index de l'onglet actif par défaut
    
    Returns:
        L'ID de l'onglet sélectionné
    """
    # Créer les colonnes pour les tabs
    tab_cols = st.columns(len(tabs))
    
    # Initialiser l'état si nécessaire
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = tabs[default_index][0]
    
    # Rendre chaque tab
    for i, (tab_id, tab_label) in enumerate(tabs):
        with tab_cols[i]:
            if st.button(
                tab_label,
                key=f"tab_{tab_id}",
                use_container_width=True
            ):
                st.session_state.active_tab = tab_id
                st.rerun()
    
    return st.session_state.active_tab
