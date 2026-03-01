"""
Smart Quick Actions component.
Displays contextual actions based on user's app usage state.
Replaces the static 'Revoir le guide' button with intelligent suggestions.
"""

import streamlit as st

from modules.db.budgets import get_budgets
from modules.db.rules import get_learning_rules
from modules.db.stats import get_global_stats
from modules.db.transactions import get_all_transactions


def get_user_progress_state():
    """
    Analyze user's app usage to determine progress state.

    Returns:
        Dictionary with:
        - has_transactions: bool
        - has_rules: bool
        - has_budgets: bool
        - tx_count: int
        - rules_count: int
        - budgets_count: int
        - uncategorized_count: int
    """
    state = {
        "has_transactions": False,
        "has_rules": False,
        "has_budgets": False,
        "tx_count": 0,
        "rules_count": 0,
        "budgets_count": 0,
        "uncategorized_count": 0,
        "needs_attention": False,
    }

    try:
        # Get transaction stats
        stats = get_global_stats()
        state["tx_count"] = stats.get("total_transactions", 0)
        state["has_transactions"] = state["tx_count"] > 0

        # Check for uncategorized transactions
        if state["has_transactions"]:
            df = get_all_transactions(limit=1000)
            if not df.empty and "category_validated" in df.columns:
                uncategorized = df[
                    (df["category_validated"].isna())
                    | (df["category_validated"] == "")
                    | (df["category_validated"] == "Non catégorisé")
                ]
                state["uncategorized_count"] = len(uncategorized)

        # Get rules count
        rules_df = get_learning_rules()
        state["rules_count"] = len(rules_df)
        state["has_rules"] = state["rules_count"] > 0

        # Get budgets count
        budgets_df = get_budgets()
        state["budgets_count"] = len(budgets_df)
        state["has_budgets"] = state["budgets_count"] > 0

        # Determine if attention is needed
        state["needs_attention"] = (
            state["uncategorized_count"] > 5
            or (state["has_transactions"] and not state["has_rules"])
            or (state["has_transactions"] and not state["has_budgets"])
        )

    except Exception as e:
        # Log error but don't break UI - return default state
        from modules.logger import logger

        logger.warning(f"Could not compute user progress state: {e}")
        # State remains with default values

    return state


def get_primary_action(state):
    """
    Determine the primary action based on user state.
    Priority order: Import > Categorize > Rules > Budgets > Dashboard

    Returns:
        Action dict with: icon, label, description, page, priority
    """
    # Priority 1: No transactions -> Import
    if not state["has_transactions"]:
        return {
            "icon": "📥",
            "label": "Importer mon premier relevé",
            "description": "Commencez par ajouter vos transactions bancaires",
            "page": "1_Opérations",
            "priority": "high",
            "action_type": "primary",
            "tab": "📥 Importation",
        }

    # Priority 2: Many uncategorized -> Validation
    if state["uncategorized_count"] > 5:
        return {
            "icon": "🏷️",
            "label": "Catégoriser ({} en attente)".format(state["uncategorized_count"]),
            "description": "Validez vos transactions non catégorisées",
            "page": "1_Opérations",
            "priority": "high",
            "action_type": "primary",
            "tab": "✅ Validation",
        }

    # Priority 3: No rules -> Create rules
    if not state["has_rules"]:
        return {
            "icon": "⚡",
            "label": "Créer une règle auto",
            "description": "Automatisez la catégorisation de vos dépenses",
            "page": "4_Intelligence",
            "priority": "medium",
            "action_type": "primary",
            "tab": "📋 Règles",
        }

    # Priority 4: No budgets -> Set budgets
    if not state["has_budgets"]:
        return {
            "icon": "🎯",
            "label": "Définir un budget",
            "description": "Suivez vos limites de dépenses par catégorie",
            "page": "4_Intelligence",
            "priority": "medium",
            "action_type": "primary",
            "tab": "🎯 Budgets",
        }

    # Default: View dashboard
    return {
        "icon": "📊",
        "label": "Voir mon tableau de bord",
        "description": "{} transactions • {} règles • {} budgets".format(
            state["tx_count"], state["rules_count"], state["budgets_count"]
        ),
        "page": "3_Synthèse",
        "priority": "normal",
        "action_type": "secondary",
    }


