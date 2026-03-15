"""
Tests pour le module de prédiction de trésorerie (cashflow).

Couvre:
- Prévisions de solde futur
- Détection de découvert potentiel
- Simulation de scénarios
"""

from datetime import date, timedelta
from unittest.mock import Mock, patch

import pandas as pd
import pytest


class TestCashflowPrediction:
    """Tests les prédictions de trésorerie."""

    def test_predict_balance_simple(self, temp_db):
        """Prédit le solde futur basique."""
        from modules.cashflow.predictor import predict_balance

        # Historique simple
        history = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=30, freq="D"),
            "amount": [-50.0] * 30  # Dépense quotidienne moyenne de 50€
        })

        prediction = predict_balance(
            current_balance=1000.0,
            daily_expenses_avg=50.0,
            days=30
        )

        # 1000 - (50 * 30) = -500
        assert prediction["final_balance"] == -500.0
        assert prediction["trend"] == "decreasing"

    def test_predict_balance_with_income(self, temp_db):
        """Prédit avec revenus réguliers."""
        from modules.cashflow.predictor import predict_balance_with_income

        prediction = predict_balance_with_income(
            current_balance=1000.0,
            daily_expenses_avg=50.0,
            monthly_income=2000.0,
            days=30
        )

        # Revenus quotidiens moyens: 2000/30 = 66.67
        # Solde change de: 66.67 - 50 = +16.67/jour
        assert prediction["final_balance"] > 1000.0
        assert prediction["trend"] == "increasing"

    def test_predict_balance_empty_history(self):
        """Gère l'historique vide."""
        from modules.cashflow.predictor import predict_balance_from_history

        empty_history = pd.DataFrame(columns=["date", "amount"])
        prediction = predict_balance_from_history(
            current_balance=1000.0,
            history=empty_history,
            days=30
        )

        # Sans historique, maintient le solde actuel
        assert prediction["final_balance"] == 1000.0


class TestOverdraftDetection:
    """Tests la détection de découvert."""

    def test_detects_overdraft_risk(self):
        """Détecte un risque de découvert."""
        from modules.cashflow.risk import detect_overdraft_risk

        future_transactions = pd.DataFrame({
            "date": pd.date_range("2024-03-01", periods=10, freq="D"),
            "amount": [-100.0] * 10  # Dépenses importantes
        })

        risk = detect_overdraft_risk(
            current_balance=500.0,
            future_transactions=future_transactions
        )

        assert risk["has_risk"] is True
        assert risk["risk_date"] is not None
        assert risk["recommended_action"] is not None

    def test_no_risk_with_sufficient_balance(self):
        """Pas de risque avec solde suffisant."""
        from modules.cashflow.risk import detect_overdraft_risk

        future_transactions = pd.DataFrame({
            "date": pd.date_range("2024-03-01", periods=10, freq="D"),
            "amount": [-10.0] * 10
        })

        risk = detect_overdraft_risk(
            current_balance=1000.0,
            future_transactions=future_transactions
        )

        assert risk["has_risk"] is False

    def test_overdraft_date_calculation(self):
        """Calcule correctement la date de découvert."""
        from modules.cashflow.risk import calculate_overdraft_date

        overdraft_date = calculate_overdraft_date(
            current_balance=500.0,
            daily_expense_rate=50.0,
            start_date=date(2024, 3, 1)
        )

        # 500 / 50 = 10 jours
        expected_date = date(2024, 3, 11)
        assert overdraft_date == expected_date


class TestRecurringExpenses:
    """Tests la gestion des dépenses récurrentes."""

    def test_identify_recurring_expenses(self):
        """Identifie les dépenses récurrentes."""
        from modules.cashflow.recurring import identify_recurring_expenses

        history = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01"]),
            "label": ["LOYER", "LOYER", "LOYER"],
            "amount": [-800.0, -800.0, -800.0]
        })

        recurring = identify_recurring_expenses(history)

        assert len(recurring) > 0
        assert recurring[0]["label"] == "LOYER"
        assert recurring[0]["amount"] == -800.0
        assert recurring[0]["frequency"] == "monthly"

    def test_project_recurring_expenses(self):
        """Projette les dépenses récurrentes futures."""
        from modules.cashflow.recurring import project_recurring_expenses

        recurring = [
            {"label": "LOYER", "amount": -800.0, "frequency": "monthly", "day": 1},
            {"label": "NETFLIX", "amount": -15.99, "frequency": "monthly", "day": 15},
        ]

        projections = project_recurring_expenses(
            recurring,
            start_date=date(2024, 3, 1),
            months=3
        )

        assert len(projections) > 0
        # Devrait avoir des projections pour les 3 mois
        assert any(p["label"] == "LOYER" for p in projections)


