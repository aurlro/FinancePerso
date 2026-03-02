"""
Test Intégration: Performance critique
=======================================
"""

import time
import pytest
from modules.wealth import quick_simulation, MonteCarloSimulator
from modules.wealth.math_engine import ScenarioType


class TestPerformance:
    """Tests de performance"""

    def test_monte_carlo_speed(self):
        """Test: 1000 simulations en <2 secondes"""
        start = time.time()

        result = quick_simulation(
            initial_capital=10000,
            monthly_contribution=500,
            years=10,
            scenario=ScenarioType.MODERE,
            n_simulations=1000,
        )

        elapsed = time.time() - start

        assert elapsed < 2.0, f"Trop lent: {elapsed:.2f}s"
        assert result["median"] > 0

    def test_cache_efficiency(self):
        """Test: Cache réduit le temps de calcul"""
        from modules.performance import AdvancedCache

        cache = AdvancedCache()

        @cache.decorator(ttl_seconds=60)
        def expensive_calculation(x):
            time.sleep(0.1)
            return x * 2

        # Premier appel (lent)
        start = time.time()
        expensive_calculation(5)
        first_time = time.time() - start

        # Second appel (cache, rapide)
        start = time.time()
        expensive_calculation(5)
        second_time = time.time() - start

        assert second_time < first_time / 10  # Cache 10x plus rapide
