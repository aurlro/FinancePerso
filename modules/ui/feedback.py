"""
Module de feedback visuel centralisé pour FinancePerso.

Fournit des fonctions standardisées pour afficher des notifications,
toasts, et messages de confirmation à l'utilisateur.
"""

import streamlit as st
import streamlit.components.v1 as components
from enum import Enum
from typing import Optional, Callable, Any
import functools
import time


class FeedbackType(Enum):
    """Types de feedback disponibles."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# ============================================================================
# TOAST NOTIFICATIONS (brefs messages en haut à droite)
# ============================================================================

def toast_success(message: str, icon: str = "✅"):
    """Affiche un toast de succès."""
    st.toast(message, icon=icon)


def toast_error(message: str, icon: str = "❌"):
    """Affiche un toast d'erreur."""
    st.toast(message, icon=icon)


def toast_warning(message: str, icon: str = "⚠️"):
    """Affiche un toast d'avertissement."""
    st.toast(message, icon=icon)


def toast_info(message: str, icon: str = "ℹ️"):
    """Affiche un toast d'information."""
    st.toast(message, icon=icon)


# ============================================================================
# BANNERS (messages persistants dans la page)
# ============================================================================

def show_success(message: str, icon: str = "✅"):
    """Affiche un message de succès persistant."""
    st.success(f"{icon} {message}")


def show_error(message: str, icon: str = "❌"):
    """Affiche un message d'erreur persistant."""
    st.error(f"{icon} {message}")


def show_warning(message: str, icon: str = "⚠️"):
    """Affiche un message d'avertissement persistant."""
    st.warning(f"{icon} {message}")


def show_info(message: str, icon: str = "ℹ️"):
    """Affiche un message d'information persistant."""
    st.info(f"{icon} {message}")


# ============================================================================
# CONFIRMATION DIALOGS
# ============================================================================

def confirm_dialog(
    title: str,
    message: str,
    confirm_label: str = "Confirmer",
    cancel_label: str = "Annuler",
    confirm_type: str = "primary",
    danger: bool = False
) -> bool:
    """
    Affiche une boîte de dialogue de confirmation.
    Retourne True si confirmé, False sinon.
    
    Usage:
        if confirm_dialog("Supprimer ?", "Cette action est irréversible"):
            delete_item()
    """
    with st.container(border=True):
        if danger:
            st.error(f"⚠️ {title}")
        else:
            st.warning(f"⚠️ {title}")
        st.write(message)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button(confirm_label, type="primary" if not danger else "secondary", use_container_width=True, key='button_100'):
                return True
        with col2:
            if st.button(cancel_label, type="secondary" if not danger else "primary", use_container_width=True, key='button_103'):
                return False
        return None


# ============================================================================
# SPINNER / PROGRESS
# ============================================================================

def with_spinner(message: str = "Chargement..."):
    """
    Décorateur pour afficher un spinner pendant l'exécution d'une fonction.
    
    Usage:
        @with_spinner("Traitement en cours...")
        def long_operation():
            time.sleep(2)
            return result
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with st.spinner(message):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# ACTION FEEDBACK (toast + banner combinés)
# ============================================================================

def action_feedback(
    success: bool,
    success_message: str,
    error_message: Optional[str] = None,
    show_banner: bool = False
):
    """
    Affiche un feedback d'action (toast + banner optionnel).
    
    Args:
        success: Si l'action a réussi
        success_message: Message en cas de succès
        error_message: Message en cas d'erreur (défaut: success_message)
        show_banner: Si True, affiche aussi un banner persistant
    """
    if success:
        toast_success(success_message)
        if show_banner:
            show_success(success_message)
    else:
        msg = error_message or success_message
        toast_error(msg)
        if show_banner:
            show_error(msg)


def save_feedback(entity_name: str, success: bool = True, created: bool = True):
    """
    Feedback standard pour opérations de sauvegarde.
    
    Args:
        entity_name: Nom de l'entité (ex: "Membre", "Catégorie")
        success: Si l'opération a réussi
        created: Si c'est une création (True) ou modification (False)
    """
    action = "créé" if created else "mis à jour"
    if success:
        toast_success(f"✅ {entity_name} {action} avec succès !")
    else:
        toast_error(f"❌ Erreur lors de la sauvegarde de {entity_name}")


def delete_feedback(entity_name: str, success: bool = True):
    """
    Feedback standard pour opérations de suppression.
    
    Args:
        entity_name: Nom de l'entité (ex: "Membre", "Catégorie")
        success: Si l'opération a réussi
    """
    if success:
        toast_success(f"🗑️ {entity_name} supprimé avec succès")
    else:
        toast_error(f"❌ Erreur lors de la suppression de {entity_name}")


# ============================================================================
# NOTIFICATIONS CONTEXTUELLES
# ============================================================================

def notify_no_data(message: str = "Aucune donnée disponible"):
    """Affiche une notification quand il n'y a pas de données."""
    show_info(message, icon="📭")


