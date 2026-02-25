# AGENT-007: AI Provider Manager

## 🎯 Mission

Architecte du systeme multi-providers IA de FinancePerso. Responsable de l'abstraction des providers (Gemini, OpenAI, DeepSeek, Ollama), de la gestion des fallbacks, du rate limiting et de la resilience. Garant de la disponibilite du service IA.

---

## 📚 Contexte: Architecture Multi-Providers

### Philosophie
> "L'IA est un service, pas une dependance. Un provider down ne doit jamais bloquer l'utilisateur."

### Architecture Providers

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AI PROVIDER ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    AI Manager v2                              │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │  │
│  │  │  Primary    │→ │  Fallback   │→ │  Emergency          │  │  │
│  │  │  Provider   │  │  Provider   │  │  (Local/Ollama)     │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘  │  │
│  │                                                              │  │
│  │  Features:                                                   │  │
│  │  • Rate limiting (min 500ms entre calls)                     │  │
│  │  • Retry avec backoff                                        │  │
│  │  • Circuit breaker                                           │  │
│  │  • Cost tracking                                             │  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│         ┌────────────────────┼────────────────────┐                 │
│         ↓                    ↓                    ↓                 │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐         │
│  │   Gemini    │      │   OpenAI    │      │  DeepSeek   │         │
│  │  (Google)   │      │  (ChatGPT)  │      │  (Budget)   │         │
│  └─────────────┘      └─────────────┘      └─────────────┘         │
│         ↑                                                           │
│  ┌─────────────┐                                                    │
│  │   Ollama    │  ← 100% Local, Fallback ultime                    │
│  │   (Local)   │                                                    │
│  └─────────────┘                                                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Comparaison Providers

| Provider | Latence | Cout | Qualite | Offline | Fallback |
|----------|---------|------|---------|---------|----------|
| **Gemini** | ~300ms | Gratuit | Tres bon | Non | Primary |
| **OpenAI** | ~500ms | Payant | Excellent | Non | Secondary |
| **DeepSeek** | ~800ms | Bon marche | Tres bon | Non | Tertiary |
| **Ollama** | ~2000ms | Gratuit | Bon | **Oui** | Emergency |

---

## 🔌 Module 1: Provider Abstraction

### Base Provider Class

