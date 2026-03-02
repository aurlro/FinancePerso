"""
Constantes pour la gestion des transactions.
===========================================

Ce module définit les constantes utilisées dans le traitement des transactions,
notamment la taxonomie PFCv2 (Personal Finance Categories v2) basée sur le standard Plaid.

Référence: https://plaid.com/docs/transactions/pfc-migration/

Usage:
    from modules.transactions.constants import PFCV2_CATEGORIES, CategoryType

    # Accéder aux catégories
    main_categories = PFCV2_CATEGORIES.keys()
    sub_categories = PFCV2_CATEGORIES["Food & Drink"]  # ["Groceries", "Restaurants", ...]
"""

from enum import Enum


class CategoryType(Enum):
    """Types de catégories financières."""

    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    UNKNOWN = "unknown"


class CategorizationMethod(Enum):
    """Méthodes de catégorisation utilisées."""

    HEURISTIC = "HEURISTIC"  # Règles basées sur des patterns
    SIMILARITY = "SIMILARITY"  # Matching par similarité
    LOCAL_AI = "LOCAL_AI"  # IA locale (Llama)
    CLOUD_AI = "CLOUD_AI"  # IA cloud (Gemini/DeepSeek)
    MANUAL = "MANUAL"  # Catégorisation manuelle


# ============================================================================
# Taxonomie PFCv2 (Personal Finance Categories v2)
# ============================================================================
# Structure conforme au standard Plaid PFCv2
# Référence: https://plaid.com/docs/transactions/pfc-migration/

PFC_TAXONOMY: dict[str, list[str]] = {
    # Revenus
    "INCOME": [
        "Salary",
        "Freelance",
        "Investments",
        "Refunds",
        "Gifts Received",
        "Benefits",
        "Rental Income",
        "Other Income",
    ],
    # Transferts entrants
    "TRANSFER_IN": [
        "Internal Transfer",
        "External Transfer",
        "Investment Transfer",
        "Savings",
    ],
    # Transferts sortants
    "TRANSFER_OUT": [
        "Internal Transfer",
        "External Transfer",
        "Investment Transfer",
        "Savings",
    ],
    # Paiements de prêts
    "Loan Payments": [
        "Car Payment",
        "Credit Card Payment",
        "Student Loan Payment",
        "Mortgage",
        "Personal Loan Payment",
    ],
    # Frais bancaires (sous Financial)
    "Financial": [
        "Bank Fees",
        "Overdraft",
        "ATM",
        "Foreign Transaction",
        "Wire Transfer",
        "Insufficient Funds",
        "Account Maintenance",
        "Interest",
        "Investments",
        "Insurance",
        "Loans",
    ],
    # Alimentation
    "Food & Drink": [
        "Groceries",
        "Restaurants",
        "Fast Food",
        "Coffee Shops",
        "Bars",
        "Food Delivery",
        "Alcohol & Bars",
    ],
    # Transport
    "Transportation": [
        "Fuel",
        "Public Transit",
        "Taxi & Rideshare",
        "Parking",
        "Tolls",
        "Vehicle Maintenance",
        "Vehicle Insurance",
    ],
    # Logement
    "Housing": [
        "Rent",
        "Mortgage",
        "Utilities",
        "Internet",
        "Phone",
        "Home Improvement",
        "Home Insurance",
        "Furniture",
        "Lawn & Garden",
    ],
    # Shopping
    "SHOPPING": [
        "Clothing",
        "Electronics",
        "Books & Hobbies",
        "Sporting Goods",
        "Gifts",
        "Department Stores",
        "Discount Stores",
    ],
    # Santé
    "Health": [
        "Medical",
        "Pharmacy",
        "Dental",
        "Vision",
        "Health Insurance",
        "Gym & Fitness",
        "Mental Health",
    ],
    # Loisirs
    "Entertainment": [
        "Streaming",
        "Movies & Shows",
        "Games",
        "Music",
        "Events & Concerts",
        "Subscriptions",
        "Arts & Crafts",
    ],
    # Voyage
    "Travel": [
        "Flights",
        "Hotels",
        "Car Rental",
        "Vacation",
        "Travel Insurance",
    ],
    # Services
    "Service": [
        "Cleaning",
        "Repair & Maintenance",
        "Legal",
        "Consulting",
        "Accounting",
    ],
    # Éducation
    "Education": [
        "Tuition",
        "Books & Supplies",
        "Courses",
        "Student Loans",
        "Professional Development",
    ],
    # Finances (complément)
    "Financial Services": [
        "Investments",
        "Insurance",
        "Taxes",
        "Financial Planning",
        "Cryptocurrency",
    ],
    # Animaux
    "Pets": [
        "Pet Food",
        "Veterinary",
        "Pet Supplies",
        "Pet Services",
    ],
    # Enfants
    "Kids": [
        "Childcare",
        "Toys",
        "Baby Supplies",
        "Kids Activities",
        "Education",
    ],
    # Taxes
    "Tax": [
        "Income Tax",
        "Property Tax",
        "Sales Tax",
        "VAT",
    ],
    # Dons
    "Donations": [
        "Charity",
        "Religious",
        "Political",
    ],
    # Inconnu
    "Unknown": [
        "Uncategorized",
    ],
}


