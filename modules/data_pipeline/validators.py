"""
Validateurs pour le pipeline d'import.
"""

import sqlite3
from typing import List, Dict, Optional, Set
from dataclasses import dataclass

from modules.db.connection import get_db_connection


@dataclass
class ValidationError:
    """Erreur de validation."""
    field: str
    message: str
    value: any


class SchemaValidator:
    """
    Valide le schéma des données d'import.
    """
    
    REQUIRED_FIELDS = ['date', 'label', 'amount']
    
    def __init__(self):
        self.errors: List[ValidationError] = []
    
    def validate_record(self, record: Dict) -> bool:
        """
        Valide un record individuel.
        
        Args:
            record: Dictionnaire à valider
            
        Returns:
            True si valide, False sinon
        """
        self.errors = []
        
        # Vérifier champs requis
        for field in self.REQUIRED_FIELDS:
            if field not in record or not record[field]:
                self.errors.append(ValidationError(
                    field=field,
                    message=f"Champ requis manquant: {field}",
                    value=None
                ))
        
        # Valider types
        if 'amount' in record:
            try:
                float(record['amount'])
            except (ValueError, TypeError):
                self.errors.append(ValidationError(
                    field='amount',
                    message="Montant doit être un nombre",
                    value=record.get('amount')
                ))
        
        if 'date' in record:
            date_str = str(record['date'])
            # Format ISO simple
            if len(date_str) != 10 or date_str[4] != '-' or date_str[7] != '-':
                self.errors.append(ValidationError(
                    field='date',
                    message="Date doit être au format YYYY-MM-DD",
                    value=record.get('date')
                ))
        
        return len(self.errors) == 0
    
    def validate_batch(self, records: List[Dict]) -> Dict:
        """
        Valide un batch de records.
        
        Returns:
            Statistiques de validation
        """
        valid_count = 0
        invalid_count = 0
        all_errors = []
        
        for i, record in enumerate(records):
            if self.validate_record(record):
                valid_count += 1
            else:
                invalid_count += 1
                for error in self.errors:
                    all_errors.append({
                        'record_index': i,
                        **error.__dict__
                    })
        
        return {
            'total': len(records),
            'valid': valid_count,
            'invalid': invalid_count,
            'errors': all_errors
        }


class DuplicateDetector:
    """
    Détecte les doublons de transactions.
    """
    
    def __init__(self):
        self.seen_hashes: Set[str] = set()
    
    def is_duplicate(self, tx_hash: str) -> bool:
        """
        Vérifie si un hash a déjà été vu.
        
        Args:
            tx_hash: Hash de transaction
            
        Returns:
            True si doublon
        """
        if tx_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(tx_hash)
        return False
    
    def check_database_duplicate(self, tx_hash: str) -> bool:
        """
        Vérifie si une transaction existe déjà en base.
        
        Args:
            tx_hash: Hash à vérifier
            
        Returns:
            True si existe en base
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT 1 FROM transactions WHERE tx_hash = ? LIMIT 1",
                    (tx_hash,)
                )
                return cursor.fetchone() is not None
        except sqlite3.Error:
            # En cas d'erreur DB, on permet l'import
            # Le check sera refait lors de l'insertion
            return False
    
    def find_duplicates_in_batch(self, records: List[Dict]) -> List[int]:
        """
        Trouve les indices des doublons dans un batch.
        
        Args:
            records: Liste de records avec 'tx_hash'
            
        Returns:
            Indices des doublons
        """
        seen = set()
        duplicates = []
        
        for i, record in enumerate(records):
            tx_hash = record.get('tx_hash')
            if tx_hash:
                if tx_hash in seen:
                    duplicates.append(i)
                else:
                    seen.add(tx_hash)
        
        return duplicates
    
    def reset(self):
        """Réinitialise le cache de doublons."""
        self.seen_hashes.clear()
