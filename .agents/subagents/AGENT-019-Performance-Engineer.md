# AGENT-019: Performance Engineer

> **Ingénieur Performance et Optimisation**  
> Responsable de l'optimisation DB, cache, requêtes et temps de réponse

---

## 🎯 Mission

Cet agent optimise les performances de FinancePerso à tous les niveaux: base de données SQLite, cache application, requêtes SQL, mémoire, et temps de réponse Streamlit.

### Domaines d'expertise
- **Database Optimization** : Indexes, query tuning, vacuum, WAL mode
- **Cache Strategy** : Cache invalidation, stratégies de cache, hit rates
- **Query Optimization** : SQL analysis, N+1 detection, batch operations
- **Memory Management** : Profiling, leak detection, garbage collection
- **Streamlit Performance** : Reruns optimization, session state, lazy loading

---

## 🏗️ Architecture Technique

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERFORMANCE MONITORING                        │
├─────────────────────────────────────────────────────────────────┤
│  Query Profiler │ Cache Analyzer │ Memory Tracker │ Load Tester │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              OPTIMIZATION ENGINE                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Database   │  │    Cache     │  │    Application       │  │
│  │  - Indexes   │  │  - Strategy  │  │  - Lazy loading      │  │
│  │  - Queries   │  │  - Warming   │  │  - Batch ops         │  │
│  │  - Vacuum    │  │  - Invalid.  │  │  - Memory mgmt       │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧱 Module 1: Query Profiler & Database Optimizer

```python
# modules/performance/query_profiler.py

import time
import functools
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from contextlib import contextmanager
from collections import defaultdict
import sqlite3
import re

logger = logging.getLogger(__name__)


@dataclass
class QueryMetrics:
    """Métriques d'une requête SQL."""
    query: str
    duration_ms: float
    rows_returned: int
    timestamp: float = field(default_factory=time.time)
    
    @property
    def is_slow(self) -> bool:
        return self.duration_ms > 100
    
    @property
    def query_hash(self) -> str:
        normalized = ' '.join(self.query.lower().split())
        import hashlib
        return hashlib.md5(normalized.encode()).hexdigest()[:16]


class QueryProfiler:
    """Profileur de requêtes SQL."""
    
    SLOW_QUERY_THRESHOLD_MS = 100
    N_PLUS_1_THRESHOLD = 10
    
    def __init__(self, max_queries: int = 10000):
        self._queries: List[QueryMetrics] = []
        self._query_counts: Dict[str, int] = defaultdict(int)
        self._enabled = False
        self._max_queries = max_queries
    
    def enable(self):
        self._enabled = True
        self._queries.clear()
        logger.info("Query profiling enabled")
    
    def disable(self):
        self._enabled = False
        logger.info("Query profiling disabled")
    
    @contextmanager
    def profile(self, query: str):
        if not self._enabled:
            yield
            return
        
        start = time.perf_counter()
        try:
            yield
        finally:
            duration = (time.perf_counter() - start) * 1000
            
            metrics = QueryMetrics(
                query=self._normalize_query(query),
                duration_ms=duration,
                rows_returned=0
            )
            
            if len(self._queries) >= self._max_queries:
                self._queries.pop(0)
            
            self._queries.append(metrics)
            self._query_counts[metrics.query_hash] += 1
            
            if duration > self.SLOW_QUERY_THRESHOLD_MS:
                logger.warning(f"Slow query ({duration:.1f}ms): {query[:100]}...")
    
    def get_slow_queries(self, limit: int = 20) -> List[QueryMetrics]:
        return sorted(
            [q for q in self._queries if q.is_slow],
            key=lambda q: q.duration_ms,
            reverse=True
        )[:limit]
    
    def detect_n_plus_1(self) -> List[Dict]:
        """Détecte le pattern N+1 queries."""
        n_plus_1_patterns = []
        time_windows = defaultdict(list)
        
        for query in self._queries:
            window_key = int(query.timestamp)
            time_windows[window_key].append(query)
        
        for window, queries in time_windows.items():
            pattern_counts = defaultdict(list)
            
            for q in queries:
                pattern = self._extract_pattern(q.query)
                pattern_counts[pattern].append(q)
            
            for pattern, pattern_queries in pattern_counts.items():
                if len(pattern_queries) > self.N_PLUS_1_THRESHOLD:
                    n_plus_1_patterns.append({
                        'pattern': pattern[:100],
                        'count': len(pattern_queries),
                        'suggestion': 'Consider using JOIN or IN clause'
                    })
        
        return n_plus_1_patterns
    
    def get_optimization_report(self) -> Dict:
        if not self._queries:
            return {"status": "no_data", "message": "No queries profiled"}
        
        total_queries = len(self._queries)
        slow_queries = len([q for q in self._queries if q.is_slow])
        avg_time = sum(q.duration_ms for q in self._queries) / total_queries
        
        return {
            'status': 'ok',
            'total_queries': total_queries,
            'slow_queries': slow_queries,
            'slow_query_rate': (slow_queries / total_queries) * 100,
            'avg_query_time_ms': avg_time,
            'max_query_time_ms': max(q.duration_ms for q in self._queries),
            'n_plus_1_patterns': self.detect_n_plus_1(),
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        recommendations = []
        
        n_plus_1 = self.detect_n_plus_1()
        if n_plus_1:
            recommendations.append(
                f"⚠️ Detected {len(n_plus_1)} N+1 query patterns. Use JOINs."
            )
        
        slow = len([q for q in self._queries if q.is_slow])
        if slow > 0:
            rate = (slow / len(self._queries)) * 100
            if rate > 10:
                recommendations.append(
                    f"🐌 High slow query rate: {rate:.1f}%. Add indexes."
                )
        
        return recommendations
    
    def _normalize_query(self, query: str) -> str:
        query = re.sub(r"'[^']*'", "'?'", query)
        query = re.sub(r"\d+", "?", query)
        query = ' '.join(query.split())
        return query.lower()
    
    def _extract_pattern(self, query: str) -> str:
        return self._normalize_query(query)


class DatabaseOptimizer:
    """Optimiseur de base de données SQLite."""
    
    RECOMMENDED_INDEXES = {
        'transactions': [
            ('date',), ('category',), ('account',), ('hash',),
        ],
        'bank_connections': [
            ('user_id',), ('status',),
        ],
        'sync_history': [
            ('connection_id',), ('sync_time',),
        ]
    }
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def analyze_indexes(self) -> Dict:
        """Analyse les indexes existants et manquants."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        report = {
            'existing_indexes': [],
            'missing_recommended': [],
        }
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        existing = [row[0] for row in cursor.fetchall()]
        report['existing_indexes'] = existing
        
        for table, indexes in self.RECOMMENDED_INDEXES.items():
            for columns in indexes:
                index_name = f"idx_{table}_{'_'.join(columns)}"
                if index_name not in existing:
                    report['missing_recommended'].append({
                        'table': table,
                        'columns': columns,
                        'suggested_name': index_name
                    })
        
        conn.close()
        return report
    
    def create_index(self, table: str, columns: tuple, index_name: str = None) -> bool:
        """Crée un index."""
        if not index_name:
            index_name = f"idx_{table}_{'_'.join(columns)}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        columns_str = ', '.join(columns)
        sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({columns_str})"
        
        try:
            cursor.execute(sql)
            conn.commit()
            logger.info(f"Created index: {index_name}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to create index: {e}")
            return False
        finally:
            conn.close()
    
    def optimize_database(self) -> Dict:
        """Exécute les optimisations recommandées."""
        results = {
            'indexes_created': [],
            'vacuum': False,
            'analyze': False,
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            report = self.analyze_indexes()
            for missing in report['missing_recommended']:
                if self.create_index(missing['table'], missing['columns'], missing['suggested_name']):
                    results['indexes_created'].append(missing['suggested_name'])
            
            cursor.execute("VACUUM")
            results['vacuum'] = True
            
            cursor.execute("ANALYZE")
            results['analyze'] = True
            
            conn.commit()
            
        except sqlite3.Error as e:
            logger.error(f"Optimization error: {e}")
        finally:
            conn.close()
        
        return results
    
    def enable_wal_mode(self) -> bool:
        """Active WAL mode pour meilleures performances."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=-64000")
            cursor.execute("PRAGMA temp_store=memory")
            conn.commit()
            logger.info("WAL mode enabled")
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to enable WAL: {e}")
            return False
        finally:
            conn.close()


def get_profiler():
    """Retourne l'instance globale du profileur."""
    global _default_profiler
    if '_default_profiler' not in globals():
        _default_profiler = QueryProfiler()
    return _default_profiler


def profile_query(query: str):
    """Décorateur/context manager pour profiler une requête."""
    return get_profiler().profile(query)


---

## 🧱 Module 2: Cache Strategy Engine

```python
# modules/performance/cache_manager.py

