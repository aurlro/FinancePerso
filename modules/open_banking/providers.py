"""Providers Open Banking.

Implémentations pour GoCardless, Bridge, et mock pour tests.
"""

import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from modules.logger import logger


class BaseBankingProvider(ABC):
    """Classe de base pour les providers bancaires."""
    
    @abstractmethod
    def get_banks(self, country: str = "FR") -> list[dict]:
        """Liste les banques disponibles."""
        pass
    
    @abstractmethod
    def create_connection(self, bank_id: str, redirect_url: str) -> dict:
        """Crée une connexion bancaire."""
        pass
    
    @abstractmethod
    def get_connection_status(self, connection_id: str) -> str:
        """Vérifie le statut d'une connexion."""
        pass
    
    @abstractmethod
    def list_accounts(self, connection_id: str) -> list[dict]:
        """Liste les comptes."""
        pass
    
    @abstractmethod
    def get_transactions(
        self,
        account_id: str,
        date_from: datetime | None = None,
        date_to: datetime | None = None
    ) -> list[dict]:
        """Récupère les transactions."""
        pass
    
    @abstractmethod
    def disconnect(self, connection_id: str) -> bool:
        """Déconnecte une banque."""
        pass


class MockProvider(BaseBankingProvider):
    """Provider mock pour tests."""
    
    MOCK_BANKS = [
        {"id": "mock_bank_1", "name": "Banque Mock 1", "logo": "🏦"},
        {"id": "mock_bank_2", "name": "Banque Mock 2", "logo": "🏛️"},
    ]
    
    def __init__(self):
        self._connections = {}
        self._accounts = {}
        self._transactions = {}
    
    def get_banks(self, country: str = "FR") -> list[dict]:
        return self.MOCK_BANKS
    
    def create_connection(self, bank_id: str, redirect_url: str) -> dict:
        conn_id = f"mock_conn_{len(self._connections)}"
        self._connections[conn_id] = {
            "bank_id": bank_id,
            "status": "connected"
        }
        
        # Créer des comptes mock
        self._accounts[conn_id] = [
            {
                "id": f"mock_acc_{conn_id}_1",
                "name": "Compte Courant",
                "iban": "FRXX XXXX XXXX XXXX",
                "balance": 1500.50,
                "currency": "EUR"
            },
            {
                "id": f"mock_acc_{conn_id}_2",
                "name": "Livret A",
                "iban": "FRXX XXXX XXXX XXXX",
                "balance": 5000.00,
                "currency": "EUR"
            }
        ]
        
        # Créer des transactions mock
        self._transactions[f"mock_acc_{conn_id}_1"] = [
            {
                "id": f"tx_{i}",
                "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "amount": -50.0 - i * 10,
                "description": f"Transaction test {i}",
                "counterparty": f"Commerçant {i}"
            }
            for i in range(10)
        ]
        
        return {
            "connection_id": conn_id,
            "auth_url": redirect_url + f"?connection_id={conn_id}&status=success"
        }
    
    def get_connection_status(self, connection_id: str) -> str:
        conn = self._connections.get(connection_id)
        return conn["status"] if conn else "error"
    
    def list_accounts(self, connection_id: str) -> list[dict]:
        return self._accounts.get(connection_id, [])
    
    def get_transactions(
        self,
        account_id: str,
        date_from: datetime | None = None,
        date_to: datetime | None = None
    ) -> list[dict]:
        return self._transactions.get(account_id, [])
    
    def disconnect(self, connection_id: str) -> bool:
        if connection_id in self._connections:
            del self._connections[connection_id]
            return True
        return False


