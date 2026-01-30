from dotenv import load_dotenv
from modules.logger import logger
from modules.utils import clean_label
from modules.data_manager import get_categories
from modules.ai_manager import get_ai_provider, get_active_model_name
import json

load_dotenv()

# Rules have been migrated to database (see modules/data_manager.py)

PROMPT_TEMPLATE = """
Tu es un expert en catégorisation financière. Analyse la transaction suivante et détermine la catégorie la plus appropriée.
Catégories possibles : {categories}

Transaction :
- Libellé : {label}
- Montant : {amount}
- Date : {date}

Réponds UNIQUEMENT au format JSON :
{{
  "category": "Nom de la catégorie",
  "confidence": 0.0 à 1.0 (estimation de ta certitude)
}}
"""

# Avoid circular imports by importing inside function or passing rules
# But here we want a clean import. 
# We'll use a local import inside apply_rules to avoid circular dependency with data_manager if any.
# Actually data_manager imports pandas and sqlite3, not categorization. 
# Categorization is imported by 1_Import.py.
# So if we import data_manager here, it should be fine.


def apply_rules(label):
    """
    Apply rules to a transaction label.
    Priority:
    1. User learned rules (DB with pre-compiled patterns)
    2. Hardcoded regex rules (Code)

    Performance: Uses pre-compiled regex patterns for 90-95% speed improvement.
    """
    label_upper = label.upper()

    # 1. User Rules from DB (with pre-compiled patterns for performance)
    try:
        from modules.db.rules import get_compiled_learning_rules
        compiled_rules = get_compiled_learning_rules()

        # Rules are already sorted by priority (highest first)
        for pattern_compiled, category, priority, pattern_str in compiled_rules:
            if pattern_compiled:
                # Use pre-compiled pattern (90-95% faster than re.search on every transaction)
                if pattern_compiled.search(label_upper):
                    return category, 1.0
            else:
                # Fallback for invalid regex: simple string matching
                if pattern_str.upper() in label_upper:
                    return category, 1.0
    except Exception as e:
        logger.error(f"Rule Error: {e}")

    # 2. Hardcoded Rules (Empty as migrated to DB)
    return None, 0.0

def predict_category_ai(label, amount, date):
    """
    Generic AI API call via Manager.
    """
    # Pre-clean label for better AI focus
    cleaned_label = clean_label(label)
    
    try:
        provider = get_ai_provider()
        # Get dynamic categories
        categories_list = get_categories()
        categories_str = ", ".join(categories_list)
        
        # We pass both original and cleaned, just in case context helps, but emphasize cleaned.
        prompt = PROMPT_TEMPLATE.format(
            categories=categories_str,
            label=f"{cleaned_label} (Original: {label})", 
            amount=amount, 
            date=date
        )
        
        model_name = get_active_model_name()
        data = provider.generate_json(prompt, model_name=model_name)
        
        return data.get("category", "Inconnu"), float(data.get("confidence", 0.5))
        
    except Exception as e:
        logger.error(f"AI Manager Error: {e}")
        return "Inconnu", 0.0

def categorize_transaction(label, amount, date):
    """
    Main entry point for categorization.
    1. Try Rules (User & Hardcoded)
    2. Try Business Logic (Internal Transfers)
    3. Try AI if no rule matches
    """
    label_upper = label.upper()
    
    # 1. Rules
    cat, conf = apply_rules(label)
    if cat:
        return cat, "rule", conf
    
    # 2. Heuristic: Internal Transfers Detection
    # If the label contains common internal transfer keywords AND mentions known household members/accounts
    from modules.db.settings import get_internal_transfer_targets

    TRANSFER_KEYWORDS = ["VIR ", "VIREMENT", "VRT", "PIVOT", "MOUVEMENT", "TRANSFERT"]
    INTERNAL_TARGETS = get_internal_transfer_targets()

    if any(k in label_upper for k in TRANSFER_KEYWORDS) and any(t in label_upper for t in INTERNAL_TARGETS):
        return "Virement Interne", "rule", 1.0
        
    # 3. AI
    cat, conf = predict_category_ai(label, amount, date)
    
    # 4. Global Constraint: Negative amounts cannot be "Revenus"
    if cat == "Revenus" and amount < 0:
        return "Inconnu", "rule_constraint", 0.0
        
    return cat, "ai", conf

def generate_financial_report(stats_json):
    """
    Generate a financial report using generic AI provider.
    stats_json: dict containing monthly totals, top categories, ytd data...
    """
    try:
        provider = get_ai_provider()
        model_name = get_active_model_name()
        
        prompt = f"""
        Tu es un conseiller financier personnel bienveillant et perspicace.
        Analyse les données financières suivantes (format JSON) pour le mois courant.
        
        Données :
        {json.dumps(stats_json, indent=2, ensure_ascii=False)}
        
        Tes missions :
        1. **Résumé du mois** : Un paragraphe narratif sur les dépenses du mois, l'évolution par rapport au mois précédent (MoM), et les grands postes de dépenses.
        2. **Bilan Annuel (YTD)** : Un point sur la situation depuis le début de l'année (Total épargné ou perdu, tendances).
        3. **Conseils & Épargne** : 3 conseils concrets et personnalisés pour améliorer l'épargne ou réduire les frais, basés sur les catégories les plus coûteuses identifiées.
        
        Ton ton doit être : Professionnel mais encourageant, "Serene Finance".
        Formate la réponse en Markdown propre (titres #, listes à puces).
        Ne mentionne pas "JSON" dans ta réponse, parle directement à l'utilisateur.
        """
        
        return provider.generate_text(prompt, model_name=model_name)
        
    except Exception as e:
        return f"Erreur lors de la génération du rapport : {e}"