# ============================================================================
# Mapping des catégories vers leur type (revenu/dépense)
# ============================================================================

CATEGORY_TO_TYPE: dict[str, CategoryType] = {
    "Income": CategoryType.INCOME,
    "Transfer In": CategoryType.INCOME,
    "Transfer Out": CategoryType.TRANSFER,
    "Loan Payments": CategoryType.EXPENSE,
    "Bank Fees": CategoryType.EXPENSE,
    "Food & Drink": CategoryType.EXPENSE,
    "Transportation": CategoryType.EXPENSE,
    "Housing": CategoryType.EXPENSE,
    "Shopping": CategoryType.EXPENSE,
    "Health": CategoryType.EXPENSE,
    "Entertainment": CategoryType.EXPENSE,
    "Travel": CategoryType.EXPENSE,
    "Service": CategoryType.EXPENSE,
    "Education": CategoryType.EXPENSE,
    "Financial": CategoryType.EXPENSE,
    "Financial Services": CategoryType.EXPENSE,
    "Pets": CategoryType.EXPENSE,
    "Kids": CategoryType.EXPENSE,
    "Tax": CategoryType.EXPENSE,
    "Donations": CategoryType.EXPENSE,
    "Unknown": CategoryType.UNKNOWN,
}


# ============================================================================
# Patterns heuristiques pour la catégorisation automatique
# ============================================================================

HEURISTIC_PATTERNS: dict[str, tuple] = {
    # Food & Drink
    r"(?i)(carrefour|auchan|leclerc|lidl|aldi|casino|monoprix|franprix|intermarche|super u|match|colruyt)": (
        "Food & Drink",
        "Groceries",
    ),
    r"(?i)(macdo|mcdonald|burger king|kfc|subway|quick|five guys|taco bell|chipotle)": (
        "Food & Drink",
        "Fast Food",
    ),
    r"(?i)(starbuck|costa|pret|paul|eric kayser|boulangerie|patisserie|brasserie|cafe)": (
        "Food & Drink",
        "Coffee Shops",
    ),
    r"(?i)(uber eat|deliveroo|just eat|foodchery|stuart|glovo)": ("Food & Drink", "Food Delivery"),
    # Transportation
    r"(?i)(total|shell|bp|esso|avia|e\.leclerc essence|carrefour essence|elan|agip)": (
        "Transportation",
        "Fuel",
    ),
    r"(?i)(uber|bolt|taxi|g7|allocab|marcel|heetch|kapten|free now)": (
        "Transportation",
        "Taxi & Rideshare",
    ),
    r"(?i)(ratp|sncf|transilien|metro|bus|tram|navigo|idf mobilit|cityscoot)": (
        "Transportation",
        "Public Transit",
    ),
    r"(?i)(parking|indigo|saemes|park|garage|stationnement)": ("Transportation", "Parking"),
    # Financial
    r"(?i)(agios|frais|commission|interet|cheque|prelevement|tip|gratuity)": (
        "Financial",
        "Bank Fees",
    ),
    r"(?i)(assurance|axa|maif|macif|gmf|groupama|allianz|generali|mnef)": (
        "Financial",
        "Insurance",
    ),
    # Housing
    r"(?i)(edf|engie|direct energie|total energie|veolia|suez|grdf|eau)": ("Housing", "Utilities"),
    r"(?i)(orange|sfr|bouygues|free mobile|sosh|red|coriolis|nrj mobile)": ("Housing", "Phone"),
    r"(?i)(orange|sfr|free|bouygues telecom.*box|sosh.*box|numericable)": ("Housing", "Internet"),
    r"(?i)(loyer|rent|proprietaire|agence|foncia|orpi|century|coldwell)": ("Housing", "Rent"),
    # Entertainment
    r"(?i)(netflix|spotify|amazon prime|disney|apple tv|youtube|canal|ocs)": (
        "Entertainment",
        "Streaming",
    ),
    r"(?i)(cinema|ugc|gaumont|pathe|mk2|cine|imax)": ("Entertainment", "Movies & Shows"),
    # Health
    r"(?i)(pharmacie|pharmacy|parapharmacie|sephora|nocibe|marionnaud)": ("Health", "Pharmacy"),
    r"(?i)(doctolib|medecin|dentiste|ophtalmo|kine|osteopathe|generaliste)": ("Health", "Medical"),
    r"(?i)(basic fit|keep cool|neoness|fitness park|gym|club med|wellness)": (
        "Health",
        "Gym & Fitness",
    ),
    # Income patterns (positive amounts)
    r"(?i)(salaire|virement.*employeur|paye|remuneration|wage|payroll)": ("Income", "Salary"),
    r"(?i)(remboursement|rembourse|retrocession|refund|reimbursement)": ("Income", "Refunds"),
    r"(?i)(freelance|consulting|contract|mission|prestation)": ("Income", "Freelance"),
    # Shopping
    r"(?i)(amazon|cdiscount|fnac|darty|boulanger|ldlc|top achat|materiel)": (
        "Shopping",
        "Electronics",
    ),
    r"(?i)(zara|h&m|uniqlo|celio|jules|hm|bershka|pull.*bear|mango)": ("Shopping", "Clothing"),
    # Travel
    r"(?i)(airbnb|booking|hotel|ibis|mercure|novotel|hilton|marriott)": ("Travel", "Hotels"),
    r"(?i)(air france|easyjet|ryanair|transavia|vueling|volotea|lufthansa)": ("Travel", "Flights"),
}


