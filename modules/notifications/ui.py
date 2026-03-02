"""Composants UI pour les notifications.

Utilise le Design System pour une interface cohérente.
"""

import streamlit as st

from modules.ui.atoms import Badge, Button
from modules.ui.molecules import Card
from modules.ui.tokens import Colors, Spacing, Typography

from .models import Notification, NotificationAction, NotificationLevel
from .service import NotificationService


def render_notification_badge(
    service: NotificationService | None = None,
    key: str = "notif_badge",
) -> None:
    """Rend le badge de notification pour la sidebar.

    Args:
        service: Instance du service (créée si non fournie)
        key: Clé unique pour Streamlit
    """
    if service is None:
        service = NotificationService()

    count = service.count_unread()

    if count == 0:
        return

    # Container avec style
    container_style = f"""
        display: flex;
        align-items: center;
        gap: {Spacing.SM};
        padding: {Spacing.SM} {Spacing.MD};
        background-color: {Colors.SLATE_100};
        border-radius: 8px;
        margin-bottom: {Spacing.MD};
    """

    st.markdown(f'<div style="{container_style}">', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])

    with col1:
        # Icône cloche avec compteur
        bell_icon = "🔔" if count > 0 else "🔕"
        st.markdown(f"<div style='font-size: 1.5rem;'>{bell_icon}</div>", unsafe_allow_html=True)

    with col2:
        # Texte et badge
        st.markdown(
            f"<div style='font-weight: {Typography.WEIGHT_SEMIBOLD};'>Notifications</div>",
            unsafe_allow_html=True,
        )

        if count > 0:
            level = "danger" if count > 5 else "warning" if count > 2 else "info"
            getattr(Badge, level)(f"{count} non lue(s)")

    st.markdown("</div>", unsafe_allow_html=True)

    # Liste rapide des 3 dernières notifications
    if count > 0:
        unread = service.get_unread(limit=3)
        for notif in unread:
            _render_mini_notification(notif, service)

        if count > 3:
            st.caption(f"...et {count - 3} autres")

        # Bouton vers centre complet
        if Button.secondary("Voir tout", key=f"{key}_see_all", use_container_width=True):
            st.switch_page("pages/21_Systeme.py")


def _render_mini_notification(
    notification: Notification,
    service: NotificationService,
) -> None:
    """Rend une notification compacte pour la sidebar."""
    # Couleur selon niveau
    color_map = {
        NotificationLevel.CRITICAL: Colors.DANGER,
        NotificationLevel.WARNING: Colors.WARNING,
        NotificationLevel.INFO: Colors.INFO,
        NotificationLevel.SUCCESS: Colors.SUCCESS,
        NotificationLevel.ACHIEVEMENT: Colors.ACCENT,
    }
    color = color_map.get(notification.level, Colors.SLATE_500)

    # Style compact
    container_style = f"""
        padding: {Spacing.XS} {Spacing.SM};
        border-left: 3px solid {color};
        background-color: {Colors.SLATE_50};
        margin-bottom: {Spacing.XS};
        font-size: {Typography.SIZE_SM};
    """

    st.markdown(f'<div style="{container_style}">', unsafe_allow_html=True)

    # Icône + titre/message
    icon = notification.icon or "📌"
    text = notification.title or notification.message[:50]
    st.markdown(f"<div>{icon} {text}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_notification_center(
    service: NotificationService | None = None,
) -> None:
    """Rend le centre de notifications complet.

    Page complète avec historique, filtres et actions.
    """
    if service is None:
        service = NotificationService()

    st.title("🔔 Centre de notifications")

    # Stats
    unread_count = service.count_unread()
    all_notifications = service.get_all(limit=100, include_dismissed=False)

    # Header avec stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        Card.metric("Non lues", str(unread_count), icon="🔔")
    with col2:
        Card.metric("Total", str(len(all_notifications)), icon="📬")
    with col3:
        critical_count = sum(1 for n in all_notifications if n.level == NotificationLevel.CRITICAL)
        Card.metric("Critiques", str(critical_count), icon="🚨")
    with col4:
        if Button.primary("Tout marquer comme lu" if unread_count > 0 else "Aucune notification"):
            if unread_count > 0:
                service.mark_all_read()
                st.rerun()

    st.divider()

    # Filtres
    col1, col2 = st.columns(2)
    with col1:
        filter_type = st.selectbox(
            "Filtrer par type",
            ["Tous", "Non lus", "Budget", "Validation", "Système", "Gamification"],
            key="notif_filter_type",
        )
    with col2:
        sort_order = st.selectbox(
            "Trier par", ["Plus récent", "Plus ancien", "Priorité"], key="notif_sort"
        )

    # Filtrer les notifications
    filtered = all_notifications
    if filter_type == "Non lus":
        filtered = [n for n in filtered if not n.is_read]
    elif filter_type == "Budget":
        filtered = [n for n in filtered if n.category == "budget"]
    elif filter_type == "Validation":
        filtered = [n for n in filtered if n.category == "validation"]
    elif filter_type == "Système":
        filtered = [n for n in filtered if n.category == "system"]
    elif filter_type == "Gamification":
        filtered = [n for n in filtered if n.category == "gamification"]

    # Trier
    if sort_order == "Plus récent":
        filtered = sorted(filtered, key=lambda x: x.created_at, reverse=True)
    elif sort_order == "Plus ancien":
        filtered = sorted(filtered, key=lambda x: x.created_at)
    elif sort_order == "Priorité":
        priority_map = {
            NotificationLevel.CRITICAL: 0,
            NotificationLevel.WARNING: 1,
            NotificationLevel.INFO: 2,
            NotificationLevel.SUCCESS: 3,
            NotificationLevel.ACHIEVEMENT: 4,
        }
        filtered = sorted(filtered, key=lambda x: priority_map.get(x.level, 5))

    # Afficher les notifications
    if not filtered:
        Card.empty(
            title="Aucune notification",
            message="Vous n'avez pas de notifications dans cette catégorie.",
            icon="📭",
        )
    else:
        for notif in filtered:
            _render_full_notification(notif, service)


