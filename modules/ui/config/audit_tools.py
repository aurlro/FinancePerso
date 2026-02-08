import streamlit as st
import pandas as pd
import difflib
import hashlib
from modules.utils import clean_label
from modules.db.audit import (
    get_transfer_inconsistencies,
    get_suggested_mappings,
    whitelist_transfer_label,
)
from modules.db.tags import learn_tags_from_history
from modules.data_manager import auto_fix_common_inconsistencies
from modules.db.members import (
    get_members,
    rename_member,
    add_member,
    add_member_mapping,
    get_orphan_labels,
    delete_and_replace_label,
)
from modules.db.categories import (
    get_categories,
    merge_categories,
    add_category,
    get_all_categories_including_ghosts,
)
from modules.db.rules import add_learning_rule
from modules.db.transactions import (
    get_transactions_by_criteria,
    delete_transaction_by_id,
    update_transaction_category,
    bulk_update_transaction_status,
    get_duplicates_report,
)
from modules.backup_manager import create_backup
from modules.ui.feedback import (
    toast_success,
    toast_error,
    toast_warning,
    toast_info,
    show_success,
    show_warning,
    show_info,
    celebrate_completion,
)


def render_audit_tools():
    """
    Render the Audit & Nettoyage tab content.
    Comprehensive data quality tools: auto-fix, orphan cleanup, ghost categories,
    duplicate detection, transfer audit, and card suggestions.
    """
    st.header("🧹 Audit & Nettoyage de Données")
    st.markdown("Outils pour maintenir la cohérence de vos données (membres, catégories, etc.)")

    # --- AUTOMATIC FIX ---
    with st.expander("🪄 Corrections Automatiques (Magic Fix 5.1)"):
        st.info(
            """
            **Le Magic Fix 5.1 optimise vos flux et vos bénéficiaires :**
            - 🔄 **Rapprochement Inter-Comptes** : Détecte et certifie automatiquement les virements entre vos comptes.
            - 🏢 **Normalisation Bénéficiaires** : Harmonise les noms des marchands via vos alias personnalisés.
            - 🧠 **Smart Tagging (IA)** : Remplit vos tags vides en apprenant de votre historique.
            - 👤 **Ré-attribution Membres** : Corrige l'attribution des membres sur les transactions.
            - 🧹 **Nettoyage Deep** : Supprime le bruit bancaire et les doublons universels.
        """
        )
        if st.button("Lancer les corrections magiques ✨", type="primary", key="audit_button_46"):
            with st.spinner("Analyse et correction des données..."):
                # Créer une sauvegarde avant
                backup_path = create_backup(label="pre_magic_fix")
                if backup_path:
                    toast_info("Sauvegarde de sécurité créée", icon="💾")

                count = auto_fix_common_inconsistencies()
                count_learned = learn_tags_from_history()

            if count > 0 or count_learned > 0:
                toast_success(
                    f"Fait ! {count} corrections + {count_learned} tags appris", icon="🪄"
                )
                show_success(f"✅ {count} corrections appliquées | {count_learned} tags appris")
                celebrate_completion(min_items=5, actual_items=count + count_learned)
            else:
                toast_info("Tout semble déjà propre !", icon="✨")
                show_info("Aucune correction nécessaire - vos données sont impeccables !")
            st.rerun()

    # --- MEMBER CLEANUP (Orphans) ---
    st.divider()
    st.subheader("👤 Nettoyage des Membres & Bénéficiaires")
    st.markdown(
        "Identifiez les noms qui apparaissent dans vos transactions mais qui ne figurent pas dans votre liste de membres officiels."
    )

    orphans = get_orphan_labels()
    official_members_list = sorted(
        [m["name"] for m in get_members().to_dict("records")] + ["Maison", "Famille", "Inconnu"]
    )

    if not orphans:
        st.success(
            "Félicitations ! Tous les noms dans vos transactions correspondent à des membres connus. ✨"
        )
    else:
        st.warning(
            f"Il y a **{len(orphans)}** noms de membres ou bénéficiaires 'inconnus' dans votre base."
        )

        for i, orphan in enumerate(orphans):
            c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1, 1, 0.5])
            c1.write(f"❓ **{orphan}**")

            with c2:
                target = st.selectbox(
                    "Fusionner avec...",
                    official_members_list,
                    key=f"merge_orphan_{i}",
                    label_visibility="collapsed",
                )

            with c3:
                if st.button(
                    "🔀 Fusion", key=f"btn_orphan_{i}", help="Fusionner avec un membre officiel"
                ):
                    count = rename_member(orphan, target)
                    st.toast(f"✅ '{orphan}' ➔ '{target}' ({count} tx)", icon="🔀")
                    st.rerun()

            with c4:
                if st.button(
                    "👥 Tiers",
                    key=f"btn_tiers_{i}",
                    help="Enregistrer comme nouveau Tiers officiel",
                ):
                    add_member(orphan, "EXTERNAL")
                    st.toast(f"✅ '{orphan}' ajouté aux Tiers !", icon="👥")
                    st.rerun()

            with c5:
                if st.button(
                    "🗑️", key=f"btn_del_{i}", help="Supprimer partout et remplacer par 'Inconnu'"
                ):
                    count = delete_and_replace_label(orphan, "Inconnu")
                    st.toast(f"✅ '{orphan}' supprimé ({count} tx)", icon="🗑️")
                    st.rerun()

    # --- CATEGORY MERGE SECTION ---
    st.divider()
    st.subheader("🔀 Fusionner des catégories")
    st.info(
        """
        Transférez toutes les transactions d'une catégorie vers une autre (utile pour les doublons).
    """
    )

    col_m1, col_m2, col_m3 = st.columns([2, 2, 1])

    all_cats = get_categories()
    with col_m1:
        source_cat = st.selectbox(
            "Catégorie à absorber",
            all_cats,
            key="merge_source_audit",
            help="Cette catégorie sera vidée de ses transactions",
        )

    with col_m2:
        target_options = [c for c in all_cats if c != source_cat]
        target_cat = st.selectbox(
            "Catégorie cible",
            target_options if target_options else [""],
            key="merge_target_audit",
            help="Cette catégorie recevra toutes les transactions",
        )

    with col_m3:
        st.markdown("<div style='height: 0.1rem;'></div>", unsafe_allow_html=True)
        if st.button(
            "Fusionner", key="btn_merge_cat_audit", use_container_width=True, type="primary"
        ):
            if source_cat and target_cat and source_cat != target_cat:
                result = merge_categories(source_cat, target_cat)
                st.toast(f"✅ {result['transactions']} transactions transférées !", icon="🔀")
                st.rerun()
            else:
                st.warning("Veuillez sélectionner deux catégories différentes.")

    # --- GHOST BUSTER (Category Cleanup) ---
    st.divider()
    st.subheader("👻 Chasse aux Catégories Fantômes")
    st.markdown(
        "Identifiez les catégories utilisées dans les transactions mais qui n'existent pas officiellement (souvent issues des imports)."
    )

    all_cats_status = get_all_categories_including_ghosts()
    ghosts = [c for c in all_cats_status if c["type"] == "GHOST"]

    if not ghosts:
        st.success("Aucune catégorie fantôme détectée ! 🛡️")
    else:
        st.warning(f"**{len(ghosts)}** catégories fantômes détectées.")

        # Display as a clean table with actions
        for g in ghosts:
            g_name = g["name"]
            with st.container(border=True):
                c1, c2, c3_options, c4_action = st.columns(
                    [2, 1, 2, 1], vertical_alignment="center"
                )
                c1.markdown(f"👻 **{g_name}**")

                # Option A: Create it
                if c2.button(
                    "Créer ✅",
                    key=f"create_ghost_{g_name}",
                    help="Ajouter aux catégories officielles",
                ):
                    add_category(g_name)
                    st.toast(f"✅ Catégorie '{g_name}' officialisée !", icon="🛡️")
                    st.rerun()

                # Option B: Migrate it
                official_names = [c["name"] for c in all_cats_status if c["type"] == "OFFICIAL"]
                target = c3_options.selectbox(
                    "Ou fusionner vers...",
                    [""] + official_names,
                    key=f"sel_mig_{g_name}",
                    label_visibility="collapsed",
                )

                if c4_action.button("Fusionner 🔀", key=f"mig_ghost_{g_name}"):
                    if target:
                        res = merge_categories(g_name, target)
                        count = res.get("transactions", 0)
                        toast_success(f"Transféré ! {count} tx déplacées", icon="🔀")
                        st.rerun()
                    else:
                        toast_warning("Choisissez une cible", icon="⚠️")

    # --- DUPLICATE FINDER ---
    st.divider()
    st.subheader("🕵️ Détecteur de Doublons")
    st.markdown(
        "Identifie les transactions identiques (même date, libellé et montant) pour nettoyage."
    )

    dup_df = get_duplicates_report()

    if dup_df.empty:
        st.success("Aucun doublon détecté ! ✨")
    else:
        st.warning(f"**{len(dup_df)}** groupes de doublons potentiels trouvés.")
        for i, row in dup_df.iterrows():
            with st.expander(
                f"📌 {row['date']} • {row['label']} • {row['amount']:.2f}€ ({row['count']} fois)"
            ):
                # Get details
                details = get_transactions_by_criteria(row["date"], row["label"], row["amount"])

                # Show each with a delete button
                for _, d_row in details.iterrows():
                    c1, c2, c3 = st.columns([3, 1, 0.5])
                    c1.write(f"🏢 {d_row['account_label']} | 👤 {d_row['member']}")
                    c2.write(f":grey[{d_row['import_date']}]")
                    if c3.button("🗑️", key=f"del_dup_{d_row['id']}"):
                        delete_transaction_by_id(d_row["id"])
                        toast_success("Transaction supprimée", icon="🗑️")
                        st.rerun()

                if st.button("🪄 Garder un seul (Auto)", key=f"clean_grp_{i}"):
                    to_delete = details.iloc[1:]["id"].tolist()
                    deleted_count = 0
                    for tid in to_delete:
                        deleted_count += delete_transaction_by_id(tid)
                    toast_success(f"{deleted_count} doublons supprimés", icon="🪄")
                    st.rerun()

    # --- TRANSFER AUDIT ---
    st.divider()
    st.subheader("🔄 Audit des Virements")
    st.markdown("Identifiez les virements internes qui pourraient être mal catégorisés.")

    missing_t, wrong_t = get_transfer_inconsistencies()

    if missing_t.empty and wrong_t.empty:
        st.success("Aucune incohérence de virement détectée. ✨")
    else:
        if not missing_t.empty:
            st.warning(
                f"**{len(missing_t)}** transactions ressemblent à des virements mais n'ont pas la catégorie 'Virement Interne'."
            )

            # Grouping Logic
            missing_t["clean"] = missing_t["label"].apply(clean_label)

            exact_groups = missing_t.groupby("clean")
            final_groups = {}

            for label, group in exact_groups:
                found_match = False
                for existing_label in final_groups.keys():
                    similarity = difflib.SequenceMatcher(None, label, existing_label).ratio()
                    if similarity >= 0.8:
                        final_groups[existing_label] = pd.concat(
                            [final_groups[existing_label], group]
                        )
                        found_match = True
                        break

                if not found_match:
                    final_groups[label] = group

            # Display groups
            with st.expander("Voir et corriger les groupes de virements", expanded=True):
                # Global action for this section
                if st.button(
                    "✅ Tout valider comme Virement",
                    use_container_width=True,
                    key="bulk_accept_all_missing",
                ):
                    tx_ids = missing_t["id"].tolist()
                    bulk_update_transaction_status(tx_ids, "Virement Interne")
                    toast_success(f"Corrigé ! {len(tx_ids)} transactions validées.", icon="🔄")
                    st.rerun()

                st.divider()

                all_categories = get_categories()
                default_cat = (
                    "Virement Interne"
                    if "Virement Interne" in all_categories
                    else all_categories[0]
                )

                for label, group in final_groups.items():
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([2, 1, 1])
                        count = len(group)
                        total_amount = group["amount"].sum()
                        c1.markdown(f"📦 **{label}** ({count} tx)")
                        c1.caption(f"Total : {total_amount:.2f}€")

                        # Suggest Revenus if total amount is positive
                        if total_amount > 0 and "Revenus" in all_categories:
                            group_default = "Revenus"
                        else:
                            group_default = default_cat

                        # Safe and unique key for Streamlit
                        safe_key = hashlib.md5(label.encode()).hexdigest()[:12]

                        target_cat = c2.selectbox(
                            "Catégorie",
                            all_categories,
                            index=all_categories.index(group_default),
                            key=f"bulk_cat_{safe_key}",
                            label_visibility="collapsed",
                        )

                        if c3.button(f"Confirmer ce groupe", key=f"bulk_fix_{safe_key}"):
                            tx_ids = group["id"].tolist()
                            bulk_update_transaction_status(tx_ids, target_cat)
                            toast_success(
                                f"Corrigé ! {len(tx_ids)} tx en '{target_cat}'", icon="🔄"
                            )
                            st.rerun()

                        # Show individual transactions if user wants
                        if st.checkbox(f"Détails", key=f"show_detail_{label}"):
                            for _, row in group.iterrows():
                                st.write(
                                    f"  • {row['date']} • {row['label']} • {row['amount']:.2f}€"
                                )

        if not wrong_t.empty:
            st.info(
                f"**{len(wrong_t)}** transactions sont catégorisées 'Virement Interne' mais n'en ont pas l'air."
            )

            # Grouping Logic for doubtful transfers
            wrong_t["clean"] = wrong_t["label"].apply(clean_label)
            exact_groups_w = wrong_t.groupby("clean")
            final_groups_w = {}

            for label, group in exact_groups_w:
                found_match = False
                for existing_label in final_groups_w.keys():
                    similarity = difflib.SequenceMatcher(None, label, existing_label).ratio()
                    if similarity >= 0.8:
                        final_groups_w[existing_label] = pd.concat(
                            [final_groups_w[existing_label], group]
                        )
                        found_match = True
                        break
                if not found_match:
                    final_groups_w[label] = group

            with st.expander("Examiner les virements douteux", expanded=True):
                # Global action for this section
                if st.button(
                    "✅ Confirmer tous ces virements",
                    use_container_width=True,
                    key="bulk_whitelist_all",
                ):
                    unique_labels = wrong_t["label"].unique()
                    for l in unique_labels:
                        whitelist_transfer_label(l)
                    toast_success(
                        f"Connaissance enrichie ! {len(unique_labels)} libellés validés.", icon="🧠"
                    )
                    st.rerun()

                st.divider()

                all_categories = get_categories()

                for label, group in final_groups_w.items():
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([2, 1, 1])
                        count = len(group)
                        total_amount = group["amount"].sum()
                        c1.markdown(f"❓ **{label}** ({count} tx)")
                        c1.caption(f"Total : {total_amount:.2f}€")

                        safe_key = hashlib.md5(f"wrong_{label}".encode()).hexdigest()[:12]

                        # Option A: Whitelist (Knowledge Enrichment)
                        if c2.button(
                            "✅ C'est un virement",
                            key=f"whitelist_{safe_key}",
                            help="Confirmer que c'est un virement interne (enrichit la connaissance)",
                        ):
                            # We whitelist the groups labels (actually we should whitelist the specific unique labels in this group)
                            unique_labels = group["label"].unique()
                            for l in unique_labels:
                                whitelist_transfer_label(l)
                            toast_success(
                                f"Connaissance enrichie ! '{label}' est désormais validé.",
                                icon="🧠",
                            )
                            st.rerun()

                        # Option B: Bulk Re-attribute
                        target_cat = c3.selectbox(
                            "Ré-attribuer à...",
                            all_categories,
                            index=0,  # Default to first
                            key=f"bulk_re_cat_{safe_key}",
                            label_visibility="collapsed",
                        )

                        if st.button(
                            f"Changer de catégorie ({count})",
                            key=f"bulk_re_fix_{safe_key}",
                            use_container_width=True,
                        ):
                            tx_ids = group["id"].tolist()
                            bulk_update_transaction_status(tx_ids, target_cat)
                            # Knowledge enrichment: add a rule for the cleaned label
                            add_learning_rule(label, target_cat, priority=2)
                            toast_success(
                                f"Déplacé ! {len(tx_ids)} tx en '{target_cat}' (Règle apprise 🧠)",
                                icon="🔀",
                            )
                            st.rerun()

                        if st.checkbox(f"Détails", key=f"show_detail_w_{label}"):
                            for _, row in group.iterrows():
                                st.write(
                                    f"  • {row['date']} • {row['label']} • {row['amount']:.2f}€"
                                )

    # --- CARD SUGGESTIONS ---
    st.divider()
    st.subheader("💳 Suggestions de Membres (Cartes)")
    st.markdown(
        "Numéros de carte détectés dans vos libellés qui ne sont pas encore associés à un membre."
    )

    suggestions = get_suggested_mappings()
    if suggestions.empty:
        st.success("Toutes vos cartes semblent déjà mappées ! ✨")
    else:
        for _, row in suggestions.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 2, 1])
                c1.write(f"💳 Carte **{row['card_suffix']}**")
                c1.caption(f"Vue {row['occurrence']} fois (ex: {row['example_label']})")

                members_list = sorted(get_members()["name"].tolist())
                target_m = c2.selectbox(
                    "Attribuer à",
                    members_list,
                    key=f"sugg_m_{row['card_suffix']}",
                    label_visibility="collapsed",
                )

                if c3.button(
                    "Associer", key=f"btn_sugg_{row['card_suffix']}", use_container_width=True
                ):
                    add_member_mapping(row["card_suffix"], target_m)
                    toast_success(
                        f"Carte ...{row['card_suffix']} associée à {target_m} !", icon="💳"
                    )
                    st.rerun()
