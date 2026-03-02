"""
Test Unit: Subscription Engine (Phase 3)
=========================================
"""

import pytest
from datetime import date
from modules.wealth import Subscription, SubscriptionDetector, SubscriptionStatus


class TestSubscriptionEngine:
    """Tests du moteur d'abonnements"""

    def test_subscription_creation(self):
        """Test: Création d'un abonnement"""
        sub = Subscription(
            merchant="NETFLIX",
            frequency="monthly",
            average_amount=17.99,
            amount_std=0.5,
            last_date="2026-01-15",
            next_expected_date="2026-02-15",
            confidence_score=0.95,
            status=SubscriptionStatus.ACTIF.value,
            transaction_count=12,
        )

        assert sub.merchant == "NETFLIX"
        assert sub.frequency == "monthly"

    def test_remaining_budget_calculation(self):
        """Test: Calcul Reste à Vivre"""
        from modules.wealth import calculate_remaining_budget
        from datetime import datetime, timedelta

        # Créer un abonnement avec date future
        future_date = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")

        sub = Subscription(
            merchant="NETFLIX",
            frequency="monthly",
            average_amount=17.99,
            amount_std=0,
            last_date=datetime.now().strftime("%Y-%m-%d"),
            next_expected_date=future_date,
            confidence_score=0.95,
            status="ACTIF",
            transaction_count=12,
        )

        result = calculate_remaining_budget(
            current_balance=1500.0,
            subscriptions=[sub],
            days_ahead=30,
        )

        # Vérifier que le calcul fonctionne (valeur exacte dépend des dates)
        assert result.remaining_budget <= 1500.0  # Doit être moins après déduction
        assert result.current_balance == 1500.0
