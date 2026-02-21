"""
Package src - Data Engineering pour FinancePerso.
=================================================

Ce package contient les modules de traitement des données :
- data_cleaning: Nettoyage et normalisation des libellés
"""

from src.data_cleaning import (
    clean_merchant_name,
    clean_transaction_label,
    extract_card_suffix,
    extract_location,
    normalize_merchant_name,
    batch_clean_labels,
)

__all__ = [
    "clean_merchant_name",
    "clean_transaction_label",
    "extract_card_suffix",
    "extract_location",
    "normalize_merchant_name",
    "batch_clean_labels",
]
