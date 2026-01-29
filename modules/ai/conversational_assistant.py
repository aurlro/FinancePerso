"""
Conversational AI Assistant for Financial Queries.

Allows users to ask questions about their finances in natural language.
"""
import pandas as pd
import datetime
from modules.ai_manager import get_ai_provider, get_active_model_name
from modules.db.transactions import get_all_transactions
from modules.db.budgets import get_budgets
from modules.db.categories import get_categories
from modules.logger import logger


# Tool functions that the AI can call
def get_expenses_by_category(category: str = None, month: str = None) -> dict:
    """
    Get total expenses for a category and/or month.
    
    Args:
        category: Category name (optional)
        month: Month in YYYY-MM format (optional)
        
    Returns:
        Dict with total and transaction count
    """
    df = get_all_transactions()
    df_exp = df[df['amount'] < 0].copy()
    
    if month:
        df_exp['date_dt'] = pd.to_datetime(df_exp['date'])
        df_exp = df_exp[df_exp['date_dt'].dt.strftime('%Y-%m') == month]
    
    if category:
        df_exp = df_exp[df_exp['category_validated'] == category]
    
    total = df_exp['amount'].sum()
    count = len(df_exp)
    
    return {
        'total': abs(total),
        'count': count,
        'category': category or 'Toutes',
        'month': month or 'Toutes périodes'
    }


def get_budget_status(category: str = None) -> dict:
    """
    Get budget status for a category or all categories.
    
    Args:
        category: Category name (optional)
        
    Returns:
        Dict with budget info
    """
    budgets = get_budgets()
    
    if budgets.empty:
        return {'message': 'Aucun budget défini'}
    
    if category:
        budget_row = budgets[budgets['category'] == category]
        if budget_row.empty:
            return {'message': f'Pas de budget défini pour {category}'}
        
        budget_amt = budget_row.iloc[0]['amount']
        
        # Get current month spending
        df = get_all_transactions()
        today = datetime.date.today()
        month_str = today.strftime('%Y-%m')
        
        df['date_dt'] = pd.to_datetime(df['date'])
        df_month = df[df['date_dt'].dt.strftime('%Y-%m') == month_str]
        df_cat = df_month[(df_month['category_validated'] == category) & (df_month['amount'] < 0)]
        
        spent = abs(df_cat['amount'].sum())
        remaining = budget_amt - spent
        usage_pct = (spent / budget_amt * 100) if budget_amt > 0 else 0
        
        return {
            'category': category,
            'budget': budget_amt,
            'spent': spent,
            'remaining': remaining,
            'usage_percent': usage_pct,
            'status': 'ok' if usage_pct < 80 else ('warning' if usage_pct < 100 else 'overrun')
        }
    else:
        return {
            'message': 'Budgets disponibles',
            'categories': budgets['category'].tolist()
        }


def get_top_expenses(month: str = None, limit: int = 5) -> list:
    """
    Get top expenses for a period.
    
    Args:
        month: Month in YYYY-MM format (optional)
        limit: Number of results
        
    Returns:
        List of top expense dicts
    """
    df = get_all_transactions()
    df_exp = df[df['amount'] < 0].copy()
    
    if month:
        df_exp['date_dt'] = pd.to_datetime(df_exp['date'])
        df_exp = df_exp[df_exp['date_dt'].dt.strftime('%Y-%m') == month]
    
    df_exp['abs_amount'] = df_exp['amount'].abs()
    top = df_exp.nlargest(limit, 'abs_amount')
    
    return [
        {
            'label': row['label'],
            'amount': abs(row['amount']),
            'category': row['category_validated'],
            'date': row['date']
        }
        for _, row in top.iterrows()
    ]


# Main conversational function
def chat_with_assistant(user_message: str, conversation_history: list = None) -> str:
    """
    Process a user message and generate a response using AI with function calling.
    
    Args:
        user_message: User's question
        conversation_history: Previous messages (optional)
        
    Returns:
        AI assistant's response
    """
    try:
        provider = get_ai_provider()
        model_name = get_active_model_name()
        
        # Build system prompt with available tools
        system_prompt = """
        Tu es un assistant financier personnel intelligent. Tu as accès aux données financières de l'utilisateur.
        
        Outils disponibles :
        - get_expenses_by_category(category, month) : Obtenir les dépenses par catégorie/mois
        - get_budget_status(category) : Vérifier le statut d'un budget
        - get_top_expenses(month, limit) : Obtenir les plus grosses dépenses
        
        Réponds de manière concise et amicale. Utilise les outils si nécessaire pour répondre précisément.
        """
        
        # For MVP, we'll use a simple prompt-based approach
        # In production, implement proper function calling with the AI provider
        
        # Get context
        categories = get_categories()
        today = datetime.date.today()
        current_month = today.strftime('%Y-%m')
        
        prompt = f"""
        {system_prompt}
        
        Catégories disponibles : {', '.join(categories)}
        Mois actuel : {current_month}
        
        Question de l'utilisateur : {user_message}
        
        Si la question nécessite des données spécifiques (montants, budgets, etc.), 
        réponds en expliquant comment l'utilisateur peut trouver cette information dans l'application.
        Sinon, réponds directement de manière utile et concise.
        """
        
        response = provider.generate_text(prompt, model_name=model_name)
        
        logger.info(f"Conversational assistant responded to: {user_message[:50]}...")
        return response
        
    except Exception as e:
        logger.error(f"Error in conversational assistant: {e}")
        return "Désolé, je rencontre un problème technique. Pouvez-vous reformuler votre question ?"
