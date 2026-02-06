"""
🔁 Analyse des Récurrences - Enhanced V3
Features:
- User feedback on detected recurrences (confirm/reject)
- Manual addition of recurring patterns
- Separate views for confirmed, rejected, and pending recurrences
- Improved drill-down with transaction IDs
"""
import streamlit as st
import pandas as pd
from modules.db.transactions import get_all_transactions
from modules.db.categories import get_categories_with_emojis
from modules.db.recurrence_feedback import (
    init_recurrence_feedback_table,
    set_recurrence_feedback,
    get_all_feedback,
    delete_feedback,
    get_feedback_stats
)
from modules.analytics_v2 import (
    detect_recurring_payments_v2, 
    group_by_category, 
    get_recurring_by_tags,
    analyze_recurrence_summary
)
from modules.ui import load_css, render_scroll_to_top
from modules.ui.components.transaction_drill_down import render_transaction_drill_down
from modules.ui.recurrence_manager import (
    render_recurrence_card,
    render_feedback_summary,
    render_confirmed_recurring_section,
    render_rejected_recurring_section,
    render_manual_add_section,
    filter_by_user_feedback
)

st.set_page_config(page_title="Récurrence", page_icon="🔁", layout="wide")
load_css()
init_recurrence_feedback_table()

# Helper functions (defined before use)
def confirm_recurrence(label: str, category: str):
    """Mark a recurrence as confirmed by user."""
    success = set_recurrence_feedback(
        label_pattern=label,
        is_recurring=True,
        category=category,
        notes="Confirmée par l'utilisateur"
    )
    if success:
        st.toast(f"✅ '{label}' confirmé comme récurrence", icon="✅")
        st.rerun()
    else:
        st.error("Erreur lors de la sauvegarde")

def reject_recurrence(label: str, category: str):
    """Mark a recurrence as rejected (false positive)."""
    # Get reason from session state if available
    note_key = f'pending_note_{label}'
    note = st.session_state.get(note_key, "Rejetée par l'utilisateur")
    
    success = set_recurrence_feedback(
        label_pattern=label,
        is_recurring=False,
        category=category,
        notes=note
    )
    if success:
        st.toast(f"❌ '{label}' marqué comme non-récurrent", icon="❌")
        st.rerun()
    else:
        st.error("Erreur lors de la sauvegarde")

st.title("🔁 Analyse des Récurrences")
st.markdown("Détection et validation des abonnements, factures et revenus réguliers.")

# Feedback summary at top
render_feedback_summary()

# Load data
df = get_all_transactions()

# Helper function to enrich with feedback
def enrich_with_feedback(recurring_df):
    """Add user_feedback column to dataframe."""
    import pandas as pd
    from modules.db.recurrence_feedback import get_all_feedback
    
    if recurring_df.empty:
        recurring_df['user_feedback'] = None
        return recurring_df
        
    feedback = get_all_feedback()
    feedback_map = {(f['label_pattern'], f['category']): f['user_feedback'] for f in feedback}
    
    def get_status(row):
        key = (row['label'], row.get('category', ''))
        return feedback_map.get(key, None)
        
    recurring_df['user_feedback'] = recurring_df.apply(get_status, axis=1)
    return recurring_df

if df.empty:
    st.info("Aucune donnée disponible pour l'analyse.")
else:
    # Sidebar
    st.sidebar.markdown("### 📊 Analyse Récurrence")
    st.sidebar.info("Détection automatique des abonnements et revenus réguliers sur base de l'historique.")

    # We only analyze validated transactions
    validated_df = df[df['status'] == 'validated']
    
    if validated_df.empty:
        st.warning("Veuillez valider quelques transactions pour permettre l'analyse.")
    else:
        # Run analysis
        with st.spinner("Analyse des tendances en cours..."):
            recurring_df = detect_recurring_payments_v2(validated_df)
            
        # Enrich with feedback status
        recurring_df = enrich_with_feedback(recurring_df)
        
        # Tabs Layout
        tabs = st.tabs(["📊 Tableau de Bord", "✅ Validation", "💳 Abonnements", "🗑️ Corbeille"])
        
        cat_emoji_map = get_categories_with_emojis()
        
        from modules.ui.recurrence_tabs import (
            render_dashboard_tab,
            render_timeline_chart,
            render_validation_tab,
            render_subscriptions_tab,
            render_trash_tab
        )
        
        with tabs[0]:
            render_dashboard_tab(recurring_df, validated_df)
            
        with tabs[1]:
            render_validation_tab(recurring_df, cat_emoji_map)
            
        with tabs[2]:
            render_subscriptions_tab(recurring_df, cat_emoji_map)
            
        with tabs[3]:
            render_trash_tab()

render_scroll_to_top()
from modules.ui.layout import render_app_info
render_app_info()
