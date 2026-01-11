import pandas as pd
import io

def parse_bourso_csv(file):
    """
    Parse a BoursoBank CSV file.
    Expected format: Semicolon delimiter, French number formatting.
    """
    try:
        # Read CSV with correct encoding and delimiter
        # 'latin-1' is common for French banks, or 'utf-8' with BOM. Try pd.read_csv default or specify.
        df = pd.read_csv(file, sep=';', encoding='utf-8', decimal=',', thousands=' ')
        
        # Identify critical columns
        # Based on analysis: dateOp, label, amount, category
        
        # Rename for internal consistency
        import re
        
        # Rename for internal consistency
        rename_map = {
            'dateOp': 'date',
            'label': 'label',
            'amount': 'amount',
            'category': 'original_category',
            'accountNum': 'account_id',
            'accountLabel': 'account_label'
        }
        
        df_clean = df.rename(columns=rename_map)
        
        # Clean amount if pandus didn't catch the thousands separator correctly (read_csv usually handles it with thousands=' ')
        if df_clean['amount'].dtype == 'object':
             df_clean['amount'] = df_clean['amount'].str.replace(' ', '').str.replace(',', '.').astype(float)

        # Convert date
        df_clean['date'] = pd.to_datetime(df_clean['date'], format='%Y-%m-%d').dt.date

        # MEMBER EXTRACTION
        # Mapping rules based on analysis
        CARD_MAP = {
            '6759': 'Aurélien',  # Compte Perso
            '7238': 'Élise',     # Compte Joint
            '3857': 'Aurélien'   # Compte Joint
        }
        
        def extract_member(label):
            # Find CB*XXXX
            match = re.search(r'CB\*(\d{4})', str(label), re.IGNORECASE)
            if match:
                card_end = match.group(1)
                return CARD_MAP.get(card_end, f"Carte {card_end}")
            return "Inconnu"

        df_clean['member'] = df_clean['label'].apply(extract_member)

        # Add metadata columns
        df_clean['status'] = 'pending'
        df_clean['category_validated'] = 'Inconnu' # To be filled by AI or User
        
        # Ensure account_label exists (if CSV didn't have it, fill default)
        if 'account_label' not in df_clean.columns:
             df_clean['account_label'] = 'Compte Principal'
        
        # Select only relevant columns
        final_cols = ['date', 'label', 'amount', 'original_category', 'account_id', 'status', 'category_validated', 'account_label', 'member']
        return df_clean[final_cols]
        
    except Exception as e:
        return None, str(e)

def load_transaction_file(uploaded_file):
    if uploaded_file is not None:
        return parse_bourso_csv(uploaded_file)
    return None