```python
from abc import ABC, abstractmethod
from typing import Any

class AIProvider(ABC):
    """Classe abstraite pour tous les providers IA."""
    
    @abstractmethod
    def generate_text(self, prompt: str, model_name: str = None) -> str:
        """Genere du texte a partir d'un prompt."""
        pass
    
    @abstractmethod
    def generate_json(self, prompt: str, model_name: str = None) -> dict[str, Any]:
        """Genere une reponse JSON structuree."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Verifie si le provider est disponible."""
        pass
    
    @abstractmethod
    def get_cost_estimate(self, prompt: str) -> float:
        """Estime le cout de la requete (en USD)."""
        pass

class GeminiProvider(AIProvider):
    """Provider Google Gemini."""
    
    def __init__(self, api_key: str):
        from google import genai
        self.client = genai.Client(api_key=api_key)
        self.default_model = "gemini-2.0-flash"
    
    def generate_text(self, prompt: str, model_name: str = None) -> str:
        model = model_name or self.default_model
        
        response = self.client.models.generate_content(
            model=model,
            contents=prompt
        )
        
        return response.text
    
    def generate_json(self, prompt: str, model_name: str = None) -> dict:
        import json
        
        # Ajouter instruction JSON
        json_prompt = f"{prompt}\n\nReponds UNIQUEMENT en JSON valide."
        
        text = self.generate_text(json_prompt, model_name)
        
        # Parser JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Extraire JSON du texte
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise
    
    def is_available(self) -> bool:
        try:
            self.generate_text("test", model_name=self.default_model)
            return True
        except Exception:
            return False
    
    def get_cost_estimate(self, prompt: str) -> float:
        # Gemini est gratuit dans les limites
        return 0.0

class OpenAIProvider(AIProvider):
    """Provider OpenAI."""
    
    def __init__(self, api_key: str):
        import openai
        self.client = openai.OpenAI(api_key=api_key)
        self.default_model = "gpt-3.5-turbo"
    
    def generate_text(self, prompt: str, model_name: str = None) -> str:
        model = model_name or self.default_model
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content
    
    def generate_json(self, prompt: str, model_name: str = None) -> dict:
        import json
        
        # Utiliser mode JSON d'OpenAI
        response = self.client.chat.completions.create(
            model=model_name or self.default_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def is_available(self) -> bool:
        try:
            self.client.models.list()
            return True
        except Exception:
            return False
    
    def get_cost_estimate(self, prompt: str) -> float:
        # Estimation: $0.0015 / 1K tokens input
        tokens = len(prompt.split()) * 1.3  # Estimation grossiere
        return (tokens / 1000) * 0.0015

class OllamaProvider(AIProvider):
    """Provider Ollama (local)."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.default_model = "llama3.2"
    
    def generate_text(self, prompt: str, model_name: str = None) -> str:
        import requests
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": model_name or self.default_model,
                "prompt": prompt,
                "stream": False
            }
        )
        
        return response.json()["response"]
    
    def generate_json(self, prompt: str, model_name: str = None) -> dict:
        import json
        
        json_prompt = f"{prompt}\n\nReponds UNIQUEMENT en JSON."
        text = self.generate_text(json_prompt, model_name)
        
        return json.loads(text)
    
    def is_available(self) -> bool:
        import requests
        try:
            requests.get(f"{self.base_url}/api/tags", timeout=2)
            return True
        except Exception:
            return False
    
    def get_cost_estimate(self, prompt: str) -> float:
        # Gratuit (local)
        return 0.0
```

### Factory Pattern

```python
class ProviderFactory:
    """Factory pour creer les providers."""
    
    PROVIDERS = {
        'gemini': GeminiProvider,
        'openai': OpenAIProvider,
        'deepseek': DeepSeekProvider,
        'ollama': OllamaProvider
    }
    
    @classmethod
    def create(cls, provider_name: str, config: dict) -> AIProvider:
        """Cree un provider."""
        provider_class = cls.PROVIDERS.get(provider_name)
        
        if not provider_class:
            raise ValueError(f"Provider inconnu: {provider_name}")
        
        return provider_class(**config)
    
    @classmethod
    def list_available(cls) -> list[str]:
        """Liste les providers disponibles."""
        return list(cls.PROVIDERS.keys())
```

---

## 🛡️ Module 2: Resilience & Fallback

### Circuit Breaker

```python
"""
Pattern Circuit Breaker pour eviter les cascades de failures.
"""

from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"      # Fonctionnement normal
    OPEN = "open"          # En erreur, rejette les requetes
    HALF_OPEN = "half_open"  # Test de recovery

class CircuitBreaker:
    """Circuit breaker pour provider IA."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_max_calls: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
    
    def call(self, func, *args, **kwargs):
        """Execute une fonction avec circuit breaker."""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
            else:
                raise Exception("Circuit breaker is OPEN")
        
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls >= self.half_open_max_calls:
                raise Exception("Circuit breaker HALF_OPEN limit reached")
            self.half_open_calls += 1
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Gere succes."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_max_calls:
                # Recovery complete
                self._reset()
        else:
            self.failure_count = max(0, self.failure_count - 1)
    
    def _on_failure(self):
        """Gere echec."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            # Echec recovery, re-ouvrir
            self.state = CircuitState.OPEN
        elif self.failure_count >= self.failure_threshold:
            # Ouvrir circuit
            self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Verifie si tentative recovery possible."""
        if not self.last_failure_time:
            return True
        
        elapsed = (datetime.now() - self.last_failure_time).seconds
        return elapsed >= self.recovery_timeout
    
    def _reset(self):
        """Reset le circuit."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0
        self.last_failure_time = None
```

