"""
Transaction Types Module
Centralise la définition et la détection des types de transactions.

🔴 RÈGLE D'OR : Une transaction est caractérisée par SA CATÉGORIE, pas par le signe de son montant.

Ne JAMAIS utiliser `amount > 0` ou `amount < 0` pour déterminer le type d'une transaction.
Utiliser TOUJOURS les fonctions de ce module :
  - is_income_category(category)
  - is_expense_category(category) 
  - get_category_type(category)
  - get_transaction_icon(category)

Exemples :
  ✅ CORRECT : is_expense_category('Alimentation') → True
  ❌ INCORRECT : amount < 0  (une dépense remboursée a un montant positif !)
"""
from typing import List, Tuple, Optional
import pandas as pd

# ============================================================================
# CATÉGORIES PAR TYPE
# ============================================================================

# Catégories considérées comme des REVENUS (entrées d'argent)
INCOME_CATEGORIES = [
    'Revenus',
    'Salaire', 
    'Prime',
    'Remboursement',  # Remboursements sont des entrées mais pas des revenus à proprement parler
    'Revenus secondaires',
    'Investissements',
    'Intérêts',
    'Dividendes',
    'Cadeaux reçus',
    'Ventes',
]

# Catégories à EXCLURE des calculs (ni revenu ni dépense)
EXCLUDED_CATEGORIES = [
    'Virement Interne',
    'Hors Budget',
    'Transfert',
    'Épargne',  # Mouvements entre comptes
]

# Catégories de REMBOURSEMENT (entrées d'argent liées à une dépense précédente)
# Ces catégories sont des cas spéciaux : montant positif mais ce n'est pas un "vrai" revenu
REFUND_CATEGORIES = [
    'Remboursement',
    'Remboursement santé',
    'Remboursement assurance',
]

# Catégories de DÉPENSES par défaut (tout ce qui n'est pas ci-dessus)
# Note : On ne définit pas une liste exhaustive car les catégories sont personnalisables


# ============================================================================
# FONCTIONS DE DÉTECTION
# ============================================================================

def is_income_category(category: Optional[str]) -> bool:
    """
    Détermine si une catégorie est un revenu.
    
    Args:
        category: Nom de la catégorie
        
    Returns:
        True si c'est une catégorie de revenu
        
    Examples:
        >>> is_income_category('Salaire')
        True
        >>> is_income_category('Alimentation')
        False
    """
    if not category:
        return False
    return category.strip() in INCOME_CATEGORIES


def is_expense_category(category: Optional[str]) -> bool:
    """
    Détermine si une catégorie est une dépense.
    
    Args:
        category: Nom de la catégorie
        
    Returns:
        True si c'est une catégorie de dépense
        
    Note:
        Une catégorie est une dépense si elle n'est ni revenu, ni exclue.
    """
    if not category:
        return False
    category = category.strip()
    return (
        category not in INCOME_CATEGORIES and 
        category not in EXCLUDED_CATEGORIES
    )


def is_excluded_category(category: Optional[str]) -> bool:
    """
    Détermine si une catégorie doit être exclue des calculs.
    
    Args:
        category: Nom de la catégorie
        
    Returns:
        True si la catégorie doit être ignorée (virements internes, etc.)
    """
    if not category:
        return False
    return category.strip() in EXCLUDED_CATEGORIES


def is_refund_category(category: Optional[str]) -> bool:
    """
    Détermine si une catégorie est un remboursement.
    
    Les remboursements sont des cas particuliers :
    - Ce sont des entrées d'argent (montant positif)
    - Mais ce ne sont pas des revenus à proprement parler
    - Ils compensent une dépense précédente
    
    Returns:
        True si c'est une catégorie de remboursement
    """
    if not category:
        return False
    return category.strip() in REFUND_CATEGORIES


def get_category_type(category: Optional[str]) -> str:
    """
    Retourne le type d'une catégorie.
    
    Returns:
        'income' | 'expense' | 'refund' | 'excluded' | 'unknown'
    """
    if not category:
        return 'unknown'
    
    if is_excluded_category(category):
        return 'excluded'
    if is_refund_category(category):
        return 'refund'
    if is_income_category(category):
        return 'income'
    if is_expense_category(category):
        return 'expense'
    
    return 'unknown'


