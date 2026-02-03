"""
Composants visuels pour afficher les notifications dans Streamlit.
Design moderne avec animations, barres de progression, et actions.
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import List, Optional, Callable

from .types import (
    Notification, NotificationLevel, NotificationAction,
    LEVEL_COLORS, LEVEL_BG_COLORS, DEFAULT_ICONS
)
from .manager import get_notification_manager


# ==================== Composants Toast ====================

def render_toast_container():
    """
    Rend le conteneur de toasts fixe en haut à droite.
    À appeler une fois par page, idéalement dans la sidebar ou en début de page.
    """
    # CSS pour le conteneur de toasts
    st.markdown("""
        <style>
        /* Conteneur de toasts */
        .fp-toast-container {
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 999999;
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-width: 400px;
            pointer-events: none;
        }
        
        /* Toast individuel */
        .fp-toast {
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            padding: 16px;
            pointer-events: all;
            animation: fp-toast-in 0.3s ease-out;
            border-left: 4px solid;
            position: relative;
            overflow: hidden;
        }
        
        @keyframes fp-toast-in {
            from {
                opacity: 0;
                transform: translateX(100%);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes fp-toast-out {
            from {
                opacity: 1;
                transform: translateX(0);
            }
            to {
                opacity: 0;
                transform: translateX(100%);
            }
        }
        
        .fp-toast.exiting {
            animation: fp-toast-out 0.3s ease-in forwards;
        }
        
        /* Barre de progression */
        .fp-toast-progress {
            position: absolute;
            bottom: 0;
            left: 0;
            height: 3px;
            background: currentColor;
            opacity: 0.3;
            transition: width 0.1s linear;
        }
        
        /* Header du toast */
        .fp-toast-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 6px;
        }
        
        .fp-toast-icon {
            font-size: 20px;
            flex-shrink: 0;
        }
        
        .fp-toast-title {
            font-weight: 600;
            font-size: 14px;
            color: #1f2937;
            margin: 0;
        }
        
        .fp-toast-close {
            position: absolute;
            top: 8px;
            right: 8px;
            background: none;
            border: none;
            cursor: pointer;
            opacity: 0.4;
            transition: opacity 0.2s;
            font-size: 16px;
            padding: 4px;
            line-height: 1;
        }
        
        .fp-toast-close:hover {
            opacity: 0.8;
        }
        
        /* Message */
        .fp-toast-message {
            font-size: 13px;
            color: #4b5563;
            line-height: 1.5;
            margin-left: 30px;
        }
        
        /* Actions */
        .fp-toast-actions {
            display: flex;
            gap: 8px;
            margin-top: 12px;
            margin-left: 30px;
        }
        
        .fp-toast-action {
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            border: none;
            transition: all 0.2s;
        }
        
        .fp-toast-action.primary {
            background: #3b82f6;
            color: white;
        }
        
        .fp-toast-action.primary:hover {
            background: #2563eb;
        }
        
        .fp-toast-action.secondary {
            background: #f3f4f6;
            color: #374151;
        }
        
        .fp-toast-action.secondary:hover {
            background: #e5e7eb;
        }
        
        /* Responsive */
        @media (max-width: 640px) {
            .fp-toast-container {
                left: 10px;
                right: 10px;
                max-width: none;
            }
            
            .fp-toast {
                width: 100%;
            }
        }
        </style>
    """, unsafe_allow_html=True)


def render_notification_toast(notification: Notification, on_dismiss: Optional[Callable] = None):
    """
    Rend une notification au format toast.
    
    Args:
        notification: La notification à afficher
        on_dismiss: Callback appelé lors de la fermeture
    """
    color = LEVEL_COLORS.get(notification.level, "#3b82f6")
    bg_color = LEVEL_BG_COLORS.get(notification.level, "#eff6ff")
    icon = notification.icon or DEFAULT_ICONS.get(notification.level, "ℹ️")
    
    # Calculer le temps restant
    progress = 100
    if notification.duration and notification.duration > 0:
        elapsed = notification.age_seconds
        remaining = max(0, notification.duration - elapsed)
        progress = (remaining / notification.duration) * 100
    
    # HTML du toast
    html = f"""
    <div class="fp-toast" id="toast-{notification.id}" style="
        border-left-color: {color};
        background: linear-gradient(to right, {bg_color} 0%, white 100%);
    ">
        <button class="fp-toast-close" onclick="dismissToast('{notification.id}')">×</button>
        
        <div class="fp-toast-header">
            <span class="fp-toast-icon">{icon}</span>
            <span class="fp-toast-title" style="color: {color};">
                {notification.title or notification.level.value.title()}
            </span>
        </div>
        
        <div class="fp-toast-message">{notification.message}</div>
    """
    
    # Ajouter les actions
    if notification.actions:
        html += '<div class="fp-toast-actions">'
        for action in notification.actions:
            btn_class = "primary" if action.primary else "secondary"
            icon_html = f"{action.icon} " if action.icon else ""
            html += f'''
                <button class="fp-toast-action {btn_class}" 
                        onclick="handleAction('{notification.id}', '{action.label}')">
                    {icon_html}{action.label}
                </button>
            '''
        html += '</div>'
    
    # Ajouter la barre de progression
    if notification.show_progress and notification.duration and notification.duration > 0:
        html += f'''
            <div class="fp-toast-progress" style="
                width: {progress}%;
                color: {color};
            "></div>
        '''
    
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)


def render_all_active_toasts():
    """Affiche toutes les notifications actives sous forme de toasts."""
    manager = get_notification_manager()
    notifications = manager.active_notifications
    
    if not notifications:
        return
    
    # Rendre le conteneur une seule fois
    render_toast_container()
    
    # Rendre chaque notification
    for notif in notifications:
        render_notification_toast(notif, on_dismiss=lambda nid=notif.id: manager.dismiss(nid))


# ==================== Composants Inline ====================

def render_inline_notification(
    message: str,
    level: NotificationLevel = NotificationLevel.INFO,
    title: Optional[str] = None,
    icon: Optional[str] = None,
    actions: Optional[List[NotificationAction]] = None,
    dismissible: bool = False,
    key: Optional[str] = None
) -> bool:
    """
    Affiche une notification inline dans le flux de la page.
    
    Args:
        message: Contenu du message
        level: Niveau de notification
        title: Titre optionnel
        icon: Icône personnalisée
        actions: Actions associées
        dismissible: Si True, affiche un bouton pour fermer
        key: Clé unique pour le composant
    
    Returns:
        True si fermé par l'utilisateur
    """
    color = LEVEL_COLORS.get(level, "#3b82f6")
    bg_color = LEVEL_BG_COLORS.get(level, "#eff6ff")
    icon = icon or DEFAULT_ICONS.get(level, "ℹ️")
    
    component_key = key or f"inline_notif_{hash(message)}"
    
    # Initialiser l'état de fermeture
    if f"{component_key}_dismissed" not in st.session_state:
        st.session_state[f"{component_key}_dismissed"] = False
    
    if st.session_state[f"{component_key}_dismissed"]:
        return True
    
    with st.container():
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {bg_color} 0%, white 100%);
                border: 1px solid {color}30;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
            ">
                <div style="display: flex; align-items: flex-start; gap: 12px;">
                    <span style="font-size: 20px; flex-shrink: 0;">{icon}</span>
                    <div style="flex: 1;">
                        {f'<div style="font-weight: 600; color: {color}; margin-bottom: 4px;">{title}</div>' if title else ''}
                        <div style="color: #374151; line-height: 1.5;">{message}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Actions
        if actions or dismissible:
            cols = st.columns([1] * (len(actions or [])) + ([1] if dismissible else []))
            
            for i, action in enumerate(actions or []):
                with cols[i]:
                    btn_type = "primary" if action.primary else "secondary"
                    if st.button(
                        f"{action.icon or ''} {action.label}".strip(),
                        key=f"{component_key}_action_{i}",
                        type=btn_type,
                        use_container_width=True
                    ):
                        if action.callback:
                            action.callback()
                        if action.url:
                            st.switch_page(action.url)
            
            if dismissible:
                with cols[-1]:
                    if st.button("✕ Fermer", key=f"{component_key}_dismiss", type="secondary"):
                        st.session_state[f"{component_key}_dismissed"] = True
                        st.rerun()
    
    return False


# ==================== Composants Spéciaux ====================

def render_achievement_unlock(
    title: str,
    description: str,
    icon: str = "🏆",
    reward: Optional[str] = None
):
    """
    Affiche une célébration pour un achievement débloqué.
    
    Args:
        title: Nom de l'achievement
        description: Description de ce qui a été accompli
        icon: Icône de l'achievement
        reward: Récompense éventuelle (badge, points, etc.)
    """
    # Animation de célébration
    st.balloons()
    
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 50%, #fbbf24 100%);
            border-radius: 16px;
            padding: 32px;
            text-align: center;
            margin: 20px 0;
            box-shadow: 0 10px 40px rgba(251, 191, 36, 0.3);
            animation: achievement-pulse 2s ease-in-out infinite;
        ">
            <div style="font-size: 64px; margin-bottom: 16px;">{icon}</div>
            <div style="
                font-size: 14px;
                font-weight: 600;
                color: #92400e;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 8px;
            ">Achievement Débloqué !</div>
            <div style="
                font-size: 24px;
                font-weight: 700;
                color: #78350f;
                margin-bottom: 8px;
            ">{title}</div>
            <div style="color: #92400e; font-size: 16px;">{description}</div>
            {f'<div style="margin-top: 16px; padding: 8px 16px; background: rgba(255,255,255,0.5); border-radius: 20px; display: inline-block; color: #92400e; font-weight: 600;">🎁 {reward}</div>' if reward else ''}
        </div>
        
        <style>
        @keyframes achievement-pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.02); }}
        }}
        </style>
    """, unsafe_allow_html=True)


