"""
Module de nettoyage avancé des libellés de transactions.
=====================================================

Ce module fournit des fonctions pour normaliser et nettoyer les libellés
de transactions bancaires, en supprimant le bruit et en extrayant les
 informations pertinentes.

Usage:
    from src.data_cleaning import clean_merchant_name, extract_location
    
    cleaned = clean_merchant_name("MONOPRIX PARIS 14 CB*1234")
    # Result: "MONOPRIX"
    
    location = extract_location("MONOPRIX PARIS 14")
    # Result: "PARIS 14"
"""

import re
from typing import Optional, Tuple

# Import existing clean_label for base cleaning
from modules.utils import clean_label as base_clean_label


# Patterns pour le nettoyage avancé
TERMINAL_PATTERNS = [
    r"CB\*?\d{0,4}",  # CB*1234, CB1234
    r"CARTE\s*\*?\d*",  # CARTE, CARTE*1234
    r"PRLV\s*\w*",  # Prélèvement
    r"VIR\s*\w*",  # Virement
    r"SEPA\s*\w*",  # SEPA
    r"RETRAIT\s*DAB",  # Retrait
    r"CHEQUE\s*\d*",  # Chèque
]

LOCATION_PATTERNS = [
    r"\s+PARIS\s*\d{0,2}",  # PARIS 14, PARIS
    r"\s+LYON\s*\d{0,2}",  # LYON 7
    r"\s+MARSEILLE\s*\d{0,2}",  # MARSEILLE 13
    r"\s+TOULOUSE\s*\d{0,2}",
    r"\s+NANTES\s*\d{0,2}",
    r"\s+STRASBOURG\s*\d{0,2}",
    r"\s+MONTPELLIER\s*\d{0,2}",
    r"\s+BORDEAUX\s*\d{0,2}",
    r"\s+LILLE\s*\d{0,2}",
    r"\s+RENNES\s*\d{0,2}",
    r"\s+REIMS\s*\d{0,2}",
    r"\s+LE\s+HAVRE\s*\d{0,2}",
    r"\s+SAINT[-\s]\w+\s*\d{0,2}",  # SAINT-ETIENNE, SAINT ETIENNE
]

DATE_PATTERNS = [
    r"\d{2}/\d{2}/\d{4}",  # 15/01/2024
    r"\d{2}/\d{2}/\d{2}",  # 15/01/24
    r"\d{2}/\d{2}",  # 15/01
    r"\d{2}-\d{2}-\d{4}",  # 15-01-2024
    r"\d{2}-\d{2}-\d{2}",  # 15-01-24
]


def clean_merchant_name(label: str, aggressive: bool = True) -> str:
    """
    Nettoie un libellé pour extraire le nom du commerçant.
    
    Cette fonction supprime :
    - Les codes de terminaux de paiement (CB*1234)
    - Les dates
    - Les localisations géographiques (si aggressive=True)
    - Les numéros de références
    
    Args:
        label: Libellé brut de la transaction
        aggressive: Si True, supprime aussi les localisations
        
    Returns:
        Nom du commerçant nettoyé
        
    Examples:
        >>> clean_merchant_name("MONOPRIX PARIS 14 CB*1234")
        'MONOPRIX'
        >>> clean_merchant_name("UBER EATS PARIS", aggressive=True)
        'UBER EATS'
        >>> clean_merchant_name("CARREFOUR MARKET LYON 7", aggressive=False)
        'CARREFOUR MARKET LYON 7'
    """
    if not label:
        return ""
    
    cleaned = label.upper()
    
    # 1. Supprimer les dates
    for pattern in DATE_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned)
    
    # 2. Supprimer les codes de terminaux
    for pattern in TERMINAL_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    
    # 3. Supprimer les localisations (si mode agressif)
    if aggressive:
        for pattern in LOCATION_PATTERNS:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    
    # 4. Supprimer les numéros de références (séquences de chiffres longues)
    cleaned = re.sub(r"\b\d{4,}\b", "", cleaned)
    
    # 5. Supprimer les caractères spéciaux en début/fin
    cleaned = re.sub(r"^[^A-Z0-9]+|[^A-Z0-9]+$", "", cleaned)
    
    # 6. Normaliser les espaces multiples
    cleaned = re.sub(r"\s+", " ", cleaned)
    
    # 7. Appliquer le nettoyage de base
    cleaned = base_clean_label(cleaned)
    
    return cleaned.strip()


