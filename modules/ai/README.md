# Intelligence Artificielle

Providers IA, gestion des modèles, assistants

## Fichiers principaux

- `ai_manager_v2.py` - Gestionnaire IA unifié (Gemini, OpenAI, DeepSeek, Ollama, ML local)
- `conversational_assistant.py` - Assistant conversationnel

## Exemple

```python
from modules.ai.ai_manager_v2 import AI_MANAGER

# Utilisation du gestionnaire IA pour catégoriser une transaction
result = AI_MANAGER.categorize_transaction(
    transaction_description="Achat supermarché Carrefour",
    provider="gemini"
)
```
