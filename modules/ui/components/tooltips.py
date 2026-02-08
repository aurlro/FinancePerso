"""
Tooltips and Help Component - Contextual help for better UX.
Provides guidance without cluttering the interface.
"""
import streamlit as st


def render_tooltip(text: str, help_text: str, icon: str = "💡"):
    """
    Render a label with tooltip.
    
    Args:
        text: Main label text
        help_text: Help text shown on hover
        icon: Icon to show
    """
    st.markdown(f"""
    <span title="{help_text}" style="
        border-bottom: 1px dotted #94a3b8;
        cursor: help;
        position: relative;
    ">{text} <span style="color: #94a3b8;">{icon}</span></span>
    """, unsafe_allow_html=True)


def render_info_box(
    title: str,
    content: str,
    type: str = "info"  # info, warning, success, error
):
    """
    Render an info box with icon.
    
    Args:
        title: Box title
        content: Box content
        type: Type of info box
    """
    colors = {
        "info": ("#3b82f6", "#dbeafe", "ℹ️"),
        "warning": ("#f59e0b", "#fef3c7", "⚠️"),
        "success": ("#10b981", "#d1fae5", "✅"),
        "error": ("#ef4444", "#fee2e2", "❌"),
    }
    
    border_color, bg_color, icon = colors.get(type, colors["info"])
    
    st.markdown(f"""
    <div style="
        background: {bg_color};
        border-left: 4px solid {border_color};
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    ">
        <div style="font-weight: 600; color: {border_color}; margin-bottom: 0.5rem;">
            {icon} {title}
        </div>
        <div style="color: #374151;">{content}</div>
    </div>
    """, unsafe_allow_html=True)


def render_contextual_help(helps: dict):
    """
    Render a collapsible help section.
    
    Args:
        helps: Dict of {title: content}
    """
    with st.expander("❓ Aide et conseils", expanded=False):
        for title, content in helps.items():
            st.markdown(f"**{title}**")
            st.markdown(content)
            st.markdown("---")


def render_shortcut_hint(shortcut: str, action: str):
    """
    Render a keyboard shortcut hint.
    
    Args:
        shortcut: Keyboard shortcut (e.g., "Ctrl+S")
        action: Action description
    """
    st.markdown(f"""
    <div style="
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        color: #64748b;
        background: #f1f5f9;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
    ">
        <kbd style="
            background: #fff;
            border: 1px solid #cbd5e1;
            border-radius: 3px;
            padding: 0.1rem 0.4rem;
            font-family: monospace;
            font-size: 0.8rem;
        ">{shortcut}</kbd>
        <span>{action}</span>
    </div>
    """, unsafe_allow_html=True)


def render_step_guide(steps: list, current_step: int):
    """
    Render a step-by-step guide.
    
    Args:
        steps: List of step descriptions
        current_step: Current step index (0-based)
    """
    for i, step in enumerate(steps):
        if i < current_step:
            # Completed
            st.markdown(f"""
            <div style="
                display: flex;
                align-items: center;
                gap: 0.5rem;
                color: #10b981;
                margin: 0.5rem 0;
            ">
                <span style="font-size: 1.2rem;">✅</span>
                <span style="text-decoration: line-through; opacity: 0.7;">{i+1}. {step}</span>
            </div>
            """, unsafe_allow_html=True)
        elif i == current_step:
            # Current
            st.markdown(f"""
            <div style="
                display: flex;
                align-items: center;
                gap: 0.5rem;
                color: #3b82f6;
                font-weight: 600;
                margin: 0.5rem 0;
                background: #eff6ff;
                padding: 0.5rem;
                border-radius: 4px;
            ">
                <span style="font-size: 1.2rem;">▶️</span>
                <span>{i+1}. {step}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Future
            st.markdown(f"""
            <div style="
                display: flex;
                align-items: center;
                gap: 0.5rem;
                color: #94a3b8;
                margin: 0.5rem 0;
            ">
                <span style="font-size: 1.2rem;">⭕</span>
                <span>{i+1}. {step}</span>
            </div>
            """, unsafe_allow_html=True)


def render_floating_help_button(help_content: str, key: str = "help"):
    """
    Render a floating help button (bottom right).
    
    Args:
        help_content: Markdown content to show
        key: Unique key
    """
    st.markdown("""
    <style>
    .floating-help {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        z-index: 999;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([6, 2, 1])
        with col3:
            if st.button("❓", key=f"{key}_btn"):
                st.session_state[f"{key}_show"] = True
        
        if st.session_state.get(f"{key}_show", False):
            with st.expander("Aide", expanded=True):
                st.markdown(help_content)
                if st.button("Fermer", key=f"{key}_close"):
                    st.session_state[f"{key}_show"] = False
                    st.rerun()


# Common help content
IMPORT_HELP = """
**📥 Comment importer vos relevés :**

1. Connectez-vous à votre banque en ligne
2. Téléchargez votre relevé au format CSV
3. Sélectionnez le format de votre banque
4. Glissez-déposez le fichier ou cliquez pour sélectionner

**Formats supportés :**
- BoursoBank (auto-détection)
- Banques génériques CSV
"""

VALIDATION_HELP = """
**✅ Conseils pour la validation :**

- **Catégorie** : Choisissez la catégorie la plus appropriée
- **Membre** : Indiquez qui a effectué la dépense
- **Tags** : Ajoutez des tags pour un filtrage facile
- **Règles** : Cochez "Mémoriser" pour automatiser

Les transactions groupées partagent la même catégorie.
"""

BUDGET_HELP = """
**🎯 Gestion des budgets :**

- Définissez un budget mensuel par catégorie
- Les alertes s'affichent à 80% et 90% du budget
- Les dépenses fixes sont exclues des alertes
"""


# Export
__all__ = [
    'render_tooltip',
    'render_info_box',
    'render_contextual_help',
    'render_shortcut_hint',
    'render_step_guide',
    'render_floating_help_button',
    'IMPORT_HELP',
    'VALIDATION_HELP',
    'BUDGET_HELP',
]
