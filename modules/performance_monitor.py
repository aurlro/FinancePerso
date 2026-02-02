"""
Performance Monitoring & Optimization
Outils pour monitorer et optimiser les performances de l'application.
"""

import time
import functools
import streamlit as st
from typing import Callable, Any, Optional
from contextlib import contextmanager
from datetime import datetime
import pandas as pd

from modules.logger import logger


class PerformanceMonitor:
    """Moniteur de performance pour les opérations critiques."""
    
    def __init__(self):
        self.metrics = {}
    
    def time_operation(self, operation_name: str):
        """Décorateur pour mesurer le temps d'une opération."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start_time
                    
                    # Stocker la métrique
                    if operation_name not in self.metrics:
                        self.metrics[operation_name] = []
                    self.metrics[operation_name].append({
                        'timestamp': datetime.now(),
                        'duration': elapsed,
                        'status': 'success'
                    })
                    
                    # Logger si trop lent
                    if elapsed > 2.0:
                        logger.warning(f"Slow operation: {operation_name} took {elapsed:.2f}s")
                    
                    return result
                except Exception as e:
                    elapsed = time.time() - start_time
                    self.metrics[operation_name].append({
                        'timestamp': datetime.now(),
                        'duration': elapsed,
                        'status': 'error',
                        'error': str(e)
                    })
                    raise
            return wrapper
        return decorator
    
    @contextmanager
    def measure(self, operation_name: str):
        """Context manager pour mesurer une opération."""
        start_time = time.time()
        try:
            yield
        finally:
            elapsed = time.time() - start_time
            if operation_name not in self.metrics:
                self.metrics[operation_name] = []
            self.metrics[operation_name].append({
                'timestamp': datetime.now(),
                'duration': elapsed,
                'status': 'success'
            })
            
            if elapsed > 2.0:
                logger.warning(f"Slow operation: {operation_name} took {elapsed:.2f}s")
    
    def get_summary(self) -> pd.DataFrame:
        """Retourne un résumé des performances."""
        data = []
        for op_name, measurements in self.metrics.items():
            if measurements:
                durations = [m['duration'] for m in measurements]
                data.append({
                    'Operation': op_name,
                    'Count': len(measurements),
                    'Avg (s)': sum(durations) / len(durations),
                    'Min (s)': min(durations),
                    'Max (s)': max(durations),
                    'Last (s)': durations[-1]
                })
        
        return pd.DataFrame(data) if data else pd.DataFrame()


# Instance globale
_perf_monitor = PerformanceMonitor()

def get_performance_monitor() -> PerformanceMonitor:
    """Récupère l'instance globale du moniteur."""
    return _perf_monitor


class LazyLoader:
    """Chargeur paresseux pour les widgets lourds."""
    
    def __init__(self, placeholder_text: str = "Chargement..."):
        self.placeholder_text = placeholder_text
        self.loaded = False
    
    def render(self, render_fn: Callable, *args, **kwargs):
        """Rend un widget avec lazy loading."""
        if not self.loaded:
            with st.spinner(self.placeholder_text):
                result = render_fn(*args, **kwargs)
                self.loaded = True
                return result
        else:
            return render_fn(*args, **kwargs)


def smart_cache_data(ttl: int = 600, max_entries: int = 10):
    """
    Cache intelligent avec invalidation conditionnelle.
    
    Args:
        ttl: Durée de vie du cache en secondes
        max_entries: Nombre maximum d'entrées à conserver
    """
    def decorator(func: Callable) -> Callable:
        # Utiliser le cache natif de Streamlit avec gestion supplémentaire
        cached_func = st.cache_data(ttl=ttl, max_entries=max_entries)(func)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Clé de cache basée sur les arguments
            cache_key = f"{func.__name__}_{hash(str(args))}_{hash(str(kwargs))}"
            
            # Vérifier si invalidation demandée
            invalidate_key = f"invalidate_{cache_key}"
            if invalidate_key in st.session_state and st.session_state[invalidate_key]:
                st.cache_data.clear()
                st.session_state[invalidate_key] = False
            
            return cached_func(*args, **kwargs)
        
        wrapper.clear_cache = lambda: st.cache_data.clear()
        return wrapper
    return decorator


def invalidate_cache(cache_key: str):
    """Invalide une entrée de cache spécifique."""
    st.session_state[f"invalidate_{cache_key}"] = True


@contextmanager
def loading_skeleton(height: int = 200, text: str = "Chargement des données..."):
    """Affiche un skeleton pendant le chargement."""
    placeholder = st.empty()
    
    # Skeleton HTML
    skeleton_html = f"""
    <div style="
        height: {height}px;
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #666;
    ">
        {text}
    </div>
    <style>
        @keyframes loading {{
            0% {{ background-position: 200% 0; }}
            100% {{ background-position: -200% 0; }}
        }}
    </style>
    """
    
    placeholder.markdown(skeleton_html, unsafe_allow_html=True)
    
    try:
        yield placeholder
    finally:
        placeholder.empty()


def render_performance_dashboard():
    """Affiche un dashboard de performance pour le debug."""
    st.subheader("🔍 Performance Dashboard")
    
    monitor = get_performance_monitor()
    summary = monitor.get_summary()
    
    if not summary.empty:
        st.dataframe(summary, use_container_width=True)
        
        # Alertes sur opérations lentes
        slow_ops = summary[summary['Max (s)'] > 2.0]
        if not slow_ops.empty:
            st.warning("⚠️ Opérations lentes détectées (> 2s)")
            for _, row in slow_ops.iterrows():
                st.write(f"- {row['Operation']}: {row['Max (s)']:.2f}s max")
    else:
        st.info("Aucune métrique de performance disponible")
    
    # Bouton de clear cache
    if st.button("🗑️ Vider tous les caches"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("Caches vidés !")


__all__ = [
    'PerformanceMonitor',
    'get_performance_monitor',
    'LazyLoader',
    'smart_cache_data',
    'invalidate_cache',
    'loading_skeleton',
    'render_performance_dashboard'
]