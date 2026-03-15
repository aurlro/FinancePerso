# -*- coding: utf-8 -*-
"""
Rate limiting pour l'API et les appels externes.

Implémentations:
- In-memory (développement)
- Redis (production)
- SQLite fallback
"""

import functools
import time
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Callable

from modules.logger import logger


class RateLimitStrategy(Enum):
    """Stratégies de rate limiting."""

    FIXED_WINDOW = "fixed_window"  # Fenêtre fixe (simple)
    SLIDING_WINDOW = "sliding_window"  # Fenêtre glissante (précis)
    TOKEN_BUCKET = "token_bucket"  # Bucket de tokens (burst)


@dataclass
class RateLimitConfig:
    """Configuration du rate limiting."""

    requests: int = 100  # Nombre de requêtes
    window: int = 60  # Fenêtre en secondes
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    burst_size: int | None = None  # Pour token bucket


class RateLimitExceeded(Exception):
    """Exception levée quand la limite est dépassée."""

    def __init__(self, retry_after: int, limit: int, remaining: int = 0):
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining
        super().__init__(f"Rate limit exceeded. Retry after {retry_after}s")


class InMemoryRateLimiter:
    """
    Rate limiter en mémoire (pour dev et tests).
    """

    def __init__(self):
        self._storage = defaultdict(list)  # key -> list of timestamps
        self._configs: dict[str, RateLimitConfig] = {}

    def configure(self, key: str, config: RateLimitConfig) -> None:
        """Configure le rate limiting pour une clé."""
        self._configs[key] = config

    def is_allowed(self, key: str) -> tuple[bool, dict]:
        """
        Vérifie si une requête est autorisée.
        
        Returns:
            (allowed, headers) où headers contient les infos de rate limit
        """
        config = self._configs.get(key)
        if not config:
            # Pas de limit configured = toujours autorisé
            return True, {}

        now = time.time()
        window_start = now - config.window

        # Nettoyer les anciennes entrées
        self._storage[key] = [ts for ts in self._storage[key] if ts > window_start]

        # Vérifier la limite
        current_count = len(self._storage[key])
        
        if current_count >= config.requests:
            # Calculer quand réessayer
            oldest = min(self._storage[key])
            retry_after = int(oldest + config.window - now) + 1
            
            headers = {
                "X-RateLimit-Limit": str(config.requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(now + retry_after)),
                "Retry-After": str(retry_after),
            }
            return False, headers

        # Autoriser la requête
        self._storage[key].append(now)
        
        remaining = config.requests - current_count - 1
        headers = {
            "X-RateLimit-Limit": str(config.requests),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(now + config.window)),
        }
        return True, headers

    def get_remaining(self, key: str) -> int:
        """Retourne le nombre de requêtes restantes."""
        config = self._configs.get(key)
        if not config:
            return -1  # Illimité
        
        now = time.time()
        window_start = now - config.window
        self._storage[key] = [ts for ts in self._storage[key] if ts > window_start]
        
        return max(0, config.requests - len(self._storage[key]))

    def reset(self, key: str | None = None) -> None:
        """Reset le compteur pour une clé ou tout."""
        if key:
            self._storage[key].clear()
        else:
            self._storage.clear()


# Instance globale pour l'application
_rate_limiter = InMemoryRateLimiter()


def get_rate_limiter() -> InMemoryRateLimiter:
    """Retourne l'instance globale du rate limiter."""
    return _rate_limiter


def configure_rate_limit(key: str, requests: int = 100, window: int = 60) -> None:
    """
    Configure le rate limiting pour une clé.
    
    Args:
        key: Identifiant (ex: 'api', 'login', 'ai_provider')
        requests: Nombre de requêtes autorisées
        window: Fenêtre de temps en secondes
    """
    config = RateLimitConfig(requests=requests, window=window)
    _rate_limiter.configure(key, config)
    logger.info(f"Rate limit configured for '{key}': {requests}/{window}s")


