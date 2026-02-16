"""
Rule Manager UI Component.

Handles CRUD operations for learning rules with search, filter, and pagination.
Uses Streamlit fragments for performance optimization.
"""

from datetime import datetime

import pandas as pd
import streamlit as st

from modules.db.categories import get_categories
from modules.db.rules import add_learning_rule, delete_learning_rule, get_learning_rules
from modules.logger import logger
from modules.ui.feedback import (
    show_error,
    show_info,
    show_success,
    show_warning,
    toast_error,
    toast_success,
    toast_warning,
)
from modules.utils import validate_regex_pattern


def invalidate_rules_cache():
    """Invalidate all rules-related session state caches."""
    keys_to_clear = [
        "quick_audit_score",
        "audit_results",
        "rules_cache_hash",
        "filtered_rules_cache",
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


@st.cache_data(ttl=300)
def _get_cached_rules() -> pd.DataFrame:
    """Cached wrapper for get_learning_rules."""
    return get_learning_rules()


@st.cache_data(ttl=300)
def _get_cached_categories() -> list:
    """Cached wrapper for get_categories."""
    return get_categories()


def _get_rules_hash(rules_df: pd.DataFrame) -> str:
    """Generate a hash for rules DataFrame to detect changes."""
    if rules_df.empty:
        return "empty"
    return f"{len(rules_df)}_{rules_df['id'].sum()}_{rules_df['created_at'].max()}"


def _filter_rules(
    rules_df: pd.DataFrame, search_query: str = "", category_filter: list = None
) -> pd.DataFrame:
    """Filter rules based on search query and category selection."""
    if rules_df.empty:
        return rules_df

    filtered = rules_df.copy()

    # Apply search filter
    if search_query:
        search_lower = search_query.lower()
        filtered = filtered[
            filtered["pattern"].str.lower().str.contains(search_lower, na=False)
            | filtered["category"].str.lower().str.contains(search_lower, na=False)
        ]

    # Apply category filter
    if category_filter:
        filtered = filtered[filtered["category"].isin(category_filter)]

    return filtered


@st.fragment
def render_rule_list():
    """
    Render the list of learning rules with search, filter, and pagination.

    This is a Streamlit fragment - deleting a rule will only re-render this section,
    not the entire page.
    """
    # Load cached data
    rules_df = _get_cached_rules()
    categories = _get_cached_categories()

    if rules_df.empty:
        show_info(
            "Aucune règle apprise pour le moment. Ajoutez-en une ci-dessus ou cochez 'Mém.' lors de la validation !",
            icon="📭",
        )
        return

    # Header with count
    col_header, col_spacer = st.columns([1, 2])
    with col_header:
        st.markdown(f"**{len(rules_df)}** règles actives")

    st.divider()

    # Search and filter section
    col_search, col_filter = st.columns([2, 1])

    with col_search:
        search_query = st.text_input(
            "🔍 Rechercher", placeholder="Mot-clé, pattern ou catégorie...", key="rule_search_query"
        )

    with col_filter:
        selected_categories = st.multiselect(
            "Filtrer par catégorie", options=categories, default=[], key="rule_category_filter"
        )

    # Filter rules
    filtered_rules = _filter_rules(rules_df, search_query, selected_categories)

    if filtered_rules.empty:
        show_warning("Aucune règle ne correspond aux critères de recherche", icon="🔍")
        return

    # Pagination
    items_per_page = 10
    total_pages = max(1, (len(filtered_rules) + items_per_page - 1) // items_per_page)

    col_info, col_pagination = st.columns([2, 1])
    with col_info:
        st.caption(f"{len(filtered_rules)} règle(s) affichée(s)")

    with col_pagination:
        if total_pages > 1:
            current_page = st.number_input(
                "Page", min_value=1, max_value=total_pages, value=1, key="rule_list_page"
            )
        else:
            current_page = 1

    # Calculate slice for current page
    start_idx = (current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(filtered_rules))
    page_rules = filtered_rules.iloc[start_idx:end_idx]

    # Render rules table header
    cols_header = st.columns([3, 2, 2, 1])
    with cols_header[0]:
        st.markdown("**Pattern**")
    with cols_header[1]:
        st.markdown("**Catégorie**")
    with cols_header[2]:
        st.markdown("**Créé le**")
    with cols_header[3]:
        st.markdown("**Action**")

    st.divider()

    # Render each rule
    for _, row in page_rules.iterrows():
        cols = st.columns([3, 2, 2, 1])

        with cols[0]:
            st.code(row["pattern"], language="text")
        with cols[1]:
            st.markdown(f"**{row['category']}**")
        with cols[2]:
            created_at = row["created_at"]
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    st.caption(created_at.strftime("%d/%m/%Y"))
                except (ValueError, TypeError):
                    st.caption(str(created_at)[:10])
            else:
                st.caption(str(created_at)[:10] if created_at else "-")
        with cols[3]:
            delete_key = f"del_rule_{row['id']}"
            if st.button("🗑️", key=delete_key, help="Supprimer cette règle"):
                try:
                    if delete_learning_rule(row["id"]):
                        pattern_preview = (
                            row["pattern"][:30] + "..."
                            if len(row["pattern"]) > 30
                            else row["pattern"]
                        )
                        toast_success(f"Règle '{pattern_preview}' supprimée", icon="🗑️")
                        invalidate_rules_cache()
                        _get_cached_rules.clear()
                        st.rerun(scope="fragment")
                    else:
                        toast_error("Erreur lors de la suppression", icon="❌")
                except Exception as e:
                    logger.error(f"Error deleting rule {row['id']}: {e}")
                    toast_error(f"Erreur: {e}", icon="❌")
                    show_error(f"Impossible de supprimer la règle: {e}")

    # Page indicator
    if total_pages > 1:
        st.caption(f"Page {current_page} sur {total_pages}")


@st.fragment
def render_add_rule_form():
    """
    Render the form to add a new learning rule.

    This is a Streamlit fragment - adding a rule will only re-render this section
    and invalidate the rules list cache.
    """
    categories = _get_cached_categories()

    with st.expander("➕ Ajouter une nouvelle règle", expanded=False):
        with st.form("add_rule_form"):
            col_pat, col_cat = st.columns([3, 2])

            with col_pat:
                new_pattern = st.text_input(
                    "Mot-clé ou Pattern (Regex)",
                    placeholder="Ex: UBER ou ^UBER.*TRIP",
                    help="Peut être un simple mot-clé ou une expression régulière",
                )

            with col_cat:
                new_category = st.selectbox(
                    "Catégorie cible",
                    options=categories,
                    help="La catégorie qui sera assignée aux transactions correspondantes",
                )

            # Pattern tester
            if new_pattern:
                is_valid, error_msg = validate_regex_pattern(new_pattern)
                if is_valid:
                    st.success("✅ Pattern valide")
                else:
                    st.error(f"❌ {error_msg}")

            submitted = st.form_submit_button("Ajouter la règle", type="primary")

            if submitted:
                if not new_pattern or not new_pattern.strip():
                    toast_warning("Veuillez remplir le pattern", icon="⚠️")
                    return

                if not new_category:
                    toast_warning("Veuillez sélectionner une catégorie", icon="⚠️")
                    return

                # Validate regex pattern
                is_valid, error_msg = validate_regex_pattern(new_pattern)
                if not is_valid:
                    toast_error(f"Pattern invalide: {error_msg}", icon="❌")
                    show_error(f"Pattern invalide: {error_msg}")
                    show_info(
                        "💡 Le pattern peut être un simple mot-clé (ex: UBER) ou une expression régulière (ex: ^UBER.*TRIP)"
                    )
                    return

                try:
                    if add_learning_rule(new_pattern.strip(), new_category):
                        pattern_preview = (
                            new_pattern[:30] + "..." if len(new_pattern) > 30 else new_pattern
                        )
                        toast_success(
                            f"Règle '{pattern_preview}' → '{new_category}' ajoutée !", icon="✅"
                        )
                        show_success("Règle créée avec succès")
                        invalidate_rules_cache()
                        _get_cached_rules.clear()
                        st.rerun(scope="fragment")
                    else:
                        toast_error(
                            "Erreur lors de l'ajout (peut-être que ce pattern existe déjà ?)",
                            icon="❌",
                        )
                        show_warning("Cette règle existe peut-être déjà")
                except Exception as e:
                    logger.error(f"Error adding rule: {e}")
                    toast_error(f"Erreur lors de l'ajout: {e}", icon="❌")
                    show_error(f"Impossible d'ajouter la règle: {e}")
