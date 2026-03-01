"""
Loading States Component (Legacy wrapper).
Ce module fournit des implémentations de fallback simples pour la compatibilité.
"""

from contextlib import contextmanager

import streamlit as st


def render_skeleton_card(height: int = 100, key: str = None):
    """Affiche un squelette de carte simple."""
    placeholder = st.empty()
    placeholder.markdown(f"""
        <div style="
            height: {height}px;
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
            border-radius: 8px;
            margin: 8px 0;
        "></div>
        <style>
            @keyframes shimmer {{
                0% {{ background-position: 200% 0; }}
                100% {{ background-position: -200% 0; }}
            }}
        </style>
    """, unsafe_allow_html=True)
    return placeholder


def render_skeleton_text(lines: int = 3, key: str = None):
    """Affiche un squelette de texte simple."""
    placeholder = st.empty()
    html_lines = ""
    for i in range(lines):
        width = 100 if i < lines - 1 else 60
        html_lines += f'<div style="height: 12px; width: {width}%; background: #e0e0e0; margin: 8px 0; border-radius: 4px;"></div>'
    placeholder.markdown(f"""
        <div style="padding: 10px;">
            {html_lines}
        </div>
    """, unsafe_allow_html=True)
    return placeholder


def render_skeleton_kpi_cards(count: int = 4, key: str = None):
    """Affiche des squelettes de cartes KPI simples."""
    placeholder = st.empty()
    cols_html = ""
    for _ in range(count):
        cols_html += '''
            <div style="
                flex: 1;
                height: 80px;
                background: #f0f0f0;
                border-radius: 8px;
                margin: 0 8px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                padding: 0 16px;
            ">
                <div style="height: 12px; width: 40%; background: #d0d0d0; border-radius: 4px; margin-bottom: 8px;"></div>
                <div style="height: 20px; width: 60%; background: #e0e0e0; border-radius: 4px;"></div>
            </div>
        '''
    placeholder.markdown(f"""
        <div style="display: flex; flex-wrap: wrap; margin: -8px;">
            {cols_html}
        </div>
    """, unsafe_allow_html=True)
    return placeholder


def render_skeleton_table(rows: int = 5, cols: int = 4, key: str = None):
    """Affiche un squelette de tableau simple."""
    placeholder = st.empty()
    header_html = ""
    for _ in range(cols):
        header_html += '<th style="padding: 12px; background: #f5f5f5; border-bottom: 2px solid #ddd;"><div style="height: 14px; width: 80%; background: #d0d0d0; border-radius: 4px;"></div></th>'
    
    rows_html = ""
    for _ in range(rows):
        row_cells = ""
        for _ in range(cols):
            row_cells += '<td style="padding: 12px; border-bottom: 1px solid #eee;"><div style="height: 12px; width: 70%; background: #e8e8e8; border-radius: 4px;"></div></td>'
        rows_html += f'<tr>{row_cells}</tr>'
    
    placeholder.markdown(f"""
        <table style="width: 100%; border-collapse: collapse;">
            <thead><tr>{header_html}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    """, unsafe_allow_html=True)
    return placeholder


@contextmanager
def loading_spinner(text: str = "Chargement en cours..."):
    """Context manager pour afficher un spinner de chargement."""
    with st.spinner(text) as spinner:
        def update_msg(new_text: str):
            # Streamlit ne permet pas de mettre à jour dynamiquement le texte du spinner
            # On retourne une fonction no-op pour compatibilité
            pass
        yield update_msg


def render_progress_steps(steps: list, current_step: int = 0, key: str = None):
    """Affiche une barre de progression des étapes."""
    total_steps = len(steps)
    if total_steps == 0:
        return
    
    progress = (current_step + 1) / total_steps
    st.progress(progress, text=f"Étape {current_step + 1}/{total_steps}")
    
    # Afficher les étapes
    cols = st.columns(total_steps)
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if i < current_step:
                st.success(f"✓ {step}")
            elif i == current_step:
                st.info(f"⏳ {step}")
            else:
                st.caption(f"○ {step}")


def render_operation_progress(operation_id: str, title: str = "Opération en cours", key: str = None):
    """Affiche la progression d'une opération."""
    progress_key = f"op_progress_{operation_id}"
    
    if progress_key not in st.session_state:
        st.session_state[progress_key] = 0
    
    st.write(f"**{title}**")
    progress_bar = st.progress(st.session_state[progress_key])
    status_text = st.empty()
    
    return {
        "progress_bar": progress_bar,
        "status_text": status_text,
        "operation_id": operation_id
    }


def clear_operation_progress(operation_id: str):
    """Efface la progression d'une opération."""
    progress_key = f"op_progress_{operation_id}"
    if progress_key in st.session_state:
        del st.session_state[progress_key]
    st.empty()


__all__ = [
    "render_skeleton_card",
    "render_skeleton_text",
    "render_skeleton_kpi_cards",
    "render_skeleton_table",
    "loading_spinner",
    "render_progress_steps",
    "render_operation_progress",
    "clear_operation_progress",
]