class TestCashflowSimulation:
    """Tests les simulations de scénarios."""

    def test_simulate_expense_reduction(self):
        """Simule une réduction de dépenses."""
        from modules.cashflow.simulation import simulate_scenario

        result = simulate_scenario(
            current_balance=500.0,
            daily_expenses_avg=50.0,
            days=30,
            expense_reduction_percent=20  # Réduction de 20%
        )

        # Dépenses réduites: 50 * 0.8 = 40€/jour
        # Nouveau solde: 500 - (40 * 30) = -700
        assert result["final_balance"] > -1000.0  # Mieux que sans réduction

    def test_simulate_extra_income(self):
        """Simule un revenu supplémentaire."""
        from modules.cashflow.simulation import simulate_scenario

        result = simulate_scenario(
            current_balance=500.0,
            daily_expenses_avg=50.0,
            days=30,
            extra_income=1000.0  # Prime de 1000€
        )

        # Avec revenu supplémentaire: 500 + 1000 - 1500 = 0
        assert result["final_balance"] == 0.0

    def test_simulate_multiple_changes(self):
        """Simule plusieurs changements simultanés."""
        from modules.cashflow.simulation import simulate_scenario

        result = simulate_scenario(
            current_balance=500.0,
            daily_expenses_avg=50.0,
            days=30,
            expense_reduction_percent=10,
            extra_income=500.0
        )

        # Les deux facteurs devraient améliorer le résultat
        assert result["final_balance"] > -1000.0


class TestCashflowAlerts:
    """Tests les alertes de trésorerie."""

    def test_generate_low_balance_alert(self):
        """Génère une alerte si solde bas."""
        from modules.cashflow.alerts import generate_cashflow_alerts

        alerts = generate_cashflow_alerts(
            current_balance=100.0,
            predicted_lowest_balance=-50.0,
            overdraft_risk=True
        )

        assert len(alerts) > 0
        assert any(a["level"] == "warning" for a in alerts)
        assert any("découvert" in a["message"].lower() for a in alerts)

    def test_no_alert_when_healthy(self):
        """Pas d'alerte si trésorerie saine."""
        from modules.cashflow.alerts import generate_cashflow_alerts

        alerts = generate_cashflow_alerts(
            current_balance=5000.0,
            predicted_lowest_balance=2000.0,
            overdraft_risk=False
        )

        assert len(alerts) == 0


class TestCashflowVisualization:
    """Tests la préparation des données pour visualisation."""

    def test_prepare_timeline_data(self):
        """Prépare les données pour timeline."""
        from modules.cashflow.visualization import prepare_timeline_data

        data = prepare_timeline_data(
            current_balance=1000.0,
            predictions=[
                {"date": date(2024, 3, 1), "balance": 950.0},
                {"date": date(2024, 3, 15), "balance": 800.0},
                {"date": date(2024, 3, 30), "balance": 500.0},
            ]
        )

        assert "dates" in data
        assert "balances" in data
        assert len(data["dates"]) == 3
        assert len(data["balances"]) == 3

    def test_identify_critical_points(self):
        """Identifie les points critiques sur la timeline."""
        from modules.cashflow.visualization import identify_critical_points

        predictions = [
            {"date": date(2024, 3, 1), "balance": 1000.0},
            {"date": date(2024, 3, 15), "balance": -100.0},  # Découvert
            {"date": date(2024, 3, 30), "balance": 500.0},
        ]

        critical = identify_critical_points(predictions)

        assert len(critical) > 0
        assert any(c["date"] == date(2024, 3, 15) for c in critical)
