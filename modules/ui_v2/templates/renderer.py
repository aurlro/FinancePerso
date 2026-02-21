"""Dashboard Renderer for UI v2.

Fonctions de rendu pour le dashboard personnalisable avec grille responsive.
"""

import pandas as pd
import streamlit as st

from modules.logger import logger
from modules.ui import card_kpi
from modules.ui.dashboard.budget_tracker import render_budget_tracker
from modules.ui.dashboard.category_charts import (
    prepare_expense_dataframe,
    render_category_bar_chart,
    render_monthly_stacked_chart,
)
from modules.ui.dashboard.evolution_chart import render_evolution_chart, render_savings_trend_chart
from modules.ui.dashboard.kpi_cards import calculate_trends
from modules.ui.dashboard.smart_recommendations import render_smart_recommendations_section
from modules.ui.dashboard.top_expenses import render_top_expenses
from modules.ui_v2.atoms.colors import ColorScheme, FeedbackColor
from modules.ui_v2.atoms.icons import IconSet
from modules.ui_v2.templates.layouts import WidgetType, LAYOUT_TEMPLATES, DEFAULT_LAYOUT
from modules.ui_v2.templates.manager import DashboardLayoutManager


def _get_column_width(size: str) -> int:
    """Convertit une taille de widget en nombre de colonnes (sur 12).

    Args:
        size: Taille du widget ('small', 'medium', 'large', 'full')

    Returns:
        Nombre de colonnes (1-12)
    """
    width_map = {
        "small": 3,   # 4 widgets par ligne
        "medium": 6,  # 2 widgets par ligne
        "large": 9,   # 2/3 de la largeur
        "full": 12,   # Toute la largeur
    }
    return width_map.get(size, 6)


