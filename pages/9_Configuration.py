import streamlit as st
import os
import pandas as pd
import shutil
import sqlite3
import difflib
from modules.ui import load_css
from modules.utils import clean_label
from modules.data_manager import (
    get_members, add_member, delete_member, init_db, DB_PATH, 
    get_available_months, get_categories_df, add_category, 
    delete_category, update_category_emoji, update_category_fixed, 
    get_member_mappings_df, add_member_mapping, delete_member_mapping, 
    get_all_transactions, delete_transactions_by_period, get_all_tags, 
    remove_tag_from_all_transactions, get_learning_rules, delete_learning_rule, 
    rename_member, merge_categories, get_categories, get_orphan_labels, 
    auto_fix_common_inconsistencies, update_member_type, 
    delete_and_replace_label, get_duplicates_report, 
    get_transactions_by_criteria, delete_transaction_by_id, 
    get_suggested_mappings, get_transfer_inconsistencies, 
    update_transaction_category
)

# Page Setup
st.set_page_config(page_title="Configuration", page_icon="⚙️")
load_css()
init_db() # Ensure tables exist

st.title("⚙️ Configuration")

# TABS
tab_api, tab_members, tab_cats, tab_tags_rules, tab_audit, tab_data = st.tabs(["🔑 API & Services", "🏠 Foyer & Membres", "🏷️ Catégories", "🧠 Tags & Règles", "🧹 Audit & Nettoyage", "💾 Données & Danger"])

# --- TAB 1: API ---
with tab_api:
    st.header("🤖 Cerveau IA")
    st.markdown("Choisissez quel moteur d'intelligence artificielle pilote votre assistant.")
    
    # helper to read env
    def load_env_vars():
        vars = {}
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        vars[k] = v
        return vars

    env_vars = load_env_vars()
    
    # Provider Selection
    PROVIDERS = ["Gemini", "Ollama", "DeepSeek", "OpenAI"]
    current_provider = env_vars.get("AI_PROVIDER", "Gemini").capitalize()
    if current_provider not in PROVIDERS:
        current_provider = "Gemini"
        
    selected_provider = st.selectbox("Fournisseur IA", PROVIDERS, index=PROVIDERS.index(current_provider))
    
    st.divider()
    
    # Form based on selection
    with st.form("ai_config"):
        new_env = env_vars.copy()
        new_env["AI_PROVIDER"] = selected_provider.lower()
        
        if selected_provider == "Gemini":
            st.info("Le modèle standard : Rapide, performant et gratuit/pas cher.")
            val = st.text_input("Clé API Google Gemini", value=env_vars.get("GEMINI_API_KEY", ""), type="password")
            new_env["GEMINI_API_KEY"] = val
            
        elif selected_provider == "Ollama":
            st.info("🔒 100% Local & Privé. Assurez-vous qu'Ollama tourne sur votre machine.")
            url = st.text_input("URL du serveur Ollama", value=env_vars.get("OLLAMA_URL", "http://localhost:11434"))
            new_env["OLLAMA_URL"] = url
            # Model selection could be dynamic here but let's stick to env var for simplicity or hardcode defaults in manager
            # Maybe add a model name field?
            
        elif selected_provider == "DeepSeek":
            st.info("Performance coût/efficacité redoutable.")
            val = st.text_input("Clé API DeepSeek", value=env_vars.get("DEEPSEEK_API_KEY", ""), type="password")
            new_env["DEEPSEEK_API_KEY"] = val
            
        elif selected_provider == "OpenAI":
            st.info("Le standard de l'industrie (GPT-4 / GPT-3.5).")
            val = st.text_input("Clé API OpenAI", value=env_vars.get("OPENAI_API_KEY", ""), type="password")
            new_env["OPENAI_API_KEY"] = val
            
        # Common: Model Name Override
        st.subheader("Options Avancées")
        model_val = st.text_input("Nom du modèle (laisser vide pour défaut)", value=env_vars.get("AI_MODEL_NAME", ""), help="Ex: llama3, gpt-4o, gemini-1.5-pro")
        new_env["AI_MODEL_NAME"] = model_val

        if st.form_submit_button("Sauvegarder et Appliquer", type="primary"):
            # Write .env
            with open(".env", "w") as f:
                for k, v in new_env.items():
                    if v: # Only write if not empty? Or write empty string? Better write all to be clear.
                        f.write(f"{k}={v}\n")
            
            # Update OS environ for immediate effect
            for k, v in new_env.items():
                os.environ[k] = v
                
            st.success(f"Configuration IA mise à jour ! Mode : {selected_provider}")

