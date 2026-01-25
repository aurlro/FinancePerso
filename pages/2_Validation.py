import streamlit as st
from modules.categorization import predict_category_ai

from modules.data_manager import add_learning_rule, get_pending_transactions, update_transaction_category, get_members, update_transaction_member, init_db, get_categories, get_categories_with_emojis, bulk_update_transaction_status, get_all_tags, get_all_account_labels, mark_transaction_as_ungrouped, get_categories_suggested_tags
from modules.ui import load_css
from modules.utils import clean_label
import re
import pandas as pd

st.set_page_config(page_title="Validation", page_icon="✅", layout="wide")
load_css()
init_db()  # Ensure tables exist

if 'excluded_tx_ids' not in st.session_state:
    st.session_state['excluded_tx_ids'] = set()

# Helper for validation with optional memory
def validate_with_memory(tx_ids, label, category, remember, member_update=None, tags=None, beneficiary=None):
    if remember:
        # Pattern from the representative label
        pattern = re.sub(r'(?i)CARTE|CB\*?\d*|\d{2}/\d{2}/\d{2}', '', label).strip()
        clean_pattern = re.sub(r'[^a-zA-Z\s]', '', pattern).strip().upper()
        clean_pattern = re.sub(r'\s+', ' ', clean_pattern)
        
        if len(clean_pattern) > 2:
            add_learning_rule(clean_pattern, category)
            
    bulk_update_transaction_status(tx_ids, category, tags=tags, beneficiary=beneficiary)
    if member_update:
        for tx_id in tx_ids:
            update_transaction_member(tx_id, member_update)

# --- CSS INJECTION FOR GREEN BUTTONS ---
st.markdown("""
<style>
div[data-testid="stButton"] button[kind="primary"] {
    background-color: #22c55e;
    border-color: #22c55e;
    color: white;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    background-color: #16a34a;
    border-color: #16a34a;
    color: white;
}

/* SMART VISIBILITY: Hide the blind-validation button (Column 2) if Expander (Column 1) is Open */
div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:first-child details[open]) div[data-testid="column"]:nth-child(2) button {
    display: none;
}
</style>
""", unsafe_allow_html=True)

st.title("✅ Validation des dépenses")

# Load data
df = get_pending_transactions()
members_raw = get_members()
all_members = members_raw['name'].tolist()
member_type_map = dict(zip(members_raw['name'], members_raw['member_type']))

if not all_members:
    all_members = ["Aurélien", "Élise", "Compte Joint"]
    member_type_map = {m: 'HOUSEHOLD' for m in all_members}


if df.empty:
    st.success("Toutes les transactions sont validées ! 🎉")
