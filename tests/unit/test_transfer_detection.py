"""
Tests unitaires pour le module transfer_detection.
"""

import pandas as pd
import pytest

from modules.transaction_types import (
    EXCLUDED_CATEGORIES,
    calculate_true_expenses,
    calculate_true_income,
    is_excluded_category,
)

# Tests pour les nouvelles catégories de transfert


class TestNewExcludedCategories:
    """Tests pour les nouvelles catégories exclues (Contribution Partenaire, Apport Externe)."""

    def test_contribution_partenaire_is_excluded(self):
        """Vérifie que 'Contribution Partenaire' est dans les catégories exclues."""
        assert "Contribution Partenaire" in EXCLUDED_CATEGORIES
        assert is_excluded_category("Contribution Partenaire") is True

    def test_apport_externe_is_excluded(self):
        """Vérifie que 'Apport Externe' est dans les catégories exclues."""
        assert "Apport Externe" in EXCLUDED_CATEGORIES
        assert is_excluded_category("Apport Externe") is True

    def test_contribution_excluded_from_income_calculation(self):
        """Une contribution partenaire ne doit pas compter comme revenu."""
        df = pd.DataFrame(
            {
                "amount": [2500.00, 500.00],  # Salaire + Contribution
                "category_validated": ["Salaire", "Contribution Partenaire"],
            }
        )
        # Seul le salaire doit compter comme revenu
        income = calculate_true_income(df, include_refunds=False)
        assert income == 2500.00

    def test_internal_transfer_excluded_from_income(self):
        """Un virement interne ne doit pas compter comme revenu."""
        df = pd.DataFrame(
            {
                "amount": [2500.00, 1000.00],  # Salaire + Virement Interne
                "category_validated": ["Salaire", "Virement Interne"],
            }
        )
        income = calculate_true_income(df, include_refunds=False)
        assert income == 2500.00

    def test_mixed_transfers_excluded(self):
        """Test avec différents types de transferts."""
        df = pd.DataFrame(
            {
                "amount": [2500.00, 1000.00, 500.00, -300.00],  # Salaire + Transferts + Dépense
                "category_validated": [
                    "Salaire",
                    "Virement Interne",
                    "Contribution Partenaire",
                    "Alimentation",
                ],
            }
        )
        # Revenus: uniquement le salaire
        income = calculate_true_income(df, include_refunds=False)
        assert income == 2500.00

        # Dépenses: uniquement l'alimentation (les transferts sont exclus)
        expenses = calculate_true_expenses(df, include_refunds=True)
        assert expenses == 300.00

    def test_partner_contribution_not_expense(self):
        """Une contribution partenaire ne doit pas être considérée comme une dépense."""
        from modules.transaction_types import is_expense_category

        assert is_expense_category("Contribution Partenaire") is False

    def test_partner_contribution_not_income(self):
        """Une contribution partenaire ne doit pas être considérée comme un revenu."""
        from modules.transaction_types import is_income_category

        assert is_income_category("Contribution Partenaire") is False


class TestTransferDetectionLogic:
    """Tests pour la logique de détection des transferts."""

    def test_real_income_calculation_scenario(self):
        """
        Scénario réel: Salaire + Virement interne + Contribution partenaire.
        Seul le salaire doit compter comme revenu réel.
        """
        df = pd.DataFrame(
            {
                "amount": [
                    3000.00,  # Salaire (vrai revenu)
                    -1200.00,  # Loyer (dépense)
                    -400.00,  # Courses (dépense)
                    1000.00,  # Virement interne A -> B (à exclure)
                    -1000.00,  # Virement interne A -> B (partie négative)
                    600.00,  # Contribution partenaire C -> B (à exclure)
                ],
                "category_validated": [
                    "Salaire",
                    "Logement",
                    "Alimentation",
                    "Virement Interne",
                    "Virement Interne",
                    "Contribution Partenaire",
                ],
            }
        )

        # Revenus réels: uniquement le salaire
        income = calculate_true_income(df, include_refunds=False)
        assert income == 3000.00

        # Dépenses: Logement + Alimentation (pas les virements internes)
        expenses = calculate_true_expenses(df, include_refunds=True)
        assert expenses == 1600.00  # 1200 + 400

        # Solde: 3000 - 1600 = 1400
        assert income - expenses == 1400.00


class TestExcludedCategoriesConstants:
    """Tests pour vérifier les constantes de catégories exclues."""

    def test_all_expected_excluded_categories_present(self):
        """Vérifie que toutes les catégories attendues sont présentes."""
        expected_excluded = [
            "Virement Interne",
            "Hors Budget",
            "Transfert",
            "Épargne",
            "Contribution Partenaire",
            "Apport Externe",
        ]
        for cat in expected_excluded:
            assert cat in EXCLUDED_CATEGORIES, f"Catégorie manquante: {cat}"

    def test_no_duplicate_in_excluded(self):
        """Vérifie qu'il n'y a pas de doublons dans les catégories exclues."""
        assert len(EXCLUDED_CATEGORIES) == len(set(EXCLUDED_CATEGORIES))
