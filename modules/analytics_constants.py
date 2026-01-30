"""
Analytics constants for recurring payment detection and financial profiling.

This module centralizes all magic numbers used in analytics calculations
to improve maintainability and make threshold tuning easier.
"""

# ============================================================================
# RECURRING PAYMENT DETECTION
# ============================================================================

# Minimum occurrences required to consider a pattern as recurring
MIN_OCCURRENCES_FOR_RECURRING = 2

# Amount variability tolerances (as decimal percentages)
# Lower tolerance = stricter matching for exact amounts
AMOUNT_TOLERANCE_ENERGY = 0.15  # 15% for energy/utilities (variable bills)
AMOUNT_TOLERANCE_STANDARD = 0.05  # 5% for standard subscriptions (fixed amounts)
AMOUNT_TOLERANCE_FIXED_THRESHOLD = 0.05  # 5% threshold to classify as "Fixe" vs "Variable"

# Frequency detection ranges (in days)
# These ranges account for month length variations and processing delays
FREQUENCY_MONTHLY_MIN = 25
FREQUENCY_MONTHLY_MAX = 35
FREQUENCY_MONTHLY_LABEL = "Mensuel"

FREQUENCY_QUARTERLY_MIN = 80
FREQUENCY_QUARTERLY_MAX = 100
FREQUENCY_QUARTERLY_LABEL = "Trimestriel"

FREQUENCY_ANNUAL_MIN = 350
FREQUENCY_ANNUAL_MAX = 380
FREQUENCY_ANNUAL_LABEL = "Annuel"

# Energy/utility provider keywords for variable bill detection
ENERGY_KEYWORDS = [
    "EDF", "ENGIE", "TOTAL", "EAU", "SUEZ", "VEOLIA",
    "OHM", "MINT", "VATTEN", "ENI", "TOTALENERGIE", "VATTENFALL"
]

# ============================================================================
# FINANCIAL PROFILE DETECTION
# ============================================================================

# Salary detection threshold (minimum positive amount)
SALARY_MIN_AMOUNT = 500

# High confidence threshold (minimum transaction count)
HIGH_CONFIDENCE_MIN_COUNT = 1

# Rent/loan detection threshold (minimum negative amount)
RENT_LOAN_MIN_AMOUNT = -600

# Financial category keywords for auto-classification
CATEGORY_KEYWORDS = {
    "Logement": [
        "LOYER", "IMMO", "PROPRIETAIRE", "QUITTANCE", "BAIL", "CAUTION"
    ],
    "Emprunt immobilier": [
        "PRET", "CREDIT", "ECHEANCE"
    ],
    "Assurances": [
        "ASSURANCE", "MACIF", "MAIF", "AXA", "ALLIANZ", "MUTUELLE",
        "PREVOYANCE", "GENERALI", "SWISSLIFE", "MGEN", "MALAKOFF", "ALAN"
    ],
    "Abonnements": [
        "EDF", "ENGIE", "TOTALENERGIE", "EAU", "SUEZ", "VEOLIA",
        "ORANGE", "SFR", "BOUYGUES", "FREE", "NETFLIX", "SPOTIFY",
        "AMAZON PRIME", "ENI", "VATTENFALL", "OHM", "MINT"
    ]
}

# ============================================================================
# SAVINGS TREND ANALYSIS
# ============================================================================

# Default number of months to analyze for savings trends
DEFAULT_MONTHS_TREND = 12

# ============================================================================
# INTERNAL TRANSFER DETECTION
# ============================================================================

# Default label patterns for detecting internal transfers
INTERNAL_TRANSFER_PATTERNS = [
    "VIR SEPA AURELIEN",
    "ALIMENTATION COMPTE JOINT",
    "VIR SEPA",
    "VIREMENT",
    "VIR ",
    "ALIMENTATION",
    "TRANSFERT"
]