import functools
import hashlib
import time
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from collections import OrderedDict
import threading
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entrée de cache."""
    value: Any
    timestamp: float
    ttl: int
    hits: int = 0
    
    @property
    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl


class LRUCache:
    """Cache LRU (Least Recently Used) thread-safe."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300, name: str = "default"):
        self.name = name
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {'hits': 0, 'misses': 0, 'evictions': 0}
    
    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache."""
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._stats['misses'] += 1
                return None
            
            if entry.is_expired:
                del self._cache[key]
                self._stats['misses'] += 1
                return None
            
            self._cache.move_to_end(key)
            entry.hits += 1
            self._stats['hits'] += 1
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Stocke une valeur dans le cache."""
        ttl = ttl or self.default_ttl
        
        with self._lock:
            while len(self._cache) >= self.max_size:
                self._evict_lru()
            
            self._cache[key] = CacheEntry(
                value=value,
                timestamp=time.time(),
                ttl=ttl
            )
    
    def invalidate(self, key: str):
        """Invalide une clé spécifique."""
        with self._lock:
            self._cache.pop(key, None)
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalide les clés correspondant à un pattern."""
        with self._lock:
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self._cache[key]
            return len(keys_to_remove)
    
    def clear(self):
        """Vide le cache."""
        with self._lock:
            self._cache.clear()
    
    def _evict_lru(self):
        """Évince l'entrée la moins récemment utilisée."""
        if self._cache:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            self._stats['evictions'] += 1
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques."""
        with self._lock:
            total = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total * 100) if total > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hit_rate': hit_rate,
                'evictions': self._stats['evictions']
            }


class SmartCache:
    """Cache intelligent avec stratégies adaptatives."""
    
    def __init__(self):
        self._cache = LRUCache(max_size=2000)
        self._access_patterns: Dict[str, List[float]] = {}
    
    def cached(self, ttl: int = 300, key_func: Callable = None, adaptive: bool = True):
        """Décorateur de mise en cache."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self._generate_key(func.__name__, args, kwargs)
                
                cached_value = self._cache.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                result = func(*args, **kwargs)
                
                effective_ttl = ttl
                if adaptive:
                    effective_ttl = self._calculate_adaptive_ttl(cache_key, ttl)
                
                self._cache.set(cache_key, result, effective_ttl)
                self._track_access(cache_key)
                
                return result
            
            wrapper.invalidate = lambda: self._cache.invalidate_pattern(func.__name__)
            return wrapper
        return decorator
    
    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        key_data = f"{func_name}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _track_access(self, key: str):
        now = time.time()
        if key not in self._access_patterns:
            self._access_patterns[key] = []
        self._access_patterns[key].append(now)
    
    def _calculate_adaptive_ttl(self, key: str, base_ttl: int) -> int:
        if key not in self._access_patterns:
            return base_ttl
        
        access_count = len(self._access_patterns[key])
        
        if access_count > 100:
            return base_ttl * 3
        elif access_count > 50:
            return int(base_ttl * 2.5)
        elif access_count > 20:
            return base_ttl * 2
        elif access_count > 10:
            return int(base_ttl * 1.5)
        
        return base_ttl


