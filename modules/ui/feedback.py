"""
Module de feedback visuel centralisé pour FinancePerso.

Fournit des fonctions standardisées pour afficher des notifications,
toasts, et messages de confirmation à l'utilisateur.
# Force reload
"""

import functools
import time
from collections.abc import Callable
from enum import Enum
from typing import Any

import streamlit as st
import streamlit.components.v1 as components


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
    danger: bool = False,
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
            if st.button(
                confirm_label,
                type="primary" if not danger else "secondary",
                use_container_width=True,
                key="button_100",
            ):
                return True
        with col2:
            if st.button(
                cancel_label,
                type="secondary" if not danger else "primary",
                use_container_width=True,
                key="button_103",
            ):
                return False
        return None


# ============================================================================
# RICH FEEDBACK (Toast + Banner + Timer)
# ============================================================================


def show_rich_success(
    message: str,
    key_prefix: str,
    keep_open: bool = False,
    auto_close_delay: int = 3,
    on_close_callback: Callable | None = None,
):
    """
    Affiche un feedback riche : Toast immédiat + Banner optionnel + Auto-close.

    Args:
        message: Message de succès
        key_prefix: Préfixe unique pour les clés de session state
        keep_open: Si True, force l'affichage persistant initialement
        auto_close_delay: Délai avant fermeture automatique (si non gardé ouvert)
        on_close_callback: Callback optionnel à l'expiration
    """
    # 1. Toast immédiat
    toast_success(message, icon="✅")

    # Gestion des clés d'état
    keep_open_key = f"{key_prefix}_keep_open"
    if keep_open_key not in st.session_state:
        st.session_state[keep_open_key] = keep_open

    # 2. Conteneur persistant (Banner)
    # On utilise un conteneur pour pouvoir le vider ou le cacher
    container = st.empty()

    # Si l'utilisateur a demandé de garder ouvert ou qu'on est dans le délai
    with container.container():
        col1, col2 = st.columns([5, 1])
        with col1:
            st.success(message)
        with col2:
            # Bouton pour garder ouvert / fermer
            if not st.session_state[keep_open_key]:
                if st.button(
                    "📌 Fixer", key=f"{key_prefix}_pin_btn", help="Garder ce message affiché"
                ):
                    st.session_state[keep_open_key] = True
                    st.rerun()
            else:
                if st.button("❌ Fermer", key=f"{key_prefix}_close_btn"):
                    st.session_state[keep_open_key] = False
                    # On force le re-run pour nettoyer
                    st.rerun()

    # 3. Logique d'Auto-Close (Javascript)
    if not st.session_state.get(keep_open_key, False):
        # On utilise un script pour envoyer un signal de fermeture au parent (si dans un expander)
        # ou juste pour masquer visuellement après délai
        # Note: Streamlit ne permet pas facilement de supprimer un élément après délai sans rerun.
        # Mais on peut utiliser setTimeout pour appeler un callback Streamlit si on avait des custom components.
        # Ici, on utilise l'astuce du postMessage pour les expanders, ou rien si c'est top-level.

        st.markdown(
            f"""
            <script>
                setTimeout(function() {{
                    const keepOpen = {str(st.session_state.get(keep_open_key, False)).lower()};
                    if (!keepOpen) {{
                        try {{
                            window.parent.postMessage({{type: 'streamlit:closeExpander'}}, '*');
                        }} catch (e) {{}}
                    }}
                }}, {auto_close_delay * 1000});
            </script>
        """,
            unsafe_allow_html=True,
        )

        # Optionnel: Callback Python (ne marchera qu'au prochain rerun malheureusement)
        if on_close_callback:
            # On ne peut pas appeler le callback "dans le futur" ici sans blocage.
            pass


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
    error_message: str | None = None,
    show_banner: bool = False,
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


def config_saved_feedback(section: str | None = None):
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
    if "flash_messages" not in st.session_state:
        st.session_state.flash_messages = []
    st.session_state.flash_messages.append(
        {"message": message, "type": msg_type.value, "timestamp": time.time()}
    )


def display_flash_messages():
    """Affiche et nettoie les messages flash en attente."""
    if "flash_messages" not in st.session_state:
        return

    current_time = time.time()
    messages_to_display = []
    messages_to_keep = []

    for msg in st.session_state.flash_messages:
        # Messages de moins de 5 secondes
        if current_time - msg["timestamp"] < 5:
            messages_to_display.append(msg)
        else:
            messages_to_keep.append(msg)

    # Afficher les messages
    for msg in messages_to_display:
        if msg["type"] == "success":
            show_success(msg["message"])
        elif msg["type"] == "error":
            show_error(msg["message"])
        elif msg["type"] == "warning":
            show_warning(msg["message"])
        elif msg["type"] == "info":
            show_info(msg["message"])

    # Mettre à jour le session state
    st.session_state.flash_messages = messages_to_keep


def clear_flash_messages():
    """Nettoie tous les messages flash."""
    if "flash_messages" in st.session_state:
        st.session_state.flash_messages = []


def display_flash_toasts():
    """Affiche et nettoie les messages flash en attente (toasts)."""
    if "flash_messages" not in st.session_state:
        return

    current_time = time.time()
    messages_to_display = []
    messages_to_keep = []

    for msg in st.session_state.flash_messages:
        # Messages de moins de 5 secondes
        if current_time - msg["timestamp"] < 5:
            messages_to_display.append(msg)
        else:
            messages_to_keep.append(msg)

    # Afficher les messages sous forme de toasts
    for msg in messages_to_display:
        if msg["type"] == "success":
            toast_success(msg["message"])
        elif msg["type"] == "error":
            toast_error(msg["message"])
        elif msg["type"] == "warning":
            toast_warning(msg["message"])
        elif msg["type"] == "info":
            toast_info(msg["message"])

    # Mettre à jour le session state
    st.session_state.flash_messages = messages_to_keep