def render_loading_state(
    message: str = "Chargement en cours...",
    submessage: Optional[str] = None,
    progress: Optional[float] = None
):
    """
    Affiche un état de chargement amélioré.
    
    Args:
        message: Message principal
        submessage: Message secondaire détaillé
        progress: Progression entre 0 et 1 (None = indéterminé)
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
            <div style="
                text-align: center;
                padding: 40px 20px;
                background: #f9fafb;
                border-radius: 12px;
                margin: 20px 0;
            ">
                <div style="
                    font-size: 48px;
                    margin-bottom: 16px;
                    animation: loading-bounce 1.5s ease-in-out infinite;
                ">🔄</div>
                <div style="
                    font-size: 18px;
                    font-weight: 600;
                    color: #374151;
                    margin-bottom: 8px;
                ">{message}</div>
                {f'<div style="color: #6b7280; font-size: 14px;">{submessage}</div>' if submessage else ''}
            </div>
            
            <style>
            @keyframes loading-bounce {{
                0%, 100% {{ transform: translateY(0) rotate(0deg); }}
                50% {{ transform: translateY(-10px) rotate(180deg); }}
            }}
            </style>
        """, unsafe_allow_html=True)
        
        if progress is not None:
            st.progress(progress, text=f"{progress*100:.0f}%")
        else:
            st.progress(0, text="Patientez...")


