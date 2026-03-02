# Module `modules/ai`

> Intelligence Artificielle pour FinancePerso.

## Vue d'ensemble

Ce module contient les fonctionnalités IA : détection d'anomalies, prédictions, suggestions de tags et classification.

## Architecture

```
modules/ai/
├── __init__.py              # Exports
├── anomaly_detector.py      # Détection d'anomalies
├── predictor.py             # Prédictions
├── tag_suggester.py         # Suggestions de tags
├── classifier.py            # Classification transactions
└── feedback_handler.py      # Gestion feedback IA
```

## Utilisation

### Détection d'anomalies

```python
from modules.ai.anomaly_detector import detect_anomalies

anomalies = detect_anomalies(transactions_df)
```

### Suggestions de tags

```python
from modules.ai.tag_suggester import suggest_tags

tags = suggest_tags(transaction_label, category)
```

## Intégration

Ce module est utilisé par `modules/ai_manager.py` qui fournit l'interface unifiée.

## Dépendances

- `ai_manager.py` - Interface unifiée IA
- `local_ml.py` - ML local (scikit-learn)
