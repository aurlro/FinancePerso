"""
Page Synthèse - Tableau de bord financier optimisé.

Optimisations apportées:
- Imports centralisés en haut du fichier
- Caching des données et calculs
- Fragments pour les sections lourdes (réduisent les re-rendus)
- Organisation en onglets pour réduire le scroll
- DRY: Logique de filtrage extraite dans un module dédié
- Déduplication des conversions datetime
"""

# ============================================================================
# IMPORTS STANDARD
# ============================================================================
import os
import sys

# ============================================================================
# IMPORTS TIERS
# ============================================================================
import streamlit as st
import pandas as pd

# ============================================================================
# IMPORTS LOCAUX - Modules de base
# ============================================================================
from modules.db.migrations import init_db
from modules.db.categories import get_categories_with_emojis
from modules.db.members import get_orphan_labels, get_unique_members
from modules.ui import load_css, render_scroll_to_top
from modules.analytics import detect_financial_profile
from modules.notifications import check_budget_alerts

# ============================================================================
# IMPORTS LOCAUX - Composants dashboard
# ============================================================================
from modules.ui.dashboard.filters import (
    render_filter_sidebar,
    compute_previous_period,
)
from modules.ui.dashboard.sections import (
    render_budget_tab,
    render_analysis_tab,
    render_ai_tab,
)
from modules.ui.dashboard.customizable_dashboard import (
    render_customizable_overview,
    render_dashboard_configurator,
    DashboardLayoutManager
)

# ============================================================================
# CONFIGURATION PAGE
# ============================================================================
st.set_page_config(page_title="Synthèse", page_icon="📊", layout="wide")
load_css()
init_db()

# ============================================================================
# CONSTANTES
# ============================================================================
ONBOARDING_KEY = 'onboarding_checked'
ONBOARDING_COUNT_KEY = 'onboarding_suggestions_count'
CACHE_TTL_SECONDS = 300  # 5 minutes


# ============================================================================
# FONCTIONS DE CACHE
# ============================================================================
@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_cached_transactions() -> pd.DataFrame:
    """
    Récupère les transactions avec conversion datetime (cache 5 min).
    Évite de re-parcourir et re-convertir la base à chaque interaction.
    """
    # Import différé pour éviter les imports circulaires au niveau module
    from modules.data_manager import get_all_transactions
    
    df = get_all_transactions()
    if not df.empty:
        df['date_dt'] = pd.to_datetime(df['date'])
    return df


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_cached_categories() -> tuple:
    """
    Récupère les catégories avec emojis et le DataFrame complet.
    """
    cat_emoji_map = get_categories_with_emojis()
    from modules.data_manager import get_categories_df
    cat_df = get_categories_df()
    return cat_emoji_map, cat_df


# ============================================================================
# NOTIFICATIONS ET ALERTES
# ============================================================================
def render_onboarding_notification(df: pd.DataFrame) -> None:
    """
    Affiche la notification de configuration assistée si nécessaire.
    Compact et collapsible par défaut.
    """
    if ONBOARDING_KEY not in st.session_state:
        st.session_state[ONBOARDING_KEY] = False
    
    if not st.session_state[ONBOARDING_KEY] and not df.empty:
        suggestions = detect_financial_profile(df)
        if suggestions:
            st.session_state[ONBOARDING_COUNT_KEY] = len(suggestions)
            st.session_state[ONBOARDING_KEY] = True
    
    count = st.session_state.get(ONBOARDING_COUNT_KEY, 0)
    if count > 0:
        with st.expander(f"🔔 Configuration Assistée - {count} suggestions détectées", expanded=False):
            st.info(
                f"J'ai détecté **{count}** éléments importants à configurer "
                "(Salaire, Loyer, Factures...)."
            )
            col1, col2, _ = st.columns([1, 1, 2])
            with col1:
                if st.button("Configurer maintenant ➡️", type="primary", key="btn_config"):
                    st.switch_page("pages/5_Assistant.py")
            with col2:
                if st.button("Me rappeler plus tard", key="btn_remind"):
                    st.session_state[ONBOARDING_COUNT_KEY] = 0
                    st.rerun()