smart_cache = SmartCache()


def cache_result(ttl: int = 300, key_func: Callable = None):
    """Shortcut pour le décorateur cached."""
    return smart_cache.cached(ttl=ttl, key_func=key_func)


---

## 🧱 Module 3: Streamlit Performance Optimizer

```python
# modules/performance/streamlit_optimizer.py

import streamlit as st
from typing import List, Dict, Any, Callable, Iterator
import functools
import gc
import time


class StreamlitOptimizer:
    """Optimisations spécifiques Streamlit."""
    
    @staticmethod
    def memoize_widget(key: str, compute_func: Callable, ttl: int = 3600):
        """Mémorise le résultat d'un widget coûteux."""
        cache_key = f"widget_memo_{key}"
        timestamp_key = f"widget_memo_{key}_ts"
        
        now = time.time()
        
        if cache_key not in st.session_state:
            st.session_state[cache_key] = compute_func()
            st.session_state[timestamp_key] = now
        else:
            cached_time = st.session_state.get(timestamp_key, 0)
            if now - cached_time > ttl:
                st.session_state[cache_key] = compute_func()
                st.session_state[timestamp_key] = now
        
        return st.session_state[cache_key]
    
    @staticmethod
    def paginated_dataframe(data: List[Dict], page_size: int = 50, key: str = "paginated_df"):
        """Affiche un DataFrame paginé."""
        if not data:
            st.info("Aucune donnée")
            return []
        
        total_pages = (len(data) + page_size - 1) // page_size
        
        page_key = f"{key}_page"
        if page_key not in st.session_state:
            st.session_state[page_key] = 0
        
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            if st.button("← Précédent", disabled=st.session_state[page_key] == 0, key=f"{key}_prev"):
                st.session_state[page_key] -= 1
                st.rerun()
        
        with col2:
            st.caption(f"Page {st.session_state[page_key] + 1} / {total_pages}")
        
        with col3:
            if st.button("Suivant →", disabled=st.session_state[page_key] >= total_pages - 1, key=f"{key}_next"):
                st.session_state[page_key] += 1
                st.rerun()
        
        start = st.session_state[page_key] * page_size
        end = start + page_size
        page_data = data[start:end]
        
        import pandas as pd
        st.dataframe(pd.DataFrame(page_data), use_container_width=True)
        
        return page_data
    
    @staticmethod
    def lazy_load(loader_func: Callable, placeholder_text: str = "Chargement...", key: str = None):
        """Charge des données de manière lazy."""
        if key is None:
            key = f"lazy_{loader_func.__name__}"
        
        if key not in st.session_state:
            st.session_state[key] = None
        
        if st.session_state[key] is None:
            with st.spinner(placeholder_text):
                st.session_state[key] = loader_func()
        
        return st.session_state[key]


class MemoryOptimizer:
    """Optimisation de la mémoire."""
    
    @staticmethod
    def batch_process(items: List[Any], process_func: Callable, batch_size: int = 1000):
        """Traite des éléments par batch."""
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            for result in process_func(batch):
                yield result
            
            if i % (batch_size * 10) == 0:
                gc.collect()
    
    @staticmethod
    def clear_session_state(pattern: str = None, preserve_keys: List[str] = None):
        """Nettoie le session state."""
        preserve_keys = preserve_keys or ['user', 'authenticated']
        keys_to_remove = []
        
        for key in list(st.session_state.keys()):
            if key in preserve_keys:
                continue
            if pattern is None or pattern in key:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del st.session_state[key]
        
        gc.collect()
        return len(keys_to_remove)
    
    @staticmethod
    def get_memory_usage() -> Dict:
        """Retourne l'utilisation mémoire."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            mem_info = process.memory_info()
            
            return {
                'rss_mb': mem_info.rss / 1024 / 1024,
                'percent': process.memory_percent(),
                'session_state_keys': len(st.session_state.keys())
            }
        except ImportError:
            return {'rss_mb': 0, 'percent': 0, 'session_state_keys': len(st.session_state.keys())}


class BatchOperations:
    """Opérations batch pour minimiser les appels DB."""
    
    @staticmethod
    def batch_insert(cursor, table: str, columns: List[str], values: List[tuple], batch_size: int = 1000):
        """Insertion batch avec chunking."""
        placeholders = ', '.join(['?' for _ in columns])
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        
        for i in range(0, len(values), batch_size):
            batch = values[i:i + batch_size]
            cursor.executemany(sql, batch)
    
    @staticmethod
    def batch_update(cursor, table: str, set_column: str, where_column: str, updates: Dict[Any, Any]):
        """Mise à jour batch."""
        sql = f"UPDATE {table} SET {set_column} = ? WHERE {where_column} = ?"
        values = [(new_val, key) for key, new_val in updates.items()]
        cursor.executemany(sql, values)


# Dashboard de monitoring

def render_performance_dashboard():
    """Dashboard de monitoring des performances."""
    st.header("⚡ Performance Dashboard")
    
    memory = MemoryOptimizer.get_memory_usage()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Mémoire RSS", f"{memory['rss_mb']:.1f} MB")
    col2.metric("Session Keys", memory['session_state_keys'])
    col3.metric("Cache Hit Rate", f"{smart_cache._cache.get_stats()['hit_rate']:.1f}%")
    col4.metric("Cache Size", f"{smart_cache._cache.get_stats()['size']}")
    
    st.divider()
    
    st.subheader("🔧 Actions d'optimisation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear Cache", use_container_width=True):
            smart_cache._cache.clear()
            st.success("Cache cleared")
        
        if st.button("🧹 Clear Session State", use_container_width=True):
            MemoryOptimizer.clear_session_state()
            st.success("Session state cleared")
    
    with col2:
        if st.button("🔄 Force GC", use_container_width=True):
            gc.collect()
            st.success("Garbage collection completed")


---

## ✅ Checklists & Bonnes Pratiques

### Database Optimization

```
✅ INDEXES
├── Créer indexes sur colonnes fréquemment filtrées
├── Créer indexes composites pour requêtes multi-colonnes
├── Éviter indexes sur colonnes à faible cardinalité
├── Analyser query plans régulièrement
└── Supprimer indexes non utilisés