def render_dashboard_configurator() -> None:
    """Affiche l'interface de configuration du dashboard avec mode Preview et templates."""
    manager = DashboardLayoutManager()

    # Initialiser le preview si pas déjà fait
    if not manager.is_preview_mode():
        manager.start_preview()

    st.subheader(f"{IconSet.SETTINGS.value} Personnaliser le Tableau de bord")

    # Indicateur de mode Preview
    if manager.is_preview_mode():
        st.info(f"{IconSet.VISIBLE.value} **Mode Preview** : Vos modifications ne sont pas encore appliquées.")

    # Section 1: Templates rapides
    st.markdown(f"**{IconSet.MAGIC.value} Templates prédéfinis**")
    st.caption("Choisissez un template pour démarrer rapidement :")

    template_cols = st.columns(len(LAYOUT_TEMPLATES))
    for i, (template_key, template_data) in enumerate(LAYOUT_TEMPLATES.items()):
        with template_cols[i]:
            with st.container(border=True):
                st.markdown(f"**{template_data['name']}**")
                st.caption(template_data['description'])
                st.caption(f"{len(template_data['widgets'])} widgets")
                if st.button(
                    f"{IconSet.CONFIRM.value} Appliquer",
                    key=f"template_{template_key}",
                    use_container_width=True
                ):
                    # Charger le template dans le preview
                    st.session_state[manager.preview_key] = [
                        w.to_dict() for w in template_data['widgets']
                    ]
                    st.success(f"{IconSet.SUCCESS.value} Template '{template_data['name']}' chargé !")
                    st.rerun()

    st.divider()

    # Section 2: Layouts sauvegardés
    saved_layouts = manager.get_saved_layouts()

    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        st.markdown(f"**{IconSet.FOLDER.value} Mes layouts**")
        if saved_layouts:
            layout_names = [l["name"] for l in saved_layouts if l["name"] != "default"]
            if layout_names:
                selected = st.selectbox(
                    "Charger",
                    ["Sélectionner..."] + layout_names,
                    label_visibility="collapsed"
                )
                if selected != "Sélectionner..." and st.button(
                    f"{IconSet.DOWNLOAD.value} Charger",
                    use_container_width=True,
                    key="load_saved"
                ):
                    if manager.load_from_db(selected):
                        manager.start_preview()
                        st.rerun()
            else:
                st.caption("Aucun layout sauvegardé")
        else:
            st.caption("Aucun layout sauvegardé")

    with col2:
        st.markdown(f"**{IconSet.SAVE.value} Sauvegarder**")
        layout_name = st.text_input(
            "Nom",
            value="mon_layout",
            label_visibility="collapsed"
        )

    with col3:
        st.markdown(f"**{IconSet.REFRESH.value} Actions**")
        if st.button(
            f"{IconSet.REFRESH.value} Réinit. défaut",
            use_container_width=True,
            key="dash_reset_default"
        ):
            manager.reset_to_default()
            manager.start_preview()
            st.rerun()

    # Configuration des widgets
    st.divider()
    st.markdown(f"**{IconSet.TOOLS.value} Widgets** - Activez/désactivez et réorganisez :")

    widgets = manager.get_all_widgets(use_preview=True)

    for widget in sorted(widgets, key=lambda w: w.position):
        cols = st.columns([4, 2, 2, 1])

        with cols[0]:
            status = IconSet.VISIBLE.value if widget.visible else IconSet.HIDDEN.value
            st.write(f"{status} {widget.position}. {widget.title}")

        with cols[1]:
            toggle_label = f"{IconSet.HIDDEN.value} Masquer" if widget.visible else f"{IconSet.VISIBLE.value} Afficher"
            if st.button(
                toggle_label,
                key=f"btn_toggle_{widget.id}",
                use_container_width=True,
            ):
                manager.toggle_widget_visibility(widget.id, use_preview=True)
                st.rerun()

        with cols[2]:
            new_pos = st.number_input(
                "Pos",
                min_value=1,
                max_value=len(widgets),
                value=widget.position,
                key=f"input_pos_{widget.id}",
                label_visibility="collapsed",
            )
            if new_pos != widget.position:
                manager.move_widget(widget.id, int(new_pos), use_preview=True)
                st.rerun()

        with cols[3]:
            st.caption(f"[{widget.size}]")

    # Boutons d'action Preview
    st.divider()

    col_preview1, col_preview2, col_preview3 = st.columns([1, 1, 2])

    with col_preview1:
        if st.button(
            f"{IconSet.SUCCESS.value} Appliquer les changements",
            type="primary",
            use_container_width=True,
            key="dash_apply_changes",
        ):
            if manager.apply_preview(layout_name):
                st.success(f"{IconSet.SUCCESS.value} Layout '{layout_name}' sauvegardé et appliqué !")
                st.session_state["show_dashboard_config"] = False
                st.rerun()
            else:
                st.error(f"{IconSet.ERROR.value} Erreur lors de la sauvegarde")

    with col_preview2:
        if st.button(
            f"{IconSet.CANCEL.value} Annuler",
            use_container_width=True,
            key="dash_cancel_changes"
        ):
            manager.cancel_preview()
            st.session_state["show_dashboard_config"] = False
            st.rerun()

    with col_preview3:
        if st.button(
            f"{IconSet.SAVE.value} Sauvegarder sans appliquer",
            use_container_width=True,
            key="dash_save_only"
        ):
            from modules.db.dashboard_layouts import save_layout
            preview = st.session_state.get(manager.preview_key)
            if preview and save_layout(layout_name, preview, set_active=False):
                st.success(f"{IconSet.SAVE.value} Layout '{layout_name}' sauvegardé !")


