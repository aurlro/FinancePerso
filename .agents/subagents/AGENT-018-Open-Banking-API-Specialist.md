# AGENT-018: Open Banking & API Integration Specialist

## 🎯 Mission

Spécialiste de l'intégration bancaire via Open Banking (PSD2) et APIs tierces. Responsable des connexions directes aux banques, de la synchronisation automatique des transactions, et de la gestion sécurisée des credentials bancaires.

---

## 📚 Contexte: Open Banking Architecture

### Philosophie
> "Le futur de la gestion financière est automatique. Connectez une fois, synchronisez toujours."

### APIs Supportées

```
┌─────────────────────────────────────────────────────────────────┐
│                    OPEN BANKING PROVIDERS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🇪🇺 EUROPE (PSD2)                                              │
│  ├── Bridge (Crédit Agricole) - bridgeapi.io                   │
│  ├── Tink (Visa) - tink.com                                    │
│  ├── TrueLayer - truelayer.com                                 │
│  ├── Budget Insight - budget-insight.com                       │
│  └── Nordigen (GoCardless) - gocardless.com                    │
│                                                                  │
│  🇫🇷 FRANCE SPÉCIFIQUE                                          │
│  ├── LaBanquePostale API                                       │
│  ├── Boursorama API                                            │
│  └── Crédit Mutuel API                                         │
│                                                                  │
│  🌍 INTERNATIONAL                                              │
│  ├── Plaid (US/UK/EU) - plaid.com                              │
│  ├── Yodlee (US) - yodlee.com                                  │
│  └── Salt Edge (Global) - saltedge.com                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture Technique

```python
# modules/banking/__init__.py
"""
Open Banking Integration Module.
Gestion des connexions bancaires via APIs PSD2.
"""

from .providers import (
    BridgeProvider,
    TinkProvider,
    TrueLayerProvider,
    NordigenProvider
)
from .sync import BankSyncManager, SyncSchedule
from .auth import OAuthManager, TokenStorage
from .webhooks import WebhookHandler

__all__ = [
    'BridgeProvider', 'TinkProvider', 'TrueLayerProvider', 'NordigenProvider',
    'BankSyncManager', 'SyncSchedule',
    'OAuthManager', 'TokenStorage',
    'WebhookHandler'
]
```

---

## 🧱 Module 1: Banking Provider Interface

```python
# modules/banking/providers.py

import abc
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Iterator
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib.parse import urlencode

from modules.logger import logger
from modules.encryption import encrypt_field, decrypt_field


@dataclass
class BankConnection:
    """Connexion bancaire."""
    id: str
    bank_name: str
    account_name: str
    account_iban: str
    currency: str
    balance: float
    status: str  # active, expired, error
    last_sync: datetime
    provider: str


@dataclass
class BankTransaction:
    """Transaction bancaire."""
    transaction_id: str
    date: str
    label: str
    amount: float
    currency: str
    category: Optional[str]
    merchant_name: Optional[str]


class BankingProvider(abc.ABC):
    """
    Interface abstraite pour les providers bancaires.
    """
    
    def __init__(self, client_id: str, client_secret: str, sandbox: bool = True):
        self.client_id = client_id
        self.client_secret = client_secret
        self.sandbox = sandbox
        self.session = requests.Session()
        self.session.mount('https://', HTTPAdapter(max_retries=3))
        self._access_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None
    
    @abc.abstractmethod
    def get_name(self) -> str:
        """Nom du provider."""
        pass
    
    @abc.abstractmethod
    def get_auth_url(self, redirect_uri: str, state: str) -> str:
        """URL d'authentification OAuth."""
        pass
    
    @abc.abstractmethod
    def exchange_code(self, code: str, redirect_uri: str) -> Dict:
        """Échange le code OAuth contre un token."""
        pass
    
    @abc.abstractmethod
    def refresh_token(self, refresh_token: str) -> Dict:
        """Rafraîchit le token d'accès."""
        pass
    
    @abc.abstractmethod
    def list_connections(self, access_token: str) -> List[BankConnection]:
        """Liste les connexions bancaires."""
        pass
    
    @abc.abstractmethod
    def get_transactions(
        self,
        access_token: str,
        account_id: str,
        date_from: datetime,
        date_to: datetime
    ) -> Iterator[BankTransaction]:
        """Récupère les transactions."""
        pass
    
    @abc.abstractmethod
    def get_balance(self, access_token: str, account_id: str) -> float:
        """Récupère le solde."""
        pass


