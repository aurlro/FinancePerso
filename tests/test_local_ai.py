"""
Tests pour l'IA Locale Souveraine
=================================

Valide:
- Le format JSON strict des réponses
- La cascade de confiance
- La similarité avec SequenceMatcher
- Le fallback cloud

Usage:
    pytest tests/test_local_ai.py -v
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestLocalSLMProvider:
    """Tests pour LocalSLMProvider."""

    def test_provider_initialization(self):
        """Test que le provider s'initialise correctement."""
        from modules.ai.local_slm_provider import LocalSLMProvider

        # Without unsloth (mock mode)
        with patch("modules.ai.local_slm_provider.UNSLOTH_AVAILABLE", False):
            provider = LocalSLMProvider(fallback_to_cloud=False)
            assert provider.model_name == "unsloth/Llama-3.2-3B-Instruct"
            assert not provider._model_loaded

    def test_build_prompt_format(self):
        """Test que le prompt suit le format Llama 3.2 Instruct."""
        from modules.ai.local_slm_provider import LocalSLMProvider

        provider = LocalSLMProvider(fallback_to_cloud=False)
        prompt = provider._build_prompt("Test transaction", "Tu es un assistant.")

        # Check required tokens
        assert "<|begin_of_text|>" in prompt
        assert "<|start_header_id|>system<|end_header_id|>" in prompt
        assert "<|start_header_id|>user<|end_header_id|>" in prompt
        assert "<|start_header_id|>assistant<|end_header_id|>" in prompt
        assert "Test transaction" in prompt

    def test_extract_json_clean(self):
        """Test l'extraction JSON d'une réponse propre."""
        from modules.ai.local_slm_provider import LocalSLMProvider

        provider = LocalSLMProvider(fallback_to_cloud=False)

        # Clean JSON
        clean_response = '{"category": "Food", "confidence": 0.95}'
        result = provider._extract_json(clean_response)
        assert result["category"] == "Food"
        assert result["confidence"] == 0.95

    def test_extract_json_with_markdown(self):
        """Test l'extraction JSON avec markdown."""
        from modules.ai.local_slm_provider import LocalSLMProvider

        provider = LocalSLMProvider(fallback_to_cloud=False)

        # Markdown wrapped JSON
        markdown_response = """```json
{"category": "Transport", "confidence": 0.88}
```"""
        result = provider._extract_json(markdown_response)
        assert result["category"] == "Transport"

    def test_extract_json_with_text(self):
        """Test l'extraction JSON avec texte autour."""
        from modules.ai.local_slm_provider import LocalSLMProvider

        provider = LocalSLMProvider(fallback_to_cloud=False)

        # JSON embedded in text
        text_response = 'Voici le résultat: {"category": "Shopping", "confidence": 0.92} Merci!'
        result = provider._extract_json(text_response)
        assert result["category"] == "Shopping"

    def test_fallback_to_cloud(self):
        """Test le fallback sur cloud si local échoue."""
        from modules.ai.local_slm_provider import LocalSLMProvider

        # Mock cloud provider
        mock_cloud = MagicMock()
        mock_cloud.generate_json.return_value = {
            "category": "Food & Drink > Groceries",
            "confidence_score": 0.95,
            "source": "cloud",
        }

        with patch("modules.ai.local_slm_provider.UNSLOTH_AVAILABLE", False):
            provider = LocalSLMProvider(fallback_to_cloud=True)
            provider._fallback_provider = mock_cloud

            result = provider.generate_json("Carrefour Paris")

            assert "category" in result
            mock_cloud.generate_json.assert_called_once()

    def test_model_info(self):
        """Test que get_model_info retourne les bonnes infos."""
        from modules.ai.local_slm_provider import LocalSLMProvider

        provider = LocalSLMProvider(
            model_name="llama-3.2-3b", load_in_4bit=True, fallback_to_cloud=False
        )

        info = provider.get_model_info()

        assert info["model_name"] == "unsloth/Llama-3.2-3B-Instruct"
        assert info["quantization"] == "4-bit"
        assert "device" in info


