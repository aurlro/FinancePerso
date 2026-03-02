"""
Module Analytics pour FinancePerso v5.5
Suivi des métriques utilisateurs en interne (SQLite)
"""

from .events import AnalyticsTracker, track_event, get_analytics_summary, init_analytics, EventType
from .metrics import MetricsCollector

# Lazy import pour éviter l'import circulaire avec modules/analytics.py
# (fichier d'analytics financière séparé du package de tracking utilisateur)
_imported_financial_analytics = None


def _get_financial_analytics():
    """Import différé des fonctions d'analytics financière."""
    global _imported_financial_analytics
    if _imported_financial_analytics is None:
        import sys
        import importlib.util
        from pathlib import Path

        # Charger modules/analytics.py manuellement pour éviter le conflit de noms
        analytics_file = Path(__file__).parent.parent / "analytics.py"
        spec = importlib.util.spec_from_file_location("_financial_analytics", analytics_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules["_financial_analytics"] = module
        spec.loader.exec_module(module)
        _imported_financial_analytics = module
    return _imported_financial_analytics


def detect_recurring_payments(df):
    """Détecte les paiements récurrents dans les transactions."""
    mod = _get_financial_analytics()
    return mod.detect_recurring_payments(df)


def detect_financial_profile(df):
    """Détecte le profil financier (salaire, loyer, etc.)."""
    mod = _get_financial_analytics()
    return mod.detect_financial_profile(df)


def exclude_internal_transfers(df, patterns=None):
    """Exclut les virements internes d'un DataFrame de transactions."""
    mod = _get_financial_analytics()
    return mod.exclude_internal_transfers(df, patterns)


__all__ = [
    "AnalyticsTracker",
    "track_event",
    "get_analytics_summary",
    "init_analytics",
    "EventType",
    "MetricsCollector",
    "detect_recurring_payments",
    "detect_financial_profile",
    "exclude_internal_transfers",
]
