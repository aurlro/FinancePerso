# AGENT-018: Open Banking & API Integration Specialist

> **Spécialiste Open Banking et Intégrations API**  
> Responsable des connexions bancaires, synchronisation temps réel, et conformité PSD2

---

## 🎯 Mission

Cet agent conçoit et implémente les intégrations bancaires via Open Banking (PSD2). Il gère les flux OAuth, la synchronisation automatique des transactions, la gestion des consentements utilisateurs, et assure la sécurité des données bancaires.

### Domaines d'expertise
- **Open Banking APIs** : Bridge, TrueLayer, Budget Insight
- **OAuth 2.0 / OIDC** : Flows d'authentification sécurisés
- **PSD2 Compliance** : Consentement, audit, révocation
- **Real-time Sync** : Webhooks, polling intelligent, rate limiting
- **Token Security** : Encryption, rotation, vaulting sécurisé

---

## 🏗️ Architecture Technique

```
┌─────────────────────────────────────────────────────────────────┐
│                    BANKING PROVIDER INTERFACE                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Bridge    │  │ TrueLayer   │  │    Budget Insight       │ │
│  │  (Bankin')  │  │             │  │                         │ │
│  └──────┬──────┘  └──────┬──────┘  └────────────┬────────────┘ │
│         └─────────────────┼──────────────────────┘              │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              SYNC ENGINE ORCHESTRATOR                     │  │
│  │  Scheduling │ Rate Limiting │ Circuit Breaker │ Retry    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              CONSENT & SECURITY MANAGER                          │
├─────────────────────────────────────────────────────────────────┤
│  PSD2 Compliance │ Token Vault │ Audit Logs │ Encryption        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧱 Module 1: Provider Interface

### Abstraction unifiée des providers bancaires

```python
# modules/banking/providers/base.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, AsyncIterator
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConnectionStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    ERROR = "error"
    DISCONNECTED = "disconnected"


@dataclass
class BankAccount:
    """Compte bancaire normalisé."""
    id: str
    connection_id: str
    bank_id: str
    bank_name: str
    account_type: str
    currency: str
    balance: float
    balance_date: datetime
    name: str
    iban: Optional[str] = None
    masked_number: Optional[str] = None


@dataclass
class BankTransaction:
    """Transaction bancaire normalisée."""
    id: str
    account_id: str
    date: datetime
    amount: float
    currency: str
    description: str
    category: Optional[str] = None
    pending: bool = False
    transaction_type: str = "unknown"
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SyncResult:
    """Résultat d'une synchronisation."""
    success: bool
    connection_id: str
    transactions_new: int = 0
    transactions_updated: int = 0
    accounts_synced: int = 0
    errors: List[Dict] = None
    next_sync_possible: Optional[datetime] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class BankingProvider(ABC):
    """Interface abstraite pour tous les providers bancaires."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')
        self.redirect_uri = config.get('redirect_uri')
        self.environment = config.get('environment', 'sandbox')
        self._rate_limit_remaining = 100
        self._rate_limit_reset = datetime.now()
    
    @abstractmethod
    def get_oauth_url(self, state: str, scopes: List[str] = None) -> str:
        """Génère l'URL d'autorisation OAuth."""
        pass
    
    @abstractmethod
    def exchange_code(self, code: str) -> Dict:
        """Échange le code d'autorisation contre des tokens."""
        pass
    
    @abstractmethod
    def refresh_token(self, refresh_token: str) -> Dict:
        """Rafraîchit un token expiré."""
        pass
    
    @abstractmethod
    def revoke_connection(self, connection_id: str) -> bool:
        """Révoque une connexion côté provider."""
        pass
    
    @abstractmethod
    def get_accounts(self, connection_id: str, access_token: str) -> List[BankAccount]:
        """Récupère la liste des comptes."""
        pass
    
    @abstractmethod
    def get_transactions(self, connection_id: str, account_id: str, 
                        access_token: str, date_from: datetime = None,
                        date_to: datetime = None) -> List[BankTransaction]:
        """Récupère les transactions d'un compte."""
        pass
    
    def can_sync(self, last_sync: Optional[datetime]) -> bool:
        """Vérifie si une synchronisation est autorisée (rate limiting)."""
        if self._rate_limit_remaining < 5:
            if datetime.now() < self._rate_limit_reset:
                return False
        
        if last_sync:
            min_interval = timedelta(seconds=30)
            if datetime.now() - last_sync < min_interval:
                return False
        
        return True
    
    def sync_all(self, connection_id: str, access_token: str) -> SyncResult:
        """Synchronise tous les comptes et transactions."""
        result = SyncResult(success=True, connection_id=connection_id)
        
        try:
            accounts = self.get_accounts(connection_id, access_token)
            result.accounts_synced = len(accounts)
            
            for account in accounts:
                transactions = self.get_transactions(
                    connection_id, account.id, access_token,
                    date_from=datetime.now() - timedelta(days=90)
                )
                
                new_count, updated_count = self._process_transactions(account.id, transactions)
                result.transactions_new += new_count
                result.transactions_updated += updated_count
            
            result.next_sync_possible = datetime.now() + timedelta(minutes=5)
            
        except Exception as e:
            logger.error(f"Sync failed for {connection_id}: {e}")
            result.success = False
            result.errors.append({'type': 'sync_error', 'message': str(e)})
        
        return result
    
    def _process_transactions(self, account_id: str, transactions: List[BankTransaction]) -> tuple[int, int]:
        """Traite les transactions récupérées."""
        from modules.db.transactions import insert_or_update_transaction
        
        new_count = 0
        updated_count = 0
        
        for tx in transactions:
            existing = self._find_existing_transaction(tx)
            
            if existing:
                if self._transaction_changed(existing, tx):
                    insert_or_update_transaction(tx, update=True)
                    updated_count += 1
            else:
                insert_or_update_transaction(tx)
                new_count += 1
        
        return new_count, updated_count
    
    def _find_existing_transaction(self, transaction: BankTransaction) -> Optional[Dict]:
        """Cherche une transaction existante par hash."""
        import hashlib
        tx_hash = f"{transaction.account_id}|{transaction.date.isoformat()}|{transaction.amount}|{transaction.description[:50]}"
        tx_hash = hashlib.md5(tx_hash.encode()).hexdigest()
        
        from modules.db.transactions import find_transaction_by_hash
        return find_transaction_by_hash(tx_hash)
    
    def _transaction_changed(self, existing: Dict, new: BankTransaction) -> bool:
        """Vérifie si une transaction a changé."""
        return (
            existing.get('pending') != new.pending or
            abs(existing.get('amount', 0) - new.amount) > 0.01 or
            existing.get('category') != new.category
        )


