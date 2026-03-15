"""
Tests pour le module de gestion du patrimoine (wealth).

Couvre:
- Calcul de la valeur totale du patrimoine
- Suivi des actifs (immobilier, épargne, investissements)
- Objectifs d'épargne
- Projections de patrimoine
"""

from datetime import date
from unittest.mock import Mock, patch

import pandas as pd
import pytest


class TestWealthCalculation:
    """Tests le calcul de la valeur du patrimoine."""

    def test_calculate_total_wealth(self, temp_db):
        """Calcule la valeur totale du patrimoine."""
        from modules.wealth.calculator import calculate_total_wealth

        assets = [
            {"type": "real_estate", "value": 250000.0},
            {"type": "savings", "value": 50000.0},
            {"type": "investments", "value": 100000.0},
        ]

        total = calculate_total_wealth(assets)

        assert total == 400000.0

    def test_calculate_wealth_with_liabilities(self):
        """Calcule le patrimoine net (actifs - dettes)."""
        from modules.wealth.calculator import calculate_net_worth

        assets = [
            {"type": "real_estate", "value": 250000.0},
            {"type": "savings", "value": 50000.0},
        ]
        liabilities = [
            {"type": "mortgage", "value": 150000.0},
            {"type": "loan", "value": 10000.0},
        ]

        net_worth = calculate_net_worth(assets, liabilities)

        # (250000 + 50000) - (150000 + 10000) = 140000
        assert net_worth == 140000.0

    def test_wealth_by_category(self):
        """Calcule la répartition par catégorie."""
        from modules.wealth.calculator import calculate_wealth_by_category

        assets = [
            {"type": "real_estate", "value": 250000.0, "category": "immobilier"},
            {"type": "savings", "value": 50000.0, "category": "liquide"},
            {"type": "checking", "value": 20000.0, "category": "liquide"},
        ]

        by_category = calculate_wealth_by_category(assets)

        assert by_category["immobilier"] == 250000.0
        assert by_category["liquide"] == 70000.0


class TestAssetManagement:
    """Tests la gestion des actifs."""

    def test_add_asset(self, temp_db):
        """Ajoute un nouvel actif."""
        from modules.wealth.assets import add_asset, get_assets

        add_asset(
            name="Appartement Paris",
            asset_type="real_estate",
            value=350000.0,
            acquisition_date=date(2020, 1, 15)
        )

        assets = get_assets()
        assert len(assets) > 0
        assert any(a["name"] == "Appartement Paris" for a in assets)

    def test_update_asset_value(self, temp_db):
        """Met à jour la valeur d'un actif."""
        from modules.wealth.assets import add_asset, update_asset_value, get_asset

        asset_id = add_asset(
            name="Actions Tesla",
            asset_type="investment",
            value=10000.0
        )

        update_asset_value(asset_id, 12000.0, valuation_date=date.today())

        asset = get_asset(asset_id)
        assert asset["value"] == 12000.0

    def test_delete_asset(self, temp_db):
        """Supprime un actif."""
        from modules.wealth.assets import add_asset, delete_asset, get_asset

        asset_id = add_asset(
            name="Test Asset",
            asset_type="savings",
            value=1000.0
        )

        delete_asset(asset_id)

        asset = get_asset(asset_id)
        assert asset is None


class TestSavingsGoals:
    """Tests les objectifs d'épargne."""

    def test_create_savings_goal(self, temp_db):
        """Crée un objectif d'épargne."""
        from modules.wealth.goals import create_savings_goal, get_savings_goals

        create_savings_goal(
            name="Vacances Été",
            target_amount=3000.0,
            deadline=date(2024, 6, 1),
            current_amount=1000.0
        )

        goals = get_savings_goals()
        assert len(goals) > 0
        assert any(g["name"] == "Vacances Été" for g in goals)

    def test_calculate_goal_progress(self):
        """Calcule la progression vers un objectif."""
        from modules.wealth.goals import calculate_goal_progress

        progress = calculate_goal_progress(
            target_amount=10000.0,
            current_amount=2500.0
        )

        assert progress["percentage"] == 25.0
        assert progress["remaining"] == 7500.0
        assert progress["is_achieved"] is False

    def test_goal_achievement_detection(self):
        """Détecte quand un objectif est atteint."""
        from modules.wealth.goals import calculate_goal_progress

        progress = calculate_goal_progress(
            target_amount=5000.0,
            current_amount=5000.0
        )

        assert progress["is_achieved"] is True
        assert progress["percentage"] == 100.0

    def test_estimate_goal_completion(self):
        """Estime la date de complétion."""
        from modules.wealth.goals import estimate_completion_date

        estimation = estimate_completion_date(
            target_amount=10000.0,
            current_amount=2000.0,
            monthly_saving_rate=500.0
        )

        # Il manque 8000€, à 500€/mois = 16 mois
        assert estimation["months_remaining"] == 16
        assert estimation["estimated_date"] is not None


