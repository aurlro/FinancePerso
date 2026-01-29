"""
Smart Tag Suggestions using AI.

Analyzes transaction context to suggest relevant tags.
"""
import pandas as pd
from modules.ai_manager import get_ai_provider, get_active_model_name
from modules.logger import logger


def suggest_tags_for_transaction(tx_row: pd.Series) -> list:
    """
    Suggest contextual tags for a single transaction using AI.
    
    Args:
        tx_row: Series with transaction data (label, amount, category_validated, date)
        
    Returns:
        List of suggested tag strings
        
    Example:
        tags = suggest_tags_for_transaction(transaction)
        # ['Remboursement', 'Professionnel']
    """
    try:
        provider = get_ai_provider()
        model_name = get_active_model_name()
        
        # Build context
        label = tx_row.get('label', '')
        amount = tx_row.get('amount', 0)
        category = tx_row.get('category_validated', 'Inconnu')
        date = tx_row.get('date', '')
        
        prompt = f"""
        Analyse cette transaction et suggère 1 à 3 tags pertinents parmi cette liste :
        - Remboursement
        - Professionnel
        - Cadeau
        - Urgent
        - Récurrent
        - Exceptionnel
        - Santé
        - Famille
        - Loisirs
        
        Transaction :
        - Libellé : {label}
        - Montant : {amount}€
        - Catégorie : {category}
        - Date : {date}
        
        Réponds UNIQUEMENT en JSON (liste de strings) :
        ["Tag1", "Tag2"]
        
        Si aucun tag ne semble pertinent, renvoie [].
        """
        
        tags = provider.generate_json(prompt, model_name=model_name)
        
        # Validate response
        if isinstance(tags, list):
            return [str(tag) for tag in tags if tag]
        return []
        
    except Exception as e:
        logger.error(f"Error suggesting tags: {e}")
        return []


def suggest_tags_batch(df: pd.DataFrame, limit: int = 20) -> dict:
    """
    Suggest tags for multiple transactions in batch.
    
    Args:
        df: DataFrame with transactions
        limit: Maximum number of transactions to process
        
    Returns:
        Dict mapping transaction IDs to suggested tags
        {tx_id: ['Tag1', 'Tag2'], ...}
    """
    if df.empty:
        return {}
    
    # Limit to avoid excessive API calls
    df_sample = df.head(limit)
    
    suggestions = {}
    
    for _, row in df_sample.iterrows():
        tx_id = row.get('id')
        tags = suggest_tags_for_transaction(row)
        if tags:
            suggestions[tx_id] = tags
    
    logger.info(f"Generated tag suggestions for {len(suggestions)} transactions")
    return suggestions