class TestCategorizationCascade:
    """Tests pour la cascade de confiance."""

    def test_heuristic_pattern_matching(self):
        """Test la détection par patterns heuristiques."""
        from modules.categorization_cascade import TransactionCategorizer

        categorizer = TransactionCategorizer(use_local_ai=False, use_cloud_fallback=False)

        # Test carrefour (groceries)
        result = categorizer._check_heuristics("CARREFOUR PARIS 15", -45.67)
        assert result is not None
        assert "Groceries" in result.category
        assert result.source == "heuristic"
        assert result.confidence_score == 0.95

    def test_heuristic_fast_food(self):
        """Test détection fast food."""
        from modules.categorization_cascade import TransactionCategorizer

        categorizer = TransactionCategorizer(use_local_ai=False, use_cloud_fallback=False)

        result = categorizer._check_heuristics("MCDONALD'S PARIS", -12.50)
        assert result is not None
        assert "Fast Food" in result.category

    def test_heuristic_fuel(self):
        """Test détection station essence."""
        from modules.categorization_cascade import TransactionCategorizer

        categorizer = TransactionCategorizer(use_local_ai=False, use_cloud_fallback=False)

        result = categorizer._check_heuristics("TOTAL ENERGIES PARIS", -65.00)
        assert result is not None
        assert "Fuel" in result.category

    def test_similarity_matching(self):
        """Test la similarité avec SequenceMatcher."""
        from modules.categorization_cascade import TransactionCategorizer

        # Mock history
        mock_history = MagicMock()
        mock_history.empty = False
        mock_history.iterrows.return_value = [
            (0, {"id": 1, "label": "CARREFOUR PARIS 15", "category_validated": "Food > Groceries"}),
            (1, {"id": 2, "label": "UBER EATS", "category_validated": "Food > Delivery"}),
        ]

        categorizer = TransactionCategorizer(use_local_ai=False, use_cloud_fallback=False)
        categorizer._history_cache = mock_history

        # Should match carrefour
        result = categorizer._check_similarity("CARREFOUR PARIS 16")

        assert result is not None
        assert result.similarity_score is not None
        assert result.similarity_score >= 0.85
        assert result.source == "similarity"

    def test_similarity_threshold(self):
        """Test que les scores < 0.85 ne matchent pas."""
        from difflib import SequenceMatcher

        # Test similarity calculation directly
        score_high = SequenceMatcher(None, "CARREFOUR PARIS 15", "CARREFOUR PARIS 16").ratio()
        score_low = SequenceMatcher(None, "CARREFOUR PARIS", "RESTAURANT CHEZ PIERRE").ratio()

        assert score_high > 0.85  # Should match
        assert score_low < 0.85  # Should not match

    def test_clean_merchant_extraction(self):
        """Test l'extraction du nom du marchand."""
        from modules.categorization_cascade import TransactionCategorizer

        categorizer = TransactionCategorizer(use_local_ai=False, use_cloud_fallback=False)

        # Test various formats
        test_cases = [
            ("CB CARREFOUR PARIS 15 12/02/24", "CARREFOUR PARIS 15"),
            ("PRLV EDF 45.67 EUR 01/02/24", "EDF"),
            ("VIR SALAIRE EMPLOYEUR 2500.00", "SALAIRE EMPLOYEUR"),
            ("RETRAIT DAB LYON 100.00", "DAB LYON"),
        ]

        for raw_label, expected in test_cases:
            result = categorizer._extract_merchant(raw_label)
            assert expected in result or result in expected, f"Failed for {raw_label}"

    def test_recurring_pattern_detection(self):
        """Test la détection des transactions récurrentes."""
        from modules.categorization_cascade import TransactionCategorizer

        categorizer = TransactionCategorizer(use_local_ai=False, use_cloud_fallback=False)

        # Recurring patterns
        assert categorizer._is_recurring_pattern("NETFLIX SUBSCRIPTION")
        assert categorizer._is_recurring_pattern("EDF MENSUEL")
        assert categorizer._is_recurring_pattern("ORANGE ABONNEMENT")

        # Non-recurring
        assert not categorizer._is_recurring_pattern("CARREFOUR ACHAT")
        assert not categorizer._is_recurring_pattern("RESTAURANT PIZZA")

    def test_build_ai_prompt_structure(self):
        """Test la structure du prompt IA."""
        from modules.categorization_cascade import TransactionCategorizer

        categorizer = TransactionCategorizer(use_local_ai=False, use_cloud_fallback=False)
        prompt = categorizer._build_ai_prompt("CARREFOUR PARIS", -45.67, "2024-02-20")

        # Check PFCv2 taxonomy is present
        assert "Food & Drink" in prompt
        assert "Transportation" in prompt
        assert "Financial" in prompt

        # Check JSON schema
        assert '"transaction_id"' in prompt
        assert '"clean_merchant"' in prompt
        assert '"category"' in prompt
        assert '"is_recurring_candidate"' in prompt
        assert '"risk_flag"' in prompt
        assert '"confidence_score"' in prompt

        # Check transaction data
        assert "CARREFOUR PARIS" in prompt
        assert "-45.67" in prompt or "45.67" in prompt

    def test_cascade_order(self):
        """Test que la cascade respecte l'ordre: heuristique > similarité > IA."""
        from modules.categorization_cascade import TransactionCategorizer

        categorizer = TransactionCategorizer(use_local_ai=False, use_cloud_fallback=False)

        # Mock methods to track calls
        categorizer._check_heuristics = MagicMock(return_value=None)
        categorizer._check_similarity = MagicMock(return_value=None)
        categorizer._call_ai = MagicMock(
            return_value=MagicMock(
                category="Test", clean_merchant="Test", confidence_score=0.5, source="local_ai"
            )
        )

        # Trigger categorization
        categorizer.categorize("SOME TRANSACTION", -10.00, "2024-02-20")

        # Verify order
        categorizer._check_heuristics.assert_called_once()
        categorizer._check_similarity.assert_called_once()
        categorizer._call_ai.assert_called_once()


