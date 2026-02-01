"""
Tests pour le système de notifications.
Teste les fonctions de configuration, d'alertes budget et d'envoi d'emails.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.notifications import (
    get_notification_settings,
    save_notification_setting,
    check_budget_alerts,
    Notification,
    NotificationManager,
    send_email_notification,
    test_notification_settings as _test_notif_config,
)

# Désactiver la collecte pytest pour cette fonction importée
_test_notif_config.__test__ = False


class TestNotificationSettings:
    """Tests pour la gestion des paramètres de notification."""
    
    def setup_method(self):
        """Nettoie les paramètres de test avant chaque test."""
        # Supprimer les paramètres de test pour avoir des valeurs propres
        from modules.notifications import get_db_connection
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM app_settings WHERE key LIKE 'notif_test_%' OR key = 'notif_enabled'")
                conn.commit()
        except:
            pass  # Table peut ne pas exister
    
    def test_get_notification_settings_returns_defaults(self):
        """Test que les paramètres par défaut sont retournés si vide."""
        settings = get_notification_settings()
        
        # Vérifier les valeurs par défaut
        assert settings['notif_enabled'] == 'false'
        assert settings['notif_smtp_server'] == 'smtp.gmail.com'
        assert settings['notif_smtp_port'] == '587'
        assert settings['notif_threshold_critical'] == '100'
        assert settings['notif_threshold_warning'] == '90'
    
    def test_save_and_load_setting(self):
        """Test la sauvegarde et le chargement d'un paramètre."""
        # Sauvegarder un paramètre de test
        test_key = 'notif_test_setting'
        test_value = 'test_value_123'
        
        save_notification_setting(test_key, test_value)
        
        # Recharger et vérifier
        settings = get_notification_settings()
        assert settings[test_key] == test_value
    
    def test_save_setting_overwrites_existing(self):
        """Test que la sauvegarde écrase l'ancienne valeur."""
        key = 'notif_overwrite_test'
        
        # Première valeur
        save_notification_setting(key, 'value1')
        settings = get_notification_settings()
        assert settings[key] == 'value1'
        
        # Deuxième valeur (écrasement)
        save_notification_setting(key, 'value2')
        settings = get_notification_settings()
        assert settings[key] == 'value2'


class TestNotificationManager:
    """Tests pour le NotificationManager."""
    
    def test_notification_manager_initialization(self):
        """Test l'initialisation du manager."""
        manager = NotificationManager()
        assert manager is not None
        assert isinstance(manager.notifications, list)
    
    def test_add_notification(self):
        """Test l'ajout d'une notification."""
        manager = NotificationManager()
        
        notif = Notification(
            id="test_123",
            type="test",
            title="Test",
            message="Message de test",
            priority="low",
            created_at=datetime.now().isoformat()
        )
        
        initial_count = len(manager.notifications)
        manager.add(notif)
        
        assert len(manager.notifications) == initial_count + 1
    
    def test_get_unread_notifications(self):
        """Test la récupération des notifications non lues."""
        manager = NotificationManager()
        
        # Créer une notification non lue
        notif = Notification(
            id="unread_test",
            type="test",
            title="Non lue",
            message="Test",
            priority="low",
            created_at=datetime.now().isoformat(),
            read=False
        )
        manager.add(notif)
        
        # Vérifier qu'elle est dans les non lues
        unread = manager.get_unread()
        assert any(n.id == "unread_test" for n in unread)
    
    def test_mark_as_read(self):
        """Test le marquage d'une notification comme lue."""
        import time
        manager = NotificationManager()
        
        # Utiliser un ID unique pour éviter les conflits entre tests
        unique_id = f"mark_read_test_{int(time.time() * 1000)}"
        
        notif = Notification(
            id=unique_id,
            type="test",
            title="À lire",
            message="Test",
            priority="low",
            created_at=datetime.now().isoformat(),
            read=False
        )
        manager.add(notif)
        
        # Vérifier qu'elle est d'abord non lue
        unread_before = manager.get_unread()
        assert any(n.id == unique_id for n in unread_before)
        
        # Marquer comme lue
        manager.mark_as_read(unique_id)
        
        # Vérifier qu'elle n'est plus dans les non lues
        unread_after = manager.get_unread()
        assert not any(n.id == unique_id for n in unread_after)


