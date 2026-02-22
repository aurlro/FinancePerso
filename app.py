"""
FinancePerso v5.5 - Application consolidée
============================================

Version rationalisée avec:
- Architecture simplifiée (src/ + modules/)
- Nouvelles fonctionnalités Phases 4-5-6 intégrées
- Performance optimisée
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Configuration de base
st.set_page_config(
    page_title="FinancePerso",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ajouter le répertoire au path
sys.path.insert(0, str(Path(__file__).parent))

# ============================================================
# IMPORTS CORE (Infrastructure)
# ============================================================

from modules.logger import logger
from modules.error_tracking import init_error_tracking
from modules.encryption import get_encryption

# DB - Utiliser wrapper de compatibilité pendant transition
from modules.db_migration_wrapper import (
    get_db_connection,
    get_all_transactions_wrapper as get_all_transactions,
    add_transaction_wrapper as add_transaction,
)

# UI - Design System Vibe
from modules.ui import apply_vibe_theme
from modules.ui.components.quick_actions import render_quick_actions_grid
from modules.ui.components.daily_widget import render_daily_widget

# Notifications
from modules.notifications import get_notification_manager

# ============================================================
# IMPORTS BUSINESS LOGIC (src/)
# ============================================================

# Phase 2: Data Engineering
from src import (
    clean_transaction_label,
    clean_merchant_name,
)

# Phase 3: Subscription Engine
from src import (
    SubscriptionDetector,
    calculate_remaining_budget,
    Subscription,
)

# Phase 4: Monte Carlo
from src import (
    MonteCarloSimulator,
    ScenarioType,
    quick_simulation,
)

# Phase 5: Wealth & Agentic
from src import (
    WealthManager,
    AgentOrchestrator,
    RealEstateAsset,
    CryptoAsset,
)

# Phase 6: Security & Privacy
from src import SecurityMonitor
from modules.privacy import GDPRManager

# ============================================================
# IMPORTS VIEWS
# ============================================================

# Vues principales (anciennes)
from modules.db.migrations import init_db
from modules.db.stats import is_app_initialized, get_global_stats

# Nouvelles vues Phases 4-5-6
try:
    from views.subscriptions import render_subscriptions_page
    from views.projections import render_projections_page
    from views.wealth_view import render_wealth_dashboard
    NEW_VIEWS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Nouvelles vues non disponibles: {e}")
    NEW_VIEWS_AVAILABLE = False

# ============================================================
# INITIALISATION
# ============================================================

@st.cache_resource
def init_app():
    """Initialise l'application"""
    init_error_tracking()
    init_db()
    
    # Appliquer le thème Vibe
    try:
        apply_vibe_theme()
    except Exception as e:
        logger.warning(f"Thème Vibe non appliqué: {e}")
    
    return True

# Initialiser
init_app()

# ============================================================
# ROUTER PRINCIPAL
# ============================================================

def render_dashboard():
    """Rend le tableau de bord principal"""
    st.title("💰 FinancePerso - Dashboard")
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Balance", "€2,450", "+€120")
    with col2:
        st.metric("Dépenses", "€850", "-5%")
    with col3:
        st.metric("Épargne", "€450", "+€50")
    with col4:
        st.metric("Abonnements", "12", "0")
    
    # Widget quotidien
    render_daily_widget()
    
    # Actions rapides
    st.subheader("Actions rapides")
    render_quick_actions_grid()
    
    # Nouvelles fonctionnalités
    if NEW_VIEWS_AVAILABLE:
        st.divider()
        st.subheader("🆕 Nouveautés v5.5")
        
        cols = st.columns(3)
        with cols[0]:
            if st.button("📊 Patrimoine 360°", use_container_width=True):
                st.session_state.page = "Patrimoine"
                st.rerun()
        with cols[1]:
            if st.button("📈 Projections", use_container_width=True):
                st.session_state.page = "Projections"
                st.rerun()
        with cols[2]:
            if st.button("🔄 Abonnements", use_container_width=True):
                st.session_state.page = "Abonnements"
                st.rerun()

def render_old_import():
    """Rend l'ancienne vue d'import"""
    st.title("📥 Import de transactions")
    st.info("Utilisez la nouvelle vue 'Abonnements' pour une expérience améliorée.")
    
    uploaded_file = st.file_uploader("Fichier CSV", type=['csv'])
    if uploaded_file:
        st.success("Fichier chargé avec succès!")

def render_old_validation():
    """Rend l'ancienne vue de validation"""
    st.title("✅ Validation")
    st.info("Cette vue sera migrée vers le nouveau système.")

# ============================================================
# NAVIGATION
# ============================================================

def main():
    """Fonction principale"""
    
    # Sidebar
    with st.sidebar:
        st.title("💰 FinancePerso")
        st.markdown("v5.5 - Consolidé")
        st.divider()
        
        # Menu principal
        pages = {
            "🏠 Dashboard": "Dashboard",
            "📥 Import": "Import",
            "✅ Validation": "Validation",
        }
        
        # Ajouter nouvelles pages si disponibles
        if NEW_VIEWS_AVAILABLE:
            pages.update({
                "🔄 Abonnements": "Abonnements",
                "📈 Projections": "Projections",
                "📊 Patrimoine": "Patrimoine",
            })
        
        # Navigation
        selected = st.radio("Navigation", list(pages.keys()))
        page = pages[selected]
        
        # Stocker dans session state
        if "page" in st.session_state:
            page = st.session_state.page
            del st.session_state.page
        
        st.divider()
        
        # Stats
        st.caption("📊 Statistiques")
        st.metric("Transactions", "1,234")
        st.metric("Ce mois", "€2,450")
    
    # Rendre la page sélectionnée
    if page == "Dashboard":
        render_dashboard()
    elif page == "Import":
        render_old_import()
    elif page == "Validation":
        render_old_validation()
    elif page == "Abonnements" and NEW_VIEWS_AVAILABLE:
        render_subscriptions_page()
    elif page == "Projections" and NEW_VIEWS_AVAILABLE:
        render_projections_page()
    elif page == "Patrimoine" and NEW_VIEWS_AVAILABLE:
        render_wealth_dashboard()
    else:
        st.error("Page non disponible")

if __name__ == "__main__":
    main()
