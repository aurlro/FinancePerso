"""Log viewer UI component - Simplified."""

import streamlit as st
from pathlib import Path


def render_log_viewer() -> None:
    """Render log viewer section."""
    st.subheader("📋 Logs système")
    
    log_files = list(Path("logs").glob("*.log")) if Path("logs").exists() else []
    
    if not log_files:
        st.info("Aucun fichier log trouvé.")
        return
    
    selected_log = st.selectbox(
        "Fichier log",
        options=[f.name for f in log_files],
        key="log_file_selector"
    )
    
    if selected_log:
        log_path = Path("logs") / selected_log
        try:
            content = log_path.read_text(encoding="utf-8", errors="ignore")
            # Show last 100 lines
            lines = content.split("\n")[-100:]
            st.code("\n".join(lines), language="log")
        except Exception as e:
            st.error(f"Erreur lecture log: {e}")
