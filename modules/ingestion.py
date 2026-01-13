import pandas as pd
import io
import re

def parse_bourso_csv(file):
    """
    Legacy parser for BoursoBank specific format.
    """
    # ... (code logic matches original but wrapped to reuse if needed, 
    # but efficient to just treat it as a specific config if possible? 
    # For now let's keep it but maybe we can make it a specific call or mapped internally)
    # Actually, let's keep the existing logic for Bourso as a "Preset" and just add the generic one.
    try:
        df = pd.read_csv(file, sep=';', encoding='utf-8', decimal=',', thousands=' ')
        
        rename_map = {
            'dateOp': 'date',
            'label': 'label',
            'amount': 'amount',
            'category': 'original_category',
            'accountNum': 'account_id',
            'accountLabel': 'account_label'
        }
        
        # Check if columns exist before renaming to be safe
        available_cols = set(df.columns)
        actual_rename = {k: v for k, v in rename_map.items() if k in available_cols}
        
        df_clean = df.rename(columns=actual_rename)
        
        if df_clean['amount'].dtype == 'object':
             df_clean['amount'] = df_clean['amount'].str.replace(' ', '').str.replace(',', '.').astype(float)

        df_clean['date'] = pd.to_datetime(df_clean['date'], format='%Y-%m-%d').dt.date

        # MEMBER EXTRACTION (Hardcoded specific for user context, maybe keep this as a "Post-process" for everyone?)
        # Let's keep it here for this preset
        CARD_MAP = {
            '6759': 'Aurélien',
            '7238': 'Élise',
            '3857': 'Aurélien'
        }
        
        def extract_member(label):
            match = re.search(r'CB\*(\d{4})', str(label), re.IGNORECASE)
            if match:
                card_end = match.group(1)
                return CARD_MAP.get(card_end, f"Carte {card_end}")
            return "Inconnu"

        df_clean['member'] = df_clean['label'].apply(extract_member)
        df_clean['status'] = 'pending'
        df_clean['category_validated'] = 'Inconnu'
        
        if 'account_label' not in df_clean.columns:
             df_clean['account_label'] = 'Compte Principal'
        
        # Ensure minimal columns are present
        for col in ['account_id', 'original_category']:
            if col not in df_clean.columns:
                df_clean[col] = None

        final_cols = ['date', 'label', 'amount', 'original_category', 'account_id', 'status', 'category_validated', 'account_label', 'member']
        return df_clean[final_cols]
        
    except Exception as e:
        return None, f"Erreur Bourso: {str(e)}"

def parse_generic_csv(file, config):
    """
    Parse a CSV based on dynamic config.
    config = {
        'sep': ';',
        'decimal': ',',
        'skiprows': 0,
        'mapping': {'date': 'ColA', 'amount': 'ColB', 'label': 'ColC'}
    }
    """
    try:
        # Load
        df = pd.read_csv(
            file, 
            sep=config.get('sep', ';'), 
            decimal=config.get('decimal', ','), 
            skiprows=config.get('skiprows', 0),
            encoding='utf-8', # Consider adding encoding option if needed
            thousands=config.get('thousands', None)
        )
        
        # Map columns
        mapping = config.get('mapping', {})
        # Inverse mapping: User says "Date is ColA", so { 'date': 'ColA' }
        # We want to rename ColA to date.
        rename_map = {v: k for k, v in mapping.items() if v} # v is the csv column name, k is our internal name
        
        df_clean = df.rename(columns=rename_map)
        
        # Required checks
        for req in ['date', 'label', 'amount']:
            if req not in df_clean.columns:
                 return None, f"Colonne manquante après mapping : {req}"
        
        # Conversions
        # Date: Try to detect format or standard parser
        df_clean['date'] = pd.to_datetime(df_clean['date'], dayfirst=True, errors='coerce').dt.date
        df_clean = df_clean.dropna(subset=['date']) # Drop invalid dates
        
        # Amount: Clean symbols if still object
        if df_clean['amount'].dtype == 'object':
             df_clean['amount'] = df_clean['amount'].astype(str).str.replace(' ', '').str.replace('€', '').str.replace(',', '.')
             df_clean['amount'] = pd.to_numeric(df_clean['amount'], errors='coerce')
             
        if 'member' not in df_clean.columns:
            # Member extraction (Generic regex for CB*XXXX is useful generally)
            def extract_member_generic(label):
                match = re.search(r'CB\*(\d{4})', str(label), re.IGNORECASE)
                if match:
                    return f"Carte {match.group(1)}"
                return "" # Empty string better than Inconnu for generic?
                
            df_clean['member'] = df_clean['label'].apply(extract_member_generic)
        else:
             # Clean up if mapped
             df_clean['member'] = df_clean['member'].fillna("")
        
        # Fill missing
        df_clean['status'] = 'pending'
        df_clean['category_validated'] = 'Inconnu'
        df_clean['account_label'] = 'Import Manuel'
        df_clean['original_category'] = None
        df_clean['account_id'] = None
        
        final_cols = ['date', 'label', 'amount', 'original_category', 'account_id', 'status', 'category_validated', 'account_label', 'member']
        # Add missing columns with None
        for col in final_cols:
            if col not in df_clean.columns:
                df_clean[col] = None
                
        return df_clean[final_cols]
        
    except Exception as e:
        return None, f"Erreur Générique: {str(e)}"

def load_transaction_file(uploaded_file, mode="auto", config=None):
    if uploaded_file is None:
        return None
        
    # Reset file pointer if it was read for preview
    uploaded_file.seek(0)
    
    if mode == "bourso_preset":
        return parse_bourso_csv(uploaded_file)
    elif mode == "custom" and config:
        return parse_generic_csv(uploaded_file, config)
    else:
        # Default/Auto: Try Bourso
        return parse_bourso_csv(uploaded_file)
