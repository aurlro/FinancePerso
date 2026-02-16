"""
Gestionnaire centralisé des notifications.
Gère la file d'attente, l'historique, et la persistance.
"""

import json
import threading
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .types import (
    Notification,
    NotificationAction,
    NotificationLevel,
    NotificationPreferences,
)


class NotificationManager:
    """
    Gestionnaire singleton des notifications de l'application.

    Responsabilités:
    - Maintenir la file d'attente des notifications actives
    - Gérer l'historique persistant
    - Appliquer les préférences utilisateur
    - Coordonner l'affichage avec les limites visuelles
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._storage_path = Path("Data/notifications_v2.json")
        self._storage_path.parent.mkdir(exist_ok=True)

        # État interne (non persisté)
        self._active_notifications: list[Notification] = []
        self._notification_history: list[Notification] = []
        self._preferences = NotificationPreferences()
        self._subscribers: list[Callable] = []

        # Chargement initial
        self._load_history()
        self._load_preferences()

    # ==================== API Publique ====================

    def notify(
        self,
        message: str,
        level: NotificationLevel = NotificationLevel.INFO,
        title: str | None = None,
        icon: str | None = None,
        duration: float | None = None,
        persistent: bool = False,
        actions: list[NotificationAction] | None = None,
        group: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Notification:
        """
        Crée et affiche une nouvelle notification.

        Args:
            message: Contenu de la notification
            level: Niveau de priorité
            title: Titre optionnel
            icon: Icône personnalisée
            duration: Durée en secondes (None = auto selon le niveau)
            persistent: Si True, reste jusqu'à action utilisateur
            actions: Actions associées
            group: Groupe pour regrouper les notifications similaires
            metadata: Données supplémentaires

        Returns:
            La notification créée
        """
        # Vérifier les préférences
        if not self._preferences.should_show(level):
            return None

        # Appliquer la durée des préférences si non spécifiée
        if duration is None:
            duration = self._preferences.get_duration(level)

        notification = Notification(
            level=level,
            title=title,
            message=message,
            icon=icon,
            duration=duration,
            persistent=persistent,
            actions=actions or [],
            group=group,
            metadata=metadata or {},
            position=self._preferences.position,
        )

        # Gérer le regroupement
        if group and self._preferences.group_similar:
            self._handle_grouping(notification)

        # Ajouter à la file active
        self._active_notifications.append(notification)

        # Limiter le nombre visible
        self._enforce_max_visible()

        # Sauvegarder dans l'historique
        self._notification_history.insert(0, notification)
        self._trim_history()
        self._save_history()

        # Notifier les abonnés
        self._notify_subscribers(notification)

        return notification

    # Méthodes pratiques pour chaque niveau

    def success(
        self, message: str, title: str | None = None, duration: float | None = None, **kwargs
    ) -> Notification:
        """Notification de succès."""
        return self.notify(
            message=message,
            level=NotificationLevel.SUCCESS,
            title=title,
            duration=duration or 3.0,
            **kwargs,
        )

    def error(
        self, message: str, title: str = "Erreur", persistent: bool = True, **kwargs
    ) -> Notification:
        """Notification d'erreur (persistante par défaut)."""
        return self.notify(
            message=message,
            level=NotificationLevel.CRITICAL,
            title=title,
            persistent=persistent,
            **kwargs,
        )

    def warning(
        self,
        message: str,
        title: str | None = "Attention",
        duration: float | None = None,
        **kwargs,
    ) -> Notification:
        """Notification d'avertissement."""
        return self.notify(
            message=message,
            level=NotificationLevel.WARNING,
            title=title,
            duration=duration or 10.0,
            **kwargs,
        )

    def info(
        self, message: str, title: str | None = None, duration: float | None = None, **kwargs
    ) -> Notification:
        """Notification informative."""
        return self.notify(
            message=message,
            level=NotificationLevel.INFO,
            title=title,
            duration=duration or 5.0,
            **kwargs,
        )

    def achievement(
        self, message: str, title: str = "🎉 Félicitations !", **kwargs
    ) -> Notification:
        """Notification de réussite/achievement."""
        return self.notify(
            message=message,
            level=NotificationLevel.ACHIEVEMENT,
            title=title,
            duration=5.0,
            **kwargs,
        )

    def loading(
        self, message: str, title: str | None = "Chargement...", **kwargs
    ) -> Notification:
        """Notification de chargement (à fermer manuellement)."""
        return self.notify(
            message=message,
            level=NotificationLevel.LOADING,
            title=title,
            persistent=True,
            show_progress=True,
            **kwargs,
        )

    # ==================== Gestion de l'état ====================

    def dismiss(self, notification_id: str) -> bool:
        """Ferme une notification spécifique."""
        for notif in self._active_notifications:
            if notif.id == notification_id:
                notif.dismiss()
                self._active_notifications.remove(notif)
                self._save_history()
                return True
        return False

    def dismiss_all(self, level: NotificationLevel | None = None) -> int:
        """
        Ferme toutes les notifications, ou seulement celles d'un niveau donné.

        Returns:
            Nombre de notifications fermées
        """
        count = 0
        to_remove = []

        for notif in self._active_notifications:
            if level is None or notif.level == level:
                notif.dismiss()
                to_remove.append(notif)
                count += 1

        for notif in to_remove:
            self._active_notifications.remove(notif)

        if count > 0:
            self._save_history()

        return count

    def mark_as_read(self, notification_id: str) -> bool:
        """Marque une notification comme lue."""
        for notif in self._notification_history:
            if notif.id == notification_id:
                notif.read = True
                self._save_history()
                return True
        return False

    def mark_all_as_read(self) -> int:
        """Marque toutes les notifications comme lues."""
        count = 0
        for notif in self._notification_history:
            if not notif.read:
                notif.read = True
                count += 1

        if count > 0:
            self._save_history()

        return count

    # ==================== Accesseurs ====================

    @property
    def active_notifications(self) -> list[Notification]:
        """Notifications actuellement affichées."""
        return self._active_notifications.copy()

    @property
    def notification_history(self) -> list[Notification]:
        """Historique complet des notifications."""
        return self._notification_history.copy()

    @property
    def unread_count(self) -> int:
        """Nombre de notifications non lues."""
        return sum(1 for n in self._notification_history if not n.read)

    @property
    def preferences(self) -> NotificationPreferences:
        """Préférences utilisateur."""
        return self._preferences

    def get_active_by_level(self, level: NotificationLevel) -> list[Notification]:
        """Retourne les notifications actives d'un niveau donné."""
        return [n for n in self._active_notifications if n.level == level]

    def get_history_by_level(self, level: NotificationLevel, limit: int = 50) -> list[Notification]:
        """Retourne l'historique filtré par niveau."""
        filtered = [n for n in self._notification_history if n.level == level]
        return filtered[:limit]

    # ==================== Préférences ====================

    def update_preferences(self, **kwargs) -> None:
        """Met à jour les préférences utilisateur."""
        for key, value in kwargs.items():
            if hasattr(self._preferences, key):
                setattr(self._preferences, key, value)
        self._save_preferences()

    def reset_preferences(self) -> None:
        """Réinitialise les préférences aux valeurs par défaut."""
        self._preferences = NotificationPreferences()
        self._save_preferences()

    # ==================== Abonnements ====================

    def subscribe(self, callback: Callable[[Notification], None]) -> None:
        """S'abonne aux nouvelles notifications."""
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[Notification], None]) -> None:
        """Se désabonne des notifications."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    # ==================== Nettoyage ====================

    def clear_history(self, older_than_days: int | None = None) -> int:
        """
        Nettoie l'historique des notifications.

        Args:
            older_than_days: Si spécifié, supprime uniquement les notifications plus anciennes

        Returns:
            Nombre de notifications supprimées
        """
        if older_than_days is None:
            count = len(self._notification_history)
            self._notification_history.clear()
        else:
            cutoff = datetime.now() - timedelta(days=older_than_days)
            to_remove = [n for n in self._notification_history if n.created_at < cutoff]
            count = len(to_remove)
            for n in to_remove:
                self._notification_history.remove(n)

        if count > 0:
            self._save_history()

        return count

    def cleanup_expired(self) -> int:
        """Supprime les notifications expirées de la file active."""
        now = datetime.now()
        to_remove = []

        for notif in self._active_notifications:
            if notif.persistent:
                continue
            if notif.duration and notif.duration > 0:
                age = (now - notif.created_at).total_seconds()
                if age > notif.duration:
                    to_remove.append(notif)

        for notif in to_remove:
            self._active_notifications.remove(notif)

        return len(to_remove)

    # ==================== Méthodes privées ====================

    def _handle_grouping(self, notification: Notification) -> None:
        """Gère le regroupement des notifications similaires."""
        # Chercher une notification existante du même groupe
        for existing in self._active_notifications:
            if existing.group == notification.group:
                # Incrémenter le compteur dans les métadonnées
                count = existing.metadata.get("group_count", 1) + 1
                existing.metadata["group_count"] = count
                existing.message = f"{notification.message} (+{count-1} similaires)"
                return

    def _enforce_max_visible(self) -> None:
        """Garantit qu'on ne dépasse pas le nombre max de notifications visibles."""
        max_visible = self._preferences.max_visible

        while len(self._active_notifications) > max_visible:
            # Retirer la plus ancienne non-persistante
            for notif in self._active_notifications:
                if not notif.persistent:
                    self._active_notifications.remove(notif)
                    break
            else:
                # Toutes sont persistantes, retirer la plus ancienne
                self._active_notifications.pop(0)

    def _notify_subscribers(self, notification: Notification) -> None:
        """Notifie tous les abonnés."""
        for callback in self._subscribers:
            try:
                callback(notification)
            except Exception:
                pass  # Ignorer les erreurs des callbacks

    def _trim_history(self, max_items: int = 100) -> None:
        """Limite la taille de l'historique."""
        if len(self._notification_history) > max_items:
            self._notification_history = self._notification_history[:max_items]

    def _load_history(self) -> None:
        """Charge l'historique depuis le fichier."""
        if not self._storage_path.exists():
            return

        try:
            with open(self._storage_path, encoding="utf-8") as f:
                data = json.load(f)

            self._notification_history = [
                Notification.from_dict(n) for n in data.get("history", [])
            ]
        except Exception:
            # En cas d'erreur, partir d'un historique vide
            self._notification_history = []

    def _save_history(self) -> None:
        """Sauvegarde l'historique dans le fichier."""
        try:
            data = {
                "history": [n.to_dict() for n in self._notification_history[:50]],
                "saved_at": datetime.now().isoformat(),
            }
            with open(self._storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # Ne pas bloquer l'application pour ça

    def _load_preferences(self) -> None:
        """Charge les préférences depuis la base de données."""
        try:
            from modules.db.connection import get_db_connection

            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = 'notification_preferences'")
                row = cursor.fetchone()

                if row:
                    data = json.loads(row[0])
                    for key, value in data.items():
                        if hasattr(self._preferences, key):
                            setattr(self._preferences, key, value)
        except Exception:
            pass  # Utiliser les valeurs par défaut

    def _save_preferences(self) -> None:
        """Sauvegarde les préférences dans la base de données."""
        try:
            from modules.db.connection import get_db_connection

            data = {
                "enabled": self._preferences.enabled,
                "desktop_enabled": self._preferences.desktop_enabled,
                "sound_enabled": self._preferences.sound_enabled,
                "max_visible": self._preferences.max_visible,
                "position": self._preferences.position.value,
                "group_similar": self._preferences.group_similar,
                "show_critical": self._preferences.show_critical,
                "show_warning": self._preferences.show_warning,
                "show_success": self._preferences.show_success,
                "show_info": self._preferences.show_info,
                "show_achievement": self._preferences.show_achievement,
                "custom_durations": self._preferences.custom_durations,
            }

            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO settings (key, value, updated_at)
                       VALUES ('notification_preferences', ?, CURRENT_TIMESTAMP)
                       ON CONFLICT(key) DO UPDATE SET
                       value = excluded.value,
                       updated_at = CURRENT_TIMESTAMP""",
                    (json.dumps(data),),
                )
                conn.commit()
        except Exception:
            pass


# Instance globale
_manager = None


def get_notification_manager() -> NotificationManager:
    """Retourne l'instance singleton du gestionnaire."""
    global _manager
    if _manager is None:
        _manager = NotificationManager()
    return _manager


# Fonctions pratiques au niveau module
def notify(
    message: str, level: NotificationLevel = NotificationLevel.INFO, **kwargs
) -> Notification:
    """Crée une notification."""
    return get_notification_manager().notify(message, level, **kwargs)


def success(message: str, **kwargs) -> Notification:
    """Notification de succès."""
    return get_notification_manager().success(message, **kwargs)


def error(message: str, **kwargs) -> Notification:
    """Notification d'erreur."""
    return get_notification_manager().error(message, **kwargs)


def warning(message: str, **kwargs) -> Notification:
    """Notification d'avertissement."""
    return get_notification_manager().warning(message, **kwargs)


def info(message: str, **kwargs) -> Notification:
    """Notification informative."""
    return get_notification_manager().info(message, **kwargs)


def achievement(message: str, **kwargs) -> Notification:
    """Notification d'achievement."""
    return get_notification_manager().achievement(message, **kwargs)


def loading(message: str, **kwargs) -> Notification:
    """Notification de chargement."""
    return get_notification_manager().loading(message, **kwargs)