else:
    # Filters in Sidebar
    with st.sidebar:
        st.header("🔍 Filtres")
        filtered_df = df.copy()
        
        if 'account_label' in df.columns:
            accounts = sorted(df['account_label'].unique().tolist())
            sel_acc = st.multiselect("Par Compte", accounts)
            if sel_acc:
                filtered_df = filtered_df[filtered_df['account_label'].isin(sel_acc)]
                
        if 'member' in df.columns:
            members = sorted([m for m in df['member'].unique() if m])
            sel_mem = st.multiselect("Par Membre", members)
            if sel_mem:
                filtered_df = filtered_df[filtered_df['member'].isin(sel_mem)]
                
        st.divider()
        st.caption("💡 Astuce : Le regroupement intelligent fusionne les opérations identiques pour une validation plus rapide.")

    col_sort1, col_sort2, col_sort3 = st.columns([2, 1, 1])
    with col_sort1:
        sort_options = {
            "Gros groupes (Défaut)": "count",
            "Plus récentes": "date_recent",
            "Plus anciennes": "date_old",
            "Montant (Décroissant)": "amount_desc",
            "Montant (Croissant)": "amount_asc"
        }
        sort_choice = st.selectbox("Trier par", list(sort_options.keys()), label_visibility="visible")
        sort_key = sort_options[sort_choice]

    with col_sort2:
        st.markdown(f"<p style='margin-top:28px; font-weight:600; color:#64748B;'>{len(filtered_df)} en attente</p>", unsafe_allow_html=True)
    
    with col_sort3:
        with st.popover("❓ Aide", use_container_width=True):
            st.info("""
            **Virement Interne** (🔄) : Pour les transferts entre vos comptes suivis. Exclu des graphiques de dépenses.
            
            **Dégrouper** : Si une opération dans un groupe est différente, utilisez le bouton dans 'Détails' pour l'isoler.
            """)
    
    # --- PROGRESS BAR GAMIFICATION ---
    total_pending = len(filtered_df)
    if 'initial_pending_count' not in st.session_state or total_pending > st.session_state['initial_pending_count']:
        st.session_state['initial_pending_count'] = total_pending
    
    init_count = st.session_state['initial_pending_count']
    if init_count > 0:
        progress = 1.0 - (total_pending / init_count)
        done_count = init_count - total_pending
        st.progress(progress, text=f"Progression : {done_count} traitées sur {init_count} 💪")
    
    st.divider()

    # Helper callback for AI update
    def run_ai_categorization(tx_id, label, amount, date):
        key = f"cat_{tx_id}"
        cat, conf = predict_category_ai(label, amount, date)
        st.session_state[key] = cat
        st.toast(f"🪄 IA : Catégorie '{cat}' suggérée", icon="✨")

    # Display list
    # Optimize: pagination or limit if too many
    cat_emoji_map = get_categories_with_emojis()
    cat_suggested_tags = get_categories_suggested_tags()
    available_categories = sorted(list(cat_emoji_map.keys()))
    
    # Unified list for "Who paid" and "For whom"
    base_options = ["", "Famille", "Maison"]
    full_member_list = sorted(list(set(base_options + all_members)))

    all_acc_labels = get_all_account_labels()
    from modules.data_manager import get_member_mappings
    active_card_maps = get_member_mappings()
    
    # Store temporary tags created during session
    if 'temp_custom_tags' not in st.session_state:
        st.session_state['temp_custom_tags'] = []
    
    # Store pending tag additions per group (for auto-select)
    if 'pending_tag_additions' not in st.session_state:
        st.session_state['pending_tag_additions'] = {}
        
    # --- BULK SELECTION STATE ---
    if 'bulk_selected_groups' not in st.session_state:
        st.session_state['bulk_selected_groups'] = set()

    # --- BULK ACTION BAR ---
    if st.session_state['bulk_selected_groups']:
        count_sel = len(st.session_state['bulk_selected_groups'])
        with st.container():
            st.info(f"⚡ **{count_sel} groupes sélectionnés**")
            b_c1, b_c2, b_c3 = st.columns([2, 1, 1])
            with b_c1:
                bulk_cat = st.selectbox("Appliquer Catégorie", available_categories, key="bulk_cat_select")
            with b_c2:
                if st.button("Appliquer", type="primary", key="btn_apply_bulk"):
                    for grp_id_list in st.session_state['bulk_selected_groups']:
                        # The set stores tuples of IDs, or we need a map. 
                        # Let's store just the group identifier or list of IDs? 
                        # Ideally we stored list of IDs. But set needs hashable. 
                        # We will convert list to tuple for storage.
                        # Wait, we need to know WHICH transactions.
                        # Ideally `bulk_selected_groups` stores group_names (clean_group) or we re-fetch?
                        # Simpler: Store tuple of IDs.
                        tx_ids = list(grp_id_list)
                        bulk_update_transaction_status(tx_ids, bulk_cat)
                        
                    st.success(f"Catégorie '{bulk_cat}' appliquée à {count_sel} groupes !")
                    st.session_state['bulk_selected_groups'] = set()
                    st.rerun()
            with b_c3:
                if st.button("Désélectionner", key="btn_clear_bulk"):
                    st.session_state['bulk_selected_groups'] = set()
                    st.rerun()
            st.divider()

    @st.fragment
    def show_validation_list(filtered_df, all_acc_labels, all_members, available_categories, cat_emoji_map, sort_key, active_card_maps, key_suffix=""):
        # Local grouping logic inside fragment to respond to isolation
        def get_smart_group(row):
            # Check DB flag (if exists in DF) OR Session state
            is_ungrouped_db = row.get('is_manually_ungrouped', 0) == 1
            if is_ungrouped_db or row['id'] in st.session_state['excluded_tx_ids']:
                return f"single_{row['id']}"
            
            lbl = str(row['label']).upper()
            
            # Detect Cheque keywords (CHQ, CHEQUE, REMISE CHEQUE/CHQ)
            # We want to group by [Cleaned Label + Amount] to separate different cheques
            if re.search(r'\b(CHQ|CHEQUE|REMISE\s+CHEQUE|REMISE\s+CHQ)\b', lbl):
                 return f"{clean_label(row['label'])} | {row['amount']:.2f} €"
                
            return clean_label(row['label'])

        local_df = filtered_df.copy()
        # Force ID to int for consistency
        local_df['id'] = local_df['id'].astype(int)
        local_df['clean_group'] = local_df.apply(get_smart_group, axis=1)
        
        # Calculate group stats for sorting
        group_stats = local_df.groupby('clean_group').agg({
            'id': 'size',
            'date': 'max',
            'amount': lambda x: x.abs().max()
        }).reset_index()
        group_stats.columns = ['clean_group', 'count', 'max_date', 'max_amount']
        
        group_stats['is_single'] = group_stats['clean_group'].apply(lambda x: 1 if str(x).startswith("single_") else 0)
        
        # Apply sorting
        if sort_key == "count":
            sorted_groups = group_stats.sort_values(by=['is_single', 'count'], ascending=[False, False])
        elif sort_key == "date_recent":
            sorted_groups = group_stats.sort_values(by=['is_single', 'max_date'], ascending=[False, False])
        elif sort_key == "date_old":
            sorted_groups = group_stats.sort_values(by=['is_single', 'max_date'], ascending=[False, True])
        elif sort_key == "amount_desc":
            sorted_groups = group_stats.sort_values(by=['is_single', 'max_amount'], ascending=[False, False])
        elif sort_key == "amount_asc":
            sorted_groups = group_stats.sort_values(by=['is_single', 'max_amount'], ascending=[False, True])
        
        MAX_GROUPS = 40
        display_groups = sorted_groups['clean_group'].tolist()[:MAX_GROUPS]
        
        if len(sorted_groups) > MAX_GROUPS:
            st.info(f"Affichage des {MAX_GROUPS} premiers groupes (sur {len(sorted_groups)}). Validez-les pour voir la suite.")

        for group_name in display_groups:
            group_df = local_df[local_df['clean_group'] == group_name]
            # Representative row (first one)
            row = group_df.iloc[0]
            group_ids = group_df['id'].tolist()
            group_count = len(group_df)
            group_total = group_df['amount'].sum()
            group_id = row['id']
            
            # --- PRE-COMPUTE STATE & LABELS ---
            # We need these BEFORE the UI to allow "Blind Validation" (External Button)
            
            # 1. Cleaned Title
            display_title = clean_label(row['label'])
            
            # 2. Category State
            cat_key = f"cat_{row['id']}{key_suffix}"
            if cat_key not in st.session_state:
                current_cat = row.get('category_validated') if row.get('category_validated') != 'Inconnu' else (row['original_category'] or "Inconnu")
                st.session_state[cat_key] = current_cat if current_cat in available_categories else "Inconnu"
            
            # 3. Payeur/Benef Default State (Logic moved up for availability)
            current_member = row.get('member', '')
            suffix = row.get('card_suffix')
            if suffix and suffix in active_card_maps:
                current_member = active_card_maps[suffix]
            if not current_member or current_member == 'Inconnu':
                acc_label = str(row.get('account_label', '')).lower()
                if 'joint' in acc_label:
                    current_member = "Duo"
                elif 'aurélien' in acc_label or 'aurelien' in acc_label:
                    current_member = "Aurélien"
                else:
                    current_member = ""
            
            current_benef = row.get('beneficiary', 'Famille') # Default
            if not current_benef: current_benef = ""
            
            # 4. Tags State
            current_tags_str = row.get('tags', '') if row.get('tags') else ""
            current_tags = [t.strip() for t in current_tags_str.split(',') if t.strip()]
            
            # AUTOMATION: Remboursement for positive "Avoir"
            if group_total > 0 and "AVOIR" in str(row['label']).upper() and "Remboursement" not in current_tags:
                current_tags.append("Remboursement")
            
            # Add pending tags for this group (for auto-select after creation)
            if group_id in st.session_state.get('pending_tag_additions', {}):
                pending = st.session_state['pending_tag_additions'][group_id]
                current_tags = list(set(current_tags + pending))  # Merge and dedupe
                # Clear pending after adding
                del st.session_state['pending_tag_additions'][group_id]

            # --- SMART EXPANDER LAYOUT ---
            # Columns: [Checkbox (5%)] [Expander (85%)] [Validate Button (10%)]
            c_chk, c_exp, c_btn = st.columns([0.05, 0.85, 0.10], vertical_alignment="top")
            
            group_ids_tuple = tuple(group_ids)
            is_selected = group_ids_tuple in st.session_state['bulk_selected_groups']
            
            with c_chk:
                st.markdown("<div style='height: 0.3rem;'></div>", unsafe_allow_html=True)
                if st.checkbox("Select", value=is_selected, key=f"d_chk_{group_id}{key_suffix}", label_visibility="collapsed"):
                    st.session_state['bulk_selected_groups'].add(group_ids_tuple)
                else:
                    if group_ids_tuple in st.session_state['bulk_selected_groups']:
                        st.session_state['bulk_selected_groups'].remove(group_ids_tuple)
            
            # Construct Label with Markdown
            # Pattern: :grey[Date] • **Title** • :color[**Amount**] :grey[(Count)]
            
            color_str = "red" if group_total < 0 else "green"
            count_str = f"({group_count})" if group_count > 1 else ""
            
            # Detect if this is a transfer (virement)
            label_upper = str(row['label']).upper()
            is_transfer = any(keyword in label_upper for keyword in ['VIR', 'VIREMENT', 'INST'])
            transfer_icon = "🔄 " if is_transfer else ""
            
            # Note: We replaced emojis for amount with color, but kept date formatting
            expander_label = f"{transfer_icon}:grey[{row['date']}] • **{display_title}** • :{color_str}[**{group_total:,.2f} €**] :grey[{count_str}]"
            
            # --- EXTERNAL VALIDATION (Blind) ---
            with c_btn:
                # Spacer to align with expander header roughly
                st.markdown("<div style='height: 0.2rem;'></div>", unsafe_allow_html=True)
                btn_key_ext = f"btn_ext_{group_id}{key_suffix}"
                # Use Icon Only Button
                if st.button("✅", key=btn_key_ext, help="Valider sans ouvrir", type="primary", use_container_width=True):
                    # Use defaults/current state
                    # Note: Inputs (SelectBox) might not be rendered yet if expander closed!
                    # So we use the PRE-COMPUTED/SessionState values.
                    
                    # For Payeur/Benef/Tags, if widget not rendered, use defaults from row or previous state if exists?
                    # Streamlit session state persists even if not rendered IF it was rendered before.
                    # If never rendered, we need valid defaults.
                    
                    # Logic: Use st.session_state if key exists (user modified before closed?), else default from row.
                    
                    # Payeur
                    mem_key = f"mem_sel_{group_id}{key_suffix}"
                    mem_input_key = f"mem_input_{group_id}{key_suffix}"
                    val_mem = st.session_state.get(mem_key, current_member)
                    if val_mem == "✍️ Saisie...": val_mem = st.session_state.get(mem_input_key, "")
                    
                    # Benef
                    ben_key = f"benef_sel_{group_id}{key_suffix}"
                    ben_input_key = f"benef_input_{group_id}{key_suffix}"
                    val_ben = st.session_state.get(ben_key, current_benef)
                    if val_ben == "✍️ Saisie...": val_ben = st.session_state.get(ben_input_key, "")
                    
                    # Tags
                    tag_key = f"tag_sel_{group_id}{key_suffix}"
                    val_tags = st.session_state.get(tag_key, current_tags)
                    val_tags_str = ", ".join(val_tags) if isinstance(val_tags, list) else ""
                    
                    # Memory
                    mem_check_key = f"mem_check_{group_id}{key_suffix}"
                    val_mem_check = st.session_state.get(mem_check_key, True)
                    
                    validate_with_memory(group_ids, row['label'], st.session_state[cat_key], val_mem_check, val_mem, tags=val_tags_str, beneficiary=val_ben)
                    st.toast(f"✅ Lot validé ({group_count} ops) !", icon="🚀")
                    if len(display_groups) == 1: st.balloons()
                    st.rerun()

            # --- EXPANDER CONTENT ---
            with c_exp:
                with st.expander(expander_label, expanded=False):
                    
                    # --- HEADER INFO INSIDE (Optional, maybe redundancy but good for context) ---
                    # Let's keep the Meta line: Date, Account, Badges
                    meta_items = [f"🏬 {row.get('account_label', 'Compte')}"]
                    if str(group_name).startswith("single_"): meta_items.append("📦 Isolée")
                    elif group_count > 1: meta_items.append(f"📦 {group_count} ops")
                    
                    # Transfer details (if detected)
                    if is_transfer:
                        source_account = row.get('account_label', 'Inconnu')
                        destination = current_benef if current_benef else "Inconnu"
                        meta_items.append(f"🔄 De : **{source_account}** → Vers : **{destination}**")
                    
                    st.caption(" • ".join(meta_items))
                    
                    # --- INPUTS ROW (Compact Step 2) ---
                    # [Category] [Payeur] [Benef] [Tags] [Actions]
                    ci_cat, ci_pay, ci_ben, ci_tags, ci_act = st.columns([3, 2, 2, 3, 2], vertical_alignment="bottom")
                    
                    with ci_cat:
                        # Category Select (Key already init above)
                        options = list(available_categories)
                        if row['original_category'] and row['original_category'] not in options: options.append(row['original_category'])
                        if st.session_state[cat_key] not in options: options.append(st.session_state[cat_key])
                        def format_cat(cat_name): return f"{cat_emoji_map.get(cat_name, '🏷️')} {cat_name}"
                        try: c_idx = options.index(st.session_state[cat_key])
                        except: c_idx = 0
                        st.selectbox("📂 Catégorie", options, index=c_idx, key=cat_key, format_func=format_cat)
                        
                    with ci_pay:
                        # Payeur
                        member_sel_key = f"mem_sel_{group_id}{key_suffix}"
                        member_input_key = f"mem_input_{group_id}{key_suffix}"
                        
                        pay_opts = sorted(list(set(all_members + ["Maison", "Famille"])))
                        if current_member and current_member not in pay_opts: pay_opts.append(current_member)
                        pay_opts.append("✍️ Saisie...")
                        try: p_idx = pay_opts.index(current_member) if current_member in pay_opts else 0
                        except: p_idx = 0
                        
                        def format_mem(name):
                            if name == "✍️ Saisie...": return "✍️ Saisie..."
                            if not name: return ""
                            m_type = member_type_map.get(name, 'HOUSEHOLD')
                            prefix = "🏘️" if m_type == 'HOUSEHOLD' else "💼"
                            if name in ["Maison", "Famille"]: prefix = "🏘️"
                            return f"{prefix} {name}"

                        pay_l = "👤 Bénéficiaire" if group_total > 0 else "👤 Payeur"
                        sel_p = st.selectbox(pay_l, pay_opts, index=p_idx, key=member_sel_key, format_func=format_mem)

                        if sel_p == "✍️ Saisie...":
                            member_val = st.text_input("Nom", key=member_input_key, label_visibility="collapsed")
                        else:
                            member_val = sel_p
                    
                    with ci_ben:
                        # Benef
                        beneficiary_key = f"benef_sel_{group_id}{key_suffix}"
                        beneficiary_input_key = f"benef_input_{group_id}{key_suffix}"
                        ben_opts = sorted(list(set(full_member_list + ["Maison", "Famille"])))
                        if current_benef and current_benef not in ben_opts: ben_opts.append(current_benef)
                        ben_opts.insert(0, "")
                        ben_opts.append("✍️ Saisie...")
                        
                        try:
                            if current_benef in ben_opts: b_idx = ben_opts.index(current_benef)
                            else: b_idx = ben_opts.index("Famille") if "Famille" in ben_opts else 0
                        except: b_idx = 0
                        
                        ben_l = "💰 Source" if group_total > 0 else "🎯 Pour qui ?"
                        sel_b = st.selectbox(ben_l, ben_opts, index=b_idx, key=beneficiary_key, format_func=format_mem)

                        if sel_b == "✍️ Saisie...":
                            beneficiary_val = st.text_input("Nom", key=beneficiary_input_key, label_visibility="collapsed")
                        else:
                            beneficiary_val = sel_b
                            
                    with ci_tags:
                        tag_key = f"tag_sel_{group_id}{key_suffix}"
                        # Split: Multiselect + Add Button
                        t_col1, t_col2 = st.columns([0.85, 0.15], vertical_alignment="bottom")
                        
                        existing_tags = get_all_tags()
                        current_cat_name = st.session_state[cat_key]
                        allowed_tags = cat_suggested_tags.get(current_cat_name, [])
                        
                        # Strict Mode Logic:
                        # If the category has specific rules (allowed_tags is not empty), we favor them.
                        # We always include:
                        # 1. Tags already on the transaction (current_tags)
                        # 2. Tags just created in this session (st.session_state['temp_custom_tags'])
                        # 3. Tags explicitly allowed/suggested for this category.
                        # If allowed_tags is empty, we fallback to showing ALL tags (permissive).
                        
                        if allowed_tags:
                            # Strict/Focused List
                            display_tags = sorted(list(set(allowed_tags + current_tags + st.session_state['temp_custom_tags'])))
                        else:
                            # Permissive List
                            display_tags = sorted(list(set(existing_tags + st.session_state['temp_custom_tags'] + current_tags)))
                        
                        with t_col1:
                             # We use display_tags as options. 
                             # Warning: if current_tags contains something not in display_tags (shouldn't happen due to set union), it crashes.
                             selected_tags = st.multiselect("🏷️ Tags", display_tags, default=current_tags, key=tag_key)
                        
                        with t_col2:
                             with st.popover("➕", use_container_width=True):
                                 new_tag_in = st.text_input("Nouveau tag", key=f"new_tag_{group_id}{key_suffix}")
                                 if st.button("Ajouter", key=f"add_tag_btn_{group_id}{key_suffix}"):
                                     if new_tag_in:
                                         # 1. Add to session state for immediate availability
                                         if new_tag_in not in st.session_state['temp_custom_tags']:
                                             st.session_state['temp_custom_tags'].append(new_tag_in)
                                         
                                         # 2. Persist strict association: Add this tag to the Category's allowed list
                                         from modules.data_manager import add_tag_to_category
                                         add_tag_to_category(current_cat_name, new_tag_in)
                                         
                                         # 3. Auto-select for this transaction
                                         if 'pending_tag_additions' not in st.session_state:
                                             st.session_state['pending_tag_additions'] = {}
                                         st.session_state['pending_tag_additions'][group_id] = [new_tag_in]
                                         
                                         st.toast(f"Tag '{new_tag_in}' créé et associé à '{current_cat_name}' !", icon="🔗")
                                         st.rerun()
                                          
                        # Show suggested tags for the category (Modern Layout with Pills)
                        current_cat_name = st.session_state[cat_key]
                        suggestions = cat_suggested_tags.get(current_cat_name, [])
                        if suggestions:
                            # Filter out tags already selected
                            filtered_sugg = [s for s in suggestions if s not in selected_tags]
                            if filtered_sugg:
                                # Use st.pills for better UX (requires streamlit >= 1.40, fallback to markdown if needed but pills is preferred)
                                # Since we want an Action (Add), we use selection combined with state check or callback simulation.
                                # Actually st.pills maintains selection. We want "click to add".
                                # If we use selection_mode="single", clicking selects it. We detect change and add it.
                                pill_key = f"pills_{group_id}{key_suffix}"
                                
                                # Hack: We want to detect a click. If st.pills returns a value that wasn't there, we add it.
                                # But st.pills persists state. We want it to reset?
                                # Alternative: Just use st.pills and if a value is selected, we consume it and rerun.
                                selected_pill = st.pills("Suggestions", filtered_sugg, selection_mode="single", key=pill_key, label_visibility="collapsed")
                                
                                if selected_pill:
                                    if 'pending_tag_additions' not in st.session_state:
                                        st.session_state['pending_tag_additions'] = {}
                                    if group_id not in st.session_state['pending_tag_additions']:
                                        st.session_state['pending_tag_additions'][group_id] = []
                                    
                                    # Add and reset
                                    st.session_state['pending_tag_additions'][group_id].append(selected_pill)
                                    # We can't easily clear the pill selection inside the run without a callback or key trick.
                                    # But rerun will rebuild the filtered_sugg list, removing the selected tag!
                                    # So the pill list changes, and selection might be lost or reset. Perfect.
                                    st.rerun()
                                         
                        final_tags_str = ", ".join(selected_tags)
                        
                    with ci_act:
                        remember = st.toggle("Mém.", key=f"mem_check_{group_id}{key_suffix}", value=True)
                        if st.button("Valider", key=f"btn_in_{group_id}{key_suffix}", type="primary", use_container_width=True):
                             validate_with_memory(group_ids, row['label'], st.session_state[cat_key], remember, member_val, tags=final_tags_str, beneficiary=beneficiary_val)
                             st.toast("✅ Modification validée !", icon="👍")
                             st.rerun()

                    # --- DETAILS LIST ---
                    st.divider()
                    st.caption(f"Détails des {group_count} opérations")
                    for _, sub_row in group_df.iterrows():
                         d_c1, d_c2, d_c3 = st.columns([3, 1, 0.5], vertical_alignment="center")
                         
                         # Col 1: Label + Date (small gray)
                         d_c1.markdown(f"**{sub_row['label']}**  \n:grey[{sub_row['date']}]")
                         
                         # Col 2: Amount (Colored)
                         color_sub = "red" if sub_row['amount'] < 0 else "green"
                         d_c2.markdown(f":{color_sub}[**{sub_row['amount']:.2f} €**]")
                         
                         # Col 3: Ungroup Button
                         if d_c3.button("❌", key=f"iso_{sub_row['id']}{key_suffix}", help="Exclure cette opération du groupe"):
                             # Persist to DB
                             mark_transaction_as_ungrouped(int(sub_row['id']))
                             # Update Session for immediate feedback
                             st.session_state['excluded_tx_ids'].add(int(sub_row['id']))
                             st.toast("✂️ Opération exclue définitivement", icon="❌")
                             st.rerun()
            
            # Separator between groups
            st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 0.5rem; opacity: 0.3;'>", unsafe_allow_html=True)
            

    # --- TABS FOR VALIDATION ---
    tab_all, tab_unknown = st.tabs(["📋 Toutes les opérations", "🔍 À identifier (Inconnu)"])

    with tab_all:
        show_validation_list(filtered_df, all_acc_labels, all_members, available_categories, cat_emoji_map, sort_key, active_card_maps, key_suffix="_all")

    with tab_unknown:
        # Filter for anything 'Inconnu'
        # 1. Category is Inconnu (or empty/None)
        # 2. Member is Inconnu (or empty/None)
        # 3. Beneficiary is Inconnu (or empty/None)
        unknown_mask = (
            (filtered_df['category_validated'].fillna('Inconnu') == 'Inconnu') |
            (filtered_df['member'].fillna('Inconnu').isin(['Inconnu', 'Anonyme', ''])) |
            (filtered_df['beneficiary'].fillna('Inconnu').isin(['Inconnu', 'Anonyme', '']))
        )
        unknown_df = filtered_df[unknown_mask]
        
        if unknown_df.empty:
            st.success("Toutes les opérations ont été identifiées ! ✨")
        else:
            show_validation_list(unknown_df, all_acc_labels, all_members, available_categories, cat_emoji_map, sort_key, active_card_maps, key_suffix="_unknown")
