"""
Service de catégorisation des transactions.
==========================================

Ce module fournit une interface de haut niveau pour la catégorisation
des transactions, utilisant la cascade de confiance (heuristique → similarité → IA).

Usage:
    from modules.transactions.services import CategorizationService
    
    service = CategorizationService()
    result = service.categorize(
        label="MONOPRIX PARIS 14",
        amount=-45.67,
        date="2024-01-15"
    )
    
    print(result.category)  # "FOOD_AND_DRINK > Groceries"
    print(result.confidence)  # 0.95
    print(result.method)  # "HEURISTIC"
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any, List
import sqlite3

from modules.transactions.constants import (
    CategorizationMethod,
    PFCV2_CATEGORIES,
    get_category_type,
    is_expense_category,
)
from modules.categorization_cascade import (
    TransactionCategorizer,
    CategorizationResult as CascadeResult,
)
from modules.db.connection import get_db_connection
from modules.db_v2 import TransactionRepository
from modules.logger import logger


@dataclass
class CategorizationServiceResult:
    """
    Résultat enrichi d'une catégorisation.
    
    Attributes:
        category: Catégorie complète (ex: "FOOD_AND_DRINK > Groceries")
        main_category: Catégorie principale (ex: "FOOD_AND_DRINK")
        subcategory: Sous-catégorie (ex: "Groceries")
        clean_merchant: Nom du commerçant nettoyé
        confidence: Score de confiance (0.0 - 1.0)
        method: Méthode utilisée (HEURISTIC, SIMILARITY, LOCAL_AI, CLOUD_AI)
        is_income: True si c'est un revenu
        is_expense: True si c'est une dépense
        metadata: Métadonnées complètes (pour stockage JSON)
        similar_transaction_id: ID de la transaction similaire (si applicable)
        similarity_score: Score de similarité (si applicable)
    """
    category: str
    main_category: str
    subcategory: str
    clean_merchant: str
    confidence: float
    method: CategorizationMethod
    is_income: bool
    is_expense: bool
    metadata: Dict[str, Any]
    similar_transaction_id: Optional[int] = None
    similarity_score: Optional[float] = None
    
    def to_json(self) -> str:
        """Convertit le résultat en JSON pour stockage."""
        return json.dumps({
            "category": self.category,
            "main_category": self.main_category,
            "subcategory": self.subcategory,
            "clean_merchant": self.clean_merchant,
            "confidence": self.confidence,
            "method": self.method.value,
            "is_income": self.is_income,
            "is_expense": self.is_expense,
            "similar_transaction_id": self.similar_transaction_id,
            "similarity_score": self.similarity_score,
            "timestamp": datetime.now().isoformat(),
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> "CategorizationServiceResult":
        """Crée un résultat depuis une chaîne JSON."""
        data = json.loads(json_str)
        data["method"] = CategorizationMethod(data["method"])
        # Extraire les champs du dictionnaire metadata si présent
        if "metadata" in data:
            metadata = data.pop("metadata")
            data.update(metadata)
        return cls(**data)


class CategorizationService:
    """
    Service de catégorisation avec persistance des métadonnées.
    
    Cette classe wrap le TransactionCategorizer existant et ajoute :
    - Stockage des métadonnées dans la base de données
    - Interface simplifiée
    - Gestion des erreurs
    
    Usage:
        service = CategorizationService()
        
        # Catégoriser une transaction
        result = service.categorize("MONOPRIX PARIS", -45.67, "2024-01-15")
        
        # Sauvegarder avec métadonnées
        service.save_categorization(transaction_id=123, result=result)
    """
    
    def __init__(
        self,
        similarity_threshold: float = 0.85,
        min_confidence: float = 0.70,
        use_local_ai: bool = True,
        use_cloud_fallback: bool = True,
    ):
        """
        Initialise le service de catégorisation.
        
        Args:
            similarity_threshold: Seuil pour le matching par similarité (0-1)
            min_confidence: Confiance minimale pour accepter un résultat IA
            use_local_ai: Utiliser l'IA locale (Llama)
            use_cloud_fallback: Fallback sur IA cloud si local échoue
        """
        self.categorizer = TransactionCategorizer(
            similarity_threshold=similarity_threshold,
            min_confidence=min_confidence,
            use_local_ai=use_local_ai,
            use_cloud_fallback=use_cloud_fallback,
        )
        self.tx_repo = TransactionRepository()
        
        # S'assurer que la colonne meta_data existe
        self._ensure_meta_data_column()
    
    def _ensure_meta_data_column(self):
        """Vérifie et crée la colonne meta_data si nécessaire."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(transactions)")
                columns = [info[1] for info in cursor.fetchall()]
                
                if "meta_data" not in columns:
                    cursor.execute(
                        "ALTER TABLE transactions ADD COLUMN meta_data TEXT"
                    )
                    conn.commit()
                    logger.info("Colonne meta_data ajoutée à la table transactions")
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la vérification de meta_data: {e}")
    
    def categorize(
        self,
        label: str,
        amount: float,
        date: str,
        transaction_id: Optional[int] = None,
    ) -> CategorizationServiceResult:
        """
        Catégorise une transaction.
        
        Args:
            label: Libellé de la transaction
            amount: Montant (négatif pour dépense, positif pour revenu)
            date: Date de la transaction (format ISO)
            transaction_id: ID de la transaction (optionnel, pour contexte)
            
        Returns:
            Résultat de la catégorisation enrichi
        """
        # Appeler le catégoriseur de la cascade
        cascade_result = self.categorizer.categorize(label, amount, date)
        
        # Convertir le résultat
        return self._convert_result(cascade_result, amount)
    
    def _convert_result(
        self,
        cascade_result: CascadeResult,
        amount: float,
    ) -> CategorizationServiceResult:
        """Convertit un résultat de cascade en résultat de service."""
        # Parser la catégorie
        if " > " in cascade_result.category:
            main_cat, sub_cat = cascade_result.category.split(" > ", 1)
        else:
            main_cat = cascade_result.category
            sub_cat = ""
        
        # Déterminer la méthode
        method_map = {
            "heuristic": CategorizationMethod.HEURISTIC,
            "similarity": CategorizationMethod.SIMILARITY,
            "local_ai": CategorizationMethod.LOCAL_AI,
            "cloud_ai": CategorizationMethod.CLOUD_AI,
        }
        method = method_map.get(cascade_result.source, CategorizationMethod.HEURISTIC)
        
        # Construire les métadonnées
        metadata = {
            "clean_merchant": cascade_result.clean_merchant,
            "is_recurring_candidate": cascade_result.is_recurring_candidate,
            "risk_flag": cascade_result.risk_flag,
            "similar_transaction_id": cascade_result.similar_transaction_id,
            "similarity_score": cascade_result.similarity_score,
            "categorization": {
                "confidence_score": cascade_result.confidence_score,
                "method": method.value,
                "timestamp": datetime.now().isoformat(),
                "version": "2.0",
            }
        }
        
        return CategorizationServiceResult(
            category=cascade_result.category,
            main_category=main_cat,
            subcategory=sub_cat,
            clean_merchant=cascade_result.clean_merchant,
            confidence=cascade_result.confidence_score,
            method=method,
            is_income=amount > 0,
            is_expense=amount < 0,
            metadata=metadata,
            similar_transaction_id=cascade_result.similar_transaction_id,
            similarity_score=cascade_result.similarity_score,
        )
    
    def save_categorization(
        self,
        transaction_id: int,
        result: CategorizationServiceResult,
    ) -> bool:
        """
        Sauvegarde les métadonnées de catégorisation en base.
        
        Args:
            transaction_id: ID de la transaction
            result: Résultat de la catégorisation
            
        Returns:
            True si sauvegardé avec succès
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Mettre à jour la transaction avec la catégorie et les métadonnées
                cursor.execute(
                    """
                    UPDATE transactions 
                    SET category_validated = ?,
                        meta_data = ?,
                        status = 'validated'
                    WHERE id = ?
                    """,
                    (
                        result.category,
                        json.dumps(result.metadata),
                        transaction_id,
                    )
                )
                conn.commit()
                
                logger.info(
                    f"Transaction {transaction_id} catégorisée: {result.category} "
                    f"(confiance: {result.confidence}, méthode: {result.method.value})"
                )
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def get_categorization_metadata(
        self,
        transaction_id: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Récupère les métadonnées de catégorisation d'une transaction.
        
        Args:
            transaction_id: ID de la transaction
            
        Returns:
            Métadonnées ou None si pas trouvé
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT meta_data FROM transactions WHERE id = ?",
                    (transaction_id,)
                )
                row = cursor.fetchone()
                
                if row and row[0]:
                    return json.loads(row[0])
                return None
                
        except (sqlite3.Error, json.JSONDecodeError) as e:
            logger.error(f"Erreur lors de la récupération: {e}")
            return None
    
    def batch_categorize(
        self,
        transactions: List[Dict[str, Any]],
        save: bool = True,
    ) -> List[CategorizationServiceResult]:
        """
        Catégorise plusieurs transactions en batch.
        
        Args:
            transactions: Liste de dicts avec keys: id, label, amount, date
            save: Si True, sauvegarde les résultats en base
            
        Returns:
            Liste des résultats
        """
        results = []
        
        for tx in transactions:
            result = self.categorize(
                label=tx["label"],
                amount=tx["amount"],
                date=tx["date"],
                transaction_id=tx.get("id"),
            )
            results.append(result)
            
            if save and tx.get("id"):
                self.save_categorization(tx["id"], result)
        
        return results
    
    def find_similar_transactions(
        self,
        label: str,
        threshold: float = 0.85,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Trouve les transactions similaires dans l'historique.
        
        Args:
            label: Libellé à chercher
            threshold: Seuil de similarité
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des transactions similaires
        """
        # Utiliser le repository pour chercher
        history = self.tx_repo.get_all(filters={"status": "validated"}, limit=5000)
        
        if history.empty:
            return []
        
        from difflib import SequenceMatcher
        
        matches = []
        for _, row in history.iterrows():
            hist_label = str(row.get("label", ""))
            similarity = SequenceMatcher(None, label.upper(), hist_label.upper()).ratio()
            
            if similarity >= threshold:
                matches.append({
                    "id": row.get("id"),
                    "label": hist_label,
                    "category": row.get("category_validated"),
                    "similarity": round(similarity, 3),
                })
        
        # Trier par similarité décroissante
        matches.sort(key=lambda x: x["similarity"], reverse=True)
        return matches[:limit]


# Singleton pour faciliter l'utilisation
_categorization_service: Optional[CategorizationService] = None


def get_categorization_service() -> CategorizationService:
    """Retourne l'instance singleton du service de catégorisation."""
    global _categorization_service
    if _categorization_service is None:
        _categorization_service = CategorizationService()
    return _categorization_service


def categorize_transaction(
    label: str,
    amount: float,
    date: str,
    transaction_id: Optional[int] = None,
) -> CategorizationServiceResult:
    """
    Fonction utilitaire pour catégoriser une transaction.
    
    Usage:
        result = categorize_transaction("MONOPRIX", -45.67, "2024-01-15")
        print(result.category)
    """
    service = get_categorization_service()
    return service.categorize(label, amount, date, transaction_id)
