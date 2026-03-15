# -*- coding: utf-8 -*-
"""
Tests pour le cache IA.
"""

import time
from unittest.mock import patch

import pytest

from modules.ai_cache import (
    AICache,
    cache_categorization_result,
    get_cached_categorization,
    get_ai_cache,
    invalidate_ai_cache,
)


class TestAICache:
    """Tests du cache IA."""

    def test_cache_singleton(self):
        """Le cache est un singleton."""
        cache1 = AICache()
        cache2 = AICache()
        assert cache1 is cache2

    def test_cache_set_and_get(self, temp_db):
        """Stocke et récupère du cache."""
        cache = AICache()
        
        cache.set(
            label="NETFLIX SUBSCRIPTION",
            amount=-15.99,
            provider="gemini",
            category="Abonnements",
            confidence=0.95,
        )
        
        result = cache.get("NETFLIX SUBSCRIPTION", -15.99, "gemini")
        
        assert result is not None
        assert result.category == "Abonnements"
        assert result.confidence == 0.95

    def test_cache_miss(self, temp_db):
        """Retourne None si pas dans le cache."""
        cache = AICache()
        
        result = cache.get("UNKNOWN LABEL", -999.0, "gemini")
        
        assert result is None

    def test_cache_key_normalization(self, temp_db):
        """Normalise les labels pour les clés."""
        cache = AICache()
        
        # Stocke avec un label
        cache.set("NETFLIX 12345", -15.99, "gemini", "Abonnements", 0.9)
        
        # Récupère avec un label similaire (numéro différent)
        result = cache.get("NETFLIX 99999", -15.99, "gemini")
        
        # Devrait matcher car les numéros sont supprimés
        assert result is not None
        assert result.category == "Abonnements"

    def test_cache_expiration(self, temp_db):
        """Le cache expire après TTL."""
        cache = AICache()
        
        cache.set(
            "TEST LABEL",
            -10.0,
            "gemini",
            "Test",
            0.9,
            ttl=0,  # Expire immédiatement
        )
        
        result = cache.get("TEST LABEL", -10.0, "gemini")
        assert result is None

    def test_cache_hit_count(self, temp_db):
        """Compte les hits du cache."""
        cache = AICache()
        
        cache.set("TEST", -10.0, "gemini", "Cat", 0.9)
        
        # Plusieurs accès
        cache.get("TEST", -10.0, "gemini")
        cache.get("TEST", -10.0, "gemini")
        cache.get("TEST", -10.0, "gemini")
        
        stats = cache.get_stats()
        assert stats["total_hits"] >= 3

    def test_cache_invalidation(self, temp_db):
        """Invalide le cache."""
        cache = AICache()
        
        cache.set("TEST1", -10.0, "gemini", "Cat1", 0.9)
        cache.set("TEST2", -20.0, "gemini", "Cat2", 0.9)
        
        deleted = cache.invalidate()
        
        assert deleted == 2
        assert cache.get("TEST1", -10.0, "gemini") is None

    def test_cache_cleanup(self, temp_db):
        """Nettoie les entrées expirées."""
        cache = AICache()
        
        # Créer une entrée expirée
        cache.set("OLD", -10.0, "gemini", "Cat", 0.9, ttl=-1)
        
        # Forcer le cleanup
        cache._maybe_cleanup()
        
        # L'entrée devrait être supprimée
        assert cache.get("OLD", -10.0, "gemini") is None


class TestAICacheHelpers:
    """Tests des fonctions utilitaires."""

    def test_cache_categorization_result(self, temp_db):
        """Helper pour cacher un résultat."""
        cache_categorization_result(
            label="UBER TRIP",
            amount=-12.50,
            provider="gemini",
            category="Transport",
            confidence=0.92,
        )
        
        category = get_cached_categorization("UBER TRIP", -12.50, "gemini")
        assert category == "Transport"

    def test_get_cached_categorization_miss(self, temp_db):
        """Retourne None si pas en cache."""
        result = get_cached_categorization("UNKNOWN", -999, "gemini")
        assert result is None

    def test_invalidate_ai_cache(self, temp_db):
        """Invalide tout le cache."""
        cache_categorization_result("TEST", -10, "gemini", "Cat", 0.9)
        
        deleted = invalidate_ai_cache()
        
        assert deleted >= 1


class TestAICacheStats:
    """Tests des statistiques du cache."""

    def test_cache_stats(self, temp_db):
        """Retourne les statistiques."""
        cache = AICache()
        
        # Ajouter des entrées
        cache.set("TEST1", -10, "gemini", "Cat1", 0.9)
        cache.set("TEST2", -20, "ollama", "Cat2", 0.8)
        
        # Accéder pour générer des hits
        cache.get("TEST1", -10, "gemini")
        
        stats = cache.get_stats()
        
        assert "total_entries" in stats
        assert "total_hits" in stats
        assert "by_provider" in stats
        assert stats["total_entries"] >= 2

    def test_stats_by_provider(self, temp_db):
        """Stats regroupées par provider."""
        cache = AICache()
        
        cache.set("A", -10, "gemini", "Cat", 0.9)
        cache.set("B", -20, "gemini", "Cat", 0.9)
        cache.set("C", -30, "ollama", "Cat", 0.9)
        
        stats = cache.get_stats()
        
        assert stats["by_provider"]["gemini"] == 2
        assert stats["by_provider"]["ollama"] == 1