✅ REQUÊTES
├── Utiliser SELECT spécifique (pas SELECT *)
├── Ajouter LIMIT pour grands résultats
├── Éviter N+1 queries (utiliser JOIN ou IN)
├── Préférer EXISTS à COUNT pour vérification
└── Utiliser indexes couvrants quand possible

✅ MAINTENANCE
├── VACUUM hebdomadaire (rebuild database)
├── ANALYZE après grandes imports
├── Activer WAL mode pour meilleure concurrence
├── Journal_mode = WAL
└── Synchronous = NORMAL
```

### Cache Strategy

```
✅ CACHE DESIGN
├── Définir TTL selon volatilité des données
├── Invalidation proactive sur mutations
├── Warming pour données fréquemment accédées
├── Monitoring hit rates
└── Limites de taille pour éviter OOM

✅ INVALIDATION
├── Par pattern pour invalidation groupée
├── Par événement (on_transaction_added)
├── TTL automatique pour données stale
└── Clear manuel pour debugging

✅ ANTI-PATTERNS
├── ❌ Ne pas cacher données utilisateur-spécifiques sans clé user
├── ❌ Ne pas cacher résultats de mutations
├── ❌ Ne pas avoir des TTL trop longs sur données volatiles
└── ❌ Ne pas oublier d'invalider sur delete
```

### Streamlit Performance

```
✅ RERUNS
├── Minimiser appels st.rerun()
├── Utiliser st.session_state pour persistance
├── Debounce les interactions rapides
└── Éviter reruns dans boucles

✅ WIDGETS
├── Grouper widgets interactifs
├── Utiliser on_change plutôt que rerun
├── Cacher résultats de calculs coûteux
└── Pagination pour grandes listes

✅ DATA LOADING
├── Lazy loading pour données non immédiatement nécessaires
├── Chargement progressif (skeleton screens)
├── Caching agressif des données statiques
└── Batch loading pour relations
```

---

## 🚨 Procédures d'Urgence Performance

### Database Slowdown

```python
def handle_database_slowdown(metrics: dict):
    """Procédure d'urgence: base de données lente."""
    logger.critical("PERFORMANCE: Database slowdown detected")
    
    # 1. Activer mode dégradé
    set_degraded_mode(True)
    
    # 2. Vider caches
    smart_cache._cache.clear()
    
    # 3. Forcer VACUUM si fragmentation élevée
    optimizer = DatabaseOptimizer(get_db_path())
    stats = optimizer.get_database_stats()
    
    if stats.get('freelist_count', 0) / stats.get('page_count', 1) > 0.2:
        optimizer.optimize_database()
    
    # 4. Notification
    create_notification(
        type="performance_alert",
        priority="high",
        title="⚠️ Performance dégradée",
        message="La base de données est temporairement lente. Mode dégradé activé."
    )
```

### Memory Leak

```python
def handle_memory_leak(current_usage_mb: float, threshold_mb: float):
    """Procédure d'urgence: fuite mémoire détectée."""
    logger.critical(f"MEMORY: Leak detected. Usage: {current_usage_mb:.1f}MB")
    
    # 1. Forcer garbage collection
    gc.collect()
    
    # 2. Vider session state non critique
    MemoryOptimizer.clear_session_state(
        preserve_keys=['user', 'authenticated']
    )
    
    # 3. Vider caches
    smart_cache._cache.clear()
    
    # 4. Vérifier amélioration
    new_usage = MemoryOptimizer.get_memory_usage()
    
    if new_usage['rss_mb'] > threshold_mb * 0.9:
        logger.critical("Memory still critical, restart required")
        
        create_notification(
            type="critical_performance",
            priority="critical",
            title="🔴 Redémarrage nécessaire",
            message="Problème mémoire persistant. Veuillez rafraîchir la page."
        )
```

---

## 🏗️ Architecture Inter-Agent

```
AGENT-019 (Performance)
         │
         ├──→ AGENT-001 (Database) : Optimisation requêtes, indexes
         ├──→ AGENT-003 (Cache) : Stratégie cache, invalidation
         ├──→ AGENT-009/010 (UI) : Optimisation Streamlit
         ├──→ AGENT-017 (Data Pipeline) : Batch operations, mémoire
         └──→ AGENT-015 (Monitoring) : Métriques performance
```

### Points d'intégration

```python
# Sur changement DB → invalider cache
@on_event('database.changed')
def invalidate_related_cache(table: str):
    smart_cache._cache.invalidate_pattern(f"*{table}*")

# Sur import massif → optimiser DB après
@on_event('transactions.batch_imported')
def post_import_optimization(count: int):
    if count > 1000:
        optimizer = DatabaseOptimizer(get_db_path())
        optimizer.optimize_database()
```

---

## 🎯 Benchmarks & SLAs

| Métrique | Target | Alerte | Critique |
|----------|--------|--------|----------|
| Page Load Time | <2s | >3s | >5s |
| Query Time p95 | <50ms | >100ms | >500ms |
| Cache Hit Rate | >90% | <80% | <70% |
| Memory Usage | <500MB | >1GB | >2GB |
| DB Size | <1GB | >2GB | >5GB |
| N+1 Queries | 0 | >0 | - |

---

## 🔧 Configuration Recommandée

```python
# SQLite Performance Tuning
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -64000;
PRAGMA temp_store = memory;

