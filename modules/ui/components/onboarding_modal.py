"""
Onboarding modal for first-time users.
Guides users through initial configuration.
"""
import streamlit as st
from modules.db.members import get_members
from modules.db.categories import get_categories
from modules.db.stats import is_app_initialized
from modules.notifications import get_notification_settings


def should_show_onboarding():
    """Check if onboarding should be shown."""
    # Check if user has dismissed onboarding
    if st.session_state.get('onboarding_dismissed', False):
        return False
    
    # Check if app is already configured
    if is_app_initialized():
        return False
    
    # Check minimum configuration
    members = get_members()
    categories = get_categories()
    
    # If no members or only default categories, show onboarding
    if members.empty or len(categories) <= 3:  # 3 = default categories
        return True
    
    return False


def dismiss_onboarding():
    """Mark onboarding as dismissed."""
    st.session_state['onboarding_dismissed'] = True


def render_onboarding_modal():
    """Render the onboarding modal dialog."""
    
    # Initialize step if needed
    if 'onboarding_step' not in st.session_state:
        st.session_state['onboarding_step'] = 1
    
    step = st.session_state['onboarding_step']
    
    # Create the modal
    @st.dialog("🚀 Bienvenue dans FinancePerso !", width="large")
    def show_modal():
        # Progress indicator
        total_steps = 4
        progress = step / total_steps
        st.progress(progress, text=f"Étape {step} sur {total_steps}")
        
        # --- STEP 1: Welcome ---
        if step == 1:
            st.markdown("""
            ## Votre assistant financier personnel
            
            FinancePerso vous aide à :
            - 📥 **Importer** vos relevés bancaires automatiquement
            - 🏷️ **Catégoriser** vos dépenses avec l'IA
            - 📊 **Visualiser** où va votre argent
            - 🔔 **Surveiller** vos budgets
            
            ### Commençons par la configuration initiale !
            """)
            
            st.info("⏱️ Cela prend environ 2 minutes")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("⏭️ Plus tard", use_container_width=True, key='button_73'):
                    dismiss_onboarding()
                    st.rerun()
            with col2:
                if st.button("🚀 Commencer", type="primary", use_container_width=True, key='button_77'):
                    st.session_state['onboarding_step'] = 2
                    st.rerun()
        
        # --- STEP 2: Members ---
        elif step == 2:
            st.markdown("""
            ## 👥 Qui utilise les comptes ?
            
            Ajoutez les membres de votre foyer pour pouvoir attribuer les dépenses.
            """)
            
            members = get_members()
            if not members.empty:
                st.success(f"✅ {len(members)} membre(s) déjà configuré(s) : {', '.join(members['name'].tolist())}")
            
            with st.form("add_member_form"):
                new_member = st.text_input("Nom du membre", placeholder="Ex: Aurélien, Élise...", key='text_input_94')
                member_type = st.selectbox(
                    "Type",
                    options=["HOUSEHOLD", "EXTERNAL"],
                    format_func=lambda x: "Membre du foyer" if x == "HOUSEHOLD" else "Extérieur (tiers)",
                    help="Membre du foyer = vous ou votre famille. Extérieur = prestataires, amis..."
                )
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    submitted = st.form_submit_button("➕ Ajouter", use_container_width=True)
                with col2:
                    skip = st.form_submit_button("⏭️ Passer →", use_container_width=True)
                
                if submitted and new_member:
                    from modules.db.members import add_member
                    if add_member(new_member, member_type):
                        st.success(f"✅ {new_member} ajouté !")
                        st.rerun()
                    else:
                        st.warning(f"⚠️ {new_member} existe déjà")
                
                if skip:
                    st.session_state['onboarding_step'] = 3
                    st.rerun()
            
            st.divider()
            col_nav1, col_nav2 = st.columns([1, 1])
            with col_nav1:
                if st.button("← Retour", use_container_width=True, key='button_123'):
                    st.session_state['onboarding_step'] = 1
                    st.rerun()
            with col_nav2:
                if st.button("Suivant →", use_container_width=True, key='button_127'):
                    st.session_state['onboarding_step'] = 3
                    st.rerun()
        
        # --- STEP 3: Categories ---
        elif step == 3:
            st.markdown("""
            ## 🏷️ Vos catégories de dépenses
            
            Quelles sont vos principales catégories de dépenses ?
            
            💡 **Conseil** : Commencez simple (5-10 catégories), vous pourrez en ajouter plus tard.
            """)
            
            # Show current categories
            categories = get_categories()
            if categories:
                st.caption(f"Catégories existantes : {', '.join(categories)}")
            
            # Quick add categories
            quick_cats = st.multiselect(
                "Catégories suggérées (sélectionnez celles qui vous concernent)",
                options=[
                    "🍽️ Alimentation",
                    "🏠 Logement", 
                    "🚗 Transport",
                    "💡 Factures",
                    "🏥 Santé",
                    "🎮 Loisirs",
                    "🛒 Shopping",
                    "📱 Abonnements",
                    "🐕 Animaux",
                    "✈️ Voyages",
                    "💰 Revenus",
                    "🏦 Épargne"
                ],
                default=["🍽️ Alimentation", "🏠 Logement", "🚗 Transport", "💰 Revenus"]
            )
            
            # Custom category
            custom_cat = st.text_input("Ou créez une catégorie personnalisée", placeholder="Ex: Sport, Enfants...", key='text_input_167')
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("➕ Ajouter les catégories", use_container_width=True, key='button_171'):
                    from modules.db.categories import add_category
                    added = 0
                    
                    for cat in quick_cats:
                        # Extract emoji and name
                        emoji = cat[:2]
                        name = cat[2:].strip()
                        if add_category(name, emoji=emoji):
                            added += 1
                    
                    if custom_cat:
                        if add_category(custom_cat, emoji="🏷️"):
                            added += 1
                    
                    if added > 0:
                        st.success(f"✅ {added} catégorie(s) ajoutée(s) !")
                        st.rerun()
                    else:
                        st.info("ℹ️ Toutes les catégories existent déjà")
            
            with col2:
                if st.button("⏭️ Passer →", use_container_width=True, key='button_193'):
                    st.session_state['onboarding_step'] = 4
                    st.rerun()
            
            st.divider()
            col_nav1, col_nav2 = st.columns([1, 1])
            with col_nav1:
                if st.button("← Retour", use_container_width=True, key='button_200'):
                    st.session_state['onboarding_step'] = 2
                    st.rerun()
            with col_nav2:
                if st.button("Suivant →", use_container_width=True, key='button_204'):
                    st.session_state['onboarding_step'] = 4
                    st.rerun()
        
        # --- STEP 4: Optional Settings ---
        elif step == 4:
            st.markdown("""
            ## ⚡ Paramètres optionnels
            
            Ces réglages peuvent être faits maintenant ou plus tard.
            """)
            
            # API Key section
            st.subheader("🤖 Intelligence Artificielle (optionnel)")
            st.caption("L'IA aide à catégoriser automatiquement vos transactions.")
            
            has_api_key = bool(st.secrets.get("GEMINI_API_KEY") or 
                             st.secrets.get("OPENAI_API_KEY") or
                             __import__('os').getenv("GEMINI_API_KEY"))
            
            if has_api_key:
                st.success("✅ Clé API détectée ! L'IA est active.")
            else:
                st.info("🌐 Mode hors ligne : seules les règles manuelles seront utilisées.")
                st.markdown("""
                Pour activer l'IA plus tard :
                1. Obtenez une clé API gratuite sur [Google AI Studio](https://aistudio.google.com/app/apikey)
                2. Configurez-la dans **⚙️ Configuration → 🔑 API & Services**
                """)
            
            st.divider()
            
            # Notifications section
            st.subheader("🔔 Notifications (optionnel)")
            st.caption("Soyez alerté quand vous dépassez vos budgets.")
            
            settings = get_notification_settings()
            notif_enabled = settings.get('notif_enabled', 'false').lower() == 'true'
            
            if notif_enabled:
                st.success("✅ Notifications activées !")
            else:
                st.info("🔕 Notifications désactivées. Activez-les dans la configuration.")
            
            st.divider()
            
            # Final step
            st.success("🎉 Configuration initiale terminée !")
            st.markdown("""
            ### Prochaines étapes :
            1. **Importez** votre premier relevé bancaire (page 📥 Import)
            2. **Validez** quelques transactions (page ✅ Validation)
            3. **Consultez** votre tableau de bord (page 📊 Synthèse)
            """)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 C'est parti !", type="primary", use_container_width=True, key='button_261'):
                    dismiss_onboarding()
                    st.rerun()
            
            st.divider()
            if st.button("← Retour", use_container_width=True, key='button_266'):
                st.session_state['onboarding_step'] = 3
                st.rerun()
    
    # Show the modal
    show_modal()


def render_floating_help_button():
    """Render a floating help button for quick access to onboarding."""
    st.markdown("""
    <style>
    .floating-help {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([6, 6, 1])
    with col3:
        if st.button("❓", help="Réouvrir le guide de démarrage", key='button_289'):
            st.session_state['onboarding_dismissed'] = False
            st.session_state['onboarding_step'] = 1
            st.rerun()
