import pandas as pd
from modules.categorization import clean_label
from modules.data_manager import get_learning_rules

def detect_recurring_payments(df):
    """
    Analyze transactions to find recurring patterns (Subscriptions, Salaries, Bills).
    Returns a DataFrame of detected recurring items.
    """
    if df.empty:
        return pd.DataFrame()

    # Work on a copy and exclude internal transfers
    data = df[~df['category_validated'].isin(['Virement Interne', 'Hors Budget'])].copy()
    
    # 1. Clean labels for grouping
    # We use a stricter cleaning here to ensure slight variations (dates) don't break grouping
    data['clean_label_strict'] = data['label'].apply(clean_label)
    
    # 2. Group analysis
    recurring_items = []
    
    # Filter only relevant columns for speed
    # We need date, amount, clean_label_strict
    data['date'] = pd.to_datetime(data['date'])
    
    grouped = data.groupby('clean_label_strict')
    
    for label, group in grouped:
        if len(group) < 2:
            continue
            
        # Check amounts consistency
        # Subscriptions usually have exact same amount
        # Utilities might vary slightly (Electricity, Water, etc.)
        amounts = group['amount'].tolist()
        amounts_std = group['amount'].std()
        avg_amount = group['amount'].mean()
        
        # Determine variability
        # Higher tolerance for utilities/energy (usually negative amounts between -30 and -300)
        # We'll use 15% for utilities and 5% for others
        is_energy = any(k in label.upper() for k in ["EDF", "ENGIE", "TOTAL", "EAU", "SUEZ", "VEOLIA", "OHM", "MINT", "VATTEN"])
        tolerance = 0.15 if is_energy else 0.05
        
        is_consistent_amount = (amounts_std / abs(avg_amount)) < tolerance if avg_amount != 0 else (amounts_std == 0)
        
        # Check Periodicity
        dates = group['date'].sort_values()
        diffs = dates.diff().dropna()
        avg_diff_days = diffs.dt.days.mean()
        
        # Look for frequencies: Monthly (~30d), Quarterly (~90d), Annual (~365d)
        is_recurring = False
        freq_label = ""
        
        if 25 <= avg_diff_days <= 35:
            is_recurring = True
            freq_label = "Mensuel"
        elif 80 <= avg_diff_days <= 100:
            is_recurring = True
            freq_label = "Trimestriel"
        elif 350 <= avg_diff_days <= 380:
            is_recurring = True
            freq_label = "Annuel"
        
        if is_consistent_amount and is_recurring:
            # It's a candidate
            # Determine category if known
            current_cat = group.iloc[0]['category_validated']
            
            recurring_items.append({
                "label": label,
                "avg_amount": round(avg_amount, 2),
                "frequency_days": round(avg_diff_days, 1),
                "frequency_label": freq_label,
                "count": len(group),
                "last_date": group['date'].max().date(),
                "category": current_cat,
                "is_subscription_candidate": True,
                "variability": "Variable" if (amounts_std / abs(avg_amount)) > 0.05 else "Fixe"
            })
            
    if not recurring_items:
        return pd.DataFrame(columns=["label", "avg_amount", "frequency_days", "frequency_label", "count", "last_date", "category", "is_subscription_candidate", "variability"])
        
    return pd.DataFrame(recurring_items).sort_values(by='avg_amount')


def detect_financial_profile(df):
    """
    Detect candidates for key financial items: Salary, Rent, Loans, Utilities.
    Filters out items that already have a learning rule.
    """
    candidates = []
    
    # Get existing rules to avoid redundancy
    rules = get_learning_rules()
    existing_patterns = rules['pattern'].unique().tolist() if not rules.empty else []
    
    def is_new(label_clean):
        # Simple exact match check. Could be fuzzier.
        return label_clean not in existing_patterns
    
    # 1. Salary: Positives > 500
    incomes = df[df['amount'] > 500].copy()
    if not incomes.empty:
        incomes['clean'] = incomes['label'].apply(clean_label)
        grouped = incomes.groupby('clean').agg({'amount': 'mean', 'date': 'count'}).reset_index()
        for _, row in grouped.iterrows():
            if is_new(row['clean']):
                candidates.append({
                    "type": "Salaire (estimé)",
                    "label": row['clean'],
                    "amount": row['amount'],
                    "confidence": "Haute" if row['date'] > 1 else "Moyenne",
                    "default_category": "Revenus"
                })

    # 2. Fixed Expenses & Bills
    expenses = df[df['amount'] < 0].copy()
    if not expenses.empty:
        expenses['clean'] = expenses['label'].apply(clean_label)
        grouped = expenses.groupby('clean').agg({'amount': 'mean', 'date': 'count'}).reset_index()
        
        # Keywords map
        KEYWORD_MAP = {
            "Logement": ["LOYER", "IMMO", "PROPRIETAIRE", "QUITTANCE", "BAIL", "CAUTION"],
            "Emprunt immobilier": ["PRET", "CREDIT", "ECHEANCE"],
            "Assurances": ["ASSURANCE", "MACIF", "MAIF", "AXA", "ALLIANZ", "MUTUELLE", "PREVOYANCE", "GENERALI", "SWISSLIFE", "MGEN", "MALAKOFF", "ALAN"],
            "Abonnements": ["EDF", "ENGIE", "TOTALENERGIE", "EAU", "SUEZ", "VEOLIA", "ORANGE", "SFR", "BOUYGUES", "FREE", "NETFLIX", "SPOTIFY", "AMAZON PRIME", "ENI", "VATTENFALL", "OHM", "MINT"]
        }
        
        for _, row in grouped.iterrows():
            if not is_new(row['clean']):
                continue
                
            label_upper = row['clean'].upper()
            found_cat = None
            
            # Check keywords
            for cat, keywords in KEYWORD_MAP.items():
                if any(k in label_upper for k in keywords):
                    found_cat = cat
                    break
            
            # Heuristics for Big Amounts (likely Rent/Loan if not matched)
            if not found_cat and row['amount'] < -600:
                found_cat = "Logement"
            
            if found_cat:
                candidates.append({
                    "type": f"Dépense Récurrente ({found_cat})",
                    "label": row['clean'],
                    "amount": row['amount'],
                    "confidence": "Haute",
                    "default_category": found_cat
                })
    
    return candidates
