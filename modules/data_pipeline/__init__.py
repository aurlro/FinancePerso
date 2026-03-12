"""
Pipeline de données pour FinancePerso.

Modules pour l'import massif, la transformation et la validation des données.
"""

from modules.data_pipeline.transformers import (
    DateNormalizer,
    AmountNormalizer,
    CategoryMapper,
    LabelCleaner,
)
from modules.data_pipeline.validators import (
    SchemaValidator,
    DuplicateDetector,
    ValidationError,
)

__all__ = [
    "DateNormalizer",
    "AmountNormalizer",
    "CategoryMapper",
    "LabelCleaner",
    "SchemaValidator",
    "DuplicateDetector",
    "ValidationError",
]
