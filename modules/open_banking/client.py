"""Client Open Banking.

Gestion des connexions bancaires via API Open Banking.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ConnectionStatus(Enum):
    """Statut d'une connexion bancaire."""
    PENDING = "pending"
    CONNECTED = "connected"
    EXPIRED = "expired"
    ERROR = "error"


@dataclass
class BankConnection:
    """Connexion a une banque."""
    id: str
    bank_id: str
    bank_name: str
    status: ConnectionStatus
    created_at: datetime
    expires_at: datetime | None = None
    last_sync: datetime | None = None
    account_ids: list[str] = None


@dataclass
class BankAccount:
    """Compte bancaire."""
    id: str
    connection_id: str
    name: str
    iban: str
    currency: str
    balance: float
    account_type: str


@dataclass  
class BankTransaction:
    """Transaction bancaire importee."""
    id: str
    account_id: str
    date: datetime
    amount: float
    currency: str
    description: str
    counterparty: str
    transaction_type: str
    status: str


class OpenBankingClient:
    """Client pour les API Open Banking."""
    
    def __init__(self, provider: str = "gocardless"):
        """
        Args:
            provider: 'gocardless', 'bridge', ou 'mock' pour tests
        """
        self.provider = provider
        self._init_provider()
    
    def _init_provider(self):
        """Initialise le provider approprie."""
        if self.provider == "gocardless":
            from .providers import GoCardlessProvider
            self._provider = GoCardlessProvider()
        elif self.provider == "bridge":
            from .providers import BridgeProvider
            self._provider = BridgeProvider()
        elif self.provider == "mock":
            from .providers import MockProvider
            self._provider = MockProvider()
        else:
            raise ValueError("Provider inconnu: " + self.provider)
    
    def get_available_banks(self, country: str = "FR") -> list[dict]:
        """Recupere la liste des banques disponibles."""
        return self._provider.get_banks(country)
    
    def create_connection(
        self,
        bank_id: str,
        redirect_url: str
    ) -> dict:
        """Cree une nouvelle connexion bancaire.
        
        Returns:
            Dict avec 'connection_id' et 'auth_url' pour redirection
        """
        return self._provider.create_connection(bank_id, redirect_url)
    
    def get_connection_status(self, connection_id: str) -> ConnectionStatus:
        """Verifie le statut d'une connexion."""
        return self._provider.get_connection_status(connection_id)
    
    def list_accounts(self, connection_id: str) -> list[BankAccount]:
        """Liste les comptes d'une connexion."""
        return self._provider.list_accounts(connection_id)
    
    def get_transactions(
        self,
        account_id: str,
        date_from: datetime | None = None,
        date_to: datetime | None = None
    ) -> list[BankTransaction]:
        """Recupere les transactions d'un compte."""
        return self._provider.get_transactions(account_id, date_from, date_to)
    
    def disconnect(self, connection_id: str) -> bool:
        """Deconnecte une banque."""
        return self._provider.disconnect(connection_id)


class ConnectionManager:
    """Gestionnaire persistant des connexions."""
    
    def __init__(self):
        self._ensure_table()
    
    def _ensure_table(self):
        """Cree la table des connexions."""
        from modules.db.connection import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bank_connections (
                    id TEXT PRIMARY KEY,
                    bank_id TEXT NOT NULL,
                    bank_name TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    last_sync TIMESTAMP,
                    access_token TEXT,
                    refresh_token TEXT,
                    account_ids TEXT
                )
            """)
            conn.commit()
    
    def save_connection(self, connection: BankConnection, provider: str):
        """Sauvegarde une connexion."""
        from modules.db.connection import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO bank_connections 
                (id, bank_id, bank_name, provider, status, created_at, expires_at, last_sync, account_ids)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    connection.id,
                    connection.bank_id,
                    connection.bank_name,
                    provider,
                    connection.status.value,
                    connection.created_at.isoformat(),
                    connection.expires_at.isoformat() if connection.expires_at else None,
                    connection.last_sync.isoformat() if connection.last_sync else None,
                    ','.join(connection.account_ids) if connection.account_ids else ''
                )
            )
            conn.commit()
    
    def get_active_connections(self) -> list[BankConnection]:
        """Recupere les connexions actives."""
        from modules.db.connection import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, bank_id, bank_name, status, created_at, expires_at, last_sync, account_ids
                FROM bank_connections
                WHERE status IN ('connected', 'pending')
                ORDER BY created_at DESC
                """
            )
            
            connections = []
            for row in cursor.fetchall():
                connections.append(BankConnection(
                    id=row[0],
                    bank_id=row[1],
                    bank_name=row[2],
                    status=ConnectionStatus(row[3]),
                    created_at=datetime.fromisoformat(row[4]),
                    expires_at=datetime.fromisoformat(row[5]) if row[5] else None,
                    last_sync=datetime.fromisoformat(row[6]) if row[6] else None,
                    account_ids=row[7].split(',') if row[7] else []
                ))
            
            return connections
    
    def update_sync_time(self, connection_id: str):
        """Met a jour la date de derniere synchro."""
        from modules.db.connection import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE bank_connections
                SET last_sync = ?
                WHERE id = ?
                """,
                (datetime.now().isoformat(), connection_id)
            )
            conn.commit()
