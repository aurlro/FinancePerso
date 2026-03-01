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

import streamlit as st


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
            st.subheader(title)
        st.write(message)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button(cancel_label, key=f"cancel_{title}", use_container_width=True):
                return False
        with col2:
            btn_type = "primary" if not danger else "secondary"
            if st.button(
                confirm_label,
                key=f"confirm_{title}",
                type=btn_type,
                use_container_width=True,
            ):
                return True
    return False


# ============================================================================
# MESSAGE FLASH (persiste entre les pages)
# ============================================================================


def flash_message(message: str, type_: str = "info"):
    """
    Ajoute un message flash qui sera affiché sur la prochaine page.

    Usage:
        flash_message("Opération réussie !", "success")
        st.switch_page("pages/1_Accueil.py")
    """
    if "flash_messages" not in st.session_state:
        st.session_state.flash_messages = []
    st.session_state.flash_messages.append({"message": message, "type": type_})


def display_flash_messages():
    """Affiche les messages flash en attente."""
    if "flash_messages" not in st.session_state:
        return

    messages = st.session_state.flash_messages.copy()
    st.session_state.flash_messages = []

    for msg in messages:
        if msg["type"] == "success":
            show_success(msg["message"])
        elif msg["type"] == "error":
            show_error(msg["message"])
        elif msg["type"] == "warning":
            show_warning(msg["message"])
        else:
            show_info(msg["message"])


# ============================================================================
# SPINNER & PROGRESS
# ============================================================================


def with_spinner(message: str = "Chargement..."):
    """
    Décorateur pour afficher un spinner pendant l'exécution.

    Usage:
        @with_spinner("Traitement en cours...")
        def ma_fonction():
            time.sleep(2)
            return result
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with st.spinner(message):
                return func(*args, **kwargs)

        return wrapper

    return decorator


# ============================================================================
# FORM VALIDATION FEEDBACK
# ============================================================================


def field_error(field_name: str, message: str):
    """Affiche une erreur pour un champ spécifique."""
    st.error(f"❌ **{field_name}**: {message}")


def field_success(field_name: str, message: str = "Validé"):
    """Affiche un succès pour un champ spécifique."""
    st.success(f"✅ **{field_name}**: {message}")


# ============================================================================
# SCROLL TO TOP BUTTON
# ============================================================================


def render_scroll_to_top(anchor_id: str = "top"):
    """
    Affiche un bouton flottant pour remonter en haut de page.
    Le bouton n'apparaît que si l'utilisateur a scrollé de plus de 300px.

    Args:
        anchor_id: ID de l'ancre cible (défaut: "top")
    """
    import streamlit as st

    # Clé unique pour cette page
    page_key = st.session_state.get("current_page", "default")
    unique_id = f"{page_key}_{anchor_id}_{int(time.time() * 1000)}"
    scroll_key = f"scroll_trigger_{unique_id}"

    # Initialiser l'état
    if scroll_key not in st.session_state:
        st.session_state[scroll_key] = False

    # CSS pour le bouton fixed + JavaScript pour la détection de scroll
    st.markdown(
        f"""
        <style>
        /* Container fixed pour le bouton */
        .scroll-to-top-fixed-{unique_id} {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 999999;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s, visibility 0.3s;
        }}
        .scroll-to-top-fixed-{unique_id}.visible {{
            opacity: 1;
            visibility: visible;
        }}
        /* Style du bouton */
        .scroll-to-top-fixed-{unique_id} button {{
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-size: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .scroll-to-top-fixed-{unique_id} button:hover {{
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(0,0,0,0.4);
        }}
        </style>
        
        <div id="scroll-container-{unique_id}" class="scroll-to-top-fixed-{unique_id}">
            <button onclick="scrollToTop{unique_id}()" title="Remonter en haut">⬆️</button>
        </div>
        
        <script>
            // Fonction de scroll
            function scrollToTop{unique_id}() {{
                // Essayer plusieurs méthodes
                const selectors = [
                    '.main .block-container',
                    '[data-testid="stAppViewContainer"]',
                    '.stApp',
                    'body',
                    'html'
                ];
                
                selectors.forEach(sel => {{
                    const el = document.querySelector(sel);
                    if (el) el.scrollTo({{top: 0, behavior: 'smooth'}});
                }});
                
                window.scrollTo({{top: 0, behavior: 'smooth'}});
            }}
            
            // Détection de scroll
            function checkScroll{unique_id}() {{
                const container = document.querySelector('.main .block-container') || window;
                let scrollTop = 0;
                
                if (container === window) {{
                    scrollTop = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
                }} else {{
                    scrollTop = container.scrollTop;
                }}
                
                const btnContainer = document.getElementById('scroll-container-{unique_id}');
                if (btnContainer) {{
                    if (scrollTop > 300) {{
                        btnContainer.classList.add('visible');
                    }} else {{
                        btnContainer.classList.remove('visible');
                    }}
                }}
            }}
            
            // Event listeners
            window.addEventListener('scroll', checkScroll{unique_id}, true);
            document.addEventListener('scroll', checkScroll{unique_id}, true);
            
            // Vérifier régulièrement
            setInterval(checkScroll{unique_id}, 500);
            checkScroll{unique_id}();
        </script>
        """,
        unsafe_allow_html=True,
    )


def render_scroll_to_top_simple():
    """
    Alternative: Render a simple text link at the bottom of the page.
    Less intrusive but requires being at the bottom to see it.
    """

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