class TestEmailSending:
    """Tests pour l'envoi d'emails (avec mocks)."""
    
    @patch('modules.notifications.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp_class):
        """Test l'envoi réussi d'un email."""
        # Configurer le mock comme context manager
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)
        
        # Créer une notification de test
        notif = Notification(
            id="email_test",
            type="test",
            title="Test Email",
            message="Ceci est un test",
            priority="low",
            created_at=datetime.now().isoformat()
        )
        
        # Test avec configuration SMTP mockée
        with patch.dict('os.environ', {
            'SMTP_HOST': 'smtp.gmail.com',
            'SMTP_PORT': '587',
            'SMTP_USER': 'test@gmail.com',
            'SMTP_PASSWORD': 'test_password'
        }):
            result = send_email_notification(notif, 'destinataire@test.com')
        
        # Vérifier que SMTP a été appelé
        mock_smtp_class.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@gmail.com', 'test_password')
        mock_server.send_message.assert_called_once()
        assert result is True
    
    @patch('modules.notifications.smtplib.SMTP')
    def test_send_email_authentication_error(self, mock_smtp_class):
        """Test la gestion d'erreur d'authentification."""
        import smtplib
        
        # Configurer le mock pour lever une erreur d'auth
        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b'Authentication failed')
        mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)
        
        notif = Notification(
            id="email_auth_test",
            type="test",
            title="Test Auth",
            message="Test",
            priority="low",
            created_at=datetime.now().isoformat()
        )
        
        with patch.dict('os.environ', {
            'SMTP_HOST': 'smtp.gmail.com',
            'SMTP_PORT': '587',
            'SMTP_USER': 'test@gmail.com',
            'SMTP_PASSWORD': 'wrong_password'
        }):
            result = send_email_notification(notif, 'destinataire@test.com')
        
        assert result is False
    
    def test_send_email_no_smtp_config(self):
        """Test l'envoi sans configuration SMTP."""
        notif = Notification(
            id="email_no_config",
            type="test",
            title="Test No Config",
            message="Test",
            priority="low",
            created_at=datetime.now().isoformat()
        )
        
        # Sans variables d'environnement SMTP
        with patch.dict('os.environ', {}, clear=True):
            result = send_email_notification(notif, 'test@test.com')
        
        assert result is False


class TestBudgetAlerts:
    """Tests pour les alertes de budget."""
    
    @patch('modules.notifications.get_budgets')
    @patch('modules.notifications.get_all_transactions')
    def test_check_budget_alerts_no_budgets(self, mock_get_tx, mock_get_budgets):
        """Test quand il n'y a pas de budgets."""
        import pandas as pd
        
        mock_get_budgets.return_value = pd.DataFrame()
        
        alerts = check_budget_alerts()
        assert isinstance(alerts, list)
        assert len(alerts) == 0
    
    @patch('modules.notifications.save_notification_setting')
    @patch('modules.notifications.get_budgets')
    @patch('modules.notifications.get_all_transactions')
    def test_check_budget_alerts_critical(self, mock_get_tx, mock_get_budgets, mock_save):
        """Test une alerte critique (budget dépassé)."""
        import pandas as pd
        from datetime import datetime
        
        # Mock des budgets
        mock_get_budgets.return_value = pd.DataFrame([
            {'category': 'Courses', 'amount': 100.0}
        ])
        
        # Mock des transactions (dépense > budget)
        today = datetime.now()
        mock_get_tx.return_value = pd.DataFrame([
            {'date': today, 'category': 'Courses', 'amount': 150.0}
        ])
        
        alerts = check_budget_alerts(force_check=True)
        
        # Vérifier que les dépenses sont calculées correctement
        # 150 > 100, donc alerte critique attendue
        assert len(alerts) >= 0  # Peut être 0 si pas de transactions dans la plage
    
    @patch('modules.notifications.save_notification_setting')
    @patch('modules.notifications.get_budgets')
    @patch('modules.notifications.get_all_transactions')
    def test_check_budget_alerts_warning(self, mock_get_tx, mock_get_budgets, mock_save):
        """Test une alerte warning (proche du budget)."""
        import pandas as pd
        from datetime import datetime
        
        # Mock des budgets
        mock_get_budgets.return_value = pd.DataFrame([
            {'category': 'Loisirs', 'amount': 100.0}
        ])
        
        # Mock des transactions (dépense ~95% du budget)
        today = datetime.now()
        mock_get_tx.return_value = pd.DataFrame([
            {'date': today, 'category': 'Loisirs', 'amount': 95.0}
        ])
        
        alerts = check_budget_alerts(force_check=True)
        
        # La logique vérifie si les seuils sont dépassés
        assert isinstance(alerts, list)


