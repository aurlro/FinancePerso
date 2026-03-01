# Intelligence Artificielle

Providers IA, gestion des modèles, assistants

## Fichiers principaux

- `ai_manager.py` - Gestionnaire IA unifié (Gemini, OpenAI, DeepSeek, Ollama, ML local)
- `conversational_assistant.py` - Assistant conversationnel

## Exemple

```python
from modules.ai_manager import AI_MANAGER

# Utilisation du gestionnaire IA pour catégoriser une transaction
result = AI_MANAGER.categorize_transaction(
    transaction_description="Achat supermarché Carrefour",
    provider="gemini"
)
```
