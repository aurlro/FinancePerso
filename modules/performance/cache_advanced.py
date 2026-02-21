"""
Cache Avancé - Optimisation des Performances
=============================================

Système de cache intelligent avec:
- TTL (Time To Live) adaptatif
- Invalidation ciblée
- Compression des données
- Métriques de performance
- Optimisation pour Monte Carlo

Usage:
    from modules.performance.cache_advanced import AdvancedCache, cache_monte_carlo
    
    # Cache avec TTL de 5 minutes
    cache = AdvancedCache(default_ttl=300)
    
    # Décoration de fonction
    @cache_monte_carlo(ttl_seconds=600)
    def run_simulation(params):
        return expensive_calculation(params)
"""

import functools
import hashlib
import json
import pickle
import time
import zlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Generic, Optional, TypeVar, List
from collections import OrderedDict
import threading

import streamlit as st

from modules.logger import logger

T = TypeVar('T')


@dataclass
class CacheEntry:
    """
    Entrée de cache avec métadonnées.
    
    Attributes:
        key: Clé de cache
        value: Valeur stockée
        created_at: Timestamp de création
        ttl_seconds: Durée de vie en secondes
        access_count: Nombre d'accès
        last_accessed: Dernier accès
        compressed: Si la valeur est compressée
        size_bytes: Taille en bytes
    """
    key: str
    value: Any
    created_at: datetime
    ttl_seconds: int
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    compressed: bool = False
    size_bytes: int = 0
    
    @property
    def is_expired(self) -> bool:
        """Vérifie si l'entrée est expirée."""
        expiry = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.now() > expiry
    
    @property
    def age_seconds(self) -> float:
        """Âge de l'entrée en secondes."""
        return (datetime.now() - self.created_at).total_seconds()
    
    def touch(self):
        """Met à jour les métadonnées d'accès."""
        self.access_count += 1
        self.last_accessed = datetime.now()