class GoCardlessProvider(BaseBankingProvider):
    """Provider GoCardless (anciennement Nordigen)."""
    
    API_BASE = "https://bankaccountdata.gocardless.com/api/v2"
    
    def __init__(self):
        self.secret_id = os.getenv("GOCARDLESS_SECRET_ID")
        self.secret_key = os.getenv("GOCARDLESS_SECRET_KEY")
        self._access_token = None
    
    def _get_access_token(self) -> str:
        """Obtient un token d'accès."""
        if self._access_token:
            return self._access_token
        
        import requests
        
        response = requests.post(
            f"{self.API_BASE}/token/new/",
            json={
                "secret_id": self.secret_id,
                "secret_key": self.secret_key
            }
        )
        response.raise_for_status()
        
        data = response.json()
        self._access_token = data["access"]
        return self._access_token
    
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json"
        }
    
    def get_banks(self, country: str = "FR") -> list[dict]:
        """Liste les banques disponibles."""
        try:
            import requests
            
            response = requests.get(
                f"{self.API_BASE}/institutions/",
                headers=self._headers(),
                params={"country": country}
            )
            response.raise_for_status()
            
            banks = response.json()
            return [
                {
                    "id": b["id"],
                    "name": b["name"],
                    "logo": b.get("logo", ""),
                    "bic": b.get("bic", "")
                }
                for b in banks
            ]
        except Exception as e:
            logger.error(f"Erreur récupération banques GoCardless: {e}")
            return []
    
    def create_connection(self, bank_id: str, redirect_url: str) -> dict:
        """Crée une connexion (réquisition)."""
        try:
            import requests
            
            # Créer un agreement
            agreement_response = requests.post(
                f"{self.API_BASE}/agreements/enduser/",
                headers=self._headers(),
                json={
                    "institution_id": bank_id,
                    "max_historical_days": 90,
                    "access_valid_for_days": 90,
                    "access_scope": ["balances", "details", "transactions"]
                }
            )
            agreement_response.raise_for_status()
            agreement_id = agreement_response.json()["id"]
            
            # Créer la réquisition
            requisition_response = requests.post(
                f"{self.API_BASE}/requisitions/",
                headers=self._headers(),
                json={
                    "institution_id": bank_id,
                    "redirect": redirect_url,
                    "agreement": agreement_id
                }
            )
            requisition_response.raise_for_status()
            
            data = requisition_response.json()
            return {
                "connection_id": data["id"],
                "auth_url": data["link"]
            }
        except Exception as e:
            logger.error(f"Erreur création connexion GoCardless: {e}")
            raise
    
    def get_connection_status(self, connection_id: str) -> str:
        """Vérifie le statut."""
        try:
            import requests
            
            response = requests.get(
                f"{self.API_BASE}/requisitions/{connection_id}/",
                headers=self._headers()
            )
            response.raise_for_status()
            
            data = response.json()
            status_map = {
                "CR": "pending",
                "GC": "connected",
                "EX": "expired",
                "RJ": "error"
            }
            return status_map.get(data["status"], "unknown")
        except Exception as e:
            logger.error(f"Erreur statut connexion: {e}")
            return "error"
    
    def list_accounts(self, connection_id: str) -> list[dict]:
        """Liste les comptes."""
        try:
            import requests
            
            # D'abord récupérer la réquisition pour avoir les account_ids
            req_response = requests.get(
                f"{self.API_BASE}/requisitions/{connection_id}/",
                headers=self._headers()
            )
            req_response.raise_for_status()
            account_ids = req_response.json().get("accounts", [])
            
            accounts = []
            for acc_id in account_ids:
                acc_response = requests.get(
                    f"{self.API_BASE}/accounts/{acc_id}/details/",
                    headers=self._headers()
                )
                acc_response.raise_for_status()
                
                details = acc_response.json().get("account", {})
                
                # Récupérer le solde
                balance_response = requests.get(
                    f"{self.API_BASE}/accounts/{acc_id}/balances/",
                    headers=self._headers()
                )
                balance_response.raise_for_status()
                balances = balance_response.json().get("balances", [])
                balance = balances[0]["balanceAmount"]["amount"] if balances else "0"
                
                accounts.append({
                    "id": acc_id,
                    "name": details.get("name", "Compte"),
                    "iban": details.get("iban", ""),
                    "currency": details.get("currency", "EUR"),
                    "balance": float(balance)
                })
            
            return accounts
        except Exception as e:
            logger.error(f"Erreur liste comptes: {e}")
            return []
    
    def get_transactions(
        self,
        account_id: str,
        date_from: datetime | None = None,
        date_to: datetime | None = None
    ) -> list[dict]:
        """Récupère les transactions."""
        try:
            import requests
            
            params = {}
            if date_from:
                params["date_from"] = date_from.strftime("%Y-%m-%d")
            if date_to:
                params["date_to"] = date_to.strftime("%Y-%m-%d")
            
            response = requests.get(
                f"{self.API_BASE}/accounts/{account_id}/transactions/",
                headers=self._headers(),
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            transactions = data.get("transactions", {}).get("booked", [])
            
            return [
                {
                    "id": t.get("transactionId", ""),
                    "date": t.get("bookingDate", ""),
                    "amount": float(t["transactionAmount"]["amount"]),
                    "currency": t["transactionAmount"]["currency"],
                    "description": t.get("remittanceInformationUnstructured", ""),
                    "counterparty": t.get("debtorName") or t.get("creditorName", ""),
                    "status": "booked"
                }
                for t in transactions
            ]
        except Exception as e:
            logger.error(f"Erreur récupération transactions: {e}")
            return []
    
    def disconnect(self, connection_id: str) -> bool:
        """Supprime la réquisition."""
        try:
            import requests
            
            response = requests.delete(
                f"{self.API_BASE}/requisitions/{connection_id}/",
                headers=self._headers()
            )
            return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Erreur déconnexion: {e}")
            return False


class BridgeProvider(BaseBankingProvider):
    """Provider Bridge (https://bridgeapi.io)."""
    
    API_BASE = "https://api.bridgeapi.io/v2"
    
    def __init__(self):
        self.client_id = os.getenv("BRIDGE_CLIENT_ID")
        self.client_secret = os.getenv("BRIDGE_CLIENT_SECRET")
        self._access_token = None
    
    def _get_access_token(self) -> str:
        """Obtient un token JWT."""
        if self._access_token:
            return self._access_token
        
        import requests
        
        response = requests.post(
            f"{self.API_BASE}/authenticate",
            json={
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
        )
        response.raise_for_status()
        
        data = response.json()
        self._access_token = data["access_token"]
        return self._access_token
    
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json"
        }
    
    def get_banks(self, country: str = "FR") -> list[dict]:
        """Liste les banques."""
        try:
            import requests
            
            response = requests.get(
                f"{self.API_BASE}/banks",
                headers=self._headers()
            )
            response.raise_for_status()
            
            banks = response.json().get("resources", [])
            return [
                {
                    "id": str(b["id"]),
                    "name": b["name"],
                    "logo": b.get("logo_url", ""),
                    "country": b.get("country_code", "FR")
                }
                for b in banks if b.get("country_code") == country
            ]
        except Exception as e:
            logger.error(f"Erreur récupération banques Bridge: {e}")
            return []
    
    def create_connection(self, bank_id: str, redirect_url: str) -> dict:
        """Crée une connexion."""
        try:
            import requests
            
            # Créer un utilisateur
            user_response = requests.post(
                f"{self.API_BASE}/users",
                headers=self._headers()
            )
            user_response.raise_for_status()
            user_uuid = user_response.json()["uuid"]
            
            # Créer une connexion
            conn_response = requests.post(
                f"{self.API_BASE}/items",
                headers=self._headers(),
                json={
                    "user_uuid": user_uuid,
                    "bank_id": int(bank_id),
                    "redirect_url": redirect_url
                }
            )
            conn_response.raise_for_status()
            
            data = conn_response.json()
            return {
                "connection_id": data["uuid"],
                "auth_url": data["redirect_url"]
            }
        except Exception as e:
            logger.error(f"Erreur création connexion Bridge: {e}")
            raise
    
    def get_connection_status(self, connection_id: str) -> str:
        """Vérifie le statut."""
        try:
            import requests
            
            response = requests.get(
                f"{self.API_BASE}/items/{connection_id}",
                headers=self._headers()
            )
            response.raise_for_status()
            
            data = response.json()
            status_map = {
                0: "pending",
                1: "connected",
                2: "error"
            }
            return status_map.get(data.get("status"), "unknown")
        except Exception as e:
            logger.error(f"Erreur statut: {e}")
            return "error"
    
    def list_accounts(self, connection_id: str) -> list[dict]:
        """Liste les comptes."""
        try:
            import requests
            
            response = requests.get(
                f"{self.API_BASE}/accounts",
                headers=self._headers(),
                params={"item_uuid": connection_id}
            )
            response.raise_for_status()
            
            accounts = response.json().get("resources", [])
            return [
                {
                    "id": acc["uuid"],
                    "name": acc["name"],
                    "iban": acc.get("iban", ""),
                    "currency": acc.get("currency_code", "EUR"),
                    "balance": acc.get("balance", 0)
                }
                for acc in accounts
            ]
        except Exception as e:
            logger.error(f"Erreur liste comptes: {e}")
            return []
    
    def get_transactions(
        self,
        account_id: str,
        date_from: datetime | None = None,
        date_to: datetime | None = None
    ) -> list[dict]:
        """Récupère les transactions."""
        try:
            import requests
            
            params = {}
            if date_from:
                params["since"] = date_from.strftime("%Y-%m-%d")
            if date_to:
                params["until"] = date_to.strftime("%Y-%m-%d")
            
            response = requests.get(
                f"{self.API_BASE}/transactions",
                headers=self._headers(),
                params={"account_uuid": account_id, **params}
            )
            response.raise_for_status()
            
            transactions = response.json().get("resources", [])
            return [
                {
                    "id": t["uuid"],
                    "date": t["date"],
                    "amount": t["amount"],
                    "currency": t.get("currency_code", "EUR"),
                    "description": t.get("description", ""),
                    "counterparty": t.get("raw_description", ""),
                    "status": "booked"
                }
                for t in transactions
            ]
        except Exception as e:
            logger.error(f"Erreur transactions: {e}")
            return []
    
    def disconnect(self, connection_id: str) -> bool:
        """Supprime la connexion."""
        try:
            import requests
            
            response = requests.delete(
                f"{self.API_BASE}/items/{connection_id}",
                headers=self._headers()
            )
            return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Erreur déconnexion: {e}")
            return False