# --- TAB 2: MEMBERS ---
with tab_members:
    st.header("Membres du Foyer")
    st.markdown("Définissez les personnes associées à ce compte pour l'attribution des dépenses.")
    
    members_df = get_members()
    
    col_list, col_add = st.columns([1, 1])
    
    with col_list:
        if members_df.empty:
            st.info("Aucun membre configuré.")
        else:
            if 'editing_member_id' not in st.session_state:
                st.session_state['editing_member_id'] = None
                
            # --- HOUSEHOLD GROUP ---
            foyer_df = members_df[members_df['member_type'] == 'HOUSEHOLD']
            st.subheader("🏘️ Membres du Foyer")
            if foyer_df.empty:
                st.caption("Aucun membre du foyer.")
            else:
                for index, row in foyer_df.iterrows():
                    member_id, member_name = row['id'], row['name']
                    if st.session_state['editing_member_id'] == member_id:
                        c1, c2, c3 = st.columns([3, 0.5, 0.5])
                        with c1: st.text_input("Nom", value=member_name, key=f"edit_in_{member_id}", label_visibility="collapsed")
                        with c2: 
                            if st.button("✅", key=f"sv_{member_id}"):
                                rename_member(member_name, st.session_state[f"edit_in_{member_id}"])
                                st.session_state['editing_member_id'] = None
                                st.rerun()
                        with c3:
                            if st.button("❌", key=f"cl_{member_id}"):
                                st.session_state['editing_member_id'] = None
                                st.rerun()
                    else:
                        c1, c2, c3, c4 = st.columns([3, 1, 0.5, 0.5])
                        c1.write(f"👤 **{member_name}**")
                        if c2.button("➡️ Tiers", key=f"to_ext_{member_id}", help="Déplacer vers Tiers"):
                            update_member_type(member_id, 'EXTERNAL')
                            st.rerun()
                        if c3.button("✏️", key=f"ed_{member_id}"):
                            st.session_state['editing_member_id'] = member_id
                            st.rerun()
                        if c4.button("🗑️", key=f"dl_{member_id}"):
                            delete_member(member_id); st.rerun()

            # --- EXTERNAL GROUP ---
            st.divider()
            tiers_df = members_df[members_df['member_type'] == 'EXTERNAL']
            st.subheader("👤 Tiers (Externes)")
            st.caption("Organismes ou personnes externes (CPAM, LBC, Impôts, Amis...)")
            if tiers_df.empty:
                st.caption("Aucun tiers configuré.")
            else:
                for index, row in tiers_df.iterrows():
                    member_id, member_name = row['id'], row['name']
                    c1, c2, c3, c4 = st.columns([3, 1, 0.5, 0.5])
                    c1.write(f"💼 {member_name}")
                    if c2.button("🏘️ Foyer", key=f"to_ho_{member_id}", help="Déplacer vers Foyer"):
                        update_member_type(member_id, 'HOUSEHOLD')
                        st.rerun()
                    if c3.button("✏️", key=f"ed_e_{member_id}"):
                        st.session_state['editing_member_id'] = member_id
                        st.rerun()
                    if c4.button("🗑️", key=f"dl_e_{member_id}"):
                        delete_member(member_id); st.rerun()

    with col_add:
        st.subheader("Ajouter un membre / tiers")
        with st.form("add_member_form"):
            new_name = st.text_input("Nom", placeholder="Ex: CPAM, Jean-Marc...")
            new_type = st.radio("Type", ["Membres du Foyer", "Tiers (Externe)"], horizontal=True)
            if st.form_submit_button("Ajouter"):
                if new_name:
                    m_type = 'EXTERNAL' if "Tiers" in new_type else 'HOUSEHOLD'
                    if add_member(new_name, m_type):
                        st.success(f"'{new_name}' ajouté !")
                        st.rerun()
                    else:
                        st.error("Ce membre existe déjà.")
                else:
                    st.warning("Veuillez entrer un nom.")

    st.divider()
    st.subheader("💳 Correspondance des Cartes")
    st.markdown("Associez un numéro de carte (4 derniers chiffres) à un membre pour l'import automatique.")
    
    from modules.data_manager import apply_member_mappings_to_pending
    if st.button("🔄 Appliquer les correspondances aux transactions en attente", help="Reparcourt toutes les transactions non validées pour mettre à jour le payeur selon votre configuration actuelle."):
        count = apply_member_mappings_to_pending()
        st.success(f"{count} transaction(s) mise(s) à jour !")
        st.rerun()
    
    mapping_df = get_member_mappings_df()
    
    col_m1, col_m2 = st.columns([1, 1])
    with col_m1:
        if mapping_df.empty:
            st.info("Aucune correspondance configurée.")
        else:
            for index, row in mapping_df.iterrows():
                cm1, cm2 = st.columns([3, 1])
                cm1.write(f"💳 **{row['card_suffix']}** ➔ {row['member_name']}")
                if cm2.button("🗑️", key=f"del_map_{row['id']}"):
                    delete_member_mapping(row['id'])
                    st.rerun()
    
    with col_m2:
        with st.form("add_mapping_form"):
            suffix = st.text_input("4 derniers chiffres", placeholder="Ex: 6759")
            m_name = st.selectbox("Membre", members_df['name'].tolist() if not members_df.empty else ["Anonyme"])
            if st.form_submit_button("Ajouter la carte"):
                if suffix and m_name:
                    add_member_mapping(suffix, m_name)
                    st.success("Mise à jour effectuée !")
                    st.rerun()