def get_transaction_icon(category: Optional[str]) -> str:
    """
    Retourne l'icône emoji appropriée pour une catégorie.
    
    Args:
        category: Nom de la catégorie
        
    Returns:
        Emoji représentant le type de transaction
        
    Examples:
        >>> get_transaction_icon('Salaire')
        '📥'
        >>> get_transaction_icon('Alimentation')
        '📤'
        >>> get_transaction_icon('Remboursement')
        '💰'
    """
    tx_type = get_category_type(category)
    
    icons = {
        'income': '📥',      # Revenu = argent qui entre
        'expense': '📤',     # Dépense = argent qui sort
        'refund': '💰',      # Remboursement = retour d'argent
        'excluded': '➡️',    # Exclu = mouvement interne
        'unknown': '❓'      # Inconnu
    }
    
    return icons.get(tx_type, '❓')


def get_transaction_label(category: Optional[str]) -> str:
    """
    Retourne le libellé français du type de transaction.
    
    Args:
        category: Nom de la catégorie
        
    Returns:
        Libellé en français
        
    Examples:
        >>> get_transaction_label('Salaire')
        'Revenu'
        >>> get_transaction_label('Alimentation')
        'Dépense'
    """
    tx_type = get_category_type(category)
    
    labels = {
        'income': 'Revenu',
        'expense': 'Dépense',
        'refund': 'Remboursement',
        'excluded': 'Exclu',
        'unknown': 'Inconnu'
    }
    
    return labels.get(tx_type, 'Inconnu')


def get_color_for_transaction(category: Optional[str]) -> str:
    """
    Retourne la couleur appropriée pour l'affichage.
    
    Args:
        category: Nom de la catégorie
        
    Returns:
        Nom de couleur Streamlit ('green', 'red', 'blue', 'gray', 'orange')
        
    Examples:
        >>> get_color_for_transaction('Salaire')
        'green'
        >>> get_color_for_transaction('Alimentation')
        'red'
    """
    tx_type = get_category_type(category)
    
    colors = {
        'income': 'green',    # Revenu = vert (positif)
        'expense': 'red',     # Dépense = rouge (attention)
        'refund': 'blue',     # Remboursement = bleu (spécial)
        'excluded': 'gray',   # Exclu = gris (neutre)
        'unknown': 'orange'   # Inconnu = orange (alerte)
    }
    
    return colors.get(tx_type, 'gray')


# ============================================================================
# VALIDATION
# ============================================================================

def validate_amount_consistency(category: str, amount: float) -> Tuple[bool, Optional[str]]:
    """
    Vérifie que le signe du montant correspond à la catégorie.
    
    Args:
        category: Catégorie de la transaction
        amount: Montant de la transaction
        
    Returns:
        Tuple (is_valid, warning_message)
        is_valid : True si cohérent
        warning_message : Message d'alerte si incohérent, None sinon
        
    Examples:
        >>> validate_amount_consistency('Salaire', 2500)
        (True, None)
        >>> validate_amount_consistency('Salaire', -2500)
        (False, "Un revenu devrait avoir un montant positif")
    """
    if is_income_category(category) and amount < 0:
        return (False, f"La catégorie '{category}' est un revenu mais le montant est négatif ({amount})")
    
    if is_expense_category(category) and amount > 0:
        return (False, f"La catégorie '{category}' est une dépense mais le montant est positif ({amount})")
    
    return (True, None)


def suggest_amount_sign(category: str) -> int:
    """
    Suggère le signe attendu pour une catégorie.
    
    Returns:
        1 pour positif (revenu/refund), -1 pour négatif (dépense), 0 pour exclu
    """
    if is_excluded_category(category):
        return 0
    if is_income_category(category) or is_refund_category(category):
        return 1
    return -1


# ============================================================================
# FILTRAGE DATAFRAME
# ============================================================================