def _render_widget_content(
    widget,
    df_current: pd.DataFrame,
    df_prev: pd.DataFrame,
    df_full: pd.DataFrame | None,
    cat_emoji_map: dict,
    trends: dict,
    in_grid: bool = False
) -> None:
    """Rend le contenu d'un widget selon son type.

    Args:
        widget: Instance de DashboardWidget
        df_current: DataFrame des transactions courantes
        df_prev: DataFrame des transactions précédentes
        df_full: DataFrame complet (toutes périodes)
        cat_emoji_map: Mapping catégories -> emojis
        trends: Données de tendances calculées
        in_grid: Si True, le widget est dans une grille
    """
    # Conteneur avec ou sans bordure selon le contexte
    container = st.container(border=not in_grid)

    with container:
        if not in_grid:
            st.markdown(f"**{widget.title}**")

        try:
            if widget.type == WidgetType.EVOLUTION_CHART and not df_current.empty:
                render_evolution_chart(df_current)

            elif widget.type == WidgetType.SAVINGS_TREND:
                render_savings_trend_chart()

            elif widget.type == WidgetType.CATEGORIES_CHART and not df_current.empty:
                render_category_bar_chart(df_current, cat_emoji_map)

            elif widget.type == WidgetType.TOP_EXPENSES and not df_current.empty:
                render_top_expenses(df_current, cat_emoji_map, limit=10)

            elif widget.type == WidgetType.MONTHLY_STACKED and df_full is not None:
                render_monthly_stacked_chart(df_full, cat_emoji_map)

            elif widget.type == WidgetType.BUDGET_TRACKER:
                df_exp = (
                    prepare_expense_dataframe(df_current, cat_emoji_map)
                    if not df_current.empty
                    else pd.DataFrame()
                )
                render_budget_tracker(df_exp, cat_emoji_map, df_full)

            elif widget.type == WidgetType.BUDGET_ALERTS and not df_current.empty:
                _render_budget_alerts_widget(df_full)

            elif widget.type == WidgetType.SMART_RECOMMENDATIONS and not df_current.empty:
                render_smart_recommendations_section(df_full or df_current, df_current)

            else:
                st.caption(f"Widget '{widget.title}'")

        except Exception as e:
            logger.error(f"Error rendering widget {widget.id}: {e}")
            st.error(f"{IconSet.ERROR.value} Erreur d'affichage")


def _render_budget_alerts_widget(df_full: pd.DataFrame | None) -> None:
    """Rend le widget d'alertes budget.

    Args:
        df_full: DataFrame complet des transactions
    """
    import datetime

    from modules.ai import get_budget_alerts_summary, predict_budget_overruns
    from modules.db.budgets import get_budgets

    budgets = get_budgets()
    if not budgets.empty:
        today = datetime.date.today()
        current_month = today.strftime("%Y-%m")
        df_month = (
            df_full[df_full["date_dt"].dt.strftime("%Y-%m") == current_month]
            if df_full is not None and not df_full.empty
            else pd.DataFrame()
        )

        if not df_month.empty:
            predictions = predict_budget_overruns(df_month, budgets)
            if predictions:
                summary = get_budget_alerts_summary(predictions)
                cols = st.columns(3)
                with cols[0]:
                    st.metric(
                        f"{IconSet.SUCCESS.value} OK",
                        summary["ok_count"]
                    )
                with cols[1]:
                    st.metric(
                        f"{IconSet.WARNING.value} Attention",
                        summary["warning_count"]
                    )
                with cols[2]:
                    st.metric(
                        f"{IconSet.ALERT.value} Dépassement",
                        summary["overrun_count"]
                    )
            else:
                st.success(f"{IconSet.SUCCESS.value} Tous les budgets sont respectés")
        else:
            st.info("Pas assez de données ce mois-ci")
    else:
        st.info("Aucun budget défini")


def _render_kpi_widgets(
    kpi_widgets: list,
    trends: dict,
    use_preview: bool
) -> None:
    """Rend les widgets KPI dans une grille de 4 colonnes.

    Args:
        kpi_widgets: Liste des widgets KPI à afficher
        trends: Données de tendances calculées
        use_preview: Si True, affiche un indicateur de preview
    """
    if not trends:
        return

    kpi_widgets.sort(key=lambda w: w.position)
    cols = st.columns(4)

    for i, kpi_w in enumerate(kpi_widgets[:4]):
        with cols[i]:
            if kpi_w.type == WidgetType.KPI_DEPENSES and "expenses" in trends:
                card_kpi(
                    f"{IconSet.MONEY.value} Dépenses",
                    f"{trends['expenses']['value']:,.0f} €",
                    trend=trends["expenses"]["trend"],
                    trend_color=trends["expenses"]["color"],
                )
            elif kpi_w.type == WidgetType.KPI_REVENUS and "revenue" in trends:
                card_kpi(
                    f"{IconSet.CREDIT_CARD.value} Revenus",
                    f"{trends['revenue']['value']:,.0f} €",
                    trend=trends["revenue"]["trend"],
                    trend_color=trends["revenue"]["color"],
                )
            elif kpi_w.type == WidgetType.KPI_SOLDE and "balance" in trends:
                card_kpi(
                    f"{IconSet.CHART.value} Solde",
                    f"{trends['balance']['value']:,.0f} €",
                    trend=trends["balance"]["trend"],
                    trend_color=trends["balance"]["color"],
                )
            elif kpi_w.type == WidgetType.KPI_EPARGNE and "savings_rate" in trends:
                card_kpi(
                    f"{IconSet.TARGET.value} Épargne",
                    f"{trends['savings_rate']['value']:.1f}%",
                    trend=trends["savings_rate"]["trend"],
                    trend_color=trends["savings_rate"]["color"],
                )


