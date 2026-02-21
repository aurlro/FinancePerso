"""Member management UI component.

Provides UI for managing household members, external entities,
and card-to-member mappings with impact analysis.
"""

from typing import Optional

import streamlit as st

from modules.db.members import (
    add_account_member_mapping,
    add_member,
    add_member_mapping,
    analyze_unknown_patterns,
    delete_account_member_mapping,
    delete_member,
    delete_member_mapping,
    ensure_no_unknown_members,
    get_account_member_mappings_df,
    get_member_mappings_df,
    get_members,
    get_unknown_member_stats,
    rename_member,
    repair_unknown_members,
    update_member_type,
)
from modules.db.settings import (
    get_default_member,
    get_force_member_identification,
    set_default_member,
    set_force_member_identification,
)
from modules.impact_analyzer import analyze_member_rename_impact, render_impact_preview
from modules.ui_v2.atoms.icons import IconSet
from modules.ui_v2.molecules.banners import show_error, show_success, show_warning
from modules.ui_v2.molecules.toasts import toast_error, toast_info, toast_success, toast_warning

# Initialisation des variables de session
if "pending_rename" not in st.session_state:
    st.session_state["pending_rename"] = None
if "editing_member_id" not in st.session_state:
    st.session_state["editing_member_id"] = None


