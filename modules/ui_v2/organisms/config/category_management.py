"""Category management UI component.

Provides UI for managing spending categories with emojis,
fixed flags, and suggested tags with merge capabilities.
"""

import streamlit as st

from modules.db.categories import (
    add_category,
    delete_category,
    get_categories,
    get_categories_df,
    merge_categories,
    update_category_emoji,
    update_category_fixed,
    update_category_suggested_tags,
)
from modules.impact_analyzer import analyze_category_merge_impact, render_impact_preview
from modules.ui_v2.atoms.icons import IconSet
from modules.ui_v2.molecules.banners import show_error, show_warning
from modules.ui_v2.molecules.toasts import toast_error, toast_info, toast_success, toast_warning


def render_category_management() -> None:
    """
    Render the Catégories tab content.
    Manage spending categories with emojis, fixed flags, and suggested tags.
    """
    st.header("Gestion des Catégories")
    st.markdown("Personnalisez les catégories de dépenses pour votre budget.")

    # List categories
    cats_df = get_categories_df()

    col_list_cat, col_add_cat = st.columns([1, 1])

    with col_list_cat:
        st.subheader("Catégories existantes")
        if cats_df.empty:
            st.info(f"{IconSet.INFO.value} Aucune catégorie configurée. Créez votre première catégorie à droite.")
        else:
            for index, row in cats_df.iterrows():
                with st.expander(
                    f"{row['emoji']} {row['name']} {' (Fixe)' if row['is_fixed'] else ''}",
                    expanded=False,
                ):
                    c1, c2 = st.columns([3, 1])
                    new_emoji = c1.text_input(
                        "Emoji", value=row["emoji"], key=f"emoji_val_{row['id']}"
                    )
                    is_fixed = c1.checkbox(
                        "Dépense Fixe (ex: Loyer, Abonnement)",
                        value=bool(row["is_fixed"]),
                        key=f"fixed_val_{row['id']}",
                    )

                    suggested_tags_val = (
                        row.get("suggested_tags", "") if row.get("suggested_tags") else ""
                    )
                    new_suggested_tags = c1.text_input(
                        "Tags suggérés (séparés par des virgules)",
                        value=suggested_tags_val,
                        key=f"tags_val_{row['id']}",
                    )

                    if c1.button(f"{IconSet.SAVE.value} Mettre à jour", key=f"upd_cat_{row['id']}"):
                        try:
                            # Track changes for detailed feedback
                            changes = []
                            if new_emoji != row["emoji"]:
                                changes.append(f"emoji {row['emoji']} → {new_emoji}")
                            if is_fixed != bool(row["is_fixed"]):
                                changes.append("type 'fixe'" if is_fixed else "type 'variable'")
                            if new_suggested_tags != suggested_tags_val:
                                changes.append("tags suggérés")

                            update_category_emoji(row["id"], new_emoji)
                            update_category_fixed(row["id"], int(is_fixed))
                            update_category_suggested_tags(row["id"], new_suggested_tags)

                            if changes:
                                change_str = ", ".join(changes)
                                toast_success(
                                    f"{IconSet.SUCCESS.value} '{row['name']}' mis à jour : {change_str}", icon=IconSet.SAVE.value
                                )
                            else:
                                toast_info(f"{IconSet.INFO.value} Aucun changement pour '{row['name']}'", icon=IconSet.INFO.value)

                            show_success(f"Catégorie '{row['name']}' mise à jour")
                            st.rerun()
                        except Exception as e:
                            error_msg = str(e)
                            if "UNIQUE constraint" in error_msg:
                                toast_error(
                                    f"{IconSet.ERROR.value} Impossible de modifier '{row['name']}' : conflit de données",
                                    icon=IconSet.WARNING.value,
                                )
                            elif "FOREIGN KEY" in error_msg:
                                toast_error(
                                    f"{IconSet.ERROR.value} Modification impossible : catégorie utilisée ailleurs",
                                    icon=IconSet.LINK.value,
                                )
                            else:
                                toast_error(
                                    f"{IconSet.ERROR.value} Erreur mise à jour de '{row['name']}' : {error_msg[:50]}",
                                    icon=IconSet.ERROR.value,
                                )

                    # Delete button with confirmation
                    if c2.button(f"{IconSet.DELETE.value} Supprimer", key=f"del_cat_{row['id']}"):
                        try:
                            delete_category(row["id"])
                            show_success(f"Catégorie '{row['name']}' supprimée")
                            toast_success(
                                f"{IconSet.DELETE.value} Catégorie '{row['name']}' supprimée avec succès", icon=IconSet.DELETE.value
                            )
                            st.rerun()
                        except Exception as e:
                            error_msg = str(e)
                            if "FOREIGN KEY" in error_msg:
                                show_error(f"Impossible de supprimer '{row['name']}'", icon=IconSet.LINK.value)
                                toast_error(
                                    f"{IconSet.ERROR.value} '{row['name']}' est utilisée par des transactions ou des règles. "
                                    "Utilisez la fusion pour réattribuer ses transactions.",
                                    icon=IconSet.LINK.value,
                                )
                            elif (
                                "not found" in error_msg.lower()
                                or "n'existe pas" in error_msg.lower()
                            ):
                                toast_warning(
                                    f"{IconSet.WARNING.value} La catégorie '{row['name']}' n'existe plus", icon=IconSet.WARNING.value
                                )
                                st.rerun()
                            else:
                                toast_error(
                                    f"{IconSet.ERROR.value} Erreur suppression '{row['name']}' : {error_msg[:50]}",
                                    icon=IconSet.ERROR.value,
                                )

    with col_add_cat:
        st.subheader(f"{IconSet.ADD.value} Ajouter une catégorie")
        with st.form("add_cat_form"):
            col_a1, col_a2, col_a3 = st.columns([3, 1, 1])
            new_cat_name = col_a1.text_input(
                "Nom de la catégorie",
                placeholder="Ex: Enfants, Sport...",
                help="Nom unique de la catégorie",
            )
            new_cat_emoji = col_a2.text_input("Emoji", value=IconSet.TAG.value, help="Emoji représentatif")
            new_is_fixed = col_a3.checkbox("Fixe", value=False, help="Dépense régulière ?")

            submitted = st.form_submit_button(f"{IconSet.ADD.value} Ajouter", use_container_width=True)
            if submitted:
                if not new_cat_name or not new_cat_name.strip():
                    toast_warning(f"{IconSet.WARNING.value} Veuillez entrer un nom de catégorie", icon=IconSet.EDIT.value)
                elif len(new_cat_name.strip()) < 2:
                    toast_warning(f"{IconSet.WARNING.value} Le nom doit contenir au moins 2 caractères", icon=IconSet.INFO.value)
                else:
                    cat_name = new_cat_name.strip()
                    try:
                        if add_category(cat_name, new_cat_emoji, int(new_is_fixed)):
                            type_label = "dépense fixe" if new_is_fixed else "dépense variable"
                            toast_success(
                                f"{IconSet.SUCCESS.value} Catégorie créée : {new_cat_emoji} '{cat_name}' ({type_label})",
                                icon=IconSet.TROPHY.value,
                            )
                            show_success(f"Catégorie '{cat_name}' créée")
                            st.rerun()
                        else:
                            show_warning(f"La catégorie '{cat_name}' existe déjà", icon=IconSet.WARNING.value)
                            toast_error(
                                f"{IconSet.ERROR.value} '{cat_name}' existe déjà. Choisissez un autre nom ou fusionnez les catégories.",
                                icon=IconSet.DELETE.value,
                            )
                    except Exception as e:
                        error_msg = str(e)
                        if "UNIQUE constraint" in error_msg:
                            toast_error(f"{IconSet.ERROR.value} La catégorie '{cat_name}' existe déjà", icon=IconSet.DELETE.value)
                        else:
                            toast_error(f"{IconSet.ERROR.value} Erreur création : {error_msg[:50]}", icon=IconSet.ERROR.value)

    # --- CATEGORY MERGE SECTION ---
    st.divider()
    st.subheader(f"{IconSet.REFRESH.value} Fusionner des catégories")
    st.info(
        "Transférez toutes les transactions d'une catégorie vers une autre. La catégorie source sera supprimée."
    )

    all_cats = get_categories()
    if len(all_cats) < 2:
        st.warning(f"{IconSet.WARNING.value} Il faut au moins 2 catégories pour effectuer une fusion.", icon=IconSet.WARNING.value)
    else:
        col_m1, col_m2, col_m3 = st.columns([2, 2, 1])

        with col_m1:
            source_cat = st.selectbox(
                "Catégorie source (sera supprimée)",
                all_cats,
                key="merge_source",
                help="Toutes ses transactions seront transférées, puis elle sera supprimée",
            )

        with col_m2:
            target_options = [c for c in all_cats if c != source_cat]
            target_cat = st.selectbox(
                "Catégorie cible (reçoit les transactions)",
                target_options,
                key="merge_target",
                help="Cette catégorie recevra toutes les transactions",
            )

        # Preview impact
        if source_cat and target_cat:
            impact = analyze_category_merge_impact(source_cat, target_cat)
            render_impact_preview("category_merge", impact)

        with col_m3:
            st.markdown("<div style='height: 1.6rem;'></div>", unsafe_allow_html=True)
            if st.button(
                f"{IconSet.REFRESH.value} Fusionner", type="primary", use_container_width=True, key="category_button_187"
            ):
                if not source_cat or not target_cat:
                    toast_warning(f"{IconSet.WARNING.value} Veuillez sélectionner les deux catégories", icon=IconSet.WARNING.value)
                elif source_cat == target_cat:
                    show_warning("Veuillez sélectionner deux catégories différentes", icon=IconSet.WARNING.value)
                    toast_error(f"{IconSet.ERROR.value} La source et la cible doivent être différentes", icon=IconSet.DELETE.value)
                else:
                    try:
                        with st.spinner(f"{IconSet.REFRESH.value} Fusion en cours : '{source_cat}' → '{target_cat}'..."):
                            result = merge_categories(source_cat, target_cat)

                        tx_count = result.get("transactions", 0)
                        rules_count = result.get("rules", 0)
                        budget_transferred = result.get("budgets_transferred", False)
                        category_deleted = result.get("category_deleted", False)

                        # Build detailed success message
                        messages = []
                        if tx_count > 0:
                            messages.append(f"• {tx_count} transaction(s) transférée(s)")
                        elif tx_count == 0:
                            messages.append("• Aucune transaction à transférer")

                        if rules_count > 0:
                            messages.append(
                                f"• {rules_count} règle(s) de catégorisation mise(s) à jour"
                            )

                        if budget_transferred:
                            messages.append("• 💰 Budget transféré")

                        if category_deleted:
                            messages.append(f"• {IconSet.DELETE.value} Catégorie '{source_cat}' supprimée")

                        success_msg = "\n".join(messages) if messages else "Fusion terminée"

                        # Toast with summary
                        toast_success(
                            f"{IconSet.SUCCESS.value} '{source_cat}' fusionnée avec '{target_cat}'\n{success_msg}",
                            icon=IconSet.REFRESH.value,
                        )

                        # Detailed success banner
                        with st.container(border=True):
                            st.markdown(f"**{IconSet.REFRESH.value} Fusion réussie**")
                            st.markdown(f"**'{source_cat}'** → **'{target_cat}'**")
                            if tx_count > 0:
                                st.markdown(f"{IconSet.SUCCESS.value} {tx_count} transaction(s) réattribuée(s)")
                            if rules_count > 0:
                                st.markdown(f"{IconSet.FILE.value} {rules_count} règle(s) mise(s) à jour")
                            if budget_transferred:
                                st.markdown(f"{IconSet.MONEY.value} Budget ajouté à '{target_cat}'")
                            if category_deleted:
                                st.caption(f"{IconSet.DELETE.value} La catégorie '{source_cat}' n'existe plus")

                        st.rerun()

                    except ValueError as e:
                        error_msg = str(e)
                        show_error(f"Fusion impossible : {error_msg}", icon=IconSet.DELETE.value)
                        toast_error(f"{IconSet.ERROR.value} {error_msg}", icon=IconSet.DELETE.value)
                    except Exception as e:
                        error_msg = str(e)
                        if "not found" in error_msg.lower() or "n'existe pas" in error_msg.lower():
                            toast_error(
                                f"{IconSet.ERROR.value} Une des catégories n'existe plus : {error_msg}", icon=IconSet.WARNING.value
                            )
                        elif "database" in error_msg.lower():
                            show_error("Erreur base de données lors de la fusion", icon=IconSet.SAVE.value)
                            toast_error(f"{IconSet.ERROR.value} Problème de base de données. Réessayez.", icon=IconSet.SAVE.value)
                        else:
                            show_error(f"Impossible de fusionner : {error_msg}", icon=IconSet.ERROR.value)
                            toast_error(f"{IconSet.ERROR.value} Échec de la fusion : {error_msg[:80]}", icon=IconSet.ERROR.value)
