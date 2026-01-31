import os
import json
import requests
import time
from abc import ABC, abstractmethod
from functools import wraps
from modules.logger import logger
from dotenv import load_dotenv

load_dotenv()

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

# Try new API first, fallback to old if not available
try:
    from google import genai
    from google.genai import types
    USE_NEW_GENAI = True
    logger.info("Using new google.genai API")
except ImportError:
    try:
        import google.generativeai as genai
        USE_NEW_GENAI = False
        logger.warning("Using deprecated google.generativeai API - please upgrade: pip install google-genai")
    except ImportError:
        logger.error("No Google AI library found. Install with: pip install google-genai")
        genai = None
        USE_NEW_GENAI = False


# --- Abstract Base Class ---
class AIProvider(ABC):
    @abstractmethod
    def generate_json(self, prompt, model_name=None):
        """Returns a python dict/list from JSON response"""
        pass

    @abstractmethod
    def generate_text(self, prompt, model_name=None):
        """Returns raw text response"""
        pass
    
    @abstractmethod
    def list_models(self):
        """Returns list of available models"""
        pass

# --- 1. Google Gemini ---
class GeminiProvider(AIProvider):
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = None
        if api_key and genai:
            if USE_NEW_GENAI:
                # New API: use Client
                self.client = genai.Client(api_key=api_key)
            else:
                # Old API: configure globally
                genai.configure(api_key=api_key)

    @rate_limited
    def generate_json(self, prompt, model_name="gemini-2.0-flash"):
        if not self.api_key or not genai:
            return {}
        try:
            if USE_NEW_GENAI and self.client:
                # New API
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                text = response.text
            else:
                # Old API fallback
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                text = response.text
            
            # Clean up markdown code blocks if present
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            logger.error(f"Gemini JSON Error: {e}")
            return {}

    @rate_limited
    def generate_text(self, prompt, model_name="gemini-2.0-flash"):
        if not self.api_key or not genai:
            return "API Key missing or library not installed"
        try:
            if USE_NEW_GENAI and self.client:
                # New API
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                return response.text
            else:
                # Old API fallback
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text
        except Exception as e:
            logger.error(f"Gemini Text Error: {e}")
            return f"Error: {e}"

    def list_models(self):
        # Hardcoded favorite + simple discovery
        return ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]

# --- 2. Ollama (Local) ---
class OllamaProvider(AIProvider):
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url

    def generate_json(self, prompt, model_name="llama3"):
        try:
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json"  # Enforce JSON mode
            }
            resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return json.loads(data['response'])
        except Exception as e:
            logger.error(f"Ollama JSON Error: {e}")
            return {}

    def generate_text(self, prompt, model_name="llama3"):
        try:
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False
            }
            resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=30)
            resp.raise_for_status()
            return resp.json()['response']
        except Exception as e:
            logger.error(f"Ollama Text Error: {e}")
            return f"Error: {e}"

    def list_models(self):
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return [m['name'] for m in data['models']]
        except (requests.RequestException, KeyError, ValueError) as e:
            logger.warning(f"Failed to fetch Ollama models: {e}")
        return ["llama3", "mistral", "gemma"]   

# --- 3. OpenAI Compatible (ChatGPT, DeepSeek, etc) ---
class OpenAICompatibleProvider(AIProvider):
    def __init__(self, api_key, base_url="https://api.openai.com/v1"):
        self.api_key = api_key
        self.base_url = base_url

    def generate_json(self, prompt, model_name="gpt-3.5-turbo"):
        # Very simplified impl
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        try:
            resp = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            content = resp.json()['choices'][0]['message']['content']
            return json.loads(content)
        except Exception as e:
             logger.error(f"OpenAI JSON Error: {e}")
             return {}

    def generate_text(self, prompt, model_name="gpt-3.5-turbo"):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            resp = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            return resp.json()['choices'][0]['message']['content']
        except Exception as e:
             logger.error(f"OpenAI Text Error: {e}")
             return f"Error: {e}"

    def list_models(self):
        return ["gpt-3.5-turbo", "gpt-4-turbo", "deepseek-chat"]  # Placeholder

# --- 4. KIMI (Moonshot AI) ---
class KimiProvider(AIProvider):
    """
    KIMI AI Provider (Moonshot AI)
    Documentation: https://platform.moonshot.cn/
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.moonshot.cn/v1"

    def generate_json(self, prompt, model_name="moonshot-v1-8k"):
        if not self.api_key:
            return {}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            resp.raise_for_status()
            content = resp.json()['choices'][0]['message']['content']
            # Clean up markdown if present
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            logger.error(f"KIMI JSON Error: {e}")
            return {}

    def generate_text(self, prompt, model_name="moonshot-v1-8k"):
        if not self.api_key:
            return "API Key missing"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            resp.raise_for_status()
            return resp.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"KIMI Text Error: {e}")
            return f"Error: {e}"

    def list_models(self):
        return [
            "moonshot-v1-8k",      # 8k context
            "moonshot-v1-32k",     # 32k context
            "moonshot-v1-128k"     # 128k context
        ]

# --- Factory ---
def get_ai_provider():
    """
    Reads env vars to decide which provider to instantiate.
    Env Vars:
    AI_PROVIDER: "gemini", "ollama", "openai", "deepseek"
    GEMINI_API_KEY
    OLLAMA_URL
    OPENAI_API_KEY
    DEEPSEEK_API_KEY
    """
    provider_type = os.getenv("AI_PROVIDER", "gemini").lower()
    
    if provider_type == "ollama":
        url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        return OllamaProvider(url)
    
    elif provider_type == "openai":
        key = os.getenv("OPENAI_API_KEY", "")
        return OpenAICompatibleProvider(key, "https://api.openai.com/v1")
        
    elif provider_type == "deepseek":
        key = os.getenv("DEEPSEEK_API_KEY", "")
        # DeepSeek often uses OpenAI compatible API
        return OpenAICompatibleProvider(key, "https://api.deepseek.com/v1")
        
    else:
        # Default Gemini
        key = os.getenv("GEMINI_API_KEY", "")
        return GeminiProvider(key)

def get_active_model_name():
    return os.getenv("AI_MODEL_NAME", "gemini-2.0-flash")

def is_ai_available():
    """Check if AI provider is properly configured and available."""
    provider = get_ai_provider()
    
    if isinstance(provider, GeminiProvider):
        return bool(provider.api_key and genai)
    elif isinstance(provider, OllamaProvider):
        try:
            requests.get(f"{provider.base_url}/api/tags", timeout=2)
            return True
        except:
            return False
    elif isinstance(provider, OpenAICompatibleProvider):
        return bool(provider.api_key)
    
    return False
