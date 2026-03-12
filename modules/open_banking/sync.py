"""Synchronisation automatique des comptes bancaires."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from modules.db.connection import get_db_connection
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
    """Résultat d'une synchronisation."""
    connection_id: str
    status: SyncStatus
    transactions_imported: int = 0
    transactions_duplicated: int = 0
    errors: list[str] = None
    started_at: datetime = None
    completed_at: datetime = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class BankSyncManager:
    """Gestionnaire de synchronisation bancaire."""
    
    def __init__(self):
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Crée les tables nécessaires."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Table des synchronisations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bank_syncs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    connection_id TEXT NOT NULL,
                    account_id TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    transactions_imported INTEGER DEFAULT 0,
                    transactions_duplicated INTEGER DEFAULT 0,
                    errors TEXT,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)
            
            # Table pour suivre les IDs externes (éviter doublons)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bank_transaction_ids (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    external_id TEXT UNIQUE NOT NULL,
                    transaction_id INTEGER,
                    account_id TEXT NOT NULL,
                    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def sync_account(
        self,
        client,
        account_id: str,
        days_back: int = 90
    ) -> SyncResult:
        """Synchronise un compte bancaire."""
        result = SyncResult(
            connection_id=account_id,
            status=SyncStatus.RUNNING,
            started_at=datetime.now()
        )
        
        try:
            # Récupérer les transactions
            date_from = datetime.now() - timedelta(days=days_back)
            transactions = client.get_transactions(account_id, date_from=date_from)
            
            logger.info(f"Récupéré {len(transactions)} transactions pour {account_id}")
            
            # Importer chaque transaction
            imported = 0
            duplicated = 0
            
            for tx in transactions:
                try:
                    if self._is_duplicate(tx.get('id'), account_id):
                        duplicated += 1
                        continue
                    
                    self._import_transaction(tx, account_id)
                    imported += 1
                    
                except Exception as e:
                    result.errors.append(f"Erreur import {tx.get('id')}: {e}")
            
            result.transactions_imported = imported
            result.transactions_duplicated = duplicated
            result.status = SyncStatus.SUCCESS if not result.errors else SyncStatus.PARTIAL
            
        except Exception as e:
            logger.error(f"Erreur synchronisation {account_id}: {e}")
            result.status = SyncStatus.ERROR
            result.errors.append(str(e))
        
        result.completed_at = datetime.now()
        self._save_sync_result(result)
        
        return result
    
    def _is_duplicate(self, external_id: str, account_id: str) -> bool:
        """Vérifie si une transaction existe déjà."""
        if not external_id:
            return False
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM bank_transaction_ids WHERE external_id = ? AND account_id = ?",
                (external_id, account_id)
            )
            return cursor.fetchone() is not None
    
    def _import_transaction(self, tx: dict, account_id: str):
        """Importe une transaction dans la base locale."""
        from modules.categorization import categorize_transaction
        from modules.db.transactions import add_transaction
        
        # Préparer les données
        amount = tx.get('amount', 0)
        
        # Créer une transaction hash unique
        tx_hash = self._generate_tx_hash(tx)
        
        # Catégoriser automatiquement
        category = categorize_transaction({
            'label': tx.get('description', ''),
            'amount': amount
        })
        
        # Ajouter à la base
        transaction_id = add_transaction(
            date=tx.get('date', datetime.now().strftime('%Y-%m-%d')),
            label=tx.get('description', 'Import bancaire'),
            amount=amount,
            category=category,
            account_id=account_id,
            beneficiary=tx.get('counterparty', ''),
            notes=f"Import auto - ID: {tx.get('id', 'N/A')}",
            tx_hash=tx_hash
        )
        
        # Enregistrer l'ID externe
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO bank_transaction_ids (external_id, transaction_id, account_id)
                VALUES (?, ?, ?)
                """,
                (tx.get('id'), transaction_id, account_id)
            )
            conn.commit()
    
    def _generate_tx_hash(self, tx: dict) -> str:
        """Génère un hash unique pour une transaction."""
        import hashlib
        
        data = f"{tx.get('id')}{tx.get('date')}{tx.get('amount')}{tx.get('description')}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def _save_sync_result(self, result: SyncResult):
        """Sauvegarde le résultat de synchronisation."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO bank_syncs 
                (connection_id, account_id, status, transactions_imported, 
                 transactions_duplicated, errors, started_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.connection_id,
                    result.connection_id,
                    result.status.value,
                    result.transactions_imported,
                    result.transactions_duplicated,
                    '\n'.join(result.errors) if result.errors else None,
                    result.started_at.isoformat() if result.started_at else None,
                    result.completed_at.isoformat() if result.completed_at else None
                )
            )
            conn.commit()
    
    def get_sync_history(self, account_id: str = None, limit: int = 50) -> list[dict]:
        """Récupère l'historique des synchronisations."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if account_id:
                cursor.execute(
                    """
                    SELECT * FROM bank_syncs
                    WHERE account_id = ?
                    ORDER BY started_at DESC
                    LIMIT ?
                    """,
                    (account_id, limit)
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM bank_syncs
                    ORDER BY started_at DESC
                    LIMIT ?
                    """,
                    (limit,)
                )
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def schedule_auto_sync(self, connection_id: str, frequency: str = "daily"):
        """Planifie une synchronisation automatique.
        
        Args:
            frequency: 'hourly', 'daily', 'weekly'
        """
        # Note: Pour une vraie planification, il faudrait utiliser
        # un scheduler comme APScheduler ou un cron job
        logger.info(f"Synchronisation auto planifiée: {connection_id} ({frequency})")
        
        # Pour l'instant, on enregistre juste la préférence
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bank_sync_schedules (
                    connection_id TEXT PRIMARY KEY,
                    frequency TEXT,
                    next_sync TIMESTAMP,
                    enabled INTEGER DEFAULT 1
                )
            """)
            
            # Calculer la prochaine exécution
            next_sync = datetime.now()
            if frequency == "hourly":
                next_sync += timedelta(hours=1)
            elif frequency == "daily":
                next_sync += timedelta(days=1)
            elif frequency == "weekly":
                next_sync += timedelta(weeks=1)
            
            cursor.execute(
                """
                INSERT OR REPLACE INTO bank_sync_schedules 
                (connection_id, frequency, next_sync)
                VALUES (?, ?, ?)
                """,
                (connection_id, frequency, next_sync.isoformat())
            )
            conn.commit()
    
    def run_scheduled_syncs(self, client):
        """Exécute les synchronisations planifiées."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT connection_id, frequency FROM bank_sync_schedules
                WHERE enabled = 1 AND next_sync <= ?
                """,
                (datetime.now().isoformat(),)
            )
            
            due_syncs = cursor.fetchall()
        
        for connection_id, frequency in due_syncs:
            logger.info(f"Exécution sync planifiée: {connection_id}")
            
            # Récupérer les comptes associés
            accounts = self._get_connection_accounts(connection_id)
            
            for account_id in accounts:
                self.sync_account(client, account_id)
            
            # Mettre à jour la prochaine exécution
            self.schedule_auto_sync(connection_id, frequency)
    
    def _get_connection_accounts(self, connection_id: str) -> list[str]:
        """Récupère les comptes d'une connexion."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT account_ids FROM bank_connections WHERE id = ?",
                (connection_id,)
            )
            row = cursor.fetchone()
            if row and row[0]:
                return row[0].split(',')
            return []


