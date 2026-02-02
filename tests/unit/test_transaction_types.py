"""
Tests unitaires pour le module transaction_types.
Couverture >95% obligatoire.
"""
import pytest
import pandas as pd
import numpy as np
from modules.transaction_types import (
    is_income_category,
    is_expense_category,
    is_excluded_category,
    is_refund_category,
    get_category_type,
    validate_amount_consistency,
    suggest_amount_sign,
    filter_income_transactions,
    filter_expense_transactions,
    filter_excluded_transactions,
    calculate_true_income,
    calculate_true_expenses,
    calculate_savings_rate,
    INCOME_CATEGORIES,
    EXCLUDED_CATEGORIES,
    REFUND_CATEGORIES,
)


class TestCategoryDetection:
    """Tests de détection des catégories."""
    
    def test_is_income_category_with_valid(self):
        """Test income avec catégories valides."""
        assert is_income_category('Revenus') is True
        assert is_income_category('Salaire') is True
        assert is_income_category('Prime') is True
    
    def test_is_income_category_with_invalid(self):
        """Test income avec catégories non revenus."""
        assert is_income_category('Alimentation') is False
        assert is_income_category('Virement Interne') is False
        assert is_income_category(None) is False
        assert is_income_category('') is False
    
    def test_is_expense_category_with_valid(self):
        """Test expense avec catégories valides."""
        assert is_expense_category('Alimentation') is True
        assert is_expense_category('Transport') is True
        assert is_expense_category('Santé') is True
    
    def test_is_expense_category_with_excluded(self):
        """Test expense avec catégories exclues."""
        assert is_expense_category('Virement Interne') is False
        assert is_expense_category('Hors Budget') is False
    
    def test_is_expense_category_with_income(self):
        """Test expense avec catégories revenus."""
        assert is_expense_category('Salaire') is False
        assert is_expense_category('Revenus') is False
    
    def test_is_excluded_category(self):
        """Test excluded categories."""
        assert is_excluded_category('Virement Interne') is True
        assert is_excluded_category('Hors Budget') is True
        assert is_excluded_category('Alimentation') is False
    
    def test_is_refund_category(self):
        """Test refund categories."""
        assert is_refund_category('Remboursement') is True
        assert is_refund_category('Remboursement santé') is True
        assert is_refund_category('Salaire') is False
    
    def test_get_category_type(self):
        """Test get_category_type."""
        assert get_category_type('Salaire') == 'income'
        assert get_category_type('Alimentation') == 'expense'
        assert get_category_type('Virement Interne') == 'excluded'
        assert get_category_type('Remboursement') == 'refund'
        assert get_category_type(None) == 'unknown'
        assert get_category_type('') == 'unknown'
    
    def test_category_with_whitespace(self):
        """Test que les espaces sont gérés."""
        assert is_income_category('  Salaire  ') is True
        assert is_income_category('Salaire ') is True


class TestValidation:
    """Tests de validation des transactions."""
    
    def test_validate_income_positive_amount(self):
        """Revenu avec montant positif = valide."""
        is_valid, warning = validate_amount_consistency('Salaire', 2500.00)
        assert is_valid is True
        assert warning is None
    
    def test_validate_income_negative_amount(self):
        """Revenu avec montant négatif = invalide."""
        is_valid, warning = validate_amount_consistency('Salaire', -2500.00)
        assert is_valid is False
        assert 'négatif' in warning or 'négatif' in warning
        assert 'Salaire' in warning
    
    def test_validate_expense_negative_amount(self):
        """Dépense avec montant négatif = valide."""
        is_valid, warning = validate_amount_consistency('Alimentation', -45.50)
        assert is_valid is True
        assert warning is None
    
    def test_validate_expense_positive_amount(self):
        """Dépense avec montant positif = invalide."""
        is_valid, warning = validate_amount_consistency('Alimentation', 45.50)
        assert is_valid is False
        assert 'positif' in warning or 'positif' in warning
    
    def test_validate_excluded_any_amount(self):
        """Catégorie exclue = toujours valide."""
        # Les virements internes peuvent être positifs ou négatifs
        is_valid, _ = validate_amount_consistency('Virement Interne', 500.00)
        assert is_valid is True
        
        is_valid, _ = validate_amount_consistency('Virement Interne', -500.00)
        assert is_valid is True
    
    def test_validate_edge_cases(self):
        """Cas limites de validation."""
        is_valid, _ = validate_amount_consistency(None, 100.00)
        assert is_valid is True  # Pas de catégorie = pas de validation
        
        is_valid, _ = validate_amount_consistency('', -50.00)
        assert is_valid is True
    
    def test_suggest_amount_sign(self):
        """Test suggestion de signe."""
        assert suggest_amount_sign('Salaire') == 1
        assert suggest_amount_sign('Alimentation') == -1
        assert suggest_amount_sign('Virement Interne') == 0