class BridgeProvider(BankingProvider):
    """
    Provider Bridge (Crédit Agricole).
    https://bridgeapi.io
    """
    
    BASE_URL = "https://api.bridgeapi.io/v2"
    SANDBOX_URL = "https://api.sandbox.bridgeapi.io/v2"
    
    def __init__(self, client_id: str, client_secret: str, sandbox: bool = True):
        super().__init__(client_id, client_secret, sandbox)
        self.base_url = self.SANDBOX_URL if sandbox else self.BASE_URL
    
    def get_name(self) -> str:
        return "Bridge"
    
    def _get_headers(self, access_token: str = None) -> Dict:
        """Headers API."""
        headers = {
            "Client-Id": self.client_id,
            "Client-Secret": self.client_secret,
            "Content-Type": "application/json"
        }
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        return headers
    
    def get_auth_url(self, redirect_uri: str, state: str) -> str:
        """URL OAuth Bridge."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state
        }
        return f"{self.base_url}/authorize?{urlencode(params)}"
    
    def exchange_code(self, code: str, redirect_uri: str) -> Dict:
        """Échange code contre token."""
        url = f"{self.base_url}/authenticate"
        
        response = self.session.post(
            url,
            headers=self._get_headers(),
            json={
                "code": code,
                "redirect_uri": redirect_uri
            }
        )
        response.raise_for_status()
        
        data = response.json()
        return {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token"),
            "expires_in": data.get("expires_in", 3600)
        }
    
    def refresh_token(self, refresh_token: str) -> Dict:
        """Rafraîchit le token."""
        url = f"{self.base_url}/refresh"
        
        response = self.session.post(
            url,
            headers=self._get_headers(),
            json={"refresh_token": refresh_token}
        )
        response.raise_for_status()
        
        data = response.json()
        return {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token"),
            "expires_in": data.get("expires_in", 3600)
        }
    
    def list_connections(self, access_token: str) -> List[BankConnection]:
        """Liste les comptes connectés."""
        url = f"{self.base_url}/accounts"
        
        response = self.session.get(
            url,
            headers=self._get_headers(access_token)
        )
        response.raise_for_status()
        
        connections = []
        for item in response.json().get("resources", []):
            connections.append(BankConnection(
                id=str(item["id"]),
                bank_name=item.get("bank", {}).get("name", "Unknown"),
                account_name=item.get("name", "Compte"),
                account_iban=item.get("iban", ""),
                currency=item.get("currency", "EUR"),
                balance=item.get("balance", 0.0),
                status="active" if item.get("status") == 0 else "error",
                last_sync=datetime.now(),
                provider="bridge"
            ))
        
        return connections
    
    def get_transactions(
        self,
        access_token: str,
        account_id: str,
        date_from: datetime,
        date_to: datetime
    ) -> Iterator[BankTransaction]:
        """Récupère les transactions."""
        url = f"{self.base_url}/accounts/{account_id}/transactions"
        
        params = {
            "limit": 500,
            "from": date_from.strftime("%Y-%m-%d"),
            "to": date_to.strftime("%Y-%m-%d")
        }
        
        page = 1
        while True:
            params["page"] = page
            
            response = self.session.get(
                url,
                headers=self._get_headers(access_token),
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            transactions = data.get("resources", [])
            
            if not transactions:
                break
            
            for tx in transactions:
                yield BankTransaction(
                    transaction_id=str(tx["id"]),
                    date=tx["date"],
                    label=tx.get("wording", tx.get("label", "")),
                    amount=tx.get("amount", 0.0),
                    currency=tx.get("currency", "EUR"),
                    category=tx.get("category", {}).get("name"),
                    merchant_name=tx.get("merchant", {}).get("name")
                )
            
            page += 1
    
    def get_balance(self, access_token: str, account_id: str) -> float:
        """Récupère le solde."""
        url = f"{self.base_url}/accounts/{account_id}"
        
        response = self.session.get(
            url,
            headers=self._get_headers(access_token)
        )
        response.raise_for_status()
        
        return response.json().get("balance", 0.0)


class NordigenProvider(BankingProvider):
    """
    Provider Nordigen (GoCardless) - Gratuit et populaire.
    https://gocardless.com/bank-account-data
    """
    
    BASE_URL = "https://bankaccountdata.gocardless.com/api/v2"
    
    def __init__(self, secret_id: str, secret_key: str, sandbox: bool = False):
        super().__init__(secret_id, secret_key, sandbox)
        self._secret_id = secret_id
        self._secret_key = secret_key
        self._access_token = None
    
    def get_name(self) -> str:
        return "Nordigen (GoCardless)"
    
    def _get_access_token(self) -> str:
        """Obtient un token d'accès."""
        if self._access_token:
            return self._access_token
        
        url = f"{self.BASE_URL}/token/new/"
        
        response = self.session.post(
            url,
            json={
                "secret_id": self._secret_id,
                "secret_key": self._secret_key
            }
        )
        response.raise_for_status()
        
        data = response.json()
        self._access_token = data["access"]
        return self._access_token
    
    def get_auth_url(self, redirect_uri: str, state: str) -> str:
        """Nordigen utilise un processus différent (requisition)."""
        # Créer d'abord un agreement, puis une requisition
        # Cette méthode retourne l'URL de la requisition
        pass
    
    def list_banks(self, country: str = "FR") -> List[Dict]:
        """Liste les banques disponibles."""
        url = f"{self.BASE_URL}/institutions/"
        
        response = self.session.get(
            url,
            headers={"Authorization": f"Bearer {self._get_access_token()}"},
            params={"country": country}
        )
        response.raise_for_status()
        
        return response.json()
    
    def create_requisition(
        self,
        institution_id: str,
        redirect_uri: str,
        reference: str
    ) -> Dict:
        """
        Crée une requisition pour connecter une banque.
        
        Returns:
            Dict avec link (URL à ouvrir) et id (requisition_id)
        """
        # 1. Créer end user agreement
        agreement_url = f"{self.BASE_URL}/agreements/enduser/"
        
        agreement_resp = self.session.post(
            agreement_url,
            headers={"Authorization": f"Bearer {self._get_access_token()}"},
            json={
                "institution_id": institution_id,
                "max_historical_days": 90,
                "access_valid_for_days": 90,
                "access_scope": ["balances", "details", "transactions"]
            }
        )
        agreement_resp.raise_for_status()
        agreement_id = agreement_resp.json()["id"]
        
        # 2. Créer requisition
        requisition_url = f"{self.BASE_URL}/requisitions/"
        
        requisition_resp = self.session.post(
            requisition_url,
            headers={"Authorization": f"Bearer {self._get_access_token()}"},
            json={
                "institution_id": institution_id,
                "redirect": redirect_uri,
                "reference": reference,
                "agreement": agreement_id,
                "user_language": "FR"
            }
        )
        requisition_resp.raise_for_status()
        
        data = requisition_resp.json()
        return {
            "requisition_id": data["id"],
            "link": data["link"],
            "status": data["status"]
        }
    
    def get_requisition_status(self, requisition_id: str) -> Dict:
        """Vérifie le statut d'une requisition."""
        url = f"{self.BASE_URL}/requisitions/{requisition_id}/"
        
        response = self.session.get(
            url,
            headers={"Authorization": f"Bearer {self._get_access_token()}"}
        )
        response.raise_for_status()
        
        return response.json()
    
    def list_connections(self, access_token: str) -> List[BankConnection]:
        """Liste les comptes d'une requisition."""
        # Nordigen: les comptes sont dans la requisition
        # On doit passer par get_requisition_status puis lister les accounts
        pass
    
    def get_account_transactions(
        self,
        account_id: str,
        date_from: datetime,
        date_to: datetime
    ) -> Iterator[BankTransaction]:
        """Récupère les transactions d'un compte."""
        url = f"{self.BASE_URL}/accounts/{account_id}/transactions/"
        
        response = self.session.get(
            url,
            headers={"Authorization": f"Bearer {self._get_access_token()}"},
            params={
                "date_from": date_from.strftime("%Y-%m-%d"),
                "date_to": date_to.strftime("%Y-%m-%d")
            }
        )
        response.raise_for_status()
        
        data = response.json()
        transactions = data.get("transactions", {}).get("booked", [])
        
        for tx in transactions:
            amount_str = tx.get("transactionAmount", {}).get("amount", "0")
            yield BankTransaction(
                transaction_id=tx.get("transactionId", tx.get("entryReference", "")),
                date=tx.get("bookingDate", tx.get("valueDate")),
                label=tx.get("remittanceInformationUnstructured", "Transaction"),
                amount=float(amount_str),
                currency=tx.get("transactionAmount", {}).get("currency", "EUR"),
                category=None,  # Nordigen ne fournit pas de catégorie
                merchant_name=tx.get("creditorName") or tx.get("debtorName")
            )
