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
# Filters
    col_filter1, col_filter2 = st.columns(2)
    filtered_df = df.copy()
    
    with col_filter1:
        if 'account_label' in df.columns:
            accounts = df['account_label'].unique().tolist()
            sel_acc = st.multiselect("Filtrer par Compte", accounts)
            if sel_acc:
                filtered_df = filtered_df[filtered_df['account_label'].isin(sel_acc)]
                
    with col_filter2:
        if 'member' in df.columns:
            members = [m for m in df['member'].unique() if m]
            sel_mem = st.multiselect("Filtrer par Membre", members)
            if sel_mem:
                filtered_df = filtered_df[filtered_df['member'].isin(sel_mem)]

    st.divider()
    col_sort1, col_sort2 = st.columns([2, 1])
    with col_sort1:
        sort_options = {
            "Gros groupes (Défaut)": "count",
            "Plus récentes": "date_recent",
            "Plus anciennes": "date_old",
            "Montant (Décroissant)": "amount_desc",
            "Montant (Croissant)": "amount_asc"
        }
        sort_choice = st.selectbox("Trier par", list(sort_options.keys()))
        sort_key = sort_options[sort_choice]

    st.markdown(f"**{len(filtered_df)}** transactions affichées (sur {len(df)} en attente).")
    
    with st.expander("💡 Aide : Virement Interne vs Compte à compte", expanded=False):
        st.info("""
        **Virement Interne** (🔄) : C'est votre catégorie pour les transferts entre vos propres comptes suivis ici. 
        Elle est exclue des graphiques de dépenses pour ne pas fausser votre budget.
        
        **Virements de compte à compte** : C'est souvent le libellé brut de votre banque. 
        Même si la banque le dit, validez-le bien en **Virement Interne** pour une comptabilité propre.
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

    st.divider()
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
            with st.container(border=True):
                col1, col2, col3, col4, col5 = st.columns([1.5, 2, 1, 2, 2.5])
                
                with col1:
                    st.caption(f"📅 {row['date']}")
                    if 'account_label' in row and row['account_label']:
                        st.caption(f"🏦 {row['account_label']}")
                    if group_count > 1:
                        st.info(f"**{group_count} op.**")
                if str(group_name).startswith("single_"):
                    st.warning("📦 **Isolée**")

                with col2:
                    st.markdown(f"**{row['label']}**")
                    
                    # Target account detection
                    current_acc = row.get('account_label', '')
                    detected_target = None
                    label_up = str(row['label']).upper()
                    for acc in all_acc_labels:
                        if acc != current_acc and acc.upper() in label_up:
                            detected_target = acc
                            break
                    
                    if detected_target:
                        st.success(f"🎯 Vers : **{detected_target}**")

                    if group_count > 1:
                        st.caption("Et autres similaires")
                    
                with col3:
                    color = "red" if group_total < 0 else "green"
                    st.markdown(f"<h4 style='color:{color}; margin:0;'>{group_total:.2f} €</h4>", unsafe_allow_html=True)
                
                with col4:
                    # Category selector
                    cat_key = f"cat_{row['id']}"
                    if cat_key not in st.session_state:
                        current_cat = row.get('category_validated') if row.get('category_validated') != 'Inconnu' else (row['original_category'] or "Inconnu")
                        st.session_state[cat_key] = current_cat if current_cat in available_categories else "Inconnu"
                    
                    options = list(available_categories)
                    if row['original_category'] and row['original_category'] not in options:
                        options.append(row['original_category'])
                    
                    # Ensure current_cat is in options to avoid error
                    if st.session_state[cat_key] not in options:
                        options.append(st.session_state[cat_key])
                    
                    def format_cat(cat_name):
                        emoji = cat_emoji_map.get(cat_name, "🏷️")
                        return f"{emoji} {cat_name}"

                    # Explicitly find index to avoid reset bug
                    try:
                        cat_idx = options.index(st.session_state[cat_key])
                    except ValueError:
                        cat_idx = 0

                    st.selectbox(
                        "Catégorie", 
                        options, 
                        index=cat_idx,
                        key=cat_key,
                        format_func=format_cat,
                        label_visibility="collapsed"
                    )
                    
                    # Payeur / Bénéficiaire en ligne
                    c_m1, c_m2 = st.columns(2)
                    with c_m1:
                        current_member = row.get('member', '')
                        suffix = row.get('card_suffix')
                        
                        # Authoritative override: if we have an active mapping for this card, use it
                        if suffix and suffix in active_card_maps:
                            current_member = active_card_maps[suffix]
                        
                        if not current_member or current_member == 'Inconnu':
                            current_member = ""
                        
                        member_sel_key = f"mem_sel_{group_id}"
                        member_input_key = f"mem_input_{group_id}"
                        
                        # Prepare options: all known members + common roles + Autre trigger
                        payeur_options = sorted(list(set(all_members + ["Maison", "Famille"])))
                        if current_member and current_member not in payeur_options:
                            payeur_options = sorted(payeur_options + [current_member])
                        payeur_options.append("✍️ Saisie libre...")
                        
                        # Find initial index
                        try:
                            init_idx = payeur_options.index(current_member) if current_member in payeur_options else 0
                        except:
                            init_idx = 0
                            
                        sel_choice = st.selectbox("👤 Payeur", options=payeur_options, index=init_idx, key=member_sel_key, help="Choisissez un membre ou saisissez un nouveau nom via 'Saisie libre'")
                        
                        if sel_choice == "✍️ Saisie libre...":
                            member_val = st.text_input("Nom du payeur", key=member_input_key, placeholder="ex: Employeur, Remboursement...")
                        else:
                            member_val = sel_choice
                    
                    with c_m2:
                        beneficiary_key = f"benef_sel_{group_id}"
                        beneficiary_input_key = f"benef_input_{group_id}"
                        
                        current_benef = row.get('beneficiary', 'Famille')
                        if not current_benef:
                            current_benef = ""
                            
                        benef_options = sorted(list(set(full_member_list + ["Maison", "Famille"])))
                        if current_benef and current_benef not in benef_options:
                            benef_options = sorted(benef_options + [current_benef])
                        benef_options.append("✍️ Saisie libre...")
                        
                        try:
                            # Default to "Famille" if exists, else first
                            if current_benef in benef_options:
                                b_idx = benef_options.index(current_benef)
                            elif "Famille" in benef_options:
                                b_idx = benef_options.index("Famille")
                            else:
                                b_idx = 0
                        except:
                            b_idx = 0
                            
                        b_choice = st.selectbox("🎯 Pour qui ?", options=benef_options, index=b_idx, key=beneficiary_key, help="À qui profite cette dépense ?")
                        
                        if b_choice == "✍️ Saisie libre...":
                            beneficiary_val = st.text_input("Nom du bénéficiaire", key=beneficiary_input_key, placeholder="ex: Ami, Voyage...")
                        else:
                            beneficiary_val = b_choice

                with col5:
                    # Tags input - Advanced
                    existing_tags = get_all_tags()
                    tag_key = f"tag_sel_{group_id}"
                    new_tag_key = f"tag_new_{group_id}"
                    
                    # Initial value for multiselect
                    current_tags_str = row.get('tags', '') if row.get('tags') else ""
                    current_tags = [t.strip() for t in current_tags_str.split(',') if t.strip()]
                    
                    # Filter current tags to ensure they are in existing_tags to avoid multiselect error
                    # If they are not in existing_tags, we add them temporarily
                    tag_options = sorted(list(set(existing_tags + current_tags)))
                    
                    selected_tags = st.multiselect("🏷️ Tags", options=tag_options, default=current_tags, key=tag_key, help="Choisissez des tags existants")
                    new_tag = st.text_input("➕ Nouveau tag", key=new_tag_key, placeholder="ex: noël, vacances...", help="Appuyez sur Entrée pour ajouter ce tag")
                    
                    final_tags_list = list(set(selected_tags + ([new_tag.strip()] if new_tag.strip() else [])))
                    final_tags_str = ", ".join(final_tags_list)

                    # Buttons
                    c_btn1, c_btn2 = st.columns([1, 3])
                    with c_btn1:
                        st.button(
                            "🪄", 
                            key=f"ai_{group_id}", 
                            help="Demander à Gemini", 
                            on_click=run_ai_categorization, 
                            args=(group_id, row['label'], row['amount'], row['date'])
                        )
                        remember = st.checkbox("Mém.", key=f"mem_check_{group_id}", help="Créer une règle", value=True)
                    
                    with c_btn2:
                        btn_label = f"Valider ({group_count})" if group_count > 1 else "Valider"
                        if st.button(btn_label, key=f"btn_bulk_{group_id}", type="primary", use_container_width=True):
                            # member_val is already computed above based on selection/input
                                
                            validate_with_memory(
                                group_ids, 
                                row['label'], 
                                st.session_state[cat_key], 
                                remember, 
                                member_val,
                                tags=final_tags_str,
                                beneficiary=beneficiary_val
                            )
                            st.toast(f"✅ {group_count} transaction(s) validée(s) !", icon="🎉")
                            
                            # If it was the last group
                            if len(display_groups) == 1:
                                st.balloons()
                                st.session_state['last_validation_success'] = True
                                
                            st.rerun()
                
                st.divider()
                
                # Drill-down: individual transactions in the group
                with st.expander(f"🔍 Détail des {group_count} opérations"):
                    st.write("Libellé complet | Date | Montant | Action")
                    for _, sub_row in group_df.iterrows():
                        c_d1, c_d2, c_d3, c_d4 = st.columns([4, 1, 1, 1])
                        with c_d1:
                            st.caption(sub_row['label'])
                        with c_d2:
                            st.caption(sub_row['date'])
                        with c_d3:
                            st.caption(f"{sub_row['amount']:.2f} €")
                        with c_d4:
                            # Use type="secondary" and specific key to avoid conflicts
                            if st.button("Dégrouper", key=f"isole_{sub_row['id']}", help="Sortir cette opération du groupe", type="secondary"):
                                st.session_state['excluded_tx_ids'].add(int(sub_row['id']))
                                st.toast("✂️ Opération extraite du groupe", icon="⚡")
                                # No rerun needed, fragment will update

    # Call the fragment
    show_validation_list(filtered_df, all_acc_labels, all_members, available_categories, cat_emoji_map, sort_key, active_card_maps)