class TestDataFrameFiltering:
    """Tests de filtrage DataFrame."""
    
    @pytest.fixture
    def sample_df(self):
        """DataFrame de test."""
        return pd.DataFrame({
            'id': ['1', '2', '3', '4', '5'],
            'amount': [2500.00, -45.50, -78.00, 25.00, -500.00],
            'category_validated': [
                'Salaire',
                'Alimentation',
                'Factures',
                'Remboursement',
                'Virement Interne'
            ]
        })
    
    def test_filter_income_transactions(self, sample_df):
        """Test filtrage revenus.
        Note: 'Remboursement' est dans INCOME_CATEGORIES, donc retourné même sans include_refunds.
        """
        result = filter_income_transactions(sample_df, include_refunds=False)
        # Salaire + Remboursement (dans INCOME_CATEGORIES)
        assert len(result) == 2
        categories = result['category_validated'].tolist()
        assert 'Salaire' in categories
        assert 'Remboursement' in categories
    
    def test_filter_income_with_refunds(self, sample_df):
        """Test filtrage revenus avec remboursements."""
        result = filter_income_transactions(sample_df, include_refunds=True)
        assert len(result) == 2
        categories = result['category_validated'].tolist()
        assert 'Salaire' in categories
        assert 'Remboursement' in categories
    
    def test_filter_expense_transactions(self, sample_df):
        """Test filtrage dépenses."""
        result = filter_expense_transactions(sample_df)
        assert len(result) == 2  # Alimentation, Factures
        categories = result['category_validated'].tolist()
        assert 'Alimentation' in categories
        assert 'Factures' in categories
        assert 'Salaire' not in categories
        assert 'Virement Interne' not in categories
    
    def test_filter_excluded_transactions(self, sample_df):
        """Test filtrage exclu."""
        result = filter_excluded_transactions(sample_df)
        assert len(result) == 4  # Tout sauf Virement Interne
        assert 'Virement Interne' not in result['category_validated'].values
    
    def test_filter_empty_dataframe(self):
        """Test filtrage DataFrame vide."""
        empty_df = pd.DataFrame()
        assert filter_income_transactions(empty_df).empty
        assert filter_expense_transactions(empty_df).empty
    
    def test_filter_missing_columns(self):
        """Test filtrage avec colonnes manquantes."""
        df = pd.DataFrame({'amount': [100, -50]})
        # Ne devrait pas planter
        result = filter_income_transactions(df)
        assert len(result) == len(df)  # Retourne tel quel si colonne manquante