# --- TAB 3: CATEGORIES ---
with tab_cats:
    st.header("Gestion des Catégories")
    st.markdown("Personnalisez les catégories de dépenses pour votre budget.")
    
    # List categories
    cats_df = get_categories_df()
    
    col_list_cat, col_add_cat = st.columns([1, 1])
    
    with col_list_cat:
        st.subheader("Catégories existantes")
        if cats_df.empty:
            st.info("Aucune catégorie configurée.")
        else:
            for index, row in cats_df.iterrows():
                with st.expander(f"{row['emoji']} {row['name']} {' (Fixe)' if row['is_fixed'] else ''}", expanded=False):
                    c1, c2 = st.columns([3, 1])
                    new_emoji = c1.text_input("Emoji", value=row['emoji'], key=f"emoji_val_{row['id']}")
                    is_fixed = c1.checkbox("Dépense Fixe (ex: Loyer, Abonnement)", value=bool(row['is_fixed']), key=f"fixed_val_{row['id']}")
                    
                    suggested_tags_val = row.get('suggested_tags', '') if row.get('suggested_tags') else ''
                    new_suggested_tags = c1.text_input("Tags suggérés (séparés par des virgules)", value=suggested_tags_val, key=f"tags_val_{row['id']}")
                    
                    if c1.button("Mettre à jour", key=f"upd_cat_{row['id']}"):
                        update_category_emoji(row['id'], new_emoji)
                        update_category_fixed(row['id'], int(is_fixed))
                        from modules.data_manager import update_category_suggested_tags
                        update_category_suggested_tags(row['id'], new_suggested_tags)
                        st.rerun()
                    
                    if c2.button("🗑️ Supprimer", key=f"del_cat_{row['id']}"):
                        delete_category(row['id'])
                        st.rerun()

    with col_add_cat:
        st.subheader("Ajouter une catégorie")
        with st.form("add_cat_form"):
            col_a1, col_a2, col_a3 = st.columns([3, 1, 1])
            new_cat_name = col_a1.text_input("Nom de la catégorie", placeholder="Ex: Enfants...")
            new_cat_emoji = col_a2.text_input("Emoji", value="🏷️")
            new_is_fixed = col_a3.checkbox("Fixe", value=False)
            
            if st.form_submit_button("Ajouter"):
                if new_cat_name:
                    if add_category(new_cat_name, new_cat_emoji, int(new_is_fixed)):
                        st.success(f"Catégorie '{new_cat_name}' ajoutée !")
                        st.rerun()
                    else:
                        st.error("Cette catégorie existe déjà.")
                    st.warning("Veuillez entrer un nom.")
    
                    st.warning("Veuillez entrer un nom.")