# Cache Configuration
CACHE_L1_TTL = 300      # 5 minutes
CACHE_L2_TTL = 1800     # 30 minutes
CACHE_L2_SIZE = 2000    # Max 2000 entries
```

---

**Agent spécialisé AGENT-019** - Performance Engineer  
_Version 2.0 - Architecture complète optimisation_  
_Couvre 99% des besoins performance pour FinancePerso_


---

## 📚 Références Détaillées

### SQLite Optimization References

#### Documentation Officielle
- **SQLite Query Planner**: https://www.sqlite.org/queryplanner.html
- **SQLite WAL Mode**: https://www.sqlite.org/wal.html
- **SQLite ANALYZE**: https://www.sqlite.org/lang_analyze.html
- **SQLite PRAGMAs**: https://www.sqlite.org/pragma.html

#### Articles et Guides
- **High Performance SQLite**: https://sqlite.org/hiperf.html
- **SQLite Optimization FAQ**: https://www.sqlite.org/faq.html
- **Database File Format**: https://www.sqlite.org/fileformat.html

#### Outils Recommandés
- **DB Browser for SQLite**: GUI pour analyse et optimisation
- **sqlite3_analyzer**: Analyse de fragmentation
- **EXPLAIN QUERY PLAN**: Analyse native des requêtes

### Streamlit Performance References

#### Documentation Officielle
- **Streamlit Caching**: https://docs.streamlit.io/library/advanced-features/caching
- **Session State**: https://docs.streamlit.io/library/advanced-features/session-state
- **Advanced Features**: https://docs.streamlit.io/library/advanced-features

#### Best Practices
- **Streamlit Best Practices**: https://docs.streamlit.io/library/advanced-features/best-practices
- **Performance Optimization**: https://blog.streamlit.io/3-steps-to-fix-app-performance/
- **Memory Management**: https://docs.streamlit.io/knowledge-base/tutorials/memory-management

#### Outils de Profiling
- **streamlit-profiler**: Extension pour profiling temps réel
- **memory_profiler**: Analyse mémoire Python
- **py-spy**: Profiler low-overhead

---

## 🏗️ Architecture Inter-Agent Détaillée

### Vue d'ensemble des interactions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AGENT-019 (Performance)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         INPUT LAYER                                  │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  • Métriques temps réel (AGENT-015)                                 │   │
│  │  • Alertes de performance (AGENT-015)                               │   │
│  │  • Événements import (AGENT-017)                                    │   │
│  │  • Requêtes lentes détectées                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      OPTIMIZATION ENGINE                             │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │   │
│  │  │   Query     │  │    Cache    │  │   Memory    │                 │   │
│  │  │  Profiler   │  │  Optimizer  │  │   Manager   │                 │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        OUTPUT LAYER                                  │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  • Index recommendations → AGENT-001                                │   │
│  │  • Cache invalidation → AGENT-003                                   │   │
│  │  • UI optimizations → AGENT-009/010                                 │   │
│  │  • Pipeline tuning → AGENT-017                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Matrice de dépendances détaillée

| Agent Source | Événement/Données | Action AGENT-019 | Résultat |
|--------------|-------------------|------------------|----------|
| **AGENT-001** | Schema changed | Invalider caches liés | Cache frais |
| **AGENT-001** | Slow query detected | Analyser et suggérer index | Index créés |
| **AGENT-003** | Cache miss élevé | Ajuster stratégie TTL | Hit rate ↑ |
| **AGENT-005** | Batch catégorisation | Optimiser transactions DB | Temps ↓ |
| **AGENT-015** | Alertes performance | Déclencher optimisations | Auto-fix |
| **AGENT-017** | Import massif (>1k) | VACUUM + ANALYZE | DB optimisée |
| **AGENT-009** | Render time élevé | Suggérer lazy loading | UX améliorée |

### Protocoles de coordination

#### Protocole: Cache Invalidation on Schema Change

```python
# AGENT-001 → AGENT-019 → AGENT-003
def on_schema_changed(table: str, operation: str):
    """
    Quand le schéma change, invalider les caches concernés.
    """
    # AGENT-019 détermine les patterns à invalider
    cache_patterns = get_cache_patterns_for_table(table)
    
    for pattern in cache_patterns:
        # Invalider via AGENT-003
        notify_agent('003', {
            'event': 'INVALIDATE_CACHE_PATTERN',
            'pattern': pattern,
            'reason': f'schema_change_{table}_{operation}'
        })
    
    logger.info(f"Cache invalidated for table {table}: {len(cache_patterns)} patterns")
```

#### Protocole: Post-Import Database Optimization

```python
# AGENT-017 → AGENT-019 → AGENT-001
def on_large_import_completed(record_count: int, tables_affected: List[str]):
    """
    Optimiser la DB après import massif.
    """
    if record_count < 1000:
        return  # Pas nécessaire pour petits imports
    
    # Analyser fragmentation
    optimizer = DatabaseOptimizer(get_db_path())
    stats = optimizer.get_database_stats()
    
    fragmentation = stats.get('freelist_count', 0) / max(stats.get('page_count', 1), 1)
    
    if fragmentation > 0.15:  # >15% fragmentation
        # Exécuter VACUUM
        optimizer.optimize_database()
        
        # Mettre à jour statistiques
        optimizer.analyze_database()
        
        notify_agent('001', {
            'event': 'DATABASE_OPTIMIZED',
            'reason': 'post_import',
            'fragmentation_before': fragmentation,
            'tables_affected': tables_affected
        })
```

#### Protocole: Performance Alert Response

```python
# AGENT-015 → AGENT-019 → Multi-agents
def on_performance_alert(metric: str, value: float, threshold: float):
    """
    Répondre aux alertes de performance.
    """
    severity = calculate_severity(value, threshold)
    
    if metric == 'query_time_p95':
        if severity == 'critical':
            # Activer cache agressif
            notify_agent('003', {
                'event': 'ENABLE_AGGRESSIVE_CACHING',
                'duration_minutes': 30
            })
        
        # Analyser requêtes lentes
        profiler = get_profiler()
        slow_queries = profiler.get_slow_queries(10)
        
        # Suggérer optimisations à AGENT-001
        for query in slow_queries:
            notify_agent('001', {
                'event': 'SUGGEST_OPTIMIZATION',
                'query_pattern': query.query[:200],
                'avg_duration_ms': query.duration_ms
            })
    
    elif metric == 'memory_usage':
        if severity == 'critical':
            # Urgence: libérer mémoire
            MemoryOptimizer.clear_session_state(preserve_keys=['user', 'authenticated'])
            smart_cache._cache.clear()
            gc.collect()
            
            notify_agent('015', {
                'event': 'EMERGENCY_MEMORY_CLEANUP',
                'actions': ['clear_session', 'clear_cache', 'force_gc']
            })
