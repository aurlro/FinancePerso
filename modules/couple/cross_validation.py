"""Workflow de validation croisée - Phase 7.

Système de double validation pour les transactions importantes.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import streamlit as st

from modules.db.connection import get_db_connection
from modules.logger import logger


class ValidationStatus(Enum):
    """Statuts de validation."""
    PENDING = "pending"
    FIRST_APPROVED = "first_approved"
    FULLY_APPROVED = "fully_approved"
    REJECTED = "rejected"


@dataclass
class ValidationRequest:
    """Demande de validation."""
    id: int
    transaction_id: int
    requested_by: str
    validator_id: str
    status: ValidationStatus
    requested_at: datetime
    validated_at: datetime | None = None
    notes: str = ""
    transaction_amount: float = 0.0
    transaction_label: str = ""


class CrossValidationManager:
    """Gestionnaire de validation croisée."""
    
    THRESHOLD_AMOUNT = 500.0  # Seuil pour validation obligatoire
    
    def __init__(self):
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Crée les tables nécessaires."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cross_validation_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id INTEGER NOT NULL,
                    requested_by TEXT NOT NULL,
                    validator_id TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    validated_at TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
                )
            """)
            conn.commit()
    
    def request_validation(
        self,
        transaction_id: int,
        requested_by: str,
        validator_id: str,
        notes: str = ""
    ) -> ValidationRequest:
        """Crée une demande de validation."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO cross_validation_requests 
                (transaction_id, requested_by, validator_id, notes)
                VALUES (?, ?, ?, ?)
                """,
                (transaction_id, requested_by, validator_id, notes)
            )
            conn.commit()
            
            logger.info(
                f"Validation demandée tx={transaction_id} "
                f"par={requested_by} validateur={validator_id}"
            )
            
            return ValidationRequest(
                id=cursor.lastrowid,
                transaction_id=transaction_id,
                requested_by=requested_by,
                validator_id=validator_id,
                status=ValidationStatus.PENDING,
                requested_at=datetime.now(),
                notes=notes
            )
    
    def approve_validation(
        self,
        validation_id: int,
        validator_id: str
    ) -> bool:
        """Approuve une demande de validation."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE cross_validation_requests
                SET status = 'fully_approved', validated_at = ?
                WHERE id = ? AND validator_id = ?
                """,
                (datetime.now().isoformat(), validation_id, validator_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def reject_validation(
        self,
        validation_id: int,
        validator_id: str,
        reason: str = ""
    ) -> bool:
        """Rejette une demande de validation."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE cross_validation_requests
                SET status = 'rejected', notes = ?, validated_at = ?
                WHERE id = ? AND validator_id = ?
                """,
                (reason, datetime.now().isoformat(), validation_id, validator_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def get_pending_validations(self, validator_id: str) -> list[ValidationRequest]:
        """Récupère les validations en attente pour un utilisateur."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT v.*, t.amount, t.label
                FROM cross_validation_requests v
                JOIN transactions t ON v.transaction_id = t.id
                WHERE v.validator_id = ? AND v.status = 'pending'
                ORDER BY v.requested_at DESC
                """,
                (validator_id,)
            )
            
            validations = []
            for row in cursor.fetchall():
                validations.append(ValidationRequest(
                    id=row[0],
                    transaction_id=row[1],
                    requested_by=row[2],
                    validator_id=row[3],
                    status=ValidationStatus(row[4]),
                    requested_at=datetime.fromisoformat(row[5]),
                    validated_at=datetime.fromisoformat(row[6]) if row[6] else None,
                    notes=row[7],
                    transaction_amount=row[8] if len(row) > 8 else 0,
                    transaction_label=row[9] if len(row) > 9 else ""
                ))
            
            return validations
    
    def get_validation_history(
        self,
        user_id: str,
        limit: int = 50
    ) -> list[ValidationRequest]:
        """Récupère l'historique des validations."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT v.*, t.amount, t.label
                FROM cross_validation_requests v
                JOIN transactions t ON v.transaction_id = t.id
                WHERE v.requested_by = ? OR v.validator_id = ?
                ORDER BY v.requested_at DESC
                LIMIT ?
                """,
                (user_id, user_id, limit)
            )
            
            validations = []
            for row in cursor.fetchall():
                validations.append(ValidationRequest(
                    id=row[0],
                    transaction_id=row[1],
                    requested_by=row[2],
                    validator_id=row[3],
                    status=ValidationStatus(row[4]) if row[4] else ValidationStatus.PENDING,
                    requested_at=datetime.fromisoformat(row[5]) if row[5] else datetime.now(),
                    validated_at=datetime.fromisoformat(row[6]) if row[6] else None,
                    notes=row[7] if len(row) > 7 else "",
                    transaction_amount=row[8] if len(row) > 8 else 0,
                    transaction_label=row[9] if len(row) > 9 else ""
                ))
            
            return validations
    
    def needs_cross_validation(self, amount: float) -> bool:
        """Vérifie si une transaction nécessite validation croisée."""
        return abs(amount) >= self.THRESHOLD_AMOUNT


