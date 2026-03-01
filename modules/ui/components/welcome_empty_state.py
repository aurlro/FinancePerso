"""
WelcomeEmptyState - Composant Empty State réutilisable pour FinancePerso

Style inspiré de FinCouple : design épuré, bordures fines, coins arrondis,
couleur d'accent dynamique selon le thème.

Usage:
    from modules.ui.components.welcome_empty_state import WelcomeEmptyState
    
    empty_state = WelcomeEmptyState()
    empty_state.render(
        title="👋 Bonjour !",
        subtitle="Bienvenue dans votre espace financier",
        message="Commencez par importer vos relevés bancaires pour visualiser vos finances.",
        primary_action=("Importer mes relevés", "pages/01_Import.py"),
        secondary_action=("Voir le guide", "docs/USER_GUIDE.md"),
        icon="💰"
    )
"""

import streamlit as st
from typing import Callable, Tuple, Optional
from modules.ui.theme import get_theme, ThemeManager


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
    
    # Les couleurs sont désormais dynamiques via theme_manager
    
    def __init__(self):
        """Initialise le composant avec les styles CSS."""
        self.theme = get_theme()
        self._inject_styles()
    
    def _inject_styles(self) -> None:
        """Injecte les styles CSS inline dans la page avec les couleurs du thème."""
        theme = self.theme
        
        # Calculer les couleurs du gradient pour l'icône
        if not theme.is_dark:
            icon_gradient_start = theme.primary_light
            icon_gradient_end = theme.primary + "40"  # 40 = 25% opacity
        else:
            icon_gradient_start = theme.primary + "30"
            icon_gradient_end = theme.primary + "10"
        
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
            background: {theme.bg_card};
            border: 1px solid {theme.border};
            border-radius: 16px;
            padding: 3rem 2.5rem;
            max-width: 480px;
            width: 100%;
            text-align: center;
            box-shadow: {theme.shadow_md};
        }}
        
        /* Conteneur d'icône */
        .empty-state-icon-wrapper {{
            width: 80px;
            height: 80px;
            margin: 0 auto 1.5rem;
            background: linear-gradient(135deg, {icon_gradient_start} 0%, {icon_gradient_end} 100%);
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
            color: {theme.text_primary};
            margin: 0 0 0.75rem 0;
            line-height: 1.3;
        }}
        
        /* Sous-titre */
        .empty-state-subtitle {{
            font-size: 1.125rem;
            font-weight: 500;
            color: {theme.text_primary};
            margin: 0 0 0.5rem 0;
        }}
        
        /* Message descriptif */
        .empty-state-message {{
            font-size: 1rem;
            color: {theme.text_secondary};
            line-height: 1.6;
            margin: 0 0 2rem 0;
        }}
        
        /* Conteneur des boutons */
        .empty-state-actions {{
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }}
        
        /* ==================== RESPONSIVE MOBILE ==================== */
        @media (max-width: 768px) {{
            .empty-state-container {{
                min-height: 50vh;
                padding: 1rem 0.5rem;
            }}
            
            .empty-state-card {{
                padding: 2rem 1.5rem;
                max-width: 100%;
                border-radius: 12px;
            }}
            
            .empty-state-icon-wrapper {{
                width: 64px;
                height: 64px;
                font-size: 2rem;
            }}
            
            .empty-state-title {{
                font-size: 1.5rem;
            }}
            
            .empty-state-subtitle {{
                font-size: 1rem;
            }}
            
            .empty-state-message {{
                font-size: 0.875rem;
                margin-bottom: 1.5rem;
            }}
        }}
        
        /* Bouton primaire */
        .btn-primary {{
            background: {theme.primary};
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
            background: {theme.primary_hover};
            transform: translateY(-1px);
            box-shadow: 0 4px 12px {theme.primary}40;
        }}
        
        /* Bouton secondaire */
        .btn-secondary {{
            background: transparent;
            color: {theme.text_secondary};
            border: 1px solid {theme.border};
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
            background: {theme.bg_page};
            border-color: {theme.text_secondary};
            color: {theme.text_primary};
        }}
        
        /* Variante compacte (pour les sections) */
        .empty-state-compact {{
            background: {theme.bg_card};
            border: 1px dashed {theme.border};
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
        
        /* Responsive - Mobile */
        @media (max-width: 768px) {{
            .empty-state-container {{
                min-height: 50vh;
                padding: 1rem 0.5rem;
            }}
            
            .empty-state-card {{
                max-width: 100% !important;
                margin: 0.5rem !important;
                padding: 2rem 1rem !important;
                border-radius: 12px;
            }}
            
            .empty-state-title {{
                font-size: 1.5rem !important;
                line-height: 1.2;
            }}
            
            .empty-state-subtitle {{
                font-size: 1rem !important;
            }}
            
            .empty-state-message {{
                font-size: 0.9375rem !important;
                margin-bottom: 1.5rem;
            }}
            
            .empty-state-icon-wrapper {{
                width: 64px;
                height: 64px;
                font-size: 2rem;
                margin-bottom: 1rem;
            }}
            
            /* Boutons empilés sur mobile */
            .empty-state-actions {{
                flex-direction: column !important;
                gap: 0.75rem !important;
            }}
            
            /* Variante compacte sur mobile */
            .empty-state-compact {{
                padding: 1.5rem 1rem;
            }}
            
            .empty-state-compact .empty-state-title {{
                font-size: 1.125rem !important;
            }}
        }}
        
        /* Petits mobiles */
        @media (max-width: 480px) {{
            .empty-state-card {{
                padding: 1.5rem 0.875rem !important;
            }}
            
            .empty-state-title {{
                font-size: 1.375rem !important;
            }}
            
            .empty-state-icon-wrapper {{
                width: 56px;
                height: 56px;
                font-size: 1.75rem;
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
            primary_action=("Importer", "pages/01_Import.py"),
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