# ============================================================================
# Seuils de confiance
# ============================================================================

CONFIDENCE_THRESHOLDS = {
    "HEURISTIC": 0.95,
    "SIMILARITY_HIGH": 0.90,
    "SIMILARITY_MEDIUM": 0.75,
    "AI_HIGH": 0.85,
    "AI_MEDIUM": 0.70,
    "AI_LOW": 0.50,
}


# ============================================================================
# Fonctions utilitaires
# ============================================================================


def get_category_type(category: str) -> CategoryType:
    """
    Détermine le type d'une catégorie (revenu/dépense/transfert).

    Args:
        category: Nom de la catégorie principale (ex: "Food & Drink")

    Returns:
        Type de la catégorie
    """
    return CATEGORY_TO_TYPE.get(category, CategoryType.UNKNOWN)


def is_expense_category(category: str) -> bool:
    """Vérifie si une catégorie est une dépense."""
    return get_category_type(category) == CategoryType.EXPENSE


def is_income_category(category: str) -> bool:
    """Vérifie si une catégorie est un revenu."""
    return get_category_type(category) == CategoryType.INCOME


def get_all_categories() -> list[str]:
    """Retourne toutes les catégories principales."""
    return list(PFC_TAXONOMY.keys())


def get_subcategories(main_category: str) -> list[str]:
    """
    Retourne les sous-catégories d'une catégorie principale.

    Args:
        main_category: Catégorie principale (ex: "Food & Drink")

    Returns:
        Liste des sous-catégories
    """
    return PFC_TAXONOMY.get(main_category, [])


def format_category(main: str, sub: str) -> str:
    """
    Formate une catégorie au format "Main > Sub".

    Args:
        main: Catégorie principale
        sub: Sous-catégorie

    Returns:
        Chaîne formatée
    """
    return f"{main} > {sub}"


def parse_category(category_str: str) -> tuple:
    """
    Parse une catégorie formatée "Main > Sub".

    Args:
        category_str: Chaîne formatée

    Returns:
        Tuple (main, sub)
    """
    if " > " in category_str:
        parts = category_str.split(" > ", 1)
        return parts[0], parts[1]
    return category_str, ""


# ============================================================================
# Alias pour compatibilité
# ============================================================================

PFCV2_CATEGORIES = PFC_TAXONOMY  # Alias pour compatibilité legacy