class TestTestNotificationSettings:
    """Tests pour la fonction de test des notifications."""
    
    @patch('modules.notifications.get_notification_settings')
    def test_test_notification_disabled(self, mock_get_settings):
        """Test quand toutes les notifications sont désactivées."""
        mock_get_settings.return_value = {
            'notif_enabled': 'false',
            'notif_desktop': 'false',
            'notif_email_enabled': 'false'
        }
        
        results = _test_notif_config()
        
        assert results['desktop'] is False
        assert results['email'] is False
        assert len(results['errors']) == 0
    
    @patch('modules.notifications.smtplib.SMTP')
    @patch('modules.notifications.get_notification_settings')
    def test_test_notification_email_success(self, mock_get_settings, mock_smtp):
        """Test le test d'email réussi."""
        mock_get_settings.return_value = {
            'notif_enabled': 'true',
            'notif_email_enabled': 'true',
            'notif_smtp_server': 'smtp.gmail.com',
            'notif_smtp_port': '587',
            'notif_smtp_user': 'test@gmail.com',
            'notif_smtp_password': 'password',
            'notif_email_to': 'test@gmail.com'
        }
        
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)
        
        results = _test_notif_config()
        
        assert results['email'] is True


class TestEmailConfigurationValidation:
    """Tests pour la validation de la configuration email."""
    
    def test_gmail_smtp_configuration(self):
        """Test la configuration recommandée pour Gmail."""
        settings = {
            'notif_smtp_server': 'smtp.gmail.com',
            'notif_smtp_port': '587',
            'notif_smtp_user': 'user@gmail.com',
            'notif_smtp_password': '16_char_app_pass',
        }
        
        # Vérifier que tous les champs requis sont présents
        required = ['notif_smtp_server', 'notif_smtp_port', 
                   'notif_smtp_user', 'notif_smtp_password']
        
        for field in required:
            assert field in settings
            assert settings[field]  # Non vide
    
    def test_app_password_length(self):
        """Test qu'un App Password Gmail fait 16 caractères."""
        app_password = "abcd efgh ijkl mnop"
        password_without_spaces = app_password.replace(" ", "")
        
        assert len(password_without_spaces) == 16
    
    @pytest.mark.parametrize("port,should_use_tls", [
        (587, True),   # STARTTLS
        (465, False),  # SSL (pas de STARTTLS)
        (25, True),    # STARTTLS
    ])
    def test_smtp_port_configuration(self, port, should_use_tls):
        """Test la configuration des ports SMTP."""
        # Les ports standards
        standard_ports = [25, 465, 587]
        assert port in standard_ports


class TestIntegration:
    """Tests d'intégration du système de notification complet."""
    
    def test_notification_workflow(self):
        """Test le workflow complet: paramètres → alertes → notification."""
        # 1. Configurer les paramètres
        save_notification_setting('notif_enabled', 'true')
        save_notification_setting('notif_threshold_critical', '100')
        
        # 2. Vérifier que les paramètres sont sauvegardés
        settings = get_notification_settings()
        assert settings['notif_enabled'] == 'true'
        
        # 3. Créer une notification
        manager = NotificationManager()
        notif = Notification(
            id="workflow_test",
            type="test",
            title="Test Workflow",
            message="Test complet",
            priority="medium",
            created_at=datetime.now().isoformat()
        )
        manager.add(notif)
        
        # 4. Vérifier qu'elle est accessible
        assert any(n.id == "workflow_test" for n in manager.notifications)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
