# Phase 2 - Data Engineering & Taxonomie PFCv2

## 🎯 Objectifs atteints

### 1. ✅ Module de nettoyage (`src/data_cleaning.py`)

**Fonctionnalités:**
- `clean_merchant_name()`: Supprime codes terminaux, dates, localisations
- `extract_location()`: Extrait les villes (PARIS 14, LYON 7, etc.)
- `extract_card_suffix()`: Extrait les 4 derniers chiffres de carte
- `normalize_merchant_name()`: Normalise les noms (supprime SAS/SARL, etc.)
- `clean_transaction_label()`: Nettoyage complet avec métadonnées

**Exemples:**
```python
from src.data_cleaning import clean_merchant_name, extract_location

clean_merchant_name("MONOPRIX PARIS 14 CB*1234")
# → "MONOPRIX"

extract_location("MONOPRIX PARIS 14")
# → "PARIS 14"
```

### 2. ✅ Taxonomie PFCv2 (`modules/transactions/constants.py`)

**20 catégories principales:**
- INCOME (Salary, Freelance, Investments...)
- FOOD_AND_DRINK (Groceries, Restaurants, Fast Food...)
- TRANSPORTATION (Fuel, Public Transit, Taxi...)
- HOME (Rent, Utilities, Internet...)
- HEALTH (Medical, Pharmacy, Gym...)
- ENTERTAINMENT (Streaming, Movies, Games...)
- Et 14 autres catégories...

**Plus de 80 sous-catégories au total!**

**Patterns heuristiques:** 30+ patterns regex pour la catégorisation automatique

### 3. ✅ Service de catégorisation (`modules/transactions/services.py`)

**Cascade de confiance:**
1. **HEURISTIC** (règles regex) → Confiance 95%
2. **SIMILARITY** (SequenceMatcher > 0.85) → Confiance basée sur le score
3. **LOCAL_AI** (Llama 3.2) → Confiance IA locale
4. **CLOUD_AI** (Gemini/DeepSeek fallback) → Confiance IA cloud

**Résultat enrichi:**
```python
@dataclass
class CategorizationServiceResult:
    category: str              # "FOOD_AND_DRINK > Groceries"
    main_category: str         # "FOOD_AND_DRINK"
    subcategory: str           # "Groceries"
    clean_merchant: str        # "CARREFOUR"
    confidence: float          # 0.95
    method: CategorizationMethod  # HEURISTIC
    is_income: bool            # False
    is_expense: bool           # True
    metadata: dict             # Métadonnées complètes
```

### 4. ✅ Migration pour champ `meta_data`

**Fichiers créés:**
- `migrations/add_meta_data_column.sql` - Script SQL
- `migrations/migrate_meta_data.py` - Script Python avec rapport

**Contenu du champ JSON:**
```json
{
  "categorization": {
    "method": "HEURISTIC",
    "confidence_score": 0.95,
    "timestamp": "2024-01-15T10:30:00",
    "version": "2.0"
  },
  "clean_merchant": "CARREFOUR",
  "is_recurring_candidate": false,
  "risk_flag": 0
}
```

## 📊 Tests validés

```bash
✅ Imports des nouveaux modules
✅ clean_merchant_name("MONOPRIX PARIS 14 CB*1234") → "Monoprix"
✅ extract_location("MONOPRIX PARIS 14") → "PARIS 14"
✅ categorize_transaction("CARREFOUR", -45.67, "2024-01-15")
   → Category: "Food & Drink > Groceries"
   → Method: HEURISTIC
   → Confidence: 0.95
✅ Colonne meta_data ajoutée automatiquement
✅ Sérialisation JSON des résultats
```

## 🔧 Architecture

```
modules/transactions/
├── __init__.py          # Exports publics
├── constants.py         # PFCv2 + patterns + utilitaires
└── services.py          # Service de catégorisation

src/
├── __init__.py          # Exports publics
└── data_cleaning.py     # Nettoyage avancé des libellés

migrations/
├── add_meta_data_column.sql   # Migration SQL
└── migrate_meta_data.py       # Script Python
```

## 🎓 Utilisation

### Nettoyage de libellés
```python
from src.data_cleaning import clean_merchant_name, extract_location

cleaned = clean_merchant_name("MONOPRIX PARIS 14 CB*1234")
# → "MONOPRIX"

location = extract_location("MONOPRIX PARIS 14")
# → "PARIS 14"
```

### Catégorisation
```python
from modules.transactions import categorize_transaction

result = categorize_transaction("CARREFOUR MARKET", -45.67, "2024-01-15")
print(result.category)      # "Food & Drink > Groceries"
print(result.confidence)    # 0.95
print(result.method)        # CategorizationMethod.HEURISTIC

# Sauvegarder avec métadonnées
service = get_categorization_service()
service.save_categorization(transaction_id=123, result=result)
```

### Accès aux constantes
```python
from modules.transactions.constants import PFCV2_CATEGORIES, is_expense_category

# Liste des catégories
main_cats = PFCV2_CATEGORIES.keys()
sub_cats = PFCV2_CATEGORIES["FOOD_AND_DRINK"]

# Vérifier le type
is_expense_category("FOOD_AND_DRINK")  # True
is_income_category("INCOME")           # True
```

## 🚀 Prochaines étapes

- [ ] Intégrer `clean_merchant_name()` dans le pipeline d'import
- [ ] Migrer les transactions existantes avec `migrate_meta_data.py`
- [ ] Utiliser `CategorizationService` dans l'interface utilisateur
- [ ] Ajouter des métriques de qualité de catégorisation
