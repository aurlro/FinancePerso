"""
Notification settings UI component.
Improved with preview mode and bulk save.
"""
import streamlit as st
from modules.notifications import (
    get_notification_settings,
    save_notification_setting,
    test_notification_settings,
    check_budget_alerts
)
from modules.ui.feedback import toast_success, toast_error, toast_warning, toast_info


def render_notification_settings():
    """Render the notification settings tab with preview mode."""
    
    # Get current settings
    settings = get_notification_settings()
    
    # Initialize preview state
    if 'notif_preview' not in st.session_state:
        st.session_state['notif_preview'] = {
            'notif_enabled': settings.get('notif_enabled', 'false').lower() == 'true',
            'notif_desktop': settings.get('notif_desktop', 'true').lower() == 'true',
            'notif_email_enabled': settings.get('notif_email_enabled', 'false').lower() == 'true',
            'notif_smtp_server': settings.get('notif_smtp_server', 'smtp.gmail.com'),
            'notif_smtp_port': settings.get('notif_smtp_port', '587'),
            'notif_smtp_user': settings.get('notif_smtp_user', ''),
            'notif_smtp_password': settings.get('notif_smtp_password', ''),
            'notif_email_to': settings.get('notif_email_to', ''),
            'notif_threshold_critical': int(settings.get('notif_threshold_critical', '100')),
            'notif_threshold_warning': int(settings.get('notif_threshold_warning', '90')),
            'notif_threshold_notice': int(settings.get('notif_threshold_notice', '75')),
        }
    
    preview = st.session_state['notif_preview']
    
    # --- GENERAL SETTINGS ---
    st.subheader("Paramètres généraux")
    
    preview['notif_enabled'] = st.toggle(
        "Activer les notifications",
        value=preview['notif_enabled'],
        help="Active/désactive toutes les notifications"
    )
    
    if not preview['notif_enabled']:
        st.info("🔕 Les notifications sont désactivées.")
        if st.button("💾 Sauvegarder", type="primary"):
            _save_all_settings(preview)
            st.success("✅ Paramètres sauvegardés !")
            st.rerun()
        return
    
    # --- DESKTOP NOTIFICATIONS ---
    st.divider()
    st.subheader("💻 Notifications Desktop")
    
    preview['notif_desktop'] = st.toggle(
        "Activer les notifications desktop",
        value=preview['notif_desktop'],
        help="Affiche des notifications sur votre bureau (macOS/Linux/Windows)"
    )
    
    if preview['notif_desktop']:
        st.caption("💡 Les notifications desktop fonctionnent sur macOS, Linux et Windows.")
    
    # --- EMAIL NOTIFICATIONS ---
    st.divider()
    st.subheader("📧 Notifications Email")
    
    preview['notif_email_enabled'] = st.toggle(
        "Activer les notifications email",
        value=preview['notif_email_enabled'],
        help="Envoie les alertes par email"
    )
    
    if preview['notif_email_enabled']:
        # Check if email is properly configured
        email_configured = all([
            preview['notif_smtp_server'],
            preview['notif_smtp_user'],
            preview['notif_smtp_password']
        ])
        
        if not email_configured:
            st.warning("⚠️ Configuration email incomplète - remplissez tous les champs SMTP")
        
        with st.container(border=True):
            st.markdown("**Configuration SMTP**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                preview['notif_smtp_server'] = st.text_input(
                    "Serveur SMTP",
                    value=preview['notif_smtp_server'],
                    placeholder="smtp.gmail.com"
                )
                
                preview['notif_smtp_user'] = st.text_input(
                    "Email / Utilisateur",
                    value=preview['notif_smtp_user'],
                    placeholder="votre.email@gmail.com"
                )
            
            with col2:
                preview['notif_smtp_port'] = st.number_input(
                    "Port",
                    value=int(preview['notif_smtp_port']),
                    min_value=1,
                    max_value=65535
                )
                
                preview['notif_smtp_password'] = st.text_input(
                    "Mot de passe / App Password",
                    value=preview['notif_smtp_password'],
                    type="password",
                    placeholder="••••••••"
                )
            
            # Email recipient
            preview['notif_email_to'] = st.text_input(
                "Destinataire (laisser vide = même que l'expéditeur)",
                value=preview['notif_email_to'],
                placeholder="votre.email@gmail.com"
            )
            
            st.info("""
            📌 **Note pour Gmail :**
            - Utilisez un "App Password" (Mot de passe d'application) au lieu de votre mot de passe principal
            - Activez l'authentification à 2 facteurs sur votre compte Google
            - Générez un App Password sur : https://myaccount.google.com/apppasswords
            """)
    
    # --- ALERT THRESHOLDS ---
    st.divider()
    st.subheader("⚡ Seuils d'alerte")
    
    col_t1, col_t2, col_t3 = st.columns(3)
    
    with col_t1:
        preview['notif_threshold_critical'] = st.slider(
            "🚨 Dépassement",
            min_value=90,
            max_value=100,
            value=preview['notif_threshold_critical'],
            step=5,
            help="Pourcentage du budget déclenchant une alerte critique"
        )
        st.caption(f"Alerte quand budget ≥ {preview['notif_threshold_critical']}%")
    
    with col_t2:
        preview['notif_threshold_warning'] = st.slider(
            "⚠️ Attention",
            min_value=70,
            max_value=95,
            value=preview['notif_threshold_warning'],
            step=5,
            help="Pourcentage du budget déclenchant un avertissement"
        )
        st.caption(f"Alerte quand budget ≥ {preview['notif_threshold_warning']}%")
    
    with col_t3:
        preview['notif_threshold_notice'] = st.slider(
            "ℹ️ Information",
            min_value=50,
            max_value=80,
            value=preview['notif_threshold_notice'],
            step=5,
            help="Pourcentage du budget déclenchant une notification informative"
        )
        st.caption(f"Alerte quand budget ≥ {preview['notif_threshold_notice']}%")
    
    # --- ACTION BUTTONS ---
    st.divider()
    
    col_save, col_test1, col_test2 = st.columns([2, 1, 1])
    
    with col_save:
        if st.button("💾 Sauvegarder les paramètres", type="primary", use_container_width=True):
            _save_all_settings(preview)
            st.success("✅ Paramètres sauvegardés !")
            st.rerun()
    
    with col_test1:
        if st.button("📤 Test notification", use_container_width=True):
            # Save temporarily for test
            _save_all_settings(preview)
            with st.spinner("Envoi en cours..."):
                results = test_notification_settings()
                
                if results['desktop']:
                    st.success("✅ Desktop OK !")
                if results['email']:
                    st.success("✅ Email OK !")
                
                if results['errors']:
                    for error in results['errors']:
                        st.error(f"{error}")
                        # Show helpful tips for common errors
                        if "Authentification" in error:
                            st.info("💡 **Pour Gmail:** Utilisez un 'App Password' généré sur https://myaccount.google.com/apppasswords")
                        elif "connecter" in error.lower():
                            st.info("💡 Vérifiez que le serveur SMTP et le port sont corrects (Gmail: smtp.gmail.com:587)")
                        elif "Destinataire" in error:
                            st.info("💡 Vérifiez que l'adresse email destinataire est valide")
                
                if not results['desktop'] and not results['email'] and not results['errors']:
                    st.warning("⚠️ Aucune notification activée")
    
    with col_test2:
        if st.button("🔔 Vérifier budgets", use_container_width=True):
            _save_all_settings(preview)
            with st.spinner("Analyse..."):
                alerts = check_budget_alerts(force_check=True)
                
                if alerts:
                    st.success(f"🚨 {len(alerts)} alerte(s) !")
                    for alert in alerts:
                        emoji = "🚨" if alert['level'] == 'critical' else "⚠️" if alert['level'] == 'warning' else "ℹ️"
                        st.write(f"{emoji} **{alert['category']}**: {alert['spent']:.0f}€ / {alert['budget']:.0f}€")
                else:
                    st.info("✅ Pas d'alerte")
    
    # --- ALERT HISTORY ---
    st.divider()
    st.subheader("📜 Historique des alertes")
    
    last_check = settings.get('notif_last_budget_check', 'Jamais')
    st.caption(f"Dernière vérification : {last_check}")
    
    # Count alerts sent this month
    current_month = __import__('datetime').datetime.now().strftime('%Y-%m')
    alert_count = sum(1 for key in settings.keys() if f'notif_alert_sent_{current_month}' in key)
    
    if alert_count > 0:
        st.write(f"📊 **{alert_count}** alerte(s) envoyée(s) ce mois-ci")
    else:
        st.write("📊 Aucune alerte ce mois-ci")


def _save_all_settings(preview):
    """Save all notification settings from preview state."""
    for key, value in preview.items():
        save_notification_setting(key, str(value))
    # Clear preview after save
    if 'notif_preview' in st.session_state:
        del st.session_state['notif_preview']
