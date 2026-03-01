"""Molecule Card - Carte unifiée pour tout l'application.

Usage:
    from modules.ui.molecules import Card
    
    # Carte simple
    Card.render(title="Titre", content="Contenu")
    
    # Carte métrique
    Card.metric(
        title="Total",
        value="1 234 €",
        trend="+12%",
        trend_up=True
    )
    
    # Carte action
    Card.action(
        title="Action",
        description="Description",
        button_text="Cliquer",
        on_click=handler
    )
"""

from collections.abc import Callable
from enum import Enum
from typing import Any

import streamlit as st

from modules.ui.atoms import Badge, Button, Icon
from modules.ui.tokens import GRADIENTS, BorderRadius, Colors, Shadow, Spacing, Typography


class CardVariant(str, Enum):
    """Variantes de cartes."""
    DEFAULT = "default"
    METRIC = "metric"
    ACTION = "action"
    ALERT = "alert"
    EMPTY = "empty"
    INFO = "info"


class Card:
    """Carte unifiée - Composant central du Design System.
    
    Remplace TOUTES les fonctions de cartes dispersées dans l'application :
    - create_card() du design_system.py
    - render_empty_state() de assistant/components.py
    - render_anomaly_card() de assistant/components.py
    - render_quick_action_card() de assistant/components.py
    - etc.
    
    Usage:
        # Carte basique
        Card.render("Titre", "Contenu de la carte")
        
        # Avec icône et badge
        Card.render(
            title="Titre",
            content="Contenu",
            icon="💰",
            badge=("PRO", "success")
        )
        
        # Carte action cliquable
        Card.action(
            title="Importer",
            description="Importer des transactions",
            icon="📥",
            button_text="Importer",
            on_click=import_handler
        )
    """
    
    @staticmethod
    def render(
        title: str | None = None,
        content: Any | None = None,
        icon: str | None = None,
        badge: tuple[str, str] | None = None,  # (text, variant)
        footer: str | None = None,
        key: str | None = None,
        variant: CardVariant = CardVariant.DEFAULT,
        on_click: Callable | None = None,
        clickable: bool = False,
    ) -> bool:
        """Rend une carte standardisée.
        
        Args:
            title: Titre de la carte
            content: Contenu (texte, HTML, ou composant Streamlit)
            icon: Emoji/icône optionnelle
            badge: Tuple (texte, variante) pour un badge
            footer: Texte de pied de carte
            key: Clé unique Streamlit
            variant: Style de carte
            on_click: Callback au clic (si clickable=True)
            clickable: Rend la carte cliquable entièrement
        
        Returns:
            True si cliquée (quand clickable=True)
        """
        clicked = False
        
        # Styles selon la variante
        if variant == CardVariant.ALERT:
            border_color = Colors.WARNING
            bg_color = Colors.WARNING_BG
        elif variant == CardVariant.INFO:
            border_color = Colors.INFO
            bg_color = Colors.INFO_BG
        elif variant == CardVariant.EMPTY:
            border_color = Colors.SLATE_200
            bg_color = Colors.SLATE_50
        else:
            border_color = Colors.SLATE_200
            bg_color = Colors.WHITE
        
        # Construction du header
        header_html = ""
        if icon or title or badge:
            header_parts = []
            
            if icon:
                header_parts.append(f'<span style="font-size: 1.5rem;">{icon}</span>')
            
            if title:
                title_style = f"""
                    font-size: {Typography.SIZE_LG};
                    font-weight: {Typography.WEIGHT_SEMIBOLD};
                    color: {Colors.SLATE_900};
                    margin: 0;
                """
                header_parts.append(f'<span style="{title_style}">{title}</span>')
            
            if badge:
                badge_text, badge_variant = badge
                # Le badge sera rendu après via st.markdown
                pass
            
            if header_parts:
                flex_style = """
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    margin-bottom: 12px;
                """
                header_html = f'<div style="{flex_style}">{" ".join(header_parts)}</div>'
        
        # Container principal
        container_style = f"""
            background-color: {bg_color};
            border: 1px solid {border_color};
            border-radius: {BorderRadius.LG};
            padding: {Spacing.MD};
            box-shadow: {Shadow.SM};
            transition: all 200ms ease-in-out;
            {"cursor: pointer;" if clickable else ""}
            {"&:hover { box-shadow: " + Shadow.MD + "; }" if clickable else ""}
        """
        
        with st.container():
            st.markdown(f'<div style="{container_style}">', unsafe_allow_html=True)
            
            # Header
            if header_html:
                st.markdown(header_html, unsafe_allow_html=True)
            
            # Badge séparé (pour éviter les problèmes de nesting HTML)
            if badge:
                badge_text, badge_variant = badge
                badge_method = getattr(Badge, badge_variant, Badge.default)
                badge_method(badge_text)
            
            # Contenu
            if content:
                if isinstance(content, str):
                    st.markdown(f'<div style="color: {Colors.SLATE_700}; font-size: {Typography.SIZE_BASE};">{content}</div>', unsafe_allow_html=True)
                else:
                    # Si c'est un callable (fonction de rendu Streamlit)
                    if callable(content):
                        content()
                    else:
                        st.write(content)
            
            # Footer
            if footer:
                footer_style = f"""
                    margin-top: {Spacing.SM};
                    padding-top: {Spacing.SM};
                    border-top: 1px solid {Colors.SLATE_200};
                    font-size: {Typography.SIZE_SM};
                    color: {Colors.SLATE_500};
                """
                st.markdown(f'<div style="{footer_style}">{footer}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Gestion du clic
            if clickable and key:
                clicked = st.button(
                    "",
                    key=f"card_click_{key}",
                    on_click=on_click,
                    use_container_width=True,
                    help="Cliquer pour voir plus"
                )
        
        return clicked
    
    @classmethod
    def metric(
        cls,
        title: str,
        value: str,
        subtitle: str | None = None,
        trend: str | None = None,
        trend_up: bool | None = None,
        icon: str | None = None,
        key: str | None = None,
    ) -> None:
        """Carte de métrique avec valeur, tendance et icône.
        
        Args:
            title: Libellé de la métrique
            value: Valeur à afficher (ex: "1 234 €")
            subtitle: Texte secondaire optionnel
            trend: Texte de tendance (ex: "+12%")
            trend_up: True si tendance positive, False si négative
            icon: Emoji/icône optionnelle
            key: Clé unique Streamlit
        
        Usage:
            Card.metric(
                title="Dépenses",
                value="1 234 €",
                trend="+12%",
                trend_up=False,
                icon="💸"
            )
        """
        # Couleur de tendance
        if trend_up is not None:
            trend_color = Colors.SUCCESS if trend_up else Colors.DANGER
            trend_icon = "↑" if trend_up else "↓"
        else:
            trend_color = Colors.SLATE_500
            trend_icon = "→"
        
        # Construction
        container_style = f"""
            background: {GRADIENTS["card"]};
            border: 1px solid {Colors.SLATE_200};
            border-radius: {BorderRadius.LG};
            padding: {Spacing.MD};
            box-shadow: {Shadow.SM};
        """
        
        with st.container():
            st.markdown(f'<div style="{container_style}">', unsafe_allow_html=True)
            
            # Header avec icône
            if icon:
                st.markdown(f'<div style="font-size: 2rem; margin-bottom: 8px;">{icon}</div>', unsafe_allow_html=True)
            
            # Titre
            st.markdown(
                f'<div style="font-size: {Typography.SIZE_SM}; color: {Colors.SLATE_500}; margin-bottom: 4px;">{title}</div>',
                unsafe_allow_html=True
            )
            
            # Valeur principale
            st.markdown(
                f'<div style="font-size: {Typography.SIZE_2XL}; font-weight: {Typography.WEIGHT_BOLD}; color: {Colors.SLATE_900};">{value}</div>',
                unsafe_allow_html=True
            )
            
            # Tendance
            if trend:
                st.markdown(
                    f'<div style="font-size: {Typography.SIZE_SM}; color: {trend_color}; margin-top: 4px;">{trend_icon} {trend}</div>',
                    unsafe_allow_html=True
                )
            
            # Sous-titre
            if subtitle:
                st.markdown(
                    f'<div style="font-size: {Typography.SIZE_XS}; color: {Colors.SLATE_400}; margin-top: 4px;">{subtitle}</div>',
                    unsafe_allow_html=True
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    @classmethod
    def action(
        cls,
        title: str,
        description: str,
        button_text: str,
        on_click: Callable,
        icon: str | None = None,
        button_icon: str | None = None,
        key: str | None = None,
        variant: str = "primary",
    ) -> None:
        """Carte avec action (bouton).
        
        Args:
            title: Titre de la carte
            description: Description de l'action
            button_text: Texte du bouton
            on_click: Callback du bouton
            icon: Icône de la carte
            button_icon: Icône du bouton
            key: Clé unique Streamlit
            variant: Variante du bouton (primary, secondary)
        
        Usage:
            Card.action(
                title="Importer",
                description="Importez vos transactions",
                button_text="Importer",
                on_click=import_handler
            )
        """
        container_style = f"""
            background-color: {Colors.WHITE};
            border: 1px solid {Colors.SLATE_200};
            border-radius: {BorderRadius.LG};
            padding: {Spacing.MD};
            box-shadow: {Shadow.SM};
        """
        
        with st.container():
            st.markdown(f'<div style="{container_style}">', unsafe_allow_html=True)
            
            # Header avec icône
            header_parts = []
            if icon:
                header_parts.append(f'<span style="font-size: 1.5rem;">{icon}</span>')
            header_parts.append(f'<span style="font-size: {Typography.SIZE_LG}; font-weight: {Typography.WEIGHT_SEMIBOLD}; color: {Colors.SLATE_900};">{title}</span>')
            
            header_html = f'<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">{" ".join(header_parts)}</div>'
            st.markdown(header_html, unsafe_allow_html=True)
            
            # Description
            st.markdown(
                f'<div style="font-size: {Typography.SIZE_BASE}; color: {Colors.SLATE_600}; margin-bottom: {Spacing.MD};">{description}</div>',
                unsafe_allow_html=True
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Bouton
            if variant == "primary":
                Button.primary(
                    button_text,
                    key=key,
                    on_click=on_click,
                    icon=button_icon
                )
            else:
                Button.secondary(
                    button_text,
                    key=key,
                    on_click=on_click,
                    icon=button_icon
                )
    
    @classmethod
    def alert(
        cls,
        title: str,
        message: str,
        severity: str = "warning",  # info, success, warning, error
        icon: str | None = None,
        action_text: str | None = None,
        on_action: Callable | None = None,
        key: str | None = None,
    ) -> None:
        """Carte d'alerte/notification.
        
        Args:
            title: Titre de l'alerte
            message: Message détaillé
            severity: Niveau de sévérité
            icon: Icône personnalisée
            action_text: Texte du bouton d'action optionnel
            on_action: Callback du bouton d'action
            key: Clé unique Streamlit
        
        Usage:
            Card.alert(
                title="Attention",
                message="Votre budget est dépassé",
                severity="warning",
                action_text="Voir",
                on_action=show_budget
            )
        """
        # Mapping sévérité vers couleurs et icônes
        severity_map = {
            "info": (Colors.INFO, Colors.INFO_BG, Colors.INFO_DARK, Icon.INFO),
            "success": (Colors.SUCCESS, Colors.SUCCESS_BG, Colors.SUCCESS_DARK, Icon.SUCCESS),
            "warning": (Colors.WARNING, Colors.WARNING_BG, Colors.WARNING_DARK, Icon.WARNING),
            "error": (Colors.DANGER, Colors.DANGER_BG, Colors.DANGER_DARK, Icon.ERROR),
        }
        
        border_color, bg_color, text_color, default_icon = severity_map.get(
            severity,
            severity_map["info"]
        )
        
        icon_to_use = icon or default_icon
        
        container_style = f"""
            background-color: {bg_color};
            border-left: 4px solid {border_color};
            border-radius: {BorderRadius.MD};
            padding: {Spacing.MD};
            margin-bottom: {Spacing.SM};
        """
        
        with st.container():
            st.markdown(f'<div style="{container_style}">', unsafe_allow_html=True)
            
            # Header
            header_html = f"""
            <div style="display: flex; align-items: flex-start; gap: 12px;">
                <span style="font-size: 1.25rem; color: {border_color};">{icon_to_use}</span>
                <div style="flex: 1;">
                    <div style="font-weight: {Typography.WEIGHT_SEMIBOLD}; color: {text_color}; margin-bottom: 4px;">{title}</div>
                    <div style="color: {Colors.SLATE_700}; font-size: {Typography.SIZE_SM};">{message}</div>
                </div>
            </div>
            """
            st.markdown(header_html, unsafe_allow_html=True)
            
            # Action button
            if action_text and on_action and key:
                st.markdown(f'<div style="margin-top: {Spacing.SM}; margin-left: 32px;">', unsafe_allow_html=True)
                if severity == "error":
                    Button.danger(action_text, key=f"{key}_action", on_click=on_action)
                else:
                    Button.primary(action_text, key=f"{key}_action", on_click=on_action)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    @classmethod
    def empty(
        cls,
        title: str,
        message: str,
        icon: str = "📭",
        action_text: str | None = None,
        on_action: Callable | None = None,
        key: str | None = None,
    ) -> None:
        """Carte d'état vide.
        
        Remplace toutes les fonctions render_empty_state_*.
        
        Args:
            title: Titre de l'état vide
            message: Message explicatif
            icon: Emoji/icône (défaut: 📭)
            action_text: Texte du bouton d'action optionnel
            on_action: Callback du bouton
            key: Clé unique Streamlit
        
        Usage:
            Card.empty(
                title="Aucune transaction",
                message="Commencez par importer vos transactions",
                icon="📄",
                action_text="Importer",
                on_action=import_handler
            )
        """
        container_style = f"""
            background: linear-gradient(135deg, {Colors.SLATE_50} 0%, {Colors.WHITE} 100%);
            border: 2px dashed {Colors.SLATE_300};
            border-radius: {BorderRadius.LG};
            padding: {Spacing.XL};
            text-align: center;
        """
        
        with st.container():
            st.markdown(f'<div style="{container_style}">', unsafe_allow_html=True)
            
            # Icône
            st.markdown(f'<div style="font-size: 3rem; margin-bottom: {Spacing.SM};">{icon}</div>', unsafe_allow_html=True)
            
            # Titre
            st.markdown(
                f'<div style="font-size: {Typography.SIZE_XL}; font-weight: {Typography.WEIGHT_SEMIBOLD}; color: {Colors.SLATE_700}; margin-bottom: {Spacing.XS};">{title}</div>',
                unsafe_allow_html=True
            )
            
            # Message
            st.markdown(
                f'<div style="font-size: {Typography.SIZE_BASE}; color: {Colors.SLATE_500}; margin-bottom: {Spacing.MD};">{message}</div>',
                unsafe_allow_html=True
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Action
            if action_text and on_action and key:
                Button.primary(action_text, key=key, on_click=on_action)