```

---

## 🧱 Module 2: Bank Sync Manager

```python
# modules/banking/sync.py

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import threading
import time

from modules.db.connection import get_db_connection
from modules.db.transactions import calculate_tx_hash
from modules.categorization import categorize_transaction
from modules.logger import logger


class SyncStatus(Enum):
    """Statut de synchronisation."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"


@dataclass
class SyncResult:
    """Résultat de synchronisation."""
    status: SyncStatus
    transactions_new: int
    transactions_updated: int
    errors: List[str]
    started_at: datetime
    completed_at: datetime
    balance: Optional[float] = None


class BankSyncManager:
    """
    Gestionnaire de synchronisation bancaire.
    
    Responsabilités:
    - Planifier les synchronisations
    - Exécuter la synchro avec retry
    - Gérer les tokens expirés
    - Logger les résultats
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._active_syncs: Dict[str, threading.Thread] = {}
    
    def schedule_sync(
        self,
        connection_id: str,
        auto_sync: bool = True,
        sync_frequency_hours: int = 24
    ):
        """
        Planifie une synchronisation automatique.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT OR REPLACE INTO sync_schedules 
                (connection_id, auto_sync, frequency_hours, next_sync_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    connection_id,
                    auto_sync,
                    sync_frequency_hours,
                    datetime.now() + timedelta(hours=sync_frequency_hours)
                )
            )
            conn.commit()
        
        logger.info(f"Sync scheduled for connection {connection_id}")
    
    def run_sync(
        self,
        connection_id: str,
        force_full: bool = False
    ) -> SyncResult:
        """
        Exécute une synchronisation.
        
        Args:
            connection_id: ID de la connexion bancaire
            force_full: Force une synchro complète (pas incrémentale)
            
        Returns:
            SyncResult avec statistiques
        """
        started_at = datetime.now()
        
        # Récupérer connexion
        connection = self._get_connection(connection_id)
        if not connection:
            return SyncResult(
                status=SyncStatus.ERROR,
                transactions_new=0,
                transactions_updated=0,
                errors=["Connection not found"],
                started_at=started_at,
                completed_at=datetime.now()
            )
        
        try:
            # Instancier provider
            provider = self._get_provider(connection['provider'])
            
            # Rafraîchir token si nécessaire
            tokens = self._refresh_token_if_needed(connection_id, provider)
            
            # Déterminer date de début
            if force_full:
                date_from = datetime.now() - timedelta(days=90)
            else:
                date_from = connection['last_sync'] or (datetime.now() - timedelta(days=7))
            
            date_to = datetime.now()
            
            # Récupérer transactions
            new_transactions = []
            for tx in provider.get_transactions(
                tokens['access_token'],
                connection['external_account_id'],
                date_from,
                date_to
            ):
                # Vérifier doublon
                if not self._transaction_exists(tx.transaction_id):
                    new_transactions.append(tx)
            
            # Importer transactions
            imported = self._import_transactions(
                new_transactions,
                connection['account_mapping']
            )
            
            # Mettre à jour solde
            balance = provider.get_balance(
                tokens['access_token'],
                connection['external_account_id']
            )
            self._update_balance(connection_id, balance)
            
            # Mettre à jour last_sync
            self._update_last_sync(connection_id)
            
            return SyncResult(
                status=SyncStatus.SUCCESS,
                transactions_new=imported,
                transactions_updated=0,
                errors=[],
                started_at=started_at,
                completed_at=datetime.now(),
                balance=balance
            )
            
        except Exception as e:
            logger.error(f"Sync error for {connection_id}: {e}")
            return SyncResult(
                status=SyncStatus.ERROR,
                transactions_new=0,
                transactions_updated=0,
                errors=[str(e)],
                started_at=started_at,
                completed_at=datetime.now()
            )
    
    def run_all_scheduled_syncs(self):
        """Exécute toutes les synchronisations planifiées."""
        pending = self._get_pending_syncs()
        
        for sync in pending:
            # Lancer dans thread séparé pour ne pas bloquer
            thread = threading.Thread(
                target=self.run_sync,
                args=(sync['connection_id'],),
                name=f"sync_{sync['connection_id']}"
            )
            thread.start()
            self._active_syncs[sync['connection_id']] = thread
    
    def _get_connection(self, connection_id: str) -> Optional[Dict]:
        """Récupère une connexion."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM bank_connections WHERE id = ?",
                (connection_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def _get_provider(self, provider_name: str):
        """Instancie un provider."""
        from modules.banking.providers import BridgeProvider, NordigenProvider
        
        # Récupérer credentials
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM banking_credentials WHERE provider = ?",
                (provider_name,)
            )
            creds = cursor.fetchone()
        
        if provider_name == "bridge":
            return BridgeProvider(
                client_id=creds['client_id'],
                client_secret=creds['client_secret'],
                sandbox=False
            )
        elif provider_name == "nordigen":
            return NordigenProvider(
                secret_id=creds['secret_id'],
                secret_key=creds['secret_key']
            )
        
        raise ValueError(f"Unknown provider: {provider_name}")
    
    def _refresh_token_if_needed(
        self,
        connection_id: str,
        provider
    ) -> Dict:
        """Rafraîchit le token si expiré."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM bank_tokens WHERE connection_id = ?",
                (connection_id,)
            )
            tokens = dict(cursor.fetchone())
        
        # Vérifier expiration
        expires_at = datetime.fromisoformat(tokens['expires_at'])
        if datetime.now() > expires_at - timedelta(minutes=5):
            # Rafraîchir
            new_tokens = provider.refresh_token(tokens['refresh_token'])
            
            # Sauvegarder
            self._save_tokens(connection_id, new_tokens)
            
            return new_tokens
        
        return tokens
    
    def _transaction_exists(self, external_id: str) -> bool:
        """Vérifie si une transaction existe déjà."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM transactions WHERE external_id = ?",
                (external_id,)
            )
            return cursor.fetchone() is not None
    
    def _import_transactions(
        self,
        transactions: List[BankTransaction],
        account_mapping: str
    ) -> int:
        """Importe les transactions."""
        imported = 0
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            for tx in transactions:
                # Catégorisation auto
                category = None
                cat_result = categorize_transaction({
                    'label': tx.label,
                    'amount': tx.amount
                })
                category = cat_result.get('category')
                
                cursor.execute(
                    """
                    INSERT INTO transactions 
                    (date, label, amount, external_id, category_validated, 
                     account_id, status, import_source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        tx.date,
                        tx.label,
                        tx.amount,
                        tx.transaction_id,
                        category,
                        account_mapping,
                        'pending' if not category else 'validated',
                        'banking_sync'
                    )
                )
                imported += 1
            
            conn.commit()
        
        return imported
    
    def _get_pending_syncs(self) -> List[Dict]:
        """Récupère les synchros à exécuter."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM sync_schedules 
                WHERE auto_sync = 1 
                AND next_sync_at <= ?
                """,
                (datetime.now(),)
            )
            return [dict(row) for row in cursor.fetchall()]
```

---

## 🧱 Module 3: UI Banking

```python
# modules/ui/banking/__init__.py

import streamlit as st
from modules.banking.providers import BridgeProvider, NordigenProvider
from modules.banking.sync import BankSyncManager


def render_banking_connections_page():
    """Page de gestion des connexions bancaires."""
    st.header("🏦 Connexions Bancaires")
    
    st.info("""
    Connectez vos comptes bancaires pour une synchronisation automatique.
    
    **Sécurité:**
    - Connexion sécurisée via OAuth2
    - Tokens chiffrés en base
    - Aucun credential stocké en clair
    """)
    
    # Liste des connexions existantes
    connections = get_bank_connections()
    
    if connections:
        st.subheader("Comptes connectés")
        
        for conn in connections:
            with st.expander(f"🏦 {conn['bank_name']} - {conn['account_name']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Solde", f"{conn['balance']:,.2f} €")
                
                with col2:
                    status_color = "🟢" if conn['status'] == 'active' else "🔴"
                    st.write(f"{status_color} Statut: {conn['status']}")
                
                with col3:
                    if conn['last_sync']:
                        st.write(f"🔄 Dernière synchro: {conn['last_sync']}")
                
                # Actions
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("🔄 Synchroniser", key=f"sync_{conn['id']}"):
                        with st.spinner("Synchronisation..."):
                            manager = BankSyncManager()
                            result = manager.run_sync(conn['id'])
                            
                            if result.status.value == "success":
                                st.success(f"✅ {result.transactions_new} nouvelles transactions")
                            else:
                                st.error(f"❌ Erreur: {result.errors}")
                
                with col2:
                    if st.button("⚙️ Paramètres", key=f"settings_{conn['id']}"):
                        render_connection_settings(conn)
                
                with col3:
                    if st.button("🗑️ Déconnecter", key=f"delete_{conn['id']}"):
                        if st.checkbox("Confirmer la déconnexion?", key=f"confirm_{conn['id']}"):
                            disconnect_bank(conn['id'])
                            st.success("Compte déconnecté")
                            st.rerun()
    else:
        st.info("Aucun compte bancaire connecté")
    
    st.divider()
    
    # Ajouter une connexion
    st.subheader("➕ Ajouter une connexion")
    
    provider = st.selectbox(
        "Sélectionnez votre banque ou provider",
        options=[
            ("bridge", "Bridge (Crédit Agricole, BNP, etc.)"),
            ("nordigen", "Nordigen/GoCardless (Multi-banques, gratuit)"),
        ],
        format_func=lambda x: x[1]
    )
    
    if provider[0] == "bridge":
        render_bridge_connection_flow()
    elif provider[0] == "nordigen":
        render_nordigen_connection_flow()


def render_bridge_connection_flow():
    """Flow de connexion Bridge."""
    st.write("**Connexion via Bridge**")
    
    # Vérifier credentials configurés
    if not check_provider_configured("bridge"):
        st.warning("⚠️ Bridge n'est pas configuré")
        
        with st.expander("Configuration Bridge"):
            client_id = st.text_input("Client ID", type="password")
            client_secret = st.text_input("Client Secret", type="password")
            
            if st.button("Sauvegarder"):
                save_provider_credentials("bridge", client_id, client_secret)
                st.success("Configuration sauvegardée")
                st.rerun()
        return
    
    # Lancer OAuth
    if st.button("🔗 Connecter mon compte", type="primary"):
        provider = BridgeProvider(
            client_id=get_provider_credential("bridge", "client_id"),
            client_secret=get_provider_credential("bridge", "client_secret"),
            sandbox=False
        )
        
        # Générer state
        import secrets
        state = secrets.token_urlsafe(32)
        
        # Sauvegarder state
        save_oauth_state(state, "bridge")
        
        # Obtenir URL
        redirect_uri = "http://localhost:8501/banking/callback"
        auth_url = provider.get_auth_url(redirect_uri, state)
        
        st.markdown(f"**[Cliquez ici pour vous connecter]({auth_url})**")
        st.info("Après autorisation, vous serez redirigé vers l'application")


def render_nordigen_connection_flow():
    """Flow de connexion Nordigen."""
    st.write("**Connexion via Nordigen (Gratuit)**")
    
    # Vérifier credentials
    if not check_provider_configured("nordigen"):
        st.info("""
        Nordigen nécessite un compte gratuit:
        1. Créez un compte sur [gocardless.com](https://gocardless.com/bank-account-data)
        2. Récupérez votre Secret ID et Secret Key
        """)
        
        with st.expander("Configuration Nordigen"):
            secret_id = st.text_input("Secret ID", type="password")
            secret_key = st.text_input("Secret Key", type="password")
            
            if st.button("Sauvegarder"):
                save_provider_credentials("nordigen", secret_id, secret_key)
                st.success("Configuration sauvegardée")
                st.rerun()
        return
    
    # Liste des banques
    provider = NordigenProvider(
        secret_id=get_provider_credential("nordigen", "secret_id"),
        secret_key=get_provider_credential("nordigen", "secret_key")
    )
    
    banks = provider.list_banks("FR")
    
    bank = st.selectbox(
        "Sélectionnez votre banque",
        options=banks,
        format_func=lambda x: f"{x['name']} ({x['bic']})"
    )
    
    if st.button("🔗 Connecter", type="primary"):
        redirect_uri = "http://localhost:8501/banking/callback"
        reference = f"user_{st.session_state.get('user_id', 'anon')}_{int(time.time())}"
        
        requisition = provider.create_requisition(
            institution_id=bank['id'],
            redirect_uri=redirect_uri,
            reference=reference
        )
        
        # Sauvegarder requisition_id
        save_requisition(requisition['requisition_id'], bank['id'])
        
        # Rediriger
        st.markdown(f"**[Autoriser l'accès]({requisition['link']})**")


def render_sync_history():
    """Affiche l'historique des synchronisations."""
    st.subheader("📜 Historique des synchronisations")
    
    history = get_sync_history()
    
    if history:
        import pandas as pd
        df = pd.DataFrame(history)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aucune synchronisation effectuée")


# Helpers

def get_bank_connections():
    """Récupère les connexions bancaires."""
    from modules.db.connection import get_db_connection
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bank_connections WHERE status = 'active'")
        return [dict(row) for row in cursor.fetchall()]


def check_provider_configured(provider: str) -> bool:
    """Vérifie si un provider est configuré."""
    from modules.db.connection import get_db_connection
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM banking_credentials WHERE provider = ?",
            (provider,)
        )
        return cursor.fetchone() is not None


def save_provider_credentials(provider: str, *args):
    """Sauvegarde les credentials (chiffrés)."""
    from modules.db.connection import get_db_connection
    from modules.encryption import encrypt_field
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if provider == "bridge":
            cursor.execute(
                """
                INSERT OR REPLACE INTO banking_credentials 
                (provider, client_id, client_secret, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (provider, encrypt_field(args[0]), encrypt_field(args[1]), datetime.now())
            )
        elif provider == "nordigen":
            cursor.execute(
                """
                INSERT OR REPLACE INTO banking_credentials 
                (provider, secret_id, secret_key, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (provider, encrypt_field(args[0]), encrypt_field(args[1]), datetime.now())
            )
        
        conn.commit()
```

---

## 🗄️ Schéma Base de Données

```sql
-- Tables pour Open Banking

CREATE TABLE banking_credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,
    client_id TEXT,
    client_secret TEXT,
    secret_id TEXT,
    secret_key TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bank_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,
    external_account_id TEXT NOT NULL,
    bank_name TEXT,
    account_name TEXT,
    account_iban TEXT,
    currency TEXT DEFAULT 'EUR',
    balance REAL DEFAULT 0,
    status TEXT DEFAULT 'pending',
    user_id INTEGER,
    account_mapping TEXT,  -- Map vers compte FP
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_sync TIMESTAMP,
    UNIQUE(provider, external_account_id)
);

CREATE TABLE bank_tokens (
    connection_id INTEGER PRIMARY KEY,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (connection_id) REFERENCES bank_connections(id) ON DELETE CASCADE
);

CREATE TABLE sync_schedules (
    connection_id INTEGER PRIMARY KEY,
    auto_sync INTEGER DEFAULT 1,
    frequency_hours INTEGER DEFAULT 24,
    next_sync_at TIMESTAMP,
    FOREIGN KEY (connection_id) REFERENCES bank_connections(id) ON DELETE CASCADE
);

CREATE TABLE sync_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    connection_id INTEGER,
    status TEXT,
    transactions_new INTEGER DEFAULT 0,
    transactions_updated INTEGER DEFAULT 0,
    errors TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (connection_id) REFERENCES bank_connections(id)
);
```

---

**Agent spécialisé AGENT-018** - Open Banking & API Integration  
_Version 1.0 - Connexions bancaires PSD2_  
_Support: Bridge, Nordigen/GoCardless (extensible)_