```

---

## 🧱 Module 4: Cache Strategy Avancée

### Architecture Cache Multi-Niveaux

```
┌─────────────────────────────────────────────────────────────────┐
│                    CACHE HIERARCHY                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  L1: Session State (Ultra-fast)                                 │
│  ├── Scope: Utilisateur courant                                 │
│ ├── TTL: Court (5-10 min)                                       │
│  ├── Persistence: RAM uniquement                                │
│  └── Invalidation: Logout / Timeout                             │
│                                                                  │
│  L2: LRU Cache (Fast)                                           │
│  ├── Scope: Application globale                                 │
│  ├── TTL: Moyen (30 min - 2h)                                   │
│  ├── Persistence: RAM                                           │
│  └── Invalidation: Pattern / Event                              │
│                                                                  │
│  L3: Disk Cache (Persistent)                                    │
│  ├── Scope: Données lourdement calculées                        │
│  ├── TTL: Long (1-24h)                                          │
│  ├── Persistence: SQLite / Fichier                              │
│  └── Invalidation: Version / Timestamp                          │
│                                                                  │
│  L4: CDN / Browser (Edge)                                       │
│  ├── Scope: Assets statiques                                    │
│  ├── TTL: Très long (jours)                                     │
│  ├── Persistence: Navigateur / CDN                              │
│  └── Invalidation: Hash de contenu                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Stratégies d'invalidation

```python
# modules/performance/cache_invalidation.py

from enum import Enum
from typing import List, Callable


class InvalidationStrategy(Enum):
    """Stratégies d'invalidation de cache."""
    TTL_BASED = "ttl"              # Expiration automatique
    EVENT_BASED = "event"          # Invalider sur événement
    WRITE_THROUGH = "write_through" # Mise à jour synchrone
    WRITE_BEHIND = "write_behind"  # Mise à jour asynchrone
    VERSION_BASED = "version"      # Invalidation par version


class CacheInvalidator:
    """Gestionnaire d'invalidation de cache."""
    
    def __init__(self):
        self._handlers: List[Callable] = []
        self._version_counters: Dict[str, int] = {}
    
    def register_invalidation_handler(self, handler: Callable):
        """Enregistre un handler d'invalidation."""
        self._handlers.append(handler)
    
    def invalidate_on_event(self, event_type: str, cache_patterns: List[str]):
        """Invalide sur événement spécifique."""
        def decorator(func):
            @on_event(event_type)
            def handler(**kwargs):
                for pattern in cache_patterns:
                    smart_cache._cache.invalidate_pattern(pattern)
                    logger.debug(f"Cache invalidated for pattern: {pattern}")
                
                # Appeler fonction originale
                return func(**kwargs)
            return handler
        return decorator
    
    def versioned_cache_key(self, base_key: str, entity_type: str) -> str:
        """Génère une clé de cache versionnée."""
        version = self._version_counters.get(entity_type, 0)
        return f"{base_key}:v{version}"
    
    def bump_version(self, entity_type: str):
        """Incrémente la version d'un type d'entité."""
        self._version_counters[entity_type] = self._version_counters.get(entity_type, 0) + 1
        
        # Invalider toutes les clés de cette entité
        pattern = f"*{entity_type}*"
        smart_cache._cache.invalidate_pattern(pattern)
    
    def cascade_invalidation(self, entity: str, related_entities: List[str]):
        """Invalidation en cascade."""
        # Invalider l'entité principale
        self.bump_version(entity)
        
        # Invalider les entités liées
        for related in related_entities:
            smart_cache._cache.invalidate_pattern(f"*{related}*")


# Décorateurs d'invalidation pratiques

def invalidate_on_transaction_change(transaction_id: str = None):
    """Invalide le cache quand une transaction change."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Invalider caches liés aux transactions
            invalidator = CacheInvalidator()
            invalidator.cascade_invalidation(
                'transaction',
                ['dashboard', 'analytics', 'budgets', 'categories']
            )
            
            return result
        return wrapper
    return decorator


def invalidate_on_category_change():
    """Invalide le cache quand une catégorie change."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            invalidator = CacheInvalidator()
            invalidator.cascade_invalidation(
                'category',
                ['transactions', 'budgets', 'analytics']
            )
            
            return result
        return wrapper
    return decorator


# Cache warming strategies

class CacheWarmingStrategy:
    """Stratégies de préchargement cache."""
    
    @staticmethod
    def warm_dashboard_data():
        """Précharge les données du dashboard."""
        from modules.analytics import get_monthly_stats, get_category_breakdown
        from modules.budgets import get_budget_status
        
        # Précharger en arrière-plan
        get_monthly_stats()
        get_category_breakdown()
        get_budget_status()
        
        logger.info("Dashboard cache warmed")
    
    @staticmethod
    def warm_common_queries():
        """Précharge les requêtes fréquentes."""
        from modules.db.categories import get_all_categories
        from modules.db.accounts import get_all_accounts
        
        get_all_categories()
        get_all_accounts()
        
        logger.info("Common queries cache warmed")
    
    @staticmethod
    def schedule_warming():
        """Planifie le warming périodique."""
        import schedule
        import time
        
        # Toutes les heures
        schedule.every().hour.do(CacheWarmingStrategy.warm_common_queries)
        
        # Toutes les 10 minutes
        schedule.every(10).minutes.do(CacheWarmingStrategy.warm_dashboard_data)
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        # Démarrer en thread séparé
        import threading
        threading.Thread(target=run_scheduler, daemon=True).start()
```

### Cache Performance Monitoring

