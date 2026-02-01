# Plan de Correction - Requêtes DB N+1

> Ce document décrit les problèmes de requêtes DB dans des boucles (pattern N+1) 
> identifiés lors de l'audit, avec les solutions recommandées.

---

## Résumé

| Fichier | Problèmes | Priorité | Complexité |
|---------|-----------|----------|------------|
| `modules/db/audit.py` | 9 | HAUTE | Moyenne |
| `modules/db/tags.py` | 4 | MOYENNE | Faible |
| `modules/db/migrations.py` | 4 | BASSE | Faible |
| `modules/db/transactions.py` | 4 | HAUTE | Moyenne |
| **TOTAL** | **21** | | |

---

## modules/db/audit.py (9 problèmes)

### Problème 1-2 : Correction des accents (lignes 31-35)

**Code actuel (inefficace):**
```python
for wrong, right in fixes.items():
    cursor.execute("SELECT count(*) FROM members WHERE name = ?", (right,))
    if cursor.fetchone()[0] > 0:
        cursor.execute("UPDATE transactions SET member = ? WHERE member = ?", (right, wrong))
        cursor.execute("UPDATE transactions SET beneficiary = ? WHERE beneficiary = ?", (right, wrong))
```

**Problème:** 2 requêtes SELECT par itération + 2 UPDATE conditionnels

**Solution optimisée:**
```python
# Une seule requête pour récupérer tous les membres valides
valid_members = set()
cursor.execute("SELECT name FROM members")
valid_members = {row[0] for row in cursor.fetchall()}

# Batch update avec executemany
updates_member = []
updates_beneficiary = []

for wrong, right in fixes.items():
    if right in valid_members:
        updates_member.append((right, wrong))
        updates_beneficiary.append((right, wrong))

if updates_member:
    cursor.executemany("UPDATE transactions SET member = ? WHERE member = ?", updates_member)
    cursor.executemany("UPDATE transactions SET beneficiary = ? WHERE beneficiary = ?", updates_beneficiary)
```

**Gain:** O(n) → O(1) + batch updates

---

### Problème 3 : Détection des doublons (lignes 42-50)

**Code actuel:**
```python
for _, row in dups.iterrows():
    cursor.execute("SELECT id FROM transactions WHERE date = ? AND label = ? AND amount = ? ORDER BY id ASC",
                   (str(row['date']), row['label'], row['amount']))
    ids = [r[0] for r in cursor.fetchall()]
    to_delete = ids[1:]
    if to_delete:
        placeholders = ','.join(['?'] * len(to_delete))
        cursor.execute(f"DELETE FROM transactions WHERE id IN ({placeholders})", to_delete)
```

**Solution optimisée:**
```python
# Une seule requête pour récupérer tous les IDs à supprimer
cursor.execute("""
    SELECT date, label, amount, GROUP_CONCAT(id) as ids
    FROM transactions
    GROUP BY date, label, amount
    HAVING COUNT(*) > 1
""")

all_ids_to_delete = []
for row in cursor.fetchall():
    ids = [int(x) for x in row[3].split(',')]
    all_ids_to_delete.extend(ids[1:])  # Tous sauf le premier

# Batch delete
if all_ids_to_delete:
    placeholders = ','.join(['?'] * len(all_ids_to_delete))
    cursor.execute(f"DELETE FROM transactions WHERE id IN ({placeholders})", all_ids_to_delete)
```

---

### Problème 4 : Normalisation des tags (lignes 56-63)

**Code actuel:**
```python
for tx_id, tags_str in idx_tags:
    normalized = ", ".join(sorted(list(set([t.strip().lower() for t in tags_str.split(',') if t.strip()]))))
    if normalized != tags_str:
        cursor.execute("UPDATE transactions SET tags = ? WHERE id = ?", (normalized, tx_id))
```

**Solution optimisée:**
```python
# Batch update
updates = []
for tx_id, tags_str in idx_tags:
    normalized = ", ".join(sorted(list(set([t.strip().lower() for t in tags_str.split(',') if t.strip()]))))
    if normalized != tags_str:
        updates.append((normalized, tx_id))

if updates:
    cursor.executemany("UPDATE transactions SET tags = ? WHERE id = ?", updates)
```

