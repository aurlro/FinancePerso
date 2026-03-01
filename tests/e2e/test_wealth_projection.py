"""
Test E2E: Projection patrimoniale complète
===========================================
Scénario: Actifs → Monte Carlo → Visualisation
"""

import pytest
from modules.wealth import WealthManager, project_wealth_evolution
from modules.wealth.math_engine import ScenarioType


class TestWealthProjection:
    """Test bout en bout des projections"""
    
    def test_full_projection_flow(self):
        """Test: Multi-actifs → Projection → Résultats"""
        # 1. Créer patrimoine
        manager = WealthManager()
        manager.set_cash_balance(10000)
        
        # 2. Projeter
        projection = project_wealth_evolution(
            wealth_manager=manager,
            years=5,
            monthly_contribution=500,
            n_simulations=100,  # Réduit pour test rapide
        )
        
        # 3. Vérifier résultats
        median = projection.get_net_worth_at_year(5)
        assert median > 10000  # Capital augmenté
        
        # 4. Vérifier cohérence
        p5 = projection.get_net_worth_at_year(5, 5)
        p95 = projection.get_net_worth_at_year(5, 95)
        assert p5 < median < p95  # Cône de probabilité cohérent
