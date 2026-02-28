# 🔍 Audit : Distinction Revenus vs Dépenses

**Date** : 2026-02-02  
**Problème** : L'application mélange les critères (montant vs catégorie) ce qui crée des incohérences dans les KPI et conseils.

---

## 📊 Comment l'app détermine Revenu vs Dépense aujourd'hui

### Méthode 1 : Par le signe du montant (KPI, Stats)
```python
# Dans modules/db/stats.py:70-71
inc = df_curr[df_curr['amount'] > 0]['amount'].sum()  # Revenus = positif
exp = abs(df_curr[df_curr['amount'] < 0]['amount'].sum())  # Dépenses = négatif
```

### Méthode 2 : Par la catégorie "Revenus" (Graphiques)
```python
# Dans category_charts.py:21
df_exp = df_current[
    (df_current['amount'] < 0) & 
    (~df_current['category_validated'].isin(['Revenus', 'Virement Interne', 'Hors Budget']))
]
```

### Problème
Si une transaction a :
- Montant POSITIF mais catégorie "Alimentation" → Comptée comme REVENU dans les KPI
- Montant NÉGATIF mais catégorie "Revenus" → Exclue des graphiques mais comptée comme DÉPENSE dans les KPI

---

## 🔴 Incohérences Identifiées

### 1. KPI Cards (kpi_cards.py)
```python
cur_exp = abs(df_current[df_current['amount'] < 0]['amount'].sum())
cur_rev = df_current[df_current['amount'] > 0]['amount'].sum()
```
❌ **Problème** : Une remboursement d'assurance (montant +, catégorie "Assurance") est compté comme REVENU

### 2. Graphiques de catégories
```python
# Exclut uniquement par catégorie
df_exp = df_current[
    (df_current['amount'] < 0) & 
    (~df_current['category_validated'].isin(['Revenus', ...]))
]
```
❌ **Problème** : Une transaction "Alimentation" avec montant positif (erreur) apparaît dans les graphiques

### 3. Budgets
```python
# Dans budgets.py - AUCUNE vérification de type
def set_budget(category: str, amount: float):
    cursor.execute("INSERT...", (category, amount))
```
❌ **Problème** : On peut créer un budget pour la catégorie "Revenus" ou "Salaire"

### 4. Top Dépenses
```python
# top_expenses.py:18
(~df_current['category_validated'].isin(['Revenus', ...]))
```
❌ **Problème** : Si un remboursement a catégorie "Remboursement" (non exclue), il apparaît dans le top

### 5. Analyse des récurrences
```python
# analytics_v2.py
expenses = filtered_df[filtered_df['avg_amount'] < 0]
incomes = filtered_df[filtered_df['avg_amount'] > 0]
```
❌ **Problème** : Même logique basée uniquement sur le montant

---

## 📋 Liste des Catégories "Spéciales" Non Définies

| Type | Catégories attendues | Où définies ? |
|------|---------------------|---------------|
| **Revenus** | Revenus, Salaire, Prime, Remboursement | ❌ Nulle part centralisé |
| **Exclusions** | Virement Interne, Hors Budget | ✅ Hardcodé dans les graphiques |
| **Dépenses** | Toutes les autres | ❌ Par défaut (tout ce qui n'est pas exclu) |

---

## 💡 Solutions Proposées

### Solution 1 : Centraliser la définition (Recommandée)
Créer un module `modules/transaction_types.py` :

```python
INCOME_CATEGORIES = ['Revenus', 'Salaire', 'Prime', 'Remboursement', ...]
EXPENSE_CATEGORIES = ['Alimentation', 'Logement', 'Transport', ...]  # Ou calcul dynamique
EXCLUDE_CATEGORIES = ['Virement Interne', 'Hors Budget']

def is_income_category(category: str) -> bool:
    return category in INCOME_CATEGORIES

def is_expense_category(category: str) -> bool:
    return category not in INCOME_CATEGORIES and category not in EXCLUDE_CATEGORIES
```

### Solution 2 : Validation à l'import
Forcer la cohérence montant/catégorie :
- Si catégorie dans INCOME_CATEGORIES → montant doit être positif
- Si catégorie dans EXPENSE_CATEGORIES → montant doit être négatif

### Solution 3 : Double critère partout
Tous les calculs utilisent :
```python
# Revenus = catégorie revenu ET montant positif
income = df[
    (df['category_validated'].isin(INCOME_CATEGORIES)) & 
    (df['amount'] > 0)
]

# Dépenses = catégorie NON revenu ET montant négatif
expenses = df[
    (~df['category_validated'].isin(INCOME_CATEGORIES + EXCLUDE_CATEGORIES)) & 
    (df['amount'] < 0)
]
```

---

## 🎯 Plan d'Action Correctif

### Phase 1 : Définition Centralisée (Immédiat)
- [ ] Créer `modules/transaction_types.py` avec les constantes
- [ ] Créer fonctions utilitaires `is_income()`, `is_expense()`, `is_excluded()`
- [ ] Documenter la logique dans AGENTS.md

### Phase 2 : Correction des KPI (Court terme)
- [ ] Modifier `kpi_cards.py` pour utiliser les catégories
- [ ] Modifier `stats.py` pour utiliser les catégories
- [ ] Modifier `analytics_v2.py` pour utiliser les catégories

### Phase 3 : Validation (Moyen terme)
- [ ] Ajouter validation dans `categorization.py`
- [ ] Ajouter alerte si montant incohérent avec catégorie
- [ ] Créer outil de correction en masse

### Phase 4 : Budgets (Moyen terme)
- [ ] Empêcher création budget sur catégorie revenu
- [ ] Ajouter option "Budget de revenu" (objectif de revenu)

---

## 🧪 Tests de Validation

```python
# Test cas limites
def test_income_expense_detection():
    # Cas 1 : Revenu standard
    assert is_income('Salaire', 2500.00) == True
    
    # Cas 2 : Dépense standard
    assert is_expense('Alimentation', -45.50) == True
    
    # Cas 3 : Remboursement (positif mais pas revenu)
    assert is_income('Remboursement', 150.00) == True  # Ou False selon choix
    
    # Cas 4 : Erreur de saisie (négatif dans revenu)
    assert is_income('Salaire', -100.00) == False  # Détecter incohérence
    
    # Cas 5 : Virement interne (exclu)
    assert is_excluded('Virement Interne', -500.00) == True
```

---

## 📈 Impact sur les Utilisateurs

| Scénario | Avant | Après correction |
|----------|-------|------------------|
| Remboursement mutuelle | Compté comme REVENU | Compté comme REMBOURSEMENT (ni revenu ni dépense, ou crédit sur Santé) |
| Erreur de signe | Silencieuse | Alerte + suggestion correction |
| Budget sur "Revenus" | Autorisé | Bloqué + message explicatif |
| KPI épargne | Potentiellement faux | Fiable |

---

## 🔧 Code de Transition (Migration)

```python
# modules/migration_transaction_types.py
"""
Script de migration pour corriger les transactions incohérentes.
"""

def fix_amount_sign_inconsistencies():
    '''
    Corrige les transactions où le signe ne correspond pas à la catégorie.
    '''
    # 1. Identifier revenus avec montant négatif
    # 2. Identifier dépenses avec montant positif
    # 3. Proposer correction ou créer alerte
    pass
```
