# ADR 002: Architecture IA - Cloud + Local

## Statut

✅ Accepté (2024-02-20)

## Contexte

La catégorisation automatique des transactions nécessite de l'IA. Deux contraintes:
1. **Précision** - Bonne catégorisation des transactions
2. **Confidentialité** - Données bancaires sensibles

## Options considérées

### 1. IA Cloud uniquement
**Avantages:**
- Modèles puissants (GPT-4, Gemini)
- Toujours à jour

**Inconvénients:**
- Données envoyées sur internet
- Coût API
- Dépendance connexion

### 2. IA Local uniquement
**Avantages:**
- 100% offline
- Données locales
- Gratuit

**Inconvénients:**
- Modèles moins performants
- Nécessite GPU pour bonnes perfs
- Complexité setup

### 3. Hybrid Cloud + Local (choisi)
**Avantages:**
- Fallback si offline
- Choix privacy/performance
- Progressive enhancement

**Inconvénients:**
- Complexité architecture
- Deux modèles à maintenir

## Décision

Architecture **hybride**:

1. **Cloud** (défaut): Gemini, GPT-4, DeepSeek
2. **Local ML**: scikit-learn sur catégories connues
3. **Règles**: Pattern matching exact (prioritaire)

Ordre de priorité:
```
Règles exactes > Règles partielles > ML Local > IA Cloud > Défaut
```

## Implémentation

```python
class AIManager:
    def categorize(self, transaction):
        # 1. Règles exactes
        if rule_match := find_exact_rule(transaction):
            return rule_match
        
        # 2. Règles partielles
        if pattern_match := find_pattern_rule(transaction):
            return pattern_match
        
        # 3. ML Local (si entraîné)
        if local_ml.is_trained():
            return local_ml.predict(transaction)
        
        # 4. IA Cloud
        return cloud_ai.categorize(transaction)
```

## Conséquences

- ✅ Fonctionne offline
- ✅ Privacy configurable
- ✅ Performance dégradable élégamment
- ⚠️ Deux systèmes à maintenir
- ⚠️ Cohérence cloud vs local

## Fournisseurs supportés

| Provider | Type | Status |
|----------|------|--------|
| Gemini | Cloud | ✅ Recommandé |
| DeepSeek | Cloud | ✅ |
| OpenAI | Cloud | ✅ |
| Ollama | Local (LLM) | ✅ |
| scikit-learn | Local (ML) | ✅ |
