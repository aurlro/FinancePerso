"""
Progress Tracker Component
Gamification progress bar with session-based tracking.
"""
import streamlit as st


def render_progress_tracker(
    current_count: int,
    session_key: str = "validation_progress",
    emoji: str = "💪",
    show_percentage: bool = False
) -> None:
    """
    Render progress bar with motivational message.
    
    Tracks initial count in session state and shows progress based on
    reduction of pending items.
    
    Args:
        current_count: Current number of pending items
        session_key: Session state key for tracking initial count
        emoji: Emoji to display in progress text
        show_percentage: Whether to show percentage alongside count
        
    Example:
        >>> pending_count = len(pending_transactions)
        >>> render_progress_tracker(pending_count)
        # Shows: "Progression : 15 traitées sur 100 💪" with progress bar
    """
    # Initialize or update initial count
    initial_key = f"{session_key}_initial"
    
    if initial_key not in st.session_state or current_count > st.session_state[initial_key]:
        st.session_state[initial_key] = current_count
    
    init_count = st.session_state[initial_key]
    
    if init_count > 0:
        # Calculate progress
        done_count = init_count - current_count
        progress = 1.0 - (current_count / init_count)
        
        # Build progress text
        if show_percentage:
            percentage = int(progress * 100)
            text = f"Progression : {done_count} traitées sur {init_count} ({percentage}%) {emoji}"
        else:
            text = f"Progression : {done_count} traitées sur {init_count} {emoji}"
        
        # Render progress bar
        st.progress(progress, text=text)
    else:
        # All complete
        st.success(f"✅ Toutes les transactions traitées ! {emoji}")


def reset_progress_tracker(session_key: str = "validation_progress") -> None:
    """
    Reset progress tracker (useful after major data changes).
    
    Args:
        session_key: Session state key to reset
    """
    initial_key = f"{session_key}_initial"
    if initial_key in st.session_state:
        del st.session_state[initial_key]
