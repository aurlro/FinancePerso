"""
Settings management for user configuration.
Provides functions to get and set application settings stored in the database.
"""
from modules.db.connection import get_db_connection
from modules.logger import logger
from typing import Optional, List


def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get a setting value from the database.

    Args:
        key: The setting key
        default: Default value if setting doesn't exist

    Returns:
        The setting value or default if not found
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            result = cursor.fetchone()
            return result[0] if result else default
    except Exception as e:
        logger.error(f"Error getting setting '{key}': {e}")
        return default


def set_setting(key: str, value: str, description: Optional[str] = None) -> bool:
    """
    Set a setting value in the database.

    Args:
        key: The setting key
        value: The setting value
        description: Optional description of the setting

    Returns:
        True if successful, False otherwise
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            if description:
                cursor.execute(
                    """
                    INSERT INTO settings (key, value, description, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(key) DO UPDATE SET
                        value = excluded.value,
                        description = excluded.description,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (key, value, description)
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO settings (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(key) DO UPDATE SET
                        value = excluded.value,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (key, value)
                )

            conn.commit()
            logger.info(f"Setting '{key}' updated successfully")
            return True
    except Exception as e:
        logger.error(f"Error setting '{key}': {e}")
        return False


def get_internal_transfer_targets() -> List[str]:
    """
    Get the list of internal transfer target keywords.

    Returns:
        List of keywords used to detect internal transfers
    """
    targets_str = get_setting("internal_transfer_targets", "")
    if not targets_str:
        # Fallback defaults if setting doesn't exist
        return ["AURELIEN", "DUO", "JOINT", "EPARGNE", "LDDS", "LIVRET", "ELISE"]

    # Split by comma and clean up whitespace
    return [t.strip().upper() for t in targets_str.split(",") if t.strip()]


def set_internal_transfer_targets(targets: List[str]) -> bool:
    """
    Set the list of internal transfer target keywords.

    Args:
        targets: List of keywords (will be converted to uppercase)

    Returns:
        True if successful, False otherwise
    """
    # Clean and uppercase the targets
    cleaned_targets = [t.strip().upper() for t in targets if t.strip()]

    # Join with commas
    targets_str = ",".join(cleaned_targets)

    return set_setting(
        "internal_transfer_targets",
        targets_str,
        "Mots-clés pour détecter les virements internes (séparés par des virgules)"
    )


def get_internal_transfer_keywords() -> List[str]:
    """Get the keywords that identify a transaction as a transfer (e.g. VIR, VRT)."""
    val = get_setting("internal_transfer_keywords", "VIR,VIREMENT,VRT,PIVOT,MOUVEMENT,TRANSFERT")
    return [t.strip().upper() for t in val.split(",") if t.strip()]


def set_internal_transfer_keywords(keywords: List[str]) -> bool:
    """Set the keywords that identify a transaction as a transfer."""
    val = ",".join([t.strip().upper() for t in keywords if t.strip()])
    return set_setting("internal_transfer_keywords", val, "Mots-clés d'identification des virements (VIR, VRT, etc.)")


def get_verified_transfer_labels() -> List[str]:
    """Get the list of verified labels that are known to be correct as internal transfers."""
    val = get_setting("internal_transfer_verified_labels", "")
    return [t.strip() for t in val.split("|") if t.strip()] # Use | as separator to allow commas in labels


def add_verified_transfer_label(label: str) -> bool:
    """Add a label to the whitelist of verified internal transfers."""
    current = get_verified_transfer_labels()
    if label in current:
        return True
    current.append(label)
    val = "|".join(current)
    return set_setting("internal_transfer_verified_labels", val, "Liste blanche des libellés de virement vérifiés")


def get_all_settings() -> dict:
    """
    Get all settings from the database.

    Returns:
        Dictionary mapping keys to (value, description) tuples
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value, description FROM settings")
            results = cursor.fetchall()
            return {row[0]: {"value": row[1], "description": row[2]} for row in results}
    except Exception as e:
        logger.error(f"Error getting all settings: {e}")
        return {}
