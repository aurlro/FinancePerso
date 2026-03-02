"""Atom Badge - Badges standardisés.

Usage:
    from modules.ui.atoms import Badge

    Badge.success("Validé")
    Badge.warning("En attente")
    Badge.danger("Erreur", count=3)
"""

from enum import Enum

import streamlit as st

from modules.ui.tokens import BorderRadius, Colors, Spacing, Typography


class BadgeVariant(str, Enum):
    """Variantes de badges."""

    DEFAULT = "default"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"
    NEUTRAL = "neutral"
    PRIMARY = "primary"


class Badge:
    """Badges standardisés selon le Design System.

    Tous les badges de l'application doivent utiliser cette classe.
    """

    # Mapping des variantes vers les couleurs
    _COLORS = {
        BadgeVariant.DEFAULT: (Colors.SLATE_700, Colors.SLATE_100, Colors.SLATE_300),
        BadgeVariant.SUCCESS: (Colors.SUCCESS_DARK, Colors.SUCCESS_BG, Colors.SUCCESS),
        BadgeVariant.WARNING: (Colors.WARNING_DARK, Colors.WARNING_BG, Colors.WARNING),
        BadgeVariant.DANGER: (Colors.DANGER_DARK, Colors.DANGER_BG, Colors.DANGER),
        BadgeVariant.INFO: (Colors.INFO_DARK, Colors.INFO_BG, Colors.INFO),
        BadgeVariant.NEUTRAL: (Colors.SLATE_500, Colors.SLATE_100, Colors.SLATE_200),
        BadgeVariant.PRIMARY: (Colors.PRIMARY, Colors.SLATE_100, Colors.PRIMARY_LIGHT),
    }

    @classmethod
    def _render(
        cls,
        text: str,
        variant: BadgeVariant = BadgeVariant.DEFAULT,
        count: int | None = None,
        icon: str | None = None,
        key: str | None = None,
    ) -> None:
        """Rendu interne du badge.

        Args:
            text: Texte du badge
            variant: Style du badge
            count: Nombre à afficher (petit cercle)
            icon: Emoji/icône optionnelle
            key: Clé unique Streamlit
        """
        text_color, bg_color, border_color = cls._COLORS[variant]

        # Construction du contenu
        content = text
        if icon:
            content = f"{icon} {content}"

        # HTML du badge
        badge_html = f"""
        <span style="
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: {Spacing.XS} {Spacing.SM};
            background-color: {bg_color};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: {BorderRadius.FULL};
            font-size: {Typography.SIZE_XS};
            font-weight: {Typography.WEIGHT_SEMIBOLD};
            line-height: 1;
            white-space: nowrap;
        ">{content}"""

        # Ajouter le compteur si présent
        if count is not None and count > 0:
            badge_html += f"""
            <span style="
                display: inline-flex;
                align-items: center;
                justify-content: center;
                min-width: 18px;
                height: 18px;
                margin-left: 4px;
                background-color: {Colors.DANGER};
                color: {Colors.WHITE};
                border-radius: {BorderRadius.FULL};
                font-size: 11px;
                font-weight: {Typography.WEIGHT_BOLD};
            ">{count if count < 100 else '99+'}</span>"""

        badge_html += "</span>"

        st.markdown(badge_html, unsafe_allow_html=True)

    @classmethod
    def default(
        cls,
        text: str,
        icon: str | None = None,
        count: int | None = None,
        key: str | None = None,
    ) -> None:
        """Badge par défaut (neutre).

        Usage:
            Badge.default("Nouveau")
        """
        cls._render(text, BadgeVariant.DEFAULT, count, icon, key)

    @classmethod
    def success(
        cls,
        text: str,
        icon: str | None = "✓",
        count: int | None = None,
        key: str | None = None,
    ) -> None:
        """Badge succès.

        Usage:
            Badge.success("Validé")
        """
        cls._render(text, BadgeVariant.SUCCESS, count, icon, key)

    @classmethod
    def warning(
        cls,
        text: str,
        icon: str | None = "⚠",
        count: int | None = None,
        key: str | None = None,
    ) -> None:
        """Badge avertissement.

        Usage:
            Badge.warning("Attention")
        """
        cls._render(text, BadgeVariant.WARNING, count, icon, key)

    @classmethod
    def danger(
        cls,
        text: str,
        icon: str | None = "✕",
        count: int | None = None,
        key: str | None = None,
    ) -> None:
        """Badge danger.

        Usage:
            Badge.danger("Erreur", count=3)
        """
        cls._render(text, BadgeVariant.DANGER, count, icon, key)

    @classmethod
    def info(
        cls,
        text: str,
        icon: str | None = "ℹ",
        count: int | None = None,
        key: str | None = None,
    ) -> None:
        """Badge info.

        Usage:
            Badge.info("Info")
        """
        cls._render(text, BadgeVariant.INFO, count, icon, key)

    @classmethod
    def neutral(
        cls,
        text: str,
        icon: str | None = None,
        count: int | None = None,
        key: str | None = None,
    ) -> None:
        """Badge neutre (subtil).

        Usage:
            Badge.neutral("Archive")
        """
        cls._render(text, BadgeVariant.NEUTRAL, count, icon, key)

    @classmethod
    def primary(
        cls,
        text: str,
        icon: str | None = None,
        count: int | None = None,
        key: str | None = None,
    ) -> None:
        """Badge primaire (marque).

        Usage:
            Badge.primary("PRO")
        """
        cls._render(text, BadgeVariant.PRIMARY, count, icon, key)

    @classmethod
    def status(
        cls,
        status: str,
        key: str | None = None,
    ) -> None:
        """Badge de statut automatique.

        Args:
            status: Statut à afficher ("active", "pending", "error", etc.)

        Usage:
            Badge.status("active")  # -> Badge vert "Active"
            Badge.status("pending") # -> Badge orange "En attente"
        """
        status_map = {
            # Français
            "actif": (BadgeVariant.SUCCESS, "Actif"),
            "active": (BadgeVariant.SUCCESS, "Actif"),
            "en attente": (BadgeVariant.WARNING, "En attente"),
            "pending": (BadgeVariant.WARNING, "En attente"),
            "erreur": (BadgeVariant.DANGER, "Erreur"),
            "error": (BadgeVariant.DANGER, "Erreur"),
            "inactif": (BadgeVariant.NEUTRAL, "Inactif"),
            "inactive": (BadgeVariant.NEUTRAL, "Inactif"),
            "terminé": (BadgeVariant.INFO, "Terminé"),
            "completed": (BadgeVariant.INFO, "Terminé"),
            "validé": (BadgeVariant.SUCCESS, "Validé"),
            "validated": (BadgeVariant.SUCCESS, "Validé"),
            "rejeté": (BadgeVariant.DANGER, "Rejeté"),
            "rejected": (BadgeVariant.DANGER, "Rejeté"),
        }

        variant, display_text = status_map.get(status.lower(), (BadgeVariant.DEFAULT, status))

        cls._render(display_text, variant, key=key)