@dataclass
class CacheStats:
    """Statistiques du cache."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_size_bytes: int = 0
    entry_count: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Taux de hit (0-1)."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    @property
    def miss_rate(self) -> float:
        """Taux de miss (0-1)."""
        return 1 - self.hit_rate


class AdvancedCache:
    """
    Cache avancé avec TTL, LRU et compression.
    
    Cette classe implémente un cache en mémoire optimisé pour:
    - Réduire les calculs coûteux (Monte Carlo)
    - Minimiser les accès disque (SQLite)
    - Économiser la mémoire (compression)
    
    Features:
    - TTL adaptatif selon le type de données
    - LRU (Least Recently Used) eviction
    - Compression zlib pour les grosses valeurs
    - Thread-safe
    - Métriques détaillées
    
    Args:
        default_ttl: TTL par défaut en secondes
        max_size: Nombre maximum d'entrées
        max_memory_mb: Limite mémoire en MB
        compression_threshold: Seuil de compression en bytes
    """
    
    def __init__(
        self,
        default_ttl: int = 300,  # 5 minutes
        max_size: int = 1000,
        max_memory_mb: float = 100.0,
        compression_threshold: int = 1024,  # 1KB
    ):
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.compression_threshold = compression_threshold
        
        # Stockage
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: OrderedDict[str, None] = OrderedDict()
        
        # Statistiques
        self.stats = CacheStats()
        
        # Thread safety
        self._lock = threading.RLock()
        
        # TTL par type de donnée
        self._ttl_by_type: Dict[str, int] = {
            'monte_carlo': 600,      # 10 min - simulations lourdes
            'transactions': 60,       # 1 min - données fréquemment modifiées
            'categories': 300,        # 5 min
            'wealth_projection': 300, # 5 min
            'subscriptions': 120,     # 2 min
            'user_profile': 3600,     # 1 heure
            'static_data': 86400,     # 24 heures
        }
        
        logger.info(f"AdvancedCache initialisé (max_size={max_size}, TTL={default_ttl}s)")
    
    def _generate_key(self, *args, **kwargs) -> str:
        """
        Génère une clé de cache à partir des arguments.
        
        Args:
            *args: Arguments positionnels
            **kwargs: Arguments nommés
            
        Returns:
            Clé de cache (hash MD5)
        """
        # Sérialiser les arguments
        key_data = {
            'args': args,
            'kwargs': kwargs,
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _compress_value(self, value: Any) -> tuple[bytes, bool]:
        """
        Compresse une valeur si nécessaire.
        
        Args:
            value: Valeur à compresser
            
        Returns:
            Tuple (valeur, compressée)
        """
        serialized = pickle.dumps(value)
        
        if len(serialized) > self.compression_threshold:
            compressed = zlib.compress(serialized, level=6)
            return compressed, True
        
        return serialized, False
    
    def _decompress_value(self, value: bytes, compressed: bool) -> Any:
        """
        Décompresse une valeur.
        
        Args:
            value: Valeur à décompresser
            compressed: Si la valeur est compressée
            
        Returns:
            Valeur décompressée
        """
        if compressed:
            decompressed = zlib.decompress(value)
            return pickle.loads(decompressed)
        
        return pickle.loads(value)
    
    def _evict_if_needed(self):
        """Évite les entrées si nécessaire (LRU)."""
        # Vérifier la taille
        while len(self._cache) >= self.max_size and self._cache:
            # Éviter la plus ancienne (LRU)
            oldest_key = next(iter(self._access_order))
            self._evict_entry(oldest_key)
        
        # Vérifier la mémoire
        while self.stats.total_size_bytes > self.max_memory_bytes and self._cache:
            oldest_key = next(iter(self._access_order))
            self._evict_entry(oldest_key)
    
    def _evict_entry(self, key: str):
        """Évite une entrée spécifique."""
        if key in self._cache:
            entry = self._cache[key]
            self.stats.total_size_bytes -= entry.size_bytes
            self.stats.evictions += 1
            
            del self._cache[key]
            if key in self._access_order:
                del self._access_order[key]
            
            logger.debug(f"Cache eviction: {key}")
    
    def _cleanup_expired(self):
        """Nettoie les entrées expirées."""
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired
        ]
        
        for key in expired_keys:
            self._evict_entry(key)
        
        if expired_keys:
            logger.debug(f"Cache cleanup: {len(expired_keys)} entrées expirées supprimées")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Récupère une valeur du cache.
        
        Args:
            key: Clé de cache
            
        Returns:
            Valeur ou None si non trouvée/expirée
        """
        with self._lock:
            self._cleanup_expired()
            
            if key not in self._cache:
                self.stats.misses += 1
                return None
            
            entry = self._cache[key]
            
            if entry.is_expired:
                self._evict_entry(key)
                self.stats.misses += 1
                return None
            
            # Mettre à jour LRU
            entry.touch()
            self._access_order.move_to_end(key)
            
            # Décompresser et retourner
            value = self._decompress_value(entry.value, entry.compressed)
            self.stats.hits += 1
            
            return value
    
    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        data_type: Optional[str] = None,
    ):
        """
        Stocke une valeur dans le cache.
        
        Args:
            key: Clé de cache
            value: Valeur à stocker
            ttl_seconds: TTL spécifique (optionnel)
            data_type: Type de données pour TTL adaptatif
        """
        with self._lock:
            # Déterminer le TTL
            if ttl_seconds is None:
                if data_type and data_type in self._ttl_by_type:
                    ttl_seconds = self._ttl_by_type[data_type]
                else:
                    ttl_seconds = self.default_ttl
            
            # Compresser la valeur
            stored_value, compressed = self._compress_value(value)
            size_bytes = len(stored_value)
            
            # Éviter si nécessaire
            self._evict_if_needed()
            
            # Créer l'entrée
            entry = CacheEntry(
                key=key,
                value=stored_value,
                created_at=datetime.now(),
                ttl_seconds=ttl_seconds,
                compressed=compressed,
                size_bytes=size_bytes,
            )
            
            # Stocker
            self._cache[key] = entry
            self._access_order[key] = None
            self.stats.total_size_bytes += size_bytes
            self.stats.entry_count = len(self._cache)
            
            logger.debug(f"Cache set: {key} (TTL={ttl_seconds}s, size={size_bytes}B)")
    
    def delete(self, key: str) -> bool:
        """
        Supprime une entrée du cache.
        
        Args:
            key: Clé à supprimer
            
        Returns:
            True si supprimée, False sinon
        """
        with self._lock:
            if key in self._cache:
                self._evict_entry(key)
                return True
            return False
    
    def clear(self):
        """Vide complètement le cache."""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
            self.stats = CacheStats()
            logger.info("Cache cleared")
    
    def invalidate_by_pattern(self, pattern: str):
        """
        Invalide les entrées correspondant à un pattern.
        
        Args:
            pattern: Pattern de clé (ex: "transactions_*")
        """
        with self._lock:
            import fnmatch
            keys_to_delete = [
                key for key in self._cache.keys()
                if fnmatch.fnmatch(key, pattern)
            ]
            
            for key in keys_to_delete:
                self._evict_entry(key)
            
            logger.info(f"Cache invalidation: {len(keys_to_delete)} entrées pour pattern '{pattern}'")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques du cache.
        
        Returns:
            Dictionnaire de statistiques
        """
        with self._lock:
            self._cleanup_expired()
            
            return {
                'hits': self.stats.hits,
                'misses': self.stats.misses,
                'hit_rate': f"{self.stats.hit_rate:.1%}",
                'evictions': self.stats.evictions,
                'entry_count': len(self._cache),
                'total_size_mb': f"{self.stats.total_size_bytes / (1024*1024):.2f}",
                'max_size': self.max_size,
                'max_memory_mb': self.max_memory_bytes / (1024*1024),
            }
    
    def decorator(
        self,
        ttl_seconds: Optional[int] = None,
        data_type: Optional[str] = None,
        key_func: Optional[Callable] = None,
    ):
        """
        Décorateur pour mettre en cache le résultat d'une fonction.
        
        Args:
            ttl_seconds: TTL spécifique
            data_type: Type de données pour TTL adaptatif
            key_func: Fonction personnalisée de génération de clé
            
        Returns:
            Décorateur
        """
        def decorator_func(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Générer la clé
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = f"{func.__name__}:{self._generate_key(*args, **kwargs)}"
                
                # Essayer de récupérer du cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value
                
                # Calculer et stocker
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl_seconds, data_type)
                
                return result
            
            # Attacher des méthodes utilitaires
            wrapper.cache = self
            wrapper.invalidate = lambda: self.delete(
                f"{func.__name__}:{self._generate_key()}"
            )
            
            return wrapper
        return decorator_func


# ==================== Fonctions utilitaires ====================

# Instance globale du cache
cache = AdvancedCache()


def cache_monte_carlo(ttl_seconds: int = 600):
    """
    Décorateur spécial pour les simulations Monte Carlo.
    
    Les simulations sont coûteuses en CPU, donc on les cache plus longtemps.
    
    Args:
        ttl_seconds: TTL en secondes (défaut: 10 minutes)
    """
    return cache.decorator(ttl_seconds=ttl_seconds, data_type='monte_carlo')


def cache_transactions(ttl_seconds: int = 60):
    """
    Décorateur pour les données de transactions.
    
    Les transactions changent fréquemment, donc TTL court.
    
    Args:
        ttl_seconds: TTL en secondes (défaut: 1 minute)
    """
    return cache.decorator(ttl_seconds=ttl_seconds, data_type='transactions')


def cache_wealth_projection(ttl_seconds: int = 300):
    """
    Décorateur pour les projections patrimoniales.
    
    Args:
        ttl_seconds: TTL en secondes (défaut: 5 minutes)
    """
    return cache.decorator(ttl_seconds=ttl_seconds, data_type='wealth_projection')


def invalidate_cache_pattern(pattern: str):
    """
    Invalide les entrées de cache correspondant à un pattern.
    
    Args:
        pattern: Pattern de clé (ex: "transactions_*")
    """
    cache.invalidate_by_pattern(pattern)


def get_cache_stats() -> Dict[str, Any]:
    """Retourne les statistiques du cache global."""
    return cache.get_stats()


def clear_all_cache():
    """Vide complètement le cache."""
    cache.clear()


# ==================== Intégration Streamlit ====================

def render_cache_stats():
    """Affiche les statistiques du cache dans Streamlit."""
    import streamlit as st
    
    stats = get_cache_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Hit Rate", stats['hit_rate'])
    with col2:
        st.metric("Entrées", stats['entry_count'])
    with col3:
        st.metric("Taille", f"{stats['total_size_mb']} MB")
    with col4:
        st.metric("Evictions", stats['evictions'])
    
    if st.button("🗑️ Vider le cache"):
        clear_all_cache()
        st.success("Cache vidé!")
        st.rerun()
