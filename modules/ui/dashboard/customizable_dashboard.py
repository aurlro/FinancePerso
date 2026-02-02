"""
Customizable Dashboard System
Système de dashboard avec widgets déplaçables et personnalisables.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json


class WidgetType(Enum):
    """Types de widgets disponibles."""
    KPI_DEPENSES = "kpi_depenses"
    KPI_REVENUS = "kpi_revenus"
    KPI_SOLDE = "kpi_solde"
    KPI_EPARGNE = "kpi_epargne"
    EVOLUTION_CHART = "evolution_chart"
    SAVINGS_TREND = "savings_trend"
    CATEGORIES_CHART = "categories_chart"
    TOP_EXPENSES = "top_expenses"
    BUDGET_TRACKER = "budget_tracker"
    BUDGET_ALERTS = "budget_alerts"
    SMART_RECOMMENDATIONS = "smart_recommendations"
    MONTHLY_STACKED = "monthly_stacked"
    MEMBERS_ANALYSIS = "members_analysis"
    TIERS_ANALYSIS = "tiers_analysis"
    TAGS_ANALYSIS = "tags_analysis"
    AI_INSIGHTS = "ai_insights"


@dataclass
class DashboardWidget:
    """Représente un widget du dashboard."""
    id: str
    type: WidgetType
    title: str
    position: int  # Ordre d'affichage
    size: str  # 'small', 'medium', 'large', 'full'
    visible: bool = True
    config: Dict = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}


class DashboardLayoutManager:
    """
    Gestionnaire de layout personnalisable.
    Stocke la configuration dans st.session_state (persistance temporaire)
    ou pourrait utiliser la DB pour persistance permanente.
    """
    
    DEFAULT_LAYOUT = [
        DashboardWidget("kpi_1", WidgetType.KPI_DEPENSES, "💸 Dépenses", 1, "small"),
        DashboardWidget("kpi_2", WidgetType.KPI_REVENUS, "💰 Revenus", 2, "small"),
        DashboardWidget("kpi_3", WidgetType.KPI_SOLDE, "📊 Solde", 3, "small"),
        DashboardWidget("kpi_4", WidgetType.KPI_EPARGNE, "🎯 Taux d'épargne", 4, "small"),
        DashboardWidget("evol_1", WidgetType.EVOLUTION_CHART, "📈 Évolution", 5, "large"),
        DashboardWidget("sav_1", WidgetType.SAVINGS_TREND, "💹 Tendance épargne", 6, "medium"),
        DashboardWidget("cat_1", WidgetType.CATEGORIES_CHART, "📊 Répartition", 7, "medium"),
        DashboardWidget("top_1", WidgetType.TOP_EXPENSES, "🔥 Top dépenses", 8, "medium"),
    ]
    
    def __init__(self, layout_key: str = "dashboard_layout"):
        self.layout_key = layout_key
        self._init_layout()
    
    def _init_layout(self):
        """Initialise le layout par défaut si nécessaire."""
        if self.layout_key not in st.session_state:
            st.session_state[self.layout_key] = [
                asdict(w) for w in self.DEFAULT_LAYOUT
            ]
    
    def get_layout(self) -> List[DashboardWidget]:
        """Récupère le layout actuel."""
        layout_data = st.session_state.get(self.layout_key, [])
        return [DashboardWidget(**w) for w in layout_data if w.get('visible', True)]
    
    def get_all_widgets(self) -> List[DashboardWidget]:
        """Récupère tous les widgets (même cachés)."""
        layout_data = st.session_state.get(self.layout_key, [])
        return [DashboardWidget(**w) for w in layout_data]
    
    def update_layout(self, widgets: List[DashboardWidget]):
        """Met à jour le layout complet."""
        st.session_state[self.layout_key] = [asdict(w) for w in widgets]
    
    def move_widget(self, widget_id: str, new_position: int):
        """Déplace un widget à une nouvelle position."""
        widgets = self.get_all_widgets()
        widget = next((w for w in widgets if w.id == widget_id), None)
        
        if widget:
            # Retirer de l'ancienne position
            widgets = [w for w in widgets if w.id != widget_id]
            # Insérer à la nouvelle position
            widget.position = new_position
            widgets.insert(new_position - 1, widget)
            
            # Recalculer toutes les positions
            for i, w in enumerate(widgets, 1):
                w.position = i
            
            self.update_layout(widgets)
    
    def toggle_widget_visibility(self, widget_id: str):
        """Active/désactive un widget."""
        widgets = self.get_all_widgets()
        for w in widgets:
            if w.id == widget_id:
                w.visible = not w.visible
                break
        self.update_layout(widgets)
    
    def reset_to_default(self):
        """Réinitialise le layout par défaut."""
        st.session_state[self.layout_key] = [
            asdict(w) for w in self.DEFAULT_LAYOUT
        ]
    
    def save_layout(self, name: str = "default"):
        """Sauvegarde le layout (pourrait utiliser la DB)."""
        save_key = f"{self.layout_key}_saved_{name}"
        st.session_state[save_key] = st.session_state[self.layout_key].copy()
        st.success(f"✅ Layout '{name}' sauvegardé !")
    
    def load_layout(self, name: str = "default"):
        """Charge un layout sauvegardé."""
        save_key = f"{self.layout_key}_saved_{name}"
        if save_key in st.session_state:
            st.session_state[self.layout_key] = st.session_state[save_key].copy()
            st.success(f"✅ Layout '{name}' chargé !")
        else:
            st.error(f"❌ Layout '{name}' non trouvé")


def render_widget_container(widget: DashboardWidget, content_fn: Callable, 
                            can_configure: bool = False, can_remove: bool = True):
    """
    Rend un widget dans un container avec bordure et contrôles.
    
    Args:
        widget: Le widget à afficher
        content_fn: Fonction qui rend le contenu du widget
        can_configure: Si True, affiche un bouton de configuration
        can_remove: Si True, affiche un bouton de suppression
    """
    with st.container(border=True):
        # Header avec titre et contrôles
        header_cols = st.columns([6, 1, 1, 1])
        
        with header_cols[0]:
            st.markdown(f"**{widget.title}**")
        
        with header_cols[1]:
            if can_configure:
                if st.button("⚙️", key=f"config_{widget.id}", help="Configurer"):
                    st.session_state[f"configuring_{widget.id}"] = True
        
        with header_cols[2]:
            if st.button("👁️", key=f"toggle_{widget.id}", help="Masquer"):
                manager = DashboardLayoutManager()
                manager.toggle_widget_visibility(widget.id)
                st.rerun()
        
        with header_cols[3]:
            # Menu de déplacement
            if st.button("⋮⋮", key=f"move_menu_{widget.id}", help="Déplacer"):
                st.session_state[f"moving_{widget.id}"] = True
        
        # Contenu du widget
        content_fn()
        
        # Dialog de déplacement
        if st.session_state.get(f"moving_{widget.id}", False):
            with st.expander(f"Déplacer '{widget.title}'", expanded=True):
                manager = DashboardLayoutManager()
                all_widgets = manager.get_all_widgets()
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    new_pos = st.selectbox(
                        "Nouvelle position",
                        options=list(range(1, len(all_widgets) + 1)),
                        index=widget.position - 1,
                        key=f"new_pos_{widget.id}"
                    )
                with col2:
                    if st.button("✓", key=f"confirm_move_{widget.id}"):
                        manager.move_widget(widget.id, new_pos)
                        del st.session_state[f"moving_{widget.id}"]
                        st.rerun()
                    if st.button("✕", key=f"cancel_move_{widget.id}"):
                        del st.session_state[f"moving_{widget.id}"]
                        st.rerun()


def render_dashboard_configurator():
    """
    Affiche l'interface de configuration du dashboard.
    Permet d'activer/désactiver les widgets et de réorganiser.
    """
    st.subheader("🎛️ Personnaliser le Tableau de bord")
    
    manager = DashboardLayoutManager()
    widgets = manager.get_all_widgets()
    
    # Mode édition
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.caption(f"{sum(1 for w in widgets if w.visible)} widgets actifs")
    
    with col2:
        if st.button("💾 Sauvegarder", use_container_width=True):
            manager.save_layout("custom")
    
    with col3:
        if st.button("🔄 Réinitialiser", use_container_width=True):
            manager.reset_to_default()
            st.rerun()
    
    # Liste des widgets avec toggles
    st.divider()
    st.caption("Activez/désactivez les widgets et changez leur ordre :")
    
    for widget in sorted(widgets, key=lambda w: w.position):
        cols = st.columns([4, 2, 2, 1])
        
        with cols[0]:
            status = "✅" if widget.visible else "❌"
            st.write(f"{status} {widget.position}. {widget.title}")
        
        with cols[1]:
            if st.button(f"{'Masquer' if widget.visible else 'Afficher'}", 
                        key=f"btn_toggle_{widget.id}",
                        use_container_width=True):
                manager.toggle_widget_visibility(widget.id)
                st.rerun()
        
        with cols[2]:
            # Déplacement rapide
            new_pos = st.number_input(
                "Pos",
                min_value=1,
                max_value=len(widgets),
                value=widget.position,
                key=f"input_pos_{widget.id}",
                label_visibility="collapsed"
            )
            if new_pos != widget.position:
                manager.move_widget(widget.id, new_pos)
                st.rerun()
        
        with cols[3]:
            st.caption(f"[{widget.size}]")


def render_customizable_overview(df_current: pd.DataFrame, df_prev: pd.DataFrame, 
                                 cat_emoji_map: Dict, df_full: pd.DataFrame = None):
    """
    Rend la vue d'ensemble personnalisée avec les widgets configurables.
    """
    from modules.ui.dashboard.kpi_cards import calculate_trends
    from modules.ui.dashboard.evolution_chart import render_evolution_chart, render_savings_trend_chart
    from modules.ui.dashboard.category_charts import render_category_bar_chart
    from modules.ui.dashboard.top_expenses import render_top_expenses
    from modules.ui import card_kpi
    
    manager = DashboardLayoutManager()
    widgets = manager.get_layout()
    
    # Trier par position
    widgets = sorted(widgets, key=lambda w: w.position)
    
    # Calculer les tendances une seule fois
    trends = calculate_trends(df_current, df_prev) if not df_current.empty else {}
    
    # Rendre les widgets selon leur type
    for widget in widgets:
        if not widget.visible:
            continue
        
        # KPIs - affichés en ligne (4 colonnes)
        if widget.type in [WidgetType.KPI_DEPENSES, WidgetType.KPI_REVENUS, 
                          WidgetType.KPI_SOLDE, WidgetType.KPI_EPARGNE]:
            # Regrouper les 4 KPIs ensemble
            if widget.position == 1:  # Premier KPI
                cols = st.columns(4)
                kpi_widgets = [w for w in widgets if w.type in [
                    WidgetType.KPI_DEPENSES, WidgetType.KPI_REVENUS,
                    WidgetType.KPI_SOLDE, WidgetType.KPI_EPARGNE
                ] and w.visible]
                
                for i, kpi_w in enumerate(kpi_widgets[:4]):
                    with cols[i]:
                        if kpi_w.type == WidgetType.KPI_DEPENSES and trends:
                            card_kpi("Dépenses", f"{trends['expenses']['value']:,.0f} €",
                                   trend=trends['expenses']['trend'],
                                   trend_color=trends['expenses']['color'])
                        elif kpi_w.type == WidgetType.KPI_REVENUS and trends:
                            card_kpi("Revenus", f"{trends['revenue']['value']:,.0f} €",
                                   trend=trends['revenue']['trend'],
                                   trend_color=trends['revenue']['color'])
                        elif kpi_w.type == WidgetType.KPI_SOLDE and trends:
                            card_kpi("Solde", f"{trends['balance']['value']:,.0f} €",
                                   trend=trends['balance']['trend'],
                                   trend_color=trends['balance']['color'])
                        elif kpi_w.type == WidgetType.KPI_EPARGNE and trends:
                            card_kpi("Épargne", f"{trends['savings_rate']['value']:.1f}%",
                                   trend=trends['savings_rate']['trend'],
                                   trend_color=trends['savings_rate']['color'])
        
        # Graphiques d'évolution
        elif widget.type == WidgetType.EVOLUTION_CHART and not df_current.empty:
            with st.container(border=True):
                st.markdown(f"**{widget.title}**")
                render_evolution_chart(df_current)
        
        elif widget.type == WidgetType.SAVINGS_TREND:
            with st.container(border=True):
                st.markdown(f"**{widget.title}**")
                render_savings_trend_chart()
        
        elif widget.type == WidgetType.CATEGORIES_CHART and not df_current.empty:
            with st.container(border=True):
                st.markdown(f"**{widget.title}**")
                render_category_bar_chart(df_current, cat_emoji_map)
        
        elif widget.type == WidgetType.TOP_EXPENSES and not df_current.empty:
            with st.container(border=True):
                st.markdown(f"**{widget.title}**")
                render_top_expenses(df_current, cat_emoji_map, limit=10)
        
        elif widget.type == WidgetType.MONTHLY_STACKED and df_full is not None:
            from modules.ui.dashboard.category_charts import render_monthly_stacked_chart
            with st.container(border=True):
                st.markdown(f"**{widget.title}**")
                render_monthly_stacked_chart(df_full, cat_emoji_map)
        
        st.markdown("---")


# Export
__all__ = [
    'DashboardLayoutManager',
    'DashboardWidget',
    'WidgetType',
    'render_widget_container',
    'render_dashboard_configurator',
    'render_customizable_overview'
]