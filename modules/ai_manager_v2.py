"""
AI Manager v2 - Modernized for google.genai API
===============================================

This module provides a unified interface for multiple AI providers.
Now uses the modern google.genai API (v2) instead of deprecated google.generativeai.

Migration from v1:
    OLD: import google.generativeai as genai
         model = genai.GenerativeModel('gemini-pro')
         response = model.generate_content(prompt)
    
    NEW: from google import genai
         client = genai.Client(api_key=key)
         response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)

Required packages:
    pip install google-genai>=0.3.0

Environment Variables:
    AI_PROVIDER: Provider type (gemini, ollama, openai, deepseek, kimi)
    GEMINI_API_KEY: Google Gemini API key
    OLLAMA_URL: Ollama server URL (default: http://localhost:11434)
    OPENAI_API_KEY: OpenAI API key
    DEEPSEEK_API_KEY: DeepSeek API key
    KIMI_API_KEY: Moonshot/KIMI API key
    AI_MODEL_NAME: Model name override (default varies by provider)
"""

import json
import os
import time
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any

import requests
from dotenv import load_dotenv

from modules.logger import logger

load_dotenv()

# Import new Google GenAI API
try:
    from google import genai
    from google.genai import types

    GENAI_AVAILABLE = True
except ImportError:
    logger.error(
        "google-genai package not found. Install with: pip install google-genai>=0.3.0"
    )
    genai = None
    types = None
    GENAI_AVAILABLE = False


# Import LocalSLMProvider (optional)
try:
    from modules.ai.local_slm_provider import LocalSLMProvider
    LOCAL_SLM_AVAILABLE = True
except ImportError:
    LocalSLMProvider = None
    LOCAL_SLM_AVAILABLE = False

# --- Rate Limiting ---
_last_call_time = 0
_min_interval = 0.5  # Minimum 500ms between API calls


