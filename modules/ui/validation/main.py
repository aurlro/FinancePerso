import re

import streamlit as st

from modules.db.categories import (
    get_categories_with_emojis,
)
from modules.db.members import get_member_mappings, get_members, update_transaction_member
from modules.db.rules import add_learning_rule
from modules.db.transactions import (
    bulk_update_transaction_status,
    get_pending_transactions,
)
from modules.ui import toast_success, toast_warning

# New modular components
from modules.ui.components.pagination import paginated_list
from modules.ui.components.progress_tracker import render_progress_tracker
from modules.ui.feedback import validation_feedback
from modules.ui.validation.grouping import calculate_group_stats, get_smart_groups
from modules.ui.validation.row_view import render_validation_row
from modules.ui.validation.sorting import get_sort_options, sort_groups


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
            from modules.db.transactions import undo_last_action

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
        all_groups = sort_groups(group_stats, sort_key=sort_key, max_groups=None)
        
        # Pagination avec le composant réutilisable
        display_groups = paginated_list(
            all_groups, 
            page_size=20,  # 20 groupes par page
            key=f"validation_pagination{key_suffix}"
        )

        if len(all_groups) > 20:
            st.caption(f"Affichage de {len(display_groups)} groupe(s) sur {len(all_groups)} total.")

        # BULK VALIDATION - Header avec checkbox "Tout sélectionner"
        selected_in_session = st.session_state.get("bulk_selected_groups", set())
        all_group_names = set(display_groups)

        col_header, col_select_all = st.columns([6, 1])
        with col_header:
            if selected_in_session:
                st.write(f"**{len(selected_in_session)}** groupe(s) sélectionné(s)")
        with col_select_all:
            select_all = st.checkbox("Tout", key=f"select_all{key_suffix}")
            if select_all:
                st.session_state["bulk_selected_groups"] = all_group_names.copy()
            elif not select_all and selected_in_session == all_group_names:
                # Décocher tout si c'était tout sélectionné
                st.session_state["bulk_selected_groups"] = set()

        # Barre d'action groupée (sticky en haut)
        if selected_in_session:
            with st.container(border=True):
                st.write(f"🎯 **{len(selected_in_session)}** groupe(s) sélectionné(s)")
                cols = st.columns([2, 2, 1])

                with cols[0]:
                    bulk_category = st.selectbox(
                        "Catégorie", available_categories, key=f"bulk_cat{key_suffix}"
                    )
                with cols[1]:
                    bulk_member = st.selectbox("Membre", all_members, key=f"bulk_mem{key_suffix}")
                with cols[2]:
                    st.write("")
                    st.write("")
                    if st.button(
                        "✅ Valider tout",
                        type="primary",
                        use_container_width=True,
                        key=f"bulk_val{key_suffix}",
                    ):
                        # Valider tous les groupes sélectionnés
                        total_validated = 0
                        for group_name in selected_in_session:
                            if group_name in display_groups:
                                g_df = local_df[local_df["clean_group"] == group_name]
                                g_ids = g_df["id"].tolist()
                                validate_with_memory(
                                    g_ids, g_df.iloc[0]["label"], bulk_category, True, bulk_member
                                )
                                total_validated += len(g_ids)

                        validation_feedback(total_validated, "opération")
                        st.session_state["bulk_selected_groups"] = set()
                        st.rerun()

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

            # Checkbox pour sélection en masse
            is_selected = group_name in st.session_state.get("bulk_selected_groups", set())
            new_selected = st.checkbox(
                "",
                value=is_selected,
                key=f"chk{key_suffix}_{group_name}",
                label_visibility="collapsed",
            )

            if new_selected != is_selected:
                if new_selected:
                    st.session_state["bulk_selected_groups"].add(group_name)
                else:
                    st.session_state["bulk_selected_groups"].discard(group_name)
                st.rerun(scope="fragment")

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