---

### Problème 5 : Ré-application des règles (lignes 74)

**Code actuel:**
```python
for _, row in pending_df.iterrows():
    # Traitement...
```

**Solution:** Ce pattern est acceptable si `apply_rules` est rapide. 
À surveiller si `pending_df` est grand (>1000 lignes).

---

## modules/db/tags.py (4 problèmes)

### Problème 1 : Suppression de tag (lignes 66-70)

**Code actuel:**
```python
for tx_id, tags_str in idx_tags:
    current_tags = [t.strip() for t in tags_str.split(',') if t.strip()]
    if tag_to_remove in current_tags:
        current_tags.remove(tag_to_remove)
        new_tags_str = ", ".join(current_tags) if current_tags else ""
        cursor.execute("UPDATE transactions SET tags = ? WHERE id = ?", (new_tags_str, tx_id))
```

**Solution optimisée:**
```python
# Batch update
updates = []
for tx_id, tags_str in idx_tags:
    current_tags = [t.strip() for t in tags_str.split(',') if t.strip()]
    if tag_to_remove in current_tags:
        current_tags.remove(tag_to_remove)
        new_tags_str = ", ".join(current_tags) if current_tags else ""
        updates.append((new_tags_str, tx_id))

if updates:
    cursor.executemany("UPDATE transactions SET tags = ? WHERE id = ?", updates)
```

---

### Problème 2 : Apprentissage des tags (lignes 119-139)

**Code actuel:**
```python
for cat, tags in cat_tags_map.items():
    cursor.execute("SELECT id, suggested_tags FROM categories WHERE name = ?", (cat,))
    row = cursor.fetchone()
    if row:
        cat_id, existing_str = row
        # ... traitement
        cursor.execute("UPDATE categories SET suggested_tags = ? WHERE id = ?", (new_str, cat_id))
```

**Solution optimisée:**
```python
# Récupérer toutes les catégories en une requête
cursor.execute("SELECT id, name, suggested_tags FROM categories WHERE name IN (%s)" % 
               ','.join(['?'] * len(cat_tags_map)), tuple(cat_tags_map.keys()))
cat_data = {row[1]: (row[0], row[2]) for row in cursor.fetchall()}

# Batch update
updates = []
for cat, tags in cat_tags_map.items():
    if cat in cat_data:
        cat_id, existing_str = cat_data[cat]
        # ... traitement
        if len(new_set) > len(existing):
            updates.append((new_str, cat_id))

if updates:
    cursor.executemany("UPDATE categories SET suggested_tags = ? WHERE id = ?", updates)
```

---

## modules/db/transactions.py (4 problèmes)

Les problèmes sont dans des fonctions de traitement batch. Solutions similaires:
- Remplacer `execute()` par `executemany()` dans les boucles
- Utiliser `GROUP_CONCAT` pour agréger les données
- Précharger les données de référence avant les boucles

---

## Ordre de correction recommandé

1. **modules/db/audit.py** - Plus gros impact (9 problèmes)
2. **modules/db/transactions.py** - Fonctions fréquemment utilisées
3. **modules/db/tags.py** - Impact moyen
4. **modules/db/migrations.py** - Moins critique (exécuté rarement)

---

## Template de correction

Pour corriger un pattern N+1:

```python
# AVANT (N+1)
for item in items:
    cursor.execute("SELECT ... WHERE id = ?", (item.id,))
    result = cursor.fetchone()
    cursor.execute("UPDATE ... SET ... WHERE id = ?", (values, item.id))

# APRÈS (Optimisé)
# 1. Précharger les données de référence
ids = [item.id for item in items]
cursor.execute("SELECT ... WHERE id IN (%s)" % ','.join(['?'] * len(ids)), ids)
ref_data = {row[0]: row for row in cursor.fetchall()}

# 2. Préparer les mises à jour batch
updates = []
for item in items:
    updates.append((values, item.id))

# 3. Exécuter en batch
if updates:
    cursor.executemany("UPDATE ... SET ... WHERE id = ?", updates)
```

---

*Document généré automatiquement lors de l'audit du 2026-02-01*
