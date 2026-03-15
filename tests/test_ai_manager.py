"""
Tests pour le gestionnaire IA unifié (ai_manager.py).

Couvre tous les providers:
- Gemini (cloud)
- OpenAI (cloud)
- DeepSeek (cloud)
- Ollama (local)
- ML Local (scikit-learn)
"""

from unittest.mock import Mock, patch

import pytest


class TestAIManagerSingleton:
    """Tests le pattern singleton du gestionnaire."""

    def test_singleton_instance(self):
        """Une seule instance existe."""
        from modules.ai_manager import get_ai_manager, reset_ai_manager

        reset_ai_manager()

        instance1 = get_ai_manager()
        instance2 = get_ai_manager()

        assert instance1 is instance2

    def test_reset_creates_new_instance(self):
        """Reset permet de créer une nouvelle instance."""
        from modules.ai_manager import get_ai_manager, reset_ai_manager

        instance1 = get_ai_manager()
        reset_ai_manager()
        instance2 = get_ai_manager()

        assert instance1 is not instance2


class TestProviderSelection:
    """Tests la sélection du provider IA."""

    @patch("modules.ai_manager.GEMINI_API_KEY", "fake_key")
    def test_selects_gemini_by_default(self):
        """Gemini est le provider par défaut."""
        from modules.ai_manager import get_ai_manager, reset_ai_manager

        reset_ai_manager()
        manager = get_ai_manager()

        assert manager.provider_name == "gemini"

    @patch("modules.ai_manager.AI_PROVIDER", "ollama")
    def test_selects_ollama_when_configured(self):
        """Respecte la configuration AI_PROVIDER."""
        from modules.ai_manager import get_ai_manager, reset_ai_manager

        reset_ai_manager()
        manager = get_ai_manager()

        assert manager.provider_name == "ollama"

    @patch("modules.ai_manager.GEMINI_API_KEY", None)
    @patch("modules.ai_manager.OPENAI_API_KEY", "fake_key")
    def test_fallback_to_openai(self):
        """Fallback sur OpenAI si Gemini non configuré."""
        from modules.ai_manager import get_ai_manager, reset_ai_manager

        reset_ai_manager()
        manager = get_ai_manager()

        assert manager.provider_name == "openai"


class TestGeminiProvider:
    """Tests le provider Gemini."""

    @patch("modules.ai_manager.genai")
    def test_gemini_categorization(self, mock_genai):
        """Gemini catégorise une transaction."""
        from modules.ai_manager import GeminiProvider

        # Mock la réponse
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Transport"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        provider = GeminiProvider(api_key="fake_key")
        result = provider.categorize("UBER TRIP", -12.50)

        assert result == "Transport"
        mock_model.generate_content.assert_called_once()

    @patch("modules.ai_manager.genai")
    def test_gemini_error_handling(self, mock_genai):
        """Gère les erreurs de l'API Gemini."""
        from modules.ai_manager import GeminiProvider

        mock_genai.GenerativeModel.side_effect = Exception("API Error")

        provider = GeminiProvider(api_key="fake_key")

        with pytest.raises(Exception):
            provider.categorize("TEST", -10.0)


class TestOllamaProvider:
    """Tests le provider Ollama (local)."""

    @patch("modules.ai_manager.requests.post")
    def test_ollama_categorization(self, mock_post):
        """Ollama catégorise une transaction."""
        from modules.ai_manager import OllamaProvider

        # Mock la réponse
        mock_post.return_value.json.return_value = {
            "response": "Alimentation"
        }
        mock_post.return_value.status_code = 200

        provider = OllamaProvider(base_url="http://localhost:11434")
        result = provider.categorize("RESTAURANT", -25.0)

        assert result == "Alimentation"

    @patch("modules.ai_manager.requests.post")
    def test_ollama_connection_error(self, mock_post):
        """Gère l'indisponibilité d'Ollama."""
        from modules.ai_manager import OllamaProvider

        mock_post.side_effect = Exception("Connection refused")

        provider = OllamaProvider(base_url="http://localhost:11434")

        with pytest.raises(Exception):
            provider.categorize("TEST", -10.0)


class TestCircuitBreaker:
    """Tests le circuit breaker."""

    def test_circuit_opens_after_failures(self):
        """Le circuit s'ouvre après N échecs."""
        from modules.ai_manager import CircuitBreaker

        cb = CircuitBreaker(failure_threshold=3)

        # Simule 3 échecs
        for _ in range(3):
            cb.record_failure()

        assert cb.is_open() is True

    def test_circuit_closes_after_timeout(self):
        """Le circuit se ferme après le timeout."""
        from modules.ai_manager import CircuitBreaker

        cb = CircuitBreaker(failure_threshold=1, timeout=0)
        cb.record_failure()

        # Timeout = 0, donc devrait être fermé immédiatement
        assert cb.is_open() is False

    def test_success_resets_failures(self):
        """Un succès reset le compteur d'échecs."""
        from modules.ai_manager import CircuitBreaker

        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()

        assert cb.failure_count == 0


