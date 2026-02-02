"""
Customizable Dashboard System
Système de dashboard avec widgets déplaçables et personnalisables.
Avec mode Preview et persistance en base de données.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json

from modules.logger import logger
from modules.db.dashboard_layouts import (
    get_layout, get_active_layout, save_layout, 
    set_active_layout, list_layouts, delete_layout, duplicate_layout
)


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
    position: int
    size: str
    visible: bool = True
    config: Dict = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}
    
    def to_dict(self) -> Dict:
        """Convertit en dictionnaire pour JSON."""
        return {
            'id': self.id,
            'type': self.type.value,
            'title': self.title,
            'position': self.position,
            'size': self.size,
            'visible': self.visible,
            'config': self.config
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DashboardWidget':
        """Crée un widget depuis un dictionnaire."""
        return cls(
            id=data['id'],
            type=WidgetType(data['type']),
            title=data['title'],
            position=data['position'],
            size=data['size'],
            visible=data.get('visible', True),
            config=data.get('config', {})
        )


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


class DashboardLayoutManager:
    """
    Gestionnaire de layout avec mode Preview et persistance DB.
    """
    
    def __init__(self, layout_key: str = "dashboard_layout"):
        self.layout_key = layout_key
        self.preview_key = f"{layout_key}_preview"
        self._init_from_db()
    
    def _init_from_db(self):
        """Initialise depuis la base de données."""
        if self.layout_key not in st.session_state:
            # Charger depuis la DB
            db_layout = get_active_layout()
            if db_layout:
                st.session_state[self.layout_key] = db_layout
            else:
                # Fallback aux valeurs par défaut
                st.session_state[self.layout_key] = [w.to_dict() for w in DEFAULT_LAYOUT]
    
    def get_layout(self, use_preview: bool = False) -> List[DashboardWidget]:
        """
        Récupère le layout actuel ou le preview.
        
        Args:
            use_preview: Si True, utilise le layout en cours de modification
        """
        key = self.preview_key if use_preview else self.layout_key
        layout_data = st.session_state.get(key, [])
        return [DashboardWidget.from_dict(w) for w in layout_data if w.get('visible', True)]
    
    def get_all_widgets(self, use_preview: bool = False) -> List[DashboardWidget]:
        """Récupère tous les widgets (même cachés)."""
        key = self.preview_key if use_preview else self.layout_key
        layout_data = st.session_state.get(key, [])
        return [DashboardWidget.from_dict(w) for w in layout_data]
    
    def start_preview(self):
        """Démarre le mode preview (copie le layout actuel)."""
        current = st.session_state.get(self.layout_key, [])
        st.session_state[self.preview_key] = [w.copy() for w in current]
        st.session_state[f"{self.layout_key}_preview_mode"] = True
    
    def cancel_preview(self):
        """Annule le mode preview."""
        if self.preview_key in st.session_state:
            del st.session_state[self.preview_key]
        st.session_state[f"{self.layout_key}_preview_mode"] = False
    
    def apply_preview(self, layout_name: str = "custom") -> bool:
        """
        Applique le layout preview et le sauvegarde en DB.
        
        Args:
            layout_name: Nom du layout à sauvegarder
        """
        preview = st.session_state.get(self.preview_key)
        if preview:
            # Met à jour le layout actif
            st.session_state[self.layout_key] = preview.copy()
            
            # Sauvegarde en DB
            success = save_layout(layout_name, preview, set_active=True)
            
            # Nettoie le preview
            self.cancel_preview()
            return success
        return False
    
    def is_preview_mode(self) -> bool:
        """Vérifie si on est en mode preview."""
        return st.session_state.get(f"{self.layout_key}_preview_mode", False)
    
    def update_preview(self, widgets: List[DashboardWidget]):
        """Met à jour le layout en preview."""
        st.session_state[self.preview_key] = [w.to_dict() for w in widgets]
    
    def move_widget(self, widget_id: str, new_position: int, use_preview: bool = True):
        """Déplace un widget."""
        key = self.preview_key if use_preview else self.layout_key
        widgets_data = st.session_state.get(key, [])
        widgets = [DashboardWidget.from_dict(w) for w in widgets_data]
        
        widget = next((w for w in widgets if w.id == widget_id), None)
        if widget:
            widgets = [w for w in widgets if w.id != widget_id]
            widget.position = new_position
            widgets.insert(min(new_position - 1, len(widgets)), widget)
            
            for i, w in enumerate(widgets, 1):
                w.position = i
            
            st.session_state[key] = [w.to_dict() for w in widgets]
    
    def toggle_widget_visibility(self, widget_id: str, use_preview: bool = True):
        """Active/désactive un widget."""
        key = self.preview_key if use_preview else self.layout_key
        widgets_data = st.session_state.get(key, [])
        widgets = [DashboardWidget.from_dict(w) for w in widgets_data]
        
        for w in widgets:
            if w.id == widget_id:
                w.visible = not w.visible
                break
        
        st.session_state[key] = [w.to_dict() for w in widgets]
    
    def load_from_db(self, name: str) -> bool:
        """Charge un layout depuis la DB."""
        layout = get_layout(name)
        if layout:
            st.session_state[self.layout_key] = layout
            return True
        return False
    
    def reset_to_default(self):
        """Réinitialise au layout par défaut."""
        st.session_state[self.layout_key] = [w.to_dict() for w in DEFAULT_LAYOUT]
        save_layout("default", st.session_state[self.layout_key], set_active=True)


def render_dashboard_configurator():
    """
    Affiche l'interface de configuration du dashboard avec mode Preview.
    """
    manager = DashboardLayoutManager()
    
    # Initialiser le preview si pas déjà fait
    if not manager.is_preview_mode():
        manager.start_preview()
    
    st.subheader("🎛️ Personnaliser le Tableau de bord")
    
    # Indicateur de mode Preview
    if manager.is_preview_mode():
        st.info("👁️ **Mode Preview** : Vos modifications ne sont pas encore appliquées. Utilisez les boutons en bas pour valider ou annuler.")
    
    # Liste des layouts sauvegardés
    saved_layouts = list_layouts()
    
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        if saved_layouts:
            layout_names = [l['name'] for l in saved_layouts]
            selected = st.selectbox("📂 Charger un layout", ["Actuel"] + layout_names)
            if selected != "Actuel" and st.button("Charger", use_container_width=True):
                if manager.load_from_db(selected):
                    manager.start_preview()  # Re-init preview
                    st.rerun()
    
    with col2:
        st.caption("💾 Sauvegarder")
        layout_name = st.text_input("Nom du layout", value="custom", label_visibility="collapsed")
    
    with col3:
        st.caption("Actions")
        if st.button("🔄 Réinit. défaut", use_container_width=True):
            manager.reset_to_default()
            manager.start_preview()
            st.rerun()
    
    # Configuration des widgets
    st.divider()
    st.caption("Activez/désactivez les widgets et changez leur ordre :")
    
    widgets = manager.get_all_widgets(use_preview=True)
    
    for widget in sorted(widgets, key=lambda w: w.position):
        cols = st.columns([4, 2, 2, 1])
        
        with cols[0]:
            status = "✅" if widget.visible else "❌"
            st.write(f"{status} {widget.position}. {widget.title}")
        
        with cols[1]:
            if st.button(f"{'Masquer' if widget.visible else 'Afficher'}", 
                        key=f"btn_toggle_{widget.id}",
                        use_container_width=True):
                manager.toggle_widget_visibility(widget.id, use_preview=True)
                st.rerun()
        
        with cols[2]:
            new_pos = st.number_input(
                "Pos",
                min_value=1,
                max_value=len(widgets),
                value=widget.position,
                key=f"input_pos_{widget.id}",
                label_visibility="collapsed"
            )
            if new_pos != widget.position:
                manager.move_widget(widget.id, new_pos, use_preview=True)
                st.rerun()
        
        with cols[3]:
            st.caption(f"[{widget.size}]")
    
    # Boutons d'action Preview
    st.divider()
    
    col_preview1, col_preview2, col_preview3 = st.columns([1, 1, 2])
    
    with col_preview1:
        if st.button("✅ Appliquer les changements", type="primary", use_container_width=True):
            if manager.apply_preview(layout_name):
                st.success(f"✅ Layout '{layout_name}' sauvegardé et appliqué !")
                st.session_state['show_dashboard_config'] = False
                st.rerun()
            else:
                st.error("❌ Erreur lors de la sauvegarde")
    
    with col_preview2:
        if st.button("❌ Annuler", use_container_width=True):
            manager.cancel_preview()
            st.session_state['show_dashboard_config'] = False
            st.rerun()
    
    with col_preview3:
        if st.button("💾 Sauvegarder sans appliquer", use_container_width=True):
            preview = st.session_state.get(manager.preview_key)
            if preview and save_layout(layout_name, preview, set_active=False):
                st.success(f"💾 Layout '{layout_name}' sauvegardé !")


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
    
    # Utiliser le preview si en mode édition, sinon le layout actif
    use_preview = manager.is_preview_mode()
    widgets = manager.get_layout(use_preview=use_preview)
    
    # Trier par position
    widgets = sorted(widgets, key=lambda w: w.position)
    
    # Calculer les tendances une seule fois
    trends = calculate_trends(df_current, df_prev) if not df_current.empty else {}
    
    # Message si mode preview
    if use_preview:
        st.warning("👁️ **Mode Preview** : Vous visualisez des modifications non sauvegardées")
    
    # Rendre les widgets selon leur type
    for widget in widgets:
        if not widget.visible:
            continue
        
        # KPIs - affichés en ligne (4 colonnes)
        if widget.type in [WidgetType.KPI_DEPENSES, WidgetType.KPI_REVENUS, 
                          WidgetType.KPI_SOLDE, WidgetType.KPI_EPARGNE]:
            if widget.position == 1:
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
    'render_dashboard_configurator',
    'render_customizable_overview',
    'DEFAULT_LAYOUT'
]