def notify_action_required(message: str):
    """Affiche une notification demandant une action utilisateur."""
    show_warning(message, icon="👉")


def notify_completed(message: str = "Opération terminée !"):
    """Affiche une notification de complétion."""
    toast_success(message, icon="🎉")


# ============================================================================
# VALIDATION FEEDBACK
# ============================================================================

def validation_feedback(count: int, entity_name: str = "élément"):
    """
    Feedback pour validation en masse.
    
    Args:
        count: Nombre d'éléments validés
        entity_name: Nom de l'entité (ex: "transaction", "groupe")
    """
    if count == 0:
        toast_warning("Aucun élément à valider", icon="⚠️")
    elif count == 1:
        toast_success(f"1 {entity_name} validé", icon="✅")
    else:
        toast_success(f"{count} {entity_name}s validés", icon="✅")


def import_feedback(count: int, skipped: int = 0, account_name: str = ""):
    """
    Feedback pour import de transactions.
    
    Args:
        count: Nombre de transactions importées
        skipped: Nombre de doublons ignorés
        account_name: Nom du compte
    """
    if count == 0 and skipped == 0:
        toast_info("Aucune nouvelle transaction à importer", icon="ℹ️")
    elif count == 0 and skipped > 0:
        toast_warning(f"{skipped} doublons ignorés", icon="⚠️")
    else:
        msg = f"🎉 {count} transactions importées"
        if account_name:
            msg += f" sur {account_name}"
        if skipped > 0:
            msg += f" ({skipped} doublons ignorés)"
        toast_success(msg, icon="📥")


# ============================================================================
# CONFIGURATION FEEDBACK
# ============================================================================

def config_saved_feedback(section: Optional[str] = None):
    """Feedback quand une configuration est sauvegardée."""
    msg = "Configuration sauvegardée"
    if section:
        msg += f" ({section})"
    toast_success(msg, icon="⚙️")


def api_config_feedback(provider: str, success: bool = True):
    """Feedback pour configuration API."""
    if success:
        toast_success(f"✅ Configuration {provider} enregistrée", icon="🔑")
    else:
        toast_error(f"❌ Erreur configuration {provider}", icon="🔑")


# ============================================================================
# ANIMATIONS DE CÉLÉBRATION
# ============================================================================

def celebrate_completion(min_items: int = 10, actual_items: int = 0):
    """
    Déclenche des animations de célébration pour les grandes opérations.
    
    Args:
        min_items: Nombre minimum d'items pour déclencher la célébration
        actual_items: Nombre réel d'items traités
    """
    if actual_items >= min_items:
        st.balloons()


def celebrate_all_done():
    """Animation quand tout est terminé (ex: toutes les transactions validées)."""
    st.balloons()
    toast_success("Tout est à jour ! 🎉", icon="🎊")


# ============================================================================
# SESSION STATE HELPERS
# ============================================================================

def set_flash_message(message: str, msg_type: FeedbackType = FeedbackType.SUCCESS):
    """
    Stocke un message flash dans le session state pour affichage après rerun.
    
    Usage:
        set_flash_message("Opération réussie !")
        st.rerun()
        
        # Au début de la page:
        display_flash_messages()
    """
    if 'flash_messages' not in st.session_state:
        st.session_state.flash_messages = []
    st.session_state.flash_messages.append({
        'message': message,
        'type': msg_type.value,
        'timestamp': time.time()
    })


def display_flash_messages():
    """Affiche et nettoie les messages flash en attente."""
    if 'flash_messages' not in st.session_state:
        return
    
    current_time = time.time()
    messages_to_display = []
    messages_to_keep = []
    
    for msg in st.session_state.flash_messages:
        # Messages de moins de 5 secondes
        if current_time - msg['timestamp'] < 5:
            messages_to_display.append(msg)
        else:
            messages_to_keep.append(msg)
    
    # Afficher les messages
    for msg in messages_to_display:
        if msg['type'] == 'success':
            show_success(msg['message'])
        elif msg['type'] == 'error':
            show_error(msg['message'])
        elif msg['type'] == 'warning':
            show_warning(msg['message'])
        elif msg['type'] == 'info':
            show_info(msg['message'])
    
    # Mettre à jour le session state
    st.session_state.flash_messages = messages_to_keep


def clear_flash_messages():
    """Nettoie tous les messages flash."""
    if 'flash_messages' in st.session_state:
        st.session_state.flash_messages = []


