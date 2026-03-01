"""Système de notifications unifié v3.0 - FinancePerso

API publique pour le système de notifications.

Usage:
    from modules.notifications import NotificationService, NotificationType
    
    service = NotificationService()
    
    # Créer une notification
    service.notify(
        type=NotificationType.BUDGET_WARNING,
        title="Budget Alimentation",
        message="Vous avez atteint 85% de votre budget",
        actions=[{"label": "Voir", "action": "navigate", "target": "/budgets"}]
    )
    
    # Récupérer les non-lues
    unread = service.get_unread(limit=10)
    
    # Marquer comme lue
    service.mark_read(notification_id)

Architecture:
    - models.py : Dataclasses Notification, NotificationLevel, NotificationType
    - service.py : NotificationService (singleton)
    - repository.py : Accès données DB
    - detectors.py : Détecteurs de notifications
    - ui.py : Composants d'interface
"""

from .models import (
    NotificationLevel,
    NotificationType,
    Notification,
    NotificationAction,
    NotificationPreferences,
)
from .service import NotificationService
from .repository import NotificationRepository
from .detectors import DetectorRegistry

__all__ = [
    # Enums
    "NotificationLevel",
    "NotificationType",
    # Models
    "Notification",
    "NotificationAction",
    "NotificationPreferences",
    # Service
    "NotificationService",
    "NotificationRepository",
    # Detectors
    "DetectorRegistry",
    # Compatibility
    "get_notification_settings",
    "check_budget_alerts",
]

# Version du module
__version__ = "3.0.0"

# Version active du système de notifications
NOTIFICATION_SYSTEM_VERSION = "3.0"  # "3.0" pour V3, "2.0" pour rollback


def get_notification_service():
    """Retourne le service de notification actif.
    
    Returns:
        NotificationService: Instance du service de notifications V3
        ou NotificationManager: Instance du service V2 (legacy)
    """
    if NOTIFICATION_SYSTEM_VERSION == "3.0":
        return NotificationService()
    else:
        # Fallback V2
        from modules.ui.notifications import NotificationManager
        return NotificationManager()


def get_notification_settings() -> dict[str, str]:
    """Récupère les paramètres de notification (compatibilité legacy).
    
    Returns:
        Dict avec les paramètres de notification
    """
    try:
        service = NotificationService()
        prefs = service.get_preferences()
        
        # Mapping des préférences V3 vers format legacy
        return {
            "notif_enabled": "true" if prefs.critical_enabled or prefs.warning_enabled else "false",
            "notif_desktop": "true",
            "notif_email_enabled": "false",
            "notif_smtp_server": "smtp.gmail.com",
            "notif_smtp_port": "587",
            "notif_smtp_user": "",
            "notif_smtp_password": "",
            "notif_email_to": "",
            "notif_threshold_critical": str(prefs.budget_critical_threshold),
            "notif_threshold_warning": str(prefs.budget_warning_threshold),
            "notif_threshold_notice": "75",
            "notif_last_budget_check": "",
        }
    except Exception:
        # Valeurs par défaut si erreur
        return {
            "notif_enabled": "false",
            "notif_desktop": "true",
            "notif_email_enabled": "false",
            "notif_smtp_server": "smtp.gmail.com",
            "notif_smtp_port": "587",
            "notif_smtp_user": "",
            "notif_smtp_password": "",
            "notif_email_to": "",
            "notif_threshold_critical": "100",
            "notif_threshold_warning": "90",
            "notif_threshold_notice": "75",
            "notif_last_budget_check": "",
        }


def check_budget_alerts(force_check: bool = False) -> list[dict]:
    """Vérifie les budgets et génère des alertes (compatibilité legacy).
    
    Args:
        force_check: Si True, vérifie même si déjà envoyé aujourd'hui
        
    Returns:
        Liste des alertes sous forme de dictionnaires
    """
    from datetime import datetime
    
    from modules.db.budgets import get_budgets
    from modules.db.transactions import get_all_transactions
    from modules.logger import logger
    
    alerts = []
    
    try:
        settings = get_notification_settings()
        
        # Seuils
        critical_threshold = int(settings.get("notif_threshold_critical", "100"))
        warning_threshold = int(settings.get("notif_threshold_warning", "90"))
        
        # Budgets
        budgets_df = get_budgets()
        if budgets_df.empty:
            return alerts
        
        # Transactions du mois
        today = datetime.now()
        first_day = today.replace(day=1)
        
        all_tx = get_all_transactions()
        if not all_tx.empty and "date" in all_tx.columns and "category" in all_tx.columns:
            import pandas as pd
            
            all_tx["date"] = pd.to_datetime(all_tx["date"])
            month_tx = all_tx[(all_tx["date"] >= first_day) & (all_tx["date"] <= today)]
            
            spending_by_category = month_tx.groupby("category")["amount"].sum().to_dict()
            
            for _, budget in budgets_df.iterrows():
                category = budget["category"]
                limit = budget["amount"]
                spent = spending_by_category.get(category, 0)
                percentage = (spent / limit * 100) if limit > 0 else 0
                
                level = None
                if percentage >= critical_threshold:
                    level = "critical"
                elif percentage >= warning_threshold:
                    level = "warning"
                
                if level:
                    # Créer également une notification V3
                    service = NotificationService()
                    service.notify_budget(category, spent, limit, percentage)
                    
                    alert = {
                        "category": category,
                        "spent": spent,
                        "budget": limit,
                        "percentage": percentage,
                        "level": level,
                        "remaining": limit - spent,
                    }
                    alerts.append(alert)
        
    except Exception as e:
        logger.error(f"Error checking budget alerts: {e}")
    
    return alerts
