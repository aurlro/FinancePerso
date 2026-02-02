# 📋 Guide : Système de Types de Transactions

## 🎯 Principe Fondamental

**Une transaction est définie par SA CATÉGORIE, pas par le signe de son montant.**

```
❌ Ancienne méthode (incorrecte) :
   Montant > 0 = Revenu
   Montant < 0 = Dépense

✅ Nouvelle méthode (correcte) :
   Catégorie = "Salaire" → Revenu (doit avoir montant > 0)
   Catégorie = "Alimentation" → Dépense (doit avoir montant < 0)
   Catégorie = "Virement Interne" → Exclu (montant quelconque)
```

---

## 📁 Structure du Module

```python
# modules/transaction_types.py

# Listes de catégories
INCOME_CATEGORIES = ['Revenus', 'Salaire', 'Prime', ...]
EXCLUDED_CATEGORIES = ['Virement Interne', 'Hors Budget', ...]
REFUND_CATEGORIES = ['Remboursement', ...]

# Fonctions de détection
is_income_category(category)     # True/False
is_expense_category(category)    # True/False
is_excluded_category(category)   # True/False

# Filtrage DataFrame
filter_income_transactions(df)   # Retourne DataFrame revenus
filter_expense_transactions(df)  # Retourne DataFrame dépenses

# Calculs financiers
calculate_true_income(df)        # Somme des vrais revenus
calculate_true_expenses(df)      # Somme des vraies dépenses
calculate_savings_rate(df)       # Taux d'épargne correct
```

---

## 🔧 Utilisation dans le Code

### Avant (Incorrect)
```python
# Calcul des dépenses par signe (problématique)
expenses = df[df['amount'] < 0]['amount'].sum()
income = df[df['amount'] > 0]['amount'].sum()

# Filtrage par catégorie hardcodé
df_exp = df[
    (df['amount'] < 0) & 
    (~df['category_validated'].isin(['Revenus', ...]))
]
```

### Après (Correct)
```python
from modules.transaction_types import (
    calculate_true_income,
    calculate_true_expenses,
    filter_expense_transactions
)

# Calcul par catégories (fiable)
expenses = calculate_true_expenses(df, include_refunds=True)
income = calculate_true_income(df, include_refunds=False)

# Filtrage par catégories centralisé
df_exp = filter_expense_transactions(df)
```

---

## ✅ Validation des Transactions

### Vérifier la cohérence
```python
from modules.transaction_types import validate_amount_consistency

is_valid, warning = validate_amount_consistency('Salaire', -2500)
# is_valid = False
# warning = "La catégorie 'Salaire' est un revenu mais le montant est négatif (-2500)"
```

### Utilisation dans les imports
```python
# Détecter les transactions incohérentes
df['is_coherent'] = df.apply(
    lambda x: validate_amount_consistency(
        x['category_validated'], 
        x['amount']
    )[0],
    axis=1
)

# Afficher les problèmes
problems = df[~df['is_coherent']]
```

---

## 📊 Impact sur les KPI

| KPI | Ancien calcul | Nouveau calcul | Différence |
|-----|---------------|----------------|------------|
| **Revenus** | `sum(amount > 0)` | `sum(catégories revenu)` | Exclut remboursements mal catégorisés |
| **Dépenses** | `sum(amount < 0)` | `sum(catégories dépense)` | Exclut erreurs de signe |
| **Épargne** | `(+)-(-)` | `Revenus - Dépenses` | Plus fiable |
| **Taux épargne** | `épargne/revenus` | `épargne/vrais revenus` | Plus représentatif |

---

## 🎨 UX et Messages Utilisateur

### Affichage des types
```python
from modules.transaction_types import get_category_type

type_label = {
    'income': '💰 Revenu',
    'expense': '💸 Dépense',
    'refund': '↩️ Remboursement',
    'excluded': '🚫 Exclu',
    'unknown': '❓ Inconnu'
}

cat_type = get_category_type(transaction['category'])
st.write(f"Type : {type_label[cat_type]}")
```

