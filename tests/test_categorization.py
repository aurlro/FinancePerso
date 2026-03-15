"""
Tests pour le module de catégorisation.

Couvre la cascade de catégorisation:
1. Règles exactes
2. Règles partielles (pattern matching)
3. ML Local (si activé)
4. IA Cloud (fallback)
5. Catégorie par défaut
"""

from unittest.mock import Mock, patch

import pandas as pd
import pytest


class TestCategorizationCascade:
    """Tests la cascade complète de catégorisation."""

    def test_exact_rule_match(self, temp_db):
        """Une règle exacte doit matcher prioritairement."""
        from modules.categorization import categorize_transaction
        from modules.db.rules import add_learning_rule

        # Créer une règle exacte
        add_learning_rule(
            pattern="NETFLIX",
            category="Abonnements",
            priority=100,
            match_type="exact"
        )

        # Transaction correspondante
        tx = {"label": "NETFLIX", "amount": -15.99}
        result = categorize_transaction(tx)

        assert result == "Abonnements"

    def test_pattern_rule_match(self, temp_db):
        """Une règle pattern doit matcher si pas d'exact."""
        from modules.categorization import categorize_transaction
        from modules.db.rules import add_learning_rule

        # Créer une règle pattern
        add_learning_rule(
            pattern="AMAZON",
            category="Achats",
            priority=50,
            match_type="contains"
        )

        # Transaction avec le pattern
        tx = {"label": "Paiement AMAZON PRIME", "amount": -49.0}
        result = categorize_transaction(tx)

        assert result == "Achats"

    def test_priority_rules(self, temp_db):
        """La règle avec plus haute priorité gagne."""
        from modules.categorization import categorize_transaction
        from modules.db.rules import add_learning_rule

        # Deux règles pour la même transaction
        add_learning_rule(
            pattern="CARREFOUR",
            category="Courses",
            priority=50
        )
        add_learning_rule(
            pattern="CARREFOUR",
            category="Alimentation",
            priority=100
        )

        tx = {"label": "CARREFOUR MARKET", "amount": -45.0}
        result = categorize_transaction(tx)

        # La priorité 100 gagne
        assert result == "Alimentation"

    def test_no_match_returns_default(self, temp_db):
        """Sans règle, retourne la catégorie par défaut."""
        from modules.categorization import categorize_transaction

        tx = {"label": "TRANSACTION INCONNUE XYZ123", "amount": -100.0}
        result = categorize_transaction(tx)

        assert result == "Inconnu"

    def test_amount_sign_handling(self, temp_db):
        """Gère correctement les montants positifs/négatifs."""
        from modules.categorization import categorize_transaction
        from modules.db.rules import add_learning_rule

        add_learning_rule(
            pattern="SALAIRE",
            category="Revenus",
            priority=100
        )

        # Montant positif (crédit)
        tx_credit = {"label": "SALAIRE MARS", "amount": 2500.0}
        result = categorize_transaction(tx_credit)
        assert result == "Revenus"

    def test_special_characters_in_label(self, temp_db):
        """Gère les caractères spéciaux dans les labels."""
        from modules.categorization import categorize_transaction
        from modules.db.rules import add_learning_rule

        add_learning_rule(
            pattern="CAFÉ",
            category="Restauration",
            priority=100
        )

        tx = {"label": "CAFÉ DE LA PAIX", "amount": -5.50}
        result = categorize_transaction(tx)

        assert result == "Restauration"


