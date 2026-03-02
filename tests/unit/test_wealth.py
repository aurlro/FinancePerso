"""
Test Unit: Wealth Manager (Phase 5)
====================================
"""

import pytest
from datetime import date
from modules.wealth import WealthManager, RealEstateAsset, MortgageSchedule


class TestWealthManager:
    """Tests de gestion patrimoniale"""

    def test_wealth_manager_creation(self):
        """Test: Création du gestionnaire"""
        manager = WealthManager()
        manager.set_cash_balance(10000)

        assert manager.cash_balance == 10000
        assert manager.get_total_net_worth() == 10000

    def test_real_estate_equity(self):
        """Test: Calcul équité immobilière"""
        mortgage = MortgageSchedule(
            principal=300000,
            monthly_payment=1200,
            interest_rate=0.023,
            start_date=date(2020, 1, 15),
            duration_months=240,
        )

        apartment = RealEstateAsset(
            id="apt-001",
            name="Appartement Test",
            address="123 Rue Test",
            purchase_price=350000,
            current_value=420000,
            purchase_date=date(2020, 1, 15),
            mortgage=mortgage,
        )

        equity = apartment.get_equity()

        # Équité = Valeur - Capital restant
        assert equity > 0
        assert equity < 420000
