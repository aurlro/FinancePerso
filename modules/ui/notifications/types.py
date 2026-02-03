"""
Types et classes de données pour le système de notifications.
Définit les différents types de notifications et leurs propriétés.
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, Callable, List, Dict, Any
from datetime import datetime
import uuid


class NotificationLevel(Enum):
    """Niveaux de priorité des notifications."""
    CRITICAL = "critical"      # Erreurs bloquantes, perte de données - persistant
    WARNING = "warning"        # Alertes importantes - 10s
    SUCCESS = "success"        # Confirmations - 3s
    INFO = "info"              # Informations contextuelles - 5s
    ACHIEVEMENT = "achievement"  # Gamification, milestones - 5s
    LOADING = "loading"        # Opérations en cours - jusqu'à completion


class NotificationPosition(Enum):
    """Positions possibles pour les notifications toast."""
    TOP_RIGHT = "top-right"
    TOP_LEFT = "top-left"
    TOP_CENTER = "top-center"
    BOTTOM_RIGHT = "bottom-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_CENTER = "bottom-center"


class NotificationSound(Enum):
    """Sons disponibles pour les notifications (si activés)."""
    NONE = None
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    ACHIEVEMENT = "achievement"
    MESSAGE = "message"


@dataclass
class NotificationAction:
    """Action associée à une notification."""
    label: str
    callback: Optional[Callable] = None
    url: Optional[str] = None  # Redirection vers une page
    primary: bool = False      # Style bouton primaire
    icon: Optional[str] = None


@dataclass
class Notification:
    """
    Représentation complète d'une notification.
    
    Attributes:
        id: Identifiant unique
        level: Niveau de priorité
        title: Titre court (optionnel)
        message: Contenu de la notification
        icon: Emoji/icône personnalisé
        duration: Durée d'affichage en secondes (None = persistant)
        persistent: Si True, reste jusqu'à action utilisateur
        actions: Actions possibles sur la notification
        metadata: Données supplémentaires
        created_at: Date de création
        read: Si la notification a été lue
        dismissed_at: Date de fermeture
        position: Position d'affichage
        sound: Son associé
        show_progress: Afficher une barre de progression
        group: Groupe pour les notifications liées
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    level: NotificationLevel = NotificationLevel.INFO
    title: Optional[str] = None
    message: str = ""
    icon: Optional[str] = None
    duration: Optional[float] = None
    persistent: bool = False
    actions: List[NotificationAction] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    read: bool = False
    dismissed_at: Optional[datetime] = None
    position: NotificationPosition = NotificationPosition.TOP_RIGHT
    sound: NotificationSound = NotificationSound.NONE
    show_progress: bool = True
    group: Optional[str] = None
    
    def __post_init__(self):
        """Définit les valeurs par défaut selon le niveau."""
        if self.duration is None and not self.persistent:
            self.duration = DEFAULT_DURATIONS.get(self.level, 5.0)
        
        if self.icon is None:
            self.icon = DEFAULT_ICONS.get(self.level, "ℹ️")
    
    @property
    def is_dismissed(self) -> bool:
        """Vérifie si la notification a été fermée."""
        return self.dismissed_at is not None
    
    @property
    def age_seconds(self) -> float:
        """Temps écoulé depuis la création."""
        return (datetime.now() - self.created_at).total_seconds()
    
    def dismiss(self):
        """Marque la notification comme fermée."""
        self.dismissed_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour sérialisation."""
        return {
            'id': self.id,
            'level': self.level.value,
            'title': self.title,
            'message': self.message,
            'icon': self.icon,
            'duration': self.duration,
            'persistent': self.persistent,
            'created_at': self.created_at.isoformat(),
            'read': self.read,
            'dismissed_at': self.dismissed_at.isoformat() if self.dismissed_at else None,
            'group': self.group,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Notification':
        """Crée une notification depuis un dictionnaire."""
        data = data.copy()
        data['level'] = NotificationLevel(data['level'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('dismissed_at'):
            data['dismissed_at'] = datetime.fromisoformat(data['dismissed_at'])
        return cls(**data)


# Configuration par défaut selon le niveau
DEFAULT_DURATIONS: Dict[NotificationLevel, float] = {
    NotificationLevel.CRITICAL: 0,      # Persistant
    NotificationLevel.WARNING: 10.0,
    NotificationLevel.SUCCESS: 3.0,
    NotificationLevel.INFO: 5.0,
    NotificationLevel.ACHIEVEMENT: 5.0,
    NotificationLevel.LOADING: 0,       # Jusqu'à completion
}

DEFAULT_ICONS: Dict[NotificationLevel, str] = {
    NotificationLevel.CRITICAL: "🚨",
    NotificationLevel.WARNING: "⚠️",
    NotificationLevel.SUCCESS: "✅",
    NotificationLevel.INFO: "ℹ️",
    NotificationLevel.ACHIEVEMENT: "🏆",
    NotificationLevel.LOADING: "🔄",
}

LEVEL_COLORS: Dict[NotificationLevel, str] = {
    NotificationLevel.CRITICAL: "#dc2626",  # Red 600
    NotificationLevel.WARNING: "#f59e0b",   # Amber 500
    NotificationLevel.SUCCESS: "#16a34a",   # Green 600
    NotificationLevel.INFO: "#3b82f6",      # Blue 500
    NotificationLevel.ACHIEVEMENT: "#fbbf24", # Amber 400
    NotificationLevel.LOADING: "#6b7280",   # Gray 500
}

LEVEL_BG_COLORS: Dict[NotificationLevel, str] = {
    NotificationLevel.CRITICAL: "#fef2f2",  # Red 50
    NotificationLevel.WARNING: "#fffbeb",   # Amber 50
    NotificationLevel.SUCCESS: "#f0fdf4",   # Green 50
    NotificationLevel.INFO: "#eff6ff",      # Blue 50
    NotificationLevel.ACHIEVEMENT: "#fffbeb", # Amber 50
    NotificationLevel.LOADING: "#f9fafb",   # Gray 50
}


@dataclass
class NotificationPreferences:
    """Préférences utilisateur pour les notifications."""
    enabled: bool = True
    desktop_enabled: bool = False
    sound_enabled: bool = False
    max_visible: int = 3
    position: NotificationPosition = NotificationPosition.TOP_RIGHT
    group_similar: bool = True
    
    # Préférences par niveau
    show_critical: bool = True
    show_warning: bool = True
    show_success: bool = True
    show_info: bool = True
    show_achievement: bool = True
    
    # Durées personnalisées (None = utiliser les défauts)
    custom_durations: Dict[str, float] = field(default_factory=dict)
    
    def should_show(self, level: NotificationLevel) -> bool:
        """Vérifie si un niveau de notification doit être affiché."""
        if not self.enabled:
            return False
        
        mapping = {
            NotificationLevel.CRITICAL: self.show_critical,
            NotificationLevel.WARNING: self.show_warning,
            NotificationLevel.SUCCESS: self.show_success,
            NotificationLevel.INFO: self.show_info,
            NotificationLevel.ACHIEVEMENT: self.show_achievement,
            NotificationLevel.LOADING: True,  # Toujours afficher les loading
        }
        return mapping.get(level, True)
    
    def get_duration(self, level: NotificationLevel) -> float:
        """Retourne la durée pour un niveau donné."""
        custom = self.custom_durations.get(level.value)
        if custom is not None:
            return custom
        return DEFAULT_DURATIONS.get(level, 5.0)