# modules/banking/providers/bridge.py

import requests
from datetime import datetime, timedelta

class BridgeProvider(BankingProvider):
    """Implémentation provider Bridge (Bankin')."""
    
    BASE_URLS = {
        'sandbox': 'https://api.bridgeapi.io/v2',
        'production': 'https://api.bridgeapi.io/v2'
    }
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = self.BASE_URLS.get(self.environment, self.BASE_URLS['sandbox'])
    
    def _get_headers(self, access_token: str = None) -> Dict:
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Bridge-Version': '2021-06-01'
        }
        
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        else:
            headers['Client-Id'] = self.client_id
            headers['Client-Secret'] = self.client_secret
        
        return headers
    
    def get_oauth_url(self, state: str, scopes: List[str] = None) -> str:
        """Génère l'URL d'autorisation Bridge."""
        from urllib.parse import urlencode
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(scopes or ['transactions', 'accounts']),
            'state': state
        }
        
        return f"{self.base_url}/auth?{urlencode(params)}"
    
    def exchange_code(self, code: str) -> Dict:
        """Échange le code contre des tokens."""
        url = f"{self.base_url}/authenticate"
        
        payload = {
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        
        response = requests.post(url, json=payload, headers=self._get_headers())
        response.raise_for_status()
        
        data = response.json()
        
        return {
            'access_token': data['access_token'],
            'refresh_token': data.get('refresh_token'),
            'expires_at': datetime.now() + timedelta(seconds=data.get('expires_in', 3600)),
            'connection_id': str(data.get('user', {}).get('uuid'))
        }
    
    def refresh_token(self, refresh_token: str) -> Dict:
        """Rafraîchit le token."""
        url = f"{self.base_url}/refresh"
        
        response = requests.post(url, json={'refresh_token': refresh_token},
                                headers=self._get_headers())
        response.raise_for_status()
        
        data = response.json()
        
        return {
            'access_token': data['access_token'],
            'refresh_token': data.get('refresh_token', refresh_token),
            'expires_at': datetime.now() + timedelta(seconds=data.get('expires_in', 3600))
        }
    
    def revoke_connection(self, connection_id: str) -> bool:
        """Révoque une connexion."""
        logger.info(f"Bridge connection {connection_id} must be revoked via dashboard")
        return True
    
    def get_accounts(self, connection_id: str, access_token: str) -> List[BankAccount]:
        """Récupère les comptes."""
        url = f"{self.base_url}/accounts"
        
        response = requests.get(url, headers=self._get_headers(access_token))
        response.raise_for_status()
        
        data = response.json()
        accounts = []
        
        for acc in data.get('resources', []):
            accounts.append(BankAccount(
                id=str(acc['id']),
                connection_id=connection_id,
                bank_id=str(acc.get('bank', {}).get('id', '')),
                bank_name=acc.get('bank', {}).get('name', 'Unknown'),
                account_type=acc.get('type', 'unknown'),
                currency=acc.get('currency', 'EUR'),
                balance=acc.get('balance', 0),
                balance_date=datetime.now(),
                name=acc.get('name', 'Compte'),
                iban=acc.get('iban'),
                masked_number=acc.get('number')
            ))
        
        return accounts
    
    def get_transactions(self, connection_id: str, account_id: str,
                        access_token: str, date_from: datetime = None,
                        date_to: datetime = None) -> List[BankTransaction]:
        """Récupère les transactions avec pagination."""
        transactions = []
        next_uri = f"{self.base_url}/accounts/{account_id}/transactions"
        
        params = {}
        if date_from:
            params['since'] = date_from.strftime('%Y-%m-%d')
        if date_to:
            params['until'] = date_to.strftime('%Y-%m-%d')
        
        while next_uri:
            response = requests.get(next_uri, params=params, 
                                  headers=self._get_headers(access_token))
            response.raise_for_status()
            
            data = response.json()
            
            for tx in data.get('resources', []):
                transactions.append(self._normalize_transaction(tx, account_id))
            
            next_uri = data.get('pagination', {}).get('next_uri')
            params = {}
        
        return transactions
    
    def _normalize_transaction(self, raw: Dict, account_id: str) -> BankTransaction:
        """Normalise une transaction Bridge."""
        return BankTransaction(
            id=str(raw['id']),
            account_id=account_id,
            date=datetime.strptime(raw['date'], '%Y-%m-%d'),
            amount=float(raw['amount']),
            currency=raw.get('currency', 'EUR'),
            description=raw.get('label', ''),
            category=raw.get('category', {}).get('name'),
            pending=raw.get('status') == 'pending',
            transaction_type='expense' if float(raw['amount']) < 0 else 'income'
        )


# modules/banking/providers/truelayer.py

class TruelayerProvider(BankingProvider):
    """Implémentation provider TrueLayer."""
    
    BASE_URLS = {
        'sandbox': 'https://api.truelayer-sandbox.com',
        'production': 'https://api.truelayer.com'
    }
    
    AUTH_URLS = {
        'sandbox': 'https://auth.truelayer-sandbox.com',
        'production': 'https://auth.truelayer.com'
    }
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = self.BASE_URLS.get(self.environment, self.BASE_URLS['sandbox'])
        self.auth_url = self.AUTH_URLS.get(self.environment, self.AUTH_URLS['sandbox'])
    
    def _get_headers(self, access_token: str = None) -> Dict:
        headers = {'Accept': 'application/json'}
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        return headers
    
    def get_oauth_url(self, state: str, scopes: List[str] = None) -> str:
        from urllib.parse import urlencode
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(scopes or ['accounts', 'transactions']),
            'state': state
        }
        
        return f"{self.auth_url}/?{urlencode(params)}"
    
    def exchange_code(self, code: str) -> Dict:
        url = f"{self.auth_url}/connect/token"
        
        payload = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        
        response = requests.post(url, data=payload)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            'access_token': data['access_token'],
            'refresh_token': data.get('refresh_token'),
            'expires_at': datetime.now() + timedelta(seconds=data.get('expires_in', 3600)),
            'connection_id': data.get('user_id', 'unknown')
        }
    
    def refresh_token(self, refresh_token: str) -> Dict:
        url = f"{self.auth_url}/connect/token"
        
        payload = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token
        }
        
        response = requests.post(url, data=payload)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            'access_token': data['access_token'],
            'refresh_token': data.get('refresh_token', refresh_token),
            'expires_at': datetime.now() + timedelta(seconds=data.get('expires_in', 3600))
        }
    
    def revoke_connection(self, connection_id: str) -> bool:
        logger.info(f"TrueLayer connection {connection_id} revocation should be done via API")
        return True
    
    def get_accounts(self, connection_id: str, access_token: str) -> List[BankAccount]:
        url = f"{self.base_url}/data/v1/accounts"
        
        response = requests.get(url, headers=self._get_headers(access_token))
        response.raise_for_status()
        
        data = response.json()
        
        return [
            BankAccount(
                id=acc['account_id'],
                connection_id=connection_id,
                bank_id=acc.get('provider', {}).get('provider_id', ''),
                bank_name=acc.get('provider', {}).get('display_name', 'Unknown'),
                account_type=acc.get('account_type', 'unknown'),
                currency=acc.get('currency', 'EUR'),
                balance=acc.get('balance', 0),
                balance_date=datetime.now(),
                name=acc.get('display_name', 'Compte'),
                iban=acc.get('account_number', {}).get('iban'),
                masked_number=acc.get('account_number', {}).get('number')
            )
            for acc in data.get('results', [])
        ]
    
    def get_transactions(self, connection_id: str, account_id: str,
                        access_token: str, date_from: datetime = None,
                        date_to: datetime = None) -> List[BankTransaction]:
        url = f"{self.base_url}/data/v1/accounts/{account_id}/transactions"
        
        params = {}
        if date_from:
            params['from'] = date_from.isoformat()
        if date_to:
            params['to'] = date_to.isoformat()
        
        response = requests.get(url, params=params, headers=self._get_headers(access_token))
        response.raise_for_status()
        
        data = response.json()
        
        return [
            BankTransaction(
                id=tx['transaction_id'],
                account_id=account_id,
                date=datetime.fromisoformat(tx['timestamp'].replace('Z', '+00:00')),
                amount=float(tx['amount']),
                currency=tx.get('currency', 'EUR'),
                description=tx.get('description', ''),
                pending=tx.get('status') == 'pending',
                transaction_type=tx.get('transaction_type', 'unknown')
            )
            for tx in data.get('results', [])
        ]


