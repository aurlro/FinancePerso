import pandas as pd
import hashlib
import re
from typing import Optional, Dict, Tuple, Union
from modules.logger import logger


def generate_tx_hash(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a unique hash for each transaction.
    To handle identical transactions on same day, we add an occurrence index.
    This index is GLOBAL (checks DB) to avoid duplicates across different imports.

    Args:
        df: DataFrame containing transaction data

    Returns:
        DataFrame with added 'tx_hash' column
    """
    if df.empty:
        return df
        
    # from modules.data_manager import get_transaction_count (Removed for count-based logic)
    
    # Sort to ensure stable local index
    df = df.sort_values(by=['date', 'label', 'amount'])
    
    # 1. Calculate local occurrence index (within the file)
    df['_local_occ'] = df.groupby(['date', 'label', 'amount']).cumcount()
    
    def calculate_hash(row):
        # Hash is now purely based on content + local index.
        # Deduplication against DB happens in data_manager.save_transactions by checking counts.
        norm_label = str(row['label']).strip().upper()
        
        # Include account_label in hash to avoid detecting same transaction on different accounts as duplicate
        account = str(row.get('account_label', '')).strip().upper()
        
        # New hash = SHA(date|label|amount|account|local_occ)
        # This hash represents "The Nth occurrence of this transaction in THIS file for THIS account".
        base = f"{row['date']}|{norm_label}|{row['amount']}|{account}|{row['_local_occ']}"
        return hashlib.sha256(base.encode()).hexdigest()[:16]
        
    df['tx_hash'] = df.apply(calculate_hash, axis=1)
    return df.drop(columns=['_local_occ'])

def parse_bourso_csv(file) -> Optional[pd.DataFrame]:
    """
    Legacy parser for BoursoBank specific format.

    Args:
        file: Uploaded file object from Streamlit

    Returns:
        DataFrame with parsed transactions, or None if parsing fails
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

        def extract_card_suffix(label):
            match = re.search(r'CB\*(\d{4})', str(label), re.IGNORECASE)
            if match:
                return match.group(1)
            return None

        df_clean['card_suffix'] = df_clean['label'].apply(extract_card_suffix)
        df_clean['member'] = df_clean['card_suffix'].apply(lambda x: f"Carte {x}" if x else "Inconnu")
        df_clean['status'] = 'pending'
        df_clean['category_validated'] = 'Inconnu'
        
        if 'account_label' not in df_clean.columns:
             df_clean['account_label'] = 'Compte Principal'
        
        # Ensure minimal columns are present
        for col in ['account_id', 'original_category']:
            if col not in df_clean.columns:
                df_clean[col] = None

        final_cols = ['date', 'label', 'amount', 'original_category', 'account_id', 'status', 'category_validated', 'account_label', 'member', 'card_suffix']
        return generate_tx_hash(df_clean[final_cols])
        
    except Exception as e:
        return None, f"Erreur Bourso: {str(e)}"

def parse_generic_csv(file, config: Dict[str, Union[str, int, Dict]]) -> Optional[pd.DataFrame]:
    """
    Parse a CSV based on dynamic config.

    Args:
        file: Uploaded file object from Streamlit
        config: Configuration dictionary with keys:
            - sep: Column separator (default: ';')
            - decimal: Decimal separator (default: ',')
            - skiprows: Number of rows to skip (default: 0)
            - thousands: Thousands separator (default: None)
            - mapping: Dict mapping internal names to CSV column names
                      {'date': 'ColA', 'amount': 'ColB', 'label': 'ColC'}

    Returns:
        DataFrame with parsed transactions, or None if parsing fails

    Example:
        config = {
            'sep': ';',
            'decimal': ',',
            'skiprows': 0,
            'mapping': {'date': 'Date', 'amount': 'Montant', 'label': 'Libellé'}
        }
        df = parse_generic_csv(file, config)
    """
    try:
        # Load
        df = pd.read_csv(
            file, 
            sep=config.get('sep', ';'), 
            decimal=config.get('decimal', ','), 
            skiprows=config.get('skiprows', 0),
            encoding='utf-8-sig', # Handle BOM from Excel/Bourso
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
        
        # Log dropped rows
        invalid_dates = df_clean[df_clean['date'].isna()]
        if not invalid_dates.empty:
            dropped_count = len(invalid_dates)
            logger.warning(f"[Ingestion] Dropped {dropped_count} rows with invalid dates. Sample: {invalid_dates.head(3).to_dict()}")
            
        df_clean = df_clean.dropna(subset=['date']) # Drop invalid dates
        
        # Amount: Clean symbols if still object
        if df_clean['amount'].dtype == 'object':
             df_clean['amount'] = df_clean['amount'].astype(str).str.replace(' ', '').str.replace('€', '').str.replace(',', '.')
             df_clean['amount'] = pd.to_numeric(df_clean['amount'], errors='coerce')
             
        if 'member' not in df_clean.columns:
            # Member extraction (Generic regex for CB*XXXX is useful generally)
            def extract_card_suffix_generic(label):
                match = re.search(r'CB\*(\d{4})', str(label), re.IGNORECASE)
                if match:
                    return match.group(1)
                return None
                
            df_clean['card_suffix'] = df_clean['label'].apply(extract_card_suffix_generic)
            df_clean['member'] = df_clean['card_suffix'].apply(lambda x: f"Carte {x}" if x else "")
        else:
             # If member was mapped from CSV, we don't have suffix usually
             df_clean['card_suffix'] = None
             df_clean['member'] = df_clean['member'].fillna("")
        
        # Fill missing
        df_clean['status'] = 'pending'
        df_clean['category_validated'] = 'Inconnu'
        df_clean['account_label'] = 'Import Manuel'
        df_clean['original_category'] = None
        df_clean['account_id'] = None
        
        final_cols = ['date', 'label', 'amount', 'original_category', 'account_id', 'status', 'category_validated', 'account_label', 'member', 'card_suffix']
        # Add missing columns with None
        for col in final_cols:
            if col not in df_clean.columns:
                df_clean[col] = None
                
        return generate_tx_hash(df_clean[final_cols])
        
    except Exception as e:
        return None, f"Erreur Générique: {str(e)}"

def load_transaction_file(uploaded_file, mode: str = "auto",
                         config: Optional[Dict[str, Union[str, int, Dict]]] = None) -> Optional[pd.DataFrame]:
    """
    Load and parse a transaction file based on specified mode.

    Args:
        uploaded_file: Uploaded file object from Streamlit
        mode: Parsing mode - "auto", "bourso_preset", or "custom"
        config: Configuration dict for custom mode (see parse_generic_csv)

    Returns:
        DataFrame with parsed transactions, or None if file is None or parsing fails

    Example:
        df = load_transaction_file(uploaded_file, mode="bourso_preset")
    """
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