def get_secondary_actions(state, primary_page):
    """
    Get 2 secondary actions complementary to the primary one.
    """
    actions = []

    # Suggest adding rules if has transactions but few/no rules
    if state["has_transactions"] and state["rules_count"] < 3 and primary_page != "4_Intelligence":
        actions.append(
            {
                "icon": "⚡",
                "label": "Règles auto",
                "page": "4_Intelligence",
                "help": "Créer des règles de catégorisation",
                "tab": "📋 Règles",
            }
        )

    # Suggest budgets if has transactions but no budgets
    if state["has_transactions"] and not state["has_budgets"] and primary_page != "4_Intelligence":
        actions.append(
            {
                "icon": "🎯",
                "label": "Budgets",
                "page": "4_Intelligence",
                "help": "Définir des limites de dépenses",
                "tab": "🎯 Budgets",
            }
        )

    # Suggest import if has some transactions
    if state["has_transactions"] and primary_page != "1_Opérations":
        actions.append(
            {
                "icon": "📥",
                "label": "Importer",
                "page": "1_Opérations",
                "help": "Ajouter de nouvelles transactions",
                "tab": "📥 Importation",
            }
        )

    # Suggest validation if has transactions
    if (
        state["has_transactions"]
        and state["uncategorized_count"] > 0
        and primary_page != "1_Opérations"
    ):
        actions.append(
            {
                "icon": "✅",
                "label": "Valider",
                "page": "1_Opérations",
                "help": "{} à catégoriser".format(state["uncategorized_count"]),
                "tab": "✅ Validation",
            }
        )

    # Suggest AI assistant
    if state["has_transactions"] and primary_page != "7_Assistant":
        actions.append(
            {
                "icon": "🤖",
                "label": "Assistant IA",
                "page": "7_Assistant",
                "help": "Poser une question sur vos finances",
            }
        )

    # Return max 2 actions
    return actions[:2]


def render_smart_actions():
    """
    Render the smart quick actions component.
    Replaces the old 'Revoir le guide' button with contextual actions.
    """
    # Get user state
    state = get_user_progress_state()

    # Get primary action
    primary = get_primary_action(state)

    # Render section
    st.subheader("Prochaine étape")

    # Primary action button (large)
    btn_type = "primary" if primary["action_type"] == "primary" else "secondary"

    if st.button(
        "{} {}".format(primary["icon"], primary["label"]),
        type=btn_type,
        use_container_width=True,
        help=primary["description"],
        key="smart_action_primary",
    ):
        if "tab" in primary:
            st.session_state["intel_active_tab"] = primary["tab"]  # For Intelligence
            st.session_state["active_op_tab"] = primary["tab"]  # For Opérations
        st.switch_page("pages/{}.py".format(primary["page"]))

    # Show description
    st.caption(primary["description"])

    # Secondary actions (compact row)
    secondary = get_secondary_actions(state, primary["page"])

    if secondary:
        st.divider()
        cols = st.columns(len(secondary))
        for idx, action in enumerate(secondary):
            with cols[idx]:
                if st.button(
                    "{} {}".format(action["icon"], action["label"]),
                    use_container_width=True,
                    help=action["help"],
                    key=f"smart_action_secondary_{idx}",
                ):
                    if "tab" in action:
                        st.session_state["intel_active_tab"] = action["tab"]
                        st.session_state["active_op_tab"] = action["tab"]
                    st.switch_page("pages/{}.py".format(action["page"]))

    # Show progress summary
    if state["has_transactions"]:
        st.divider()

        # Mini progress indicators
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Transactions", value=state["tx_count"], label_visibility="visible")
        with col2:
            st.metric(label="Règles", value=state["rules_count"], label_visibility="visible")
        with col3:
            st.metric(label="Budgets", value=state["budgets_count"], label_visibility="visible")


def render_compact_tip():
    """
    Render a compact tip widget for sidebar use.
    Shows only the primary action + a random tip.
    """
    state = get_user_progress_state()
    primary = get_primary_action(state)

    # Show primary action
    btn_type = "primary" if primary["action_type"] == "primary" else "secondary"

    if st.button(
        "{} {}".format(primary["icon"], primary["label"]),
        type=btn_type,
        use_container_width=True,
        key="compact_smart_action",
    ):
        if "tab" in primary:
            st.session_state["intel_active_tab"] = primary["tab"]
            st.session_state["active_op_tab"] = primary["tab"]
        st.switch_page("pages/{}.py".format(primary["page"]))

    # Show mini stats
    if state["has_transactions"]:
        st.caption(
            "{} {} • {} {} • {} {}".format(
                state["tx_count"],
                "transactions",
                state["rules_count"],
                "règles",
                state["budgets_count"],
                "budgets",
            )
        )
