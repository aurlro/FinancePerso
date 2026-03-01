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

# ============================================================================
# IMPORTS TIERS
# ============================================================================
import pandas as pd
import streamlit as st

from modules.analytics import detect_financial_profile
from modules.db.categories import get_categories_with_emojis
from modules.db.members import get_orphan_labels, get_unique_members

# ============================================================================
# IMPORTS LOCAUX - Modules de base
# ============================================================================
from modules.db.migrations import init_db
from modules.notifications import check_budget_alerts
from modules.ui import load_css, render_scroll_to_top
from modules.ui.components.savings_goals_widget import (
    render_savings_goals_summary,
)
from modules.ui.components.smart_reminders_widget import render_smart_reminders_widget
from modules.ui.dashboard.customizable_dashboard import (
    render_customizable_overview,
    render_dashboard_configurator,
)

# ============================================================================
# IMPORTS LOCAUX - Composants dashboard
# ============================================================================
from modules.ui.dashboard.filters import (
    compute_previous_period,
    render_filter_info,
    render_filter_sidebar,
)
from modules.ui.dashboard.sections import (
    render_ai_tab,
    render_analysis_tab,
    render_budget_tab,
)
from modules.ui.couple.dashboard import render_couple_dashboard
from modules.ui.feedback import toast_info, toast_success

# ============================================================================
# CONFIGURATION PAGE
# ============================================================================
st.set_page_config(page_title="Synthèse", page_icon="📊", layout="wide")
load_css()
init_db()

