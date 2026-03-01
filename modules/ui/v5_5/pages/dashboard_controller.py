"""Controller pour la page Test_Dashboard.

Gère la logique métier et le routing entre welcome screen et dashboard.

Usage:
    from modules.ui.v5_5.pages import DashboardController
    
    controller = DashboardController(user_name="Alex")
    controller.render()
"""

from typing import Optional
import streamlit as st

from modules.ui.v5_5 import (
    render_dashboard_v5,
    render_welcome_screen,
    has_transactions,
)


class DashboardController:
    """Controller pour la page Test_Dashboard.
    
    Responsabilités:
    - Détecter si l'utilisateur a des données
    - Router vers welcome ou dashboard
    - Gérer les modes de test/démo
    - Fournir une API simple pour la page Streamlit
    
    Args:
        user_name: Nom de l'utilisateur (défaut: "Alex")
        default_month: Mois par défaut (défaut: mois courant)
        test_mode: Mode de test (auto, dashboard, welcome)
        force_view: Forcer une vue spécifique
    """
    
    def __init__(
        self,
        user_name: Optional[str] = None,
        default_month: Optional[str] = None,
        test_mode: str = "auto",
        force_view: bool = False,
    ):
        self.user_name = user_name or self._get_default_user_name()
        self.default_month = default_month
        self.test_mode = test_mode
        self.force_view = force_view
        self._has_data = has_transactions()
    
    def _get_default_user_name(self) -> str:
        """Récupère le nom d'utilisateur par défaut."""
        # TODO: Récupérer depuis les settings utilisateur
        return "Alex"
    
    def render(self) -> None:
        """Rend la page appropriée selon le mode et les données."""
        if self.test_mode == "auto" and not self.force_view:
            self._render_auto_mode()
        elif self.test_mode == "dashboard" or (self.force_view and self.test_mode == "auto"):
            self._render_dashboard_mode()
        else:  # welcome mode
            self._render_welcome_mode()
    
    def _render_auto_mode(self) -> None:
        """Mode auto: détecte et affiche la bonne vue."""
        if self._has_data:
            render_dashboard_v5(
                user_name=self.user_name,
                default_month=self.default_month,
            )
        else:
            render_welcome_screen(user_name=self.user_name)
    
    def _render_dashboard_mode(self) -> None:
        """Mode dashboard forcé."""
        if not self._has_data:
            st.info("💡 Mode démo avec données fictives")
            self._render_mock_dashboard()
        else:
            render_dashboard_v5(
                user_name=self.user_name,
                default_month=self.default_month,
            )
    
    def _render_welcome_mode(self) -> None:
        """Mode welcome forcé."""
        render_welcome_screen(
            user_name=self.user_name,
            dashboard_page="pages/Test_Dashboard.py"
        )
    
    def _render_mock_dashboard(self) -> None:
        """Affiche un dashboard avec des données fictives pour démo."""
        from modules.ui.v5_5.components import KPICard, KPIData
        from modules.ui.v5_5.components.dashboard_header import (
            DashboardHeader,
            get_current_month_name,
        )
        from modules.ui.v5_5.theme import apply_light_theme
        
        apply_light_theme()
        
        # Header
        DashboardHeader.render(
            user_name=self.user_name,
            current_month=get_current_month_name(),
        )
        
        # KPIs mock
        st.markdown("### 📊 Vue d'ensemble")
        
        kpis = [
            KPIData(
                "Reste à vivre",
                "1 847.52 €",
                "positive",
                "💚",
                "#DCFCE7",
                "+13.8%",
                "vs Janvier",
            ),
            KPIData(
                "Dépenses",
                "-2 152.48 €",
                "negative",
                "💳",
                "#FEE2E2",
                "-9.4%",
                "vs Janvier",
            ),
            KPIData(
                "Revenus",
                "4 200.00 €",
                "positive",
                "📈",
                "#DBEAFE",
                "+5.0%",
                "vs Janvier",
            ),
            KPIData(
                "Épargne",
                "200.00 €",
                "positive",
                "🎯",
                "#F3E8FF",
                None,
                "🎉 Premier versement !",
            ),
        ]
        
        cols = st.columns(4)
        for idx, kpi in enumerate(kpis):
            with cols[idx]:
                KPICard.render(kpi)
        
        st.success("✅ Dashboard affiché avec données de démonstration")
    
    def render_sidebar_config(self) -> str:
        """Rend les options de configuration dans la sidebar.
        
        Returns:
            Le mode de test sélectionné
        """
        st.sidebar.title("🔧 Configuration")
        
        test_mode = st.sidebar.radio(
            "Mode de test",
            options=[
                ("Auto (détection)", "auto"),
                ("Dashboard (avec données)", "dashboard"),
                ("Welcome (sans données)", "welcome"),
            ],
            format_func=lambda x: x[0],
            index=0,
        )[1]
        
        self.user_name = st.sidebar.text_input(
            "Nom utilisateur",
            value=self.user_name,
        )
        
        self.force_view = st.sidebar.checkbox(
            "Forcer la vue (ignore détection)",
            value=False,
        )
        
        st.sidebar.divider()
        st.sidebar.caption("FinancePerso V5.5")
        
        self.test_mode = test_mode
        return test_mode
    
    def has_data(self) -> bool:
        """Retourne True si l'utilisateur a des données."""
        return self._has_data
