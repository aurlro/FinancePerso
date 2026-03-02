"""
Bank import templates for French banks.
Maps CSV formats to standardized transaction format.
"""

from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd

from modules.logger import logger


@dataclass
class BankTemplate:
    """Template for a specific bank's CSV format."""

    name: str  # Display name
    delimiter: str  # CSV delimiter (; or ,)
    encoding: str  # File encoding (utf-8, latin1, etc.)
    date_col: str  # Column name for date
    date_format: str  # Date format string (%d/%m/%Y, etc.)
    label_col: str  # Column name for transaction label
    amount_col: str  # Column name for amount
    amount_decimal: str  # Decimal separator (, or .)
    skip_rows: int  # Rows to skip at beginning
    card_suffix_col: str | None = None  # Optional: card suffix column
    account_label_col: str | None = None  # Optional: account label column

    # Optional transforms
    amount_transform: Callable | None = None  # Function to transform amount
    label_transform: Callable | None = None  # Function to clean label


# Templates for major French banks
BANK_TEMPLATES = {
    "boursorama": BankTemplate(
        name="Boursorama Banque",
        delimiter=";",
        encoding="latin1",
        date_col="date",
        date_format="%d/%m/%Y",
        label_col="libelle",
        amount_col="montant",
        amount_decimal=",",
        skip_rows=1,
        card_suffix_col="carte",
    ),
    "ing_direct": BankTemplate(
        name="ING Direct",
        delimiter=",",
        encoding="utf-8",
        date_col="Date",
        date_format="%Y-%m-%d",
        label_col="Libellé",
        amount_col="Montant",
        amount_decimal=".",
        skip_rows=0,
    ),
    "credit_mutuel": BankTemplate(
        name="Crédit Mutuel",
        delimiter=";",
        encoding="latin1",
        date_col="Date de comptabilisation",
        date_format="%d/%m/%Y",
        label_col="Libellé",
        amount_col="Montant",
        amount_decimal=",",
        skip_rows=0,
    ),
    "societe_generale": BankTemplate(
        name="Société Générale",
        delimiter=";",
        encoding="latin1",
        date_col="Date",
        date_format="%d/%m/%Y",
        label_col="Libellé",
        amount_col="Montant",
        amount_decimal=",",
        skip_rows=0,
    ),
    "caisse_epargne": BankTemplate(
        name="Caisse d'Épargne",
        delimiter=";",
        encoding="latin1",
        date_col="Date opération",
        date_format="%d/%m/%Y",
        label_col="Libellé",
        amount_col="Montant (EUR)",
        amount_decimal=",",
        skip_rows=0,
    ),
    "banque_populaire": BankTemplate(
        name="Banque Populaire",
        delimiter=";",
        encoding="latin1",
        date_col="dateOp",
        date_format="%d/%m/%Y",
        label_col="label",
        amount_col="amount",
        amount_decimal=",",
        skip_rows=0,
    ),
}


def detect_bank_format(file_path: str) -> str | None:
    """
    Detect bank format from CSV file.

    Analyzes the first few rows and headers to identify the bank.

    Args:
        file_path: Path to CSV file

    Returns:
        Bank template key or None if unknown
    """
    try:
        # Try reading with different encodings and delimiters
        encodings = ["utf-8", "latin1", "cp1252"]
        delimiters = [";", ",", "\t"]

        for encoding in encodings:
            for delimiter in delimiters:
                try:
                    # Read first few rows with specific delimiter
                    df = pd.read_csv(file_path, nrows=3, encoding=encoding, delimiter=delimiter)
                    columns = set(df.columns.str.lower())

                    # Check each template
                    for bank_key, template in BANK_TEMPLATES.items():
                        template_cols = {
                            template.date_col.lower(),
                            template.label_col.lower(),
                            template.amount_col.lower(),
                        }

                        # If we find the key columns, it's likely this bank
                        if template_cols.issubset(columns):
                            return bank_key

                except (UnicodeDecodeError, pd.errors.EmptyDataError):
                    continue
                except pd.errors.ParserError:
                    continue

    except Exception as e:
        logger.warning(f"Could not detect bank format: {e}")

    return None


def apply_template(df: pd.DataFrame, template: BankTemplate) -> pd.DataFrame:
    """
    Apply bank template to standardize CSV format.

    Args:
        df: Raw DataFrame from CSV
        template: BankTemplate to apply

    Returns:
        Standardized DataFrame with columns: date, label, amount, card_suffix
    """
    result = pd.DataFrame()

    # Map columns
    result["date"] = pd.to_datetime(df[template.date_col], format=template.date_format)
    result["label"] = df[template.label_col]

    # Handle amount (convert to float with proper decimal)
    amount_str = df[template.amount_col].astype(str)
    if template.amount_decimal == ",":
        amount_str = amount_str.str.replace(",", ".", regex=False)
    result["amount"] = pd.to_numeric(amount_str, errors="coerce")

    # Optional columns
    if template.card_suffix_col and template.card_suffix_col in df.columns:
        result["card_suffix"] = df[template.card_suffix_col]
    else:
        result["card_suffix"] = None

    if template.account_label_col and template.account_label_col in df.columns:
        result["account_label"] = df[template.account_label_col]
    else:
        result["account_label"] = None

    # Apply transforms if defined
    if template.label_transform:
        result["label"] = result["label"].apply(template.label_transform)

    return result


def load_bank_csv(file_path: str, bank_key: str | None = None) -> pd.DataFrame:
    """
    Load CSV file using appropriate bank template.

    Args:
        file_path: Path to CSV file
        bank_key: Optional bank template key (auto-detected if not provided)

    Returns:
        Standardized DataFrame
    """
    # Auto-detect if not specified
    if bank_key is None:
        bank_key = detect_bank_format(file_path)
        if bank_key:
            logger.info(f"Detected bank format: {BANK_TEMPLATES[bank_key].name}")

    if bank_key and bank_key in BANK_TEMPLATES:
        template = BANK_TEMPLATES[bank_key]

        # Load with correct encoding and delimiter
        df = pd.read_csv(
            file_path,
            delimiter=template.delimiter,
            encoding=template.encoding,
            skiprows=template.skip_rows,
        )

        # Apply template
        return apply_template(df, template)

    # Fallback: try generic CSV
    logger.warning("Unknown bank format, trying generic CSV")
    return pd.read_csv(file_path)


__all__ = [
    "BankTemplate",
    "BANK_TEMPLATES",
    "detect_bank_format",
    "apply_template",
    "load_bank_csv",
]
