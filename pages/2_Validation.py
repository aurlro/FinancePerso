import streamlit as st
from modules.categorization import predict_category_ai

from modules.db.rules import add_learning_rule
from modules.db.transactions import get_pending_transactions, update_transaction_category, bulk_update_transaction_status, mark_transaction_as_ungrouped
from modules.db.members import get_members, update_transaction_member, get_member_mappings
from modules.db.migrations import init_db
from modules.db.categories import get_categories, get_categories_with_emojis, get_categories_suggested_tags
from modules.db.tags import get_all_tags
from modules.db.stats import get_all_account_labels
from modules.ui import load_css, render_scroll_to_top, show_success, toast_success, toast_warning
from modules.ui.feedback import validation_feedback, celebrate_all_done
from modules.utils import clean_label

# New modular components
from modules.ui.components.filters import render_transaction_filters
from modules.ui.components.progress_tracker import render_progress_tracker
from modules.ui.components.tag_manager import render_smart_tag_selector, render_pill_tags
from modules.ui.components.member_selector import render_member_selector
from modules.ui.validation.grouping import get_smart_groups, calculate_group_stats, get_group_transactions
from modules.ui.validation.sorting import sort_groups, get_sort_options
from modules.ui.validation.row_view import render_validation_row

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

# Info box about features
st.info("""
**📝 Nouvelle interface de validation :**
- **📂 Catégorie** : Sélectionnez la catégorie appropriée
- **👤 Qui a payé** : Indiquez le membre qui a effectué la dépense
- **🎯 Pour qui** : Indiquez le bénéficiaire (Famille, Maison, ou un membre)
- **🏷️ Tags** : Ajoutez des balises en un clic sur les boutons rapides
- **🧾 Chèques** : Un champ "Nature" apparaît automatiquement pour les chèques

💡 *Les tags vous permettent de suivre des dépenses spécifiques à travers différentes catégories*
""")

# Helper function to detect cheques
def _is_cheque_transaction(label: str) -> bool:
    """Check if a transaction is a cheque based on label."""
    cheque_keywords = ['chq.', 'chèque', 'cheque', 'chq ', 'cheq ']
    label_lower = label.lower()
    return any(keyword in label_lower for keyword in cheque_keywords)

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
        filtered_df = render_transaction_filters(df, show_account=True, show_member=True)

    col_sort1, col_sort2, col_sort3 = st.columns([2, 1, 1])
    with col_sort1:
        sort_options = get_sort_options()
        sort_choice = st.selectbox("Trier par", list(sort_options.keys()), label_visibility="visible", key='selectbox_116')
        sort_key = sort_options[sort_choice]

    with col_sort2:
        st.markdown(f"<p style='margin-top:28px; font-weight:600; color:#64748B;'>{len(filtered_df)} en attente</p>", unsafe_allow_html=True)
    
    with col_sort3:
        # Undo button and help side-by-side
        h_c1, h_c2 = st.columns([1, 2])
        with h_c1:
            with st.popover("🔙", help="Annuler la dernière action"):
                st.write("Voulez-vous annuler la dernière validation ?")
                if st.button("Confirmer l'annulation", type="primary", use_container_width=True, key='button_128'):
                    from modules.data_manager import undo_last_action
                    success, msg = undo_last_action()
                    if success:
                        toast_success(msg, icon="🔙")
                        st.rerun()
                    else:
                        toast_warning(msg, icon="⚠️")
        with h_c2:
            with st.popover("❓ Aide", use_container_width=True):
                st.info("""
                **Virement Interne** (🔄) : Pour les transferts entre vos comptes suivis. Exclu des graphiques de dépenses.
                
                **Dégrouper** : Si une opération dans un groupe est différente, utilisez le bouton dans 'Détails' pour l'isoler.
                """)
    
    # --- PROGRESS BAR GAMIFICATION ---
    render_progress_tracker(len(filtered_df), session_key="validation_progress")
    
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
        # Use modular grouping logic
        local_df = get_smart_groups(filtered_df, excluded_ids=st.session_state['excluded_tx_ids'])
        
        # Calculate group statistics
        group_stats = calculate_group_stats(local_df)
        
        # Sort and limit groups
        display_groups = sort_groups(group_stats, sort_key=sort_key, max_groups=40)
        
        if len(group_stats) > 40:
            st.info(f"Affichage des 40 premiers groupes (sur {len(group_stats)}). Validez-les pour voir la suite.")

        if len(group_stats) > 40:
            st.info(f"Affichage des 40 premiers groupes (sur {len(group_stats)}). Validez-les pour voir la suite.")

        # --- NEW HORIZONTAL ROW LAYOUT ---
        # Initialize validation handler (closure to capture context)
        def handle_row_validation(row_id, category, member):
            # Find the group data again (or pass it through?)
            # Since this is a callback, we need to locate the IDs.
            # Efficient way: We know row_id maps to a group leader ID.
            
            # Simple approach: Re-filter for this group
            # OR better: The function is called inside the loop context? 
            # No, if it's a callback, streamlits reruns. 
            # Actually, my render_validation_row implementation calls the callback directly inside the button check.
            # So we are IN the loop context when it executes (before rerun).
            
            # Re-fetch group info
            target_group = next((g for g in display_groups if local_df[local_df['clean_group'] == g].iloc[0]['id'] == row_id), None)
            if not target_group: return # Should not happen
            
            g_df = local_df[local_df['clean_group'] == target_group]
            g_ids = g_df['id'].tolist()
            
            # Call existing validation logic
            validate_with_memory(g_ids, g_df.iloc[0]['label'], category, True, member)
            
            # Feedback
            st.session_state[f'validation_success_{row_id}'] = {'count': len(g_ids), 'category': category}
            validation_feedback(len(g_ids), "opération")
            if len(display_groups) == 1:
                celebrate_all_done()
            st.rerun()

        for group_name in display_groups:
            group_df = local_df[local_df['clean_group'] == group_name]
            row = group_df.iloc[0]
            
            # Prepare data dict for the component
            row_data = {
                'id': row['id'],
                'label': row['label'],
                'date': row['date'],
                'total_amount': group_df['amount'].sum(),
                'count': len(group_df),
                'category': row.get('category_validated') or row['original_category'],
                'member': row.get('member', '')
            }
            
            # Heuristic for Member default if empty
            if not row_data['member'] or row_data['member'] not in all_members:
                 suffix = row.get('card_suffix')
                 if suffix and suffix in active_card_maps:
                     row_data['member'] = active_card_maps[suffix]
                 
            render_validation_row(
                row_data=row_data,
                all_members=all_members,
                all_categories=available_categories,
                cat_emoji_map=cat_emoji_map,
                on_validate=handle_row_validation,
                key_prefix=key_suffix
            )

            

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

render_scroll_to_top()

from modules.ui.layout import render_app_info
render_app_info()