def render_data_health_notifications(df: pd.DataFrame) -> None:
    """
    Affiche les notifications de santé des données (libellés orphelins).
    Déplacé dans la sidebar pour ne pas encombrer le contenu principal.
    """
    orphans = get_orphan_labels()
    if orphans and not df.empty:
        with st.sidebar:
            st.divider()
            st.warning(
                f"🧹 **Nettoyage requis** : {len(orphans)} libellés incohérents "
                f"(ex: {', '.join(orphans[:2])})..."
            )
            if st.button("Aller au nettoyage 🛼", use_container_width=True, key="btn_cleanup"):
                st.switch_page("pages/9_Configuration.py")


# ============================================================================
# RENDU PRINCIPAL
# ============================================================================
def main():
    """Point d'entrée principal de la page."""
    
    # Titre de la page
    st.title("📊 Tableau de bord")
    
    # Vérifier les alertes budget (notifications système)
    check_budget_alerts()
    
    # PHASE 3: Notifications temps réel
    from modules.notifications_realtime import render_notification_banner
    render_notification_banner()
    
    # Charger les données (avec cache)
    df = get_cached_transactions()
    
    # Notifications (compactes)
    render_onboarding_notification(df)
    render_data_health_notifications(df)
    
    # État vide
    if df.empty:
        st.info("📭 Aucune donnée disponible. Commencez par importer des relevés.")
        st.button(
            "➕ Importer des transactions",
            on_click=lambda: st.switch_page("pages/1_Import.py"),
            type="primary"
        )
        return
    
    # Charger les catégories (avec cache)
    cat_emoji_map, _ = get_cached_categories()
    official_members = get_unique_members()
    
    # =========================================================================
    # FILTRES (Sidebar)
    # =========================================================================
    filter_result = render_filter_sidebar(df)
    df_current = filter_result['df_filtered']
    
    # Vérifier si des filtres actifs réduisent trop les données
    if df_current.empty:
        st.warning("⚠️ Aucune donnée ne correspond aux filtres sélectionnés.")
        st.caption("Essayez d'élargir votre sélection de période ou de filtres.")
        return
    
    # Calcul de la période précédente pour comparaison
    df_prev = compute_previous_period(
        df,
        df_current,
        filter_result['show_internal'],
        filter_result['show_hors_budget']
    )
    
    # =========================================================================
    # ONGLETS ORGANISÉS
    # =========================================================================
    tab_overview, tab_budget, tab_analysis, tab_ai = st.tabs([
        "📈 **Vue d'ensemble**",
        "🎯 **Budgets & Prévisions**",
        "👥 **Analyses**",
        "🔮 **IA & Rapports**"
    ])
    
    # -------------------------------------------------------------------------
    # Onglet 1: Vue d'ensemble personnalisable
    # -------------------------------------------------------------------------
    with tab_overview:
        # Bouton de configuration dans la sidebar
        with st.sidebar:
            st.divider()
            if st.button("🎛️ Personnaliser le dashboard", use_container_width=True, key="btn_customize"):
                st.session_state['show_dashboard_config'] = True
        
        # Afficher le configurateur si demandé
        if st.session_state.get('show_dashboard_config', False):
            with st.expander("Configuration du dashboard", expanded=True):
                render_dashboard_configurator()
                if st.button("Fermer", key="close_config"):
                    st.session_state['show_dashboard_config'] = False
                    st.rerun()
        
        # Rendre la vue d'ensemble personnalisée
        render_customizable_overview(df_current, df_prev, cat_emoji_map, df)
    
    # -------------------------------------------------------------------------
    # Onglet 2: Budgets & Prévisions
    # -------------------------------------------------------------------------
    with tab_budget:
        render_budget_tab(
            df_current,
            df,
            filter_result['selected_years'],
            filter_result['selected_months'],
            cat_emoji_map
        )
    
    # -------------------------------------------------------------------------
    # Onglet 3: Analyses (Membres, Bénéficiaires, Tags)
    # -------------------------------------------------------------------------
    with tab_analysis:
        render_analysis_tab(df_current, df, official_members, cat_emoji_map)
    
    # -------------------------------------------------------------------------
    # Onglet 4: IA & Rapports
    # -------------------------------------------------------------------------
    with tab_ai:
        render_ai_tab(
            df_current,
            df_prev,
            df,
            filter_result['selected_years'],
            filter_result['selected_months']
        )
    
    # =========================================================================
    # PIED DE PAGE
    # =========================================================================
    render_scroll_to_top()
    
    from modules.ui.layout import render_app_info
    render_app_info()


# Lancement
if __name__ == "__main__":
    main()
