"""
Data Pipeline Module - Import massif et migrations.

Ce module permet d'importer un grand volume de transactions (1000+)
et de migrer des données depuis d'autres outils (Bankin', YNAB, Mint).
"""

from .importers import (
    BulkTransactionImporter,
    ImportConfig,
    ImportResult,
    BankinImporter,
    YNABImporter,
)
from .transformers import (
    DateNormalizer,
    AmountNormalizer,
    CategoryMapper,
    LabelCleaner,
)
from .validators import (
    SchemaValidator,
    DuplicateDetector,
)

__all__ = [
    'BulkTransactionImporter',
    'ImportConfig',
    'ImportResult',
    'BankinImporter',
    'YNABImporter',
    'DateNormalizer',
    'AmountNormalizer',
    'CategoryMapper',
    'LabelCleaner',
    'SchemaValidator',
    'DuplicateDetector',
]

__version__ = "1.0.0"
