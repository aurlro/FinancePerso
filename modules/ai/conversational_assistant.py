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


import json
import re

# Tool functions that the AI can call
def get_spending_history(category: str = None, months: int = 3) -> dict:
    """
    Get spending history and average for a category over the last N months.
    
    Args:
        category: Category name (optional, if None = total expenses)
        months: Number of months to analyze (default: 3)
        
    Returns:
        Dict with total, average, and monthly breakdown
    """
    df = get_all_transactions()
    today = datetime.date.today()
    
    # Calculate start date
    start_date = (today.replace(day=1) - pd.DateOffset(months=months)).date()
    
    # Filter by date
    df['date_dt'] = pd.to_datetime(df['date'])
    df_period = df[df['date_dt'].dt.date >= start_date].copy()
    
    # Filter expenses
    df_exp = df_period[df_period['amount'] < 0].copy()
    
    # Filter by category
    if category:
        df_exp = df_exp[df_exp['category_validated'] == category]
    
    if df_exp.empty:
        return {
            'message': f"Aucune dépense trouvée pour {category or 'tout'} sur les {months} derniers mois."
        }
    
    # Calculate metrics
    total = abs(df_exp['amount'].sum())
    monthly_data = df_exp.groupby(df_exp['date_dt'].dt.strftime('%Y-%m'))['amount'].sum().abs()
    average = total / months  # Average over requested months, not just active ones to be fair
    
    return {
        'category': category or 'Total',
        'period_months': months,
        'total_spent': round(total, 2),
        'average_monthly': round(average, 2),
        'breakdown': {k: round(v, 2) for k, v in monthly_data.to_dict().items()}
    }

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
            'usage_percent': round(usage_pct, 1),
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


# Mapping of tool names to functions
AVAILABLE_TOOLS = {
    "get_expenses_by_category": get_expenses_by_category,
    "get_budget_status": get_budget_status,
    "get_top_expenses": get_top_expenses,
    "get_spending_history": get_spending_history
}

def execute_tool_call(tool_name: str, args: dict) -> dict:
    """Execute a tool call and return result as a dict."""
    if tool_name not in AVAILABLE_TOOLS:
        return {"error": f"Tool {tool_name} not found"}
    
    try:
        logger.info(f"Executing tool {tool_name} with args {args}")
        return AVAILABLE_TOOLS[tool_name](**args)
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        return {"error": str(e)}


# Main conversational function
def chat_with_assistant(user_message: str, conversation_history: list = None) -> str:
    """
    Process a user message using a ReAct-like loop with the AI provider.
    
    Args:
        user_message: User's question
        conversation_history: Previous messages (optional)
        
    Returns:
        AI assistant's response
    """
    try:
        provider = get_ai_provider()
        model_name = get_active_model_name()
        
        # Context
        categories = get_categories()
        today = datetime.date.today()
        current_month = today.strftime('%Y-%m')
        
        # System Prompt definition
        system_prompt = f"""
        Tu es un assistant financier expert. Tu as accès aux données réelles de l'utilisateur via des outils.
        
        CONTEXTE ACTUEL :
        - Date : {today} (Mois : {current_month})
        - Catégories valides : {', '.join(categories)}

        OUTILS DISPONIBLES :
        1. get_spending_history(category: str, months: int)
           -> Utile pour "moyenne", "tendance", "historique", "3 derniers mois".
           -> Ex: {{"tool": "get_spending_history", "kwargs": {{"category": "Alimentation", "months": 3}}}}

        2. get_expenses_by_category(category: str, month: str = None)
           -> Utile pour le total d'un mois précis ou total global.
           -> Ex: {{"tool": "get_expenses_by_category", "kwargs": {{"category": "Logement", "month": "2026-01"}}}}

        3. get_budget_status(category: str)
           -> Utile pour "budget", "reste à dépenser", "statut".
           -> Ex: {{"tool": "get_budget_status", "kwargs": {{"category": "Loisirs"}}}}

        4. get_top_expenses(month: str = None, limit: int = 5)
           -> Utile pour "plus grosses dépenses", "où va mon argent".
        
        PROTOCOLE DE RÉPONSE :
        - Si tu as besoin d'une information : Réponds UNIQUEMENT avec un objet JSON représentant l'appel d'outil.
          Format : {{"tool": "nom_outil", "kwargs": {{...}}}}
        - Si tu as l'information ou si c'est une question générale : Réponds en texte naturel à l'utilisateur.
        - Ne refuse JAMAIS de répondre si tu peux utiliser un outil pour trouver la réponse.
        - Si l'utilisateur demande une moyenne, calcule-la via get_spending_history.
        """
        
        # Conversation state initialization
        messages = [
            f"Question utilisateur : {user_message}"
        ]
        
        max_turns = 3
        current_turn = 0
        
        while current_turn < max_turns:
            # Construct full prompt for this turn
            full_prompt = f"{system_prompt}\n\nHISTORIQUE :\n" + "\n".join(messages) + "\n\nRÉPONSE (JSON ou Texte) :"
            
            # Call AI
            response = provider.generate_text(full_prompt, model_name=model_name)
            cleaned_response = response.strip()
            
            # Check for JSON tool call
            # We look for a JSON-like structure { ... }
            json_match = re.search(r'\{.*"tool":.*\}', cleaned_response, re.DOTALL)
            
            if json_match:
                try:
                    tool_call = json.loads(json_match.group(0))
                    tool_name = tool_call.get("tool")
                    tool_args = tool_call.get("kwargs", {})
                    
                    # Execute tool
                    result = execute_tool_call(tool_name, tool_args)
                    
                    # Add result to history and loop
                    messages.append(f"AI (Tool Call): {cleaned_response}")
                    messages.append(f"System (Tool Result): {json.dumps(result, ensure_ascii=False)}")
                    current_turn += 1
                    continue
                    
                except json.JSONDecodeError:
                    # If JSON parsing fails, assume it's text or retry? For now, return text.
                    logger.warning("Failed to parse JSON tool call, returning text.")
                    return cleaned_response
            else:
                # No tool call, this is the final answer
                return cleaned_response
        
        return "J'ai essayé de récupérer les informations, mais je n'y suis pas parvenu après plusieurs tentatives."
        
    except Exception as e:
        logger.error(f"Error in conversational assistant: {e}")
        return "Désolé, une erreur technique est survenue. Veuillez réessayer."