def rate_limited(func):
    """Decorator to ensure minimum interval between API calls."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        global _last_call_time
        elapsed = time.time() - _last_call_time
        if elapsed < _min_interval:
            time.sleep(_min_interval - elapsed)
        _last_call_time = time.time()
        return func(*args, **kwargs)

    return wrapper


# --- Abstract Base Class ---
class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def generate_json(self, prompt: str, model_name: str | None = None) -> dict[str, Any]:
        """Generate structured JSON response from prompt."""
        pass

    @abstractmethod
    def generate_text(self, prompt: str, model_name: str | None = None) -> str:
        """Generate text response from prompt."""
        pass

    @abstractmethod
    def list_models(self) -> list[str]:
        """List available models for this provider."""
        pass


# --- 1. Google Gemini (v2 API) ---
class GeminiProvider(AIProvider):
    """
    Google Gemini provider using modern google.genai API.
    
    Documentation: https://ai.google.dev/gemini-api/docs
    """

    DEFAULT_MODEL = "gemini-2.0-flash"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        if api_key and GENAI_AVAILABLE:
            self.client = genai.Client(api_key=api_key)

    @rate_limited
    def generate_json(
        self, prompt: str, model_name: str | None = None
    ) -> dict[str, Any]:
        """
        Generate JSON response from prompt.
        
        Args:
            prompt: The prompt to send to the model
            model_name: Model to use (default: gemini-2.0-flash)
            
        Returns:
            Parsed JSON response as dictionary
        """
        if not self.api_key:
            logger.warning("Gemini API key not configured")
            return {"error": "API key not configured", "status": "unconfigured"}
        if not GENAI_AVAILABLE:
            logger.error("google-genai package not installed")
            return {"error": "AI library not installed", "status": "error"}
        if not self.client:
            logger.error("Gemini client not initialized")
            return {"error": "Client initialization failed", "status": "error"}

        model = model_name or self.DEFAULT_MODEL

        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            text = response.text

            # Clean up markdown code blocks if present
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)

        except json.JSONDecodeError as e:
            logger.error(f"Gemini JSON parsing error: {e}")
            return {"error": "Invalid JSON response from AI", "status": "parse_error"}
        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "rate limit" in error_msg:
                logger.error(f"Gemini quota exceeded: {e}")
                return {
                    "error": "API quota exceeded. Please try again later.",
                    "status": "quota_exceeded",
                }
            elif "api key" in error_msg or "authentication" in error_msg:
                logger.error(f"Gemini authentication error: {e}")
                return {
                    "error": "Invalid API key. Please check your configuration.",
                    "status": "auth_error",
                }
            else:
                logger.error(f"Gemini JSON Error: {e}")
                return {"error": f"AI service error: {str(e)[:100]}", "status": "error"}

    @rate_limited
    def generate_text(self, prompt: str, model_name: str | None = None) -> str:
        """
        Generate text response from prompt.
        
        Args:
            prompt: The prompt to send to the model
            model_name: Model to use (default: gemini-2.0-flash)
            
        Returns:
            Generated text response
        """
        if not self.api_key:
            return "⚠️ Clé API Gemini non configurée. Configurez-la dans les paramètres."
        if not GENAI_AVAILABLE:
            return "⚠️ Bibliothèque google-genai non installée. Exécutez: pip install google-genai"
        if not self.client:
            return "⚠️ Erreur d'initialisation du client Gemini."

        model = model_name or self.DEFAULT_MODEL

        try:
            response = self.client.models.generate_content(
                model=model, contents=prompt
            )
            return response.text

        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "rate limit" in error_msg:
                logger.error(f"Gemini quota exceeded: {e}")
                return "⚠️ Quota API dépassé. Réessayez plus tard."
            elif "api key" in error_msg or "authentication" in error_msg:
                logger.error(f"Gemini authentication error: {e}")
                return "⚠️ Clé API invalide. Vérifiez votre configuration."
            else:
                logger.error(f"Gemini Text Error: {e}")
                return f"⚠️ Erreur du service IA: {str(e)[:100]}"

    def list_models(self) -> list[str]:
        """List recommended Gemini models."""
        return [
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
        ]


# --- 2. Ollama (Local) ---
class OllamaProvider(AIProvider):
    """
    Ollama local AI provider.
    Requires Ollama server running locally or remotely.
    
    Documentation: https://ollama.com/
    """

    DEFAULT_MODEL = "llama3.2"

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")

    def generate_json(self, prompt: str, model_name: str | None = None) -> dict[str, Any]:
        """Generate JSON response using Ollama."""
        model = model_name or self.DEFAULT_MODEL
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            }
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            return json.loads(data["response"])
        except requests.ConnectionError:
            logger.error(f"Ollama connection error - is Ollama running at {self.base_url}?")
            return {
                "error": "Cannot connect to Ollama. Is the server running?",
                "status": "connection_error",
            }
        except requests.Timeout:
            logger.error("Ollama request timeout")
            return {"error": "Request to Ollama timed out. Try again later.", "status": "timeout"}
        except json.JSONDecodeError as e:
            logger.error(f"Ollama JSON parsing error: {e}")
            return {"error": "Invalid JSON response from Ollama", "status": "parse_error"}
        except Exception as e:
            logger.error(f"Ollama JSON Error: {e}")
            return {"error": f"Ollama error: {str(e)[:100]}", "status": "error"}

    def generate_text(self, prompt: str, model_name: str | None = None) -> str:
        """Generate text response using Ollama."""
        model = model_name or self.DEFAULT_MODEL
        try:
            payload = {"model": model, "prompt": prompt, "stream": False}
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json()["response"]
        except requests.ConnectionError:
            logger.error(f"Ollama connection error - is Ollama running at {self.base_url}?")
            return f"⚠️ Impossible de se connecter à Ollama à {self.base_url}. Le serveur est-il démarré ?"
        except requests.Timeout:
            logger.error("Ollama request timeout")
            return "⚠️ Délai d'attente dépassé. Réessayez plus tard."
        except Exception as e:
            logger.error(f"Ollama Text Error: {e}")
            return f"⚠️ Erreur Ollama: {str(e)[:100]}"

    def list_models(self) -> list[str]:
        """List available Ollama models."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return [m["name"] for m in data.get("models", [])]
        except (requests.RequestException, KeyError, ValueError) as e:
            logger.warning(f"Failed to fetch Ollama models: {e}")
        return ["llama3.2", "mistral", "gemma2", "qwen2.5"]


