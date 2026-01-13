import google.generativeai as genai
from dotenv import load_dotenv
from modules.logger import logger
import os
import json
import re

load_dotenv()

# Configure API
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Mock rules for MVP
# Rules have been migrated to database (see modules/data_manager.py)
RULES = []

PROMPT_TEMPLATE = """
Tu es un expert en catégorisation financière. Analyse la transaction suivante et détermine la catégorie la plus appropriée.
Catégories possibles : Alimentation, Transport, Logement, Santé, Loisirs, Achats, Abonnements, Restaurants, Services, Virements, Inconnu.

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

def clean_label(label):
    """
    Remove common bank noise to help AI focus on merchant name.
    Ex: 'Carte 30/12/25 Ittrattoria 4 Cb*6759' -> 'Ittrattoria 4'
    """
    # Remove dates (dd/mm/yy or dd/mm)
    label = re.sub(r'\d{2}/\d{2}(/\d{2,4})?', '', label)
    # Remove "Carte", "Cb", numbers with *
    label = re.sub(r'(?i)CARTE|CB\*?\d*|PRLV|SEPA|VIR', '', label)
    # Remove leading/trailing non-alphanumeric
    label = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', label)
    # Remove multiple spaces
    label = re.sub(r'\s+', ' ', label)
    return label.strip()

# Avoid circular imports by importing inside function or passing rules
# But here we want a clean import. 
# We'll use a local import inside apply_rules to avoid circular dependency with data_manager if any.
# Actually data_manager imports pandas and sqlite3, not categorization. 
# Categorization is imported by 1_Import.py.
# So if we import data_manager here, it should be fine.

from modules.data_manager import get_learning_rules
from modules.ai_manager import get_ai_provider, get_active_model_name

def apply_rules(label):
    """
    Apply rules to a transaction label.
    Priority: 
    1. User learned rules (DB)
    2. Hardcoded regex rules (Code)
    """
    label_upper = label.upper()
    
    # 1. User Rules from DB
    try:
        df_rules = get_learning_rules()
        if not df_rules.empty:
            for index, row in df_rules.iterrows():
                # User rules are stored as patterns (regex or simple string)
                # We assume simple string match if not valid regex, or just regex.
                # To be safe and simple: treating user pattern as "contains" (case insensitive) if it's simple text
                # or we can treat everything as regex? Let's treat as regex for power users, but escape if simple?
                # For "Memory", usuallly it's "CONTAINS string". 
                pattern = row['pattern']
                # If the pattern is just a word, make it a case-insensitive search
                # But to support the "Memory" feature which usually snapshots a cleaned label or a specific string...
                # Let's try simple regex search.
                try:
                    if re.search(pattern, label_upper, re.IGNORECASE):
                        return row['category'], 1.0
                    if pattern.upper() in label_upper: # fallback double check
                         return row['category'], 1.0
                except re.error:
                    # Fallback for bad regex: simple string check
                    if pattern.upper() in label_upper:
                         return row['category'], 1.0
    except Exception as e:
        logger.error(f"Rule Error: {e}")

    # 2. Hardcoded Rules
    for pattern, category in RULES:
        if re.search(pattern, label_upper):
            return category, 1.0 
    return None, 0.0

def predict_category_ai(label, amount, date):
    """
    Generic AI API call via Manager.
    """
    # Pre-clean label for better AI focus
    cleaned_label = clean_label(label)
    
    try:
        provider = get_ai_provider()
        model_name = get_active_model_name()
        
        # We pass both original and cleaned, just in case context helps, but emphasize cleaned.
        prompt = PROMPT_TEMPLATE.format(label=f"{cleaned_label} (Original: {label})", amount=amount, date=date)
        
        data = provider.generate_json(prompt, model_name=model_name)
        
        return data.get("category", "Inconnu"), float(data.get("confidence", 0.5))
        
    except Exception as e:
        logger.error(f"AI Manager Error: {e}")
        return "Inconnu", 0.0

def categorize_transaction(label, amount, date):
    """
    Main entry point for categorization.
    1. Try Rules
    2. Try AI if no rule matches
    """
    # 1. Rules
    cat, conf = apply_rules(label)
    if cat:
        return cat, "rule", conf
        
    # 2. AI
    cat, conf = predict_category_ai(label, amount, date)
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
