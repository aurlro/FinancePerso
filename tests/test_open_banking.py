"""Tests du module Open Banking."""

from datetime import datetime

from modules.open_banking.client import ConnectionManager, OpenBankingClient
from modules.open_banking.providers import MockProvider
from modules.open_banking.sync import BankSyncManager


class TestMockProvider:
    """Tests du provider mock."""
    
    def test_get_banks(self):
        """Test la récupération des banques mock."""
        provider = MockProvider()
        banks = provider.get_banks("FR")
        
        assert len(banks) == 2
        assert all("id" in b and "name" in b for b in banks)
    
    def test_create_connection(self):
        """Test la création d'une connexion mock."""
        provider = MockProvider()
        
        result = provider.create_connection("mock_bank_1", "http://localhost/callback")
        
        assert "connection_id" in result
        assert "auth_url" in result
        assert "mock_conn_" in result["connection_id"]
    
    def test_get_connection_status(self):
        """Test la vérification du statut."""
        provider = MockProvider()
        
        result = provider.create_connection("mock_bank_1", "http://localhost/callback")
        status = provider.get_connection_status(result["connection_id"])
        
        assert status == "connected"
    
    def test_list_accounts(self):
        """Test le listage des comptes."""
        provider = MockProvider()
        
        result = provider.create_connection("mock_bank_1", "http://localhost/callback")
        accounts = provider.list_accounts(result["connection_id"])
        
        assert len(accounts) == 2
        assert all("id" in acc and "balance" in acc for acc in accounts)
    
    def test_get_transactions(self):
        """Test la récupération des transactions."""
        provider = MockProvider()
        
        result = provider.create_connection("mock_bank_1", "http://localhost/callback")
        accounts = provider.list_accounts(result["connection_id"])
        
        transactions = provider.get_transactions(accounts[0]["id"])
        
        assert len(transactions) == 10
        assert all("amount" in t and "date" in t for t in transactions)


class TestOpenBankingClient:
    """Tests du client Open Banking."""
    
    def test_mock_client(self):
        """Test le client avec le provider mock."""
        client = OpenBankingClient("mock")
        
        banks = client.get_available_banks("FR")
        assert len(banks) == 2
        
        result = client.create_connection("mock_bank_1", "http://localhost/callback")
        assert "connection_id" in result


class TestConnectionManager:
    """Tests du gestionnaire de connexions."""
    
    def test_save_and_get_connections(self, temp_db):
        """Test la sauvegarde et récupération des connexions."""
        from modules.open_banking.client import BankConnection, ConnectionStatus
        
        manager = ConnectionManager()
        
        conn = BankConnection(
            id="test-123",
            bank_id="bank-1",
            bank_name="Test Bank",
            status=ConnectionStatus.CONNECTED,
            created_at=datetime.now(),
            account_ids=["acc1", "acc2"]
        )
        
        manager.save_connection(conn, "mock")
        
        active = manager.get_active_connections()
        assert len(active) == 1
        assert active[0].bank_name == "Test Bank"


class TestBankSyncManager:
    """Tests du gestionnaire de synchronisation."""
    
    def test_sync_history(self, temp_db):
        """Test la récupération de l'historique de sync."""
        manager = BankSyncManager()
        
        history = manager.get_sync_history(limit=10)
        assert isinstance(history, list)
    
    def test_is_duplicate(self, temp_db):
        """Test la détection des doublons."""
        manager = BankSyncManager()
        
        # Initialement pas de doublon
        assert manager._is_duplicate("ext-123", "acc-1") is False
        
        # Après import, devrait être un doublon
        # (Note: Normalement _import_transaction l'ajoute, on teste directement)
        from modules.db.connection import get_db_connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO bank_transaction_ids (external_id, account_id) VALUES (?, ?)",
                ("ext-123", "acc-1")
            )
            conn.commit()
        
        assert manager._is_duplicate("ext-123", "acc-1") is True
        assert manager._is_duplicate("ext-456", "acc-1") is False