def filter_income_transactions(df: pd.DataFrame, include_refunds: bool = False) -> pd.DataFrame:
    """
    Filtre un DataFrame pour ne garder que les revenus.
    
    Args:
        df: DataFrame avec colonne 'category_validated'
        include_refunds: Si True, inclut aussi les remboursements
        
    Returns:
        DataFrame filtré
    """
    if df.empty or 'category_validated' not in df.columns:
        return df
    
    income_cats = INCOME_CATEGORIES.copy()
    if include_refunds:
        income_cats.extend(REFUND_CATEGORIES)
    
    return df[df['category_validated'].isin(income_cats)]


def filter_expense_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtre un DataFrame pour ne garder que les dépenses.
    
    Args:
        df: DataFrame avec colonne 'category_validated'
        
    Returns:
        DataFrame filtré
    """
    if df.empty or 'category_validated' not in df.columns:
        return df
    
    excluded = INCOME_CATEGORIES + EXCLUDED_CATEGORIES
    return df[~df['category_validated'].isin(excluded)]


def filter_excluded_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtre un DataFrame pour exclure les transactions internes.
    
    Args:
        df: DataFrame avec colonne 'category_validated'
        
    Returns:
        DataFrame sans les transactions exclues
    """
    if df.empty or 'category_validated' not in df.columns:
        return df
    
    return df[~df['category_validated'].isin(EXCLUDED_CATEGORIES)]


# ============================================================================
# CALCULS FINANCIERS
# ============================================================================

def calculate_true_income(df: pd.DataFrame, include_refunds: bool = False) -> float:
    """
    Calcule le vrai total des revenus (pas les remboursements).
    
    Args:
        df: DataFrame avec transactions
        include_refunds: Si True, inclut les remboursements
        
    Returns:
        Montant total des revenus
    """
    if df.empty:
        return 0.0
    
    income_df = filter_income_transactions(df, include_refunds=False)
    
    if 'amount' not in income_df.columns:
        return 0.0
    
    # Prendre les montants positifs uniquement (validation)
    return income_df[income_df['amount'] > 0]['amount'].sum()


def calculate_true_expenses(df: pd.DataFrame, include_refunds: bool = True) -> float:
    """
    Calcule le total net des dépenses.
    Une dépense (montant < 0) est compensée par tout montant positif (remboursement)
    dans une catégorie de dépense ou de remboursement.
    
    Args:
        df: DataFrame avec transactions
        include_refunds: Si True, déduit tous les montants positifs des dépenses
        
    Returns:
        Montant total des dépenses nettes (valeur absolue)
    """
    if df.empty:
        return 0.0
    
    expense_df = filter_expense_transactions(df)
    
    if 'amount' not in expense_df.columns:
        return 0.0
    
    # Calcul net pour les catégories de dépenses
    # (Somme des montants négatifs + Somme des montants positifs dans ces catégories)
    total_net = expense_df['amount'].sum()
    
    # Si include_refunds, on déduit aussi les remboursements classés dans INCOME_CATEGORIES
    if include_refunds:
        # On cherche les transactions positives dans REFUND_CATEGORIES
        # Note: REFUND_CATEGORIES est généralement exclu de expense_df (car dans INCOME_CATEGORIES)
        refund_df = df[df['category_validated'].isin(REFUND_CATEGORIES)]
        if not refund_df.empty:
            positive_refunds = refund_df[refund_df['amount'] > 0]['amount'].sum()
            # On soustrait la valeur absolue des remboursements du total des dépenses
            # Comme total_net est négatif (dépenses), on AJOUTE le montant positif
            total_net += positive_refunds

    return abs(total_net) if total_net < 0 else 0.0

def calculate_savings_rate(df: pd.DataFrame) -> float:
    """
    Calcule le taux d'épargne réel.
    
    Formule : (Revenus - Dépenses) / Revenus * 100
    
    Returns:
        Taux d'épargne en pourcentage
    """
    income = calculate_true_income(df, include_refunds=False)
    expenses = calculate_true_expenses(df, include_refunds=True)
    
    if income <= 0:
        return 0.0
    
    savings = income - expenses
    return (savings / income) * 100
