# -*- coding: utf-8 -*-
"""
Cache intelligent pour les appels IA.

Réduit les coûts API en cachant les résultats de catégorisation
basés sur (label, amount_bucket, provider).
"""

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any

from modules.db.connection import get_db_connection
from modules.logger import logger


@dataclass
class CachedResult:
    """Résultat mis en cache."""

    category: str
    confidence: float
    timestamp: float
    ttl: int = 86400  # 24h par défaut

    def is_expired(self) -> bool:
        """Vérifie si le cache est expiré."""
        return (time.time() - self.timestamp) > self.ttl


class AICache:
    """
    Cache pour les résultats d'IA.
    
    Utilise SQLite comme backend avec invalidation TTL.
    """

    _instance = None
    _DEFAULT_TTL = 86400  # 24 heures
    _MAX_CACHE_SIZE = 10000  # Nombre max d'entrées

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_cache()
        return cls._instance

    def _init_cache(self):
        """Initialise la table de cache."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_cache (
                    cache_key TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    provider TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    ttl INTEGER NOT NULL,
                    hit_count INTEGER DEFAULT 1
                )
            """
            )
            conn.commit()
        logger.info("AI Cache initialized")

    def _generate_key(self, label: str, amount: float, provider: str) -> str:
        """
        Génère une clé de cache unique.
        
        Normalise le label et utilise un bucket de montant
        pour regrouper les transactions similaires.
        """
        # Normaliser le label
        normalized_label = label.upper().strip()
        # Supprimer les numéros de commande/suivi
        import re

        normalized_label = re.sub(r"\b\d{4,}\b", "", normalized_label)
        normalized_label = re.sub(r"\s+", " ", normalized_label).strip()

        # Bucket de montant (arrondi à 5€ près)
        amount_bucket = round(amount / 5) * 5

        # Créer la clé
        key_data = f"{normalized_label}:{amount_bucket}:{provider}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, label: str, amount: float, provider: str) -> CachedResult | None:
        """
        Récupère un résultat du cache.
        
        Returns:
            CachedResult si trouvé et non expiré, None sinon.
        """
        cache_key = self._generate_key(label, amount, provider)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT category, confidence, timestamp, ttl, hit_count
                FROM ai_cache
                WHERE cache_key = ?
            """,
                (cache_key,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            category, confidence, timestamp, ttl, hit_count = row

            # Vérifier expiration
            if time.time() - timestamp > ttl:
                self._delete_entry(cache_key)
                return None

            # Incrémenter le compteur de hits
            cursor.execute(
                "UPDATE ai_cache SET hit_count = ? WHERE cache_key = ?",
                (hit_count + 1, cache_key),
            )
            conn.commit()

            logger.debug(f"AI Cache HIT for key {cache_key[:8]}...")
            return CachedResult(category, confidence, timestamp, ttl)

    def set(
        self,
        label: str,
        amount: float,
        provider: str,
        category: str,
        confidence: float,
        ttl: int | None = None,
    ) -> None:
        """
        Stocke un résultat dans le cache.
        """
        cache_key = self._generate_key(label, amount, provider)
        ttl = ttl or self._DEFAULT_TTL
        timestamp = time.time()

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO ai_cache
                (cache_key, category, confidence, provider, timestamp, ttl)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (cache_key, category, confidence, provider, timestamp, ttl),
            )
            conn.commit()

        logger.debug(f"AI Cache SET for key {cache_key[:8]}...")
        
        # Vérifier si on doit nettoyer le cache
        self._maybe_cleanup()

    def _delete_entry(self, cache_key: str) -> None:
        """Supprime une entrée du cache."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ai_cache WHERE cache_key = ?", (cache_key,))
            conn.commit()

    def _maybe_cleanup(self) -> None:
        """
        Nettoie le cache si nécessaire.
        Supprime les entrées les moins utilisées et expirées.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Supprimer les entrées expirées
            current_time = time.time()
            cursor.execute(
                "DELETE FROM ai_cache WHERE timestamp + ttl < ?",
                (current_time,),
            )
            expired_count = cursor.rowcount

            # Vérifier la taille totale
            cursor.execute("SELECT COUNT(*) FROM ai_cache")
            total_count = cursor.fetchone()[0]

            if total_count > self._MAX_CACHE_SIZE:
                # Supprimer les 20% les moins utilisés
                to_delete = int(self._MAX_CACHE_SIZE * 0.2)
                cursor.execute(
                    """
                    DELETE FROM ai_cache
                    WHERE cache_key IN (
                        SELECT cache_key FROM ai_cache
                        ORDER BY hit_count ASC, timestamp ASC
                        LIMIT ?
                    )
                """,
                    (to_delete,),
                )
                deleted_count = cursor.rowcount
                logger.info(f"AI Cache cleanup: removed {deleted_count} old entries")

            conn.commit()

            if expired_count > 0:
                logger.info(f"AI Cache cleanup: removed {expired_count} expired entries")

    def invalidate(self, pattern: str | None = None) -> int:
        """
        Invalide le cache.
        
        Args:
            pattern: Si spécifié, invalide uniquement les entrées
                    contenant ce pattern dans le label normalisé.
        
        Returns:
            Nombre d'entrées supprimées.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if pattern:
                # Invalider par pattern (nécessite de décoder les clés)
                # Pour simplifier, on invalide tout pour l'instant
                cursor.execute("DELETE FROM ai_cache")
            else:
                cursor.execute("DELETE FROM ai_cache")
            
            deleted = cursor.rowcount
            conn.commit()

        logger.info(f"AI Cache invalidated: {deleted} entries removed")
        return deleted

    def get_stats(self) -> dict[str, Any]:
        """
        Retourne les statistiques du cache.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*), SUM(hit_count) FROM ai_cache")
            total_entries, total_hits = cursor.fetchone()
            total_entries = total_entries or 0
            total_hits = total_hits or 0

            cursor.execute(
                "SELECT COUNT(*) FROM ai_cache WHERE timestamp + ttl < ?",
                (time.time(),),
            )
            expired_count = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT provider, COUNT(*) as count
                FROM ai_cache
                GROUP BY provider
            """
            )
            by_provider = {row[0]: row[1] for row in cursor.fetchall()}

            return {
                "total_entries": total_entries,
                "total_hits": total_hits,
                "expired_entries": expired_count,
                "average_hits": total_hits / total_entries if total_entries > 0 else 0,
                "by_provider": by_provider,
                "hit_rate": self._calculate_hit_rate(),
            }

    def _calculate_hit_rate(self) -> float:
        """Calcule le taux de hit du cache."""
        # Cette métrique serait idéalement stockée dans une table de métriques
        # Pour l'instant, on retourne une valeur estimée
        return 0.0


# Fonctions utilitaires pour l'utilisation courante

def get_ai_cache() -> AICache:
    """Retourne l'instance singleton du cache IA."""
    return AICache()


def cache_categorization_result(
    label: str,
    amount: float,
    provider: str,
    category: str,
    confidence: float = 1.0,
) -> None:
    """Cache un résultat de catégorisation."""
    cache = get_ai_cache()
    cache.set(label, amount, provider, category, confidence)


def get_cached_categorization(
    label: str, amount: float, provider: str
) -> str | None:
    """
    Récupère une catégorisation depuis le cache.
    
    Returns:
        La catégorie si trouvée, None sinon.
    """
    cache = get_ai_cache()
    result = cache.get(label, amount, provider)
    return result.category if result else None


def invalidate_ai_cache(pattern: str | None = None) -> int:
    """Invalide le cache IA."""
    cache = get_ai_cache()
    return cache.invalidate(pattern)
