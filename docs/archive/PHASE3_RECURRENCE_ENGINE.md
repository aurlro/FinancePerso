# Phase 3 - Moteur de Détection de Récurrence

## 🎯 Objectifs atteints

### 1. ✅ Moteur de Détection (`src/subscription_engine.py`)

**Classe `SubscriptionDetector` avec :**

- **Logique de Groupement** : Par `clean_merchant` (après nettoyage)
- **Analyse de Fréquence** : Calcul médian des intervalles en jours
- **Patterns supportés** :
  - Hebdomadaire (6-8 jours)
  - Bimensuel (13-16 jours)
  - Mensuel (28-32 jours)
  - Trimestriel (85-95 jours)
  - Semestriel (175-185 jours)
  - Annuel (360-370 jours)

- **Stabilité du Montant** : Écart-type < 20% (configurable)
- **Gestion des doubles prélèvements** : Tolérance de 3 jours
- **Exclusion des virements internes** : Catégories "Virement Interne", "Hors Budget"

### 2. ✅ Modèle de Données & Prédiction

**Structure JSON générée :**
```json
{
  "merchant": "Netflix",
  "frequency": "monthly",
  "average_amount": 13.49,
  "amount_std": 0.05,
  "last_date": "2026-02-15",
  "next_expected_date": "2026-03-15",
  "confidence_score": 0.95,
  "status": "ACTIF",
  "transaction_count": 6,
  "category": "Entertainment",
  "metadata": {
    "intervals": [30, 30, 31, 30, 29],
    "median_interval": 30,
    "amount_cv": 0.003
  }
}
```

### 3. ✅ Statuts d'Abonnement

- **ACTIF** : Fonctionnement normal
- **A_RISQUE** : Variation anormale détectée (>15%)
- **ZOMBIE** : Pas de transaction depuis >45j (mensuel)
- **INACTIF** : Résilié ou suspendu

### 4. ✅ Vue Streamlit (`views/subscriptions.py`)

**Interface avec :**
- **KPIs** : Total charges fixes vs Revenus, ratio
- **Tableau** : Barres de progression vers prochaine échéance
- **Alertes Zombie** : Liste des abonnements suspects
- **Alertes Augmentation** : Détection des hausses de prix
- **Calculateur** : "Vrai Reste à Vivre" avec projection

### 5. ✅ Calculateur `calculate_remaining_budget()`

```python
result = calculate_remaining_budget(
    current_balance=1500.0,
    subscriptions=subscriptions,
    days_ahead=30,
)
# {
#   "current_balance": 1500.0,
#   "upcoming_charges": 93.49,
#   "remaining_budget": 1406.51,
#   "status": "healthy"
# }
```

## 📊 Tests validés

```python
✅ Détection de Netflix (mensuel, 13.49€)
✅ Détection de EDF (mensuel, 80.00€)
✅ Exclusion des dépenses ponctuelles
✅ Charges mensuelles: 93.49€
✅ Reste à vivre: 1406.51€ (sur 1500€)
```

## 🔧 Contraintes respectées

- ✅ **Pandas** pour calculs vectoriels temporels
- ✅ **Pas d'IA lourde** : Approche probabiliste/mathématique
- ✅ **Doubles prélèvements** : Tolérance 3 jours
- ✅ **Virements internes exclus** : Par catégorie

## 📦 Livrables

```
FinancePerso/
├── src/
│   └── subscription_engine.py    # Moteur de détection
├── views/
│   ├── __init__.py
│   └── subscriptions.py          # Vue Streamlit
└── docs/
    └── PHASE3_RECURRENCE_ENGINE.md
```

## 🚀 Utilisation

### Détection simple
```python
from src.subscription_engine import detect_subscriptions_simple

subscriptions = detect_subscriptions_simple(df_transactions)
```

### Avec paramètres avancés
```python
from src.subscription_engine import SubscriptionDetector

detector = SubscriptionDetector(
    amount_tolerance=0.15,  # 15% variance
    date_tolerance=3,       # 3 jours
    min_occurrences=3,      # 3 transactions min
)

subscriptions = detector.detect_subscriptions(df)
zombies = detector.detect_zombie_subscriptions(subscriptions)
increases = detector.detect_amount_increases(df)
```

### Calculateur Reste à Vivre
```python
from src.subscription_engine import calculate_remaining_budget

result = calculate_remaining_budget(
    current_balance=1500.0,
    subscriptions=subscriptions,
    days_ahead=30,
)
print(f"Reste à vivre: {result['remaining_budget']:.2f}€")
```

## 🎓 Algorithme détaillé

### 1. Préparation des données
```python
data = df[df["amount"] < 0]  # Uniquement dépenses
data["clean_merchant"] = data["label"].apply(clean_transaction_label)
```

### 2. Pour chaque commerçant
- Grouper les transactions
- Calculer intervalles entre dates
- Médiane des intervalles
- Détecter fréquence par fenêtre

### 3. Validation
- Écart-type montant < 20%
- Minimum 3 occurrences
- Score de confiance > 0.5

### 4. Statut
- ZOMBIE si days_since_last > threshold
- A_RISQUE si CV montant > 15%
- ACTIF sinon

### 5. Prédiction
```python
next_date = last_date + timedelta(days=frequency_days)
```
