"""
Confirmation Dialog Component - For destructive actions.
Prevents accidental data loss.
"""
import streamlit as st
from typing import Optional, Callable


def confirm_dialog(
    title: str = "Confirmer l'action",
    message: str = "Êtes-vous sûr de vouloir continuer ?",
    confirm_label: str = "Confirmer",
    confirm_icon: str = "✓",
    cancel_label: str = "Annuler",
    cancel_icon: str = "✕",
    danger: bool = True,
    key: str = "confirm_dialog"
) -> bool:
    """
    Show a confirmation dialog.
    
    Args:
        title: Dialog title
        message: Warning message
        confirm_label: Label for confirm button
        confirm_icon: Icon for confirm button
        cancel_label: Label for cancel button
        cancel_icon: Icon for cancel button
        danger: Whether this is a dangerous action (red confirm button)
        key: Unique key
        
    Returns:
        True if confirmed, False otherwise
    """
    # Use session state to track confirmation
    confirm_key = f"{key}_confirmed"
    show_key = f"{key}_show_dialog"
    
    if confirm_key not in st.session_state:
        st.session_state[confirm_key] = False
    
    if show_key not in st.session_state:
        st.session_state[show_key] = False
    
    # Show dialog if requested
    if st.session_state[show_key]:
        with st.container(border=True):
            # Warning header
            st.markdown(f"""
            <div style="
                background: {'#fef2f2' if danger else '#fffbeb'};
                border-left: 4px solid {'#ef4444' if danger else '#f59e0b'};
                padding: 1rem;
                margin-bottom: 1rem;
                border-radius: 4px;
            ">
                <h4 style="margin: 0; color: {'#dc2626' if danger else '#d97706'};">⚠️ {title}</h4>
                <p style="margin: 0.5rem 0 0 0; color: {'#7f1d1d' if danger else '#92400e'};">{message}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"{cancel_icon} {cancel_label}", 
                            use_container_width=True, 
                            key=f"{key}_cancel"):
                    st.session_state[show_key] = False
                    st.session_state[confirm_key] = False
                    st.rerun()
            
            with col2:
                button_type = "primary" if danger else "secondary"
                if st.button(f"{confirm_icon} {confirm_label}", 
                            use_container_width=True, 
                            type=button_type,
                            key=f"{key}_confirm"):
                    st.session_state[show_key] = False
                    st.session_state[confirm_key] = True
                    st.rerun()
        
        return st.session_state[confirm_key]
    
    return st.session_state[confirm_key]


def trigger_confirmation(key: str):
    """Trigger the confirmation dialog to show."""
    show_key = f"{key}_show_dialog"
    st.session_state[show_key] = True
    st.rerun()


def reset_confirmation(key: str):
    """Reset the confirmation state."""
    confirm_key = f"{key}_confirmed"
    show_key = f"{key}_show_dialog"
    st.session_state[confirm_key] = False
    st.session_state[show_key] = False


def with_confirmation(
    action: Callable,
    title: str = "Confirmer l'action",
    message: str = "Êtes-vous sûr ?",
    key: str = "confirm_action"
):
    """
    Wrapper to require confirmation before executing an action.
    
    Args:
        action: Function to execute if confirmed
        title: Dialog title
        message: Warning message
        key: Unique key
    """
    confirm_key = f"{key}_confirmed"
    show_key = f"{key}_show_dialog"
    
    # Initialize
    if confirm_key not in st.session_state:
        st.session_state[confirm_key] = False
    if show_key not in st.session_state:
        st.session_state[show_key] = False
    
    # If confirmed, execute and reset
    if st.session_state[confirm_key]:
        st.session_state[confirm_key] = False
        action()
        return
    
    # If showing dialog, render it
    if st.session_state[show_key]:
        confirmed = confirm_dialog(title, message, key=key)
        if confirmed:
            st.session_state[confirm_key] = False
            action()


def confirm_delete(
    item_name: str,
    item_type: str = "élément",
    key: str = "delete_confirm"
) -> bool:
    """
    Specialized confirmation for delete operations.
    
    Args:
        item_name: Name of the item being deleted
        item_type: Type of item (category, transaction, etc.)
        key: Unique key
        
    Returns:
        True if confirmed
    """
    return confirm_dialog(
        title=f"Supprimer {item_type}",
        message=f"Êtes-vous sûr de vouloir supprimer '{item_name}' ? Cette action est irréversible.",
        confirm_label="Supprimer",
        confirm_icon="🗑️",
        danger=True,
        key=key
    )


# Export
__all__ = [
    'confirm_dialog',
    'trigger_confirmation',
    'reset_confirmation',
    'with_confirmation',
    'confirm_delete',
]