def render_member_management() -> None:
    """
    Render the Foyer & Membres tab content.
    Manage household members, external entities, and card-to-member mappings.
    """
    st.header(f"{IconSet.USERS.value} Membres du Foyer")
    st.markdown("Définissez les personnes associées à ce compte pour l'attribution des dépenses.")

    # Handle pending rename with impact preview
    pending: Optional[dict] = st.session_state.get("pending_rename")
    if pending is not None:
        with st.container(border=True):
            st.warning(f"{IconSet.WARNING.value} Confirmer le renommage ?")
            render_impact_preview("member_rename", pending["impact"])

            col_confirm, col_cancel = st.columns([1, 1])
            with col_confirm:
                if st.button(
                    f"{IconSet.USER.value} Confirmer le nouveau nom",
                    type="primary",
                    use_container_width=True,
                    key="member_button_38",
                ):
                    try:
                        rename_member(pending["old_name"], pending["new_name"])
                        del st.session_state["pending_rename"]
                        st.session_state["editing_member_id"] = None

                        affected = pending["impact"].get("total_affected", 0)
                        if affected > 0:
                            toast_success(
                                f"{IconSet.SUCCESS.value} '{pending['old_name']}' renommé en '{pending['new_name']}' ({affected} transaction(s) mise(s) à jour)",
                                icon=IconSet.USER.value,
                            )
                        else:
                            toast_success(
                                f"{IconSet.SUCCESS.value} '{pending['old_name']}' renommé en '{pending['new_name']}'",
                                icon=IconSet.USER.value,
                            )
                        show_success(
                            f"Membre '{pending['old_name']}' mis à jour"
                        )
                        st.rerun()
                    except Exception as e:
                        error_msg = str(e)
                        if "existe déjà" in error_msg.lower() or "already" in error_msg.lower():
                            toast_error(
                                f"{IconSet.ERROR.value} Le nom '{pending['new_name']}' est déjà utilisé",
                                icon=IconSet.DELETE.value,
                            )
                        elif "not found" in error_msg.lower():
                            toast_error(
                                f"{IconSet.ERROR.value} Le membre '{pending['old_name']}' n'existe plus",
                                icon=IconSet.WARNING.value,
                            )
                        else:
                            toast_error(
                                f"{IconSet.ERROR.value} Erreur lors du renommage : {error_msg[:50]}",
                                icon=IconSet.ERROR.value,
                            )
            with col_cancel:
                if st.button(
                    f"{IconSet.CANCEL.value} Annuler",
                    use_container_width=True,
                    key="member_button_66"
                ):
                    del st.session_state["pending_rename"]
                    toast_info("Renommage annulé", icon=IconSet.DELETE.value)
                    st.rerun()
        st.divider()

    members_df = get_members()

    col_list, col_add = st.columns([1, 1])

    with col_list:
        if members_df.empty:
            st.info(f"{IconSet.INFO.value} Aucun membre configuré. Ajoutez votre premier membre à droite.")
        else:
            if "editing_member_id" not in st.session_state:
                st.session_state["editing_member_id"] = None

            # --- HOUSEHOLD GROUP ---
            foyer_df = members_df[members_df["member_type"] == "HOUSEHOLD"]
            st.subheader(f"{IconSet.HOME_CAT.value} Membres du Foyer")
            if foyer_df.empty:
                st.caption("Aucun membre du foyer.")
            else:
                for index, row in foyer_df.iterrows():
                    member_id, member_name = row["id"], row["name"]
                    if st.session_state["editing_member_id"] == member_id:
                        c1, c2, c3 = st.columns([3, 0.5, 0.5])
                        with c1:
                            new_name = st.text_input(
                                "Nom",
                                value=member_name,
                                key=f"edit_in_{member_id}",
                                label_visibility="collapsed",
                            )
                        with c2:
                            if st.button(IconSet.SUCCESS.value, key=f"sv_{member_id}", help="Sauvegarder"):
                                if new_name and new_name.strip():
                                    cleaned_name = new_name.strip()
                                    if cleaned_name != member_name:
                                        # Analyze impact first
                                        impact = analyze_member_rename_impact(
                                            member_name, cleaned_name
                                        )
                                        if impact["total_affected"] > 0:
                                            st.session_state["pending_rename"] = {
                                                "old_name": member_name,
                                                "new_name": cleaned_name,
                                                "impact": impact,
                                            }
                                            st.rerun()
                                        else:
                                            # No impact, proceed directly
                                            try:
                                                rename_member(member_name, cleaned_name)
                                                st.session_state["editing_member_id"] = None
                                                toast_success(
                                                    f"{IconSet.SUCCESS.value} Membre renommé : '{member_name}' → '{cleaned_name}'",
                                                    icon=IconSet.USER.value,
                                                )
                                                st.rerun()
                                            except Exception as e:
                                                toast_error(f"{IconSet.ERROR.value} Erreur : {str(e)[:50]}", icon=IconSet.ERROR.value)
                                    else:
                                        toast_info(f"{IconSet.INFO.value} Aucun changement", icon=IconSet.INFO.value)
                                else:
                                    toast_warning(f"{IconSet.WARNING.value} Le nom ne peut pas être vide", icon=IconSet.WARNING.value)
                        with c3:
                            if st.button(IconSet.CANCEL.value, key=f"cl_{member_id}", help="Annuler"):
                                st.session_state["editing_member_id"] = None
                                st.rerun()
                    else:
                        c1, c2, c3, c4 = st.columns([3, 1, 0.5, 0.5])
                        c1.write(f"{IconSet.USER.value} **{member_name}**")
                        if c2.button(
                            "➡️ Passer en Tiers",
                            key=f"to_ext_{member_id}",
                            help="Déplacer vers Tiers",
                        ):
                            try:
                                update_member_type(member_id, "EXTERNAL")
                                toast_success(f"{IconSet.SUCCESS.value} '{member_name}' déplacé vers Tiers", icon=IconSet.CREDIT_CARD.value)
                                st.rerun()
                            except Exception as e:
                                toast_error(
                                    f"{IconSet.ERROR.value} Impossible de déplacer '{member_name}' : {str(e)[:50]}",
                                    icon=IconSet.ERROR.value,
                                )
                        if c3.button(IconSet.EDIT.value, key=f"ed_{member_id}", help="Renommer"):
                            st.session_state["editing_member_id"] = member_id
                            st.rerun()
                        if c4.button(IconSet.DELETE.value, key=f"del_{member_id}", help="Supprimer"):
                            try:
                                delete_member(member_id)
                                show_success(f"Membre '{member_name}' supprimé")
                                toast_success(f"{IconSet.DELETE.value} Membre '{member_name}' supprimé", icon=IconSet.DELETE.value)
                                st.rerun()
                            except Exception as e:
                                error_msg = str(e)
                                if "FOREIGN KEY" in error_msg or "utilisé" in error_msg.lower():
                                    show_error(
                                        f"Impossible de supprimer '{member_name}'", icon=IconSet.LINK.value
                                    )
                                    toast_error(
                                        f"{IconSet.ERROR.value} '{member_name}' est utilisé dans des transactions ou des cartes. "
                                        "Supprimez d'abord ces associations.",
                                        icon=IconSet.LINK.value,
                                    )
                                else:
                                    toast_error(
                                        f"{IconSet.ERROR.value} Erreur suppression : {error_msg[:50]}", icon=IconSet.ERROR.value
                                    )

            # --- EXTERNAL GROUP ---
            ext_df = members_df[members_df["member_type"] == "EXTERNAL"]
            st.subheader(f"{IconSet.CREDIT_CARD.value} Tiers (Externe)")
            if ext_df.empty:
                st.caption("Aucun tiers externe.")
            else:
                for index, row in ext_df.iterrows():
                    member_id, member_name = row["id"], row["name"]
                    if st.session_state["editing_member_id"] == member_id:
                        c1, c2, c3 = st.columns([3, 0.5, 0.5])
                        with c1:
                            edit_name = st.text_input(
                                "Nom",
                                value=member_name,
                                key=f"edit_in_{member_id}",
                                label_visibility="collapsed",
                            )
                        with c2:
                            if st.button(IconSet.SUCCESS.value, key=f"sv_{member_id}", help="Sauvegarder"):
                                if edit_name and edit_name.strip():
                                    cleaned_name = edit_name.strip()
                                    if cleaned_name != member_name:
                                        try:
                                            rename_member(member_name, cleaned_name)
                                            st.session_state["editing_member_id"] = None
                                            toast_success(
                                                f"{IconSet.SUCCESS.value} Membre renommé : '{member_name}' → '{cleaned_name}'",
                                                icon=IconSet.USER.value,
                                            )
                                            st.rerun()
                                        except Exception as e:
                                            toast_error(f"{IconSet.ERROR.value} Erreur : {str(e)[:50]}", icon=IconSet.ERROR.value)
                                    else:
                                        toast_info(f"{IconSet.INFO.value} Aucun changement", icon=IconSet.INFO.value)
                                else:
                                    toast_warning(f"{IconSet.WARNING.value} Le nom ne peut pas être vide", icon=IconSet.WARNING.value)
                        with c3:
                            if st.button(IconSet.CANCEL.value, key=f"cl_{member_id}", help="Annuler"):
                                st.session_state["editing_member_id"] = None
                                st.rerun()
                    else:
                        c1, c2, c3, c4 = st.columns([3, 1, 0.5, 0.5])
                        c1.write(f"{IconSet.CREDIT_CARD.value} **{member_name}**")
                        if c2.button(
                            "⬅️ Passer au Foyer",
                            key=f"to_hh_{member_id}",
                            help="Déplacer vers Foyer",
                        ):
                            try:
                                update_member_type(member_id, "HOUSEHOLD")
                                toast_success(f"{IconSet.SUCCESS.value} '{member_name}' déplacé vers Foyer", icon=IconSet.HOME_CAT.value)
                                st.rerun()
                            except Exception as e:
                                toast_error(
                                    f"{IconSet.ERROR.value} Impossible de déplacer '{member_name}' : {str(e)[:50]}",
                                    icon=IconSet.ERROR.value,
                                )
                        if c3.button(IconSet.EDIT.value, key=f"ed_{member_id}", help="Renommer"):
                            st.session_state["editing_member_id"] = member_id
                            st.rerun()
                        if c4.button(IconSet.DELETE.value, key=f"del_{member_id}", help="Supprimer"):
                            try:
                                delete_member(member_id)
                                toast_success(f"{IconSet.DELETE.value} Membre '{member_name}' supprimé", icon=IconSet.DELETE.value)
                                st.rerun()
                            except Exception as e:
                                error_msg = str(e)
                                if "FOREIGN KEY" in error_msg or "utilisé" in error_msg.lower():
                                    show_error(
                                        f"Impossible de supprimer '{member_name}'", icon=IconSet.LINK.value
                                    )
                                    toast_error(
                                        f"{IconSet.ERROR.value} '{member_name}' est utilisé dans des transactions ou des cartes",
                                        icon=IconSet.LINK.value,
                                    )
                                else:
                                    toast_error(
                                        f"{IconSet.ERROR.value} Erreur suppression : {error_msg[:50]}", icon=IconSet.ERROR.value
                                    )

    with col_add:
        st.subheader(f"{IconSet.ADD.value} Ajouter un membre")
        with st.form("add_member_form"):
            new_name = st.text_input(
                "Nom", placeholder="Ex: Jean, Marie...", help="Nom unique du membre"
            )
            new_type = st.radio(
                "Type",
                ["HOUSEHOLD", "EXTERNAL"],
                format_func=lambda x: f"{IconSet.HOME_CAT.value} Foyer" if x == "HOUSEHOLD" else f"{IconSet.CREDIT_CARD.value} Tiers",
                help="Foyer = membre du budget, Tiers = externe (ex: crèche, impôts)",
            )

            submitted = st.form_submit_button(f"{IconSet.ADD.value} Ajouter", use_container_width=True)
            if submitted:
                if not new_name or not new_name.strip():
                    toast_warning(f"{IconSet.WARNING.value} Veuillez entrer un nom", icon=IconSet.EDIT.value)
                elif len(new_name.strip()) < 2:
                    toast_warning(f"{IconSet.WARNING.value} Le nom doit contenir au moins 2 caractères", icon=IconSet.INFO.value)
                else:
                    cleaned_name = new_name.strip()
                    try:
                        if add_member(cleaned_name, new_type):
                            member_type_label = "Foyer" if new_type == "HOUSEHOLD" else "Tiers"
                            toast_success(
                                f"{IconSet.SUCCESS.value} Membre créé : '{cleaned_name}' ({member_type_label})",
                                icon=IconSet.TROPHY.value,
                            )
                            show_success(f"Membre '{cleaned_name}' créé")
                            st.rerun()
                        else:
                            show_warning(f"Le membre '{cleaned_name}' existe déjà", icon=IconSet.WARNING.value)
                            toast_error(
                                f"{IconSet.ERROR.value} '{cleaned_name}' existe déjà. Choisissez un nom différent.",
                                icon=IconSet.DELETE.value,
                            )
                    except Exception as e:
                        error_msg = str(e)
                        if "existe déjà" in error_msg.lower() or "already" in error_msg.lower():
                            toast_error(f"{IconSet.ERROR.value} Le membre '{cleaned_name}' existe déjà", icon=IconSet.DELETE.value)
                        else:
                            toast_error(f"{IconSet.ERROR.value} Erreur création : {error_msg[:50]}", icon=IconSet.ERROR.value)

    # --- CARD MAPPINGS ---
    st.divider()
    st.subheader(f"{IconSet.CREDIT_CARD.value} Correspondances Cartes → Membres")
    st.markdown("Associez automatiquement une carte bancaire (4 derniers chiffres) à un membre.")

    if members_df.empty:
        st.warning(f"{IconSet.WARNING.value} Ajoutez d'abord des membres pour configurer les correspondances.", icon=IconSet.WARNING.value)
        return

    mapping_df = get_member_mappings_df()

    col_m1, col_m2 = st.columns([1, 1])
    with col_m1:
        if mapping_df.empty:
            st.info(f"{IconSet.INFO.value} Aucune correspondance configurée.")
        else:
            st.caption(f"{len(mapping_df)} carte(s) configurée(s)")
            for index, row in mapping_df.iterrows():
                cm1, cm2 = st.columns([3, 1])
                cm1.write(f"{IconSet.CREDIT_CARD.value} **...{row['card_suffix']}** ➔ {IconSet.USER.value} {row['member_name']}")
                if cm2.button(IconSet.DELETE.value, key=f"del_map_{row['id']}", help="Supprimer la correspondance"):
                    try:
                        delete_member_mapping(row["id"])
                        toast_success(
                            f"{IconSet.DELETE.value} Carte ...{row['card_suffix']} dissociée de {row['member_name']}",
                            icon=IconSet.DELETE.value,
                        )
                        st.rerun()
                    except Exception as e:
                        toast_error(f"{IconSet.ERROR.value} Erreur : {str(e)[:50]}", icon=IconSet.ERROR.value)

    with col_m2:
        with st.form("add_mapping_form"):
            suffix = st.text_input(
                "4 derniers chiffres",
                placeholder="Ex: 6759",
                help="Les 4 derniers chiffres de la carte bancaire",
            )
            m_name = st.selectbox(
                "Membre",
                members_df["name"].tolist() if not members_df.empty else ["Anonyme"],
                help="Membre associé à cette carte",
            )

            submitted = st.form_submit_button(f"{IconSet.ADD.value} Ajouter la carte", use_container_width=True)
            if submitted:
                if not suffix or not suffix.strip():
                    toast_warning(f"{IconSet.WARNING.value} Veuillez entrer les 4 derniers chiffres", icon=IconSet.CREDIT_CARD.value)
                elif not m_name:
                    toast_warning(f"{IconSet.WARNING.value} Veuillez sélectionner un membre", icon=IconSet.USER.value)
                elif len(suffix.strip()) != 4 or not suffix.strip().isdigit():
                    toast_warning(f"{IconSet.WARNING.value} Le suffixe doit être exactement 4 chiffres", icon=IconSet.INFO.value)
                else:
                    clean_suffix = suffix.strip()
                    try:
                        add_member_mapping(clean_suffix, m_name)
                        toast_success(f"{IconSet.SUCCESS.value} Carte ...{clean_suffix} associée à {m_name}", icon=IconSet.CREDIT_CARD.value)
                        show_success(f"Carte '...{clean_suffix}' associée à {m_name}")
                        st.rerun()
                    except Exception as e:
                        error_msg = str(e)
                        if "existe déjà" in error_msg.lower() or "already" in error_msg.lower():
                            toast_error(
                                f"{IconSet.ERROR.value} La carte ...{clean_suffix} est déjà associée", icon=IconSet.DELETE.value
                            )
                        else:
                            toast_error(f"{IconSet.ERROR.value} Erreur : {error_msg[:50]}", icon=IconSet.ERROR.value)

    # --- ACCOUNT MAPPINGS ---
    st.divider()
    st.subheader(f"{IconSet.BANK.value} Correspondances Comptes → Membres")
    st.markdown(
        "Définissez un membre par défaut pour toutes les transactions d'un compte spécifique (ex: votre compte personnel)."
    )

    acc_mapping_df = get_account_member_mappings_df()

    col_a1, col_a2 = st.columns([1, 1])
    with col_a1:
        if acc_mapping_df.empty:
            st.info(f"{IconSet.INFO.value} Aucune correspondance par compte.")
        else:
            for index, row in acc_mapping_df.iterrows():
                ca1, ca2 = st.columns([3, 1])
                ca1.write(f"{IconSet.BANK.value} **{row['account_label']}** ➔ {IconSet.USER.value} {row['member_name']}")
                if ca2.button(IconSet.DELETE.value, key=f"del_acc_map_{row['id']}", help="Supprimer cette règle"):
                    delete_account_member_mapping(row["id"])
                    toast_success(f"{IconSet.DELETE.value} Règle supprimée pour {row['account_label']}", icon=IconSet.DELETE.value)
                    st.rerun()

    with col_a2:
        with st.form("add_acc_mapping_form"):
            # Fetch existing account labels to help
            from modules.db.transactions import get_all_transactions

            df_temp = get_all_transactions(limit=1000)
            acc_list = (
                sorted(df_temp["account_label"].dropna().unique().tolist())
                if not df_temp.empty
                else []
            )

            acc_label = st.selectbox(
                "Libellé du compte",
                options=[""] + acc_list if acc_list else [""],
                help="Sélectionnez un compte existant ou tapez-en un nouveau ci-dessous",
            )

            manual_acc = st.text_input(
                "Ou saisir manuellement", placeholder="Ex: Compte Perso Aurélien"
            )
            final_acc = manual_acc if manual_acc else acc_label

            m_name_acc = st.selectbox(
                "Membre par défaut",
                members_df["name"].tolist() if not members_df.empty else ["Anonyme"],
                key="sel_m_acc",
            )

            submitted_acc = st.form_submit_button(f"{IconSet.ADD.value} Ajouter la règle", use_container_width=True)
            if submitted_acc:
                if not final_acc:
                    toast_warning(f"{IconSet.WARNING.value} Veuillez spécifier un compte", icon=IconSet.BANK.value)
                else:
                    add_account_member_mapping(final_acc, m_name_acc)
                    toast_success(f"{IconSet.SUCCESS.value} Compte {final_acc} associé à {m_name_acc}", icon=IconSet.BANK.value)
                    st.rerun()

    # --- DEFAULT MEMBER CONFIGURATION ---
    st.divider()
    st.subheader(f"{IconSet.TARGET.value} Membre par Défaut & Identification Forcée")
    st.markdown(
        """
    Configurez le membre utilisé par défaut lorsque l'attribution automatique échoue.
    Cela remplace les transactions 'Inconnu' par un membre identifié.
    """
    )

    col_def1, col_def2 = st.columns([1, 1])

    with col_def1:
        current_default = get_default_member()
        force_enabled = get_force_member_identification()

        with st.form("default_member_form"):
            st.caption(
                "Configuration actuelle"
                if current_default != "Inconnu"
                else f"{IconSet.WARNING.value} Pas de membre par défaut configuré"
            )

            default_member_input = st.selectbox(
                "Membre par défaut",
                options=members_df["name"].tolist() if not members_df.empty else ["Inconnu"],
                index=(
                    members_df["name"].tolist().index(current_default)
                    if current_default in members_df["name"].tolist()
                    else 0
                ),
                help="Ce membre sera utilisé quand aucune autre attribution n'est possible",
            )

            force_identification = st.toggle(
                "Forcer l'identification (jamais 'Inconnu')",
                value=force_enabled,
                help="Si activé, toutes les transactions auront un membre identifié. Jamais 'Inconnu'.",
            )

            submitted_def = st.form_submit_button(f"{IconSet.SAVE.value} Sauvegarder", use_container_width=True)
            if submitted_def:
                set_default_member(default_member_input)
                set_force_member_identification(force_identification)
                toast_success(
                    f"{IconSet.SUCCESS.value} Configuration sauvegardée: '{default_member_input}' est le membre par défaut",
                    icon=IconSet.TARGET.value,
                )
                st.rerun()

    with col_def2:
        # Show statistics
        stats = get_unknown_member_stats()

        st.metric(
            label="Transactions 'Inconnu'",
            value=f"{stats['count']} ({stats['percentage']}%)",
            delta=f"sur {stats['total']} total" if stats["total"] > 0 else None,
        )

        if stats["count"] > 0:
            st.caption("Répartition par compte:")
            for account, count in list(stats["by_account"].items())[:3]:
                st.progress(count / stats["count"], text=f"{account}: {count}")

    # --- UNKNOWN MEMBER ACTIONS ---
    if stats["count"] > 0:
        st.divider()
        st.subheader(f"{IconSet.TOOLS.value} Actions sur les Transactions 'Inconnu'")

        col_act1, col_act2, col_act3 = st.columns([1, 1, 1])

        with col_act1:
            if st.button(
                f"{IconSet.CHART.value} Analyser les Patterns", use_container_width=True, key="btn_analyze_patterns"
            ):
                suggestions = analyze_unknown_patterns()
                if suggestions:
                    st.info(f"{IconSet.LIGHTBULB.value} Suggestions d'amélioration:")
                    for s in suggestions:
                        with st.expander(f"{s['type']}: {s['value']} ({s['count']} transactions)"):
                            st.write(s["action"])
                            if "sql_check" in s:
                                st.code(s["sql_check"])
                            if "example" in s:
                                st.code(s["example"])
                else:
                    toast_info("Aucune suggestion automatique disponible", icon=IconSet.INFO.value)

        with col_act2:
            if st.button(
                f"{IconSet.SEARCH.value} Simuler Réparation", use_container_width=True, key="btn_simulate_repair"
            ):
                result = repair_unknown_members(dry_run=True)
                st.info(result["message"])
                if result["sample_repaired"]:
                    st.caption("Exemples de transactions qui seraient modifiées:")
                    for sample in result["sample_repaired"][:3]:
                        st.write(f"- {sample['label'][:40]}... ({sample['account']})")

        with col_act3:
            if st.button(
                f"{IconSet.SUCCESS.value} Tout Réparer Maintenant",
                type="primary",
                use_container_width=True,
                key="btn_repair_all",
            ):
                result = repair_unknown_members(dry_run=False)
                toast_success(result["message"], icon=IconSet.SUCCESS.value)
                st.rerun()

        # Ultimate solution
        st.divider()
        st.subheader(f"{IconSet.ROCKET.value} Solution Ultime: Zéro 'Inconnu'")
        st.markdown(
            """
        Activez l'**identification forcée** pour garantir que toutes les transactions passées et futures 
        auront un membre identifié. Cela:
        1. Active le mode forcé
        2. Répare toutes les transactions existantes
        3. Garantit l'attribution pour les imports futurs
        """
        )

        if st.button(
            f"{IconSet.ROCKET.value} Activer l'Identification Forcée",
            type="primary",
            use_container_width=True,
            key="btn_force_id",
        ):
            result = ensure_no_unknown_members()
            toast_success(result["message"], icon=IconSet.ROCKET.value)
            st.rerun()
