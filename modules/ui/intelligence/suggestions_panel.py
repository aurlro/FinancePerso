"""
Smart Suggestions Panel for Intelligence page.

Renders actionable suggestions based on data analysis.
"""


import pandas as pd
import streamlit as st

from modules.ai.smart_suggestions import Suggestion, get_smart_suggestions
from modules.db.rules import add_learning_rule
from modules.logger import logger
from modules.ui.feedback import toast_error, toast_info, toast_success

# Session state initialization
if "suggestions_filter" not in st.session_state:
    st.session_state["suggestions_filter"] = "all"
if "suggestions_dismissed" not in st.session_state:
    st.session_state["suggestions_dismissed"] = set()


def _get_priority_color(priority: str) -> str:
    """Get color for priority level."""
    return {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")


def _get_type_icon(suggestion_type: str) -> str:
    """Get icon for suggestion type."""
    return {
        "category": "🏷️",
        "rule": "📝",
        "budget": "💰",
        "member": "👤",
        "duplicate": "⚠️",
        "pattern": "📊",
        "income": "💵",
        "savings": "🏦",
        "subscription": "💳",
    }.get(suggestion_type, "💡")


def _handle_suggestion_action(suggestion: Suggestion):
    """Handle the action for a suggestion."""
    action_data = suggestion.action_data
    action_type = action_data.get("type")

    try:
        if action_type == "create_rule":
            pattern = action_data.get("pattern", "")
            category = action_data.get("category", action_data.get("suggested_category", "Inconnu"))

            if pattern and category:
                add_learning_rule(pattern, category)
                toast_success(f"✅ Règle créée : '{pattern}' → {category}", icon="📝")
                return True

        elif action_type == "map_card":
            card_suffix = action_data.get("card_suffix")
            # Store in session state for redirect to member config
            st.session_state["pending_card_mapping"] = card_suffix
            toast_info(
                f"💳 Allez dans Configuration → Membres pour mapper la carte ...{card_suffix}",
                icon="👤",
            )
            return True

        elif action_type == "map_account":
            account_label = action_data.get("account_label")
            st.session_state["pending_account_mapping"] = account_label
            toast_info(
                "🏦 Allez dans Configuration → Membres pour définir le membre par défaut",
                icon="👤",
            )
            return True

        elif action_type == "adjust_budget":
            category = action_data.get("category")
            st.session_state["pending_budget_adjustment"] = category
            toast_info("💰 Allez dans l'onglet Budgets pour ajuster", icon="💰")
            return True

        elif action_type == "view_duplicates":
            st.session_state["show_duplicate_analysis"] = True
            toast_info("🔍 Analyse des doublons activée", icon="🔍")
            return True

        elif action_type == "merge_categories":
            source = action_data.get("source")
            target = action_data.get("target")
            toast_info(
                f"🏷️ Pour fusionner '{source}' → '{target}', utilisez Configuration → Catégories",
                icon="🏷️",
            )
            return True

        elif action_type == "view_subscription":
            label = action_data.get("label")
            st.session_state["view_subscription_label"] = label
            toast_info(f"💳 Analyse de l'abonnement '{label[:30]}...'", icon="💳")
            return True

        elif action_type == "view_income_analysis":
            st.session_state["view_income_analysis"] = True
            toast_info("📊 Analyse des revenus", icon="📊")
            return True

        elif action_type == "view_budget":
            category = action_data.get("category")
            st.session_state["view_budget_category"] = category
            toast_info(f"💰 Détails du budget : {category}", icon="💰")
            return True

        elif action_type == "view_transaction":
            tx_id = action_data.get("transaction_id")
            st.session_state["highlight_transaction_id"] = tx_id
            toast_info("💰 Vérification de la transaction", icon="💰")
            return True

        elif action_type == "add_member":
            name = action_data.get("name")
            st.session_state["pending_new_member"] = name
            toast_info(f"👤 Allez dans Configuration → Membres pour ajouter '{name}'", icon="👤")
            return True

        elif action_type == "view_savings_analysis":
            st.session_state["view_savings_analysis"] = True
            toast_info("🏦 Analyse de l'épargne", icon="🏦")
            return True

        elif action_type == "add_tags":
            category = action_data.get("category")
            st.session_state["add_tags_category"] = category
            toast_info(f"🏷️ Ajoutez des tags aux transactions de '{category}'", icon="🏷️")
            return True

        elif action_type == "explore_category":
            category = action_data.get("category")
            st.session_state["explore_category"] = category
            toast_info(f"🔍 Exploration de la catégorie : {category}", icon="🔍")
            return True

    except Exception as e:
        logger.error(f"Error handling suggestion action: {e}")
        toast_error(f"❌ Erreur : {str(e)[:50]}", icon="❌")

    return False


@st.fragment
def render_smart_suggestions_panel(
    transactions_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    budgets_df: pd.DataFrame,
    members_df: pd.DataFrame,
):
    """
    Render the smart suggestions panel.

    This is a Streamlit fragment that only re-renders this section
    when suggestions are refreshed.
    """
    st.header("💡 Suggestions Intelligentes")
    st.markdown("L'IA analyse vos données pour vous proposer des optimisations.")

    # Check if we have data
    if transactions_df.empty:
        st.info("📭 Ajoutez des transactions pour recevoir des suggestions personnalisées.")
        return

    # Initialize session state for dismissed suggestions (safeguard)
    if "suggestions_dismissed" not in st.session_state:
        st.session_state["suggestions_dismissed"] = set()

    # Get suggestions
    with st.spinner("Analyse en cours..."):
        suggestions = get_smart_suggestions(transactions_df, rules_df, budgets_df, members_df)

    # Filter out dismissed suggestions
    suggestions = [s for s in suggestions if s.id not in st.session_state["suggestions_dismissed"]]

    if not suggestions:
        st.success("🎉 Tout semble bien configuré ! Aucune suggestion pour le moment.")
        return

    # Initialize filter session state (safeguard)
    if "suggestions_filter" not in st.session_state:
        st.session_state["suggestions_filter"] = "all"

    # Filter controls
    col_filter, col_count = st.columns([2, 1])

    with col_filter:
        filter_options = {
            "all": "Toutes les suggestions",
            "high": "🔴 Priorité haute",
            "rule": "📝 Règles",
            "budget": "💰 Budgets",
            "member": "👤 Membres",
            "pattern": "📊 Patterns",
            "income": "💵 Revenus",
            "savings": "🏦 Épargne",
            "duplicate": "⚠️ Doublons",
        }

        selected_filter = st.segmented_control(
            "Filtrer",
            options=list(filter_options.keys()),
            format_func=lambda x: filter_options[x],
            default=st.session_state["suggestions_filter"],
            key="suggestions_filter_control",
        )

        if selected_filter:
            st.session_state["suggestions_filter"] = selected_filter

    with col_count:
        st.metric("Suggestions", value=len(suggestions))

    # Apply filter
    filtered_suggestions = suggestions
    filter_type = st.session_state["suggestions_filter"]

    if filter_type == "high":
        filtered_suggestions = [s for s in suggestions if s.priority == "high"]
    elif filter_type in ["rule", "budget", "member"]:
        filtered_suggestions = [s for s in suggestions if s.type == filter_type]

    # Display suggestions
    st.divider()

    for i, suggestion in enumerate(filtered_suggestions[:10]):  # Limit to 10
        with st.container(border=True):
            # Header with icon and title
            col_icon, col_title, col_priority = st.columns([0.5, 4, 1])

            with col_icon:
                st.markdown(f"{_get_type_icon(suggestion.type)}")

            with col_title:
                st.markdown(f"**{suggestion.title}**")

            with col_priority:
                st.markdown(f"{_get_priority_color(suggestion.priority)}")

            # Description
            st.markdown(suggestion.description)

            # Impact indicator
            impact_col, action_col, dismiss_col = st.columns([2, 1.5, 0.8])

            with impact_col:
                st.progress(
                    suggestion.impact_score / 100, text=f"Impact: {suggestion.impact_score}/100"
                )

            with action_col:
                action_key = f"sugg_action_{suggestion.id}_{i}"

                if suggestion.auto_fixable:
                    if st.button(
                        f"✨ {suggestion.action_label}",
                        use_container_width=True,
                        key=action_key,
                        type="primary",
                    ):
                        if _handle_suggestion_action(suggestion):
                            st.session_state["suggestions_dismissed"].add(suggestion.id)
                            st.rerun(scope="fragment")
                else:
                    if st.button(suggestion.action_label, use_container_width=True, key=action_key):
                        _handle_suggestion_action(suggestion)

            with dismiss_col:
                dismiss_key = f"sugg_dismiss_{suggestion.id}_{i}"
                if st.button("🗑️", key=dismiss_key, help="Ignorer cette suggestion"):
                    st.session_state["suggestions_dismissed"].add(suggestion.id)
                    toast_info("Suggestion ignorée", icon="🗑️")
                    st.rerun(scope="fragment")

    # Show more indicator
    if len(filtered_suggestions) > 10:
        st.caption(f"... et {len(filtered_suggestions) - 10} autres suggestions")

    # Summary stats
    if suggestions:
        st.divider()
        cols = st.columns(4)

        high_count = len([s for s in suggestions if s.priority == "high"])
        medium_count = len([s for s in suggestions if s.priority == "medium"])
        auto_fixable_count = len([s for s in suggestions if s.auto_fixable])
        total_impact = sum(s.impact_score for s in suggestions)

        with cols[0]:
            st.metric("🔴 Haute prio", high_count)
        with cols[1]:
            st.metric("🟡 Moyenne prio", medium_count)
        with cols[2]:
            st.metric("✨ Auto-fixables", auto_fixable_count)
        with cols[3]:
            st.metric("📊 Impact total", f"{total_impact}/1000")


def render_mini_suggestions_card(
    transactions_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    budgets_df: pd.DataFrame,
    members_df: pd.DataFrame,
):
    """
    Render a compact card showing top suggestions count.
    Use this in dashboard or overview pages.
    """
    if transactions_df.empty:
        return

    suggestions = get_smart_suggestions(transactions_df, rules_df, budgets_df, members_df)
    suggestions = [
        s for s in suggestions if s.id not in st.session_state.get("suggestions_dismissed", set())
    ]

    if not suggestions:
        st.success("🎉 Aucune suggestion - Tout est optimisé !")
        return

    high_priority = len([s for s in suggestions if s.priority == "high"])

    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            st.markdown("### 💡")

        with col2:
            st.markdown(f"**{len(suggestions)} suggestion(s) d'optimisation**")
            if high_priority > 0:
                st.markdown(f"🔴 {high_priority} priorité haute")

        with col3:
            if st.button("Voir", use_container_width=True, key="mini_suggestions_btn"):
                # Navigate to intelligence page
                st.query_params["tab"] = "Suggestions"
                st.rerun()
