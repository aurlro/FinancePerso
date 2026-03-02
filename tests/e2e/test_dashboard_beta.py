"""Tests E2E pour Dashboard Beta V5.5.

Usage:
    pytest tests/e2e/test_dashboard_beta.py -v --headed

Requirements:
    - Streamlit doit tourner sur http://localhost:8501
    - Playwright doit être installé
"""

import pytest
import time
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8501"
DASHBOARD_BETA_URL = f"{BASE_URL}/Dashboard_Beta"


@pytest.fixture(scope="module")
def browser_context_args(browser_context_args):
    """Configuration du contexte navigateur."""
    return {
        **browser_context_args,
        "viewport": {"width": 1440, "height": 900},
    }


class TestDashboardBetaLoading:
    """Tests de chargement de la page."""

    def test_page_loads(self, page: Page):
        """Test que la page se charge correctement."""
        page.goto(DASHBOARD_BETA_URL)

        # Attendre que le titre soit visible
        expect(page).to_have_title("Dashboard Beta V5.5")

    def test_header_displays(self, page: Page):
        """Test que le header s'affiche."""
        page.goto(DASHBOARD_BETA_URL)

        # Vérifier le header
        header = page.get_by_text("Bonjour,")
        expect(header).to_be_visible()

    def test_kpi_cards_display(self, page: Page):
        """Test que les KPI cards s'affichent."""
        page.goto(DASHBOARD_BETA_URL)

        # Vérifier les 4 KPIs
        kpis = ["Reste à vivre", "Dépenses", "Revenus", "Épargne"]
        for kpi in kpis:
            expect(page.get_by_text(kpi)).to_be_visible()


class TestDashboardBetaNavigation:
    """Tests de navigation."""

    def test_sidebar_navigation(self, page: Page):
        """Test la navigation depuis la sidebar."""
        page.goto(DASHBOARD_BETA_URL)

        # Cliquer sur le menu
        page.get_by_role("button", name="View less").click()

        # Vérifier que Dashboard Beta est dans la liste
        expect(page.get_by_text("Dashboard Beta")).to_be_visible()

    def test_import_button(self, page: Page):
        """Test le bouton d'import."""
        page.goto(DASHBOARD_BETA_URL)

        # Cliquer sur le bouton import
        import_btn = page.get_by_role("button", name="Importer des opérations")
        expect(import_btn).to_be_visible()


class TestDashboardBetaFeatures:
    """Tests des fonctionnalités."""

    def test_month_selector(self, page: Page):
        """Test le sélecteur de mois."""
        page.goto(DASHBOARD_BETA_URL)

        # Vérifier que le sélecteur existe
        selector = page.get_by_role("combobox").first
        expect(selector).to_be_visible()

    def test_expenses_chart_section(self, page: Page):
        """Test la section graphique dépenses."""
        page.goto(DASHBOARD_BETA_URL)

        # Vérifier le titre de la section
        expect(page.get_by_text("Répartition des dépenses")).to_be_visible()

    def test_transactions_section(self, page: Page):
        """Test la section transactions."""
        page.goto(DASHBOARD_BETA_URL)

        # Vérifier le titre de la section
        expect(page.get_by_text("Transactions récentes")).to_be_visible()


class TestDashboardBetaResponsive:
    """Tests responsive."""

    def test_mobile_viewport(self, page: Page):
        """Test avec un viewport mobile."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(DASHBOARD_BETA_URL)

        # La page devrait toujours charger
        expect(page).to_have_title("Dashboard Beta V5.5")

    def test_tablet_viewport(self, page: Page):
        """Test avec un viewport tablette."""
        page.set_viewport_size({"width": 768, "height": 1024})
        page.goto(DASHBOARD_BETA_URL)

        # La page devrait toujours charger
        expect(page).to_have_title("Dashboard Beta V5.5")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
