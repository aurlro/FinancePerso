"""Molecule Metric - Métrique simple avec tendance.

Usage:
    from modules.ui.molecules import Metric, MetricTrend

    Metric.render(
        label="Dépenses",
        value="1 234 €",
        trend=MetricTrend.up("+12%"),
        icon="💸"
    )
"""

from dataclasses import dataclass

import streamlit as st

from modules.ui.tokens import BorderRadius, Colors, Shadow, Spacing, Typography


@dataclass
class MetricTrend:
    """Représente une tendance de métrique.

    Usage:
        trend = MetricTrend.up("+12%")
        trend = MetricTrend.down("-5%")
        trend = MetricTrend.neutral("0%")
    """

    value: str
    direction: str  # "up", "down", "neutral"
    color: str
    icon: str

    @classmethod
    def up(cls, value: str) -> "MetricTrend":
        """Tendance positive."""
        return cls(value, "up", Colors.SUCCESS, "↑")

    @classmethod
    def down(cls, value: str) -> "MetricTrend":
        """Tendance négative."""
        return cls(value, "down", Colors.DANGER, "↓")

    @classmethod
    def neutral(cls, value: str) -> "MetricTrend":
        """Tendance neutre."""
        return cls(value, "neutral", Colors.SLATE_500, "→")


class Metric:
    """Métrique unifiée avec valeur, tendance et contexte.

    Remplace les différentes implémentations de métriques KPI.
    """

    @staticmethod
    def render(
        label: str,
        value: str,
        trend: MetricTrend | None = None,
        subtitle: str | None = None,
        icon: str | None = None,
        help_text: str | None = None,
    ) -> None:
        """Rend une métrique.

        Args:
            label: Libellé de la métrique
            value: Valeur à afficher
            trend: Tendance (MetricTrend.up/down/neutral)
            subtitle: Texte secondaire
            icon: Emoji/icône
            help_text: Texte d'aide (tooltip)
        """
        container = st.container()

        with container:
            # Card style
            card_style = f"""
                background-color: {Colors.WHITE};
                border: 1px solid {Colors.SLATE_200};
                border-radius: {BorderRadius.LG};
                padding: {Spacing.MD};
                box-shadow: {Shadow.SM};
            """
            st.markdown(f'<div style="{card_style}">', unsafe_allow_html=True)

            # Icône
            if icon:
                st.markdown(
                    f'<div style="font-size: 1.5rem; margin-bottom: 4px;">{icon}</div>',
                    unsafe_allow_html=True,
                )

            # Label avec help
            label_html = (
                f'<div style="font-size: {Typography.SIZE_SM}; color: {Colors.SLATE_500}; '
                f'margin-bottom: 2px;">{label}'
            )
            if help_text:
                label_html += f' <span title="{help_text}">ℹ️</span>'
            label_html += "</div>"
            st.markdown(label_html, unsafe_allow_html=True)

            # Valeur
            st.markdown(
                f'<div style="font-size: {Typography.SIZE_2XL}; '
                f'font-weight: {Typography.WEIGHT_BOLD}; color: {Colors.SLATE_900};">'
                f"{value}</div>",
                unsafe_allow_html=True,
            )

            # Tendance
            if trend:
                st.markdown(
                    f'<div style="font-size: {Typography.SIZE_SM}; color: {trend.color}; '
                    f'margin-top: 2px;">{trend.icon} {trend.value}</div>',
                    unsafe_allow_html=True,
                )

            # Sous-titre
            if subtitle:
                st.markdown(
                    f'<div style="font-size: {Typography.SIZE_XS}; color: {Colors.SLATE_400}; '
                    f'margin-top: 4px;">{subtitle}</div>',
                    unsafe_allow_html=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)

    @classmethod
    def comparison(
        cls,
        label: str,
        current_value: str,
        previous_value: str,
        icon: str | None = None,
    ) -> None:
        """Métrique avec comparaison.

        Usage:
            Metric.comparison(
                label="Dépenses",
                current_value="1 234 €",
                previous_value="1 100 €"
            )
        """
        # Calculer la tendance
        try:
            current = float(current_value.replace(" ", "").replace("€", "").replace(",", "."))
            previous = float(previous_value.replace(" ", "").replace("€", "").replace(",", "."))

            if previous > 0:
                change = ((current - previous) / previous) * 100
                if change > 0:
                    trend = MetricTrend.up(f"+{change:.1f}%")
                elif change < 0:
                    trend = MetricTrend.down(f"{change:.1f}%")
                else:
                    trend = MetricTrend.neutral("0%")
            else:
                trend = None
        except (ValueError, TypeError):
            trend = None

        cls.render(
            label=label,
            value=current_value,
            trend=trend,
            subtitle=f"vs {previous_value} (période précédente)",
            icon=icon,
        )

    @classmethod
    def mini(
        cls,
        label: str,
        value: str,
        trend: str | None = None,
        trend_positive: bool = True,
    ) -> None:
        """Version compacte pour tableaux/listes.

        Usage:
            Metric.mini("Total", "123", "+5", True)
        """
        trend_obj = None
        if trend:
            trend_obj = MetricTrend.up(trend) if trend_positive else MetricTrend.down(trend)

        container_style = f"""
            display: flex;
            align-items: center;
            gap: {Spacing.SM};
        """

        st.markdown(f'<div style="{container_style}">', unsafe_allow_html=True)

        # Label
        st.markdown(
            f'<span style="font-size: {Typography.SIZE_XS}; color: {Colors.SLATE_500};">{label}:</span>',
            unsafe_allow_html=True,
        )

        # Value
        st.markdown(
            f'<span style="font-size: {Typography.SIZE_SM}; '
            f'font-weight: {Typography.WEIGHT_SEMIBOLD}; color: {Colors.SLATE_900};">'
            f"{value}</span>",
            unsafe_allow_html=True,
        )

        # Trend
        if trend_obj:
            st.markdown(
                f'<span style="font-size: {Typography.SIZE_XS}; color: {trend_obj.color};">'
                f"{trend_obj.icon} {trend_obj.value}</span>",
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)
