# -*- coding: utf-8 -*-
"""
Monitoring des requêtes SQL pour performance et debugging.

Fonctionnalités:
- Logging des requêtes lentes (> seuil)
- Statistiques d'exécution (temps moyen, nombre d'appels)
- Détection des requêtes N+1
- Alertes de performance
"""

import functools
import time
from collections import defaultdict
from contextlib import contextmanager
from typing import Any, Callable

from modules.db.connection import get_db_connection
from modules.logger import logger

# Seuil d'alerte pour requêtes lentes (en secondes)
SLOW_QUERY_THRESHOLD = 0.1  # 100ms

# Stats globales
_query_stats = defaultdict(lambda: {"count": 0, "total_time": 0.0, "max_time": 0.0})
_call_stack = []


class QueryMonitor:
    """Moniteur de requêtes SQL."""

    def __init__(self):
        self.enabled = True
        self.slow_query_threshold = SLOW_QUERY_THRESHOLD
        self._query_log = []

    def log_query(
        self,
        query: str,
        params: tuple | None,
        execution_time: float,
        source: str | None = None,
    ) -> None:
        """Log une requête exécutée."""
        if not self.enabled:
            return

        # Normaliser la requête pour les stats
        normalized_query = self._normalize_query(query)

        # Mettre à jour les stats
        _query_stats[normalized_query]["count"] += 1
        _query_stats[normalized_query]["total_time"] += execution_time
        _query_stats[normalized_query]["max_time"] = max(
            _query_stats[normalized_query]["max_time"], execution_time
        )

        # Logger si requête lente
        if execution_time > self.slow_query_threshold:
            logger.warning(
                f"SLOW QUERY ({execution_time:.3f}s): {normalized_query[:100]}... "
                f"Source: {source or 'unknown'}"
            )

        # Stocker dans l'historique récent
        self._query_log.append(
            {
                "query": normalized_query[:200],
                "time": execution_time,
                "timestamp": time.time(),
                "source": source,
            }
        )

        # Garder uniquement les 100 dernières requêtes
        if len(self._query_log) > 100:
            self._query_log.pop(0)

    def _normalize_query(self, query: str) -> str:
        """Normalise une requête pour le regroupement des stats."""
        # Supprimer les espaces multiples
        query = " ".join(query.split())
        # Remplacer les valeurs littérales par ?
        import re

        query = re.sub(r"'[^']*'", "?", query)
        query = re.sub(r"\b\d+\b", "?", query)
        return query.strip()

    def get_stats(self) -> dict[str, Any]:
        """Retourne les statistiques de monitoring."""
        stats = {
            "total_queries": sum(s["count"] for s in _query_stats.values()),
            "unique_queries": len(_query_stats),
            "slow_queries": [
                {
                    "query": q[:100],
                    "avg_time": s["total_time"] / s["count"],
                    "max_time": s["max_time"],
                    "count": s["count"],
                }
                for q, s in _query_stats.items()
                if s["total_time"] / s["count"] > self.slow_query_threshold
            ],
            "most_frequent": sorted(
                [
                    {"query": q[:100], "count": s["count"], "avg_time": s["total_time"] / s["count"]}
                    for q, s in _query_stats.items()
                ],
                key=lambda x: x["count"],
                reverse=True,
            )[:10],
            "recent_queries": self._query_log[-20:],
        }
        return stats

    def reset_stats(self) -> None:
        """Reset les statistiques."""
        _query_stats.clear()
        self._query_log.clear()

    def detect_n_plus_one(self) -> list[dict[str, Any]]:
        """
        Détecte les patterns N+1 potentiels.
        
        Returns:
            Liste des suspects N+1 avec détails.
        """
        suspects = []
        
        # Analyser les requêtes récentes
        select_patterns = defaultdict(int)
        for entry in self._query_log:
            query = entry["query"]
            if query.upper().startswith("SELECT") and "WHERE" in query.upper():
                # Extraire le pattern WHERE
                import re
                match = re.search(r"WHERE\s+(.+?)(?:ORDER|LIMIT|$)", query, re.IGNORECASE)
                if match:
                    where_clause = match.group(1).strip()
                    select_patterns[where_clause] += 1

        # Détecter les patterns répétés
        for pattern, count in select_patterns.items():
            if count > 5:  # Plus de 5 requêtes similaires
                suspects.append(
                    {
                        "pattern": pattern[:100],
                        "count": count,
                        "suggestion": "Considérer l'utilisation d'un JOIN ou IN clause",
                    }
                )

        return suspects


# Instance globale
_monitor = QueryMonitor()


def get_monitor() -> QueryMonitor:
    """Retourne l'instance du moniteur."""
    return _monitor


@contextmanager
def monitor_query(query: str, params: tuple | None = None, source: str | None = None):
    """
    Context manager pour monitorer une requête.
    
    Usage:
        with monitor_query("SELECT * FROM transactions"):
            cursor.execute("SELECT * FROM transactions")
    """
    start_time = time.perf_counter()
    try:
        yield
    finally:
        execution_time = time.perf_counter() - start_time
        _monitor.log_query(query, params, execution_time, source)


def monitor_queries(func: Callable) -> Callable:
    """
    Décorateur pour monitorer toutes les requêtes d'une fonction.
    
    Usage:
        @monitor_queries
        def get_transactions():
            ...
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        source = f"{func.__module__}.{func.__name__}"
        start_time = time.perf_counter()
        
        # Ajouter au call stack pour détection N+1
        _call_stack.append(source)
        
        try:
            result = func(*args, **kwargs)
            
            # Vérifier si on a un pattern N+1
            if len(_call_stack) > 2:
                logger.debug(f"Deep call stack detected: {' -> '.join(_call_stack)}")
            
            return result
        finally:
            _call_stack.pop()

    return wrapper


def get_slow_queries(min_time: float | None = None) -> list[dict[str, Any]]:
    """
    Retourne la liste des requêtes lentes.
    
    Args:
        min_time: Temps minimum pour considérer une requête comme lente.
    
    Returns:
        Liste des requêtes lentes avec stats.
    """
    threshold = min_time or SLOW_QUERY_THRESHOLD
    
    return [
        {
            "query": q[:150],
            "avg_time": s["total_time"] / s["count"],
            "max_time": s["max_time"],
            "count": s["count"],
        }
        for q, s in _query_stats.items()
        if s["total_time"] / s["count"] > threshold
    ]


def log_performance_summary() -> None:
    """Log un résumé des performances."""
    stats = _monitor.get_stats()
    
    logger.info("=" * 50)
    logger.info("DATABASE PERFORMANCE SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Total queries: {stats['total_queries']}")
    logger.info(f"Unique queries: {stats['unique_queries']}")
    
    if stats["slow_queries"]:
        logger.warning(f"Slow queries detected: {len(stats['slow_queries'])}")
        for sq in stats["slow_queries"][:5]:
            logger.warning(f"  - {sq['query'][:80]}... (avg: {sq['avg_time']:.3f}s)")
    
    n_plus_one = _monitor.detect_n_plus_one()
    if n_plus_one:
        logger.warning(f"Potential N+1 queries detected: {len(n_plus_one)}")
    
    logger.info("=" * 50)


def create_performance_table() -> None:
    """Crée la table pour stocker les métriques de performance."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS query_performance_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_pattern TEXT NOT NULL,
                execution_time REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                source TEXT,
                INDEX idx_timestamp (timestamp)
            )
        """
        )
        conn.commit()