def extract_location(label: str) -> Optional[str]:
    """
    Extrait la localisation géographique d'un libellé.
    
    Args:
        label: Libellé de la transaction
        
    Returns:
        Localisation extraite ou None
        
    Examples:
        >>> extract_location("MONOPRIX PARIS 14")
        'PARIS 14'
        >>> extract_location("CARREFOUR LYON 7")
        'LYON 7'
        >>> extract_location("AMAZON")
        None
    """
    if not label:
        return None
    
    label_upper = label.upper()
    
    # Rechercher les patterns de localisation
    for pattern in LOCATION_PATTERNS:
        match = re.search(pattern, label_upper, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    
    return None


def extract_card_suffix(label: str) -> Optional[str]:
    """
    Extrait le suffixe de carte (4 derniers chiffres) d'un libellé.
    
    Args:
        label: Libellé de la transaction
        
    Returns:
        Suffixe de carte ou None
        
    Examples:
        >>> extract_card_suffix("CB*1234 MONOPRIX")
        '1234'
        >>> extract_card_suffix("CARTE 5678 AMAZON")
        '5678'
    """
    if not label:
        return None
    
    # Pattern CB*1234 ou CARTE 1234
    match = re.search(r"(?:CB|CARTE)\*?\s*(\d{4})", label, re.IGNORECASE)
    if match:
        return match.group(1)
    
    return None


def normalize_merchant_name(merchant: str) -> str:
    """
    Normalise un nom de commerçant pour la recherche.
    
    - Supprime les suffixes courants (SAS, SARL, etc.)
    - Normalise les abréviations
    - Met en majuscules
    
    Args:
        merchant: Nom du commerçant
        
    Returns:
        Nom normalisé
    """
    if not merchant:
        return ""
    
    normalized = merchant.upper()
    
    # Supprimer les suffixes juridiques
    legal_suffixes = [r"\s+SAS", r"\s+SARL", r"\s+SA", r"\s+EURL", r"\s+SASU"]
    for suffix in legal_suffixes:
        normalized = re.sub(suffix, "", normalized)
    
    # Normaliser les abréviations courantes
    replacements = {
        r"\bST\b": "SAINT",
        r"\bSTE\b": "SAINTE",
        r"\bGEN\b": "GENERAL",
        r"\bMAG\b": "MAGASIN",
        r"\bHYP\b": "HYPERMARCHE",
        r"\bSUP\b": "SUPERMARCHE",
    }
    
    for pattern, replacement in replacements.items():
        normalized = re.sub(pattern, replacement, normalized)
    
    return normalized.strip()


def clean_transaction_label(label: str, amount: float = 0) -> Tuple[str, dict]:
    """
    Nettoyage complet d'un libellé de transaction avec métadonnées.
    
    Args:
        label: Libellé brut
        amount: Montant de la transaction (pour détecter les revenus)
        
    Returns:
        Tuple (libellé_nettoyé, métadonnées)
        
    Examples:
        >>> clean_transaction_label("MONOPRIX PARIS 14 CB*1234", -45.67)
        ('MONOPRIX', {
            'original': 'MONOPRIX PARIS 14 CB*1234',
            'clean_merchant': 'MONOPRIX',
            'location': 'PARIS 14',
            'card_suffix': '1234',
            'is_income': False
        })
    """
    metadata = {
        "original": label,
        "clean_merchant": clean_merchant_name(label, aggressive=True),
        "location": extract_location(label),
        "card_suffix": extract_card_suffix(label),
        "is_income": amount > 0,
    }
    
    return metadata["clean_merchant"], metadata


def batch_clean_labels(labels: list[str], amounts: list[float] = None) -> list[Tuple[str, dict]]:
    """
    Nettoie une liste de libellés en batch.
    
    Args:
        labels: Liste des libellés
        amounts: Liste des montants (optionnel)
        
    Returns:
        Liste de tuples (libellé_nettoyé, métadonnées)
    """
    if amounts is None:
        amounts = [0] * len(labels)
    
    return [
        clean_transaction_label(label, amount)
        for label, amount in zip(labels, amounts)
    ]


# Alias pour compatibilité
extract_merchant = clean_merchant_name