class TestFinancialCalculations:
    """Tests des calculs financiers."""
    
    @pytest.fixture
    def financial_df(self):
        """DataFrame financier de test."""
        return pd.DataFrame({
            'amount': [2500.00, 50.00, -45.50, -78.00, -500.00],  # Remboursement 50 < Dépenses 123.50
            'category_validated': [
                'Salaire',
                'Remboursement',
                'Alimentation',
                'Factures',
                'Virement Interne'
            ]
        })
    
    def test_calculate_true_income(self, financial_df):
        """Test calcul revenus.
        Note: 'Remboursement' est dans INCOME_CATEGORIES, donc pris en compte par défaut.
        Les montants négatifs sont filtrés (seuls les montants positifs comptent).
        """
        # Sans remboursements explicites (mais Remboursement est déjà dans INCOME_CATEGORIES)
        # Montants: 2500 (Salaire), 50 (Remboursement) = 2550
        income = calculate_true_income(financial_df, include_refunds=False)
        assert income == 2550.00
        
        # Avec remboursements (même résultat car déjà inclus)
        income = calculate_true_income(financial_df, include_refunds=True)
        assert income == 2550.00  # 2500 + 50
    
    def test_calculate_true_expenses(self, financial_df):
        """Test calcul dépenses.
        Note: Remboursement est dans INCOME_CATEGORIES, donc exclu des dépenses.
        Remboursement de 50 déduit des dépenses: 123.50 - 50 = 73.50
        """
        # Alimentation: -45.50, Factures: -78.00 = 123.50
        # Remboursement: 50 -> Déduit -> 123.50 - 50 = 73.50
        expenses = calculate_true_expenses(financial_df, include_refunds=True)
        assert expenses == 73.50  # 123.50 - 50
    
    def test_calculate_expenses_with_refunds(self):
        """Test calcul dépenses avec remboursements déduits."""
        df = pd.DataFrame({
            'amount': [-100.00, -50.00, 30.00],  # Dépenses 100+50, remboursement 30
            'category_validated': ['Santé', 'Santé', 'Remboursement']
        })
        
        expenses = calculate_true_expenses(df, include_refunds=True)
        assert expenses == 120.00  # 150 - 30
    
    def test_calculate_savings_rate(self, financial_df):
        """Test calcul taux d'épargne.
        Revenus: 2500 (Salaire) + 50 (Remboursement) = 2550
        Dépenses: 73.50 (123.50 - 50 remboursement déduit)
        Taux: (2550 - 73.50) / 2550 * 100 = 97.12%
        """
        rate = calculate_savings_rate(financial_df)
        # Revenus: 2550 (Salaire + Remboursement, include_refunds=False -> 2500 seul? Non, Remboursement est dans INCOME_CATEGORIES)
        # Attendez, calculate_true_income utilise include_refunds=False mais Remboursement est déjà dans INCOME_CATEGORIES
        # Donc revenus = 2550
        # Dépenses = 73.50 (123.50 - 50 remboursement)
        # Taux = (2550 - 73.50) / 2550 * 100
        income = 2550.00
        expenses = 73.50
        expected_rate = (income - expenses) / income * 100
        assert abs(rate - expected_rate) < 0.01
    
    def test_calculate_savings_rate_no_income(self):
        """Test calcul taux sans revenu."""
        df = pd.DataFrame({
            'amount': [-50.00, -30.00],
            'category_validated': ['Alimentation', 'Transport']
        })
        rate = calculate_savings_rate(df)
        assert rate == 0.0
    
    def test_calculate_empty_dataframe(self):
        """Test calculs avec DataFrame vide."""
        empty_df = pd.DataFrame()
        assert calculate_true_income(empty_df) == 0.0
        assert calculate_true_expenses(empty_df) == 0.0
        assert calculate_savings_rate(empty_df) == 0.0


class TestConstants:
    """Tests des constantes."""
    
    def test_income_categories_not_empty(self):
        """Les listes de catégories ne doivent pas être vides."""
        assert len(INCOME_CATEGORIES) > 0
        assert len(EXCLUDED_CATEGORIES) > 0
    
    def test_no_duplicate_categories(self):
        """Pas de doublons dans les catégories."""
        assert len(INCOME_CATEGORIES) == len(set(INCOME_CATEGORIES))
        assert len(EXCLUDED_CATEGORIES) == len(set(EXCLUDED_CATEGORIES))
    
    def test_no_overlap_income_excluded(self):
        """Pas de chevauchement entre revenus et exclues."""
        overlap = set(INCOME_CATEGORIES) & set(EXCLUDED_CATEGORIES)
        assert len(overlap) == 0, f"Chevauchement détecté: {overlap}"


class TestEdgeCases:
    """Tests des cas limites et erreurs."""
    
    def test_none_values(self):
        """Gestion des valeurs None."""
        assert is_income_category(None) is False
        assert is_expense_category(None) is False
        assert get_category_type(None) == 'unknown'
    
    def test_whitespace_handling(self):
        """Gestion des espaces."""
        assert is_income_category('  Salaire  ') is True
        assert is_income_category('Salaire\t') is True
    
    def test_case_sensitivity(self):
        """Vérification de la sensibilité à la casse."""
        # Actuellement sensible à la casse - à modifier si besoin
        assert is_income_category('salaire') is False  # minuscule
        assert is_income_category('SALAIRE') is False  # majuscule
    
    def test_dataframe_with_nan(self):
        """Gestion des NaN dans DataFrame."""
        df = pd.DataFrame({
            'amount': [100.00, np.nan, -50.00],
            'category_validated': ['Salaire', 'Alimentation', None]
        })
        # Ne devrait pas planter
        result = filter_income_transactions(df)
        assert isinstance(result, pd.DataFrame)


# ============================================================================
# Tests de Performance (optionnels)
# ============================================================================

@pytest.mark.slow
class TestPerformance:
    """Tests de performance pour les grandes quantités de données."""
    
    def test_filter_large_dataframe(self):
        """Test performance avec 10000 transactions."""
        import time
        
        n = 10000
        df = pd.DataFrame({
            'amount': np.random.randn(n) * 100,
            'category_validated': np.random.choice(
                ['Alimentation', 'Salaire', 'Transport', 'Virement Interne'],
                n
            )
        })
        
        start = time.time()
        result = filter_expense_transactions(df)
        duration = time.time() - start
        
        # Devrait prendre moins d'une seconde
        assert duration < 1.0, f"Filtrage trop lent: {duration:.2f}s"