# --- 3. OpenAI Compatible ---
class OpenAICompatibleProvider(AIProvider):
    """
    Generic OpenAI-compatible provider.
    Works with OpenAI, DeepSeek, and other compatible APIs.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def generate_json(
        self, prompt: str, model_name: str | None = None
    ) -> dict[str, Any]:
        """Generate JSON response using OpenAI-compatible API."""
        if not self.api_key:
            return {"error": "API key not configured", "status": "unconfigured"}

        model = model_name or "gpt-3.5-turbo"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
        }
        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            return json.loads(content)
        except requests.HTTPError as e:
            status_code = e.response.status_code if hasattr(e, "response") else "unknown"
            logger.error(f"OpenAI HTTP Error {status_code}: {e}")
            if status_code == 401:
                return {"error": "Invalid API key", "status": "auth_error"}
            elif status_code == 429:
                return {
                    "error": "Rate limit exceeded. Please try again later.",
                    "status": "rate_limit",
                }
            elif status_code >= 500:
                return {"error": "AI service temporarily unavailable", "status": "service_error"}
            else:
                return {"error": f"API Error: {str(e)[:100]}", "status": "error"}
        except json.JSONDecodeError as e:
            logger.error(f"OpenAI JSON parsing error: {e}")
            return {"error": "Invalid JSON response", "status": "parse_error"}
        except Exception as e:
            logger.error(f"OpenAI JSON Error: {e}")
            return {"error": f"Service error: {str(e)[:100]}", "status": "error"}

    def generate_text(self, prompt: str, model_name: str | None = None) -> str:
        """Generate text response using OpenAI-compatible API."""
        if not self.api_key:
            return "⚠️ Clé API non configurée"

        model = model_name or "gpt-3.5-turbo"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except requests.HTTPError as e:
            status_code = e.response.status_code if hasattr(e, "response") else "unknown"
            logger.error(f"OpenAI HTTP Error {status_code}: {e}")
            if status_code == 401:
                return "⚠️ Clé API invalide"
            elif status_code == 429:
                return "⚠️ Limite de requêtes dépassée. Réessayez plus tard."
            elif status_code >= 500:
                return "⚠️ Service IA temporairement indisponible"
            else:
                return f"⚠️ Erreur API: {str(e)[:100]}"
        except Exception as e:
            logger.error(f"OpenAI Text Error: {e}")
            return f"⚠️ Erreur: {str(e)[:100]}"

    def list_models(self) -> list[str]:
        """List available models."""
        if "deepseek" in self.base_url:
            return ["deepseek-chat", "deepseek-coder"]
        return ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]


# --- 4. KIMI (Moonshot AI) ---
class KimiProvider(AIProvider):
    """
    KIMI AI Provider (Moonshot AI)
    Documentation: https://platform.moonshot.cn/
    """

    DEFAULT_MODEL = "moonshot-v1-8k"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.moonshot.cn/v1"

    def generate_json(
        self, prompt: str, model_name: str | None = None
    ) -> dict[str, Any]:
        """Generate JSON response using KIMI."""
        if not self.api_key:
            return {"error": "API key not configured", "status": "unconfigured"}

        model = model_name or self.DEFAULT_MODEL
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
        }
        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except requests.HTTPError as e:
            status_code = e.response.status_code if hasattr(e, "response") else "unknown"
            logger.error(f"KIMI HTTP Error {status_code}: {e}")
            if status_code == 401:
                return {"error": "Invalid API key", "status": "auth_error"}
            elif status_code == 429:
                return {"error": "Rate limit exceeded", "status": "rate_limit"}
            else:
                return {"error": f"API Error: {str(e)[:100]}", "status": "error"}
        except json.JSONDecodeError as e:
            logger.error(f"KIMI JSON parsing error: {e}")
            return {"error": "Invalid JSON response", "status": "parse_error"}
        except Exception as e:
            logger.error(f"KIMI JSON Error: {e}")
            return {"error": f"Service error: {str(e)[:100]}", "status": "error"}

    def generate_text(self, prompt: str, model_name: str | None = None) -> str:
        """Generate text response using KIMI."""
        if not self.api_key:
            return "⚠️ Clé API KIMI non configurée"

        model = model_name or self.DEFAULT_MODEL
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except requests.HTTPError as e:
            status_code = e.response.status_code if hasattr(e, "response") else "unknown"
            logger.error(f"KIMI HTTP Error {status_code}: {e}")
            if status_code == 401:
                return "⚠️ Clé API invalide"
            elif status_code == 429:
                return "⚠️ Limite de requêtes dépassée"
            else:
                return f"⚠️ Erreur API: {str(e)[:100]}"
        except Exception as e:
            logger.error(f"KIMI Text Error: {e}")
            return f"⚠️ Erreur: {str(e)[:100]}"

    def list_models(self) -> list[str]:
        """List available KIMI models."""
        return [
            "moonshot-v1-8k",
            "moonshot-v1-32k",
            "moonshot-v1-128k",
        ]


# --- Factory ---
def get_ai_provider() -> AIProvider:
    """
    Factory function to get the configured AI provider.
    
    Reads AI_PROVIDER environment variable to determine which provider to use.
    
    Returns:
        AIProvider: Configured AI provider instance
        
    Raises:
        ConfigurationError: If required API key is not set
    """
    from modules.exceptions import ConfigurationError

    provider_type = os.getenv("AI_PROVIDER", "gemini").lower()

    if provider_type == "ollama":
        url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        return OllamaProvider(url)

    elif provider_type == "openai":
        key = os.getenv("OPENAI_API_KEY", "")
        if not key:
            raise ConfigurationError("OPENAI_API_KEY environment variable is not set")
        return OpenAICompatibleProvider(key, "https://api.openai.com/v1")

    elif provider_type == "deepseek":
        key = os.getenv("DEEPSEEK_API_KEY", "")
        if not key:
            raise ConfigurationError("DEEPSEEK_API_KEY environment variable is not set")
        return OpenAICompatibleProvider(key, "https://api.deepseek.com/v1")

    elif provider_type == "kimi":
        key = os.getenv("KIMI_API_KEY", "")
        if not key:
            raise ConfigurationError("KIMI_API_KEY environment variable is not set")
        return KimiProvider(key)

    elif provider_type in ("local", "slm"):
        # Local Small Language Model (Llama 3.2, etc.)
        from modules.ai.local_slm_provider import get_local_slm_provider
        model = os.getenv("LOCAL_SLM_MODEL", "llama-3.2-3b")
        fallback = os.getenv("LOCAL_SLM_FALLBACK", "true").lower() == "true"
        return get_local_slm_provider(model_name=model, fallback_to_cloud=fallback)

    else:  # Default Gemini
        key = os.getenv("GEMINI_API_KEY", "")
        if not key:
            raise ConfigurationError("GEMINI_API_KEY environment variable is not set")
        return GeminiProvider(key)


def get_active_model_name() -> str:
    """Get the currently configured AI model name."""
    provider = os.getenv("AI_PROVIDER", "gemini").lower()
    defaults = {
        "gemini": "gemini-2.0-flash",
        "ollama": "llama3.2",
        "openai": "gpt-3.5-turbo",
        "deepseek": "deepseek-chat",
        "kimi": "moonshot-v1-8k",
        "local": "llama-3.2-3b",
        "slm": "llama-3.2-3b",
    }
    return os.getenv("AI_MODEL_NAME", defaults.get(provider, "gemini-2.0-flash"))


def is_ai_available() -> bool:
    """Check if AI provider is properly configured and available."""
    try:
        provider = get_ai_provider()

        if isinstance(provider, GeminiProvider):
            return bool(provider.api_key and GENAI_AVAILABLE and provider.client)
        elif isinstance(provider, OllamaProvider):
            try:
                requests.get(f"{provider.base_url}/api/tags", timeout=2)
                return True
            except Exception:
                return False
        elif isinstance(provider, (OpenAICompatibleProvider, KimiProvider)):
            return bool(provider.api_key)
        elif isinstance(provider, LocalSLMProvider):
            return provider._model_loaded or (provider.fallback_to_cloud and bool(provider._get_fallback_provider()))

        return False
    except Exception as e:
        logger.warning(f"Error checking AI availability: {e}")
        return False


def get_ai_error_message() -> str:
    """Get a user-friendly error message explaining why AI is not available."""
    try:
        provider_type = os.getenv("AI_PROVIDER", "gemini").lower()

        if provider_type == "gemini":
            if not os.getenv("GEMINI_API_KEY"):
                return "🔑 Clé API Gemini non configurée. Ajoutez GEMINI_API_KEY dans votre fichier .env"
            if not GENAI_AVAILABLE:
                return "📦 Bibliothèque google-genai non installée. Exécutez: pip install google-genai"
        elif provider_type == "ollama":
            url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            return f"🔌 Ollama non disponible à l'adresse {url}. Vérifiez que le serveur est démarré."
        elif provider_type == "openai":
            return "🔑 Clé API OpenAI non configurée. Ajoutez OPENAI_API_KEY dans votre fichier .env"
        elif provider_type == "deepseek":
            return "🔑 Clé API DeepSeek non configurée. Ajoutez DEEPSEEK_API_KEY dans votre fichier .env"
        elif provider_type == "kimi":
            return "🔑 Clé API KIMI non configurée. Ajoutez KIMI_API_KEY dans votre fichier .env"
        elif provider_type in ("local", "slm"):
            return "🖥️ Modèle local non disponible. Vérifiez qu'Unsloth est installé (pip install unsloth) et que vous avez un GPU compatible."

        return "🤖 Service IA non disponible"
    except Exception as e:
        return f"🤖 Service IA non disponible: {str(e)[:100]}"


# Backward compatibility aliases
get_provider = get_ai_provider
