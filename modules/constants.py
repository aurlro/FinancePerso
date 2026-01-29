# Application Version
APP_VERSION = "2.3.0"


class SystemCategory:
    """Predefined system categories that have special behavior."""
    INTERNAL_TRANSFER = "Virement Interne"
    OUT_OF_BUDGET = "Hors Budget"
    UNKNOWN = "Inconnu"
    AVOIR = "Avoir"
    OTHER = "Autre"


class MemberType:
    """Types of members in the application."""
    HOUSEHOLD = "HOUSEHOLD"  # Members of the household
    EXTERNAL = "EXTERNAL"    # External entities


class TransactionStatus:
    """Status values for transactions."""
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"


class UILabel:
    """User-facing labels and messages."""
    IMPORT_SUCCESS = "✅ Import réussi"
    VALIDATION_REQUIRED = "⚠️ Validation requise"
    NO_DATA = "Aucune donnée disponible"
    LOADING = "Chargement en cours..."


class DefaultValues:
    """Default values used throughout the application."""
    DEFAULT_ACCOUNT = "Compte Principal"
    DEFAULT_MEMBER = "Anonyme"
    DEFAULT_EMOJI = "🏷️"



