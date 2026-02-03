"""
Page de démonstration et gestion du nouveau système de notifications.

Cette page permet de :
- Tester les différents types de notifications
- Configurer les préférences
- Voir l'historique complet
"""

import streamlit as st

st.set_page_config(
    page_title="🔔 Notifications",
    page_icon="🔔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importer le nouveau système
from modules.ui.notifications import (
    # Fonctions principales
    success, warning, error, info, achievement, loading,
    # Centre de notifications
    render_notification_center_full,
    render_notification_settings,
    render_notifications_auto,
    # Composants spéciaux
    render_achievement_unlock,
    render_loading_state,
    render_empty_state,
    show_confirmation,
    render_inline_notification,
    NotificationAction,
    NotificationLevel,
)

# Afficher les notifications en attente
render_notifications_auto()

# Tabs pour organiser le contenu
tab_demo, tab_center, tab_settings = st.tabs([
    "🎮 Démonstration", 
    "📬 Centre de notifications", 
    "⚙️ Paramètres"
])

# ==================== TAB 1: DÉMONSTRATION ====================
with tab_demo:
    st.header("🎮 Démonstration des notifications")
    st.markdown("""
        Testez les différents types de notifications disponibles dans le nouveau système.
        Chaque type a une durée et un style adaptés à son importance.
    """)
    
    st.divider()
    
    # Section 1: Types de base
    st.subheader("📊 Types de notifications")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**✅ Succès** (3s)")
        if st.button("Test Succès", use_container_width=True, type="primary"):
            success("Opération réussie ! Vos données ont été sauvegardées.")
            st.rerun()
        
        st.caption("Pour confirmer une action réussie")
    
    with col2:
        st.markdown("**ℹ️ Info** (5s)")
        if st.button("Test Info", use_container_width=True):
            info("Une nouvelle mise à jour est disponible.")
            st.rerun()
        
        st.caption("Pour les informations contextuelles")
    
    with col3:
        st.markdown("**⚠️ Avertissement** (10s)")
        if st.button("Test Avertissement", use_container_width=True):
            warning("Votre budget 'Alimentation' est à 90%.")
            st.rerun()
        
        st.caption("Pour alerter sur une situation")
    
    st.divider()
    
    # Section 2: Types avancés
    st.subheader("🔔 Notifications avancées")
    
    col_adv1, col_adv2, col_adv3 = st.columns(3)
    
    with col_adv1:
        st.markdown("**🚨 Erreur** (Persistant)")
        if st.button("Test Erreur", use_container_width=True, type="secondary"):
            error(
                "Échec de la connexion à la base de données. Veuillez réessayer.",
                persistent=True
            )
            st.rerun()
        
        st.caption("Reste visible jusqu'à action")
    
    with col_adv2:
        st.markdown("**🏆 Achievement** (5s)")
        if st.button("Test Achievement", use_container_width=True):
            achievement(
                "Badge 'Import Expert' débloqué !",
                title="🎉 Félicitations !"
            )
            st.rerun()
        
        st.caption("Pour la gamification")
    
    with col_adv3:
        st.markdown("**🔄 Chargement**")
        if st.button("Test Chargement", use_container_width=True):
            notif = loading(
                "Import de 150 transactions en cours...",
                title="Traitement"
            )
            st.session_state['loading_notif_id'] = notif.id
            st.rerun()
        
        if st.session_state.get('loading_notif_id'):
            if st.button("Arrêter le chargement", type="primary"):
                from modules.ui.notifications import get_notification_manager
                manager = get_notification_manager()
                manager.dismiss(st.session_state['loading_notif_id'])
                del st.session_state['loading_notif_id']
                success("Import terminé !")
                st.rerun()
        
        st.caption("Persiste jusqu'à fermeture manuelle")
    
    st.divider()
    
    # Section 3: Avec actions
    st.subheader("🎬 Notifications avec actions")
    
    col_act1, col_act2 = st.columns(2)
    
    with col_act1:
        st.markdown("**Action contextuelle**")
        if st.button("Notification avec action", use_container_width=True):
            warning(
                "3 transactions en attente de validation",
                actions=[
                    NotificationAction(
                        label="Valider maintenant",
                        callback=lambda: st.switch_page("pages/2_Validation.py"),
                        primary=True,
                        icon="✅"
                    ),
                    NotificationAction(
                        label="Plus tard",
                        callback=lambda: None,
                        icon="⏰"
                    )
                ]
            )
            st.rerun()
    
    with col_act2:
        st.markdown("**Confirmation**")
        if st.button("Demande de confirmation", use_container_width=True):
            st.session_state['show_delete_confirm'] = True
            st.rerun()
        
        if st.session_state.get('show_delete_confirm'):
            show_confirmation(
                title="Supprimer toutes les données ?",
                message="Cette action est irréversible. Toutes vos transactions seront supprimées.",
                on_confirm=lambda: (
                    success("Données supprimées (simulation)")
                    or st.session_state.update({'show_delete_confirm': False})
                ),
                on_cancel=lambda: st.session_state.update({'show_delete_confirm': False}),
                confirm_label="Oui, tout supprimer",
                cancel_label="Annuler",
                danger=True,
                key="delete_confirm"
            )
    
    st.divider()
    
    # Section 4: Composants spéciaux
    st.subheader("🎨 Composants spéciaux")
    
    col_spec1, col_spec2 = st.columns(2)
    
    with col_spec1:
        if st.checkbox("Afficher Achievement Unlock"):
            render_achievement_unlock(
                title="Maître du Budget",
                description="Vous avez respecté tous vos budgets pendant 3 mois consécutifs !",
                icon="🏆",
                reward="+500 points fidélité"
            )
    
    with col_spec2:
        if st.checkbox("Afficher Loading State"):
            progress = st.session_state.get('demo_progress', 0.0)
            render_loading_state(
                message="Analyse de vos transactions...",
                submessage=f"Traitement en cours ({int(progress * 150)}/150)",
                progress=progress
            )
            
            # Simuler la progression
            if progress < 1.0:
                import time
                time.sleep(0.5)
                st.session_state['demo_progress'] = min(1.0, progress + 0.1)
                st.rerun()
            else:
                st.session_state['demo_progress'] = 0.0
                success("Analyse terminée !")


# ==================== TAB 2: CENTRE DE NOTIFICATIONS ====================
with tab_center:
    render_notification_center_full()


# ==================== TAB 3: PARAMÈTRES ====================
with tab_settings:
    st.header("⚙️ Configuration des notifications")
    st.markdown("""
        Personnalisez votre expérience de notification.
        Choisissez quels types de notifications vous souhaitez recevoir et pendant combien de temps.
    """)
    
    render_notification_settings()


# Sidebar
with st.sidebar:
    st.title("🔔 Notifications")
    st.caption("Nouveau système v2.0")
    
    st.divider()
    
    # Stats rapides
    from modules.ui.notifications import get_notification_manager
    manager = get_notification_manager()
    
    st.metric("Non lues", manager.unread_count)
    st.metric("Total historique", len(manager.notification_history))
    
    st.divider()
    
    # Raccourcis
    st.markdown("### 🚀 Raccourcis")
    
    if st.button("📥 Importer des données", use_container_width=True):
        st.switch_page("pages/1_Import.py")
    
    if st.button("📊 Voir la synthèse", use_container_width=True):
        st.switch_page("pages/3_Synthese.py")
    
    st.divider()
    
    st.caption("💡 Astuce : Les notifications vous aident à rester informé de l'état de vos finances.")
