import streamlit as st
from modules.categorization import predict_category_ai

from modules.data_manager import add_learning_rule, get_pending_transactions, update_transaction_category, get_unique_members, update_transaction_member, init_db, get_categories, get_categories_with_emojis, bulk_update_transaction_status, get_all_tags, get_all_account_labels
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

st.title("✅ Validation des dépenses")

# Load data
df = get_pending_transactions()
all_members = get_unique_members() # Get available members
if not all_members:
    all_members = ["Aurélien", "Élise", "Compte Joint"] # Fallback defaults

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
    available_categories = sorted(list(cat_emoji_map.keys()))
    
    # Unified list for "Who paid" and "For whom"
    base_options = ["", "Famille", "Maison"]
    full_member_list = sorted(list(set(base_options + all_members)))

    all_acc_labels = get_all_account_labels()
    from modules.data_manager import get_member_mappings
    active_card_maps = get_member_mappings()

    @st.fragment
    def show_validation_list(filtered_df, all_acc_labels, all_members, available_categories, cat_emoji_map, sort_key, active_card_maps):
        # Local grouping logic inside fragment to respond to isolation
        def get_smart_group(row):
            if row['id'] in st.session_state['excluded_tx_ids']:
                return f"single_{row['id']}"
            
            lbl = str(row['label']).upper()
            if "CHEQUE" in lbl:
                # Group checks by their amount as requested by user
                return f"CHEQUE_{row['amount']}"
                
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
            st.warning(f"Affichage des {MAX_GROUPS} premiers groupes (sur {len(sorted_groups)}). Validez-les pour voir la suite.")

        for group_name in display_groups:
            group_df = local_df[local_df['clean_group'] == group_name]
            # Representative row (first one)
            row = group_df.iloc[0]
            group_ids = group_df['id'].tolist()
            group_count = len(group_df)
            group_total = group_df['amount'].sum()
            group_id = row['id']
            
            # --- START PREMIUM CARD ---
            marker_class = "tx-card-marker-neg" if group_total < 0 else "tx-card-marker-pos"
            with st.container(border=True):
                st.markdown(f'<div class="{marker_class}" style="display:none;"></div>', unsafe_allow_html=True)
                
                # Header Section
                st.markdown(f"""
<div class="tx-header">
<div class="tx-date-acc">
📅 {row['date']} &nbsp; • &nbsp; 🏦 {row.get('account_label', 'Compte Principal')}
</div>
<div style="display: flex; gap: 0.5rem;">
{f'<span class="status-badge badge-isolated">📦 Isolée</span>' if str(group_name).startswith("single_") else ""}
{f'<span class="status-badge badge-group">📦 {group_count} opérations</span>' if group_count > 1 else ""}
</div>
</div>
""", unsafe_allow_html=True)
            
            # Body: Label & Amount
            c_body1, c_body2 = st.columns([3.5, 1])
            with c_body1:
                st.markdown(f'<div class="tx-label">{row["label"]}</div>', unsafe_allow_html=True)
                
                # Target account detection
                current_acc = row.get('account_label', '')
                detected_target = None
                label_up = str(row['label']).upper()
                for acc in all_acc_labels:
                    if acc != current_acc and acc.upper() in label_up:
                        detected_target = acc
                        break
                if detected_target:
                    st.markdown(f'<span style="color:#059669; font-size:0.75rem; font-weight:700;">🎯 Vers : {detected_target}</span>', unsafe_allow_html=True)
                elif group_count > 1:
                    st.caption("Et autres opérations similaires")
            
            with c_body2:
                amt_class = "tx-amount-pos" if group_total >= 0 else "tx-amount-neg"
                st.markdown(f'<div class="tx-amount {amt_class}">{group_total:.2f} €</div>', unsafe_allow_html=True)

            # Actions & Inputs Area
            with st.container():
                st.markdown('<div class="tx-actions"></div>', unsafe_allow_html=True)
            
            # Row 1: Category & Tags
            c_input1, c_input2 = st.columns([1, 1])
            with c_input1:
                cat_key = f"cat_{row['id']}"
                if cat_key not in st.session_state:
                    current_cat = row.get('category_validated') if row.get('category_validated') != 'Inconnu' else (row['original_category'] or "Inconnu")
                    st.session_state[cat_key] = current_cat if current_cat in available_categories else "Inconnu"
                
                options = list(available_categories)
                if row['original_category'] and row['original_category'] not in options:
                    options.append(row['original_category'])
                
                if st.session_state[cat_key] not in options:
                    options.append(st.session_state[cat_key])
                
                def format_cat(cat_name):
                    emoji = cat_emoji_map.get(cat_name, "🏷️")
                    return f"{emoji} {cat_name}"

                try:
                    cat_idx = options.index(st.session_state[cat_key])
                except:
                    cat_idx = 0

                st.selectbox("Catégorie", options, index=cat_idx, key=cat_key, format_func=format_cat)
                
            with c_input2:
                # Tags input
                tag_key = f"tag_sel_{group_id}"
                new_tag_key = f"tag_new_{group_id}"
                current_tags_str = row.get('tags', '') if row.get('tags') else ""
                current_tags = [t.strip() for t in current_tags_str.split(',') if t.strip()]
                existing_tags = get_all_tags()
                tag_options = sorted(list(set(existing_tags + current_tags)))
                
                selected_tags = st.multiselect("🏷️ Tags", options=tag_options, default=current_tags, key=tag_key)
                new_tag = st.text_input("➕ Nouveau tag", key=new_tag_key, placeholder="Ex: noël...")
                
                final_tags_list = list(set(selected_tags + ([new_tag.strip()] if new_tag.strip() else [])))
                final_tags_str = ", ".join(final_tags_list)

            # Row 2: Payeur & Bénéficiaire
            c_input3, c_input4 = st.columns([1, 1])
            with c_input3:
                current_member = row.get('member', '')
                suffix = row.get('card_suffix')
                if suffix and suffix in active_card_maps:
                    current_member = active_card_maps[suffix]
                if not current_member or current_member == 'Inconnu':
                    current_member = ""
                
                member_sel_key = f"mem_sel_{group_id}"
                member_input_key = f"mem_input_{group_id}"
                payeur_options = sorted(list(set(all_members + ["Maison", "Famille"])))
                if current_member and current_member not in payeur_options:
                    payeur_options = sorted(payeur_options + [current_member])
                payeur_options.append("✍️ Saisie libre...")
                
                try:
                    init_idx = payeur_options.index(current_member) if current_member in payeur_options else 0
                except:
                    init_idx = 0
                
                sel_choice = st.selectbox("👤 Payeur", options=payeur_options, index=init_idx, key=member_sel_key)
                if sel_choice == "✍️ Saisie libre...":
                    member_val = st.text_input("Nom du payeur", key=member_input_key)
                else:
                    member_val = sel_choice
                    
            with c_input4:
                beneficiary_key = f"benef_sel_{group_id}"
                beneficiary_input_key = f"benef_input_{group_id}"
                current_benef = row.get('beneficiary', 'Famille')
                if not current_benef: current_benef = ""
                
                benef_options = sorted(list(set(full_member_list + ["Maison", "Famille"])))
                if current_benef and current_benef not in benef_options:
                    benef_options = sorted(benef_options + [current_benef])
                benef_options.insert(0, "") # Placeholder for clear
                benef_options.append("✍️ Saisie libre...")
                
                try:
                    if current_benef in benef_options: b_idx = benef_options.index(current_benef)
                    else: b_idx = benef_options.index("Famille") if "Famille" in benef_options else 0
                except: b_idx = 0
                
                b_choice = st.selectbox("🎯 Pour qui ?", options=benef_options, index=b_idx, key=beneficiary_key)
                if b_choice == "✍️ Saisie libre...":
                    beneficiary_val = st.text_input("Nom du bénéficiaire", key=beneficiary_input_key)
                else:
                    beneficiary_val = b_choice


            # Bottom Controls (AI, Memory, Validate)
            c_ctrl1, c_ctrl2, c_ctrl3 = st.columns([0.5, 1, 3])
            with c_ctrl1:
                st.button("🪄", key=f"ai_{group_id}", help="Suggérer via IA", 
                          on_click=run_ai_categorization, args=(group_id, row['label'], row['amount'], row['date']))
            with c_ctrl2:
                remember = st.checkbox("Mémoriser", key=f"mem_check_{group_id}", value=True)
            with c_ctrl3:
                btn_label = f"Valider {group_count} opérations" if group_count > 1 else "Valider l'opération"
                if st.button(btn_label, key=f"btn_bulk_{group_id}", type="primary", use_container_width=True):
                    validate_with_memory(group_ids, row['label'], st.session_state[cat_key], remember, member_val, tags=final_tags_str, beneficiary=beneficiary_val)
                    st.toast(f"✅ Transaction(s) validée(s) !", icon="🎉")
                    if len(display_groups) == 1: st.balloons()
                    st.rerun()

            with st.expander(f"🔍 Détails ({group_count} lignes)"):
                for _, sub_row in group_df.iterrows():
                    cd1, cd2, cd3, cd4 = st.columns([4, 1, 1, 1])
                    cd1.caption(sub_row['label'])
                    cd2.caption(sub_row['date'])
                    cd3.caption(f"{sub_row['amount']:.2f} €")
                    if cd4.button("Dégrouper", key=f"isole_{sub_row['id']}", type="secondary"):
                        st.session_state['excluded_tx_ids'].add(int(sub_row['id']))
                        st.toast("✂️ Opération isolée", icon="⚡")
            

    # Call the fragment
    show_validation_list(filtered_df, all_acc_labels, all_members, available_categories, cat_emoji_map, sort_key, active_card_maps)