# --- TAB 4: TAGS & RULES ---
with tab_tags_rules:
    col_tr1, col_tr2 = st.columns([1, 1])
    
    # --- TAGS ---
    with col_tr1:
        st.header("🏷️ Gestion des Tags")
        st.markdown("Liste des tags utilisés dans vos transactions.")
        
        all_tags = get_all_tags()
        if not all_tags:
            st.info("Aucun tag trouvé.")
        else:
            # Paging or scrolling logic if too many? For now list all.
            # Use a container with fixed height if list is huge?
            with st.container(height=500):
                for tag in all_tags:
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"🔹 **{tag}**")
                    if c2.button("🗑️", key=f"del_tag_{tag}", help=f"Supprimer le tag '{tag}' de toutes les transactions"):
                        count = remove_tag_from_all_transactions(tag)
                        st.success(f"Tag '{tag}' retiré de {count} transactions.")
                        st.rerun()

    # --- RULES ---
    with col_tr2:
        st.header("🧠 Règles d'Apprentissage")
        st.markdown("Historique des associations mémorisées (Tiers -> Catégorie).")
        
        rules_df = get_learning_rules()
        if rules_df.empty:
            st.info("Aucune règle mémorisée.")
        else:
             with st.container(height=500):
                 for index, row in rules_df.iterrows():
                     c1, c2 = st.columns([3, 1])
                     c1.markdown(f"**{row['pattern']}** ➔ {row['category']}")
                     if c2.button("🗑️", key=f"del_rule_{row['id']}"):
                         delete_learning_rule(row['id'])
                         st.rerun()

# --- TAB 5: AUDIT & CLEANUP ---
with tab_audit:
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
            from modules.backup_manager import create_backup
            create_backup(label="pre_magic_fix")
            count = auto_fix_common_inconsistencies()
            if count > 0:
                st.success(f"Fait ! {count} corrections/nettoyages effectués.")
            else:
                st.info("Tout semble déjà propre ! ✨")
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
                    st.success(f"'{orphan}' ➔ '{target}' ({count} transactions)")
                    st.rerun()
            
            with c4:
                if st.button("👥 Tiers", key=f"btn_tiers_{i}", help="Enregistrer comme nouveau Tiers officiel"):
                    add_member(orphan, 'EXTERNAL')
                    st.success(f"'{orphan}' ajouté aux Tiers !")
                    st.rerun()
            
            with c5:
                if st.button("🗑️", key=f"btn_del_{i}", help="Supprimer partout et remplacer par 'Inconnu'"):
                    count = delete_and_replace_label(orphan, "Inconnu")
                    st.success(f"'{orphan}' supprimé ({count} transactions nettoyées)")
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
                st.success(f"✅ {result['transactions']} transactions transférées !")
                st.rerun()
            else:
                st.warning("Veuillez sélectionner deux catégories différentes.")

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
                    # Keep the one with highest ID or lowest ID? Let's say keeping the first imported or last.
                    # Usually better to keep the one that might have been validated.
                    # But let's just keep the first one for simplicity.
                    to_delete = details.iloc[1:]['id'].tolist()
                    deleted_count = 0
                    for tid in to_delete:
                        deleted_count += delete_transaction_by_id(tid)
                    st.success(f"{deleted_count} doublons supprimés.")
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
            
            # --- Grouping Logic ---
            missing_t['clean'] = missing_t['label'].apply(clean_label)
            groups = []
            
            # Group by exact cleaned label first
            exact_groups = missing_t.groupby('clean')
            
            # Process groups for similarity
            processed_labels = []
            final_groups = {} # clean_label -> list of rows
            
            for label, group in exact_groups:
                found_match = False
                for existing_label in final_groups.keys():
                    # Similarity check
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

                        target_cat = c2.selectbox(
                            "Catégorie", 
                            all_categories, 
                            index=all_categories.index(group_default),
                            key=f"bulk_cat_{label}",
                            label_visibility="collapsed"
                        )
                        
                        if c3.button(f"Tout corriger", key=f"bulk_fix_{label}"):
                            from modules.data_manager import bulk_update_transaction_status
                            bulk_update_transaction_status(group['id'].tolist(), target_cat)
                            st.success(f"Groupe '{label}' corrigé en '{target_cat}' !")
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
                    st.success(f"Carte {row['card_suffix']} associée à {target_m} !")
                    st.rerun()