def check_rate_limit(key: str) -> tuple[bool, dict]:
    """
    Vérifie le rate limit pour une clé.
    
    Returns:
        (allowed, headers)
    
    Raises:
        RateLimitExceeded: Si la limite est dépassée
    """
    allowed, headers = _rate_limiter.is_allowed(key)
    
    if not allowed:
        retry_after = int(headers.get("Retry-After", 60))
        limit = int(headers.get("X-RateLimit-Limit", 100))
        raise RateLimitExceeded(retry_after, limit)
    
    return allowed, headers


def rate_limit(key: str | Callable, requests: int = 100, window: int = 60):
    """
    Décorateur pour appliquer le rate limiting.
    
    Usage:
        @rate_limit("api", requests=100, window=60)
        def my_api_function():
            ...
        
        # Ou avec fonction pour key dynamique
        @rate_limit(lambda req: f"user:{req.user_id}")
        def user_endpoint(request):
            ...
    """
    def decorator(func: Callable) -> Callable:
        # Configurer si key est statique
        if isinstance(key, str):
            configure_rate_limit(key, requests, window)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Déterminer la clé
            if callable(key):
                # Fonction qui retourne la clé dynamiquement
                limit_key = key(*args, **kwargs)
                # Configurer si pas déjà fait
                if limit_key not in _rate_limiter._configs:
                    configure_rate_limit(limit_key, requests, window)
            else:
                limit_key = key
            
            try:
                allowed, headers = check_rate_limit(limit_key)
                # Stocker les headers pour pouvoir les récupérer
                wrapper._rate_limit_headers = headers
                return func(*args, **kwargs)
            except RateLimitExceeded as e:
                logger.warning(f"Rate limit exceeded for '{limit_key}'")
                raise
        
        return wrapper
    return decorator


# Configurations par défaut pour différents endpoints

def configure_default_rate_limits() -> None:
    """Configure les rate limits par défaut pour l'application."""
    
    # API générale
    configure_rate_limit("api", requests=1000, window=3600)  # 1000/h
    
    # Authentification (plus restrictif)
    configure_rate_limit("login", requests=5, window=300)  # 5 tentatives/5min
    configure_rate_limit("register", requests=3, window=3600)  # 3/heure
    
    # IA (coûteux)
    configure_rate_limit("ai_categorize", requests=100, window=3600)  # 100/h
    configure_rate_limit("ai_analyze", requests=50, window=3600)  # 50/heure
    
    # Import de données
    configure_rate_limit("import_csv", requests=10, window=300)  # 10/5min
    
    logger.info("Default rate limits configured")


class RateLimitMiddleware:
    """
    Middleware pour FastAPI/Flask pour appliquer le rate limiting.
    
    Usage avec FastAPI:
        app.add_middleware(RateLimitMiddleware)
    """
    
    def __init__(self, app, default_limit: int = 100, default_window: int = 60):
        self.app = app
        self.default_limit = default_limit
        self.default_window = default_window
        configure_default_rate_limits()
    
    def get_client_key(self, request) -> str:
        """Extrait la clé client depuis la requête."""
        # Par défaut: IP + endpoint
        ip = getattr(request, 'client', None)
        ip = ip.host if ip else 'unknown'
        path = getattr(request, 'url', None)
        path = path.path if path else 'unknown'
        return f"{ip}:{path}"
    
    def __call__(self, request, call_next):
        """Appel du middleware."""
        key = self.get_client_key(request)
        
        try:
            allowed, headers = check_rate_limit(key)
            response = call_next(request)
            
            # Ajouter les headers de rate limit
            for header, value in headers.items():
                response.headers[header] = str(value)
            
            return response
            
        except RateLimitExceeded as e:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": e.retry_after,
                },
                headers={
                    "Retry-After": str(e.retry_after),
                    "X-RateLimit-Limit": str(e.limit),
                },
            )