# ============================================================================
# CONSTANTES
# ============================================================================
ONBOARDING_KEY = "onboarding_checked"
ONBOARDING_COUNT_KEY = "onboarding_suggestions_count"
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
    from modules.db.transactions import get_all_transactions

    df = get_all_transactions()
    if not df.empty:
        df["date_dt"] = pd.to_datetime(df["date"])
    return df


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_cached_categories() -> tuple:
    """
    Récupère les catégories avec emojis et le DataFrame complet.
    """
    cat_emoji_map = get_categories_with_emojis()
    from modules.db.categories import get_categories_df

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
        suggestions = detect_financial_profile(df)

        # Fermer par défaut après la première visite (amélioration UX)
        CONFIG_SEEN_KEY = "config_assist_seen"
        is_first_visit = CONFIG_SEEN_KEY not in st.session_state
        expanded_default = is_first_visit  # Ouvert uniquement la première fois

        with st.expander(
            f"🔔 Configuration Assistée - {count} suggestion(s) détectée(s)",
            expanded=expanded_default,
        ):
            # Marquer comme vu après affichage
            if is_first_visit:
                st.session_state[CONFIG_SEEN_KEY] = True
            st.markdown("##### J'ai détecté des opportunités de configuration")
            st.caption("Vérifiez et ajustez les suggestions avant de les valider.")

            from modules.db.categories import get_categories_with_emojis
            from modules.db.rules import add_learning_rule
            from modules.ui.feedback import toast_error, toast_success

            # Get available categories for dropdown
            categories = get_categories_with_emojis()
            category_list = (
                list(categories.keys())
                if categories
                else ["Revenus", "Logement", "Alimentation", "Transport", "Loisirs"]
            )

            for i, sug in enumerate(suggestions):
                with st.container(border=True):
                    # Header
                    col_header, col_actions = st.columns([3, 1])
                    with col_header:
                        st.write(f"**{sug['type']}**")
                        confidence = sug.get("confidence", "Moyenne")
                        amount_display = abs(sug["amount"])
                        st.caption(
                            f"Confiance: {'🟢' if confidence == 'Haute' else '🟡'} {confidence} | Montant moyen: {amount_display:.2f} €"
                        )

                    with col_actions:
                        if st.button(
                            "🗑️ Ignorer",
                            key=f"sug_skip_{i}",
                            help="Ne pas créer de règle pour cette suggestion",
                        ):
                            st.session_state[ONBOARDING_COUNT_KEY] -= 1
                            st.rerun()

                    # Editable fields
                    col1, col2, col3 = st.columns([2, 1, 1])

                    with col1:
                        # Pattern input with current value
                        current_label = (
                            sug["label"] if sug["label"] else sug.get("original_label", "")
                        )
                        edited_label = st.text_input(
                            "Pattern de détection",
                            value=current_label,
                            key=f"sug_pattern_{i}",
                            help="Modifiez pour affiner la détection (ex: 'SALAIRE' détectera toutes les transactions contenant 'SALAIRE')",
                        )

                    with col2:
                        # Category dropdown
                        current_cat = sug["default_category"]
                        edited_category = st.selectbox(
                            "Catégorie",
                            options=category_list,
                            index=(
                                category_list.index(current_cat)
                                if current_cat in category_list
                                else 0
                            ),
                            key=f"sug_cat_{i}",
                        )

                    with col3:
                        st.write("")
                        st.write("")
                        if st.button(
                            "✅ Valider",
                            key=f"sug_val_{i}",
                            use_container_width=True,
                            type="primary",
                        ):
                            if not edited_label.strip():
                                toast_error("Le pattern ne peut pas être vide", icon="⚠️")
                            else:
                                if add_learning_rule(edited_label, edited_category):
                                    toast_success(
                                        f"✅ Règle créée: '{edited_label}' → {edited_category}",
                                        icon="📝",
                                    )
                                    st.session_state[ONBOARDING_COUNT_KEY] -= 1
                                    st.rerun()
                                else:
                                    toast_error("❌ Erreur lors de la création de la règle")

            st.divider()
            col1, col2, _ = st.columns([1, 1, 2])
            with col1:
                if st.button("Gérer toutes les règles ➡️", type="primary", key="btn_config"):
                    toast_success("Ouverture de la configuration des règles...", icon="⚡")
                    st.session_state["intel_active_tab"] = "📋 Règles"
                    st.switch_page("pages/4_Intelligence.py")
            with col2:
                if st.button("Ignorer toutes", key="btn_remind"):
                    toast_info(
                        "Vous pourrez configurer les règles plus tard dans l'onglet Intelligence",
                        icon="💡",
                    )
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
            if st.button("Aller à la configuration ⚙️", use_container_width=True, key="btn_cleanup"):
                toast_success("Ouverture de la configuration...", icon="⚙️")
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
    render_smart_reminders_widget()  # Rappels intelligents
    render_onboarding_notification(df)
    render_data_health_notifications(df)

    # État vide
    if df.empty:
        from modules.ui.components.welcome_empty_state import WelcomeEmptyState

        WelcomeEmptyState.render(
            title="👋 Bonjour !",
            subtitle="Bienvenue dans votre tableau de bord",
            message="Importez vos premiers relevés pour visualiser vos finances et suivre vos objectifs.",
            primary_action_text="📥 Importer mes relevés",
            primary_action_link="pages/1_Opérations.py",
            show_steps=True,
        )
        return

    # Charger les catégories (avec cache)
    cat_emoji_map, _ = get_cached_categories()
    official_members = get_unique_members()

    # =========================================================================
    # FILTRES (Sidebar)
    # =========================================================================
    filter_result = render_filter_sidebar(df)
    df_current = filter_result["df_filtered"]

    # Affichage des infos de filtres et alertes d'exclusion
    render_filter_info(df, filter_result)

    # Vérifier si des filtres actifs réduisent trop les données
    if df_current.empty:
        st.warning("⚠️ Aucune donnée ne correspond aux filtres sélectionnés.")
        st.caption("Essayez d'élargir votre sélection de période ou de filtres.")
        return

    # Calcul de la période précédente pour comparaison
    df_prev = compute_previous_period(
        df, df_current, filter_result["show_internal"], filter_result["show_hors_budget"]
    )

    # =========================================================================
    # ONGLETS ORGANISÉS
    # =========================================================================
    # Vérifier si le mode couple est configuré pour afficher l'onglet
    from modules.couple.couple_settings import is_couple_configured
    show_couple_tab = is_couple_configured()
    
    if show_couple_tab:
        tab_overview, tab_couple, tab_budget, tab_analysis, tab_ai = st.tabs(
            [
                "📈 **Vue d'ensemble**",
                "💑 **Vue Couple**",
                "🎯 **Budgets & Prévisions**",
                "👥 **Analyses**",
                "🔮 **IA & Rapports**",
            ]
        )
    else:
        tab_overview, tab_budget, tab_analysis, tab_ai = st.tabs(
            [
                "📈 **Vue d'ensemble**",
                "🎯 **Budgets & Prévisions**",
                "👥 **Analyses**",
                "🔮 **IA & Rapports**",
            ]
        )

    # -------------------------------------------------------------------------
    # Onglet 1: Vue d'ensemble personnalisable
    # -------------------------------------------------------------------------
    with tab_overview:
        # Bouton de configuration dans la sidebar
        with st.sidebar:
            st.divider()
            if st.button(
                "🎛️ Personnaliser le dashboard", use_container_width=True, key="btn_customize"
            ):
                st.session_state["show_dashboard_config"] = True

        # Afficher le configurateur si demandé
        if st.session_state.get("show_dashboard_config", False):
            with st.expander("Configuration du dashboard", expanded=True):
                render_dashboard_configurator()
                if st.button("Fermer", key="close_config"):
                    st.session_state["show_dashboard_config"] = False
                    st.rerun()

        # Rendre la vue d'ensemble personnalisée
        render_customizable_overview(df_current, df_prev, cat_emoji_map, df)

        # Objectifs d'épargne (nouvelle section)
        st.divider()
        render_savings_goals_summary()

    # -------------------------------------------------------------------------
    # Onglet 2: Vue Couple (si configuré)
    # -------------------------------------------------------------------------
    if show_couple_tab:
        with tab_couple:
            render_couple_dashboard()

    # -------------------------------------------------------------------------
    # Onglet 3: Budgets & Prévisions
    # -------------------------------------------------------------------------
    with tab_budget:
        render_budget_tab(
            df_current,
            df,
            filter_result["selected_years"],
            filter_result["selected_months"],
            cat_emoji_map,
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
            filter_result["selected_years"],
            filter_result["selected_months"],
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
