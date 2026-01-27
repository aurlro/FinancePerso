import streamlit as st
from modules.ui import load_css, card_kpi
from modules.data_manager import init_db, is_app_initialized, get_global_stats, add_member

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="MyFinance Companion",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()
init_db()

# --- MAIN LOGIC ---

if not is_app_initialized():
    # === ONBOARDING MODE ===
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
            user_name = st.text_input("Votre Prénom", value="Moi")
            account_name = st.text_input("Nom de votre compte principal", value="Compte Principal")
            
            submit = st.form_submit_button("Commencer l'aventure ➡️", type="primary")
            
            if submit:
                # Create the first member
                add_member(user_name, "HOUSEHOLD")
                # We can't really "create" the account here as it's created on first import,
                # but we can store it in session state to pre-fill the import page.
                st.session_state['default_account_name'] = account_name
                st.session_state['onboarding_complete'] = True
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

    if st.session_state.get('onboarding_complete'):
        st.success(f"Parfait {user_name} ! Passons à l'import de vos premières données.")
        if st.button("Aller à l'import 📥"):
            st.switch_page("pages/1_Import.py")

else:
    # === DASHBOARD MODE ===
    stats = get_global_stats()
    
    st.title("🏠 Accueil")
    
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
        st.write("") # Placeholder or shortcut
        if st.button("📥 Nouvel Import", use_container_width=True, type="primary"):
            st.switch_page("pages/1_Import.py")
        if st.button("📊 Voir la Synthèse", use_container_width=True):
            st.switch_page("pages/3_Synthese.py")
            
    st.divider()
    
    # 2. Key Actions & Status
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        st.subheader("📌 Actions Rapides")
        col_a, col_b = st.columns(2)
        with col_a:
            with st.container(border=True):
                st.markdown("#### 🧠 Validation IA")
                st.caption("Vérifiez les catégories proposées par l'assistant.")
                if st.button("Valider les transactions"):
                    st.switch_page("pages/2_Validation.py")
        
        with col_b:
            with st.container(border=True):
                st.markdown("#### ⚙️ Configuration")
                st.caption("Gérez les règles, les membres et les préférences.")
                if st.button("Paramètres"):
                    st.switch_page("pages/9_Configuration.py")

    with c_right:
        st.subheader("💡 Le saviez-vous ?")
        st.info("Vous pouvez définir des règles automatiques pour classer vos dépenses récurrentes directement depuis la page 'Validation'.")
        
    st.sidebar.success("✅ Application Initialisée")
    
    # Show App Info in Sidebar
    from modules.ui.layout import render_app_info
    render_app_info()