def _render_full_notification(
    notification: Notification,
    service: NotificationService,
) -> None:
    """Rend une notification complète avec actions."""
    # Couleur selon niveau
    color_map = {
        NotificationLevel.CRITICAL: (Colors.DANGER, Colors.DANGER_BG),
        NotificationLevel.WARNING: (Colors.WARNING, Colors.WARNING_BG),
        NotificationLevel.INFO: (Colors.INFO, Colors.INFO_BG),
        NotificationLevel.SUCCESS: (Colors.SUCCESS, Colors.SUCCESS_BG),
        NotificationLevel.ACHIEVEMENT: (Colors.ACCENT, Colors.ACCENT_BG),
    }
    border_color, bg_color = color_map.get(notification.level, (Colors.SLATE_400, Colors.SLATE_50))

    # Style
    opacity = "1" if not notification.is_read else "0.7"
    container_style = f"""
        padding: {Spacing.MD};
        border-left: 4px solid {border_color};
        background-color: {bg_color};
        border-radius: {Spacing.SM};
        margin-bottom: {Spacing.SM};
        opacity: {opacity};
    """

    with st.container():
        st.markdown(f'<div style="{container_style}">', unsafe_allow_html=True)

        # Header: Icône + Titre + Date
        header_cols = st.columns([1, 4, 2])

        with header_cols[0]:
            icon = notification.icon or "📌"
            st.markdown(f"<div style='font-size: 1.5rem;'>{icon}</div>", unsafe_allow_html=True)

        with header_cols[1]:
            title = notification.title or notification.type.value.replace("_", " ").title()
            weight = (
                Typography.WEIGHT_BOLD if not notification.is_read else Typography.WEIGHT_NORMAL
            )
            st.markdown(
                f"<div style='font-weight: {weight}; font-size: {Typography.SIZE_LG};'>{title}</div>",
                unsafe_allow_html=True,
            )

        with header_cols[2]:
            date_str = notification.created_at.strftime("%d/%m %H:%M")
            st.caption(date_str)

        # Message
        st.markdown(
            f"<div style='margin: {Spacing.SM} 0; color: {Colors.SLATE_700};'>{notification.message}</div>",
            unsafe_allow_html=True,
        )

        # Actions
        if notification.actions:
            action_cols = st.columns(
                len(notification.actions) + (1 if not notification.is_read else 0)
            )

            for i, action in enumerate(notification.actions):
                with action_cols[i]:
                    if Button.secondary(action.label, key=f"action_{notification.id}_{i}"):
                        _handle_action(notification, action, service)

            # Bouton "Marquer comme lu" si non lu
            if not notification.is_read:
                with action_cols[-1]:
                    if Button.ghost("✓ Lu", key=f"read_{notification.id}"):
                        service.mark_read(notification.id)
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


def _handle_action(
    notification: Notification,
    action: NotificationAction,
    service: NotificationService,
) -> None:
    """Gère l'exécution d'une action sur une notification."""
    if action.action == "navigate" and action.target:
        # Navigation vers une page
        st.switch_page(f"pages/{action.target}.py")

    elif action.action == "dismiss":
        # Ignorer la notification
        service.dismiss(notification.id)
        st.rerun()

    elif action.action == "action" and action.data:
        # Action personnalisée
        action_type = action.data.get("action")

        if action_type == "merge_duplicates":
            # Fusionner les doublons
            date = action.data.get("date")
            label = action.data.get("label")
            amount = action.data.get("amount")
            st.info(f"Fusion des doublons: {label} ({amount}€) le {date}")
            # TODO: Appeler la fonction de fusion
            service.dismiss(notification.id)
            st.rerun()


def render_notification_settings(
    service: NotificationService | None = None,
) -> None:
    """Rend les paramètres de notification."""
    if service is None:
        service = NotificationService()

    st.header("⚙️ Paramètres de notification")

    prefs = service.get_preferences()

    # Niveaux de notification
    st.subheader("Niveaux activés")
    col1, col2, col3 = st.columns(3)

    with col1:
        prefs.critical_enabled = st.toggle("🚨 Critiques", prefs.critical_enabled)
        prefs.warning_enabled = st.toggle("⚠️ Avertissements", prefs.warning_enabled)

    with col2:
        prefs.info_enabled = st.toggle("ℹ️ Informations", prefs.info_enabled)
        prefs.success_enabled = st.toggle("✅ Succès", prefs.success_enabled)

    with col3:
        prefs.achievement_enabled = st.toggle("🏆 Réussites", prefs.achievement_enabled)

    # Seuils de budget
    st.subheader("Seuils d'alerte budget")
    col1, col2 = st.columns(2)

    with col1:
        prefs.budget_warning_threshold = st.slider(
            "Alerte (%)", 50, 100, prefs.budget_warning_threshold
        )

    with col2:
        prefs.budget_critical_threshold = st.slider(
            "Critique (%)", 80, 150, prefs.budget_critical_threshold
        )

    # Résumés
    st.subheader("Récapitulatifs")
    prefs.daily_digest_enabled = st.toggle("Récap quotidien", prefs.daily_digest_enabled)
    prefs.weekly_summary_enabled = st.toggle("Résumé hebdomadaire", prefs.weekly_summary_enabled)

    # Sauvegarder
    if Button.primary("💾 Sauvegarder les préférences", use_container_width=True):
        service.save_preferences(prefs)
        st.success("Préférences sauvegardées !")