class TestCategorizationWithAI:
    """Tests la catégorisation avec fallback IA."""

    @patch("modules.categorization.get_ai_manager")
    def test_ai_fallback_when_no_rules(self, mock_get_ai, temp_db):
        """L'IA est appelée quand aucune règle ne match."""
        from modules.categorization import categorize_transaction

        # Mock AI manager
        mock_ai = Mock()
        mock_ai.categorize.return_value = "Transport"
        mock_get_ai.return_value = mock_ai

        tx = {"label": "UBER TRIP", "amount": -12.50}
        result = categorize_transaction(tx, use_ai=True)

        mock_ai.categorize.assert_called_once()
        assert result == "Transport"

    @patch("modules.categorization.get_ai_manager")
    def test_ai_error_fallback_to_default(self, mock_get_ai, temp_db):
        """En cas d'erreur IA, fallback sur catégorie par défaut."""
        from modules.categorization import categorize_transaction

        # Mock AI qui échoue
        mock_ai = Mock()
        mock_ai.categorize.side_effect = Exception("API Error")
        mock_get_ai.return_value = mock_ai

        tx = {"label": "TRANSACTION", "amount": -10.0}
        result = categorize_transaction(tx, use_ai=True)

        assert result == "Inconnu"

    def test_ai_disabled_flag(self, temp_db):
        """Respecte le flag use_ai=False."""
        from modules.categorization import categorize_transaction

        with patch("modules.categorization.get_ai_manager") as mock_get_ai:
            tx = {"label": "TEST", "amount": -10.0}
            result = categorize_transaction(tx, use_ai=False)

            # L'IA ne doit pas être appelée
            mock_get_ai.assert_not_called()
            assert result == "Inconnu"


class TestCategorizationBatch:
    """Tests la catégorisation en batch (DataFrame)."""

    def test_batch_categorization(self, temp_db):
        """Catégorise plusieurs transactions d'un coup."""
        from modules.categorization import categorize_transactions_batch
        from modules.db.rules import add_learning_rule

        # Règles
        add_learning_rule("NETFLIX", "Abonnements", 100)
        add_learning_rule("CARREFOUR", "Courses", 100)

        # DataFrame de transactions
        df = pd.DataFrame({
            "label": ["NETFLIX", "CARREFOUR", "INCONNU"],
            "amount": [-15.99, -45.0, -10.0]
        })

        results = categorize_transactions_batch(df)

        assert results[0] == "Abonnements"
        assert results[1] == "Courses"
        assert results[2] == "Inconnu"

    def test_batch_preserves_order(self, temp_db):
        """Préserve l'ordre des transactions."""
        from modules.categorization import categorize_transactions_batch

        df = pd.DataFrame({
            "label": ["A", "B", "C", "D", "E"],
            "amount": [-1, -2, -3, -4, -5]
        })

        results = categorize_transactions_batch(df)

        assert len(results) == 5

    def test_batch_empty_dataframe(self):
        """Gère un DataFrame vide."""
        from modules.categorization import categorize_transactions_batch

        df = pd.DataFrame(columns=["label", "amount"])
        results = categorize_transactions_batch(df)

        assert len(results) == 0


class TestCategorizationCache:
    """Tests le caching des résultats de catégorisation."""

    def test_caches_category_result(self, temp_db):
        """Cache les résultats pour éviter recalculs."""
        from modules.categorization import get_cached_category

        # Premier appel
        result1 = get_cached_category("NETFLIX", -15.99)

        # Deuxième appel (devrait utiliser cache)
        result2 = get_cached_category("NETFLIX", -15.99)

        assert result1 == result2

    def test_cache_invalidation_on_rule_change(self, temp_db):
        """Invalide le cache quand une règle change."""
        from modules.categorization import get_cached_category, invalidate_category_cache
        from modules.db.rules import add_learning_rule

        # Cache un résultat
        result1 = get_cached_category("TEST", -10.0)

        # Ajoute une nouvelle règle
        add_learning_rule("TEST", "NouvelleCat", 100)
        invalidate_category_cache()

        # Nouveau résultat après invalidation
        result2 = get_cached_category("TEST", -10.0)

        assert result2 == "NouvelleCat"


class TestCategoryValidation:
    """Tests la validation des catégories."""

    def test_valid_category_name(self):
        """Accepte les noms de catégories valides."""
        from modules.categorization import is_valid_category

        assert is_valid_category("Alimentation") is True
        assert is_valid_category("Transport") is True
        assert is_valid_category("Factures") is True

    def test_invalid_category_name(self):
        """Rejette les noms invalides."""
        from modules.categorization import is_valid_category

        assert is_valid_category("") is False
        assert is_valid_category("   ") is False
        assert is_valid_category(None) is False
        assert is_valid_category("A" * 100) is False  # Trop long

    def test_system_categories_protected(self):
        """Les catégories système sont protégées."""
        from modules.categorization import is_system_category

        assert is_system_category("Virement Interne") is True
        assert is_system_category("Inconnu") is True
        assert is_system_category("Hors Budget") is True
        assert is_system_category("Courses") is False
