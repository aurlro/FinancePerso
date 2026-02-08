import streamlit as st
import pandas as pd
import re
from modules.categorization import predict_category_ai
from modules.db.rules import add_learning_rule
from modules.db.transactions import (
    get_pending_transactions,
    update_transaction_category,
    bulk_update_transaction_status,
)
from modules.db.members import get_members, update_transaction_member, get_member_mappings
from modules.db.categories import (
    get_categories,
    get_categories_with_emojis,
    get_categories_suggested_tags,
)
from modules.db.stats import get_all_account_labels
from modules.ui import show_success, toast_success, toast_warning
from modules.ui.feedback import validation_feedback, celebrate_all_done

# New modular components
from modules.ui.components.filters import render_transaction_filters
from modules.ui.components.progress_tracker import render_progress_tracker
from modules.ui.validation.grouping import get_smart_groups, calculate_group_stats
from modules.ui.validation.sorting import sort_groups, get_sort_options
from modules.ui.validation.row_view import render_validation_row


def validate_with_memory(
    tx_ids, label, category, remember, member_update=None, tags=None, beneficiary=None
):
    if remember:
        pattern = re.sub(r"(?i)CARTE|CB\*?\d*|\d{2}/\d{2}/\d{2}", "", label).strip()
        clean_pattern = re.sub(r"[^a-zA-Z\s]", "", pattern).strip().upper()
        clean_pattern = re.sub(r"\s+", " ", clean_pattern)
        if len(clean_pattern) > 2:
            add_learning_rule(clean_pattern, category)
    bulk_update_transaction_status(tx_ids, category, tags=tags, beneficiary=beneficiary)
    if member_update:
        for tx_id in tx_ids:
            update_transaction_member(tx_id, member_update)


def render_validation_tab():
    """Renders the Validation tab content."""

    st.header("✅ Validation des dépenses")

    # Load data
    df = get_pending_transactions()
    members_raw = get_members()
    all_members = members_raw["name"].tolist()

    if not all_members:
        all_members = ["Moi", "Conjoint", "Famille"]

    if df.empty:
        st.success("Toutes les transactions sont validées ! 🎉")
        return

    # Info box
    with st.expander("ℹ️ Aide à la validation", expanded=False):
        st.info(
            """
        **📝 Rappel :**
        - **📂 Catégorie** : Sélectionnez la catégorie appropriée
        - **👤 Qui a payé** : Indiquez le membre
        - **🏷️ Tags** : Seront ajoutés si vous utilisez les outils avancés
        """
        )

    # --- PROGRESS BAR ---
    render_progress_tracker(len(df), session_key="validation_progress")

    # Sorting controls
    col_sort1, col_sort2, col_sort3 = st.columns([2, 1, 1])
    with col_sort1:
        sort_options = get_sort_options()
        sort_choice = st.selectbox("Trier par", list(sort_options.keys()), key="sel_sort_val")
        sort_key = sort_options[sort_choice]

    with col_sort2:
        st.markdown(
            f"<p style='margin-top:28px; font-weight:600; color:#64748B;'>{len(df)} en attente</p>",
            unsafe_allow_html=True,
        )

    with col_sort3:
        if st.button("🔙 Annuler", help="Annuler la dernière action", use_container_width=True):
            from modules.data_manager import undo_last_action

            success, msg = undo_last_action()
            if success:
                toast_success(msg, icon="🔙")
                st.rerun()
            else:
                toast_warning(msg, icon="⚠️")

    st.divider()

    # Bulk Selection State
    if "bulk_selected_groups" not in st.session_state:
        st.session_state["bulk_selected_groups"] = set()

    # Components Data
    cat_emoji_map = get_categories_with_emojis()
    available_categories = sorted(list(cat_emoji_map.keys()))
    active_card_maps = get_member_mappings()

    @st.fragment
    def show_validation_list(
        filtered_df, available_categories, cat_emoji_map, sort_key, active_card_maps, key_suffix=""
    ):
        local_df = get_smart_groups(filtered_df, excluded_ids=set())
        group_stats = calculate_group_stats(local_df)
        display_groups = sort_groups(group_stats, sort_key=sort_key, max_groups=40)

        if len(group_stats) > 40:
            st.info(f"Affichage des 40 premiers groupes (sur {len(group_stats)}).")

        def handle_row_validation(row_id, category, member):
            target_group = next(
                (
                    g
                    for g in display_groups
                    if local_df[local_df["clean_group"] == g].iloc[0]["id"] == row_id
                ),
                None,
            )
            if not target_group:
                return

            g_df = local_df[local_df["clean_group"] == target_group]
            g_ids = g_df["id"].tolist()

            validate_with_memory(g_ids, g_df.iloc[0]["label"], category, True, member)
            validation_feedback(len(g_ids), "opération")
            st.rerun()

        for group_name in display_groups:
            group_df = local_df[local_df["clean_group"] == group_name]
            row = group_df.iloc[0]

            row_data = {
                "id": row["id"],
                "label": row["label"],
                "date": row["date"],
                "total_amount": group_df["amount"].sum(),
                "count": len(group_df),
                "category": row.get("category_validated") or row["original_category"],
                "member": row.get("member", ""),
            }

            if not row_data["member"] or row_data["member"] not in all_members:
                suffix = row.get("card_suffix")
                if suffix and suffix in active_card_maps:
                    row_data["member"] = active_card_maps[suffix]

            render_validation_row(
                row_data=row_data,
                all_members=all_members,
                all_categories=available_categories,
                cat_emoji_map=cat_emoji_map,
                on_validate=handle_row_validation,
                key_prefix=key_suffix,
            )

    tab_all, tab_unknown = st.tabs(["📋 Toutes", "🔍 Inconnues"])

    with tab_all:
        show_validation_list(
            df, available_categories, cat_emoji_map, sort_key, active_card_maps, key_suffix="_all"
        )

    with tab_unknown:
        unknown_mask = df["category_validated"].fillna("Inconnu") == "Inconnu"
        show_validation_list(
            df[unknown_mask],
            available_categories,
            cat_emoji_map,
            sort_key,
            active_card_maps,
            key_suffix="_unk",
        )