class TestWealthProjection:
    """Tests les projections de patrimoine."""

    def test_project_wealth_simple(self):
        """Projette l'évolution du patrimoine."""
        from modules.wealth.projection import project_wealth

        projection = project_wealth(
            current_wealth=100000.0,
            monthly_savings=500.0,
            annual_return_rate=0.05,
            years=10
        )

        assert len(projection) == 11  # Année 0 + 10 années
        # Le patrimoine devrait augmenter
        assert projection[-1]["total"] > projection[0]["total"]

    def test_project_with_compound_interest(self):
        """Calcule les intérêts composés."""
        from modules.wealth.projection import calculate_compound_growth

        final_value = calculate_compound_growth(
            principal=10000.0,
            monthly_contribution=200.0,
            annual_rate=0.07,
            years=10
        )

        # Avec intérêts composés + contributions
        assert final_value > 10000.0 + (200 * 12 * 10)  # Plus que juste les contributions

    def test_project_wealth_breakdown(self):
        """Projette avec détail par type d'actif."""
        from modules.wealth.projection import project_wealth_breakdown

        assets = {
            "real_estate": {"value": 200000.0, "growth_rate": 0.03},
            "stocks": {"value": 50000.0, "growth_rate": 0.08},
            "bonds": {"value": 30000.0, "growth_rate": 0.02},
        }

        projection = project_wealth_breakdown(
            assets=assets,
            monthly_savings=500.0,
            years=5
        )

        assert "real_estate" in projection[-1]
        assert "stocks" in projection[-1]
        assert "total" in projection[-1]


class TestInvestmentTracking:
    """Tests le suivi des investissements."""

    def test_calculate_roi(self):
        """Calcule le retour sur investissement."""
        from modules.wealth.investments import calculate_roi

        roi = calculate_roi(
            initial_value=10000.0,
            current_value=12500.0,
            dividends=500.0
        )

        # (12500 + 500 - 10000) / 10000 = 30%
        assert roi["percentage"] == 30.0
        assert roi["absolute"] == 3000.0

    def test_calculate_annualized_return(self):
        """Calcule le rendement annualisé."""
        from modules.wealth.investments import calculate_annualized_return

        annualized = calculate_annualized_return(
            initial_value=10000.0,
            final_value=14641.0,
            years=4
        )

        # (14641/10000)^(1/4) - 1 = 0.10 (10%)
        assert abs(annualized - 0.10) < 0.001

    def test_track_dividend_income(self, temp_db):
        """Suit les revenus de dividendes."""
        from modules.wealth.investments import add_dividend, get_dividend_history

        add_dividend(
            asset_id=1,
            amount=150.0,
            date=date(2024, 3, 15),
            source="AAPL"
        )

        dividends = get_dividend_history()
        assert len(dividends) > 0
        assert dividends[0]["amount"] == 150.0


class TestRealEstateTracking:
    """Tests le suivi immobilier."""

    def test_add_property(self, temp_db):
        """Ajoute un bien immobilier."""
        from modules.wealth.real_estate import add_property, get_properties

        add_property(
            name="Résidence Principale",
            address="123 Rue de Paris",
            purchase_price=300000.0,
            current_value=350000.0,
            mortgage_remaining=150000.0
        )

        properties = get_properties()
        assert len(properties) > 0

    def test_calculate_property_equity(self):
        """Calcule la plus-value immobilière."""
        from modules.wealth.real_estate import calculate_equity

        equity = calculate_equity(
            current_value=400000.0,
            mortgage_remaining=200000.0
        )

        assert equity == 200000.0

    def test_calculate_rental_yield(self):
        """Calcule le rendement locatif."""
        from modules.wealth.real_estate import calculate_rental_yield

        yield_rate = calculate_rental_yield(
            annual_rent=12000.0,
            property_value=200000.0,
            expenses=2000.0
        )

        # (12000 - 2000) / 200000 = 5%
        assert yield_rate == 0.05


class TestWealthHistory:
    """Tests l'historique du patrimoine."""

    def test_record_wealth_snapshot(self, temp_db):
        """Enregistre un snapshot du patrimoine."""
        from modules.wealth.history import record_wealth_snapshot, get_wealth_history

        record_wealth_snapshot(
            total_wealth=150000.0,
            date=date(2024, 3, 1)
        )

        history = get_wealth_history()
        assert len(history) > 0

    def test_calculate_wealth_growth(self):
        """Calcule la croissance du patrimoine sur une période."""
        from modules.wealth.history import calculate_wealth_growth

        history = [
            {"date": date(2023, 1, 1), "total": 100000.0},
            {"date": date(2024, 1, 1), "total": 115000.0},
        ]

        growth = calculate_wealth_growth(history)

        assert growth["absolute"] == 15000.0
        assert growth["percentage"] == 15.0