### Multi-Provider Manager

```python
class MultiProviderManager:
    """Gestionnaire multi-providers avec fallback."""
    
    def __init__(self):
        self.providers: dict[str, AIProvider] = {}
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self.priority_order: list[str] = []
        
        # Initialiser depuis config
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialise les providers depuis .env."""
        import os
        
        # Configuration
        configs = {
            'gemini': {'api_key': os.getenv('GEMINI_API_KEY')},
            'openai': {'api_key': os.getenv('OPENAI_API_KEY')},
            'deepseek': {'api_key': os.getenv('DEEPSEEK_API_KEY')},
            'ollama': {'base_url': os.getenv('OLLAMA_URL', 'http://localhost:11434')}
        }
        
        # Ordre de priorite
        self.priority_order = ['gemini', 'openai', 'deepseek', 'ollama']
        
        # Creer providers
        for name in self.priority_order:
            if configs[name].get('api_key') or name == 'ollama':
                try:
                    self.providers[name] = ProviderFactory.create(name, configs[name])
                    self.circuit_breakers[name] = CircuitBreaker()
                except Exception as e:
                    logger.warning(f"Failed to initialize {name}: {e}")
    
    def generate_with_fallback(
        self,
        prompt: str,
        prefer_provider: str = None
    ) -> tuple[str, str]:
        """
        Genere avec fallback automatique.
        
        Returns:
            (response, provider_used)
        """
        # Determiner ordre d'essai
        order = self.priority_order.copy()
        
        if prefer_provider and prefer_provider in order:
            order.remove(prefer_provider)
            order.insert(0, prefer_provider)
        
        # Essayer chaque provider
        last_error = None
        
        for provider_name in order:
            if provider_name not in self.providers:
                continue
            
            provider = self.providers[provider_name]
            breaker = self.circuit_breakers[provider_name]
            
            try:
                # Verifier circuit breaker
                result = breaker.call(provider.generate_text, prompt)
                
                logger.info(f"AI call succeeded with {provider_name}")
                return result, provider_name
                
            except Exception as e:
                logger.warning(f"Provider {provider_name} failed: {e}")
                last_error = e
                continue
        
        # Tous les providers ont echoue
        raise Exception(f"All AI providers failed. Last error: {last_error}")
```

### Rate Limiting

```python
"""
Rate limiting pour eviter de depasser les quotas.
"""

import time
from collections import deque

class RateLimiter:
    """Rate limiter par provider."""
    
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.calls: deque[float] = deque()
    
    def acquire(self):
        """Attend si necessaire avant d'appeler."""
        now = time.time()
        
        # Nettoyer vieux appels (> 60s)
        while self.calls and self.calls[0] < now - 60:
            self.calls.popleft()
        
        # Verifier limite
        if len(self.calls) >= self.calls_per_minute:
            # Attendre
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                logger.info(f"Rate limiting: sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)
        
        # Enregistrer appel
        self.calls.append(time.time())
```

---

## 💰 Module 3: Cost Tracking

### Suivi des Couts

```python
class CostTracker:
    """Suivi des couts API."""
    
    def __init__(self):
        self.daily_costs: dict[str, float] = {}
        self.monthly_costs: dict[str, float] = {}
    
    def track_call(self, provider: str, cost: float):
        """Enregistre un appel."""
        today = datetime.now().strftime('%Y-%m-%d')
        month = datetime.now().strftime('%Y-%m')
        
        key_day = f"{provider}:{today}"
        key_month = f"{provider}:{month}"
        
        self.daily_costs[key_day] = self.daily_costs.get(key_day, 0) + cost
        self.monthly_costs[key_month] = self.monthly_costs.get(key_month, 0) + cost
    
    def get_daily_cost(self, provider: str = None) -> float:
        """Cout journalier."""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if provider:
            return self.daily_costs.get(f"{provider}:{today}", 0)
        
        return sum(v for k, v in self.daily_costs.items() if today in k)
    
    def get_monthly_cost(self, provider: str = None) -> float:
        """Cout mensuel."""
        month = datetime.now().strftime('%Y-%m')
        
        if provider:
            return self.monthly_costs.get(f"{provider}:{month}", 0)
        
        return sum(v for k, v in self.monthly_costs.items() if month in k)
    
    def check_budget_alert(self, monthly_budget: float = 50.0) -> bool:
        """Verifie si alerte budget."""
        return self.get_monthly_cost() > monthly_budget
```

