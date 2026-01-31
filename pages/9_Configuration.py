import streamlit as st
from modules.ui import load_css
from modules.db.migrations import init_db
from modules.ui.config.config_dashboard import render_config_dashboard
from modules.ui.config.config_mode import (
    render_mode_toggle, is_advanced_mode, render_simple_mode_help
)
from modules.ui.config.api_settings import render_api_settings
from modules.ui.config.member_management import render_member_management
from modules.ui.config.category_management import render_category_management
from modules.ui.config.tags_rules import render_tags_rules
from modules.ui.config.audit_tools import render_audit_tools
from modules.ui.config.data_operations import render_data_operations, render_export_section
from modules.ui.config.backup_restore import render_backup_restore
from modules.ui.config.log_viewer import render_log_viewer
from modules.ui.config.notifications import render_notification_settings
from modules.ui.feedback import display_flash_messages, toast_info

# Page Setup
st.set_page_config(page_title="Configuration", page_icon="⚙️", layout="wide")
load_css()
init_db()  # Ensure tables exist

# Afficher les messages flash en attente
display_flash_messages()

st.title("⚙️ Configuration")
toast_info("Page de configuration chargée", icon="⚙️")

# --- MODE TOGGLE (Simple vs Advanced) ---
render_mode_toggle()
render_simple_mode_help()
st.divider()

# Handle jump-to from dashboard
jump_to = st.session_state.get('config_jump_to', None)

# Create tabs based on mode
if is_advanced_mode():
    # Full tabs in advanced mode
    tab_labels = [
        "🏠 Vue d'ensemble",
        "👤 Profil",
        "🤖 IA & Services", 
        "💰 Budgets",
        "🧠 Règles & Automatisations",
        "🔧 Maintenance"
    ]
else:
    # Simplified tabs in simple mode
    tab_labels = [
        "🏠 Vue d'ensemble",
        "👤 Profil",
        "🤖 IA & Services", 
        "💰 Budgets"
    ]

# Set default tab if jump requested
default_index = 0
if jump_to:
    try:
        default_index = tab_labels.index(jump_to)
        del st.session_state['config_jump_to']
    except ValueError:
        pass

tabs = st.tabs(tab_labels)

# --- TAB 1: DASHBOARD ---
with tabs[0]:
    render_config_dashboard()

# --- TAB 2: PROFILE (Members + Categories) ---
with tabs[1]:
    st.header("👤 Configuration du Profil")
    
    # Members Section
    st.subheader("Membres du foyer", divider="blue")
    render_member_management()
    
    st.divider()
    
    # Categories Section  
    st.subheader("Catégories de dépenses", divider="blue")
    render_category_management()

# --- TAB 3: AI & SERVICES (API + Notifications) ---
with tabs[2]:
    st.header("🤖 Intelligence Artificielle")
    st.markdown("Configurez les services externes pour enrichir l'expérience.")
    
    # API Settings
    st.subheader("Configuration IA", divider="blue")
    render_api_settings()
    
    st.divider()
    
    # Notifications
    st.header("🔔 Notifications")
    st.markdown("Recevez des alertes pour les dépassements de budget.")
    st.subheader("Paramètres des alertes", divider="blue")
    render_notification_settings()

# --- TAB 4: BUDGETS ---
with tabs[3]:
    st.header("💰 Gestion des Budgets")
    st.markdown("Définissez vos limites de dépenses par catégorie.")
    
    from modules.db.budgets import get_budgets, set_budget, delete_budget
    from modules.db.categories import get_categories
    from modules.impact_analyzer import analyze_budget_creation_impact, render_impact_preview
    import pandas as pd
    
    budgets_df = get_budgets()
    categories = get_categories()
    
    col_b1, col_b2 = st.columns([2, 1])
    
    with col_b1:
        st.subheader("Budgets actuels", divider="blue")
        
        if budgets_df.empty:
            st.info("Aucun budget défini. Créez votre premier budget !")
        else:
            # Display budgets with progress
            for _, row in budgets_df.iterrows():
                cat = row['category']
                amount = row['amount']
                
                # Calculate current spending
                from modules.db.transactions import get_all_transactions
                import datetime
                
                df = get_all_transactions()
                if not df.empty:
                    current_month = datetime.datetime.now().strftime('%Y-%m')
                    df['date_dt'] = pd.to_datetime(df['date'])
                    month_spending = df[
                        (df['category_validated'] == cat) & 
                        (df['date_dt'].dt.strftime('%Y-%m') == current_month) &
                        (df['amount'] < 0)
                    ]['amount'].sum()
                    
                    spent = abs(month_spending)
                    percentage = min(100, (spent / amount * 100)) if amount > 0 else 0
                    
                    # Color based on percentage
                    color = "normal"
                    if percentage >= 100:
                        color = "error"
                    elif percentage >= 80:
                        color = "warning"
                    
                    col_cat, col_amount, col_progress, col_del = st.columns([2, 1, 3, 0.5])
                    
                    with col_cat:
                        st.write(f"**{cat}**")
                    with col_amount:
                        st.write(f"{amount:.0f}€/mois")
                    with col_progress:
                        st.progress(percentage / 100, text=f"{spent:.0f}€ ({percentage:.0f}%)")
                    with col_del:
                        if st.button("🗑️", key=f"del_budget_{cat}", help="Supprimer ce budget"):
                            delete_budget(cat)
                            from modules.ui.feedback import delete_feedback
                            delete_feedback(f"Budget '{cat}'")
                            st.rerun()
    
    with col_b2:
        st.subheader("Ajouter un budget", divider="blue")
        
        available_cats = [c for c in categories if c not in budgets_df['category'].tolist()]
        
        if not available_cats:
            st.info("Toutes les catégories ont déjà un budget !")
        else:
            with st.form("add_budget"):
                cat = st.selectbox("Catégorie", available_cats)
                amount = st.number_input("Montant mensuel (€)", min_value=1, value=100)
                
                # Preview impact
                impact = analyze_budget_creation_impact(cat, amount)
                render_impact_preview('budget_creation', impact)
                
                if st.form_submit_button("💾 Créer le budget", type="primary"):
                    set_budget(cat, amount)
                    from modules.ui.feedback import save_feedback
                    save_feedback(f"Budget '{cat}'", created=True)
                    st.rerun()

# --- TAB 5: RULES & AUTOMATIONS (Advanced only) ---
if is_advanced_mode():
    with tabs[4]:
        st.header("🧠 Règles & Automatisations")
        st.markdown("Gérez les règles de catégorisation automatique et les paramètres avancés.")
        
        render_tags_rules()

# --- TAB 6: MAINTENANCE (Advanced only) ---
if is_advanced_mode():
    with tabs[5]:
        st.header("🔧 Maintenance et Outils")
        
        # Export Section (extracted from data_operations)
        st.subheader("📤 Export des données", divider="blue")
        render_export_section()
        
        st.divider()
        
        # Audit Tools
        st.subheader("🧹 Audit & Nettoyage", divider="blue")
        render_audit_tools()
        
        st.divider()
        
        # Backups
        col_back1, col_back2 = st.columns([1, 1])
        
        with col_back1:
            st.subheader("💾 Sauvegardes", divider="blue")
            render_backup_restore()
        
        with col_back2:
            st.subheader("📑 Logs système", divider="blue")
            render_log_viewer()

from modules.ui.layout import render_app_info
render_app_info()
