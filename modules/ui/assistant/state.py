"""
State management for Assistant page.
Centralizes all session_state keys and operations.
"""
import streamlit as st
from typing import Any, Dict, List, Optional, Union


# Session state keys
STATE_KEYS = {
    # Audit
    'audit_results': 'assistant_audit_results',
    'audit_corrected': 'assistant_audit_corrected',
    'audit_hidden': 'assistant_audit_hidden',
    'audit_bulk_selection': 'assistant_audit_bulk_selection',
    'audit_in_progress': 'assistant_audit_in_progress',
    'audit_progress': 'assistant_audit_progress',
    
    # Amount anomalies
    'anomaly_results': 'assistant_anomaly_results',
    
    # Trends
    'trend_results': 'assistant_trend_results',
    'show_trends': 'assistant_show_trends',
    
    # Setup
    'setup_candidates': 'assistant_setup_candidates',
    
    # Chat
    'chat_history': 'assistant_chat_history',
    
    # UI
    'confirm_bulk_rules': 'assistant_confirm_bulk_rules',
    'show_corrected': 'assistant_show_corrected',
    'show_hidden': 'assistant_show_hidden',
}


def init_assistant_state():
    """Initialize all assistant-related session state variables."""
    defaults = {
        STATE_KEYS['audit_results']: None,
        STATE_KEYS['audit_corrected']: [],
        STATE_KEYS['audit_hidden']: [],
        STATE_KEYS['audit_bulk_selection']: [],
        STATE_KEYS['audit_in_progress']: False,
        STATE_KEYS['audit_progress']: 0,
        STATE_KEYS['anomaly_results']: None,
        STATE_KEYS['trend_results']: None,
        STATE_KEYS['show_trends']: False,
        STATE_KEYS['setup_candidates']: None,
        STATE_KEYS['chat_history']: [],
        STATE_KEYS['confirm_bulk_rules']: False,
        STATE_KEYS['show_corrected']: True,
        STATE_KEYS['show_hidden']: False,
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def get_assistant_state(key: str) -> Any:
    """Get a specific state value."""
    full_key = STATE_KEYS.get(key, key)
    return st.session_state.get(full_key)


def set_assistant_state(key: str, value: Any):
    """Set a specific state value."""
    full_key = STATE_KEYS.get(key, key)
    st.session_state[full_key] = value


def clear_assistant_state():
    """Clear all assistant state."""
    for key in STATE_KEYS.values():
        if key in st.session_state:
            del st.session_state[key]
    init_assistant_state()


def add_to_corrected(index: int):
    """Mark an anomaly as corrected."""
    corrected = get_assistant_state('audit_corrected')
    if index not in corrected:
        corrected.append(index)
        set_assistant_state('audit_corrected', corrected)


def remove_from_corrected(index: int):
    """Unmark a corrected anomaly."""
    corrected = get_assistant_state('audit_corrected')
    if index in corrected:
        corrected.remove(index)
        set_assistant_state('audit_corrected', corrected)


def add_to_hidden(index: int):
    """Hide an anomaly."""
    hidden = get_assistant_state('audit_hidden')
    if index not in hidden:
        hidden.append(index)
        set_assistant_state('audit_hidden', hidden)


def remove_from_hidden(index: int):
    """Unhide an anomaly."""
    hidden = get_assistant_state('audit_hidden')
    if index in hidden:
        hidden.remove(index)
        set_assistant_state('audit_hidden', hidden)


def toggle_bulk_selection(index: int, selected: bool):
    """Toggle bulk selection for an anomaly."""
    selection = get_assistant_state('audit_bulk_selection')
    if selected and index not in selection:
        selection.append(index)
    elif not selected and index in selection:
        selection.remove(index)
    set_assistant_state('audit_bulk_selection', selection)


def clear_bulk_selection():
    """Clear all bulk selections."""
    set_assistant_state('audit_bulk_selection', [])


def add_chat_message(role: str, content: str):
    """Add a message to chat history."""
    history = get_assistant_state('chat_history')
    history.append({'role': role, 'content': content})
    set_assistant_state('chat_history', history)


def clear_chat_history():
    """Clear chat history."""
    set_assistant_state('chat_history', [])


def get_audit_stats() -> Dict[str, int]:
    """Get current audit statistics."""
    results = get_assistant_state('audit_results') or []
    corrected = get_assistant_state('audit_corrected') or []
    hidden = get_assistant_state('audit_hidden') or []
    
    total = len(results)
    pending = total - len(corrected) - len(hidden)
    
    return {
        'total': total,
        'corrected': len(corrected),
        'hidden': len(hidden),
        'pending': max(0, pending)
    }


def switch_to_tab(tab_name: str):
    """Switch to specified tab using query params."""
    st.query_params['tab'] = tab_name
    st.rerun()