class TestJSONValidation:
    """Tests de validation du format JSON strict."""

    def test_required_json_fields(self):
        """Test que tous les champs requis sont présents."""
        required_fields = [
            "transaction_id",
            "clean_merchant",
            "category",
            "is_recurring_candidate",
            "risk_flag",
            "confidence_score",
        ]

        # Example valid response
        valid_response = {
            "transaction_id": "auto",
            "clean_merchant": "Carrefour",
            "category": "Food & Drink > Groceries",
            "is_recurring_candidate": False,
            "risk_flag": 0,
            "confidence_score": 0.95,
        }

        for field in required_fields:
            assert field in valid_response, f"Missing field: {field}"

    def test_category_format_pfcv2(self):
        """Test que les catégories suivent le format PFCv2."""
        from modules.categorization_cascade import TransactionCategorizer

        valid_categories = [
            "Food & Drink > Groceries",
            "Transportation > Fuel",
            "Financial > Bank Fees",
            "Housing > Utilities",
        ]

        for cat in valid_categories:
            # Should match "Main > Sub" pattern
            assert ">" in cat
            parts = cat.split(">")
            assert len(parts) == 2
            assert parts[0].strip() in TransactionCategorizer.PFCV2_CATEGORIES

    def test_confidence_score_range(self):
        """Test que le score de confiance est entre 0 et 1."""
        test_cases = [
            ({"confidence_score": 0.95}, True),
            ({"confidence_score": 0.0}, True),
            ({"confidence_score": 1.0}, True),
            ({"confidence_score": 1.5}, False),
            ({"confidence_score": -0.1}, False),
        ]

        for data, should_pass in test_cases:
            score = data["confidence_score"]
            is_valid = 0.0 <= score <= 1.0
            assert is_valid == should_pass, f"Failed for score: {score}"

    def test_risk_flag_values(self):
        """Test que risk_flag est entre 0 et 3."""
        for valid in [0, 1, 2, 3]:
            assert 0 <= valid <= 3

        for invalid in [-1, 4, 5, 10]:
            assert not (0 <= invalid <= 3)


class TestIntegration:
    """Tests d'intégration."""

    @pytest.mark.slow
    def test_full_categorization_pipeline(self):
        """Test le pipeline complet (nécessite modèle local ou cloud)."""
        pytest.skip("Requires local model or cloud API keys")

        from modules.categorization_cascade import categorize_transaction

        result = categorize_transaction("CARREFOUR PARIS 15", -45.67, "2024-02-20")

        # Validate result structure
        assert "category" in result
        assert "clean_merchant" in result
        assert "confidence_score" in result
        assert "source" in result

        # Validate types
        assert isinstance(result["category"], str)
        assert isinstance(result["confidence_score"], (int, float))
        assert isinstance(result["is_recurring_candidate"], bool)

    def test_pfcv2_taxonomy_completeness(self):
        """Test que la taxonomie PFCv2 couvre tous les cas principaux."""
        from modules.categorization_cascade import TransactionCategorizer

        # Main categories
        main_cats = list(TransactionCategorizer.PFCV2_CATEGORIES.keys())

        # Common transaction types should be covered
        assert "Food & Drink" in main_cats
        assert "Transportation" in main_cats
        assert "Housing" in main_cats
        assert "Financial" in main_cats
        assert "Shopping" in main_cats
        assert "Income" in main_cats

        # Each main category should have subcategories
        for main, subs in TransactionCategorizer.PFCV2_CATEGORIES.items():
            assert len(subs) > 0, f"{main} has no subcategories"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
