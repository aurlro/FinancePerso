# -*- coding: utf-8 -*-
"""
Module de catégorisation des transactions.

Implémente la cascade de catégorisation :
1. Règles exactes (learning_rules)
2. Règles partielles (pattern matching)
3. ML Local (si activé et disponible)
4. IA Cloud (Gemini/OpenAI/DeepSeek/Ollama)
5. Catégorie par défaut ("Inconnu")
"""

import re
from typing import Any

import pandas as pd

from modules.ai_cache import get_cached_categorization, cache_categorization_result
from modules.constants import SystemCategory
from modules.db.connection import get_db_connection
from modules.db.rules import get_learning_rules
from modules.logger import logger


# Cache mémoire simple pour les catégories
_category_cache: dict[str, str] = {}


def categorize_transaction(
    transaction: dict[str, Any],
    rules: list[dict] | None = None,
    use_ai: bool = True,
) -> str:
    """
    Catégorise une transaction selon la cascade de règles.
    
    Args:
        transaction: Dict avec 'label' et 'amount'
        rules: Liste optionnelle de règles (sinon récupère depuis DB)
        use_ai: Utiliser l'IA si aucune règle ne match
    
    Returns:
        Nom de la catégorie
    """
    label = transaction.get("label", "")
    amount = transaction.get("amount", 0.0)
    
    # 1. Vérifier le cache IA
    cached = get_cached_categorization(label, amount, "default")
    if cached:
        return cached
    
    # 2. Récupérer les règles si non fournies
    if rules is None:
        rules_df = get_learning_rules()
        rules = rules_df.to_dict('records') if not rules_df.empty else []
    
    # 3. Chercher une règle exacte
    for rule in rules:
        if rule.get('pattern', '').upper() == label.upper():
            result = rule.get('category', SystemCategory.UNKNOWN)
            cache_categorization_result(label, amount, "default", result, 1.0)
            return result
    
    # 4. Chercher une règle partielle (contains)
    for rule in sorted(rules, key=lambda r: r.get('priority', 0), reverse=True):
        pattern = rule.get('pattern', '').upper()
        if pattern in label.upper():
            result = rule.get('category', SystemCategory.UNKNOWN)
            cache_categorization_result(label, amount, "default", result, 0.9)
            return result
    
    # 5. Fallback IA si activé
    if use_ai:
        try:
            from modules.ai_manager import ai_manager
            result = ai_manager.categorize(label, amount)
            if result:
                cache_categorization_result(label, amount, "default", result, 0.8)
                return result
        except Exception as e:
            logger.warning(f"AI categorization failed: {e}")
    
    # 6. Catégorie par défaut
    return SystemCategory.UNKNOWN


def categorize_transactions_batch(
    df: pd.DataFrame,
    use_ai: bool = False,
) -> list[str]:
    """
    Catégorise un batch de transactions.
    
    Args:
        df: DataFrame avec colonnes 'label' et 'amount'
        use_ai: Utiliser l'IA (désactivé par défaut pour les batches)
    
    Returns:
        Liste des catégories
    """
    if df.empty:
        return []
    
    # Récupérer toutes les règles une fois
    rules_df = get_learning_rules()
    rules = rules_df.to_dict('records') if not rules_df.empty else []
    
    results = []
    for _, row in df.iterrows():
        tx = {"label": row.get("label", ""), "amount": row.get("amount", 0.0)}
        category = categorize_transaction(tx, rules=rules, use_ai=use_ai)
        results.append(category)
    
    return results


def get_cached_category(label: str, amount: float) -> str | None:
    """
    Récupère une catégorie depuis le cache.
    
    Returns:
        Catégorie si trouvée, None sinon
    """
    cache_key = f"{label.upper()}:{amount}"
    return _category_cache.get(cache_key)


def invalidate_category_cache() -> None:
    """Invalide le cache de catégorisation."""
    global _category_cache
    _category_cache = {}
    logger.info("Category cache invalidated")


def is_valid_category(category: str) -> bool:
    """
    Vérifie si un nom de catégorie est valide.
    
    Args:
        category: Nom à vérifier
    
    Returns:
        True si valide
    """
    if not category or not isinstance(category, str):
        return False
    
    category = category.strip()
    if len(category) == 0 or len(category) > 50:
        return False
    
    return True


def is_system_category(category: str) -> bool:
    """
    Vérifie si une catégorie est une catégorie système.
    
    Args:
        category: Nom à vérifier
    
    Returns:
        True si c'est une catégorie système
    """
    system_categories = {
        SystemCategory.INTERNAL_TRANSFER,
        SystemCategory.OUT_OF_BUDGET,
        SystemCategory.UNKNOWN,
        SystemCategory.AVOIR,
        SystemCategory.OTHER,
    }
    return category in system_categories
