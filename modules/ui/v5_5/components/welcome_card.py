"""Welcome Card - Composant d'accueil V5.5.

Card centrée avec icône dans cercle coloré, inspirée des maquettes FinCouple.

Usage:
    from modules.ui.v5_5.components.welcome_card import WelcomeCard

    WelcomeCard.render(
        on_primary=lambda: st.switch_page("pages/01_Import.py"),
        on_secondary=lambda: show_guide()
    )
"""

from collections.abc import Callable

import streamlit as st

from modules.ui.atoms import Button


class WelcomeCard:
    """Card d'accueil centrée selon maquette V5.5.

    Affiche une card blanche centrée avec:
    - Icône dans un cercle coloré (vert émeraude)
    - Titre "👋 Bonjour !"
    - Sous-titre "Bienvenue dans votre espace financier"
    - Description
    - Deux boutons : Primaire (Importer) + Secondaire (Guide)

    Usage:
        WelcomeCard.render(
            on_primary=import_handler,
            on_secondary=guide_handler,
            user_name="Alex"  # Optionnel
        )
    """

    @staticmethod
    def render(
        on_primary: Callable | None = None,
        on_secondary: Callable | None = None,
        user_name: str | None = None,
        primary_text: str = "▶️ Importer mes relevés",
        secondary_text: str = "📖 Voir le guide",
        key_prefix: str = "welcome",
    ) -> None:
        """Rend la card d'accueil centrée.

        Args:
            on_primary: Callback bouton primaire (Importer)
            on_secondary: Callback bouton secondaire (Guide)
            user_name: Nom de l'utilisateur (affiché dans le titre)
            primary_text: Texte du bouton primaire
            secondary_text: Texte du bouton secondaire
            key_prefix: Préfixe pour les clés Streamlit
        """

        # CSS personnalisé pour la card
        st.markdown(
            """
        <style>
        .v5-welcome-container {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 70vh;
            padding: 2rem;
        }
        
        .v5-welcome-card {
            background: #FFFFFF;
            border-radius: 16px;
            padding: 3rem 2.5rem;
            text-align: center;
            max-width: 480px;
            width: 100%;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 
                        0 2px 4px -2px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        .v5-welcome-card:hover {
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 
                        0 4px 6px -4px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }
        
        .v5-welcome-icon-wrapper {
            margin-bottom: 1.5rem;
        }
        
        .v5-welcome-icon-circle {
            width: 80px;
            height: 80px;
            background: #D1FAE5;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
            margin: 0 auto;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
        }
        
        .v5-welcome-title {
            font-size: 2rem;
            font-weight: 700;
            color: #1F2937;
            margin-bottom: 0.75rem;
            letter-spacing: -0.025em;
        }
        
        .v5-welcome-subtitle {
            font-size: 1.125rem;
            font-weight: 500;
            color: #374151;
            margin-bottom: 0.75rem;
        }
        
        .v5-welcome-description {
            font-size: 1rem;
            color: #6B7280;
            line-height: 1.6;
            margin-bottom: 2rem;
            max-width: 360px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .v5-welcome-actions {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            max-width: 280px;
            margin: 0 auto;
        }
        </style>
        
        <div class="v5-welcome-container">
            <div class="v5-welcome-card">
                <div class="v5-welcome-icon-wrapper">
                    <div class="v5-welcome-icon-circle">💰</div>
                </div>
                
                <h1 class="v5-welcome-title">
                    👋 Bonjour{f', {user_name}' if user_name else ''} !
                </h1>
                
                <div class="v5-welcome-subtitle">
                    Bienvenue dans votre espace financier
                </div>
                
                <div class="v5-welcome-description">
                    Commencez par importer vos relevés bancaires pour 
                    visualiser vos finances, suivre vos budgets et atteindre 
                    vos objectifs d'épargne.
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Boutons (en dessous de la card, mais toujours centrés)
        # On utilise des colonnes pour centrer les boutons
        col_left, col_center, col_right = st.columns([1, 2, 1])

        with col_center:
            # Bouton primaire (Importer)
            if Button.primary(
                label=primary_text,
                key=f"{key_prefix}_primary",
                on_click=on_primary,
                use_container_width=True,
            ):
                pass  # Le callback est géré par on_click

            # Petit espace entre les boutons
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

            # Bouton secondaire (Guide)
            if Button.secondary(
                label=secondary_text,
                key=f"{key_prefix}_secondary",
                on_click=on_secondary,
                use_container_width=True,
            ):
                pass  # Le callback est géré par on_click

    @classmethod
    def render_with_guide_modal(
        cls,
        on_primary: Callable | None = None,
        user_name: str | None = None,
    ) -> None:
        """Rend la card avec modal guide intégré.

        Cette variante gère automatiquement l'affichage du guide
        dans un dialog modal.

        Args:
            on_primary: Callback bouton importer
            user_name: Nom de l'utilisateur
        """
        # Vérifier si on doit afficher le guide
        if st.session_state.get("show_welcome_guide", False):
            cls._render_guide_modal()
            return

        # Rendre la card normale
        cls.render(
            on_primary=on_primary,
            on_secondary=lambda: st.session_state.update(show_welcome_guide=True),
            user_name=user_name,
        )

    @staticmethod
    def _render_guide_modal() -> None:
        """Affiche le guide d'onboarding dans un modal."""

        @st.dialog("📖 Guide de démarrage")
        def guide_dialog():
            st.markdown(
                """
            ### Comment utiliser FinancePerso
            
            **1. 📥 Importez vos relevés**
            
            Téléchargez votre relevé bancaire au format CSV depuis 
            votre espace client banque.
            
            **2. 🤖 Laissez l'IA catégoriser**
            
            Notre intelligence artificielle analyse automatiquement 
            vos transactions et leur attribue une catégorie.
            
            **3. ✏️ Validez les suggestions**
            
            Vérifiez et corrigez si besoin les catégories proposées. 
            Plus vous validez, plus l'IA devient précise !
            
            **4. 📊 Visualisez vos finances**
            
            Consultez votre dashboard, suivez vos budgets et 
            atteignez vos objectifs d'épargne.
            """
            )

            if st.button("✅ J'ai compris", use_container_width=True):
                st.session_state.show_welcome_guide = False
                st.rerun()

        guide_dialog()


def render_welcome_simple():
    """Version simplifiée pour test rapide.

    Usage:
        from modules.ui.v5_5.components.welcome_card import render_welcome_simple
        render_welcome_simple()
    """
    WelcomeCard.render(
        on_primary=lambda: st.success("Navigation vers Import..."),
        on_secondary=lambda: st.info("Affichage du guide..."),
    )