# --- TAB 6: DATA ---
with tab_data:
    st.header("💾 Sauvegardes")
    st.markdown("L'application effectue une sauvegarde automatique chaque jour.")
    
    from modules.backup_manager import list_backups, restore_backup, create_backup
    
    backups = list_backups()
    
    if backups:
        # Mini dashboard for backups
        st.caption(f"**{len(backups)}** sauvegardes disponibles (Rétention : 1 an)")
        
        # Display as a table with actions
        df_bkp = pd.DataFrame(backups)
        df_bkp['Taille'] = df_bkp['size'].apply(lambda x: f"{x/1024:.0f} KB")
        df_bkp['Date'] = df_bkp['date'].dt.strftime('%d/%m/%Y %H:%M')
        
        # We'll use a loop to provide a restore button for each
        for b in backups[:10]: # Show last 10
            c1, c2, c3 = st.columns([2, 1, 1])
            c1.write(f"📄 {b['date'].strftime('%d/%m/%Y %H:%M')}")
            c2.write(f"{b['size']/1024:.0f} KB")
            if c3.button("Restaurer", key=f"restore_{b['filename']}", help="Restaurer cette version (une sécurité sera créée avant)"):
                success, msg = restore_backup(b['filename'])
                if success:
                    st.success(msg)
                    st.balloons()
                    st.cache_data.clear() # Clear streamlit cache
                else:
                    st.error(msg)
        
        if len(backups) > 10:
            st.info("Plus de sauvegardes sont disponibles dans le dossier Data/backups.")
            
    else:
        st.info("Aucune sauvegarde trouvée.")
        
    if st.button("Lancer une sauvegarde manuelle 🛡️"):
        path = create_backup(label="manual")
        if path:
            st.success(f"Sauvegarde créée avec succès !")
            st.rerun()

    st.divider()
    st.header("📤 Export des Données")
    
    df_all = get_all_transactions()
    
    csv = df_all.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger tout (CSV)",
        data=csv,
        file_name='finance_export_complet.csv',
        mime='text/csv',
    )
    
    st.divider()
    
    st.header("🔥 Zone de Danger")
    st.warning("Actions irréversibles. Manipulez avec précaution.")
    
    with st.expander("Supprimer des données"):
        months = get_available_months()
        
        if months:
            target_month = st.selectbox("Sélectionner le mois à supprimer", months)
            if st.button(f"🗑️ Supprimer tout le mois {target_month}", type="secondary"):
                deleted = delete_transactions_by_period(target_month)
                st.success(f"{deleted} transactions supprimées pour {target_month}.")
                st.rerun()
        else:
            st.write("Aucune donnée à supprimer.")

        st.divider()
        
        if st.checkbox("Je veux vider TOUTE la base de données (Reset Total)"):
            if st.button("💣 TOUT EFFACER", type="primary"):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("DELETE FROM transactions")
                c.execute("DELETE FROM learning_rules")
                c.execute("DELETE FROM budgets")
                c.execute("DELETE FROM members")
                conn.commit()
                conn.close()
                st.error("Base de données entièrement vidée.")
                st.rerun()
