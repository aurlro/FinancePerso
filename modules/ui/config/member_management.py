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
from modules.ui.feedback import (
    delete_feedback,
    save_feedback,
    show_error,
    show_warning,
    toast_error,
    toast_info,
    toast_success,
    toast_warning,
)

# Initialisation des variables de session
if "pending_rename" not in st.session_state:
    st.session_state["pending_rename"] = None
if "editing_member_id" not in st.session_state:
    st.session_state["editing_member_id"] = None


def render_member_management():
    """
    Render the Foyer & Membres tab content.
    Manage household members, external entities, and card-to-member mappings.
    """
    st.header("👥 Membres du Foyer")
    st.markdown("Définissez les personnes associées à ce compte pour l'attribution des dépenses.")

    # Handle pending rename with impact preview
    pending = st.session_state.get("pending_rename")
    if pending is not None:
        with st.container(border=True):
            st.warning("⚠️ Confirmer le renommage ?")
            render_impact_preview("member_rename", pending["impact"])

            col_confirm, col_cancel = st.columns([1, 1])
            with col_confirm:
                if st.button(
                    "👤 Confirmer le nouveau nom",
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
                                f"✅ '{pending['old_name']}' renommé en '{pending['new_name']}' ({affected} transaction(s) mise(s) à jour)",
                                icon="👤",
                            )
                        else:
                            toast_success(
                                f"✅ '{pending['old_name']}' renommé en '{pending['new_name']}'",
                                icon="👤",
                            )
                        save_feedback(
                            f"Membre '{pending['old_name']}' → '{pending['new_name']}'",
                            created=False,
                        )
                        st.rerun()
                    except Exception as e:
                        error_msg = str(e)
                        if "existe déjà" in error_msg.lower() or "already" in error_msg.lower():
                            toast_error(
                                f"❌ Le nom '{pending['new_name']}' est déjà utilisé", icon="🚫"
                            )
                        elif "not found" in error_msg.lower():
                            toast_error(
                                f"❌ Le membre '{pending['old_name']}' n'existe plus", icon="⚠️"
                            )
                        else:
                            toast_error(
                                f"❌ Erreur lors du renommage : {error_msg[:50]}", icon="❌"
                            )
            with col_cancel:
                if st.button("❌ Annuler", use_container_width=True, key="member_button_66"):
                    del st.session_state["pending_rename"]
                    toast_info("Renommage annulé", icon="🚫")
                    st.rerun()
        st.divider()

    members_df = get_members()

    col_list, col_add = st.columns([1, 1])

    with col_list:
        if members_df.empty:
            st.info("📭 Aucun membre configuré. Ajoutez votre premier membre à droite.")
        else:
            if "editing_member_id" not in st.session_state:
                st.session_state["editing_member_id"] = None

            # --- HOUSEHOLD GROUP ---
            foyer_df = members_df[members_df["member_type"] == "HOUSEHOLD"]
            st.subheader("🏘️ Membres du Foyer")
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
                            if st.button("✅", key=f"sv_{member_id}", help="Sauvegarder"):
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
                                                    f"✅ Membre renommé : '{member_name}' → '{cleaned_name}'",
                                                    icon="👤",
                                                )
                                                st.rerun()
                                            except Exception as e:
                                                toast_error(f"❌ Erreur : {str(e)[:50]}", icon="❌")
                                    else:
                                        toast_info("ℹ️ Aucun changement", icon="ℹ️")
                                else:
                                    toast_warning("⚠️ Le nom ne peut pas être vide", icon="⚠️")
                        with c3:
                            if st.button("❌", key=f"cl_{member_id}", help="Annuler"):
                                st.session_state["editing_member_id"] = None
                                st.rerun()
                    else:
                        c1, c2, c3, c4 = st.columns([3, 1, 0.5, 0.5])
                        c1.write(f"👤 **{member_name}**")
                        if c2.button(
                            "➡️ Passer en Tiers",
                            key=f"to_ext_{member_id}",
                            help="Déplacer vers Tiers",
                        ):
                            try:
                                update_member_type(member_id, "EXTERNAL")
                                toast_success(f"✅ '{member_name}' déplacé vers Tiers", icon="💼")
                                st.rerun()
                            except Exception as e:
                                toast_error(
                                    f"❌ Impossible de déplacer '{member_name}' : {str(e)[:50]}",
                                    icon="❌",
                                )
                        if c3.button("✏️", key=f"ed_{member_id}", help="Renommer"):
                            st.session_state["editing_member_id"] = member_id
                            st.rerun()
                        if c4.button("🗑️", key=f"del_{member_id}", help="Supprimer"):
                            try:
                                delete_member(member_id)
                                delete_feedback(f"Membre '{member_name}'")
                                toast_success(f"🗑️ Membre '{member_name}' supprimé", icon="🗑️")
                                st.rerun()
                            except Exception as e:
                                error_msg = str(e)
                                if "FOREIGN KEY" in error_msg or "utilisé" in error_msg.lower():
                                    show_error(
                                        f"Impossible de supprimer '{member_name}'", icon="🔗"
                                    )
                                    toast_error(
                                        f"❌ '{member_name}' est utilisé dans des transactions ou des cartes. "
                                        "Supprimez d'abord ces associations.",
                                        icon="🔗",
                                    )
                                else:
                                    toast_error(
                                        f"❌ Erreur suppression : {error_msg[:50]}", icon="❌"
                                    )

            # --- EXTERNAL GROUP ---
            ext_df = members_df[members_df["member_type"] == "EXTERNAL"]
            st.subheader("💼 Tiers (Externe)")
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
                            if st.button("✅", key=f"sv_{member_id}", help="Sauvegarder"):
                                if edit_name and edit_name.strip():
                                    cleaned_name = edit_name.strip()
                                    if cleaned_name != member_name:
                                        try:
                                            rename_member(member_name, cleaned_name)
                                            st.session_state["editing_member_id"] = None
                                            toast_success(
                                                f"✅ Membre renommé : '{member_name}' → '{cleaned_name}'",
                                                icon="👤",
                                            )
                                            st.rerun()
                                        except Exception as e:
                                            toast_error(f"❌ Erreur : {str(e)[:50]}", icon="❌")
                                    else:
                                        toast_info("ℹ️ Aucun changement", icon="ℹ️")
                                else:
                                    toast_warning("⚠️ Le nom ne peut pas être vide", icon="⚠️")
                        with c3:
                            if st.button("❌", key=f"cl_{member_id}", help="Annuler"):
                                st.session_state["editing_member_id"] = None
                                st.rerun()
                    else:
                        c1, c2, c3, c4 = st.columns([3, 1, 0.5, 0.5])
                        c1.write(f"💼 **{member_name}**")
                        if c2.button(
                            "⬅️ Passer au Foyer",
                            key=f"to_hh_{member_id}",
                            help="Déplacer vers Foyer",
                        ):
                            try:
                                update_member_type(member_id, "HOUSEHOLD")
                                toast_success(f"✅ '{member_name}' déplacé vers Foyer", icon="🏘️")
                                st.rerun()
                            except Exception as e:
                                toast_error(
                                    f"❌ Impossible de déplacer '{member_name}' : {str(e)[:50]}",
                                    icon="❌",
                                )
                        if c3.button("✏️", key=f"ed_{member_id}", help="Renommer"):
                            st.session_state["editing_member_id"] = member_id
                            st.rerun()
                        if c4.button("🗑️", key=f"del_{member_id}", help="Supprimer"):
                            try:
                                delete_member(member_id)
                                toast_success(f"🗑️ Membre '{member_name}' supprimé", icon="🗑️")
                                st.rerun()
                            except Exception as e:
                                error_msg = str(e)
                                if "FOREIGN KEY" in error_msg or "utilisé" in error_msg.lower():
                                    show_error(
                                        f"Impossible de supprimer '{member_name}'", icon="🔗"
                                    )
                                    toast_error(
                                        f"❌ '{member_name}' est utilisé dans des transactions ou des cartes",
                                        icon="🔗",
                                    )
                                else:
                                    toast_error(
                                        f"❌ Erreur suppression : {error_msg[:50]}", icon="❌"
                                    )

    with col_add:
        st.subheader("➕ Ajouter un membre")
        with st.form("add_member_form"):
            new_name = st.text_input(
                "Nom", placeholder="Ex: Jean, Marie...", help="Nom unique du membre"
            )
            new_type = st.radio(
                "Type",
                ["HOUSEHOLD", "EXTERNAL"],
                format_func=lambda x: "🏘️ Foyer" if x == "HOUSEHOLD" else "💼 Tiers",
                help="Foyer = membre du budget, Tiers = externe (ex: crèche, impôts)",
            )

            submitted = st.form_submit_button("➕ Ajouter", use_container_width=True)
            if submitted:
                if not new_name or not new_name.strip():
                    toast_warning("⚠️ Veuillez entrer un nom", icon="✏️")
                elif len(new_name.strip()) < 2:
                    toast_warning("⚠️ Le nom doit contenir au moins 2 caractères", icon="📏")
                else:
                    cleaned_name = new_name.strip()
                    try:
                        if add_member(cleaned_name, new_type):
                            member_type_label = "Foyer" if new_type == "HOUSEHOLD" else "Tiers"
                            toast_success(
                                f"✅ Membre créé : '{cleaned_name}' ({member_type_label})",
                                icon="🎉",
                            )
                            save_feedback(
                                f"Membre '{cleaned_name}' ({member_type_label})", created=True
                            )
                            st.rerun()
                        else:
                            show_warning(f"Le membre '{cleaned_name}' existe déjà", icon="⚠️")
                            toast_error(
                                f"❌ '{cleaned_name}' existe déjà. Choisissez un nom différent.",
                                icon="🚫",
                            )
                    except Exception as e:
                        error_msg = str(e)
                        if "existe déjà" in error_msg.lower() or "already" in error_msg.lower():
                            toast_error(f"❌ Le membre '{cleaned_name}' existe déjà", icon="🚫")
                        else:
                            toast_error(f"❌ Erreur création : {error_msg[:50]}", icon="❌")

    # --- CARD MAPPINGS ---
    st.divider()
    st.subheader("💳 Correspondances Cartes → Membres")
    st.markdown("Associez automatiquement une carte bancaire (4 derniers chiffres) à un membre.")

    if members_df.empty:
        st.warning("⚠️ Ajoutez d'abord des membres pour configurer les correspondances.", icon="⚠️")
        return

    mapping_df = get_member_mappings_df()

    col_m1, col_m2 = st.columns([1, 1])
    with col_m1:
        if mapping_df.empty:
            st.info("📭 Aucune correspondance configurée.")
        else:
            st.caption(f"{len(mapping_df)} carte(s) configurée(s)")
            for index, row in mapping_df.iterrows():
                cm1, cm2 = st.columns([3, 1])
                cm1.write(f"💳 **...{row['card_suffix']}** ➔ 👤 {row['member_name']}")
                if cm2.button("🗑️", key=f"del_map_{row['id']}", help="Supprimer la correspondance"):
                    try:
                        delete_member_mapping(row["id"])
                        toast_success(
                            f"🗑️ Carte ...{row['card_suffix']} dissociée de {row['member_name']}",
                            icon="🗑️",
                        )
                        st.rerun()
                    except Exception as e:
                        toast_error(f"❌ Erreur : {str(e)[:50]}", icon="❌")

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

            submitted = st.form_submit_button("➕ Ajouter la carte", use_container_width=True)
            if submitted:
                if not suffix or not suffix.strip():
                    toast_warning("⚠️ Veuillez entrer les 4 derniers chiffres", icon="💳")
                elif not m_name:
                    toast_warning("⚠️ Veuillez sélectionner un membre", icon="👤")
                elif len(suffix.strip()) != 4 or not suffix.strip().isdigit():
                    toast_warning("⚠️ Le suffixe doit être exactement 4 chiffres", icon="📏")
                else:
                    clean_suffix = suffix.strip()
                    try:
                        add_member_mapping(clean_suffix, m_name)
                        toast_success(f"✅ Carte ...{clean_suffix} associée à {m_name}", icon="💳")
                        save_feedback(
                            f"Carte '...{clean_suffix}' associée à {m_name}", created=True
                        )
                        st.rerun()
                    except Exception as e:
                        error_msg = str(e)
                        if "existe déjà" in error_msg.lower() or "already" in error_msg.lower():
                            toast_error(
                                f"❌ La carte ...{clean_suffix} est déjà associée", icon="🚫"
                            )
                        else:
                            toast_error(f"❌ Erreur : {error_msg[:50]}", icon="❌")

    # --- ACCOUNT MAPPINGS ---
    st.divider()
    st.subheader("🏦 Correspondances Comptes → Membres")
    st.markdown(
        "Définissez un membre par défaut pour toutes les transactions d'un compte spécifique (ex: votre compte personnel)."
    )

    acc_mapping_df = get_account_member_mappings_df()

    col_a1, col_a2 = st.columns([1, 1])
    with col_a1:
        if acc_mapping_df.empty:
            st.info("📭 Aucune correspondance par compte.")
        else:
            for index, row in acc_mapping_df.iterrows():
                ca1, ca2 = st.columns([3, 1])
                ca1.write(f"🏦 **{row['account_label']}** ➔ 👤 {row['member_name']}")
                if ca2.button("🗑️", key=f"del_acc_map_{row['id']}", help="Supprimer cette règle"):
                    delete_account_member_mapping(row["id"])
                    toast_success(f"🗑️ Règle supprimée pour {row['account_label']}", icon="🗑️")
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

            submitted_acc = st.form_submit_button("➕ Ajouter la règle", use_container_width=True)
            if submitted_acc:
                if not final_acc:
                    toast_warning("⚠️ Veuillez spécifier un compte", icon="🏦")
                else:
                    add_account_member_mapping(final_acc, m_name_acc)
                    toast_success(f"✅ Compte {final_acc} associé à {m_name_acc}", icon="🏦")
                    st.rerun()

    # --- DEFAULT MEMBER CONFIGURATION ---
    st.divider()
    st.subheader("🎯 Membre par Défaut & Identification Forcée")
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
                else "⚠️ Pas de membre par défaut configuré"
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

            submitted_def = st.form_submit_button("💾 Sauvegarder", use_container_width=True)
            if submitted_def:
                set_default_member(default_member_input)
                set_force_member_identification(force_identification)
                toast_success(
                    f"✅ Configuration sauvegardée: '{default_member_input}' est le membre par défaut",
                    icon="🎯",
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
        st.subheader("🔧 Actions sur les Transactions 'Inconnu'")

        col_act1, col_act2, col_act3 = st.columns([1, 1, 1])

        with col_act1:
            if st.button(
                "📊 Analyser les Patterns", use_container_width=True, key="btn_analyze_patterns"
            ):
                suggestions = analyze_unknown_patterns()
                if suggestions:
                    st.info("💡 Suggestions d'amélioration:")
                    for s in suggestions:
                        with st.expander(f"{s['type']}: {s['value']} ({s['count']} transactions)"):
                            st.write(s["action"])
                            if "sql_check" in s:
                                st.code(s["sql_check"])
                            if "example" in s:
                                st.code(s["example"])
                else:
                    toast_info("Aucune suggestion automatique disponible", icon="ℹ️")

        with col_act2:
            if st.button(
                "🔍 Simuler Réparation", use_container_width=True, key="btn_simulate_repair"
            ):
                result = repair_unknown_members(dry_run=True)
                st.info(result["message"])
                if result["sample_repaired"]:
                    st.caption("Exemples de transactions qui seraient modifiées:")
                    for sample in result["sample_repaired"][:3]:
                        st.write(f"- {sample['label'][:40]}... ({sample['account']})")

        with col_act3:
            if st.button(
                "✅ Tout Réparer Maintenant",
                type="primary",
                use_container_width=True,
                key="btn_repair_all",
            ):
                result = repair_unknown_members(dry_run=False)
                toast_success(result["message"], icon="✅")
                st.rerun()

        # Ultimate solution
        st.divider()
        st.subheader("🚀 Solution Ultime: Zéro 'Inconnu'")
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
            "🚀 Activer l'Identification Forcée",
            type="primary",
            use_container_width=True,
            key="btn_force_id",
        ):
            result = ensure_no_unknown_members()
            toast_success(result["message"], icon="🚀")
            st.rerun()
