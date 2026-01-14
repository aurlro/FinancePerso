import streamlit as st
from modules.categorization import predict_category_ai

from modules.data_manager import add_learning_rule, get_pending_transactions, update_transaction_category, get_unique_members, update_transaction_member, init_db
from modules.ui import load_css
import re
import pandas as pd

st.set_page_config(page_title="Validation", page_icon="✅", layout="wide")
load_css()
init_db()  # Ensure tables exist

# Helper for validation with optional memory
def validate_with_memory(tx_id, label, category, remember, member_update=None):
    if remember:
        pattern = re.sub(r'(?i)CARTE|CB\*?\d*|\d{2}/\d{2}/\d{2}', '', label).strip()
        clean_pattern = re.sub(r'[^a-zA-Z\s]', '', pattern).strip().upper()
        clean_pattern = re.sub(r'\s+', ' ', clean_pattern)
        
        if len(clean_pattern) > 2:
            add_learning_rule(clean_pattern, category)
            
    update_transaction_category(tx_id, category)
    if member_update:
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

    st.markdown(f"**{len(filtered_df)}** transactions affichées (sur {len(df)} en attente).")
    st.divider()

    # Helper callback for AI update
    def run_ai_categorization(tx_id, label, amount, date):
        key = f"cat_{tx_id}"
        cat, conf = predict_category_ai(label, amount, date)
        st.session_state[key] = cat

    # Display list
    # Optimize: pagination or limit if too many
    for index, row in filtered_df.iterrows():
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 2, 2])
            
            with col1:
                st.caption(row['date'])
                
                # Dynamic Member Selection
                current_member = row.get('member', '')
                member_key = f"mem_sel_{row['id']}"
                
                # Check if "Inconnu" or empty -> Allow selection
                # We check literal 'Inconnu' (str) or empty
                is_unknown = (current_member == 'Inconnu' or not current_member)
                
                if is_unknown:
                    # Provide selectbox
                    selected_member_val = st.selectbox(
                        "Qui ?", 
                        ["Inconnu"] + all_members, 
                        key=member_key,
                        label_visibility="collapsed"
                    )
                else:
                    st.caption(f"Cards: {current_member}")
                    selected_member_val = None

            with col2:
                st.markdown(f"**{row['label']}**")
                if row.get('ai_confidence'):
                   st.caption(f"Confiance IA: {row['ai_confidence']:.2f}")

            with col3:
                color = "red" if row['amount'] < 0 else "green"
                st.markdown(f":{color}[{row['amount']:.2f} €]")
            
            with col4:
                # Category selector
                cat_key = f"cat_{row['id']}"
                if cat_key not in st.session_state:
                     current_cat = row.get('category_validated') if row.get('category_validated') != 'Inconnu' else (row['original_category'] or "Inconnu")
                     st.session_state[cat_key] = current_cat

                options = ["Alimentation", "Transport", "Loisirs", "Santé", "Logement", "Revenus", "Autre", "Restaurants", "Abonnements", "Achats", "Services"]
                if row['original_category'] and row['original_category'] not in options:
                    options.append(row['original_category'])
                
                # Ensure current_cat is in options to avoid error
                if st.session_state[cat_key] not in options:
                    options.append(st.session_state[cat_key])
                
                selected_cat = st.selectbox(
                    "Catégorie", 
                    options, 
                    key=cat_key,
                    label_visibility="collapsed"
                )
            
            with col5:
                # Ensure unique keys for buttons
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.button(
                        "🪄", 
                        key=f"ai_{row['id']}", 
                        help="Demander à Gemini", 
                        on_click=run_ai_categorization, 
                        args=(row['id'], row['label'], row['amount'], row['date'])
                    )
                
                with c2:
                     remember = st.checkbox("Mém.", key=f"mem_{row['id']}", help="Créer une règle pour ce libellé")

                with c3:
                    if st.button("OK", key=f"btn_{row['id']}", type="primary"):
                        # If member was "Inconnu", we use the selectbox value to update, UNLESS it's still Inconnu
                        final_member = None
                        if is_unknown and selected_member_val and selected_member_val != "Inconnu":
                            final_member = selected_member_val
                            
                        validate_with_memory(row['id'], row['label'], st.session_state[cat_key], remember, final_member)
                        st.rerun()
            
            st.divider()
