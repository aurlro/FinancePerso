"""
Utility functions shared across modules.
Centralizes common operations to avoid code duplication.
"""
import re

def clean_label(label):
    """
    Remove common bank noise to help AI focus on merchant name.
    Ex: 'VIR Virement de Aurelien...' -> 'Virement Aurelien'
    """
    # Remove dates (dd/mm/yy or dd/mm)
    label = re.sub(r'\d{2}/\d{2}(/\d{2,4})?', '', label)
    
    # Remove technical bank prefixes but KEEP "Virement", "Cotisation" if they are part of the name
    # We remove "CARTE", "CB", "PRLV" (Prélèvement can be noisy but let's see), "SEPA", "VIR" (often redundant with Virement)
    label = re.sub(r'(?i)\b(CARTE|CB|PRLV|SEPA|VIR)\b\*?\d*', '', label)
    
    # Remove numbers with * that are often card references
    label = re.sub(r'\b\d{4,}\b', '', label) # Long numbers
    
    # Remove leading/trailing non-alphanumeric
    label = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', label)
    
    # Remove multiple spaces
    label = re.sub(r'\s+', ' ', label)
    
    # Title Case
    return label.strip().title()

def extract_card_member(label, card_map=None):
    """
    Extract member name from card number in label.
    card_map: dict mapping card endings to names, e.g. {'6759': 'Aurélien'}
    """
    if card_map is None:
        card_map = {}
    
    match = re.search(r'CB\*(\d{4})', str(label), re.IGNORECASE)
    if match:
        card_end = match.group(1)
        return card_map.get(card_end, f"Carte {card_end}")
    return ""

def validate_csv_file(uploaded_file, max_size_mb=10):
    """
    Validate uploaded CSV file.
    Returns (is_valid, error_message)
    """
    if uploaded_file is None:
        return False, "Aucun fichier sélectionné"
    
    # Check file size
    uploaded_file.seek(0, 2)  # Seek to end
    size_bytes = uploaded_file.tell()
    uploaded_file.seek(0)  # Reset to beginning
    
    max_size_bytes = max_size_mb * 1024 * 1024
    if size_bytes > max_size_bytes:
        return False, f"Fichier trop volumineux ({size_bytes / 1024 / 1024:.1f} MB > {max_size_mb} MB)"
    
    # Check extension
    filename = getattr(uploaded_file, 'name', '')
    if not filename.lower().endswith(('.csv', '.xlsx', '.xls')):
        return False, f"Format non supporté: {filename}. Utilisez CSV ou Excel."
    
    return True, ""

def format_currency(amount, symbol="€"):
    """Format amount as currency string."""
    if amount >= 0:
        return f"+{amount:,.2f} {symbol}"
    return f"{amount:,.2f} {symbol}"
