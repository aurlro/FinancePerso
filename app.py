import streamlit as st
import os

# --- ERROR TRACKING & SECURITY INITIALIZATION ---
from modules.error_tracking import init_error_tracking
from modules.encryption import get_encryption
from modules.logger import logger

# Initialize Sentry if DSN configured
if os.getenv('SENTRY_DSN'):
    init_error_tracking(
        dsn=os.getenv('SENTRY_DSN'),
        environment=os.getenv('ENVIRONMENT', 'production')
    )

# Initialize encryption
encryption = get_encryption()
if encryption.is_enabled():
    logger.info("🔐 Encryption enabled for sensitive fields")
else:
    logger.warning("⚠️  Encryption disabled - add ENCRYPTION_KEY to .env for production")

from modules.ui import load_css, card_kpi, render_scroll_to_top, display_flash_messages
from modules.ui.feedback import toast_success, show_success
from modules.db.migrations import init_db
from modules.db.stats import is_app_initialized, get_global_stats
from modules.db.members import add_member
from modules.ui.components.onboarding_modal import should_show_onboarding, render_onboarding_modal
from modules.ui.components.quick_actions import render_quick_actions_grid
from modules.ui.components.smart_actions import render_smart_actions
from modules.ui.components.daily_widget import render_daily_widget, render_quick_stats_row
from modules.notifications import NotificationManager, check_all_notifications, render_notification_badge

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="MyFinance Companion",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()
init_db()

# --- SESSION STATE INITIALIZATION (AVANT toute utilisation) ---
if 'default_account_name' not in st.session_state:
    st.session_state['default_account_name'] = None
if 'onboarding_complete' not in st.session_state:
    st.session_state['onboarding_complete'] = None
if 'onboarding_dismissed' not in st.session_state:
    st.session_state['onboarding_dismissed'] = None
if 'onboarding_step' not in st.session_state:
    st.session_state['onboarding_step'] = None

# --- DASHBOARD CLEANUP (Auto-repair on startup) ---
try:
    from modules.db.dashboard_cleanup import run_startup_cleanup
    cleanup_result = run_startup_cleanup()
    if cleanup_result.widgets_fixed > 0 or cleanup_result.widgets_removed > 0:
        logger.info(f"Dashboard auto-cleanup: {cleanup_result.message}")
except Exception as e:
    logger.warning(f"Dashboard cleanup failed (non-critical): {e}")

# Vérifier les notifications (budget alerts, daily digest, etc.)
check_all_notifications()

# Afficher le badge de notification dans la sidebar
render_notification_badge()

# Afficher les messages flash en attente
display_flash_messages()

# --- ONBOARDING MODAL ---
if should_show_onboarding():
    render_onboarding_modal()

# --- MAIN LOGIC ---

if not is_app_initialized():
    # === ONBOARDING MODE (Fallback if modal was dismissed) ===
    st.title("👋 Bienvenue sur MyFinance Companion")
    st.markdown("### Votre assistant personnel pour une gestion financière sereine.")
    
    col_l, col_r = st.columns([1, 1])
    
    with col_l:
        st.info("""
        **Pourquoi cette application ?**
        - 🔒 **Données locales** : Vos comptes ne quittent jamais votre ordinateur.
        - 🧠 **Intelligence Artificielle** : Catégorisation automatique et conseils personnalisés.
        - 📊 **Tableaux de bord** : Visualisez où part votre argent.
        """)
        
        st.divider()
        st.subheader("🚀 Démarrage Rapide")
        
        with st.form("onboarding_form"):
            st.write("Pour commencer, créons votre profil principal.")
            user_name = st.text_input("Votre Prénom", value="Moi", key='text_input_78')
            account_name = st.text_input("Nom de votre compte principal", value="Compte Principal", key='text_input_79')
            
            submit = st.form_submit_button("Commencer l'aventure ➡️", type="primary")
            
            if submit:
                # Create the first member
                add_member(user_name, "HOUSEHOLD")
                # We can't really "create" the account here as it's created on first import,
                # but we can store it in session state to pre-fill the import page.
                st.session_state['default_account_name'] = account_name
                st.session_state['onboarding_complete'] = True
                toast_success(f"Bienvenue {user_name} ! Configuration initiale créée.", icon="👋")
                st.rerun()

    with col_r:
        # Show a static image or features list
        st.markdown("#### Fonctionnalités Clés")
        st.markdown("""
        - **Import Universel** : BoursoBank, CSV générique...
        - **Nettoyage Intelligent** : Détection de doublons.
        - **Budgets** : Définissez vos limites par catégorie.
        """)
        
        # --- NEW: PROFILE SETUP FORM ---
        st.divider()
        from modules.ui.components.profile_form import render_profile_setup_form
        render_profile_setup_form(key_prefix="onboarding")
        
        # Button to reopen onboarding modal
        st.divider()
        if st.button("🎯 Guide de démarrage", use_container_width=True, type="secondary", key='button_109'):
            st.session_state['onboarding_dismissed'] = False
            st.session_state['onboarding_step'] = 1
            st.rerun()

    if st.session_state.get('onboarding_complete'):
        show_success(f"Parfait {user_name} ! Passons à l'import de vos premières données.")
        if st.button("Aller à l'import 📥", type="primary", key='button_116'):
            toast_success("Redirection vers l'import...", icon="📥")
            st.switch_page("pages/1_Import.py")

else:
    # === DASHBOARD MODE ===
    stats = get_global_stats()
    
    st.title("🏠 Accueil")
    
    # 🆕 DAILY WIDGET - Crée l'habitude quotidienne
    render_daily_widget()
    
    # 🆕 QUICK STATS ROW
    render_quick_stats_row()
    
    st.divider()
    
    # 1. Global KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        card_kpi("Transactions Totales", f"{stats.get('total_transactions', 0)}", trend="Données", trend_color="positive")
    with c2:
        last_date = stats.get('last_import')
        last_str = last_date if last_date else "Jamais"
        card_kpi("Dernier Import", last_str, trend="Date", trend_color="positive")
    with c3:
        sav = stats.get('current_month_savings', 0)
        color = "positive" if sav >= 0 else "negative"
        card_kpi("Épargne du Mois", f"{sav:+,.0f} €", trend=f"{stats.get('current_month_rate', 0):.1f}%", trend_color=color)
    with c4:
        st.write("")  # Placeholder or shortcut
        if st.button("📥 Nouvel Import", use_container_width=True, type="primary", key='button_148'):
            st.switch_page("pages/1_Import.py")
        if st.button("📊 Voir la Synthèse", use_container_width=True, key='button_150'):
            st.switch_page("pages/3_Synthese.py")
            
    st.divider()
    
    # 2. Key Actions & Status
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        # Nouvelles actions rapides avec popups
        render_quick_actions_grid()

    with c_right:
        # 🆕 SMART ACTIONS - remplace le bouton "Revoir le guide" inutile
        render_smart_actions()
    
    st.sidebar.success("✅ Application Initialisée")
    
    # Show App Info in Sidebar
    from modules.ui.layout import render_app_info
    render_app_info()
    
    # Scroll to top button
    render_scroll_to_top()