---

## 🔧 Responsabilites

### Quand consulter cet agent

- Ajout nouveau provider IA
- Configuration fallback
- Probleme de disponibilite IA
- Optimisation couts
- Rate limiting
- Circuit breaker tuning

---

**Version**: 1.0
**Date**: 2026-02-25
**Statut**: PRET A L'EMPLOI

---

## 🔧 Module Additionnel: Complements & Robustesse

### DeepSeek Provider

```python
class DeepSeekProvider(AIProvider):
    """Provider DeepSeek (budget-friendly)."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
        self.default_model = "deepseek-chat"
    
    def generate_text(self, prompt: str, model_name: str = None) -> str:
        import requests
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": model_name or self.default_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
        )
        
        return response.json()["choices"][0]["message"]["content"]
    
    def generate_json(self, prompt: str, model_name: str = None) -> dict:
        import json
        
        json_prompt = f"{prompt}\n\nReponds UNIQUEMENT en JSON valide."
        text = self.generate_text(json_prompt, model_name)
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise
    
    def is_available(self) -> bool:
        import requests
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def get_cost_estimate(self, prompt: str) -> float:
        # DeepSeek: ~$0.0005 / 1K tokens
        tokens = len(prompt.split()) * 1.3
        return (tokens / 1000) * 0.0005
```

### Retry avec Exponential Backoff

```python
"""
Retry robuste avec jitter pour eviter les thundering herds.
"""

import random
import time
from functools import wraps

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: tuple = (Exception,)
):
    """
    Decorateur de retry avec exponential backoff.
    
    Args:
        max_retries: Nombre max de tentatives
        base_delay: Delai initial
        max_delay: Delai maximum
        exponential_base: Base exponentielle
        jitter: Ajouter du jitter aleatoire
        exceptions: Exceptions à capturer
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries - 1:
                        # Calculer delai
                        delay = min(
                            base_delay * (exponential_base ** attempt),
                            max_delay
                        )
                        
                        if jitter:
                            # Ajouter jitter (±25%)
                            delay *= random.uniform(0.75, 1.25)
                        
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        
                        time.sleep(delay)
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries} attempts")
            
            raise last_exception
        return wrapper
    return decorator

# Usage
@retry_with_backoff(
    max_retries=3,
    base_delay=1.0,
    exceptions=(requests.RequestException, TimeoutError)
)
def call_ai_api(provider, prompt):
    return provider.generate_text(prompt)
```

### Health Check & Monitoring