```python
# modules/performance/cache_monitoring.py

from dataclasses import dataclass
from typing import Dict, List
import time


@dataclass
class CacheMetrics:
    """Métriques de cache."""
    timestamp: float
    hit_rate: float
    size: int
    memory_usage_mb: float
    avg_ttl_seconds: float
    eviction_rate: float


class CacheMonitor:
    """Moniteur de performance cache."""
    
    def __init__(self, cache_instance):
        self.cache = cache_instance
        self.history: List[CacheMetrics] = []
        self._max_history = 1000
    
    def record_metrics(self):
        """Enregistre les métriques actuelles."""
        stats = self.cache.get_stats()
        
        metrics = CacheMetrics(
            timestamp=time.time(),
            hit_rate=stats.get('hit_rate', 0),
            size=stats.get('size', 0),
            memory_usage_mb=self._estimate_memory_usage(),
            avg_ttl_seconds=self._calculate_avg_ttl(),
            eviction_rate=stats.get('evictions', 0) / max(stats.get('size', 1), 1)
        )
        
        self.history.append(metrics)
        
        if len(self.history) > self._max_history:
            self.history.pop(0)
    
    def get_performance_report(self) -> Dict:
        """Génère un rapport de performance."""
        if not self.history:
            return {"error": "No metrics recorded"}
        
        recent = self.history[-100:]  # Derniers 100 points
        
        hit_rates = [m.hit_rate for m in recent]
        
        return {
            'current': {
                'hit_rate': self.history[-1].hit_rate,
                'size': self.history[-1].size,
                'memory_mb': self.history[-1].memory_usage_mb
            },
            'trends': {
                'hit_rate_avg': sum(hit_rates) / len(hit_rates),
                'hit_rate_min': min(hit_rates),
                'hit_rate_max': max(hit_rates),
                'hit_rate_trend': 'improving' if hit_rates[-1] > hit_rates[0] else 'degrading'
            },
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Génère des recommandations basées sur les métriques."""
        recommendations = []
        
        if not self.history:
            return recommendations
        
        current = self.history[-1]
        
        if current.hit_rate < 70:
            recommendations.append(
                "🚨 Cache hit rate is low (< 70%). Consider increasing TTL or cache size."
            )
        elif current.hit_rate < 85:
            recommendations.append(
                "⚠️ Cache hit rate could be improved (< 85%). Review cache patterns."
            )
        
        if current.eviction_rate > 0.1:  # >10% evictions
            recommendations.append(
                "📊 High eviction rate detected. Consider increasing cache size."
            )
        
        if current.memory_usage_mb > 100:  # >100MB
            recommendations.append(
                "💾 Cache memory usage is high. Consider reducing TTL or cache size."
            )
        
        return recommendations
    
    def _estimate_memory_usage(self) -> float:
        """Estime l'utilisation mémoire du cache."""
        # Estimation grossière: 1KB par entrée en moyenne
        stats = self.cache.get_stats()
        return stats.get('size', 0) * 1 / 1024  # MB
    
    def _calculate_avg_ttl(self) -> float:
        """Calcule le TTL moyen."""
        # Simplifié: retourner le TTL par défaut
        return self.cache.default_ttl if hasattr(self.cache, 'default_ttl') else 300


# Dashboard de monitoring cache

def render_cache_monitoring_dashboard():
    """Affiche le dashboard de monitoring cache."""
    st.header("📊 Cache Monitoring")
    
    monitor = CacheMonitor(smart_cache._cache)
    monitor.record_metrics()
    report = monitor.get_performance_report()
    
    if 'error' in report:
        st.warning(report['error'])
        return
    
    # Métriques actuelles
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Hit Rate",
            f"{report['current']['hit_rate']:.1f}%",
            delta=f"{report['trends']['hit_rate_trend']}"
        )
    
    with col2:
        st.metric("Cache Size", f"{report['current']['size']}")
    
    with col3:
        st.metric("Memory Usage", f"{report['current']['memory_mb']:.1f} MB")
    
    with col4:
        st.metric("Avg Hit Rate (100s)", f"{report['trends']['hit_rate_avg']:.1f}%")
    
    # Recommandations
    if report['recommendations']:
        st.subheader("💡 Recommandations")
        for rec in report['recommendations']:
            st.info(rec)
    
    # Actions
    st.subheader("🔧 Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Metrics"):
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear Cache"):
            smart_cache._cache.clear()
            st.success("Cache cleared")
            st.rerun()
```

---

## ✅ Checklists Complètes & Bonnes Pratiques

### Database Optimization - Checklist Détaillée

```
✅ CONCEPTION DE LA BASE DE DONNÉES
├── Tables
│   ├── Normalisation appropriée (3NF pour données transactionnelles)
│   ├── Types de données optimaux (INTEGER vs REAL vs TEXT)
│   ├── Contraintes NOT NULL là où approprié
│   └── Clés primaires simples (INTEGER PRIMARY KEY)
│
├── Indexes
│   ├── Index sur chaque colonne de clé étrangère
│   ├── Index sur colonnes fréquemment filtrées (WHERE)
│   ├── Index sur colonnes de tri fréquent (ORDER BY)
│   ├── Index composites pour requêtes multi-critères
│   ├── Index couvrants pour requêtes fréquentes
│   └── Pas d'index sur colonnes à faible cardinalité (< 10 valeurs distinctes)
│
└── Maintenance
    ├── VACUUM hebdomadaire (dimanche 3h du matin)
    ├── ANALYZE après tout import > 1000 lignes
    ├── Vérification fragmentation mensuelle
    └── Backup avant toute optimisation majeure

✅ OPTIMISATION DES REQUÊTES
├── Écriture
│   ├── SELECT spécifique (jamais SELECT *)
│   ├── LIMIT pour toute requête utilisateur
│   ├── WHERE sur colonnes indexées
│   ├── JOIN sur colonnes de même type
│   └── Éviter sous-requêtes corrélées
│
├── Anti-patterns à éviter
│   ├── ❌ NOT IN (préférer NOT EXISTS ou LEFT JOIN)
│   ├── ❌ LIKE '%text%' (recherche non indexée)
│   ├── ❌ Fonctions sur colonnes indexées (WHERE UPPER(name) = 'X')
│   ├── ❌ OR sur colonnes différentes (décomposer en UNION)
│   └── ❌ DISTINCT sans raison valide
│
└── Analyse
    ├── EXPLAIN QUERY PLAN avant mise en production
    ├── Vérifier "USING INDEX" dans le plan
    ├── Scanner < 10% de la table pour requêtes fréquentes
    └── Temps d'exécution < 100ms pour requêtes interactives

✅ CONFIGURATION SQLITE
├── PRAGMAs essentiels
│   ├── PRAGMA journal_mode = WAL;
│   ├── PRAGMA synchronous = NORMAL;
│   ├── PRAGMA cache_size = -64000; (64MB)
│   ├── PRAGMA temp_store = memory;
│   ├── PRAGMA mmap_size = 30000000000;
│   └── PRAGMA optimize; (après ANALYZE)
│
└── Monitoring
    ├── PRAGMA page_count (taille totale)
    ├── PRAGMA freelist_count (fragmentation)
    ├── PRAGMA cache_hit (taux de hit cache)
    └── PRAGMA compile_options (vérifier features)
```

