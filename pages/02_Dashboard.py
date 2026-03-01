"""
Dashboard_Beta - Page de production V5.5 (nouvelle interface FinCouple).

Cette page est la version de production du dashboard V5.5 avec le design
FinCouple (light mode, épuré).

URL: http://localhost:8501/Dashboard_Beta

Usage:
    # Depuis la navigation ou directement:
    st.switch_page("pages/Dashboard_Beta.py")
"""

import streamlit as st

# =============================================================================
# VÉRIFICATION FEATURE FLAG
# =============================================================================
from modules.constants import TEST_DASHBOARD_ENABLED

if not TEST_DASHBOARD_ENABLED:
    st.set_page_config(page_title="Non disponible", page_icon="🚧")
    st.error("🚧 Cette fonctionnalité n'est pas encore activée.")
    st.info("Le dashboard V5.5 est en cours de développement.")
    st.stop()

# =============================================================================
# IMPORTS
# =============================================================================
from modules.db.migrations import init_db
from modules.logger import logger
from modules.notifications import NotificationService
from modules.notifications.ui import render_notification_badge as render_notification_badge_v3
from modules.ui import load_css
from modules.ui.theme import ThemeManager, init_theme, render_theme_toggle
from modules.ui.v5_5 import (
    get_user_name,
    has_transactions,
    render_dashboard_v5,
    render_welcome_screen,
)

# =============================================================================
# CONFIGURATION PAGE
# =============================================================================
st.set_page_config(
    page_title="Synthèse",
    page_icon="📊",
    layout="wide",
)

# =============================================================================
# INITIALISATION
# =============================================================================
load_css()
init_db()

# Initialiser le thème V5.5
init_theme()
ThemeManager.apply_theme_css()


# =============================================================================
# RÉCUPÉRATION NOM UTILISATEUR
# =============================================================================
def get_display_user_name() -> str:
    """Récupère le nom d'utilisateur à afficher."""
    # 1. Essayer depuis session_state
    if "user_name" in st.session_state and st.session_state.user_name:
        return st.session_state.user_name

    # 2. Essayer depuis le module couple
    try:
        name = get_user_name()
        if name:
            return name
    except Exception:
        pass

    # 3. Défaut
    return "Alex"


user_name = get_display_user_name()

# =============================================================================
# SIDEBAR - Navigation & Configuration
# =============================================================================
st.sidebar.title("💰 Synthèse")

# Toggle de thème
render_theme_toggle()

st.sidebar.divider()

# Navigation rapide
st.sidebar.markdown("### 🧭 Navigation")
if st.sidebar.button("📥 Importer des opérations", use_container_width=True):
    st.switch_page("pages/01_Import.py")

if st.sidebar.button("⚙️ Configuration", use_container_width=True):
    st.switch_page("pages/08_Configuration.py")

st.sidebar.divider()

# Mode de test (optionnel, pour le développement)
with st.sidebar.expander("🔧 Options de test", expanded=False):
    test_mode = st.radio(
        "Mode",
        options=["Auto", "Dashboard forcé", "Welcome forcé"],
        index=0,
        help="Mode Auto: détecte automatiquement si vous avez des données",
    )

    user_name_input = st.text_input("Nom affiché", value=user_name)
    if user_name_input != user_name:
        user_name = user_name_input
        st.session_state.user_name = user_name

    show_mock = st.checkbox("Mode démo (données fictives)", value=False)

st.sidebar.divider()

# Notifications
notification_service_v3 = NotificationService()
render_notification_badge_v3(notification_service_v3)


# =============================================================================
# LOGIQUE DE RENDU PRINCIPAL
# =============================================================================
def render_auto_mode():
    """Mode automatique: détecte les données et affiche la vue appropriée."""
    has_data = has_transactions()

    if has_data:
        logger.info(f"Test_Dashboard: affichage dashboard pour {user_name}")
        render_dashboard_v5(user_name=user_name)
    else:
        logger.info(f"Test_Dashboard: affichage welcome screen pour {user_name}")
        render_welcome_screen(
            user_name=user_name,
            redirect_to_dashboard=False,  # Ne pas rediriger, rester sur cette page
            dashboard_page="pages/Dashboard_Beta.py",
        )


def render_forced_dashboard_mode():
    """Mode dashboard forcé (pour test)."""
    if show_mock or not has_transactions():
        # Mode démo avec données fictives
        st.info("💡 Mode démonstration avec données fictives")

        from modules.ui.v5_5.components import KPICard, KPIData
        from modules.ui.v5_5.components.dashboard_header import (
            DashboardHeader,
            get_current_month_name,
        )
        from modules.ui.v5_5.theme import apply_light_theme

        apply_light_theme()

        # Header
        DashboardHeader.render(
            user_name=user_name,
            current_month=get_current_month_name(),
        )

        # KPIs mock
        st.markdown("### 📊 Vue d'ensemble")

        kpis = [
            KPIData(
                "Reste à vivre",
                "1 847.52 €",
                "positive",
                "💚",
                "#DCFCE7",
                "+13.8%",
                "vs Janvier",
            ),
            KPIData(
                "Dépenses",
                "-2 152.48 €",
                "negative",
                "💳",
                "#FEE2E2",
                "-9.4%",
                "vs Janvier",
            ),
            KPIData(
                "Revenus",
                "4 200.00 €",
                "positive",
                "📈",
                "#DBEAFE",
                "+5.0%",
                "vs Janvier",
            ),
            KPIData(
                "Épargne",
                "200.00 €",
                "positive",
                "🎯",
                "#F3E8FF",
                None,
                "🎉 Premier versement !",
            ),
        ]

        cols = st.columns(4)
        for idx, kpi_data in enumerate(kpis):
            with cols[idx]:
                KPICard.render(kpi_data)

        st.success("✅ Dashboard affiché avec données de démonstration")
    else:
        render_dashboard_v5(user_name=user_name)


def render_forced_welcome_mode():
    """Mode welcome forcé (pour test)."""
    render_welcome_screen(
        user_name=user_name, redirect_to_dashboard=False, dashboard_page="pages/Dashboard_Beta.py"
    )


# =============================================================================
# RENDU PRINCIPAL
# =============================================================================
try:
    if test_mode == "Auto":
        render_auto_mode()
    elif test_mode == "Dashboard forcé":
        render_forced_dashboard_mode()
    else:  # Welcome forcé
        render_forced_welcome_mode()

except Exception as e:
    logger.exception("Erreur dans Test_Dashboard")
    st.error("🚨 Une erreur est survenue lors du chargement du dashboard.")
    st.exception(e)

    # Bouton de récupération
    if st.button("🔄 Réessayer"):
        st.rerun()

# =============================================================================
# FOOTER
# =============================================================================
st.divider()
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.caption("FinancePerso V5.5")

with col2:
    st.caption("[Retour à l'accueil](app.py)")

with col3:
    if has_transactions():
        st.caption("✅ Données synchronisées")
    else:
        st.caption("⚠️ Aucune donnée - Importez vos relevés")
