"""
Privacy Module - RGPD et Conformité
====================================

Ce module gère la conformité RGPD et la protection des données.

Usage:
    from modules.privacy import GDPRManager

    gdpr = GDPRManager()
    gdpr.purge_user_data(user_id)
"""

from modules.privacy.gdpr_manager import (
    GDPRManager,
    DataRetentionPolicy,
    DeletionRecord,
    ConsentRecord,
    quick_export,
    quick_purge,
)

__all__ = [
    "GDPRManager",
    "DataRetentionPolicy",
    "DeletionRecord",
    "ConsentRecord",
    "quick_export",
    "quick_purge",
]
