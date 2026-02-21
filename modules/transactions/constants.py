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
from typing import Dict, List, Optional


class CategoryType(Enum):
    """Types de catégories financières."""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    UNKNOWN = "unknown"


class CategorizationMethod(Enum):
    """Méthodes de catégorisation utilisées."""
    HEURISTIC = "HEURISTIC"      # Règles basées sur des patterns
    SIMILARITY = "SIMILARITY"    # Matching par similarité
    LOCAL_AI = "LOCAL_AI"        # IA locale (Llama)
    CLOUD_AI = "CLOUD_AI"        # IA cloud (Gemini/DeepSeek)
    MANUAL = "MANUAL"            # Catégorisation manuelle


# ============================================================================
# Taxonomie PFCv2 (Personal Finance Categories v2)
# ============================================================================

PFCV2_CATEGORIES: Dict[str, List[str]] = {
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
    "LOAN_PAYMENTS": [
        "Car Payment",
        "Credit Card Payment",
        "Student Loan Payment",
        "Mortgage Payment",
        "Personal Loan Payment",
    ],
    
    # Frais bancaires
    "BANK_FEES": [
        "Overdraft",
        "ATM",
        "Foreign Transaction",
        "Wire Transfer",
        "Insufficient Funds",
        "Account Maintenance",
    ],
    
    # Alimentation
    "FOOD_AND_DRINK": [
        "Groceries",
        "Restaurants",
        "Fast Food",
        "Coffee Shops",
        "Bars",
        "Food Delivery",
        "Alcohol & Bars",
    ],
    
    # Transport
    "TRANSPORTATION": [
        "Fuel",
        "Public Transit",
        "Taxi & Rideshare",
        "Parking",
        "Tolls",
        "Vehicle Maintenance",
        "Vehicle Insurance",
    ],
    
    # Logement
    "HOME": [
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
    "HEALTH": [
        "Medical",
        "Pharmacy",
        "Dental",
        "Vision",
        "Health Insurance",
        "Gym & Fitness",
        "Mental Health",
    ],
    
    # Loisirs
    "ENTERTAINMENT": [
        "Streaming",
        "Movies & Shows",
        "Games",
        "Music",
        "Events & Concerts",
        "Subscriptions",
        "Arts & Crafts",
    ],
    
    # Voyage
    "TRAVEL": [
        "Flights",
        "Hotels",
        "Car Rental",
        "Vacation",
        "Travel Insurance",
    ],
    
    # Services
    "SERVICE": [
        "Cleaning",
        "Repair & Maintenance",
        "Legal",
        "Consulting",
        "Accounting",
    ],
    
    # Éducation
    "EDUCATION": [
        "Tuition",
        "Books & Supplies",
        "Courses",
        "Student Loans",
        "Professional Development",
    ],
    
    # Finances
    "FINANCIAL": [
        "Investments",
        "Insurance",
        "Taxes",
        "Financial Planning",
        "Cryptocurrency",
    ],
    
    # Animaux
    "PETS": [
        "Pet Food",
        "Veterinary",
        "Pet Supplies",
        "Pet Services",
    ],
    
    # Enfants
    "KIDS": [
        "Childcare",
        "Toys",
        "Baby Supplies",
        "Kids Activities",
        "Education",
    ],
    
    # Taxes
    "TAX": [
        "Income Tax",
        "Property Tax",
        "Sales Tax",
        "VAT",
    ],
    
    # Dons
    "DONATIONS": [
        "Charity",
        "Religious",
        "Political",
    ],
    
    # Inconnu
    "UNKNOWN": [
        "Uncategorized",
    ],
}


# ============================================================================
# Mapping des catégories vers leur type (revenu/dépense)
# ============================================================================

CATEGORY_TO_TYPE: Dict[str, CategoryType] = {
    "INCOME": CategoryType.INCOME,
    "TRANSFER_IN": CategoryType.INCOME,
    "TRANSFER_OUT": CategoryType.TRANSFER,
    "LOAN_PAYMENTS": CategoryType.EXPENSE,
    "BANK_FEES": CategoryType.EXPENSE,
    "FOOD_AND_DRINK": CategoryType.EXPENSE,
    "TRANSPORTATION": CategoryType.EXPENSE,
    "HOME": CategoryType.EXPENSE,
    "SHOPPING": CategoryType.EXPENSE,
    "HEALTH": CategoryType.EXPENSE,
    "ENTERTAINMENT": CategoryType.EXPENSE,
    "TRAVEL": CategoryType.EXPENSE,
    "SERVICE": CategoryType.EXPENSE,
    "EDUCATION": CategoryType.EXPENSE,
    "FINANCIAL": CategoryType.EXPENSE,
    "PETS": CategoryType.EXPENSE,
    "KIDS": CategoryType.EXPENSE,
    "TAX": CategoryType.EXPENSE,
    "DONATIONS": CategoryType.EXPENSE,
    "UNKNOWN": CategoryType.UNKNOWN,
}


# ============================================================================
# Patterns heuristiques pour la catégorisation automatique
# ============================================================================

HEURISTIC_PATTERNS: Dict[str, tuple] = {
    # Food & Drink
    r"(?i)(carrefour|auchan|leclerc|lidl|aldi|casino|monoprix|franprix|intermarche|super u|match|colruyt)": 
        ("FOOD_AND_DRINK", "Groceries"),
    r"(?i)(macdo|mcdonald|burger king|kfc|subway|quick|five guys|taco bell|chipotle)": 
        ("FOOD_AND_DRINK", "Fast Food"),
    r"(?i)(starbuck|costa|pret|paul|eric kayser|boulangerie|patisserie|brasserie|cafe)": 
        ("FOOD_AND_DRINK", "Coffee Shops"),
    r"(?i)(uber eat|deliveroo|just eat|foodchery|stuart|glovo)": 
        ("FOOD_AND_DRINK", "Food Delivery"),
    
    # Transportation
    r"(?i)(total|shell|bp|esso|avia|e\.leclerc essence|carrefour essence|elan|agip)": 
        ("TRANSPORTATION", "Fuel"),
    r"(?i)(uber|bolt|taxi|g7|allocab|marcel|heetch|kapten|free now)": 
        ("TRANSPORTATION", "Taxi & Rideshare"),
    r"(?i)(ratp|sncf|transilien|metro|bus|tram|navigo|idf mobilit|cityscoot)": 
        ("TRANSPORTATION", "Public Transit"),
    r"(?i)(parking|indigo|saemes|park|garage|stationnement)": 
        ("TRANSPORTATION", "Parking"),
    
    # Financial
    r"(?i)(agios|frais|commission|interet|cheque|prelevement|tip|gratuity)": 
        ("BANK_FEES", "Overdraft"),
    r"(?i)(assurance|axa|maif|macif|gmf|groupama|allianz|generali|mnef)": 
        ("FINANCIAL", "Insurance"),
    
    # Housing
    r"(?i)(edf|engie|direct energie|total energie|veolia|suez|grdf|eau)": 
        ("HOME", "Utilities"),
    r"(?i)(orange|sfr|bouygues|free mobile|sosh|red|coriolis|nrj mobile)": 
        ("HOME", "Phone"),
    r"(?i)(orange|sfr|free|bouygues telecom.*box|sosh.*box|numericable)": 
        ("HOME", "Internet"),
    r"(?i)(loyer|rent|proprietaire|agence|foncia|orpi|century|coldwell)": 
        ("HOME", "Rent"),
    
    # Entertainment
    r"(?i)(netflix|spotify|amazon prime|disney|apple tv|youtube|canal|ocs)": 
        ("ENTERTAINMENT", "Streaming"),
    r"(?i)(cinema|ugc|gaumont|pathe|mk2|cine|imax)": 
        ("ENTERTAINMENT", "Movies & Shows"),
    
    # Health
    r"(?i)(pharmacie|pharmacy|parapharmacie|sephora|nocibe|marionnaud)": 
        ("HEALTH", "Pharmacy"),
    r"(?i)(doctolib|medecin|dentiste|ophtalmo|kine|osteopathe|generaliste)": 
        ("HEALTH", "Medical"),
    r"(?i)(basic fit|keep cool|neoness|fitness park|gym|club med|wellness)": 
        ("HEALTH", "Gym & Fitness"),
    
    # Income patterns (positive amounts)
    r"(?i)(salaire|virement.*employeur|paye|remuneration|wage|payroll)": 
        ("INCOME", "Salary"),
    r"(?i)(remboursement|rembourse|retrocession|refund|reimbursement)": 
        ("INCOME", "Refunds"),
    r"(?i)(freelance|consulting|contract|mission|prestation)": 
        ("INCOME", "Freelance"),
    
    # Shopping
    r"(?i)(amazon|cdiscount|fnac|darty|boulanger|ldlc|top achat|materiel)": 
        ("SHOPPING", "Electronics"),
    r"(?i)(zara|h&m|uniqlo|celio|jules|hm|bershka|pull.*bear|mango)": 
        ("SHOPPING", "Clothing"),
    
    # Travel
    r"(?i)(airbnb|booking|hotel|ibis|mercure|novotel|hilton|marriott)": 
        ("TRAVEL", "Hotels"),
    r"(?i)(air france|easyjet|ryanair|transavia|vueling|volotea|lufthansa)": 
        ("TRAVEL", "Flights"),
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
        category: Nom de la catégorie principale (ex: "FOOD_AND_DRINK")
        
    Returns:
        Type de la catégorie
    """
    return CATEGORY_TO_TYPE.get(category.upper(), CategoryType.UNKNOWN)


def is_expense_category(category: str) -> bool:
    """Vérifie si une catégorie est une dépense."""
    return get_category_type(category) == CategoryType.EXPENSE


def is_income_category(category: str) -> bool:
    """Vérifie si une catégorie est un revenu."""
    return get_category_type(category) == CategoryType.INCOME


def get_all_categories() -> List[str]:
    """Retourne toutes les catégories principales."""
    return list(PFCV2_CATEGORIES.keys())


def get_subcategories(main_category: str) -> List[str]:
    """
    Retourne les sous-catégories d'une catégorie principale.
    
    Args:
        main_category: Catégorie principale (ex: "FOOD_AND_DRINK")
        
    Returns:
        Liste des sous-catégories
    """
    return PFCV2_CATEGORIES.get(main_category.upper(), [])


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