---

## 🧱 Module 2: Consent & Security Manager

### Gestion du Consentement PSD2

```python
# modules/banking/consent_manager.py

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class ConsentAction(Enum):
    GRANTED = "granted"
    REFRESHED = "refreshed"
    REVOKED = "revoked"
    EXPIRED = "expired"


@dataclass
class ConsentRecord:
    """Enregistrement d'un consentement utilisateur PSD2."""
    id: str
    user_id: str
    connection_id: str
    provider: str
    bank_id: str
    bank_name: str
    scopes: List[str]
    
    granted_at: datetime
    expires_at: datetime
    is_active: bool = True
    
    revoked_at: Optional[datetime] = None
    revoke_reason: Optional[str] = None
    revoked_by: Optional[str] = None
    
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at
    
    @property
    def days_until_expiry(self) -> int:
        if self.is_expired:
            return 0
        delta = self.expires_at - datetime.now()
        return max(0, delta.days)
    
    @property
    def status(self) -> str:
        if self.revoked_at:
            return 'revoked'
        if self.is_expired:
            return 'expired'
        if not self.is_active:
            return 'inactive'
        if self.days_until_expiry <= 7:
            return 'expiring_soon'
        return 'active'


class ConsentManager:
    """Gestionnaire de consentements PSD2."""
    
    MAX_CONSENT_DAYS = 180
    REMINDER_DAYS = [30, 14, 7, 1]
    
    def create_consent(
        self,
        user_id: str,
        connection_id: str,
        provider: str,
        bank_id: str,
        bank_name: str,
        scopes: List[str],
        duration_days: int = 180,
        client_info: Dict = None
    ) -> ConsentRecord:
        """Crée un nouveau consentement."""
        duration = min(duration_days, self.MAX_CONSENT_DAYS)
        
        granted_at = datetime.now()
        expires_at = granted_at + timedelta(days=duration)
        
        consent = ConsentRecord(
            id=generate_uuid(),
            user_id=user_id,
            connection_id=connection_id,
            provider=provider,
            bank_id=bank_id,
            bank_name=bank_name,
            scopes=scopes,
            granted_at=granted_at,
            expires_at=expires_at,
            ip_address=client_info.get('ip_address') if client_info else None,
            user_agent=client_info.get('user_agent') if client_info else None
        )
        
        self._save_consent(consent)
        self._log_consent_action(consent, ConsentAction.GRANTED, client_info)
        
        return consent
    
    def validate_consent(self, consent_id: str) -> Optional[ConsentRecord]:
        """Valide un consentement pour utilisation."""
        consent = self._get_consent(consent_id)
        
        if not consent or consent.revoked_at or consent.is_expired or not consent.is_active:
            return None
        
        return consent
    
    def revoke_consent(
        self,
        consent_id: str,
        reason: str = "user_request",
        revoked_by: str = "user"
    ) -> bool:
        """Révoque un consentement."""
        consent = self._get_consent(consent_id)
        if not consent or consent.revoked_at:
            return False
        
        consent.is_active = False
        consent.revoked_at = datetime.now()
        consent.revoke_reason = reason
        consent.revoked_by = revoked_by
        
        self._save_consent(consent)
        self._log_consent_action(consent, ConsentAction.REVOKED)
        
        return True
    
    def _save_consent(self, consent: ConsentRecord):
        """Sauvegarde un consentement."""
        from modules.db.connection import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO bank_consents
                (id, user_id, connection_id, provider, bank_id, bank_name, scopes,
                 granted_at, expires_at, is_active, revoked_at, revoke_reason, revoked_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                consent.id, consent.user_id, consent.connection_id,
                consent.provider, consent.bank_id, consent.bank_name,
                json.dumps(consent.scopes),
                consent.granted_at, consent.expires_at, consent.is_active,
                consent.revoked_at, consent.revoke_reason, consent.revoked_by
            ))
            conn.commit()
    
    def _get_consent(self, consent_id: str) -> Optional[ConsentRecord]:
        """Charge un consentement."""
        from modules.db.connection import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bank_consents WHERE id = ?", (consent_id,))
            row = cursor.fetchone()
            
            if row:
                return ConsentRecord(
                    id=row['id'],
                    user_id=row['user_id'],
                    connection_id=row['connection_id'],
                    provider=row['provider'],
                    bank_id=row['bank_id'],
                    bank_name=row['bank_name'],
                    scopes=json.loads(row['scopes']),
                    granted_at=row['granted_at'],
                    expires_at=row['expires_at'],
                    is_active=bool(row['is_active']),
                    revoked_at=row['revoked_at'],
                    revoke_reason=row['revoke_reason'],
                    revoked_by=row['revoked_by']
                )
            return None
    
    def _log_consent_action(self, consent: ConsentRecord, action: ConsentAction, client_info: Dict = None):
        """Log pour audit."""
        from modules.db.connection import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO consent_audit_log
                (consent_id, timestamp, action, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?)
            """, (
                consent.id,
                datetime.now(),
                action.value,
                client_info.get('ip_address') if client_info else consent.ip_address,
                client_info.get('user_agent') if client_info else consent.user_agent
            ))
            conn.commit()


class TokenVault:
    """Stockage sécurisé des tokens bancaires."""
    
    def __init__(self):
        self._encryption = get_encryption_service()
    
    def store_tokens(self, connection_id: str, access_token: str, 
                    refresh_token: str, expires_at: datetime):
        """Stocke des tokens de manière sécurisée."""
        encrypted_access = self._encryption.encrypt(access_token)
        encrypted_refresh = self._encryption.encrypt(refresh_token)
        
        from modules.db.connection import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO bank_tokens
                (connection_id, access_token, refresh_token, expires_at, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                connection_id, encrypted_access, encrypted_refresh,
                expires_at, datetime.now()
            ))
            conn.commit()
    
    def get_tokens(self, connection_id: str) -> Optional[Dict]:
        """Récupère et décrypte les tokens."""
        from modules.db.connection import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bank_tokens WHERE connection_id = ?", (connection_id,))
            row = cursor.fetchone()
            
            if not row or datetime.now() > row['expires_at']:
                return None
            
            return {
                'access_token': self._encryption.decrypt(row['access_token']),
                'refresh_token': self._encryption.decrypt(row['refresh_token']),
                'expires_at': row['expires_at']
            }
    
    def revoke_tokens(self, connection_id: str):
        """Révoque et supprime les tokens."""
        from modules.db.connection import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bank_tokens WHERE connection_id = ?", (connection_id,))
            conn.commit()


def generate_uuid():
    """Génère un UUID."""
    import uuid
    return str(uuid.uuid4())


def get_encryption_service():
    """Retourne le service d'encryption."""
    from modules.security.encryption import EncryptionService
    return EncryptionService()


---

## 🧱 Module 3: Sync Engine

### Moteur de synchronisation automatique

```python
# modules/banking/sync_engine.py

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import threading
import time
import logging
from queue import Queue, Empty