class OpenBankingUI:
    """Interface UI pour l'Open Banking."""
    
    def __init__(self):
        from .client import ConnectionManager
        self.manager = ConnectionManager()
        self.sync_manager = BankSyncManager()
    
    def render_bank_connection_flow(self):
        """Rend le flux de connexion bancaire."""
        import streamlit as st

        from .client import OpenBankingClient
        
        st.subheader("🏦 Connexion bancaire")
        
        # Sélection du provider
        provider = st.selectbox(
            "Provider",
            options=[
                ("mock", "🧪 Mode Test"),
                ("gocardless", "💳 GoCardless (Nordigen)"),
                ("bridge", "🏛️ Bridge")
            ],
            format_func=lambda x: x[1]
        )[0]
        
        # Sélection de la banque
        if st.button("Lister les banques disponibles"):
            with st.spinner("Chargement..."):
                try:
                    client = OpenBankingClient(provider)
                    banks = client.get_available_banks()
                    
                    if banks:
                        st.session_state['available_banks'] = banks
                    else:
                        st.error("Aucune banque trouvée. Vérifiez vos credentials.")
                except Exception as e:
                    st.error(f"Erreur: {e}")
        
        if 'available_banks' in st.session_state:
            bank = st.selectbox(
                "Sélectionnez votre banque",
                options=st.session_state['available_banks'],
                format_func=lambda x: f"{x.get('name', 'Banque')}"
            )
            
            if st.button("Se connecter", type="primary"):
                with st.spinner("Création de la connexion..."):
                    try:
                        client = OpenBankingClient(provider)
                        result = client.create_connection(
                            bank_id=bank['id'],
                            redirect_url="http://localhost:8501/callback"
                        )
                        
                        st.success("Connexion créée!")
                        st.markdown(f"""
                        <a href="{result['auth_url']}" target="_blank" style="
                            display: inline-block;
                            padding: 0.75rem 1.5rem;
                            background: #10B981;
                            color: white;
                            text-decoration: none;
                            border-radius: 8px;
                            font-weight: 500;
                        ">🔐 Autoriser l'accès bancaire</a>
                        """, unsafe_allow_html=True)
                        
                        st.info(f"ID de connexion: `{result['connection_id']}`")
                        
                    except Exception as e:
                        st.error(f"Erreur: {e}")
    
    def render_sync_status(self):
        """Rend le statut des synchronisations."""
        import streamlit as st
        
        st.subheader("🔄 Synchronisations")
        
        history = self.sync_manager.get_sync_history(limit=20)
        
        if not history:
            st.info("Aucune synchronisation enregistrée.")
            return
        
        for sync in history:
            status_emoji = {
                "success": "✅",
                "error": "❌",
                "partial": "⚠️",
                "running": "⏳"
            }.get(sync['status'], "❓")
            
            with st.expander(
                f"{status_emoji} {sync['account_id'][:20]}... - "
                f"{sync['started_at'][:16] if sync['started_at'] else 'N/A'}"
            ):
                cols = st.columns(3)
                with cols[0]:
                    st.metric("Importées", sync['transactions_imported'])
                with cols[1]:
                    st.metric("Doublons", sync['transactions_duplicated'])
                with cols[2]:
                    st.metric("Statut", sync['status'])
                
                if sync['errors']:
                    st.error("Erreurs:")
                    st.code(sync['errors'])
    
    def render_connected_banks(self):
        """Rend la liste des banques connectées."""
        import streamlit as st

        from .client import OpenBankingClient
        
        st.subheader("🔌 Banques connectées")
        
        connections = self.manager.get_active_connections()
        
        if not connections:
            st.info("Aucune banque connectée.")
            return
        
        for conn in connections:
            with st.container():
                cols = st.columns([3, 1, 1])
                
                with cols[0]:
                    st.markdown(f"**{conn.bank_name}**")
                    st.caption(f"Statut: {conn.status.value}")
                    if conn.last_sync:
                        st.caption(f"Dernière sync: {conn.last_sync.strftime('%d/%m %H:%M')}")
                
                with cols[1]:
                    if st.button("🔄 Sync", key=f"sync_{conn.id}"):
                        with st.spinner("Synchronisation..."):
                            client = OpenBankingClient(conn.provider)
                            for account_id in conn.account_ids:
                                result = self.sync_manager.sync_account(
                                    client, account_id
                                )
                                st.success(
                                    f"{result.transactions_imported} transactions importées"
                                )
                            self.manager.update_sync_time(conn.id)
                            st.rerun()
                
                with cols[2]:
                    if st.button("❌ Déconnecter", key=f"disconnect_{conn.id}"):
                        # TODO: Implémenter la déconnexion
                        st.warning("Fonctionnalité à venir")


# Instance globale
bank_sync_manager = BankSyncManager()