def render_customizable_overview(
    df_current: pd.DataFrame,
    df_prev: pd.DataFrame,
    cat_emoji_map: dict,
    df_full: pd.DataFrame | None = None,
) -> None:
    """Rend la vue d'ensemble personnalisée avec widgets configurables.

    Args:
        df_current: DataFrame des transactions du mois courant
        df_prev: DataFrame des transactions du mois précédent
        cat_emoji_map: Mapping catégories -> emojis
        df_full: DataFrame complet (optionnel)
    """
    manager = DashboardLayoutManager()

    # Utiliser le preview si en mode édition, sinon le layout actif
    use_preview = manager.is_preview_mode()
    widgets = manager.get_layout(use_preview=use_preview)

    # Si aucun widget visible, proposer de réinitialiser
    if not widgets:
        st.info(
            f"{IconSet.INFO.value} Aucun widget configuré. "
            f"Cliquez sur '{IconSet.SETTINGS.value} Personnaliser le dashboard' pour configurer votre vue."
        )
        if st.button(
            f"{IconSet.REFRESH.value} Réinitialiser au layout par défaut",
            key="reset_default_layout"
        ):
            manager.reset_to_default()
            st.rerun()
        return

    # Trier par position
    widgets = sorted(widgets, key=lambda w: w.position)

    # Calculer les tendances une seule fois
    trends = calculate_trends(df_current, df_prev) if not df_current.empty else {}

    # Message si mode preview
    if use_preview:
        st.warning(
            f"{IconSet.VISIBLE.value} **Mode Preview** : "
            "Vous visualisez des modifications non sauvegardées"
        )

    # Gestion de la grille responsive
    current_col = 0
    current_row_widgets = []

    def flush_row() -> None:
        """Affiche les widgets de la ligne actuelle."""
        nonlocal current_col, current_row_widgets
        if not current_row_widgets:
            return

        if len(current_row_widgets) == 1:
            # Widget seul sur la ligne
            widget = current_row_widgets[0]
            _render_widget_content(
                widget, df_current, df_prev, df_full, cat_emoji_map, trends
            )
        else:
            # Plusieurs widgets sur la ligne
            cols = st.columns(len(current_row_widgets))
            for col, widget in zip(cols, current_row_widgets):
                with col:
                    _render_widget_content(
                        widget, df_current, df_prev, df_full,
                        cat_emoji_map, trends, in_grid=True
                    )

        current_col = 0
        current_row_widgets = []

    # Rendre tous les widgets (sauf KPIs qui sont traités séparément)
    for widget in widgets:
        if not widget.visible:
            continue

        widget_width = _get_column_width(widget.size)

        # Les KPIs sont traités ensemble à la fin
        if widget.type in [
            WidgetType.KPI_DEPENSES,
            WidgetType.KPI_REVENUS,
            WidgetType.KPI_SOLDE,
            WidgetType.KPI_EPARGNE,
        ]:
            continue

        # Si le widget ne tient pas sur la ligne actuelle, flush et recommencer
        if current_col + widget_width > 12 and current_row_widgets:
            flush_row()

        current_row_widgets.append(widget)
        current_col += widget_width

        # Si la ligne est pleine, flush
        if current_col >= 12:
            flush_row()

    # Flush la dernière ligne
    flush_row()

    # Traiter les KPIs en dernier (affichage spécial en 4 colonnes)
    kpi_widgets = [
        w for w in widgets
        if w.type in [
            WidgetType.KPI_DEPENSES,
            WidgetType.KPI_REVENUS,
            WidgetType.KPI_SOLDE,
            WidgetType.KPI_EPARGNE,
        ] and w.visible
    ]

    if kpi_widgets:
        _render_kpi_widgets(kpi_widgets, trends, use_preview)


__all__ = [
    "render_dashboard_configurator",
    "render_customizable_overview",
    "_get_column_width",
]
