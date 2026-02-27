"""Feedback V2 - Système de feedback modernisé avec Design System.

Remplace modules/ui/feedback.py avec une version utilisant :
- Design Tokens (couleurs, typographie, espacements)
- Atomes (Button, Badge)
- Molécules (Card)

Usage:
    from modules.ui.feedback_v2 import Feedback
    
    # Toast notifications
    Feedback.toast.success("Opération réussie !")
    Feedback.toast.error("Une erreur s'est produite")
    
    # Banners
    Feedback.banner.warning("Attention", "Votre budget est dépassé")
    
    # Confirmation dialogs
    if Feedback.confirm("Êtes-vous sûr ?"):
        delete_item()
"""

from enum import Enum
from typing import Callable, Optional, Any
import streamlit as st

from modules.ui.tokens import Colors, Typography, Spacing, BorderRadius, Shadow
from modules.ui.atoms import Button, Badge, Icon
from modules.ui.molecules import Card


class FeedbackType(str, Enum):
    """Types de feedback."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class Toast:
    """Notifications toast (éphémères)."""
    
    _ICONS = {
        FeedbackType.SUCCESS: "✅",
        FeedbackType.ERROR: "❌",
        FeedbackType.WARNING: "⚠️",
        FeedbackType.INFO: "ℹ️",
    }
    
    @classmethod
    def _show(
        cls,
        message: str,
        type_: FeedbackType,
        icon: Optional[str] = None,
    ) -> None:
        """Affiche un toast."""
        emoji = icon or cls._ICONS[type_]
        
        # Mapping vers les fonctions Streamlit natives
        toast_methods = {
            FeedbackType.SUCCESS: st.success,
            FeedbackType.ERROR: st.error,
            FeedbackType.WARNING: st.warning,
            FeedbackType.INFO: st.info,
        }
        
        toast_methods[type_](f"{emoji} {message}", icon=emoji)
    
    @classmethod
    def success(cls, message: str) -> None:
        """Toast succès.
        
        Usage:
            Toast.success("Transaction sauvegardée !")
        """
        cls._show(message, FeedbackType.SUCCESS)
    
    @classmethod
    def error(cls, message: str) -> None:
        """Toast erreur.
        
        Usage:
            Toast.error("Impossible de sauvegarder")
        """
        cls._show(message, FeedbackType.ERROR)
    
    @classmethod
    def warning(cls, message: str) -> None:
        """Toast avertissement.
        
        Usage:
            Toast.warning("Vérifier les données")
        """
        cls._show(message, FeedbackType.WARNING)
    
    @classmethod
    def info(cls, message: str) -> None:
        """Toast info.
        
        Usage:
            Toast.info("Nouvelle fonctionnalité disponible")
        """
        cls._show(message, FeedbackType.INFO)


class Banner:
    """Banners persistants (plus visibles que les toasts)."""
    
    @staticmethod
    def render(
        title: str,
        message: str,
        type_: FeedbackType = FeedbackType.INFO,
        action_text: Optional[str] = None,
        on_action: Optional[Callable] = None,
        dismissible: bool = True,
        key: Optional[str] = None,
    ) -> bool:
        """Rend un banner.
        
        Args:
            title: Titre du banner
            message: Message détaillé
            type_: Type de feedback
            action_text: Texte bouton action (optionnel)
            on_action: Callback action
            dismissible: Si True, peut être fermé
            key: Clé unique
        
        Returns:
            True si l'action a été cliquée
        """
        # Utiliser la Card d'alerte
        Card.alert(
            title=title,
            message=message,
            severity=type_.value,
            action_text=action_text,
            on_action=on_action,
            key=key,
        )
        
        return False  # Simplifié pour l'instant
    
    @classmethod
    def success(
        cls,
        title: str,
        message: str,
        **kwargs
    ) -> bool:
        """Banner succès."""
        return cls.render(title, message, FeedbackType.SUCCESS, **kwargs)
    
    @classmethod
    def error(
        cls,
        title: str,
        message: str,
        **kwargs
    ) -> bool:
        """Banner erreur."""
        return cls.render(title, message, FeedbackType.ERROR, **kwargs)
    
    @classmethod
    def warning(
        cls,
        title: str,
        message: str,
        **kwargs
    ) -> bool:
        """Banner avertissement."""
        return cls.render(title, message, FeedbackType.WARNING, **kwargs)
    
    @classmethod
    def info(
        cls,
        title: str,
        message: str,
        **kwargs
    ) -> bool:
        """Banner info."""
        return cls.render(title, message, FeedbackType.INFO, **kwargs)


class ConfirmDialog:
    """Dialogues de confirmation."""
    
    @staticmethod
    def render(
        message: str,
        title: str = "Confirmation",
        confirm_text: str = "Confirmer",
        cancel_text: str = "Annuler",
        danger: bool = False,
        key: Optional[str] = None,
    ) -> bool:
        """Affiche un dialogue de confirmation.
        
        Args:
            message: Message à afficher
            title: Titre du dialogue
            confirm_text: Texte bouton confirmer
            cancel_text: Texte bouton annuler
            danger: Si True, bouton en rouge
            key: Clé unique
        
        Returns:
            True si confirmé, False sinon
        
        Usage:
            if ConfirmDialog.render("Supprimer cette transaction ?", danger=True):
                delete_transaction()
        """
        dialog_key = key or "confirm_dialog"
        state_key = f"{dialog_key}_open"
        result_key = f"{dialog_key}_result"
        
        # Initialiser l'état
        if state_key not in st.session_state:
            st.session_state[state_key] = False
            st.session_state[result_key] = None
        
        # Si le dialogue n'est pas ouvert, retourner le résultat précédent
        if not st.session_state[state_key]:
            result = st.session_state[result_key]
            st.session_state[result_key] = None
            return result if result else False
        
        # Afficher le dialogue
        with st.container():
            st.markdown(f"### {title}")
            st.markdown(message)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if danger:
                    clicked = Button.danger(
                        confirm_text,
                        key=f"{dialog_key}_confirm"
                    )
                else:
                    clicked = Button.primary(
                        confirm_text,
                        key=f"{dialog_key}_confirm"
                    )
                
                if clicked:
                    st.session_state[state_key] = False
                    st.session_state[result_key] = True
                    st.rerun()
            
            with col2:
                if Button.secondary(cancel_text, key=f"{dialog_key}_cancel"):
                    st.session_state[state_key] = False
                    st.session_state[result_key] = False
                    st.rerun()
        
        return False
    
    @staticmethod
    def danger(
        message: str,
        title: str = "Action destructive",
        **kwargs
    ) -> bool:
        """Dialogue de confirmation danger."""
        return ConfirmDialog.render(message, title, danger=True, **kwargs)


# API unifiée
class Feedback:
    """API unifiée pour tout le système de feedback.
    
    Usage:
        from modules.ui.feedback_v2 import Feedback
        
        # Toasts éphémères
        Feedback.toast.success("Sauvegardé !")
        
        # Banners persistants
        Feedback.banner.warning("Attention", "Message...")
        
        # Confirmations
        if Feedback.confirm("Supprimer ?"):
            delete()
        
        # Confirmations dangereuses
        if Feedback.confirm.danger("Supprimer définitivement ?"):
            delete_permanent()
    """
    toast = Toast()
    banner = Banner()
    
    @staticmethod
    def confirm(
        message: str,
        title: str = "Confirmation",
        **kwargs
    ) -> bool:
        """Dialogue de confirmation simple."""
        return ConfirmDialog.render(message, title, **kwargs)
    
    class confirm_danger:
        """Namespace pour confirmations dangereuses."""
        
        @staticmethod
        def render(
            message: str,
            title: str = "Action destructive",
            **kwargs
        ) -> bool:
            """Dialogue de confirmation danger."""
            return ConfirmDialog.danger(message, title, **kwargs)


# Compatibilité avec l'ancienne API
def toast_success(message: str) -> None:
    """Compatibilité: Toast succès."""
    Toast.success(message)

def toast_error(message: str) -> None:
    """Compatibilité: Toast erreur."""
    Toast.error(message)

def toast_warning(message: str) -> None:
    """Compatibilité: Toast avertissement."""
    Toast.warning(message)

def toast_info(message: str) -> None:
    """Compatibilité: Toast info."""
    Toast.info(message)

def show_success(title: str, message: str, **kwargs) -> bool:
    """Compatibilité: Banner succès."""
    return Banner.success(title, message, **kwargs)

def show_error(title: str, message: str, **kwargs) -> bool:
    """Compatibilité: Banner erreur."""
    return Banner.error(title, message, **kwargs)

def show_warning(title: str, message: str, **kwargs) -> bool:
    """Compatibilité: Banner avertissement."""
    return Banner.warning(title, message, **kwargs)

def show_info(title: str, message: str, **kwargs) -> bool:
    """Compatibilité: Banner info."""
    return Banner.info(title, message, **kwargs)

def confirm_dialog(
    message: str,
    title: str = "Confirmation",
    **kwargs
) -> bool:
    """Compatibilité: Dialogue de confirmation."""
    return ConfirmDialog.render(message, title, **kwargs)