### Alertes incohérence
```python
# Dans la page de validation
if not is_valid:
    st.warning(f"⚠️ {warning}")
    st.info("💡 Vérifiez que le signe du montant correspond à la catégorie.")
```

---

## 🔄 Migration des Données Existantes

### Identifier les problèmes
```python
# Script de diagnostic
def find_inconsistent_transactions(df):
    '''Trouve les transactions incohérentes.'''
    problems = []
    
    for _, row in df.iterrows():
        is_valid, warning = validate_amount_consistency(
            row['category_validated'],
            row['amount']
        )
        if not is_valid:
            problems.append({
                'id': row['id'],
                'label': row['label'],
                'amount': row['amount'],
                'category': row['category_validated'],
                'warning': warning
            })
    
    return pd.DataFrame(problems)

# Utilisation
problems = find_inconsistent_transactions(df)
print(f"{len(problems)} transactions incohérentes trouvées")
```

### Correction automatique
```python
def fix_amount_sign(row):
    '''Corrige le signe du montant selon la catégorie.'''
    from modules.transaction_types import suggest_amount_sign
    
    expected_sign = suggest_amount_sign(row['category_validated'])
    
    if expected_sign == 0:  # Exclu
        return row['amount']
    elif expected_sign == 1 and row['amount'] < 0:  # Devrait être positif
        return abs(row['amount'])
    elif expected_sign == -1 and row['amount'] > 0:  # Devrait être négatif
        return -abs(row['amount'])
    
    return row['amount']

# Appliquer la correction
df['amount_fixed'] = df.apply(fix_amount_sign, axis=1)
```

---

## 🧪 Tests et Vérifications

### Tests unitaires
```python
def test_transaction_types():
    # Test revenu
    assert is_income_category('Salaire') == True
    assert is_expense_category('Salaire') == False
    
    # Test dépense
    assert is_expense_category('Alimentation') == True
    assert is_income_category('Alimentation') == False
    
    # Test exclusion
    assert is_excluded_category('Virement Interne') == True
    assert is_income_category('Virement Interne') == False
    
    # Test validation
    valid, _ = validate_amount_consistency('Salaire', 2500)
    assert valid == True
    
    valid, _ = validate_amount_consistency('Salaire', -2500)
    assert valid == False
```

---

## 📚 Référence Rapide

| Fonction | Usage | Return |
|----------|-------|--------|
| `is_income_category(cat)` | Vérifier si revenu | `bool` |
| `is_expense_category(cat)` | Vérifier si dépense | `bool` |
| `is_excluded_category(cat)` | Vérifier si exclu | `bool` |
| `get_category_type(cat)` | Obtenir le type | `'income'/'expense'/'excluded'/...` |
| `filter_income_transactions(df)` | Filtrer revenus | `DataFrame` |
| `filter_expense_transactions(df)` | Filtrer dépenses | `DataFrame` |
| `calculate_true_income(df)` | Calculer revenus | `float` |
| `calculate_true_expenses(df)` | Calculer dépenses | `float` |
| `calculate_savings_rate(df)` | Calculer taux | `float` |
| `validate_amount_consistency(cat, amount)` | Valider | `(bool, str)` |
| `suggest_amount_sign(cat)` | Suggérer signe | `1/-1/0` |

---

## ⚠️ Points d'Attention

1. **Les remboursements** : Ce sont des entrées d'argent mais PAS des revenus
   - Catégorie = "Remboursement" 
   - Montant > 0
   - Traitement spécial dans `calculate_true_expenses()`

2. **Les virements internes** : Ni revenu ni dépense
   - Exclus de tous les calculs financiers
   - Utilisés uniquement pour le suivi des mouvements

3. **Personnalisation** : Les listes de catégories sont modifiables
   ```python
   from modules.transaction_types import INCOME_CATEGORIES
   INCOME_CATEGORIES.append('Nouvelle Catégorie')
   ```
