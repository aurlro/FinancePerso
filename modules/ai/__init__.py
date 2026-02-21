"""
AI Module - Suite d'intelligence artificielle
=============================================

Modules pour l'analyse, la catégorisation et les suggestions IA.

Local SLM (optional):
    pip install unsloth torch transformers
    
Usage:
    from modules.ai import categorize_transaction
    result = categorize_transaction("Carrefour Paris", amount=-45.67)
"""

# Local SLM (optional import)
try:
    from modules.ai.local_slm_provider import LocalSLMProvider, get_local_slm_provider
    LOCAL_SLM_AVAILABLE = True
except ImportError:
    LocalSLMProvider = None
    get_local_slm_provider = None
    LOCAL_SLM_AVAILABLE = False

__all__ = [
    "LocalSLMProvider",
    "get_local_slm_provider",
    "LOCAL_SLM_AVAILABLE",
]
