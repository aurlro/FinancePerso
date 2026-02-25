# AGENT-016: Notification System Architect

## 🎯 Mission

Architecte du système de notifications. Responsable des alertes en temps réel, des rapports programmés, et des intégrations externes (email, webhooks). Garant que les utilisateurs sont informés des événements importants.

---

## 📚 Contexte: Architecture Notifications

### Types de Notifications

```
┌─────────────────────────────────────────────────────────────────────┐
│                    NOTIFICATION ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  IN-APP (Streamlit)                                                 │
│  ├── Toast notifications (actions)                                 │
│  ├── Banner alerts (budget warnings)                               │
│  └── Badge counts (transactions en attente)                        │
│                                                                      │
│  EMAIL                                                              │
│  ├── Weekly digest (résumé hebdo)                                  │
│  ├── Budget alerts (dépassement)                                   │
│  └── Security alerts (nouvelle connexion)                          │
│                                                                      │
│  WEBHOOKS                                                           │
│  ├── Zapier / Make.com integrations                                │
│  └── Custom endpoints                                              │
│                                                                      │
│  PUSH (Future)                                                      │
│  ├── Mobile push notifications                                     │
│  └── Browser push                                                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Modèle de Données

```python
# modules/notifications/models.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum

class NotificationType(Enum):
    BUDGET_ALERT = "budget_alert"
    TRANSACTION_ALERT = "transaction_alert"
    GOAL_MILESTONE = "goal_milestone"
    WEEKLY_DIGEST = "weekly_digest"
    SECURITY_ALERT = "security_alert"
    SYSTEM_UPDATE = "system_update"

