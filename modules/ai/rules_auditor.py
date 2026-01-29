"""
AI Rules Auditor.

Analyzes learning rules to detect inconsistencies, conflicts, and potential improvements.
"""
import pandas as pd
from modules.logger import logger

def analyze_rules_integrity(rules_df: pd.DataFrame) -> dict:
    """
    Analyze rules for potential issues.
    
    Args:
        rules_df: DataFrame containing the rules (pattern, category, priority)
        
    Returns:
        Dict containing lists of issues:
        - conflicts: Same pattern, different categories
        - overlaps: Pattern contained in another pattern with different category
        - vague: Patterns too short or generic
        - duplicates: Exact duplicates (redundant)
    """
    if rules_df.empty:
        return {"conflicts": [], "overlaps": [], "vague": [], "duplicates": []}
    
    issues = {
        "conflicts": [],
        "overlaps": [],
        "vague": [],
        "duplicates": [],
        "stale": [],
        "score": 100
    }
    
    from datetime import datetime, timedelta
    now = datetime.now()
    six_months_ago = now - timedelta(days=180)
    
    # Check for conflicts (Same pattern, different category)
    # Actually, the DB constraint usually prevents this, but let's check logical conflicts
    # if we consider case insensitivity
    
    rules_df['pattern_lower'] = rules_df['pattern'].str.lower().str.strip()
    
    # 1. Case-insensitive duplicates with conflict
    duplicates = rules_df[rules_df.duplicated('pattern_lower', keep=False)].sort_values('pattern_lower')
    
    if not duplicates.empty:
        grouped = duplicates.groupby('pattern_lower')
        for pattern, group in grouped:
            categories = group['category'].unique()
            if len(categories) > 1:
                issues['conflicts'].append({
                    "pattern": pattern,
                    "categories": list(categories),
                    "ids": group['id'].tolist(),
                    "message": f"Le pattern '{pattern}' est défini pour plusieurs catégories différentes : {', '.join(categories)}"
                })
            else:
                issues['duplicates'].append({
                    "pattern": pattern,
                    "category": categories[0],
                    "ids": group['id'].tolist(),
                    "message": f"Le pattern '{pattern}' est défini plusieurs fois pour la même catégorie."
                })

    # 2. Overlaps (One pattern is a substring of another, but nice to check if categories differ)
    # This is O(N^2), so we should be careful if N is huge. For rules list (usually < 1000), it's fine.
    # Sorted by length to optimization
    sorted_rules = rules_df.sort_values(by="pattern_lower", key=lambda x: x.str.len())
    rules_list = sorted_rules.to_dict('records')
    
    for i, shorter in enumerate(rules_list):
        for longer in rules_list[i+1:]:
            # Optimization: if longer doesn't start with shorter's first char, native str search might be fast enough
            if shorter['pattern_lower'] in longer['pattern_lower']:
                # Conflict if categories are different and priority doesn't handle it
                # If shorter has higher or equal priority, it might shadow the longer one depending on implementation
                if shorter['category'] != longer['category']:
                     issues['overlaps'].append({
                        "shorter_pattern": shorter['pattern'],
                        "longer_pattern": longer['pattern'],
                        "shorter_category": shorter['category'],
                        "longer_category": longer['category'],
                        "message": f"Conflit potentiel : '{shorter['pattern']}' ({shorter['category']}) est inclus dans '{longer['pattern']}' ({longer['category']})."
                    })

    # 3. Vague patterns
    for _, rule in rules_df.iterrows():
        pat = rule['pattern']
        # Vague
        if len(pat) < 3 and pat.isalpha():
            issues['vague'].append({
                "pattern": pat,
                "category": rule['category'],
                "id": rule['id'],
                "message": f"Le pattern '{pat}' est très court et risque de capturer trop de transactions."
            })
            
        # 4. Stale (Older than 6 months)
        try:
            created_at = pd.to_datetime(rule['created_at'])
            if created_at < six_months_ago:
                issues['stale'].append({
                    "pattern": pat,
                    "category": rule['category'],
                    "id": rule['id'],
                    "created_at": rule['created_at'],
                    "message": f"La règle '{pat}' a été créée il y a plus de 6 mois ({rule['created_at']}). Est-elle toujours d'actualité ?"
                })
        except:
            pass
            
    # --- CALCULATE HEALTH SCORE ---
    # Penalty-based calculation
    score = 100
    score -= len(issues['conflicts']) * 15
    score -= len(issues['duplicates']) * 5
    score -= len(issues['overlaps']) * 8
    score -= len(issues['vague']) * 10
    score -= len(issues['stale']) * 2
    
    issues['score'] = max(0, score)
    
    return issues
