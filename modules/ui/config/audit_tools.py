import streamlit as st
import pandas as pd
import difflib
import hashlib
from modules.utils import clean_label
from modules.data_manager import (
    auto_fix_common_inconsistencies, learn_tags_from_history,
    get_orphan_labels, get_members, rename_member, add_member,
    delete_and_replace_label, get_categories, merge_categories,
    get_all_categories_including_ghosts, add_category,
    get_duplicates_report, get_transactions_by_criteria,
    delete_transaction_by_id, get_transfer_inconsistencies,
    update_transaction_category, bulk_update_transaction_status,
    get_suggested_mappings, add_member_mapping
)
from modules.backup_manager import create_backup

def render_audit_tools():
    """
    Render the Audit & Nettoyage tab content.
    Comprehensive data quality tools: auto-fix, orphan cleanup, ghost categories,
    duplicate detection, transfer audit, and card suggestions.
    """
    st.header("🧹 Audit & Nettoyage de Données")
    st.markdown("Outils pour maintenir la cohérence de vos données (membres, catégories, etc.)")
    
    # --- AUTOMATIC FIX ---
    with st.expander("🪄 Corrections Automatiques (Magic Fix 2.0)", expanded=True):
        st.info("""
            **Le Magic Fix 2.0 nettoie votre base en un clic :**
            - 🛠️ Corrige les fautes de frappe et accents sur les membres.
            - 🧹 Supprime automatiquement tous les doublons détectés.
            - 🏷️ Normalise les tags (minuscules et dédoublonnage).
            - 🧠 Ré-applique vos règles aux transactions en attente.
        """)
        if st.button("Lancer les corrections magiques ✨", type="primary"):
            create_backup(label="pre_magic_fix")
            count = auto_fix_common_inconsistencies()
            count_learned = learn_tags_from_history()
            
            if count > 0 or count_learned > 0:
                st.toast(f"✅ Fait ! {count} corrections + {count_learned} tags appris.", icon="🪄")
            else:
                st.toast("Tout semble déjà propre ! ✨")
            st.rerun()

    # --- MEMBER CLEANUP (Orphans) ---
    st.divider()
    st.subheader("👤 Nettoyage des Membres & Bénéficiaires")
    st.markdown("Identifiez les noms qui apparaissent dans vos transactions mais qui ne figurent pas dans votre liste de membres officiels.")
    
    orphans = get_orphan_labels()
    official_members_list = sorted([m['name'] for m in get_members().to_dict('records')] + ["Maison", "Famille", "Inconnu"])
    
    if not orphans:
        st.success("Félicitations ! Tous les noms dans vos transactions correspondent à des membres connus. ✨")
    else:
        st.warning(f"Il y a **{len(orphans)}** noms de membres ou bénéficiaires 'inconnus' dans votre base.")
        
        for i, orphan in enumerate(orphans):
            c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1, 1, 0.5])
            c1.write(f"❓ **{orphan}**")
            
            with c2:
                target = st.selectbox("Fusionner avec...", official_members_list, key=f"merge_orphan_{i}", label_visibility="collapsed")
            
            with c3:
                if st.button("🔀 Fusion", key=f"btn_orphan_{i}", help="Fusionner avec un membre officiel"):
                    count = rename_member(orphan, target)
                    st.toast(f"✅ '{orphan}' ➔ '{target}' ({count} tx)", icon="🔀")
                    st.rerun()
            
            with c4:
                if st.button("👥 Tiers", key=f"btn_tiers_{i}", help="Enregistrer comme nouveau Tiers officiel"):
                    add_member(orphan, 'EXTERNAL')
                    st.toast(f"✅ '{orphan}' ajouté aux Tiers !", icon="👥")
                    st.rerun()
            
            with c5:
                if st.button("🗑️", key=f"btn_del_{i}", help="Supprimer partout et remplacer par 'Inconnu'"):
                    count = delete_and_replace_label(orphan, "Inconnu")
                    st.toast(f"✅ '{orphan}' supprimé ({count} tx)", icon="🗑️")
                    st.rerun()

    # --- CATEGORY MERGE SECTION ---
    st.divider()
    st.subheader("🔀 Fusionner des catégories")
    st.info("""
        Transférez toutes les transactions d'une catégorie vers une autre (utile pour les doublons).
    """)
    
    col_m1, col_m2, col_m3 = st.columns([2, 2, 1])
    
    all_cats = get_categories()
    with col_m1:
        source_cat = st.selectbox(
            "Catégorie à absorber",
            all_cats,
            key="merge_source_audit",
            help="Cette catégorie sera vidée de ses transactions"
        )
    
    with col_m2:
        target_options = [c for c in all_cats if c != source_cat]
        target_cat = st.selectbox(
            "Catégorie cible",
            target_options if target_options else [""],
            key="merge_target_audit",
            help="Cette catégorie recevra toutes les transactions"
        )
    
    with col_m3:
        st.markdown("<div style='height: 0.1rem;'></div>", unsafe_allow_html=True)
        if st.button("Fusionner", key="btn_merge_cat_audit", use_container_width=True, type="primary"):
            if source_cat and target_cat and source_cat != target_cat:
                result = merge_categories(source_cat, target_cat)
                st.toast(f"✅ {result['transactions']} transactions transférées !", icon="🔀")
                st.rerun()
            else:
                st.warning("Veuillez sélectionner deux catégories différentes.")

    # --- GHOST BUSTER (Category Cleanup) ---
    st.divider()
    st.subheader("👻 Chasse aux Catégories Fantômes")
    st.markdown("Identifiez les catégories utilisées dans les transactions mais qui n'existent pas officiellement (souvent issues des imports).")
    
    all_cats_status = get_all_categories_including_ghosts()
    ghosts = [c for c in all_cats_status if c['type'] == 'GHOST']
    
    if not ghosts:
        st.success("Aucune catégorie fantôme détectée ! 🛡️")
    else:
        st.warning(f"**{len(ghosts)}** catégories fantômes détectées.")
        
        # Display as a clean table with actions
        for g in ghosts:
            g_name = g['name']
            with st.container(border=True):
                c1, c2, c3_options, c4_action = st.columns([2, 1, 2, 1], vertical_alignment="center")
                c1.markdown(f"👻 **{g_name}**")
                
                # Option A: Create it
                if c2.button("Créer ✅", key=f"create_ghost_{g_name}", help="Ajouter aux catégories officielles"):
                    add_category(g_name)
                    st.toast(f"✅ Catégorie '{g_name}' officialisée !", icon="🛡️")
                    st.rerun()
                
                # Option B: Migrate it
                official_names = [c['name'] for c in all_cats_status if c['type'] == 'OFFICIAL']
                target = c3_options.selectbox("Ou fusionner vers...", [""] + official_names, key=f"sel_mig_{g_name}", label_visibility="collapsed")
                
                if c4_action.button("Fusionner 🔀", key=f"mig_ghost_{g_name}"):
                    if target:
                        res = merge_categories(g_name, target)
                        st.toast(f"✅ Transféré ! {res['transactions']} tx déplacées.", icon="🔀")
                        st.rerun()
                    else:
                        st.warning("Choisissez une cible.")

    # --- DUPLICATE FINDER ---
    st.divider()
    st.subheader("🕵️ Détecteur de Doublons")
    st.markdown("Identifie les transactions identiques (même date, libellé et montant) pour nettoyage.")
    
    dup_df = get_duplicates_report()
    
    if dup_df.empty:
        st.success("Aucun doublon détecté ! ✨")
    else:
        st.warning(f"**{len(dup_df)}** groupes de doublons potentiels trouvés.")
        for i, row in dup_df.iterrows():
            with st.expander(f"📌 {row['date']} • {row['label']} • {row['amount']:.2f}€ ({row['count']} fois)"):
                # Get details
                details = get_transactions_by_criteria(row['date'], row['label'], row['amount'])
                
                # Show each with a delete button
                for _, d_row in details.iterrows():
                    c1, c2, c3 = st.columns([3, 1, 0.5])
                    c1.write(f"🏢 {d_row['account_label']} | 👤 {d_row['member']}")
                    c2.write(f":grey[{d_row['import_date']}]")
                    if c3.button("🗑️", key=f"del_dup_{d_row['id']}"):
                        delete_transaction_by_id(d_row['id'])
                        st.toast("Transaction supprimée")
                        st.rerun()
                
                if st.button("🪄 Garder un seul (Auto)", key=f"clean_grp_{i}"):
                    to_delete = details.iloc[1:]['id'].tolist()
                    deleted_count = 0
                    for tid in to_delete:
                        deleted_count += delete_transaction_by_id(tid)
                    st.toast(f"✅ {deleted_count} doublons supprimés.", icon="🪄")
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
            st.warning(f"**{len(missing_t)}** transactions ressemblent à des virements mais n'ont pas la catégorie 'Virement Interne'.")
            
            # Grouping Logic
            missing_t['clean'] = missing_t['label'].apply(clean_label)
            
            exact_groups = missing_t.groupby('clean')
            final_groups = {}
            
            for label, group in exact_groups:
                found_match = False
                for existing_label in final_groups.keys():
                    similarity = difflib.SequenceMatcher(None, label, existing_label).ratio()
                    if similarity >= 0.8:
                        final_groups[existing_label] = pd.concat([final_groups[existing_label], group])
                        found_match = True
                        break
                
                if not found_match:
                    final_groups[label] = group
            
            # Display groups
            with st.expander("Voir et corriger les groupes de virements", expanded=True):
                all_categories = get_categories()
                default_cat = "Virement Interne" if "Virement Interne" in all_categories else all_categories[0]
                
                for label, group in final_groups.items():
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([2, 1, 1])
                        count = len(group)
                        total_amount = group['amount'].sum()
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
                            label_visibility="collapsed"
                        )
                        
                        if c3.button(f"Tout corriger", key=f"bulk_fix_{safe_key}"):
                            tx_ids = group['id'].tolist()
                            bulk_update_transaction_status(tx_ids, target_cat)
                            st.toast(f"✅ Corrigé ! {len(tx_ids)} tx en '{target_cat}'", icon="🔄")
                            st.rerun()
                        
                        # Show individual transactions if user wants
                        if st.checkbox(f"Détails", key=f"show_detail_{label}"):
                            for _, row in group.iterrows():
                                st.write(f"  • {row['date']} • {row['label']} • {row['amount']:.2f}€")
        
        if not wrong_t.empty:
            st.info(f"**{len(wrong_t)}** transactions sont catégorisées 'Virement Interne' mais n'en ont pas l'air.")
            with st.expander("Voir les virements douteux"):
                for _, row in wrong_t.iterrows():
                    st.write(f"❓ {row['date']} • **{row['label']}** • {row['amount']:.2f}€")

    # --- CARD SUGGESTIONS ---
    st.divider()
    st.subheader("💳 Suggestions de Membres (Cartes)")
    st.markdown("Numéros de carte détectés dans vos libellés qui ne sont pas encore associés à un membre.")
    
    suggestions = get_suggested_mappings()
    if suggestions.empty:
        st.success("Toutes vos cartes semblent déjà mappées ! ✨")
    else:
        for _, row in suggestions.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 2, 1])
                c1.write(f"💳 Carte **{row['card_suffix']}**")
                c1.caption(f"Vue {row['occurrence']} fois (ex: {row['example_label']})")
                
                members_list = sorted(get_members()['name'].tolist())
                target_m = c2.selectbox("Attribuer à", members_list, key=f"sugg_m_{row['card_suffix']}", label_visibility="collapsed")
                
                if c3.button("Associer", key=f"btn_sugg_{row['card_suffix']}", use_container_width=True):
                    add_member_mapping(row['card_suffix'], target_m)
                    st.toast(f"✅ Carte {row['card_suffix']} associée à {target_m} !", icon="💳")
                    st.rerun()
