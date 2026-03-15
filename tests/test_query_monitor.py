# -*- coding: utf-8 -*-
"""
Tests pour le monitoring des requêtes SQL.
"""

import time
from unittest.mock import Mock, patch

import pytest

from modules.db.query_monitor import (
    QueryMonitor,
    get_monitor,
    get_slow_queries,
    monitor_query,
    monitor_queries,
)
from modules.rate_limiter import (
    RateLimitExceeded,
    check_rate_limit,
    configure_rate_limit,
    get_rate_limiter,
)


class TestQueryMonitor:
    """Tests du moniteur de requêtes."""

    def test_monitor_singleton(self):
        """Le moniteur est accessible via get_monitor."""
        monitor1 = get_monitor()
        monitor2 = get_monitor()
        assert monitor1 is monitor2

    def test_log_query(self):
        """Log une requête exécutée."""
        monitor = QueryMonitor()
        monitor.reset_stats()
        
        monitor.log_query(
            query="SELECT * FROM transactions",
            params=None,
            execution_time=0.05,
            source="test",
        )
        
        stats = monitor.get_stats()
        assert stats["total_queries"] == 1

    def test_detect_slow_query(self):
        """Détecte les requêtes lentes."""
        monitor = QueryMonitor()
        monitor.reset_stats()
        monitor.slow_query_threshold = 0.01  # 10ms pour le test
        
        monitor.log_query(
            query="SELECT * FROM big_table",
            params=None,
            execution_time=0.5,  # Lent
            source="test",
        )
        
        slow = get_slow_queries(min_time=0.1)
        assert len(slow) >= 1

    def test_query_normalization(self):
        """Normalise les requêtes pour les stats."""
        monitor = QueryMonitor()
        
        # Deux requêtes similaires avec valeurs différentes
        monitor.log_query("SELECT * FROM t WHERE id = 1", None, 0.01)
        monitor.log_query("SELECT * FROM t WHERE id = 2", None, 0.01)
        
        stats = monitor.get_stats()
        # Devraient être comptées comme la même requête
        assert stats["unique_queries"] == 1

    def test_detect_n_plus_one(self):
        """Détecte les patterns N+1."""
        monitor = QueryMonitor()
        monitor.reset_stats()
        
        # Simuler un pattern N+1
        for i in range(10):
            monitor.log_query(
                f"SELECT * FROM transactions WHERE user_id = {i}",
                None,
                0.01,
            )
        
        suspects = monitor.detect_n_plus_one()
        assert len(suspects) >= 1

    def test_reset_stats(self):
        """Reset les statistiques."""
        monitor = QueryMonitor()
        
        monitor.log_query("SELECT 1", None, 0.01)
        monitor.reset_stats()
        
        stats = monitor.get_stats()
        assert stats["total_queries"] == 0


class TestMonitorContextManager:
    """Tests du context manager."""

    def test_monitor_query_context(self):
        """Monitor une requête avec context manager."""
        monitor = QueryMonitor()
        monitor.reset_stats()
        
        with monitor_query("SELECT * FROM test", source="test_context"):
            time.sleep(0.01)  # Simuler une requête
        
        stats = monitor.get_stats()
        assert stats["total_queries"] == 1


class TestMonitorDecorator:
    """Tests du décorateur."""

    def test_monitor_queries_decorator(self):
        """Décorateur pour monitorer une fonction."""
        monitor = QueryMonitor()
        monitor.reset_stats()
        
        @monitor_queries
        def fetch_data():
            time.sleep(0.01)
            return "data"
        
        result = fetch_data()
        
        assert result == "data"


class TestRateLimiter:
    """Tests du rate limiter."""

    def test_rate_limiter_singleton(self):
        """Le rate limiter est accessible."""
        limiter = get_rate_limiter()
        assert limiter is not None

    def test_configure_rate_limit(self):
        """Configure une limite."""
        configure_rate_limit("test_endpoint", requests=5, window=60)
        
        limiter = get_rate_limiter()
        assert "test_endpoint" in limiter._configs

    def test_rate_limit_allowed(self):
        """Requête autorisée sous la limite."""
        configure_rate_limit("allowed_test", requests=10, window=60)
        
        allowed, headers = check_rate_limit("allowed_test")
        
        assert allowed is True
        assert "X-RateLimit-Limit" in headers
        assert "X-RateLimit-Remaining" in headers

    def test_rate_limit_exceeded(self):
        """Exception quand limite dépassée."""
        configure_rate_limit("limited_test", requests=1, window=60)
        
        # Première requête OK
        check_rate_limit("limited_test")
        
        # Deuxième doit échouer
        with pytest.raises(RateLimitExceeded) as exc_info:
            check_rate_limit("limited_test")
        
        assert exc_info.value.retry_after > 0

    def test_rate_limit_remaining(self):
        """Compte les requêtes restantes."""
        configure_rate_limit("remaining_test", requests=5, window=60)
        
        limiter = get_rate_limiter()
        remaining_before = limiter.get_remaining("remaining_test")
        
        check_rate_limit("remaining_test")
        
        remaining_after = limiter.get_remaining("remaining_test")
        assert remaining_after == remaining_before - 1

    def test_rate_limit_reset(self):
        """Reset le compteur."""
        configure_rate_limit("reset_test", requests=1, window=60)
        
        check_rate_limit("reset_test")
        
        limiter = get_rate_limiter()
        limiter.reset("reset_test")
        
        # Devrait être à nouveau autorisé
        allowed, _ = check_rate_limit("reset_test")
        assert allowed is True


class TestRateLimitHeaders:
    """Tests des headers de rate limit."""

    def test_headers_on_allowed(self):
        """Headers présents quand autorisé."""
        configure_rate_limit("headers_test", requests=100, window=60)
        
        allowed, headers = check_rate_limit("headers_test")
        
        assert headers["X-RateLimit-Limit"] == "100"
        assert int(headers["X-RateLimit-Remaining"]) == 99

    def test_headers_on_denied(self):
        """Headers présents quand refusé."""
        configure_rate_limit("denied_headers_test", requests=1, window=60)
        
        check_rate_limit("denied_headers_test")  # Première OK
        
        with pytest.raises(RateLimitExceeded) as exc_info:
            check_rate_limit("denied_headers_test")
        
        assert exc_info.value.retry_after > 0
        assert exc_info.value.limit == 1
