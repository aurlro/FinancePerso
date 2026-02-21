"""
Package src - Data Engineering pour FinancePerso.
=================================================

Ce package contient les modules de traitement des données :
- data_cleaning: Nettoyage et normalisation des libellés

Usage:
    from src import clean_transaction_label
    
    cleaned = clean_transaction_label("MONOPRIX PARIS 14 CB*1234")
    # Result: "MONOPRIX"
"""

from src.data_cleaning import (
    clean_merchant_name,
    clean_transaction_label,
    extract_card_suffix,
    extract_location,
    extract_transaction_metadata,
    normalize_merchant_name,
    batch_clean_labels,
)

__all__ = [
    "clean_merchant_name",
    "clean_transaction_label",
    "extract_card_suffix",
    "extract_location",
    "extract_transaction_metadata",
    "normalize_merchant_name",
    "batch_clean_labels",
]