# ============================================================================
# COMPOSANTS AVANCÉS
# ============================================================================


def show_operation_status(
    operation_name: str,
    status: str,  # 'pending', 'running', 'success', 'error'
    progress: float | None = None,
    message: str | None = None,
):
    """
    Affiche le statut d'une opération longue.

    Usage:
        show_operation_status("Import", "running", 0.5, "Traitement...")
    """
    icons = {"pending": "⏳", "running": "🔄", "success": "✅", "error": "❌"}

    icon = icons.get(status, "❓")

    if status == "running" and progress is not None:
        st.progress(progress, text=f"{icon} {operation_name}: {message or 'En cours...'}")
    elif status == "success":
        toast_success(f"{operation_name} terminé", icon="✅")
    elif status == "error":
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
        "blue": "#3b82f6",
        "green": "#22c55e",
        "red": "#ef4444",
        "orange": "#f97316",
        "gray": "#6b7280",
    }

    bg_color = colors.get(color, colors["blue"])

    st.markdown(
        f"""
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
    """,
        unsafe_allow_html=True,
    )


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


def render_scroll_to_top(anchor_id: str = "top"):
    """
    Render a floating scroll-to-top button at the bottom right of the page.
    Uses JavaScript for smooth scrolling.

    Args:
        anchor_id: ID de l'ancre cible (défaut: "top")
    """
    import streamlit as st
    import time

    # Clé unique pour cette page/ancre
    page_key = st.session_state.get("current_page", "default")
    scroll_key = f"scroll_trigger_{page_key}_{anchor_id}"

    # Initialiser l'état de déclenchement du scroll
    if scroll_key not in st.session_state:
        st.session_state[scroll_key] = False

    # Créer l'ancre en haut de la page (invisible)
    st.markdown(f'<div id="{anchor_id}"></div>', unsafe_allow_html=True)

    # JavaScript pour effectuer le scroll (exécuté si le flag est True)
    if st.session_state[scroll_key]:
        # Réinitialiser le flag immédiatement
        st.session_state[scroll_key] = False
        # Exécuter le scroll via JavaScript
        st.markdown(
            """
            <script>
                (function() {
                    window.scrollTo({top: 0, behavior: 'smooth'});
                    // Alternative: scroll le conteneur principal de Streamlit
                    const mainContainer = document.querySelector('.main .block-container');
                    if (mainContainer) {
                        mainContainer.scrollTo({top: 0, behavior: 'smooth'});
                    }
                    // Essayer aussi avec le body et html
                    document.body.scrollTo({top: 0, behavior: 'smooth'});
                    document.documentElement.scrollTo({top: 0, behavior: 'smooth'});
                })();
            </script>
            """,
            unsafe_allow_html=True,
        )

    # Bouton en bas à droite
    st.markdown("---")
    cols = st.columns([6, 1])
    with cols[1]:
        if st.button(
            "⬆️ Haut",
            key=f"scroll_top_{page_key}_{anchor_id}_{int(time.time() * 1000)}",
            use_container_width=True,
            type="secondary",
        ):
            # Déclencher le scroll au prochain rerun
            st.session_state[scroll_key] = True
            st.rerun()

    # Bouton flottant permanent en bas à droite avec JavaScript direct
    st.markdown(
        """
        <style>
        .scroll-to-top-floating {
            position: fixed;
            bottom: 30px;
            right: 30px;
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
            z-index: 9999;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .scroll-to-top-floating:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(0,0,0,0.4);
        }
        .scroll-to-top-floating:active {
            transform: scale(0.95);
        }
        </style>
        <button class="scroll-to-top-floating" onclick="
            window.scrollTo({top: 0, behavior: 'smooth'});
            document.body.scrollTo({top: 0, behavior: 'smooth'});
            document.documentElement.scrollTo({top: 0, behavior: 'smooth'});
            const main = document.querySelector('.main .block-container');
            if (main) main.scrollTo({top: 0, behavior: 'smooth'});
        " title="Haut de page">
            ⬆️
        </button>
        """,
        unsafe_allow_html=True,
    )


def render_scroll_to_top_simple():
    """
    Alternative: Render a simple text link at the bottom of the page.
    Less intrusive but requires being at the bottom to see it.
    """
    import time

    scroll_key = "scroll_trigger_simple"

    if scroll_key not in st.session_state:
        st.session_state[scroll_key] = False

    # JavaScript pour effectuer le scroll si déclenché
    if st.session_state[scroll_key]:
        st.session_state[scroll_key] = False
        st.markdown(
            """
            <script>
                (function() {
                    window.scrollTo({top: 0, behavior: 'smooth'});
                    document.body.scrollTo({top: 0, behavior: 'smooth'});
                    document.documentElement.scrollTo({top: 0, behavior: 'smooth'});
                    const main = document.querySelector('.main .block-container');
                    if (main) main.scrollTo({top: 0, behavior: 'smooth'});
                })();
            </script>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button(
            "⬆️ Retour en haut de page",
            use_container_width=True,
            type="secondary",
            key=f"scroll_simple_{int(time.time() * 1000)}",
        ):
            st.session_state[scroll_key] = True
            st.rerun()
