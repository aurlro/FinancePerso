"""
Utilitaires de responsive design pour FinancePerso.

Ce module fournit des fonctions pour détecter et adapter l'interface
aux différentes tailles d'écran (mobile, tablette, desktop).
"""

import streamlit as st


def is_mobile() -> bool:
    """
    Détecte approximativement si on est sur mobile.
    
    Streamlit ne donne pas directement la taille de l'écran.
    Cette fonction utilise une heuristique basée sur session_state
    qui peut être mise à jour par du JavaScript côté client.
    
    Par défaut, retourne False (desktop) si non déterminé.
    
    Returns:
        True si l'appareil est probablement un mobile
    """
    # Utiliser une valeur stockée dans session_state si disponible
    # La largeur peut être définie par du JS côté client
    viewport_width = st.session_state.get("viewport_width", 1200)
    return viewport_width < 768


def get_viewport_width() -> int:
    """
    Retourne la largeur de viewport estimée.
    
    Returns:
        Largeur en pixels (défaut: 1200 si non déterminée)
    """
    return st.session_state.get("viewport_width", 1200)


def get_column_config() -> dict:
    """
    Retourne la configuration de colonnes adaptée au viewport.
    
    Returns:
        Dict avec les configurations pour différents layouts
    """
    if is_mobile():
        return {
            "kpi_columns": 1,
            "full_width": True,
            "button_layout": "vertical",
            "card_padding": "1rem",
            "font_scale": 0.875
        }
    return {
        "kpi_columns": 2,
        "full_width": False,
        "button_layout": "horizontal",
        "card_padding": "1.25rem",
        "font_scale": 1.0
    }


def inject_viewport_detector() -> None:
    """
    Injecte du JavaScript pour détecter la taille de l'écran.
    
    À appeler au début de chaque page pour activer la détection mobile.
    Met à jour st.session_state["viewport_width"] avec la largeur réelle.
    """
    st.markdown("""
    <script>
        // Mettre à jour le viewport_width dans session_state
        const updateViewportWidth = () => {
            const width = window.innerWidth;
            // Utiliser l'API Streamlit pour communiquer avec le serveur
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: width
            }, '*');
        };
        
        // Initial + resize
        updateViewportWidth();
        window.addEventListener('resize', updateViewportWidth);
    </script>
    """, unsafe_allow_html=True)


def get_responsive_styles() -> str:
    """
    Retourne les styles CSS de base pour le responsive design.
    
    Returns:
        String CSS à injecter avec st.markdown(..., unsafe_allow_html=True)
    """
    return """
    <style>
    /* Styles de base pour mobile */
    @media (max-width: 768px) {
        /* Réduire les padding globaux */
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
        }
        
        /* Titres plus petits sur mobile */
        h1 {
            font-size: 1.5rem !important;
        }
        
        h2 {
            font-size: 1.25rem !important;
        }
        
        h3 {
            font-size: 1.125rem !important;
        }
        
        /* Boutons pleine largeur sur mobile */
        .stButton button {
            width: 100% !important;
        }
        
        /* Grids en colonne unique */
        .responsive-grid {
            grid-template-columns: 1fr !important;
        }
        
        /* Cartes moins de padding */
        .mobile-compact {
            padding: 1rem !important;
        }
    }
    
    /* Tablette */
    @media (min-width: 769px) and (max-width: 1024px) {
        .responsive-grid {
            grid-template-columns: repeat(2, 1fr) !important;
        }
    }
    
    /* Desktop */
    @media (min-width: 1025px) {
        .responsive-grid {
            grid-template-columns: repeat(2, 1fr) !important;
        }
    }
    </style>
    """