class TestFallbackChain:
    """Tests la chaîne de fallback entre providers."""

    @patch("modules.ai_manager.get_ai_manager")
    def test_fallback_on_provider_failure(self, mock_get_manager):
        """Fallback sur provider suivant si échec."""
        from modules.ai_manager import categorize_with_fallback

        # Mock manager qui échoue
        mock_manager = Mock()
        mock_manager.categorize.side_effect = Exception("Provider down")
        mock_get_manager.return_value = mock_manager

        # Devrait retourner catégorie par défaut
        result = categorize_with_fallback("TEST", -10.0)

        assert result == "Inconnu"


class TestAICostTracking:
    """Tests le tracking des coûts API."""

    def test_tracks_api_calls(self):
        """Compte les appels API."""
        from modules.ai_manager import get_ai_manager, reset_ai_manager

        reset_ai_manager()
        manager = get_ai_manager()

        # Simule des appels
        manager._track_call(provider="gemini", tokens=100)
        manager._track_call(provider="gemini", tokens=150)

        stats = manager.get_usage_stats()
        assert stats["total_calls"] == 2
        assert stats["total_tokens"] == 250

    def test_resets_stats(self):
        """Reset les statistiques."""
        from modules.ai_manager import get_ai_manager, reset_ai_manager

        reset_ai_manager()
        manager = get_ai_manager()

        manager._track_call(provider="gemini", tokens=100)
        manager.reset_stats()

        stats = manager.get_usage_stats()
        assert stats["total_calls"] == 0


class TestLocalMLFallback:
    """Tests le fallback ML local."""

    @patch("modules.ai_manager.LocalMLProvider")
    def test_uses_local_ml_when_available(self, mock_ml_class):
        """Utilise ML local si modèle disponible."""
        from modules.ai_manager import LocalMLProvider

        mock_ml = Mock()
        mock_ml.is_available.return_value = True
        mock_ml.predict.return_value = "Transport"
        mock_ml_class.return_value = mock_ml

        provider = LocalMLProvider()
        result = provider.categorize("METRO", -2.0)

        assert result == "Transport"

    @patch("modules.ai_manager.LocalMLProvider")
    def test_skips_local_ml_when_unavailable(self, mock_ml_class):
        """Ignore ML local si modèle non entraîné."""
        from modules.ai_manager import LocalMLProvider

        mock_ml = Mock()
        mock_ml.is_available.return_value = False
        mock_ml_class.return_value = mock_ml

        provider = LocalMLProvider()

        # Devrait retourner None pour passer au provider suivant
        result = provider.categorize("TEST", -10.0)

        assert result is None


class TestAIBatchProcessing:
    """Tests le traitement par batch."""

    def test_batch_categorization(self):
        """Catégorise plusieurs transactions en un appel."""
        from modules.ai_manager import categorize_batch

        transactions = [
            {"label": "UBER", "amount": -12.0},
            {"label": "RESTAURANT", "amount": -25.0},
            {"label": "NETFLIX", "amount": -15.0},
        ]

        with patch("modules.ai_manager.get_ai_manager") as mock_get:
            mock_manager = Mock()
            mock_manager.categorize_batch.return_value = [
                "Transport", "Alimentation", "Abonnements"
            ]
            mock_get.return_value = mock_manager

            results = categorize_batch(transactions)

            assert len(results) == 3
            assert results[0] == "Transport"

    def test_batch_handles_partial_failures(self):
        """Gère les échecs partiels dans un batch."""
        from modules.ai_manager import categorize_batch

        transactions = [
            {"label": "A", "amount": -10.0},
            {"label": "B", "amount": -20.0},
        ]

        with patch("modules.ai_manager.get_ai_manager") as mock_get:
            mock_manager = Mock()
            mock_manager.categorize_batch.return_value = [
                "CatA", None  # Échec sur le deuxième
            ]
            mock_get.return_value = mock_manager

            results = categorize_batch(transactions)

            assert results[0] == "CatA"
            assert results[1] == "Inconnu"  # Fallback


class TestAIProviderHealth:
    """Tests la vérification de santé des providers."""

    @patch("modules.ai_manager.requests.get")
    def test_ollama_health_check(self, mock_get):
        """Vérifie la santé d'Ollama."""
        from modules.ai_manager import OllamaProvider

        mock_get.return_value.status_code = 200

        provider = OllamaProvider(base_url="http://localhost:11434")
        is_healthy = provider.health_check()

        assert is_healthy is True

    @patch("modules.ai_manager.genai")
    def test_gemini_health_check(self, mock_genai):
        """Vérifie la santé de Gemini."""
        from modules.ai_manager import GeminiProvider

        provider = GeminiProvider(api_key="fake_key")
        is_healthy = provider.health_check()

        # Gemini est considéré healthy si la clé est présente
        assert is_healthy is True