def render_empty_state(
    icon: str,
    title: str,
    description: str,
    action_label: Optional[str] = None,
    action_callback: Optional[Callable] = None
):
    """
    Affiche un état vide engageant.
    
    Args:
        icon: Emoji représentatif
        title: Titre de l'état vide
        description: Explication
        action_label: Label du bouton d'action
        action_callback: Fonction appelée au clic
    """
    st.markdown(f"""
        <div style="
            text-align: center;
            padding: 60px 20px;
            background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
            border-radius: 16px;
            border: 2px dashed #d1d5db;
            margin: 20px 0;
        ">
            <div style="font-size: 64px; margin-bottom: 20px; opacity: 0.7;">{icon}</div>
            <div style="
                font-size: 20px;
                font-weight: 600;
                color: #374151;
                margin-bottom: 8px;
            ">{title}</div>
            <div style="color: #6b7280; max-width: 400px; margin: 0 auto;">
                {description}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if action_label and action_callback:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(f"✨ {action_label}", use_container_width=True, type="primary"):
                action_callback()


# ==================== Helpers ====================

def show_confirmation(
    title: str,
    message: str,
    on_confirm: Callable,
    on_cancel: Optional[Callable] = None,
    confirm_label: str = "Confirmer",
    cancel_label: str = "Annuler",
    danger: bool = False,
    key: str = "confirm"
) -> bool:
    """
    Affiche une boîte de confirmation.
    
    Returns:
        True si l'utilisateur a fait un choix
    """
    state_key = f"{key}_shown"
    result_key = f"{key}_result"
    
    if state_key not in st.session_state:
        st.session_state[state_key] = True
        st.session_state[result_key] = None
    
    if not st.session_state[state_key]:
        return True
    
    color = "#dc2626" if danger else "#f59e0b"
    icon = "⚠️" if danger else "🤔"
    
    with st.container():
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #fef2f2 0%, white 100%) if {danger} else linear-gradient(135deg, #fffbeb 0%, white 100%);
                border: 1px solid {color}40;
                border-left: 4px solid {color};
                border-radius: 12px;
                padding: 20px;
                margin: 16px 0;
            ">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <span style="font-size: 24px;">{icon}</span>
                    <span style="font-size: 18px; font-weight: 600; color: {color};">{title}</span>
                </div>
                <div style="color: #4b5563; margin-left: 36px;">{message}</div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 3])
        
        with col1:
            btn_type = "primary" if not danger else "secondary"
            if st.button(cancel_label, key=f"{key}_cancel", type=btn_type, use_container_width=True):
                st.session_state[state_key] = False
                st.session_state[result_key] = False
                if on_cancel:
                    on_cancel()
                st.rerun()
        
        with col2:
            btn_type = "primary" if danger else "secondary"
            if st.button(confirm_label, key=f"{key}_confirm", type=btn_type, use_container_width=True):
                st.session_state[state_key] = False
                st.session_state[result_key] = True
                on_confirm()
                st.rerun()
    
    return False


# ==================== Intégration Streamlit Native ====================

def show_native_toast(notification: Notification):
    """
    Affiche une notification via le système natif de Streamlit (st.toast).
    Fallback quand les composants customs ne sont pas disponibles.
    """
    icon = notification.icon or DEFAULT_ICONS.get(notification.level, "ℹ️")
    message = f"{icon} {notification.message}"
    
    if notification.level == NotificationLevel.SUCCESS:
        st.toast(message, icon="✅")
    elif notification.level == NotificationLevel.CRITICAL:
        st.error(message)
    elif notification.level == NotificationLevel.WARNING:
        st.warning(message)
    elif notification.level == NotificationLevel.ACHIEVEMENT:
        st.toast(message, icon="🏆")
    else:
        st.toast(message, icon="ℹ️")


def render_notifications_auto():
    """
    Fonction principale à appeler dans chaque page.
    Affiche automatiquement toutes les notifications actives.
    """
    manager = get_notification_manager()
    
    # Nettoyer les notifications expirées
    manager.cleanup_expired()
    
    # Afficher les notifications
    notifications = manager.active_notifications
    
    for notif in notifications:
        # Utiliser le système natif pour l'instant (plus stable)
        show_native_toast(notif)
