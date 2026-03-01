"""
WelcomeEmptyState - Composant Empty State réutilisable pour FinancePerso

Style inspiré de FinCouple : design épuré, bordures fines, coins arrondis,
couleur d'accent vert menthe (#10B981).

Usage:
    from modules.ui.molecules.welcome_empty_state import WelcomeEmptyState
    
    empty_state = WelcomeEmptyState()
    empty_state.render(
        title="👋 Bonjour !",
        subtitle="Bienvenue dans votre espace financier",
        message="Commencez par importer vos relevés bancaires pour visualiser vos finances.",
        primary_action=("Importer mes relevés", "pages/1_Opérations.py"),
        secondary_action=("Voir le guide", "docs/USER_GUIDE.md"),
        icon="💰"
    )
"""

import streamlit as st
from typing import Callable, Tuple, Optional


class WelcomeEmptyState:
    """
    Composant Empty State engageant pour les pages sans données.
    
    Design :
    - Carte centrale avec bordure fine et ombre légère
    - Icône illustrative en grand format
    - Titre accueillant avec emoji
    - Sous-titre explicatif
    - Boutons d'action primaire et secondaire
    """
    
    # Couleurs du Design System
    ACCENT_COLOR = "#10B981"  # Vert menthe
    ACCENT_HOVER = "#059669"
    TEXT_PRIMARY = "#1F2937"  # Gris foncé
    TEXT_SECONDARY = "#6B7280"  # Gris moyen
    BORDER_COLOR = "#E5E7EB"  # Gris clair
    BG_CARD = "#FFFFFF"
    BG_PAGE = "#F9FAFB"
    
    def __init__(self):
        """Initialise le composant avec les styles CSS."""
        self._inject_styles()
    
    def _inject_styles(self) -> None:
        """Injecte les styles CSS inline dans la page."""
        styles = f"""
        <style>
        /* Conteneur principal centré */
        .empty-state-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 60vh;
            padding: 2rem 1rem;
        }}
        
        /* Carte principale */
        .empty-state-card {{
            background: {self.BG_CARD};
            border: 1px solid {self.BORDER_COLOR};
            border-radius: 16px;
            padding: 3rem 2.5rem;
            max-width: 480px;
            width: 100%;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 
                        0 4px 12px rgba(0, 0, 0, 0.05);
        }}
        
        /* Conteneur d'icône */
        .empty-state-icon-wrapper {{
            width: 80px;
            height: 80px;
            margin: 0 auto 1.5rem;
            background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
        }}
        
        /* Titre */
        .empty-state-title {{
            font-size: 1.75rem;
            font-weight: 700;
            color: {self.TEXT_PRIMARY};
            margin: 0 0 0.75rem 0;
            line-height: 1.3;
        }}
        
        /* Sous-titre */
        .empty-state-subtitle {{
            font-size: 1.125rem;
            font-weight: 500;
            color: {self.TEXT_PRIMARY};
            margin: 0 0 0.5rem 0;
        }}
        
        /* Message descriptif */
        .empty-state-message {{
            font-size: 1rem;
            color: {self.TEXT_SECONDARY};
            line-height: 1.6;
            margin: 0 0 2rem 0;
        }}
        
        /* Conteneur des boutons */
        .empty-state-actions {{
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }}
        
        /* Bouton primaire */
        .btn-primary {{
            background: {self.ACCENT_COLOR};
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.875rem 1.5rem;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }}
        
        .btn-primary:hover {{
            background: {self.ACCENT_HOVER};
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        }}
        
        /* Bouton secondaire */
        .btn-secondary {{
            background: transparent;
            color: {self.TEXT_SECONDARY};
            border: 1px solid {self.BORDER_COLOR};
            border-radius: 10px;
            padding: 0.875rem 1.5rem;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }}
        
        .btn-secondary:hover {{
            background: {self.BG_PAGE};
            border-color: {self.TEXT_SECONDARY};
            color: {self.TEXT_PRIMARY};
        }}
        
        /* Variante compacte (pour les sections) */
        .empty-state-compact {{
            background: {self.BG_CARD};
            border: 1px dashed {self.BORDER_COLOR};
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
        }}
        
        .empty-state-compact .empty-state-icon-wrapper {{
            width: 56px;
            height: 56px;
            font-size: 1.75rem;
            margin-bottom: 1rem;
        }}
        
        .empty-state-compact .empty-state-title {{
            font-size: 1.25rem;
        }}
        
        .empty-state-compact .empty-state-message {{
            font-size: 0.9375rem;
            margin-bottom: 1.25rem;
        }}
        
        /* Animation d'entrée */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .empty-state-card {{
            animation: fadeInUp 0.5s ease-out;
        }}
        
        /* Responsive */
        @media (max-width: 640px) {{
            .empty-state-card {{
                padding: 2rem 1.5rem;
            }}
            
            .empty-state-title {{
                font-size: 1.5rem;
            }}
            
            .empty-state-icon-wrapper {{
                width: 64px;
                height: 64px;
                font-size: 2rem;
            }}
        }}
        </style>
        """
        st.markdown(styles, unsafe_allow_html=True)
    
    def render(
        self,
        title: str = "👋 Bonjour !",
        subtitle: Optional[str] = "Bienvenue dans votre espace financier",
        message: str = "Commencez par importer vos données pour visualiser vos finances.",
        primary_action: Optional[Tuple[str, str]] = None,
        secondary_action: Optional[Tuple[str, str]] = None,
        icon: str = "💰",
        compact: bool = False,
        on_primary_click: Optional[Callable] = None,
        on_secondary_click: Optional[Callable] = None,
    ) -> None:
        """
        Affiche l'empty state.
        
        Args:
            title: Titre principal (avec emoji recommandé)
            subtitle: Sous-titre court
            message: Message descriptif
            primary_action: Tuple (label, url) pour le bouton principal
            secondary_action: Tuple (label, url) pour le bouton secondaire
            icon: Emoji ou icône à afficher
            compact: True pour la version compacte (section)
            on_primary_click: Callback pour le bouton primaire (alternative à url)
            on_secondary_click: Callback pour le bouton secondaire
        """
        card_class = "empty-state-compact" if compact else "empty-state-card"
        
        # HTML de la carte
        html = f"""
        <div class="empty-state-container">
            <div class="{card_class}">
                <div class="empty-state-icon-wrapper">
                    {icon}
                </div>
                <h1 class="empty-state-title">{title}</h1>
                {f'<p class="empty-state-subtitle">{subtitle}</p>' if subtitle else ''}
                <p class="empty-state-message">{message}</p>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
        
        # Boutons (en dehors du HTML pour gérer les callbacks)
        if primary_action or secondary_action or on_primary_click or on_secondary_click:
            # Utiliser des colonnes pour centrer les boutons
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if compact:
                    # Version compacte : boutons côte à côte
                    btn_col1, btn_col2 = st.columns(2)
                    
                    with btn_col1:
                        if on_primary_click:
                            if st.button(
                                f"▶️ {primary_action[0] if primary_action else 'Commencer'}",
                                type="primary",
                                use_container_width=True,
                                key="empty_primary_compact"
                            ):
                                on_primary_click()
                        elif primary_action:
                            st.link_button(
                                f"▶️ {primary_action[0]}",
                                primary_action[1],
                                type="primary",
                                use_container_width=True
                            )
                    
                    with btn_col2:
                        if on_secondary_click:
                            if st.button(
                                f"📖 {secondary_action[0] if secondary_action else 'Guide'}",
                                use_container_width=True,
                                key="empty_secondary_compact"
                            ):
                                on_secondary_click()
                        elif secondary_action:
                            st.link_button(
                                f"📖 {secondary_action[0]}",
                                secondary_action[1],
                                use_container_width=True
                            )
                else:
                    # Version complète : boutons empilés
                    if on_primary_click:
                        if st.button(
                            f"▶️ {primary_action[0] if primary_action else 'Commencer'}",
                            type="primary",
                            use_container_width=True,
                            key="empty_primary_full"
                        ):
                            on_primary_click()
                    elif primary_action:
                        st.link_button(
                            f"▶️ {primary_action[0]}",
                            primary_action[1],
                            type="primary",
                            use_container_width=True
                        )
                    
                    if on_secondary_click:
                        if st.button(
                            f"📖 {secondary_action[0] if secondary_action else 'Guide'}",
                            use_container_width=True,
                            key="empty_secondary_full"
                        ):
                            on_secondary_click()
                    elif secondary_action:
                        st.link_button(
                            f"📖 {secondary_action[0]}",
                            secondary_action[1],
                            use_container_width=True
                        )


# Fonction helper pour usage rapide
def welcome_empty_state(
    title: str = "👋 Bonjour !",
    subtitle: Optional[str] = "Bienvenue dans votre espace financier",
    message: str = "Commencez par importer vos données pour visualiser vos finances.",
    primary_action: Optional[Tuple[str, str]] = None,
    secondary_action: Optional[Tuple[str, str]] = None,
    icon: str = "💰",
    compact: bool = False,
    on_primary_click: Optional[Callable] = None,
    on_secondary_click: Optional[Callable] = None,
) -> None:
    """
    Fonction helper pour afficher un empty state rapidement.
    
    Usage:
        welcome_empty_state(
            title="👋 Bonjour !",
            message="Importez vos relevés pour commencer.",
            primary_action=("Importer", "pages/1_Opérations.py"),
        )
    """
    component = WelcomeEmptyState()
    component.render(
        title=title,
        subtitle=subtitle,
        message=message,
        primary_action=primary_action,
        secondary_action=secondary_action,
        icon=icon,
        compact=compact,
        on_primary_click=on_primary_click,
        on_secondary_click=on_secondary_click,
    )


# Démo du composant
if __name__ == "__main__":
    st.set_page_config(
        page_title="Demo - Welcome Empty State",
        page_icon="🎨",
        layout="centered"
    )
    
    st.sidebar.title("🎨 Variantes")
    variant = st.sidebar.radio(
        "Choisir la variante:",
        ["Complète", "Compacte", "Personnalisée"]
    )
    
    if variant == "Complète":
        welcome_empty_state(
            title="👋 Bonjour !",
            subtitle="Bienvenue dans votre espace financier",
            message="Commencez par importer vos relevés bancaires pour visualiser vos finances, suivre vos budgets et atteindre vos objectifs d'épargne.",
            primary_action=("Importer mes relevés", "#"),
            secondary_action=("Voir le guide", "#"),
            icon="💰"
        )
    
    elif variant == "Compacte":
        welcome_empty_state(
            title="Aucune transaction",
            subtitle=None,
            message="Importez vos relevés pour voir l'analyse.",
            primary_action=("Importer", "#"),
            icon="📊",
            compact=True
        )
    
    else:
        st.sidebar.markdown("---")
        custom_title = st.sidebar.text_input("Titre", "🚀 C'est parti !")
        custom_subtitle = st.sidebar.text_input("Sous-titre", "Votre aventure financière commence")
        custom_message = st.sidebar.text_area("Message", "Personnalisez ce message selon vos besoins.")
        custom_icon = st.sidebar.selectbox("Icône", ["💰", "📊", "🎯", "🚀", "✨", "📈"])
        
        welcome_empty_state(
            title=custom_title,
            subtitle=custom_subtitle,
            message=custom_message,
            primary_action=("Action principale", "#"),
            secondary_action=("Action secondaire", "#"),
            icon=custom_icon
        )