```python
class ProviderHealthMonitor:
    """Monitoring de sante des providers."""
    
    def __init__(self):
        self.metrics: dict[str, ProviderMetrics] = {}
        self.last_health_check: dict[str, datetime] = {}
    
    def check_health(self, provider_name: str, provider: AIProvider) -> dict:
        """
        Verifie la sante d'un provider.
        
        Returns:
            {
                'healthy': bool,
                'latency_ms': float,
                'success_rate': float,
                'last_error': str
            }
        """
        start = time.time()
        
        try:
            # Test simple
            provider.generate_text("test", timeout=5)
            latency = (time.time() - start) * 1000
            
            return {
                'healthy': True,
                'latency_ms': latency,
                'success_rate': self._get_success_rate(provider_name),
                'last_error': None
            }
        except Exception as e:
            return {
                'healthy': False,
                'latency_ms': None,
                'success_rate': self._get_success_rate(provider_name),
                'last_error': str(e)
            }
    
    def record_call(self, provider_name: str, success: bool, latency_ms: float):
        """Enregistre un appel pour metriques."""
        if provider_name not in self.metrics:
            self.metrics[provider_name] = ProviderMetrics()
        
        self.metrics[provider_name].add_sample(success, latency_ms)
    
    def _get_success_rate(self, provider_name: str) -> float:
        """Calcule le taux de succes."""
        if provider_name not in self.metrics:
            return 1.0
        return self.metrics[provider_name].success_rate()
    
    def get_dashboard_metrics(self) -> dict:
        """Metriques pour dashboard."""
        return {
            name: {
                'success_rate': metrics.success_rate(),
                'avg_latency': metrics.avg_latency(),
                'total_calls': metrics.total_calls,
                'errors_last_hour': metrics.errors_last_hour()
            }
            for name, metrics in self.metrics.items()
        }

@dataclass
class ProviderMetrics:
    """Metriques pour un provider."""
    calls: list[tuple[datetime, bool, float]] = field(default_factory=list)
    
    def add_sample(self, success: bool, latency_ms: float):
        self.calls.append((datetime.now(), success, latency_ms))
        # Garder seulement 24h d'historique
        cutoff = datetime.now() - timedelta(hours=24)
        self.calls = [c for c in self.calls if c[0] > cutoff]
    
    def success_rate(self, hours: int = 1) -> float:
        """Taux de succes sur les dernieres heures."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [c for c in self.calls if c[0] > cutoff]
        
        if not recent:
            return 1.0
        
        successes = sum(1 for _, success, _ in recent if success)
        return successes / len(recent)
    
    def avg_latency(self, hours: int = 1) -> float:
        """Latence moyenne."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [c for _, _, lat in self.calls if c[0] > cutoff]
        
        return sum(recent) / len(recent) if recent else 0.0
```

### Template: Nouveau Provider

```python
"""
Template pour ajouter un nouveau provider IA.
"""

class NewProviderTemplate(AIProvider):
    """
    Template pour nouveau provider.
    
    Steps d'implementation:
    1. Creer la classe heritant de AIProvider
    2. Implementer __init__ avec config
    3. Implementer generate_text()
    4. Implementer generate_json()
    5. Implementer is_available()
    6. Implementer get_cost_estimate()
    7. Ajouter au ProviderFactory
    """
    
    def __init__(self, api_key: str, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url or "https://api.provider.com/v1"
        self.default_model = "model-name"
    
    def generate_text(self, prompt: str, model_name: str = None) -> str:
        """
        Implementer l'appel API.
        
        Returns:
            Texte genere
        """
        import requests
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": model_name or self.default_model,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    
    def generate_json(self, prompt: str, model_name: str = None) -> dict:
        """Generer JSON (utiliser generate_text + parsing)."""
        import json
        
        json_prompt = f"{prompt}\n\nReponds UNIQUEMENT en JSON."
        text = self.generate_text(json_prompt, model_name)
        
        return json.loads(text)
    
    def is_available(self) -> bool:
        """Verifier disponibilite."""
        try:
            self.generate_text("test", timeout=5)
            return True
        except Exception:
            return False
    
    def get_cost_estimate(self, prompt: str) -> float:
        """Estimer cout en USD."""
        # Implementer selon pricing du provider
        tokens = len(prompt.split()) * 1.3
        return (tokens / 1000) * 0.001  # $0.001 / 1K tokens

# Enregistrement
ProviderFactory.PROVIDERS['new_provider'] = NewProviderTemplate
```

---

**Version**: 1.1 - **COMPLETED**
**Ajouts**: DeepSeek provider, retry backoff, health monitoring, metrics, template