class NotificationChannel(Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    WEBHOOK = "webhook"
    PUSH = "push"

class NotificationPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class Notification:
    """Notification entity."""
    id: int
    member_id: int
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    data: Dict                           # Payload JSON
    channels: List[NotificationChannel]  # Canaux à utiliser
    read: bool = False
    read_at: Optional[datetime] = None
    created_at: datetime = None

@dataclass
class NotificationRule:
    """Règle de notification automatique."""
    id: int
    member_id: int
    name: str
    type: NotificationType
    condition: str                       # Expression conditionnelle
    channels: List[NotificationChannel]
    enabled: bool = True
    cooldown_hours: int = 24             # Anti-spam
    last_triggered: Optional[datetime] = None
```

---

## 🧱 Module 1: Notification Engine

### Gestion des Notifications

```python
# modules/notifications/engine.py

class NotificationEngine:
    """Moteur de notifications."""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.dispatchers = {
            NotificationChannel.IN_APP: InAppDispatcher(),
            NotificationChannel.EMAIL: EmailDispatcher(),
            NotificationChannel.WEBHOOK: WebhookDispatcher()
        }
    
    def create_notification(
        self,
        member_id: int,
        type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        data: dict = None,
        channels: List[NotificationChannel] = None
    ) -> Notification:
        """
        Crée une nouvelle notification.
        
        Args:
            member_id: Membre destinataire
            type: Type de notification
            title: Titre court
            message: Message détaillé
            priority: Priorité
            data: Données additionnelles
            channels: Canaux de diffusion
        """
        if channels is None:
            channels = [NotificationChannel.IN_APP]
        
        if data is None:
            data = {}
        
        cursor = self.db.cursor()
        
        cursor.execute("""
            INSERT INTO notifications 
            (member_id, type, priority, title, message, data, channels, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            member_id,
            type.value,
            priority.value,
            title,
            message,
            json.dumps(data),
            json.dumps([c.value for c in channels]),
            datetime.now()
        ))
        
        self.db.commit()
        
        notification = Notification(
            id=cursor.lastrowid,
            member_id=member_id,
            type=type,
            priority=priority,
            title=title,
            message=message,
            data=data,
            channels=channels
        )
        
        # Dispatcher
        self._dispatch(notification)
        
        return notification
    
    def _dispatch(self, notification: Notification):
        """Envoie la notification sur tous les canaux."""
        for channel in notification.channels:
            dispatcher = self.dispatchers.get(channel)
            if dispatcher:
                try:
                    dispatcher.send(notification)
                except Exception as e:
                    logger.error(f"Failed to dispatch {channel.value}: {e}")
    
    def get_unread_notifications(
        self,
        member_id: int,
        limit: int = 50
    ) -> List[Notification]:
        """Récupère les notifications non lues."""
        cursor = self.db.cursor()
        
        cursor.execute("""
            SELECT * FROM notifications
            WHERE member_id = ? AND read = 0
            ORDER BY created_at DESC
            LIMIT ?
        """, (member_id, limit))
        
        return [self._row_to_notification(row) for row in cursor.fetchall()]
    
    def mark_as_read(self, notification_id: int):
        """Marque une notification comme lue."""
        cursor = self.db.cursor()
        
        cursor.execute("""
            UPDATE notifications 
            SET read = 1, read_at = ?
            WHERE id = ?
        """, (datetime.now(), notification_id))
        
        self.db.commit()
    
    def _row_to_notification(self, row) -> Notification:
        """Convertit une ligne DB en Notification."""
        return Notification(
            id=row['id'],
            member_id=row['member_id'],
            type=NotificationType(row['type']),
            priority=NotificationPriority(row['priority']),
            title=row['title'],
            message=row['message'],
            data=json.loads(row['data']),
            channels=[NotificationChannel(c) for c in json.loads(row['channels'])],
            read=bool(row['read']),
            read_at=row['read_at'],
            created_at=row['created_at']
        )
```

---

## 🧱 Module 2: Dispatchers

### In-App Dispatcher

```python
# modules/notifications/dispatchers.py

class InAppDispatcher:
    """Dispatcher pour notifications in-app (Streamlit)."""
    
    def send(self, notification: Notification):
        """Affiche la notification dans l'interface."""
        import streamlit as st
        
        # Stocker dans session state pour affichage
        if 'notifications' not in st.session_state:
            st.session_state['notifications'] = []
        
        st.session_state['notifications'].append({
            'id': notification.id,
            'type': notification.type.value,
            'priority': notification.priority.value,
            'title': notification.title,
            'message': notification.message,
            'timestamp': datetime.now()
        })
        
        # Limiter à 10 notifications
        st.session_state['notifications'] = st.session_state['notifications'][-10:]

class EmailDispatcher:
    """Dispatcher pour emails."""
    
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_pass = os.getenv('SMTP_PASS')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@financeperso.local')
    
    def send(self, notification: Notification):
        """Envoie un email."""
        if notification.priority not in [NotificationPriority.HIGH, NotificationPriority.URGENT]:
            # Ne pas spammer pour les notifs normales
            return
        
        # Récupérer email membre
        member_email = self._get_member_email(notification.member_id)
        if not member_email:
            return
        
        subject = f"[{notification.priority.value.upper()}] {notification.title}"
        body = self._render_email_template(notification)
        
        # Envoi SMTP
        import smtplib
        from email.mime.text import MIMEText
        
        msg = MIMEText(body, 'html')
        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = member_email
        
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            server.send_message(msg)
    
    def _render_email_template(self, notification: Notification) -> str:
        """Rend le template email."""
        colors = {
            NotificationPriority.URGENT: '#DC2626',
            NotificationPriority.HIGH: '#F59E0B',
            NotificationPriority.NORMAL: '#3B82F6',
            NotificationPriority.LOW: '#6B7280'
        }
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: {colors.get(notification.priority, '#333')};">
                    {notification.title}
                </h2>
                <p>{notification.message}</p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                    Envoyé par FinancePerso le {datetime.now().strftime('%d/%m/%Y %H:%M')}
                </p>
            </div>
        </body>
        </html>
        """

class WebhookDispatcher:
    """Dispatcher pour webhooks."""
    
    def send(self, notification: Notification):
        """Envoie au webhook configuré."""
        cursor = self.db.cursor()
        
        cursor.execute("""
            SELECT url, secret FROM webhooks 
            WHERE member_id = ? AND active = 1
        """, (notification.member_id,))
        
        webhooks = cursor.fetchall()
        
        import requests
        import hmac
        import hashlib
        
        payload = {
            'type': notification.type.value,
            'priority': notification.priority.value,
            'title': notification.title,
            'message': notification.message,
            'data': notification.data,
            'timestamp': datetime.now().isoformat()
        }
        
        for webhook in webhooks:
            # Signer le payload
            signature = hmac.new(
                webhook['secret'].encode(),
                json.dumps(payload).encode(),
                hashlib.sha256
            ).hexdigest()
            
            try:
                requests.post(
                    webhook['url'],
                    json=payload,
                    headers={
                        'X-FinancePerso-Signature': signature,
                        'Content-Type': 'application/json'
                    },
                    timeout=10
                )
            except Exception as e:
                logger.error(f"Webhook failed: {e}")
```

---

## 🧱 Module 3: Scheduled Reports

### Rapports Programmés

```python
# modules/notifications/reports.py

class ReportScheduler:
    """Programmateur de rapports."""
    
    def generate_weekly_digest(self, member_id: int) -> dict:
        """
        Génère le résumé hebdomadaire.
        
        Returns:
            Données pour le rapport
        """
        cursor = self.db.cursor()
        
        # Période: semaine dernière
        from_date = datetime.now() - timedelta(days=7)
        
        # Dépenses totales
        cursor.execute("""
            SELECT COALESCE(SUM(ABS(amount)), 0) as total
            FROM transactions
            WHERE member_id = ?
            AND date >= ?
            AND amount < 0
        """, (member_id, from_date.date()))
        
        total_expenses = cursor.fetchone()['total']
        
        # Top catégories
        cursor.execute("""
            SELECT category_validated, SUM(ABS(amount)) as total
            FROM transactions
            WHERE member_id = ?
            AND date >= ?
            AND amount < 0
            GROUP BY category_validated
            ORDER BY total DESC
            LIMIT 5
        """, (member_id, from_date.date()))
        
        top_categories = cursor.fetchall()
        
        # Comparaison semaine précédente
        cursor.execute("""
            SELECT COALESCE(SUM(ABS(amount)), 0) as total
            FROM transactions
            WHERE member_id = ?
            AND date >= ? AND date < ?
            AND amount < 0
        """, (member_id, (from_date - timedelta(days=7)).date(), from_date.date()))
        
        previous_week = cursor.fetchone()['total']
        
        change_pct = ((total_expenses - previous_week) / previous_week * 100) if previous_week > 0 else 0
        
        return {
            'period': 'weekly',
            'from_date': from_date.date(),
            'to_date': datetime.now().date(),
            'total_expenses': total_expenses,
            'previous_week_expenses': previous_week,
            'change_percentage': change_pct,
            'top_categories': [
                {'category': row['category_validated'], 'amount': row['total']}
                for row in top_categories
            ],
            'transactions_count': self._get_transaction_count(member_id, from_date.date())
        }
    
    def send_scheduled_reports(self):
        """Envoie les rapports programmés."""
        cursor = self.db.cursor()
        
        # Vérifier quels rapports doivent être envoyés
        cursor.execute("""
            SELECT * FROM scheduled_reports
            WHERE next_run <= ?
        """, (datetime.now(),))
        
        for report in cursor.fetchall():
            member_id = report['member_id']
            report_type = report['report_type']
            
            if report_type == 'weekly_digest':
                data = self.generate_weekly_digest(member_id)
                
                notification = NotificationEngine(self.db).create_notification(
                    member_id=member_id,
                    type=NotificationType.WEEKLY_DIGEST,
                    title="Votre résumé hebdomadaire",
                    message=f"Dépenses cette semaine: {data['total_expenses']:.2f} EUR",
                    data=data,
                    channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL]
                )
            
            # Mettre à jour next_run
            next_run = self._calculate_next_run(report['frequency'])
            cursor.execute("""
                UPDATE scheduled_reports 
                SET last_run = ?, next_run = ?
                WHERE id = ?
            """, (datetime.now(), next_run, report['id']))
        
        self.db.commit()
```

---

## 🧱 Module 4: Budget Alerts

### Alertes Budgétaires Automatiques

```python
# modules/notifications/budget_alerts.py

class BudgetAlertRule:
    """Règles d'alerte budget."""
    
    RULES = [
        {
            'name': 'budget_warning',
            'condition': 'percentage >= 80 AND percentage < 100',
            'message': 'Budget {category} à {percentage:.0f}%',
            'priority': NotificationPriority.NORMAL,
            'cooldown': 24  # hours
        },
        {
            'name': 'budget_exceeded',
            'condition': 'percentage >= 100',
            'message': 'Budget {category} dépassé!',
            'priority': NotificationPriority.HIGH,
            'cooldown': 12
        },
        {
            'name': 'unusual_spending',
            'condition': 'daily_avg > normal_daily_avg * 2',
            'message': 'Dépense inhabituelle détectée: {amount} EUR',
            'priority': NotificationPriority.HIGH,
            'cooldown': 1
        }
    ]
    
    def check_and_notify(self, member_id: int):
        """Vérifie les règles et envoie les alertes."""
        from modules.budgets.engine import BudgetEngine
        
        engine = BudgetEngine(self.db)
        spending = engine.get_spending_vs_budget()
        
        for item in spending:
            for rule in self.RULES:
                if self._evaluate_condition(rule['condition'], item):
                    # Vérifier cooldown
                    if not self._is_in_cooldown(member_id, rule['name'], rule['cooldown']):
                        self._send_alert(member_id, rule, item)
    
    def _evaluate_condition(self, condition: str, data: dict) -> bool:
        """Évalue une condition."""
        try:
            # Remplacer variables
            expr = condition
            for key, value in data.items():
                expr = expr.replace(key, str(value))
            
            return eval(expr)
        except:
            return False
```

---

**Version**: 1.0
**Date**: 2026-02-25
**Statut**: PRÊT À L'EMPLOI


---

## 🔧 Module Additionnel: Tests & Intégrations

### Tests Unitaires

```python
# tests/unit/test_notifications.py
"""
Tests du système de notifications.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from modules.notifications.engine import NotificationEngine
from modules.notifications.dispatchers import InAppDispatcher, EmailDispatcher
from modules.notifications.reports import ReportScheduler

class TestNotificationEngine:
    """Tests du moteur de notifications."""
    
    def test_create_notification(self, db_connection):
        """Test création d'une notification."""
        engine = NotificationEngine(db_connection)
        
        notif = engine.create_notification(
            member_id=1,
            type=NotificationType.BUDGET_ALERT,
            title="Test Alert",
            message="Message de test",
            priority=NotificationPriority.NORMAL
        )
        
        assert notif.title == "Test Alert"
        assert notif.read == False
        assert notif.id is not None
    
    def test_get_unread_notifications(self, db_connection):
        """Test récupération notifications non lues."""
        engine = NotificationEngine(db_connection)
        
        # Créer notifications
        engine.create_notification(1, NotificationType.BUDGET_ALERT, "A", "Msg")
        engine.create_notification(1, NotificationType.BUDGET_ALERT, "B", "Msg")
        
        # Marquer une comme lue
        notifs = engine.get_unread_notifications(1)
        engine.mark_as_read(notifs[0].id)
        
        # Vérifier
        unread = engine.get_unread_notifications(1)
        assert len(unread) == 1
    
    @patch('modules.notifications.dispatchers.smtplib')
    def test_email_dispatch(self, mock_smtp, db_connection):
        """Test dispatch email."""
        dispatcher = EmailDispatcher()
        
        notif = Mock()
        notif.title = "Test"
        notif.message = "Message"
        notif.priority = NotificationPriority.HIGH
        
        # Simuler envoi
        with patch.object(dispatcher, '_get_member_email', return_value='test@example.com'):
            dispatcher.send(notif)
        
        # Vérifier SMTP appelé
        mock_smtp.SMTP.assert_called_once()

class TestReportScheduler:
    """Tests du programmateur de rapports."""
    
    def test_generate_weekly_digest(self, db_connection, sample_transactions):
        """Test génération digest hebdomadaire."""
        scheduler = ReportScheduler()
        
        # Insérer transactions
        for tx in sample_transactions:
            insert_transaction(db_connection, tx)
        
        digest = scheduler.generate_weekly_digest(member_id=1)
        
        assert 'total_expenses' in digest
        assert 'top_categories' in digest
        assert 'change_percentage' in digest
    
    def test_budget_alert_rule_evaluation(self, db_connection):
        """Test évaluation règles d'alerte."""
        from modules.notifications.budget_alerts import BudgetAlertRule
        
        rule_engine = BudgetAlertRule()
        
        # Simuler données dépassement
        spending_data = {
            'category': 'Alimentation',
            'percentage': 95.0,
            'daily_avg': 100.0,
            'normal_daily_avg': 30.0
        }
        
        # Vérifier condition déclenchée
        triggered = rule_engine._evaluate_condition(
            'percentage >= 80 AND percentage < 100',
            spending_data
        )
        
        assert triggered == True

class TestNotificationRules:
    """Tests des règles de notification automatique."""
    
    def test_cooldown_prevents_spam(self, db_connection):
        """Test cooldown anti-spam."""
        engine = NotificationEngine(db_connection)
        
        # Créer règle avec cooldown
        rule = NotificationRule(
            id=1,
            member_id=1,
            name="Test Rule",
            type=NotificationType.BUDGET_ALERT,
            condition="amount > 100",
            channels=[NotificationChannel.IN_APP],
            cooldown_hours=24,
            last_triggered=datetime.now() - timedelta(hours=1)  # 1h ago
        )
        
        # Ne devrait pas déclencher (cooldown actif)
        should_trigger = engine.check_rule_cooldown(rule)
        
        assert should_trigger == False
```

### Imports Standardisés

```python
# modules/notifications/__init__.py
"""
Module notifications - Imports standardisés.
"""

import logging
import sqlite3
import json
import time
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict
from enum import Enum
from dataclasses import dataclass
import requests
import hmac
import hashlib

logger = logging.getLogger(__name__)

# Exports
from .engine import NotificationEngine, Notification, NotificationRule
from .models import NotificationType, NotificationChannel, NotificationPriority
from .dispatchers import InAppDispatcher, EmailDispatcher, WebhookDispatcher
from .reports import ReportScheduler
from .budget_alerts import BudgetAlertRule

__all__ = [
    'NotificationEngine',
    'Notification',
    'NotificationRule',
    'NotificationType',
    'NotificationChannel',
    'NotificationPriority',
    'InAppDispatcher',
    'EmailDispatcher',
    'WebhookDispatcher',
    'ReportScheduler',
    'BudgetAlertRule',
    'logger'
]
```

### Configuration

```python
# modules/notifications/config.py
"""
Configuration du module notifications.
"""

# Canaux activés par défaut
DEFAULT_CHANNELS = [NotificationChannel.IN_APP]

# Cooldowns par type (heures)
DEFAULT_COOLDOWNS = {
    NotificationType.BUDGET_ALERT: 12,
    NotificationType.TRANSACTION_ALERT: 1,
    NotificationType.GOAL_MILESTONE: 24,
    NotificationType.WEEKLY_DIGEST: 168,  # 7 jours
    NotificationType.SECURITY_ALERT: 0,    # Pas de cooldown
}

# Priorités par type
DEFAULT_PRIORITIES = {
    NotificationType.BUDGET_ALERT: NotificationPriority.NORMAL,
    NotificationType.TRANSACTION_ALERT: NotificationPriority.LOW,
    NotificationType.GOAL_MILESTONE: NotificationPriority.NORMAL,
    NotificationType.WEEKLY_DIGEST: NotificationPriority.LOW,
    NotificationType.SECURITY_ALERT: NotificationPriority.HIGH,
    NotificationType.SYSTEM_UPDATE: NotificationPriority.NORMAL
}

# Configuration email
EMAIL_CONFIG = {
    'smtp_host': 'smtp.gmail.com',
    'smtp_port': 587,
    'use_tls': True,
    'from_email': 'noreply@financeperso.local',
    'from_name': 'FinancePerso'
}

# Configuration webhook
WEBHOOK_CONFIG = {
    'timeout_seconds': 10,
    'retry_attempts': 3,
    'signature_header': 'X-FinancePerso-Signature'
}
```

### Intégrations Externes

```python
# modules/notifications/integrations/slack.py
"""
Intégration Slack pour notifications.
"""

import requests
import json

class SlackIntegration:
    """Client Slack pour notifications."""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_budget_alert(self, alert: dict):
        """Envoie une alerte budget sur Slack."""
        color = '#EF4444' if alert['status'] == 'exceeded' else '#F59E0B'
        
        payload = {
            "attachments": [{
                "color": color,
                "title": f"Budget {alert['category']}: {alert['status']}",
                "text": alert['message'],
                "fields": [
                    {
                        "title": "Utilisé",
                        "value": f"{alert['percentage']:.0f}%",
                        "short": True
                    },
                    {
                        "title": "Montant",
                        "value": f"{alert['spent']:.2f} / {alert['budget_amount']:.2f} EUR",
                        "short": True
                    }
                ]
            }]
        }
        
        requests.post(self.webhook_url, json=payload)

# modules/notifications/integrations/discord.py
"""
Intégration Discord pour notifications.
"""

import requests

class DiscordIntegration:
    """Client Discord pour notifications."""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_notification(self, title: str, message: str, color: int = 0x3B82F6):
        """Envoie une notification Discord."""
        payload = {
            "embeds": [{
                "title": title,
                "description": message,
                "color": color,
                "timestamp": datetime.now().isoformat()
            }]
        }
        
        requests.post(self.webhook_url, json=payload)
```

---

**Version**: 1.1 - **TESTS ET INTÉGRATIONS AJOUTÉS**  
**Intégrations**: Slack, Discord, Webhooks