def display_flash_toasts():
    """Affiche et nettoie les messages flash en attente (toasts)."""
    if 'flash_messages' not in st.session_state:
        return
    
    current_time = time.time()
    messages_to_display = []
    messages_to_keep = []
    
    for msg in st.session_state.flash_messages:
        # Messages de moins de 5 secondes
        if current_time - msg['timestamp'] < 5:
            messages_to_display.append(msg)
        else:
            messages_to_keep.append(msg)
    
    # Afficher les messages sous forme de toasts
    for msg in messages_to_display:
        if msg['type'] == 'success':
            toast_success(msg['message'])
        elif msg['type'] == 'error':
            toast_error(msg['message'])
        elif msg['type'] == 'warning':
            toast_warning(msg['message'])
        elif msg['type'] == 'info':
            toast_info(msg['message'])
    
    # Mettre à jour le session state
    st.session_state.flash_messages = messages_to_keep


# ============================================================================
# COMPOSANTS AVANCÉS
# ============================================================================

def show_operation_status(
    operation_name: str,
    status: str,  # 'pending', 'running', 'success', 'error'
    progress: Optional[float] = None,
    message: Optional[str] = None
):
    """
    Affiche le statut d'une opération longue.
    
    Usage:
        show_operation_status("Import", "running", 0.5, "Traitement...")
    """
    icons = {
        'pending': '⏳',
        'running': '🔄',
        'success': '✅',
        'error': '❌'
    }
    
    icon = icons.get(status, '❓')
    
    if status == 'running' and progress is not None:
        st.progress(progress, text=f"{icon} {operation_name}: {message or 'En cours...'}")
    elif status == 'success':
        toast_success(f"{operation_name} terminé", icon="✅")
    elif status == 'error':
        toast_error(f"{operation_name} échoué", icon="❌")
    else:
        st.info(f"{icon} {operation_name}: {message or 'En attente...'}")


def show_count_badge(count: int, label: str, color: str = "blue"):
    """
    Affiche un badge avec un compteur.
    
    Args:
        count: Nombre à afficher
        label: Texte du label
        color: Couleur du badge (blue, green, red, orange)
    """
    colors = {
        'blue': '#3b82f6',
        'green': '#22c55e',
        'red': '#ef4444',
        'orange': '#f97316',
        'gray': '#6b7280'
    }
    
    bg_color = colors.get(color, colors['blue'])
    
    st.markdown(f"""
        <div style="
            display: inline-flex;
            align-items: center;
            background-color: {bg_color}20;
            border: 1px solid {bg_color};
            border-radius: 12px;
            padding: 2px 10px;
            font-size: 0.85em;
            color: {bg_color};
            font-weight: 600;
        ">
            <span style="background-color: {bg_color}; color: white; border-radius: 10px; 
                         padding: 1px 6px; margin-right: 6px; font-size: 0.8em;">
                {count}
            </span>
            {label}
        </div>
    """, unsafe_allow_html=True)


# ============================================================================
# SHORTCUTS STREAMLIT NATIVE
# ============================================================================

def show_progress(label: str = "Chargement..."):
    """Retourne un context manager pour st.status."""
    return st.status(label, expanded=True)


def show_expanded_status(label: str):
    """Affiche un statut expansé pour les opérations détaillées."""
    return st.status(label, expanded=True)


# ============================================================================
# SCROLL TO TOP BUTTON
# ============================================================================

def render_scroll_to_top():
    """
    Render a floating scroll-to-top button at the bottom right of the page.
    Uses a Streamlit-native button with JavaScript injection for scrolling.
    """
    import streamlit.components.v1 as components
    
    # Create a placeholder for the button at the bottom of the page
    st.markdown("---")
    col1, col2, col3 = st.columns([3, 1, 3])
    
    with col2:
        # Use a unique key based on page to avoid conflicts
        page_key = st.session_state.get('current_page', 'default')
        if st.button("⬆️ Haut de page", key=f"scroll_top_{page_key}", use_container_width=True, type="secondary"):
            # JavaScript to scroll to top
            components.html("""
                <script>
                window.parent.scrollTo({top: 0, behavior: 'smooth'});
                </script>
            """, height=0)
            st.rerun()
    
    # Also add the floating button using HTML with proper height
    components.html("""
        <style>
        .scroll-to-top-floating {
            position: fixed;
            bottom: 80px;
            right: 20px;
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
            z-index: 999999;
            opacity: 0.8;
        }
        .scroll-to-top-floating:hover {
            opacity: 1;
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.4);
        }
        </style>
        <button class="scroll-to-top-floating" onclick="window.parent.scrollTo({top: 0, behavior: 'smooth'});" title="Retour en haut">
            ⬆️
        </button>
    """, height=80)


def render_scroll_to_top_simple():
    """
    Alternative: Render a simple text link at the bottom of the page.
    Less intrusive but requires being at the bottom to see it.
    """
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("⬆️ Retour en haut de page", use_container_width=True, type="secondary", key='button_548'):
            st.markdown("<script>window.scrollTo(0, 0);</script>", unsafe_allow_html=True)
