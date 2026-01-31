"""
Notification system for FinancePerso.
Supports email notifications and desktop notifications for budget alerts.
"""
import os
import smtplib
import json
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from modules.logger import logger
from modules.db.connection import get_db_connection


def get_notification_settings():
    """Get notification settings from database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM settings WHERE key LIKE 'notif_%'")
        settings = {row[0]: row[1] for row in cursor.fetchall()}
        return settings


def save_notification_setting(key: str, value: str):
    """Save a notification setting."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO settings (key, value, description) 
               VALUES (?, ?, ?) 
               ON CONFLICT(key) DO UPDATE SET value = excluded.value""",
            (key, value, f"Notification setting: {key}")
        )
        conn.commit()


def send_desktop_notification(title: str, message: str):
    """
    Send a desktop notification.
    Works on macOS, Linux (with notify-send), and Windows.
    """
    try:
        import platform
        system = platform.system()
        
        if system == "Darwin":  # macOS
            import subprocess
            script = f'display notification "{message}" with title "{title}" sound name "Submarine"'
            subprocess.run(["osascript", "-e", script], check=True)
            return True
            
        elif system == "Linux":
            import subprocess
            subprocess.run(["notify-send", title, message], check=True)
            return True
            
        elif system == "Windows":
            try:
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=10)
                return True
            except ImportError:
                logger.warning("win10toast not installed, desktop notification skipped")
                return False
                
    except Exception as e:
        logger.error(f"Desktop notification failed: {e}")
        return False


def send_email_notification(subject: str, html_body: str, text_body: str = None):
    """
    Send an email notification.
    Requires SMTP configuration in settings.
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    settings = get_notification_settings()
    
    smtp_server = settings.get('notif_smtp_server', '')
    smtp_port = int(settings.get('notif_smtp_port', '587'))
    smtp_user = settings.get('notif_smtp_user', '')
    smtp_password = settings.get('notif_smtp_password', '')
    to_email = settings.get('notif_email_to', smtp_user)
    
    # Validation des paramètres
    if not smtp_server:
        return False, "Serveur SMTP non configuré"
    if not smtp_user:
        return False, "Email/Utilisateur SMTP non configuré"
    if not smtp_password:
        return False, "Mot de passe SMTP non configuré"
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = to_email
        
        # Attach text part
        if text_body:
            msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
        
        # Attach HTML part
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        logger.info(f"Email notification sent to {to_email}")
        return True, None
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = "Authentification échouée - vérifiez votre email et mot de passe (utilisez un App Password pour Gmail)"
        logger.error(f"Email auth failed: {e}")
        return False, error_msg
    except smtplib.SMTPConnectError as e:
        error_msg = f"Impossible de se connecter au serveur SMTP - vérifiez l'adresse et le port"
        logger.error(f"SMTP connection error: {e}")
        return False, error_msg
    except smtplib.SMTPRecipientsRefused as e:
        error_msg = f"Destinataire refusé - vérifiez l'adresse email"
        logger.error(f"SMTP recipient refused: {e}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Erreur d'envoi: {str(e)}"
        logger.error(f"Email notification failed: {e}")
        return False, error_msg


def check_budget_alerts(force_check: bool = False):
    """
    Check for budget overruns and send notifications.
    
    Args:
        force_check: If True, check even if already checked today
        
    Returns:
        List of alerts triggered
    """
    from modules.db.budgets import get_budgets
    from modules.db.transactions import get_all_transactions
    import pandas as pd
    
    settings = get_notification_settings()
    
    # Check if notifications are enabled
    if settings.get('notif_enabled', 'false').lower() != 'true':
        return []
    
    # Check if we already notified today (unless force_check)
    if not force_check:
        last_check = settings.get('notif_last_budget_check', '')
        today = datetime.now().strftime('%Y-%m-%d')
        if last_check == today:
            return []  # Already checked today
    
    # Update last check date
    save_notification_setting('notif_last_budget_check', datetime.now().strftime('%Y-%m-%d'))
    
    # Get budgets and current month transactions
    budgets = get_budgets()
    if budgets.empty:
        return []
    
    df = get_all_transactions()
    if df.empty:
        return []
    
    # Filter current month
    today = datetime.now()
    current_month = today.strftime('%Y-%m')
    df['date_dt'] = pd.to_datetime(df['date'])
    df_month = df[df['date_dt'].dt.strftime('%Y-%m') == current_month]
    
    # Calculate spending by category
    expenses_by_category = df_month[df_month['amount'] < 0].groupby('category_validated')['amount'].sum().abs()
    
    alerts = []
    
    for _, budget_row in budgets.iterrows():
        category = budget_row['category']
        budget_amount = budget_row['amount']
        spent = expenses_by_category.get(category, 0)
        
        if budget_amount <= 0:
            continue
        
        percentage = (spent / budget_amount) * 100
        
        # Determine alert level
        if percentage >= 100:
            alert_level = 'critical'
            alert_message = f"🚨 DÉPASSEMENT: {category}"
        elif percentage >= 90:
            alert_level = 'warning'
            alert_message = f"⚠️ Alerte: {category} à {percentage:.0f}%"
        elif percentage >= 75:
            alert_level = 'notice'
            alert_message = f"ℹ️ {category} à {percentage:.0f}% du budget"
        else:
            continue  # No alert needed
        
        # Check if we already sent this alert recently
        alert_key = f"notif_alert_sent_{current_month}_{category}_{alert_level}"
        if settings.get(alert_key) and not force_check:
            continue  # Already sent this alert
        
        alert = {
            'category': category,
            'budget': budget_amount,
            'spent': spent,
            'percentage': percentage,
            'level': alert_level,
            'message': alert_message
        }
        alerts.append(alert)
        
        # Mark as sent
        save_notification_setting(alert_key, datetime.now().isoformat())
    
    # Send notifications if alerts found
    if alerts:
        _send_budget_alert_notifications(alerts)
    
    return alerts


def _send_budget_alert_notifications(alerts):
    """Send notifications for budget alerts."""
    settings = get_notification_settings()
    
    # Build notification message
    critical_alerts = [a for a in alerts if a['level'] == 'critical']
    warning_alerts = [a for a in alerts if a['level'] == 'warning']
    notice_alerts = [a for a in alerts if a['level'] == 'notice']
    
    # Desktop notification
    if settings.get('notif_desktop', 'true').lower() == 'true':
        title = f"FinancePerso - {len(alerts)} alerte(s) budget"
        message_parts = []
        if critical_alerts:
            message_parts.append(f"{len(critical_alerts)} dépassement(s)")
        if warning_alerts:
            message_parts.append(f"{len(warning_alerts)} alerte(s)")
        message = " | ".join(message_parts) if message_parts else f"{len(alerts)} notification(s)"
        send_desktop_notification(title, message)
    
    # Email notification
    if settings.get('notif_email_enabled', 'false').lower() == 'true':
        subject = f"🚨 FinancePerso - Alertes budget {datetime.now().strftime('%B %Y')}"
        html_body = _build_budget_alert_email(alerts)
        text_body = _build_budget_alert_text(alerts)
        success, error = send_email_notification(subject, html_body, text_body)
        if not success:
            logger.warning(f"Budget alert email failed: {error}")


def _build_budget_alert_email(alerts):
    """Build HTML email for budget alerts."""
    current_month = datetime.now().strftime('%B %Y')
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background: #1F3A5F; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .alert {{ margin: 15px 0; padding: 15px; border-radius: 5px; }}
            .critical {{ background: #fee2e2; border-left: 4px solid #dc2626; }}
            .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; }}
            .notice {{ background: #dbeafe; border-left: 4px solid #3b82f6; }}
            .amount {{ font-size: 1.2em; font-weight: bold; }}
            .footer {{ margin-top: 30px; padding: 20px; text-align: center; color: #666; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 FinancePerso - Alertes Budget</h1>
            <p>{current_month}</p>
        </div>
        <div class="content">
            <p>Bonjour,</p>
            <p>Voici vos alertes budgétaires pour ce mois :</p>
    """
    
    for alert in alerts:
        level_class = alert['level']
        emoji = "🚨" if alert['level'] == 'critical' else "⚠️" if alert['level'] == 'warning' else "ℹ️"
        
        html += f"""
            <div class="alert {level_class}">
                <strong>{emoji} {alert['category']}</strong><br>
                <span class="amount">{alert['spent']:.2f}€ / {alert['budget']:.2f}€</span> 
                ({alert['percentage']:.1f}%)
            </div>
        """
    
    html += """
        </div>
        <div class="footer">
            <p>Notification envoyée par FinancePerso</p>
            <p><a href="http://localhost:8501">Ouvrir l'application</a></p>
        </div>
    </body>
    </html>
    """
    
    return html


def _build_budget_alert_text(alerts):
    """Build plain text email for budget alerts."""
    current_month = datetime.now().strftime('%B %Y')
    
    text = f"FinancePerso - Alertes Budget {current_month}\n"
    text += "=" * 40 + "\n\n"
    
    for alert in alerts:
        emoji = "🚨" if alert['level'] == 'critical' else "⚠️" if alert['level'] == 'warning' else "ℹ️"
        text += f"{emoji} {alert['category']}\n"
        text += f"   Dépensé: {alert['spent']:.2f}€ / Budget: {alert['budget']:.2f}€ ({alert['percentage']:.1f}%)\n\n"
    
    text += "\nOuvrir FinancePerso: http://localhost:8501"
    return text


def test_notification_settings():
    """Test notification configuration."""
    settings = get_notification_settings()
    results = {
        'desktop': False,
        'email': False,
        'errors': []
    }
    
    # Test desktop
    if settings.get('notif_desktop', 'true').lower() == 'true':
        results['desktop'] = send_desktop_notification(
            "Test FinancePerso",
            "Vos notifications desktop fonctionnent !"
        )
        if not results['desktop']:
            results['errors'].append("Notification desktop échouée")
    
    # Test email
    if settings.get('notif_email_enabled', 'false').lower() == 'true':
        success, error = send_email_notification(
            "Test FinancePerso - Notifications",
            "<h1>Test réussi !</h1><p>Vos notifications email fonctionnent.</p>",
            "Test réussi ! Vos notifications email fonctionnent."
        )
        results['email'] = success
        if not success:
            results['errors'].append(f"❌ Email: {error}")
    
    return results