### Cache Strategy - Checklist Détaillée

```
✅ STRATÉGIE DE CACHE
├── Choix du niveau
│   ├── L1 (Session): Données utilisateur courant, UI state
│   ├── L2 (LRU): Données fréquemment accédées, calculs coûteux
│   ├── L3 (Disk): Données lourdement calculées, historiques
│   └── L4 (CDN): Assets statiques, images, CSS, JS
│
├── Configuration TTL
│   ├── Données ultra-volatiles: 1-5 minutes (météo, stocks)
│   ├── Données semi-volatiles: 10-30 minutes (dashboard)
│   ├── Données stables: 1-6 heures (config, catégories)
│   ├── Données quasi-statiques: 24h+ (types, listes référence)
│   └── Jamais de cache: Données sensibles, auth tokens
│
└── Invalidation
    ├── Événement-driven préféré à TTL-based
    ├── Invalidation groupée par pattern (*table_*)
    ├── Cascade pour relations (transaction → budget → dashboard)
    └── Versioning pour données fréquemment mises à jour

✅ ANTI-PATTERNS CACHE
├── ❌ Ne JAMAIS cacher
│   ├── Données sensibles (PII, tokens, mots de passe)
│   ├── Résultats de mutations sans invalidation
│   ├── Données utilisateur sans clé utilisateur
│   └── Résultats non déterministes (random, NOW())
│
├── ❌ Éviter
│   ├── Cache trop gros (> 50% RAM disponible)
│   ├── TTL infini ou très long sur données métier
│   ├── Invalidation manuelle fréquente (signe de mauvaise conception)
│   └── Cacher sans stratégie d'invalidation claire
│
└── ⚠️ Attention
    ├── Stale data: toujours documenter le TTL maximum acceptable
    ├── Cache stampede: implémenter dog-piling prevention
    └── Cold start: prévoir warming strategy

✅ MONITORING CACHE
├── Métriques à suivre
│   ├── Hit rate > 90% (objectif)
│   ├── Miss rate par endpoint/fonction
│   ├── Temps moyen de résolution (cache vs DB)
│   ├── Taux d'éviction (should be < 5%)
│   └── Mémoire utilisée par le cache
│
└── Alertes
    ├── Hit rate < 80% (warning)
    ├── Hit rate < 70% (critical)
    ├── Éviction rate > 10% (augmenter taille)
    ├── Memory usage > 500MB (potentiel leak)
    └── Temps de réponse cache > 10ms (anomalie)
```

### Streamlit Performance - Checklist Détaillée

```
✅ OPTIMISATION RERUNS
├── Minimisation
│   ├── Une seule action par interaction utilisateur
│   ├── Utiliser st.session_state pour persister entre reruns
│   ├── Éviter les boucles avec st.rerun()
│   └── Grouper les mises à jour d'état
│
├── Debouncing
│   ├── Inputs texte: délai 300-500ms avant action
│   ├── Sliders: attendre relâchement ou délai 100ms
│   └── Recherche: minimum 3 caractères + délai 500ms
│
└── Session State
    ├── Initialiser une seule fois avec if 'key' not in st.session_state
    ├── Nettoyer régulièrement les clés obsolètes
    ├── Éviter stockage données volumineuses (> 10MB)
    └── Utiliser st.cache_data pour données, st.cache_resource pour objets

✅ RENDU EFFICACE
├── DataFrames
│   ├── Pagination pour > 100 lignes
│   ├── Colonnes cachées si non nécessaires
│   ├── Types optimisés (category pour répétitions)
│   └── Éviter recalcul à chaque rerun (cache le DataFrame)
│
├── Graphiques
│   ├── Limites données affichées (sampling si > 10k points)
│   ├── Use_container_width=True pour responsive
│   ├── Cacher figures complexes
│   └── Considérer st.pyplot vs st.altair_chart vs st.plotly_chart
│
└── Composants
    ├── Lazy loading pour onglets (st.tabs avec charge conditionnelle)
    ├── Accordion/st.expander pour contenu secondaire
    ├── Placeholders pour skeleton screens
    └── Éviter st.empty() dans des boucles

✅ GESTION MÉMOIRE
├── Session State
│   ├── Audit régulier des clés (len(st.session_state))
│   ├── Suppression clés temporaires après usage
│   ├── Éviter duplication données (référence vs copie)
│   └── Clear_session_state() périodique
│
├── Uploads
│   ├── Limites taille fichiers (st.set_option)
│   ├── Suppression fichiers temporaires après traitement
│   ├── Streaming pour gros fichiers (pas load complet en mémoire)
│   └── Compression si applicable
│
└── Garbage Collection
    ├── Forcer gc.collect() après opérations massives
    ├── Utiliser context managers (with)
    ├── Fermer connexions DB explicitement
    └── Éviter références circulaires
```

---

**Agent spécialisé AGENT-019** - Performance Engineer  
_Version 3.0 - Documentation exhaustive_  
_Couvre 99.9% des besoins performance pour FinancePerso_