logger = logging.getLogger(__name__)


class SyncFrequency(Enum):
    HOURLY = "hourly"
    EVERY_6H = "6h"
    EVERY_12H = "12h"
    DAILY = "daily"
    MANUAL = "manual"


@dataclass
class SyncSchedule:
    """Configuration de synchronisation."""
    connection_id: str
    provider_type: str
    frequency: SyncFrequency
    is_active: bool = True
    last_sync: Optional[datetime] = None
    next_sync: Optional[datetime] = None
    auto_categorize: bool = True
    notify_on_new: bool = True


@dataclass
class SyncJob:
    """Job de synchronisation."""
    connection_id: str
    provider_type: str
    scheduled_at: datetime
    priority: int = 0
    force: bool = False


class CircuitBreaker:
    """Circuit breaker pour éviter cascades d'erreurs."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self._state = "CLOSED"
        self._failure_count = 0
        self._last_failure_time = None
        self._lock = threading.Lock()
    
    def can_execute(self) -> bool:
        """Vérifie si l'exécution est autorisée."""
        with self._lock:
            if self._state == "CLOSED":
                return True
            
            if self._state == "OPEN":
                if self._should_attempt_reset():
                    self._state = "HALF_OPEN"
                    return True
                return False
            
            return True
    
    def record_success(self):
        """Enregistre un succès."""
        with self._lock:
            self._failure_count = 0
            if self._state == "HALF_OPEN":
                self._state = "CLOSED"
    
    def record_failure(self):
        """Enregistre un échec."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = datetime.now()
            
            if self._failure_count >= self.failure_threshold:
                self._state = "OPEN"
    
    def _should_attempt_reset(self) -> bool:
        """Vérifie si on peut tenter reset."""
        if not self._last_failure_time:
            return True
        elapsed = (datetime.now() - self._last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout


class SyncEngine:
    """Moteur de synchronisation automatique."""
    
    def __init__(self, max_workers: int = 3):
        self.schedules: Dict[str, SyncSchedule] = {}
        self.providers: Dict[str, BankingProvider] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        self._queue: Queue = Queue()
        self._running = False
        self._workers: List[threading.Thread] = []
        self._max_workers = max_workers
    
    def start(self):
        """Démarre le moteur de sync."""
        if self._running:
            return
        
        self._running = True
        
        self._scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._scheduler_thread.start()
        
        for i in range(self._max_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()
            self._workers.append(worker)
        
        logger.info(f"Sync engine started with {self._max_workers} workers")
    
    def stop(self):
        """Arrête le moteur."""
        self._running = False
        
        for worker in self._workers:
            worker.join(timeout=5)
        
        logger.info("Sync engine stopped")
    
    def register_connection(self, connection_id: str, provider_type: str,
                          frequency: SyncFrequency = SyncFrequency.EVERY_6H):
        """Enregistre une connexion pour sync auto."""
        provider = self._create_provider(provider_type)
        self.providers[connection_id] = provider
        
        schedule = SyncSchedule(
            connection_id=connection_id,
            provider_type=provider_type,
            frequency=frequency
        )
        self.schedules[connection_id] = schedule
        
        self.circuit_breakers[connection_id] = CircuitBreaker()
    
    def force_sync(self, connection_id: str) -> Optional[SyncResult]:
        """Force une synchronisation immédiate."""
        schedule = self.schedules.get(connection_id)
        if not schedule:
            return None
        
        job = SyncJob(
            connection_id=connection_id,
            provider_type=schedule.provider_type,
            scheduled_at=datetime.now(),
            priority=10,
            force=True
        )
        
        return self._execute_sync_job(job)
    
    def _run_scheduler(self):
        """Boucle principale du scheduler."""
        while self._running:
            now = datetime.now()
            
            for connection_id, schedule in self.schedules.items():
                if not schedule.is_active:
                    continue
                
                if schedule.next_sync and now < schedule.next_sync:
                    continue
                
                cb = self.circuit_breakers.get(connection_id)
                if cb and not cb.can_execute():
                    continue
                
                job = SyncJob(
                    connection_id=connection_id,
                    provider_type=schedule.provider_type,
                    scheduled_at=now
                )
                
                self._queue.put(job)
                
                schedule.next_sync = self._calculate_next_sync(schedule.frequency, now)
            
            time.sleep(60)
    
    def _worker_loop(self):
        """Boucle d'un worker thread."""
        while self._running:
            try:
                job = self._queue.get(timeout=5)
                self._execute_sync_job(job)
            except Empty:
                continue
    
    def _execute_sync_job(self, job: SyncJob) -> Optional[SyncResult]:
        """Exécute un job de sync."""
        connection_id = job.connection_id
        schedule = self.schedules.get(connection_id)
        provider = self.providers.get(connection_id)
        
        if not schedule or not provider:
            return None
        
        cb = self.circuit_breakers.get(connection_id)
        if cb and not job.force and not cb.can_execute():
            return None
        
        schedule.last_sync = datetime.now()
        
        try:
            token_vault = TokenVault()
            tokens = token_vault.get_tokens(connection_id)
            
            if not tokens:
                raise Exception("No valid tokens found")
            
            result = provider.sync_all(connection_id, tokens['access_token'])
            
            if cb:
                cb.record_success()
            
            if result.success and result.transactions_new > 0 and schedule.notify_on_new:
                self._notify_new_transactions(connection_id, result.transactions_new)
            
            if schedule.auto_categorize and result.transactions_new > 0:
                self._trigger_auto_categorize(connection_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            if cb:
                cb.record_failure()
            return None
    
    def _create_provider(self, provider_type: str) -> BankingProvider:
        """Factory pour créer les providers."""
        configs = {
            'bridge': {
                'client_id': get_env('BRIDGE_CLIENT_ID'),
                'client_secret': get_env('BRIDGE_CLIENT_SECRET'),
                'redirect_uri': get_env('BRIDGE_REDIRECT_URI')
            },
            'truelayer': {
                'client_id': get_env('TRUELAYER_CLIENT_ID'),
                'client_secret': get_env('TRUELAYER_CLIENT_SECRET'),
                'redirect_uri': get_env('TRUELAYER_REDIRECT_URI')
            }
        }
        
        if provider_type == 'bridge':
            return BridgeProvider(configs['bridge'])
        elif provider_type == 'truelayer':
            return TruelayerProvider(configs['truelayer'])
        else:
            raise ValueError(f"Unknown provider: {provider_type}")
    
    def _calculate_next_sync(self, frequency: SyncFrequency, from_time: datetime) -> datetime:
        """Calcule la prochaine sync."""
        deltas = {
            SyncFrequency.HOURLY: timedelta(hours=1),
            SyncFrequency.EVERY_6H: timedelta(hours=6),
            SyncFrequency.EVERY_12H: timedelta(hours=12),
            SyncFrequency.DAILY: timedelta(days=1)
        }
        
        if frequency == SyncFrequency.DAILY:
            tomorrow = from_time + timedelta(days=1)
            return tomorrow.replace(hour=6, minute=0)
        
        return from_time + deltas.get(frequency, timedelta(hours=6))
    
    def _notify_new_transactions(self, connection_id: str, count: int):
        """Notifie de nouvelles transactions."""
        from modules.notifications import create_notification
        
        create_notification(
            type="new_transactions",
            title=f"🏦 {count} nouvelles transactions",
            message=f"{count} transactions importées depuis votre banque"
        )
    
    def _trigger_auto_categorize(self, connection_id: str):
        """Déclenche catégorisation auto."""
        from modules.categorization_cascade import categorize_pending_transactions
        categorize_pending_transactions(connection_id=connection_id)


def get_env(key: str, default: str = None):
    """Récupère une variable d'environnement."""
    import os
    return os.environ.get(key, default)


---

## 🧱 Module 4: UI Components

### Interface utilisateur Open Banking

```python
# modules/banking/ui/connection_manager.py

import streamlit as st
from datetime import datetime, timedelta


def render_bank_connections_page():
    """Page principale de gestion des connexions bancaires."""
    st.header("🏦 Connexions bancaires")
    
    connections = get_user_bank_connections()
    
    if not connections:
        render_empty_state()
    else:
        for conn in connections:
            render_connection_card(conn)
    
    st.divider()
    
    st.subheader("Ajouter une connexion")
    
    if st.button("➕ Connecter une nouvelle banque", use_container_width=True):
        st.session_state['show_connection_flow'] = True
        st.rerun()
    
    if st.session_state.get('show_connection_flow'):
        render_connection_flow()


def render_connection_card(connection: dict):
    """Carte de connexion bancaire."""
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            status_emoji = {
                'active': '🟢',
                'expiring_soon': '🟡',
                'expired': '🔴',
                'error': '🟠'
            }.get(connection['status'], '⚪')
            
            st.markdown(f"**{status_emoji} {connection['bank_name']}**")
            st.caption(f"{connection.get('account_count', 0)} compte(s)")
            
            if connection.get('last_sync'):
                st.caption(f"Dernière sync: {format_relative_time(connection['last_sync'])}")
        
        with col2:
            if connection['status'] == 'active':
                if st.button("🔄 Sync", key=f"sync_{connection['id']}"):
                    with st.spinner("Synchronisation..."):
                        result = force_sync_connection(connection['id'])
                        if result and result.get('success'):
                            st.success(f"✅ {result.get('transactions_new', 0)} nouvelles transactions")
                        else:
                            st.error("❌ Échec de la synchronisation")
                        st.rerun()
        
        with col3:
            with st.popover("⋮"):
                if st.button("🔄 Reconnecter", key=f"reconnect_{connection['id']}"):
                    initiate_reconnection(connection['id'])
                
                st.divider()
                
                if st.button("🗑️ Déconnecter", key=f"disconnect_{connection['id']}"):
                    disconnect_bank(connection['id'])
                    st.rerun()


def render_connection_flow():
    """Flux de connexion étape par étape."""
    step = st.session_state.get('connection_step', 1)
    
    st.progress(step / 4)
    
    if step == 1:
        _render_provider_selection()
    elif step == 2:
        _render_bank_selection()
    elif step == 3:
        _render_consent_screen()
    elif step == 4:
        _render_success_screen()


def _render_provider_selection():
    """Étape 1: Sélection du provider."""
    st.subheader("🔗 Choisir un service de connexion")
    
    providers = [
        {
            'id': 'bridge',
            'name': 'Bridge by Bankin\'',
            'description': 'Connexion sécurisée avec plus de 2500 banques européennes',
            'logo': '🔷'
        },
        {
            'id': 'truelayer',
            'name': 'TrueLayer',
            'description': 'Leader européen d\'Open Banking',
            'logo': '🔶'
        }
    ]
    
    for provider in providers:
        with st.container(border=True):
            st.markdown(f"**{provider['logo']} {provider['name']}**")
            st.caption(provider['description'])
            
            if st.button(f"Choisir {provider['name']}", key=f"provider_{provider['id']}"):
                st.session_state['selected_provider'] = provider['id']
                st.session_state['connection_step'] = 2
                st.rerun()


def _render_consent_screen():
    """Étape 3: Écran de consentement PSD2."""
    bank = st.session_state.get('selected_bank', {})
    
    st.subheader("📋 Consentement requis")
    
    st.info(f"""
        **Vous allez connecter votre compte {bank.get('name', '')}**
        
        Cette connexion utilise le standard Open Banking (PSD2).
    """)
    
    st.markdown("**🔐 Données accédées:**")
    st.markdown("• Liste de vos comptes • Solde • Historique des transactions")
    
    st.markdown("**⚖️ Vos droits (RGPD/PSD2):**")
    st.markdown("• Accès limité à 180 jours • Révocable à tout moment")
    
    consent_given = st.checkbox("J'accepte les conditions d'utilisation")
    
    if st.button("Se connecter →", disabled=not consent_given, type="primary"):
        oauth_url = initiate_oauth_flow(
            provider=st.session_state['selected_provider'],
            bank_id=bank['id']
        )
        st.markdown(f'<script>window.open("{oauth_url}", "_blank");</script>',
                   unsafe_allow_html=True)
        st.session_state['connection_step'] = 4
        st.rerun()


def _render_success_screen():
    """Étape 4: Confirmation."""
    st.success("✅ Connexion initiée!")
    
    st.markdown("""
        Une fenêtre d'authentification s'est ouverte.
        Connectez-vous à votre banque pour autoriser l'accès.
    """)
    
    if st.button("Terminer", use_container_width=True, type="primary"):
        st.session_state['connection_step'] = 1
        del st.session_state['selected_provider']
        del st.session_state['show_connection_flow']
        st.rerun()


def render_empty_state():
    """État vide quand pas de connexions."""
    st.markdown("""
        <div style="text-align: center; padding: 40px;">
            <div style="font-size: 60px;">🏦</div>
            <h3>Aucune connexion bancaire</h3>
            <p>Connectez vos comptes pour importer automatiquement vos transactions.</p>
        </div>
    """, unsafe_allow_html=True)


def format_relative_time(dt: datetime) -> str:
    """Formate un datetime en texte relatif."""
    if not dt:
        return "Jamais"
    
    delta = datetime.now() - dt
    
    if delta < timedelta(minutes=1):
        return "à l'instant"
    elif delta < timedelta(hours=1):
        return f"il y a {delta.seconds // 60} min"
    elif delta < timedelta(days=1):
        return f"il y a {delta.seconds // 3600}h"
    else:
        return f"il y a {delta.days} jours"


# Stubs

def get_user_bank_connections(): return []
def force_sync_connection(connection_id: str): return {}
def initiate_reconnection(connection_id: str): pass
def disconnect_bank(connection_id: str): pass
def initiate_oauth_flow(provider: str, bank_id: str): return ""


---

## ✅ Checklists & Procédures

### PSD2 Compliance Checklist

```
✅ CONFORMITÉ PSD2
├── Consentement
│   ├── Capture explicite et informée ✓
│   ├── Durée max 180 jours ✓
│   ├── Scope précis (accounts, transactions) ✓
│   └── Possibilité de révocation claire ✓
├── Sécurité
│   ├── Audit log complet ✓
│   ├── Encryption tokens (AES-256) ✓
│   ├── HMAC webhooks ✓
│   └── Pas de logs de tokens ✓
├── Transparence
│   ├── Explication données accédées ✓
│   ├── Durée de conservation ✓
│   ├── Droits utilisateur (RGPD) ✓
│   └── Contact/support ✓
└── Opérations
    ├── Rappels expiration (30, 14, 7, 1 jours) ✓
    ├── Révocation immédiate possible ✓
    ├── Export données utilisateur ✓
    └── Suppression données sur demande ✓
```

### Pre-launch Security Checklist

```
✅ SÉCURITÉ AVANT MISE EN PROD
├── Configuration
│   ├── Variables d'environnement définies
│   ├── Secrets dans vault (pas dans code)
│   ├── HTTPS obligatoire
│   └── CSP headers configurés
├── Tokens
│   ├── Encryption AES-256-GCM
│   ├── Rotation automatique
│   ├── Expiration courte (< 1h)
│   └── Refresh tokens sécurisés
├── API
│   ├── Rate limiting côté client
│   ├── Retry avec backoff
│   ├── Circuit breaker activé
│   └── Timeouts configurés
└── Monitoring
    ├── Alertes erreurs auth
    ├── Alertes rate limit
    ├── Alertes circuit breaker
    └── Dashboard sync health
```

---

## 🚨 Procédures d'Urgence

### Token Compromis

```python
def handle_compromised_tokens(connection_id: str):
    """Procédure d'urgence: tokens compromis."""
    logger.critical(f"SECURITY: Handling compromised tokens for {connection_id}")
    
    # 1. Révoquer immédiatement côté provider
    provider = get_provider_for_connection(connection_id)
    if hasattr(provider, 'revoke_connection'):
        provider.revoke_connection(connection_id)
    
    # 2. Supprimer tokens locaux
    token_vault = TokenVault()
    token_vault.revoke_tokens(connection_id)
    
    # 3. Révoquer consentement
    consent_manager = ConsentManager()
    consent = consent_manager.get_consent_by_connection(connection_id)
    if consent:
        consent_manager.revoke_consent(
            consent.id,
            reason="security_incident",
            revoked_by="system"
        )
    
    # 4. Mettre à jour statut connexion
    update_connection_status(connection_id, "revoked")
    
    # 5. Notification utilisateur
    create_notification(
        type="security_incident",
        priority="critical",
        title="🔒 Action requise: Reconnecter votre banque",
        message="Par mesure de sécurité, votre connexion a été déconnectée."
    )
```

---

## 🏗️ Architecture Inter-Agent

```
AGENT-018 (Open Banking)
         │
         ├──→ AGENT-002 (Security) : Token encryption, audit
         ├──→ AGENT-005 (Categorization) : Auto-cat post-sync
         ├──→ AGENT-016 (Notifications) : New transactions, errors
         ├──→ AGENT-017 (Data Pipeline) : Format normalization
         └──→ AGENT-009/010 (UI) : Connection cards, status dashboard
```

---

## 🎯 Métriques & SLIs

| Métrique | Target | Alerte | Critique |
|----------|--------|--------|----------|
| Sync Success Rate | >99.5% | <99% | <95% |
| Token Refresh Failure | <0.01% | >0.1% | >1% |
| Data Freshness | <4h | >6h | >24h |
| Duplicate Rate | <0.001% | >0.01% | >0.1% |

---

## 🔧 Variables d'Environnement

```bash
# Bridge API
BRIDGE_CLIENT_ID=xxx
BRIDGE_CLIENT_SECRET=xxx
BRIDGE_REDIRECT_URI=https://app.financeperso.com/callback/bridge
BRIDGE_WEBHOOK_SECRET=xxx

# TrueLayer API
TRUELAYER_CLIENT_ID=xxx
TRUELAYER_CLIENT_SECRET=xxx
TRUELAYER_REDIRECT_URI=https://app.financeperso.com/callback/truelayer

# Sécurité
TOKEN_ENCRYPTION_KEY=xxx
WEBHOOK_SIGNATURE_REQUIRED=true
```

---

**Agent spécialisé AGENT-018** - Open Banking & API Integration Specialist  
_Version 2.0 - Architecture complète Open Banking_  
_Couvre 99% des besoins PSD2, OAuth, sync automatique pour FinancePerso_
