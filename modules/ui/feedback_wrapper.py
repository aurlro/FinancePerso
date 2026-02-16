"""
Feedback wrapper for user actions.
Provides consistent feedback (success, error, warning, info) for all user operations.
"""

from collections.abc import Callable
from functools import wraps
from typing import Any

import streamlit as st

from modules.logger import logger


def with_feedback(
    success_msg: str | None = None,
    error_msg: str = "Une erreur est survenue",
    showSpinner: bool = False,
    spinner_text: str = "Traitement en cours...",
    rerun: bool = False,
):
    """
    Decorator to add automatic feedback to functions.

    Args:
        success_msg: Message to show on success (if None, no success message)
        error_msg: Message to show on error
        showSpinner: Whether to show a spinner during execution
        spinner_text: Text to show in the spinner
        rerun: Whether to rerun the app after success

    Example:
        @with_feedback("Catégorie créée avec succès!", "Erreur lors de la création")
        def create_category(name):
            # ... create logic
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            from modules.ui.feedback import toast_error, toast_success

            try:
                if showSpinner:
                    with st.spinner(spinner_text):
                        result = func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                if success_msg:
                    toast_success(f"✅ {success_msg}")

                if rerun:
                    st.rerun()

                return result

            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                toast_error(f"❌ {error_msg}: {str(e)[:100]}")
                raise

        return wrapper

    return decorator


def with_confirm(
    confirm_message: str = "Êtes-vous sûr ?",
    success_msg: str | None = None,
    error_msg: str = "Action échouée",
):
    """
    Decorator to add confirmation dialog before action.

    Args:
        confirm_message: Message to show in confirmation dialog
        success_msg: Message to show on success
        error_msg: Message to show on error
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            from modules.ui.feedback import toast_error, toast_success

            # Check if confirmed via session state
            confirm_key = f"confirm_{func.__name__}"

            if not st.session_state.get(confirm_key, False):
                st.session_state[confirm_key] = True
                return None

            try:
                result = func(*args, **kwargs)
                st.session_state[confirm_key] = False

                if success_msg:
                    toast_success(f"✅ {success_msg}")

                return result

            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                toast_error(f"❌ {error_msg}: {str(e)[:100]}")
                st.session_state[confirm_key] = False
                raise

        return wrapper

    return decorator


def show_action_feedback(
    action_type: str,
    entity_name: str,
    success: bool = True,
    error_detail: str | None = None,
    icon: str | None = None,
):
    """
    Show standardized feedback for CRUD operations.

    Args:
        action_type: 'create', 'update', 'delete', 'import', 'validate'
        entity_name: Name of the entity (e.g., 'Catégorie', 'Transaction')
        success: Whether the action succeeded
        error_detail: Optional error details
        icon: Optional custom icon
    """
    from modules.ui.feedback import toast_error, toast_success

    action_labels = {
        "create": ("créée", "création"),
        "update": ("mise à jour", "mise à jour"),
        "delete": ("supprimée", "suppression"),
        "import": ("importée", "import"),
        "validate": ("validée", "validation"),
        "rename": ("renommée", "renommage"),
        "merge": ("fusionnée", "fusion"),
    }

    past_participle, noun = action_labels.get(action_type, ("traitée", "traitement"))

    if success:
        default_icon = {
            "create": "🎉",
            "update": "💾",
            "delete": "🗑️",
            "import": "📥",
            "validate": "✅",
            "rename": "👤",
            "merge": "🔀",
        }.get(action_type, "✅")

        toast_success(
            f"{icon or default_icon} {entity_name} {past_participle} avec succès!",
            icon=icon or default_icon,
        )
    else:
        error_text = f": {error_detail[:50]}" if error_detail else ""
        toast_error(f"❌ Échec de la {noun} de '{entity_name}'{error_text}", icon="❌")


def safe_execute(
    func: Callable,
    *args,
    success_msg: str | None = None,
    error_msg: str = "Action échouée",
    default_return: Any = None,
    **kwargs,
) -> Any:
    """
    Safely execute a function with feedback.

    Args:
        func: Function to execute
        *args: Positional arguments
        success_msg: Success message
        error_msg: Error message
        default_return: Value to return on error
        **kwargs: Keyword arguments

    Returns:
        Function result or default_return on error
    """
    from modules.ui.feedback import toast_error, toast_success

    try:
        result = func(*args, **kwargs)
        if success_msg:
            toast_success(f"✅ {success_msg}")
        return result
    except Exception as e:
        logger.error(f"Error executing {func.__name__}: {e}")
        toast_error(f"❌ {error_msg}: {str(e)[:100]}")
        return default_return
