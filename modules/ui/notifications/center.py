"""
Notification Center - Interface utilisateur complète.
Historique, gestion et préférences des notifications.
"""

import streamlit as st
from typing import Optional, List
from datetime import datetime

from .types import NotificationLevel, LEVEL_COLORS, DEFAULT_ICONS
from .manager import get_notification_manager
from .components import render_inline_notification


def render_notification_center_compact():
    """
    Affiche le badge de notification compact pour la sidebar.
    À placer en haut de la sidebar.
    """
    manager = get_notification_manager()
    count = manager.unread_count
    
    # CSS pour le badge
    st.markdown("""
        <style>
        .fp-notif-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            color: #92400e;
            cursor: pointer;
            transition: all 0.2s;
            border: 1px solid #fbbf24;
        }
        .fp-notif-badge:hover {
            transform: scale(1.05);
            box-shadow: 0 2px 8px rgba(251, 191, 36, 0.4);
        }
        .fp-notif-badge.empty {
            background: #f3f4f6;
            color: #9ca3af;
            border-color: #e5e7eb;
        }
        .fp-notif-count {
            background: #dc2626;
            color: white;
            border-radius: 10px;
            padding: 2px 6px;
            font-size: 11px;
            font-weight: 700;
            min-width: 18px;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if count > 0:
        badge_html = f"""
            <div class="fp-notif-badge" onclick="window.location.href='?page=notifications'">
                🔔 Notifications
                <span class="fp-notif-count">{count}</span>
            </div>
        """
    else:
        badge_html = """
            <div class="fp-notif-badge empty">
                🔔 Notifications
            </div>
        """
    
    st.markdown(badge_html, unsafe_allow_html=True)


def render_notification_center_full():
    """
    Affiche le centre de notifications complet.
    Historique, filtres et actions.
    """
    manager = get_notification_manager()
    
    st.title("🔔 Centre de Notifications")
    
    # En-tête avec stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        with st.container(border=True):
            st.metric(
                label="Non lues",
                value=manager.unread_count,
                delta=None
            )
    
    with col2:
        with st.container(border=True):
            total = len(manager.notification_history)
            st.metric(
                label="Total",
                value=total,
                delta=None
            )
    
    with col3:
        with st.container(border=True):
            critical_count = len([
                n for n in manager.notification_history 
                if n.level == NotificationLevel.CRITICAL and not n.read
            ])
            st.metric(
                label="Alertes",
                value=critical_count,
                delta="critiques" if critical_count > 0 else None,
                delta_color="inverse"
            )
    
    with col4:
        with st.container(border=True):
            if st.button("🔄 Actualiser", use_container_width=True, key="notif_refresh"):
                st.rerun()
    
    st.divider()
    
    # Barre d'actions
    col_actions1, col_actions2, col_actions3 = st.columns([1, 1, 3])
    
    with col_actions1:
        if st.button("✓ Tout marquer comme lu", use_container_width=True, type="secondary", key="notif_mark_all_read"):
            count = manager.mark_all_as_read()
            if count > 0:
                st.success(f"✅ {count} notification(s) marquée(s) comme lue(s)")
                st.rerun()
    
    with col_actions2:
        if st.button("🗑️ Vider l'historique", use_container_width=True, type="secondary", key="notif_clear_history"):
            if len(manager.notification_history) > 0:
                st.session_state['show_clear_confirm'] = True
    
    # Confirmation de suppression
    if st.session_state.get('show_clear_confirm'):
        with st.container(border=True):
            st.warning("⚠️ Êtes-vous sûr de vouloir supprimer tout l'historique ?")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("Oui, supprimer", type="primary", key="notif_confirm_clear"):
                    deleted = manager.clear_history()
                    st.session_state['show_clear_confirm'] = False
                    st.success(f"🗑️ {deleted} notification(s) supprimée(s)")
                    st.rerun()
            with col_no:
                if st.button("Annuler", key="notif_cancel_clear"):
                    st.session_state['show_clear_confirm'] = False
                    st.rerun()
    
    st.divider()
    
    # Filtres
    with st.expander("🔍 Filtres", expanded=False):
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            filter_level = st.multiselect(
                "Type",
                options=[l.value for l in NotificationLevel],
                default=[],
                format_func=lambda x: f"{DEFAULT_ICONS[NotificationLevel(x)]} {x.title()}"
            )
        
        with col_f2:
            filter_read = st.selectbox(
                "Statut",
                options=["Tous", "Non lus", "Lus"],
                index=0
            )
        
        with col_f3:
            filter_period = st.selectbox(
                "Période",
                options=["Tout", "Aujourd'hui", "7 derniers jours", "30 derniers jours"],
                index=0
            )
    
    # Liste des notifications
    notifications = manager.notification_history
    
    # Appliquer les filtres
    if filter_level:
        level_enums = [NotificationLevel(l) for l in filter_level]
        notifications = [n for n in notifications if n.level in level_enums]
    
    if filter_read == "Non lus":
        notifications = [n for n in notifications if not n.read]
    elif filter_read == "Lus":
        notifications = [n for n in notifications if n.read]
    
    if filter_period != "Tout":
        now = datetime.now()
        if filter_period == "Aujourd'hui":
            cutoff = now.replace(hour=0, minute=0, second=0)
        elif filter_period == "7 derniers jours":
            cutoff = now - __import__('datetime').timedelta(days=7)
        else:  # 30 derniers jours
            cutoff = now - __import__('datetime').timedelta(days=30)
        notifications = [n for n in notifications if n.created_at >= cutoff]
    
    # Affichage
    if not notifications:
        render_empty_state()
    else:
        st.markdown(f"**{len(notifications)} notification(s)**")
        
        for notif in notifications:
            render_notification_card(notif, manager)


def render_notification_card(notif, manager):
    """Affiche une carte de notification individuelle."""
    color = LEVEL_COLORS.get(notif.level, "#3b82f6")
    icon = notif.icon or DEFAULT_ICONS.get(notif.level, "ℹ️")
    
    # Formater la date
    now = datetime.now()
    age = now - notif.created_at
    if age.days == 0:
        if age.seconds < 60:
            time_str = "À l'instant"
        elif age.seconds < 3600:
            time_str = f"Il y a {age.seconds // 60} min"
        else:
            time_str = f"Il y a {age.seconds // 3600}h"
    elif age.days == 1:
        time_str = "Hier"
    else:
        time_str = f"Il y a {age.days} jours"
    
    # Bordure pour les non-lues
    border_style = f"border-left: 4px solid {color};" if not notif.read else ""
    bg_style = "background: linear-gradient(90deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%);" if not notif.read else ""
    
    with st.container(border=True):
        cols = st.columns([0.1, 0.7, 0.2])
        
        with cols[0]:
            st.markdown(f"<div style='font-size: 24px;'>{icon}</div>", unsafe_allow_html=True)
        
        with cols[1]:
            title = notif.title or notif.level.value.title()
            st.markdown(f"""
                <div style="{border_style} {bg_style} padding-left: 8px; border-radius: 4px;">
                    <div style="font-weight: 600; color: {color}; font-size: 14px;">
                        {title}
                    </div>
                    <div style="color: #374151; font-size: 13px; margin-top: 4px;">
                        {notif.message}
                    </div>
                    <div style="color: #9ca3af; font-size: 11px; margin-top: 8px;">
                        {time_str}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with cols[2]:
            if not notif.read:
                if st.button("✓ Lu", key=f"mark_read_{notif.id}", use_container_width=True):
                    manager.mark_as_read(notif.id)
                    st.rerun()
            
            if st.button("🗑️", key=f"delete_{notif.id}", use_container_width=True):
                manager.dismiss(notif.id)
                st.rerun()


def render_empty_state():
    """Affiche l'état vide du centre de notifications."""
    st.markdown("""
        <div style="
            text-align: center;
            padding: 60px 20px;
            background: #f9fafb;
            border-radius: 12px;
            margin-top: 20px;
        ">
            <div style="font-size: 48px; margin-bottom: 16px;">📭</div>
            <div style="font-size: 18px; font-weight: 600; color: #374151; margin-bottom: 8px;">
                Aucune notification
            </div>
            <div style="color: #6b7280;">
                Vos notifications apparaîtront ici
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_notification_settings():
    """
    Affiche les paramètres de notification.
    Permet à l'utilisateur de personnaliser son expérience.
    """
    manager = get_notification_manager()
    prefs = manager.preferences
    
    st.subheader("⚙️ Paramètres de notification")
    
    # Sauvegarde des modifications
    if 'notif_prefs_changed' not in st.session_state:
        st.session_state['notif_prefs_changed'] = False
    
    with st.container(border=True):
        # Activation globale
        enabled = st.toggle(
            "Activer les notifications",
            value=prefs.enabled,
            help="Active ou désactive toutes les notifications"
        )
        
        if not enabled:
            st.info("🔕 Les notifications sont désactivées")
            if st.button("💾 Sauvegarder", type="primary", key="notif_save_disabled"):
                manager.update_preferences(enabled=False)
                st.success("✅ Paramètres sauvegardés")
            return
        
        st.divider()
        
        # Types de notifications
        st.markdown("**Types de notifications à afficher**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            show_critical = st.checkbox(
                f"{DEFAULT_ICONS[NotificationLevel.CRITICAL]} Critiques",
                value=prefs.show_critical,
                help="Erreurs bloquantes, pertes de données"
            )
            show_warning = st.checkbox(
                f"{DEFAULT_ICONS[NotificationLevel.WARNING]} Avertissements",
                value=prefs.show_warning,
                help="Alertes budget, actions irréversibles"
            )
        
        with col2:
            show_success = st.checkbox(
                f"{DEFAULT_ICONS[NotificationLevel.SUCCESS]} Succès",
                value=prefs.show_success,
                help="Confirmations d'actions"
            )
            show_info = st.checkbox(
                f"{DEFAULT_ICONS[NotificationLevel.INFO]} Informations",
                value=prefs.show_info,
                help="Messages contextuels"
            )
        
        with col3:
            show_achievement = st.checkbox(
                f"{DEFAULT_ICONS[NotificationLevel.ACHIEVEMENT]} Achievements",
                value=prefs.show_achievement,
                help="Récompenses, milestones"
            )
        
        st.divider()
        
        # Affichage
        st.markdown("**Options d'affichage**")
        
        col_a1, col_a2 = st.columns(2)
        
        with col_a1:
            max_visible = st.slider(
                "Notifications simultanées max",
                min_value=1,
                max_value=5,
                value=prefs.max_visible,
                help="Nombre maximum de notifications affichées en même temps"
            )
        
        with col_a2:
            group_similar = st.checkbox(
                "Regrouper les notifications similaires",
                value=prefs.group_similar,
                help="Évite les doublons en groupant les notifications du même type"
            )
        
        st.divider()
        
        # Durées personnalisées
        with st.expander("⏱️ Durées d'affichage personnalisées"):
            st.caption("Laissez vide pour utiliser les valeurs par défaut")
            
            col_d1, col_d2, col_d3 = st.columns(3)
            
            custom_durations = prefs.custom_durations.copy()
            
            with col_d1:
                success_dur = st.number_input(
                    "Succès (secondes)",
                    min_value=1,
                    max_value=30,
                    value=int(custom_durations.get('success', 3)),
                    step=1
                )
                custom_durations['success'] = float(success_dur)
            
            with col_d2:
                warning_dur = st.number_input(
                    "Avertissement (secondes)",
                    min_value=1,
                    max_value=60,
                    value=int(custom_durations.get('warning', 10)),
                    step=1
                )
                custom_durations['warning'] = float(warning_dur)
            
            with col_d3:
                info_dur = st.number_input(
                    "Info (secondes)",
                    min_value=1,
                    max_value=30,
                    value=int(custom_durations.get('info', 5)),
                    step=1
                )
                custom_durations['info'] = float(info_dur)
        
        st.divider()
        
        # Boutons d'action
        col_save, col_reset = st.columns([1, 1])
        
        with col_save:
            if st.button("💾 Sauvegarder les préférences", type="primary", use_container_width=True, key="notif_save_prefs"):
                manager.update_preferences(
                    enabled=enabled,
                    show_critical=show_critical,
                    show_warning=show_warning,
                    show_success=show_success,
                    show_info=show_info,
                    show_achievement=show_achievement,
                    max_visible=max_visible,
                    group_similar=group_similar,
                    custom_durations=custom_durations
                )
                st.success("✅ Préférences sauvegardées !")
                st.rerun()
        
        with col_reset:
            if st.button("🔄 Réinitialiser", use_container_width=True, key="notif_reset_prefs"):
                manager.reset_preferences()
                st.success("✅ Préférences réinitialisées")
                st.rerun()
    
    # Test de notification
    st.divider()
    st.subheader("🧪 Test de notification")
    
    col_test1, col_test2, col_test3, col_test4 = st.columns(4)
    
    with col_test1:
        if st.button("✅ Test Succès", use_container_width=True, key="notif_test_success"):
            manager.success("Ceci est une notification de test !")
            st.rerun()
    
    with col_test2:
        if st.button("⚠️ Test Avertissement", use_container_width=True, key="notif_test_warning"):
            manager.warning("Ceci est un avertissement de test")
            st.rerun()
    
    with col_test3:
        if st.button("ℹ️ Test Info", use_container_width=True, key="notif_test_info"):
            manager.info("Ceci est une information de test")
            st.rerun()
    
    with col_test4:
        if st.button("🏆 Test Achievement", use_container_width=True, key="notif_test_achievement"):
            manager.achievement("Test débloqué !")
            st.rerun()



def render_notification_badge_sidebar():
    """
    Affiche le badge de notification dans la sidebar avec un expander
    pour voir les détails rapidement (style Legacy amélioré).
    """
    manager = get_notification_manager()
    unread = manager.get_history_by_level(NotificationLevel.CRITICAL) + \
             manager.get_history_by_level(NotificationLevel.WARNING) + \
             manager.get_history_by_level(NotificationLevel.INFO) + \
             manager.get_history_by_level(NotificationLevel.SUCCESS) + \
             manager.get_history_by_level(NotificationLevel.ACHIEVEMENT)
    
    # Filter strictly unread
    unread = [n for n in unread if not n.read]
    # Sort by date desc (recent first)
    unread.sort(key=lambda x: x.created_at, reverse=True)
    
    count = len(unread)
    
    # Header du badge
    if count > 0:
        st.sidebar.markdown(f"🔔 **{count} notification{'s' if count > 1 else ''}**")
        
        # Expander pour voir les détails
        with st.sidebar.expander("📬 Messages Récents", expanded=False):
            if not unread:
                st.caption("Rien de nouveau.")
            else:
                for notif in unread[:5]:  # Max 5
                    with st.container(border=True):
                        col1, col2 = st.columns([0.8, 0.2])
                        with col1:
                            st.caption(f"{notif.icon or 'ℹ️'} **{notif.title or 'Info'}**")
                            st.markdown(f"<div style='font-size: 0.8em; color: #555;'>{notif.message}</div>", unsafe_allow_html=True)
                            if notif.age_seconds < 60:
                                st.caption("À l'instant")
                            elif notif.age_seconds < 3600:
                                st.caption(f"Il y a {int(notif.age_seconds/60)} min")
                        
                        with col2:
                            if st.button("✓", key=f"sb_read_{notif.id}", help="Marquer comme lu"):
                                manager.mark_as_read(notif.id)
                                st.rerun()
                
                if count > 5:
                    st.caption(f"... et {count - 5} autres.")
                
                # Global actions
                if st.button("Tout marquer lu", key="sb_read_all"):
                    manager.mark_all_as_read()
                    st.rerun()
    else:
        st.sidebar.markdown("🔔 Aucune notification")