class CrossValidationUI:
    """Interface UI pour la validation croisée."""
    
    def __init__(self):
        self.manager = CrossValidationManager()
    
    def render_validation_button(
        self,
        transaction_id: int,
        amount: float,
        current_user: str,
        other_user: str,
        other_user_name: str
    ):
        """Rend le bouton de demande de validation."""
        if not self.manager.needs_cross_validation(amount):
            return
        
        st.warning(f"⚠️ Cette transaction ({amount:.2f}€) dépasse le seuil de validation croisée.")
        
        if st.button(
            f"🔒 Demander validation à {other_user_name}",
            type="primary",
            key=f"val_btn_{transaction_id}"
        ):
            self.manager.request_validation(
                transaction_id=transaction_id,
                requested_by=current_user,
                validator_id=other_user
            )
            st.success(f"Demande de validation envoyée à {other_user_name}!")
            st.rerun()
    
    def render_pending_validations_panel(self, current_user: str):
        """Rend le panneau des validations en attente."""
        st.subheader("🔔 Validations en attente")
        
        pending = self.manager.get_pending_validations(current_user)
        
        if not pending:
            st.info("Aucune validation en attente.")
            return
        
        for val in pending:
            with st.container():
                cols = st.columns([3, 1, 1])
                
                with cols[0]:
                    st.markdown(f"""
                    **{val.transaction_label}**  
                    <span style="color: #EF4444; font-weight: bold;">{val.transaction_amount:.2f}€</span>  
                    <small>Demandé par {val.requested_by} - {val.requested_at.strftime('%d/%m %H:%M')}</small>
                    """, unsafe_allow_html=True)
                
                with cols[1]:
                    if st.button("✅ Valider", key=f"approve_{val.id}"):
                        self.manager.approve_validation(val.id, current_user)
                        st.success("Validé!")
                        st.rerun()
                
                with cols[2]:
                    if st.button("❌ Refuser", key=f"reject_{val.id}"):
                        st.session_state[f"rejecting_{val.id}"] = True
                        st.rerun()
                
                if st.session_state.get(f"rejecting_{val.id}", False):
                    with st.form(key=f"reject_form_{val.id}"):
                        reason = st.text_area("Motif du refus", key=f"reason_{val.id}")
                        if st.form_submit_button("Confirmer le refus"):
                            self.manager.reject_validation(val.id, current_user, reason)
                            del st.session_state[f"rejecting_{val.id}"]
                            st.rerun()
                
                st.divider()
    
    def render_validation_history(self, current_user: str, limit: int = 20):
        """Rend l'historique des validations."""
        st.subheader("📜 Historique des validations")
        
        history = self.manager.get_validation_history(current_user, limit)
        
        if not history:
            st.info("Aucun historique.")
            return
        
        # Tableau récapitulatif
        data = []
        for val in history:
            data.append({
                "Date": val.requested_at.strftime("%d/%m/%Y"),
                "Transaction": (val.transaction_label[:30] + "..." 
                               if len(val.transaction_label) > 30 
                               else val.transaction_label),
                "Montant": f"{val.transaction_amount:.2f}€",
                "Demandé par": val.requested_by,
                "Statut": val.status.value,
            })
        
        st.dataframe(data, use_container_width=True)


# Instance globale
cross_validation_manager = CrossValidationManager()
