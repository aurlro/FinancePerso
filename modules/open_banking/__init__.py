"""Module Open Banking - Phase 8.

Import automatique via API bancaires (GoCardless/Bridge/Nordigen).
"""

from .client import BankConnection, OpenBankingClient
from .providers import BridgeProvider, GoCardlessProvider, MockProvider
from .sync import BankSyncManager, SyncResult

__all__ = [
    'OpenBankingClient',
    'BankConnection', 
    'GoCardlessProvider',
    'BridgeProvider',
    'MockProvider',
    'BankSyncManager',
    'SyncResult',
]
