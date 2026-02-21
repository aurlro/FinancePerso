# Audit Data Engineering - Phase 2

## 🔍 État actuel de l'application

### ✅ Ce qui existe déjà

#### 1. Nettoyage des libellés (`modules/utils.py`)
```python
def clean_label(label):
    """Remove common bank noise to help AI focus on merchant name."""
    # Supprime les dates (dd/mm/yy)
    # Supprime CB/CARTE/PRLV/SEPA/VIR + numéros
    # Supprime les nombres longs
    # Normalize les espaces
    # Title Case
```

**Utilisé dans :** 20+ fichiers à travers l'application

#### 2. Taxonomie PFCv2 (`modules/categorization_cascade.py`)
```python
class TransactionCategorizer:
    PFCV2_CATEGORIES = {
        "Food & Drink": ["Groceries", "Restaurants", "Fast Food", ...],
        "Transportation": ["Fuel", "Public Transit", "Taxi & Rideshare", ...],
        "Shopping": ["Clothing", "Electronics", ...],
        "Financial": ["Bank Fees", "Insurance", ...],
        "Housing": ["Rent", "Utilities", "Internet", ...],
        "Health": ["Medical", "Pharmacy", ...],
        "Entertainment": ["Streaming", "Movies", ...],
        "Education": ["Tuition", "Books", ...],
        "Income": ["Salary", "Freelance", ...],
        "Transfers": ["Internal Transfer", "External Transfer", ...],
    }
```

#### 3. Système de catégorisation en cascade (`modules/categorization_cascade.py`)
```python
@dataclass
class CategorizationResult:
    category: str                    # "Food & Drink > Groceries"
    clean_merchant: str             # "CARREFOUR"
    confidence_score: float         # 0.0 - 1.0
    source: str                     # "heuristic", "similarity", "local_ai", "cloud_ai"
    is_recurring_candidate: bool
    risk_flag: int
    similar_transaction_id: Optional[int]
    similarity_score: Optional[float]

class TransactionCategorizer:
    def categorize(self, label: str, amount: float, date: str) -> CategorizationResult:
        # 1. Heuristique (patterns regex)
        # 2. Similarité (SequenceMatcher > 0.85)
        # 3. IA locale (Llama 3.2)
        # 4. IA cloud (fallback)
```

### ❌ Ce qui manque

#### 1. Champ `meta_data` JSON dans les transactions
**Actuellement :** La table `transactions` n'a pas de champ pour stocker les métadonnées de catégorisation.

**Besoin :** Ajouter `meta_data TEXT` pour stocker :
```json
{
  "categorization": {
    "confidence_score": 0.95,
    "method": "HEURISTIC|SIMILARITY|LOCAL_AI|CLOUD_AI",
    "timestamp": "2024-01-15T10:30:00",
    "version": "2.0"
  },
  "clean_merchant": "MONOPRIX",
  "similarity_match": {
    "transaction_id": 1234,
    "score": 0.92
  }
}
```

#### 2. Module `src/data_cleaning.py` dédié
**Actuellement :** `clean_label` est dans `modules/utils.py`

**Besoin :** Un module dédié avec :
- Fonctions plus aggressives (MONOPRIX PARIS 14 → MONOPRIX)
- Extraction de commerçants
- Normalisation avancée

#### 3. Module `modules/transactions/constants.py`
**Actuellement :** PFCv2 est dans `categorization_cascade.py`

**Besoin :** Un module dédié pour les constantes transactions

#### 4. Module `modules/transactions/services.py`
**Actuellement :** La logique est dans `categorization_cascade.py`

**Besoin :** Un service dédié avec interface claire

## 🎯 Plan d'action recommandé

### Option A : Améliorer l'existant (Recommandé)
1. ✅ Réutiliser `clean_label` existante
2. ✅ Réutiliser `TransactionCategorizer` existant
3. ✅ Réutiliser `PFCV2_CATEGORIES` existant
4. ➕ Ajouter champ `meta_data` dans migrations
5. ➕ Mettre à jour `TransactionCategorizer` pour persister les métadonnées

### Option B : Créer nouvelle structure
Créer les nouveaux modules comme demandé mais en déléguant à l'existant.

## 📊 Comparaison

| Fonctionnalité | Existant | Requis | Action |
|----------------|----------|--------|--------|
| Nettoyage libellés | ✅ `clean_label` | ✅ | Réutiliser + améliorer |
| Taxonomie PFCv2 | ✅ `PFCV2_CATEGORIES` | ✅ | Réutiliser |
| Cascade catégorisation | ✅ `TransactionCategorizer` | ✅ | Réutiliser + étendre |
| Champ meta_data | ❌ | ✅ | Créer migration |
| Stockage JSON | ❌ | ✅ | Ajouter |

## 🔧 Décision

**Approche hybride :**
1. Créer `src/data_cleaning.py` qui expose une API propre mais utilise `clean_label` interne
2. Créer `modules/transactions/constants.py` qui exporte `PFCV2_CATEGORIES`
3. Créer `modules/transactions/services.py` qui wrap `TransactionCategorizer`
4. Ajouter migration pour `meta_data`
5. Mettre à jour `TransactionCategorizer` pour persister dans `meta_data`
