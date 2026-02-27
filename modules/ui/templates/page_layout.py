"""Template PageLayout - Structure standard de page.

Usage:
    from modules.ui.templates import PageLayout
    
    def render_content():
        st.write("Contenu de la page")
    
    PageLayout.render(
        title="Titre de la page",
        subtitle="Sous-titre optionnel",
        content=render_content,
        actions=[
            {"label": "Action 1", "on_click": handler1, "variant": "primary"},
            {"label": "Action 2", "on_click": handler2, "variant": "secondary"},
        ]
    )
"""

from typing import Callable, List, Optional, Any
import streamlit as st

from modules.ui.tokens import Colors, Typography, Spacing
from modules.ui.atoms import Button


class PageLayout:
    """Template de mise en page standard pour toutes les pages.
    
    Assure la cohérence visuelle entre toutes les pages de l'application.
    """
    
    @staticmethod
    def render(
        title: str,
        content: Callable,
        subtitle: Optional[str] = None,
        icon: Optional[str] = None,
        actions: Optional[List[dict]] = None,
        full_width: bool = False,
    ) -> None:
        """Rend une page avec la structure standard.
        
        Args:
            title: Titre principal de la page
            content: Fonction qui rend le contenu principal
            subtitle: Sous-titre optionnel
            icon: Emoji/icône optionnelle
            actions: Liste d'actions [{"label": str, "on_click": callable, "variant": str}]
            full_width: Utiliser toute la largeur
        """
        # Header avec titre
        header_cols = st.columns([3, 1] if actions else [1])
        
        with header_cols[0]:
            # Titre avec icône
            title_display = f"{icon} {title}" if icon else title
            st.title(title_display)
            
            # Sous-titre
            if subtitle:
                st.markdown(
                    f'<p style="color: {Colors.SLATE_500}; margin-top: -10px;">{subtitle}</p>',
                    unsafe_allow_html=True
                )
        
        # Actions dans le header
        if actions:
            with header_cols[1]:
                cols = st.columns(len(actions))
                for i, action in enumerate(actions):
                    with cols[i]:
                        variant = action.get("variant", "primary")
                        label = action["label"]
                        on_click = action["on_click"]
                        
                        if variant == "primary":
                            Button.primary(label, key=f"action_{i}", on_click=on_click)
                        elif variant == "secondary":
                            Button.secondary(label, key=f"action_{i}", on_click=on_click)
                        elif variant == "danger":
                            Button.danger(label, key=f"action_{i}", on_click=on_click)
        
        # Ligne de séparation
        st.markdown("---")
        
        # Contenu principal
        if full_width:
            content()
        else:
            with st.container():
                content()
    
    @staticmethod
    def render_section(
        title: str,
        content: Callable,
        collapsible: bool = False,
        default_expanded: bool = True,
    ) -> None:
        """Rend une section de page.
        
        Args:
            title: Titre de la section
            content: Fonction qui rend le contenu
            collapsible: Si True, utilise un expander
            default_expanded: État initial si collapsible
        """
        if collapsible:
            with st.expander(title, expanded=default_expanded):
                content()
        else:
            st.subheader(title)
            content()
    
    @staticmethod
    def render_two_column(
        left_content: Callable,
        right_content: Callable,
        left_ratio: int = 1,
        right_ratio: int = 1,
    ) -> None:
        """Rend un layout deux colonnes.
        
        Args:
            left_content: Fonction contenu gauche
            right_content: Fonction contenu droit
            left_ratio: Ratio colonne gauche
            right_ratio: Ratio colonne droite
        """
        left_col, right_col = st.columns([left_ratio, right_ratio])
        
        with left_col:
            left_content()
        
        with right_col:
            right_content()
    
    @staticmethod
    def render_three_column(
        left_content: Callable,
        center_content: Callable,
        right_content: Callable,
    ) -> None:
        """Rend un layout trois colonnes égales."""
        left_col, center_col, right_col = st.columns(3)
        
        with left_col:
            left_content()
        
        with center_col:
            center_content()
        
        with right_col:
            right_content()
