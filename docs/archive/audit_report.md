# Rapport d'Audit Streamlit

**Date** : 2026-02-01 17:35
**Application** : `/Users/aurelien/Documents/Projets/FinancePerso`

## Résumé

- **Problèmes critiques** : 41
- **Avertissements** : 512
- **Optimisations suggérées** : 172
- **Total** : 725 problèmes détectés

---

## Problèmes Critiques (A corriger en priorité)

### 1. Requête base de données dans une boucle

**ID** : `PERFORMANCE-001`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/audit.py:31`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 31). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 2. Requête base de données dans une boucle

**ID** : `PERFORMANCE-001`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/tags.py:32`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 32). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 3. Requête base de données dans une boucle

**ID** : `PERFORMANCE-004`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/audit.py:32`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 32). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 4. Requête base de données dans une boucle

**ID** : `PERFORMANCE-002`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/audit.py:33`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 33). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 5. Requête base de données dans une boucle

**ID** : `PERFORMANCE-003`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/audit.py:35`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 35). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 6. Requête base de données dans une boucle

**ID** : `PERFORMANCE-005`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/audit.py:42`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 42). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 7. Requête base de données dans une boucle

**ID** : `PERFORMANCE-007`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/audit.py:46`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 46). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 8. Requête base de données dans une boucle

**ID** : `PERFORMANCE-006`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/audit.py:50`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 50). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 9. Requête base de données dans une boucle

**ID** : `PERFORMANCE-001`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/migrations.py:57`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 57). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 10. Requête base de données dans une boucle

**ID** : `PERFORMANCE-008`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/audit.py:63`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 63). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 11. Requête base de données dans une boucle

**ID** : `PERFORMANCE-002`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/tags.py:70`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 70). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 12. Requête base de données dans une boucle

**ID** : `PERFORMANCE-009`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/audit.py:77`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 77). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 13. Requête base de données dans une boucle

**ID** : `PERFORMANCE-001`
**Catégorie** : PERFORMANCE
**Emplacement** : `./scripts/profile_db.py:88`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 88). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 14. Requête base de données dans une boucle

**ID** : `PERFORMANCE-004`
**Catégorie** : PERFORMANCE
**Emplacement** : `./scripts/profile_db.py:89`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 89). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 15. Requête base de données dans une boucle

**ID** : `PERFORMANCE-002`
**Catégorie** : PERFORMANCE
**Emplacement** : `./scripts/profile_db.py:92`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 92). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 16. Requête base de données dans une boucle

**ID** : `PERFORMANCE-003`
**Catégorie** : PERFORMANCE
**Emplacement** : `./scripts/profile_db.py:93`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 93). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 17. Requête base de données dans une boucle

**ID** : `PERFORMANCE-003`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/tags.py:115`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 115). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 18. Requête base de données dans une boucle

**ID** : `PERFORMANCE-005`
**Catégorie** : PERFORMANCE
**Emplacement** : `./scripts/profile_db.py:121`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 121). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 19. Requête base de données dans une boucle

**ID** : `PERFORMANCE-004`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/tags.py:121`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 121). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 20. Requête base de données dans une boucle

**ID** : `PERFORMANCE-005`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/tags.py:122`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 122). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 21. Requête base de données dans une boucle

**ID** : `PERFORMANCE-001`
**Catégorie** : PERFORMANCE
**Emplacement** : `./tests/ui/test_kpi_cards.py:123`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 123). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 22. Requête base de données dans une boucle

**ID** : `PERFORMANCE-002`
**Catégorie** : PERFORMANCE
**Emplacement** : `./tests/ui/test_kpi_cards.py:130`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 130). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 23. Requête base de données dans une boucle

**ID** : `PERFORMANCE-006`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/tags.py:135`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 135). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 24. Requête base de données dans une boucle

**ID** : `PERFORMANCE-002`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/migrations.py:145`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 145). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 25. Requête base de données dans une boucle

**ID** : `PERFORMANCE-003`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/migrations.py:150`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 150). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 26. Requête base de données dans une boucle

**ID** : `PERFORMANCE-001`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/transactions.py:159`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 159). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 27. Requête base de données dans une boucle

**ID** : `PERFORMANCE-001`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/update_manager.py:215`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 215). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 28. Requête base de données dans une boucle

**ID** : `PERFORMANCE-002`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/update_manager.py:216`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 216). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 29. Requête base de données dans une boucle

**ID** : `PERFORMANCE-001`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/cache_multitier.py:278`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 278). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 30. Requête base de données dans une boucle

**ID** : `PERFORMANCE-001`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/encryption.py:283`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 283). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 31. Requête base de données dans une boucle

**ID** : `PERFORMANCE-002`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/encryption.py:284`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 284). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 32. Requête base de données dans une boucle

**ID** : `PERFORMANCE-004`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/migrations.py:284`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 284). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 33. Requête base de données dans une boucle

**ID** : `PERFORMANCE-002`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/transactions.py:286`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 286). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 34. Requête base de données dans une boucle

**ID** : `PERFORMANCE-004`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/encryption.py:295`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 295). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 35. Requête base de données dans une boucle

**ID** : `PERFORMANCE-005`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/encryption.py:295`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 295). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 36. Requête base de données dans une boucle

**ID** : `PERFORMANCE-003`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/encryption.py:301`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 301). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 37. Requête base de données dans une boucle

**ID** : `PERFORMANCE-001`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/transactions_batch.py:319`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 319). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 38. Requête base de données dans une boucle

**ID** : `PERFORMANCE-001`
**Catégorie** : PERFORMANCE
**Emplacement** : `./pages/1_Import.py:337`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 337). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 39. Requête base de données dans une boucle

**ID** : `PERFORMANCE-003`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/transactions.py:432`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 432). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 40. Requête base de données dans une boucle

**ID** : `PERFORMANCE-001`
**Catégorie** : PERFORMANCE
**Emplacement** : `./tests/test_integration.py:477`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 477). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---

### 41. Requête base de données dans une boucle

**ID** : `PERFORMANCE-004`
**Catégorie** : PERFORMANCE
**Emplacement** : `./modules/db/transactions.py:498`

**Description** : Opération DB détectée à l'intérieur d'une boucle for (ligne 498). Cela cause une complexité O(n) au lieu de O(1).

**Correction suggérée** :
```
Utiliser executemany() ou récupérer toutes les données avant la boucle
```

---


## Avertissements

- **Exception handler nu (except:)** (`./modules/ui/rules/rule_manager.py:181`)
  - Except nu détecté ligne 181. Cela masque toutes les exceptions.
  - *Correction* : Spécifier les types d'exceptions attendues: except (ValueError, TypeError):

- **Exception handler nu (except:)** (`./modules/ai_manager.py:326`)
  - Except nu détecté ligne 326. Cela masque toutes les exceptions.
  - *Correction* : Spécifier les types d'exceptions attendues: except (ValueError, TypeError):

- **Exception handler nu (except:)** (`./pages/2_Validation.py:377`)
  - Except nu détecté ligne 377. Cela masque toutes les exceptions.
  - *Correction* : Spécifier les types d'exceptions attendues: except (ValueError, TypeError):

- **Aucun @st.cache_data détecté** (`./test_components.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./app.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./tests/conftest.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./tests/ui/test_kpi_cards.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/impact_analyzer.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/cache_manager.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/feedback.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/layout.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/__init__.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/config/category_management.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/config/config_mode.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/config/log_viewer.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/config/api_settings.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/config/tags_rules.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/config/backup_restore.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/config/audit_tools.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/config/notifications.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/config/config_dashboard.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/config/member_management.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/config/data_operations.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/dashboard/kpi_cards.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/dashboard/top_expenses.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/dashboard/budget_tracker.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/dashboard/ai_insights.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/components/progress_tracker.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/components/onboarding_modal.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/components/member_selector.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/components/tag_manager.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/components/transaction_drill_down.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/components/quick_actions.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/components/tag_selector_smart.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/components/profile_form.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/components/tag_selector_compact.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/components/local_ml_manager.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/components/filters.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/ui/rules/rule_validator.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./modules/db/rules.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./pages/4_Recurrence.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./pages/9_Configuration.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./pages/98_Tests.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./pages/5_Assistant.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./pages/1_Import.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./pages/2_Validation.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./pages/10_Nouveautés.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Aucun @st.cache_data détecté** (`./pages/4_Regles.py`)
  - Le fichier utilise Streamlit mais n'a pas de cache. Les données sont rechargées à chaque interaction.
  - *Correction* : Ajouter @st.cache_data sur les fonctions de chargement de données

- **Session state 'config_advanced_mode' peut ne pas être initialisé** (`./modules/ui/config/config_mode.py:15`)
  - Accès à st.session_state['config_advanced_mode'] sans vérification préalable ligne 15.
  - *Correction* : Initialiser avec: if 'config_advanced_mode' not in st.session_state: st.session_state['config_advanced_mode'] = default_value

- **Session state 'notif_preview' peut ne pas être initialisé** (`./modules/ui/config/notifications.py:23`)
  - Accès à st.session_state['notif_preview'] sans vérification préalable ligne 23.
  - *Correction* : Initialiser avec: if 'notif_preview' not in st.session_state: st.session_state['notif_preview'] = default_value

- **Widget sans clé: button** (`./modules/ui/config/config_mode.py:26`)
  - Le widget button ligne 26 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_26'

- **Session state 'pending_rename' peut ne pas être initialisé** (`./modules/ui/config/member_management.py:26`)
  - Accès à st.session_state['pending_rename'] sans vérification préalable ligne 26.
  - *Correction* : Initialiser avec: if 'pending_rename' not in st.session_state: st.session_state['pending_rename'] = default_value

- **Session state 'excluded_tx_ids' peut ne pas être initialisé** (`./pages/2_Validation.py:30`)
  - Accès à st.session_state['excluded_tx_ids'] sans vérification préalable ligne 30.
  - *Correction* : Initialiser avec: if 'excluded_tx_ids' not in st.session_state: st.session_state['excluded_tx_ids'] = default_value

- **Widget sans clé: radio** (`./pages/98_Tests.py:32`)
  - Le widget radio ligne 32 n'a pas de clé explicite.
  - *Correction* : Ajouter key='radio_32'

- **Widget sans clé: metric** (`./modules/ui/config/log_viewer.py:33`)
  - Le widget metric ligne 33 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_33'

- **Widget sans clé: button** (`./modules/ui/config/member_management.py:33`)
  - Le widget button ligne 33 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_33'

- **Widget sans clé: selectbox** (`./pages/10_Nouveautés.py:33`)
  - Le widget selectbox ligne 33 n'a pas de clé explicite.
  - *Correction* : Ajouter key='selectbox_33'

- **Session state 'onboarding_dismissed' peut ne pas être initialisé** (`./modules/ui/components/onboarding_modal.py:35`)
  - Accès à st.session_state['onboarding_dismissed'] sans vérification préalable ligne 35.
  - *Correction* : Initialiser avec: if 'onboarding_dismissed' not in st.session_state: st.session_state['onboarding_dismissed'] = default_value

- **Session state 'pending_rename' peut ne pas être initialisé** (`./modules/ui/config/member_management.py:36`)
  - Accès à st.session_state['pending_rename'] sans vérification préalable ligne 36.
  - *Correction* : Initialiser avec: if 'pending_rename' not in st.session_state: st.session_state['pending_rename'] = default_value

- **Session state 'notif_preview' peut ne pas être initialisé** (`./modules/ui/config/notifications.py:37`)
  - Accès à st.session_state['notif_preview'] sans vérification préalable ligne 37.
  - *Correction* : Initialiser avec: if 'notif_preview' not in st.session_state: st.session_state['notif_preview'] = default_value

- **Session state 'editing_member_id' peut ne pas être initialisé** (`./modules/ui/config/member_management.py:37`)
  - Accès à st.session_state['editing_member_id'] sans vérification préalable ligne 37.
  - *Correction* : Initialiser avec: if 'editing_member_id' not in st.session_state: st.session_state['editing_member_id'] = default_value

- **Widget sans clé: metric** (`./modules/ui/config/log_viewer.py:38`)
  - Le widget metric ligne 38 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_38'

- **Widget sans clé: button** (`./modules/ui/components/quick_actions.py:41`)
  - Le widget button ligne 41 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_41'

- **Widget sans clé: toggle** (`./modules/ui/config/notifications.py:42`)
  - Le widget toggle ligne 42 n'a pas de clé explicite.
  - *Correction* : Ajouter key='toggle_42'

- **Session state 'temp_custom_tags' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_compact.py:42`)
  - Accès à st.session_state['temp_custom_tags'] sans vérification préalable ligne 42.
  - *Correction* : Initialiser avec: if 'temp_custom_tags' not in st.session_state: st.session_state['temp_custom_tags'] = default_value

- **Session state 'onboarding_step' peut ne pas être initialisé** (`./modules/ui/components/onboarding_modal.py:43`)
  - Accès à st.session_state['onboarding_step'] sans vérification préalable ligne 43.
  - *Correction* : Initialiser avec: if 'onboarding_step' not in st.session_state: st.session_state['onboarding_step'] = default_value

- **Widget sans clé: metric** (`./modules/ui/config/log_viewer.py:44`)
  - Le widget metric ligne 44 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_44'

- **Widget sans clé: text_input** (`./pages/10_Nouveautés.py:44`)
  - Le widget text_input ligne 44 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_44'

- **Session state 'onboarding_step' peut ne pas être initialisé** (`./modules/ui/components/onboarding_modal.py:45`)
  - Accès à st.session_state['onboarding_step'] sans vérification préalable ligne 45.
  - *Correction* : Initialiser avec: if 'onboarding_step' not in st.session_state: st.session_state['onboarding_step'] = default_value

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_compact.py:45`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 45.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: button** (`./modules/ui/config/audit_tools.py:46`)
  - Le widget button ligne 46 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_46'

- **Widget sans clé: checkbox** (`./pages/98_Tests.py:47`)
  - Le widget checkbox ligne 47 n'a pas de clé explicite.
  - *Correction* : Ajouter key='checkbox_47'

- **Widget sans clé: checkbox** (`./pages/98_Tests.py:48`)
  - Le widget checkbox ligne 48 n'a pas de clé explicite.
  - *Correction* : Ajouter key='checkbox_48'

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_compact.py:49`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 49.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: checkbox** (`./pages/98_Tests.py:49`)
  - Le widget checkbox ligne 49 n'a pas de clé explicite.
  - *Correction* : Ajouter key='checkbox_49'

- **Widget sans clé: button** (`./modules/ui/config/notifications.py:50`)
  - Le widget button ligne 50 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_50'

- **Widget sans clé: checkbox** (`./pages/98_Tests.py:50`)
  - Le widget checkbox ligne 50 n'a pas de clé explicite.
  - *Correction* : Ajouter key='checkbox_50'

- **Widget sans clé: multiselect** (`./modules/ui/config/log_viewer.py:51`)
  - Le widget multiselect ligne 51 n'a pas de clé explicite.
  - *Correction* : Ajouter key='multiselect_51'

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_compact.py:51`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 51.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: metric** (`./modules/ui/components/local_ml_manager.py:52`)
  - Le widget metric ligne 52 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_52'

- **Widget sans clé: text_input** (`./pages/98_Tests.py:52`)
  - Le widget text_input ligne 52 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_52'

- **Widget sans clé: metric** (`./modules/ui/components/local_ml_manager.py:58`)
  - Le widget metric ligne 58 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_58'

- **Widget sans clé: text_input** (`./modules/ui/config/log_viewer.py:59`)
  - Le widget text_input ligne 59 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_59'

- **Widget sans clé: toggle** (`./modules/ui/config/notifications.py:60`)
  - Le widget toggle ligne 60 n'a pas de clé explicite.
  - *Correction* : Ajouter key='toggle_60'

- **Widget sans clé: metric** (`./modules/ui/components/local_ml_manager.py:60`)
  - Le widget metric ligne 60 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_60'

- **Widget sans clé: button** (`./modules/ui/config/member_management.py:61`)
  - Le widget button ligne 61 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_61'

- **Widget sans clé: metric** (`./modules/ui/components/transaction_drill_down.py:61`)
  - Le widget metric ligne 61 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_61'

- **Widget sans clé: button** (`./pages/98_Tests.py:61`)
  - Le widget button ligne 61 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_61'

- **Session state 'pending_rename' peut ne pas être initialisé** (`./modules/ui/config/member_management.py:62`)
  - Accès à st.session_state['pending_rename'] sans vérification préalable ligne 62.
  - *Correction* : Initialiser avec: if 'pending_rename' not in st.session_state: st.session_state['pending_rename'] = default_value

- **Session state 'temp_custom_tags' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_compact.py:62`)
  - Accès à st.session_state['temp_custom_tags'] sans vérification préalable ligne 62.
  - *Correction* : Initialiser avec: if 'temp_custom_tags' not in st.session_state: st.session_state['temp_custom_tags'] = default_value

- **Widget sans clé: file_uploader** (`./pages/1_Import.py:62`)
  - Le widget file_uploader ligne 62 n'a pas de clé explicite.
  - *Correction* : Ajouter key='file_uploader_62'

- **Widget sans clé: metric** (`./modules/ui/components/transaction_drill_down.py:63`)
  - Le widget metric ligne 63 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_63'

- **Session state 'config_jump_to' peut ne pas être initialisé** (`./pages/9_Configuration.py:64`)
  - Accès à st.session_state['config_jump_to'] sans vérification préalable ligne 64.
  - *Correction* : Initialiser avec: if 'config_jump_to' not in st.session_state: st.session_state['config_jump_to'] = default_value

- **Widget sans clé: metric** (`./modules/ui/components/transaction_drill_down.py:65`)
  - Le widget metric ligne 65 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_65'

- **Widget sans clé: metric** (`./pages/4_Recurrence.py:67`)
  - Le widget metric ligne 67 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_67'

- **Widget sans clé: text_input** (`./app.py:69`)
  - Le widget text_input ligne 69 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_69'

- **Widget sans clé: metric** (`./pages/4_Recurrence.py:69`)
  - Le widget metric ligne 69 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_69'

- **Widget sans clé: text_input** (`./app.py:70`)
  - Le widget text_input ligne 70 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_70'

- **Widget sans clé: metric** (`./pages/4_Recurrence.py:71`)
  - Le widget metric ligne 71 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_71'

- **Widget sans clé: toggle** (`./modules/ui/config/notifications.py:73`)
  - Le widget toggle ligne 73 n'a pas de clé explicite.
  - *Correction* : Ajouter key='toggle_73'

- **Widget sans clé: button** (`./modules/ui/components/onboarding_modal.py:73`)
  - Le widget button ligne 73 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_73'

- **Widget sans clé: metric** (`./pages/4_Recurrence.py:74`)
  - Le widget metric ligne 74 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_74'

- **Session state 'quick_audit_score' peut ne pas être initialisé** (`./pages/4_Regles.py:75`)
  - Accès à st.session_state['quick_audit_score'] sans vérification préalable ligne 75.
  - *Correction* : Initialiser avec: if 'quick_audit_score' not in st.session_state: st.session_state['quick_audit_score'] = default_value

- **Session state 'editing_member_id' peut ne pas être initialisé** (`./modules/ui/config/member_management.py:76`)
  - Accès à st.session_state['editing_member_id'] sans vérification préalable ligne 76.
  - *Correction* : Initialiser avec: if 'editing_member_id' not in st.session_state: st.session_state['editing_member_id'] = default_value

- **Widget sans clé: button** (`./modules/ui/components/onboarding_modal.py:77`)
  - Le widget button ligne 77 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_77'

- **Session state 'quick_audit_score' peut ne pas être initialisé** (`./pages/4_Regles.py:77`)
  - Accès à st.session_state['quick_audit_score'] sans vérification préalable ligne 77.
  - *Correction* : Initialiser avec: if 'quick_audit_score' not in st.session_state: st.session_state['quick_audit_score'] = default_value

- **Session state 'onboarding_step' peut ne pas être initialisé** (`./modules/ui/components/onboarding_modal.py:78`)
  - Accès à st.session_state['onboarding_step'] sans vérification préalable ligne 78.
  - *Correction* : Initialiser avec: if 'onboarding_step' not in st.session_state: st.session_state['onboarding_step'] = default_value

- **Widget sans clé: button** (`./modules/ui/components/local_ml_manager.py:78`)
  - Le widget button ligne 78 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_78'

- **Session state 'default_account_name' peut ne pas être initialisé** (`./app.py:79`)
  - Accès à st.session_state['default_account_name'] sans vérification préalable ligne 79.
  - *Correction* : Initialiser avec: if 'default_account_name' not in st.session_state: st.session_state['default_account_name'] = default_value

- **Session state 'onboarding_complete' peut ne pas être initialisé** (`./app.py:80`)
  - Accès à st.session_state['onboarding_complete'] sans vérification préalable ligne 80.
  - *Correction* : Initialiser avec: if 'onboarding_complete' not in st.session_state: st.session_state['onboarding_complete'] = default_value

- **Widget sans clé: selectbox** (`./pages/1_Import.py:81`)
  - Le widget selectbox ligne 81 n'a pas de clé explicite.
  - *Correction* : Ajouter key='selectbox_81'

- **Widget sans clé: button** (`./modules/ui/rules/rule_audit.py:82`)
  - Le widget button ligne 82 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_82'

- **Widget sans clé: text_area** (`./pages/10_Nouveautés.py:82`)
  - Le widget text_area ligne 82 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_area_82'

- **Widget sans clé: selectbox** (`./pages/1_Import.py:83`)
  - Le widget selectbox ligne 83 n'a pas de clé explicite.
  - *Correction* : Ajouter key='selectbox_83'

- **Widget sans clé: slider** (`./modules/ui/config/log_viewer.py:85`)
  - Le widget slider ligne 85 n'a pas de clé explicite.
  - *Correction* : Ajouter key='slider_85'

- **Widget sans clé: selectbox** (`./pages/1_Import.py:85`)
  - Le widget selectbox ligne 85 n'a pas de clé explicite.
  - *Correction* : Ajouter key='selectbox_85'

- **Session state 'editing_member_id' peut ne pas être initialisé** (`./modules/ui/config/member_management.py:86`)
  - Accès à st.session_state['editing_member_id'] sans vérification préalable ligne 86.
  - *Correction* : Initialiser avec: if 'editing_member_id' not in st.session_state: st.session_state['editing_member_id'] = default_value

- **Session state 'audit_results' peut ne pas être initialisé** (`./modules/ui/rules/rule_audit.py:86`)
  - Accès à st.session_state['audit_results'] sans vérification préalable ligne 86.
  - *Correction* : Initialiser avec: if 'audit_results' not in st.session_state: st.session_state['audit_results'] = default_value

- **Session state 'audit_last_run' peut ne pas être initialisé** (`./modules/ui/rules/rule_audit.py:87`)
  - Accès à st.session_state['audit_last_run'] sans vérification préalable ligne 87.
  - *Correction* : Initialiser avec: if 'audit_last_run' not in st.session_state: st.session_state['audit_last_run'] = default_value

- **Widget sans clé: selectbox** (`./pages/1_Import.py:87`)
  - Le widget selectbox ligne 87 n'a pas de clé explicite.
  - *Correction* : Ajouter key='selectbox_87'

- **Session state 'quick_audit_score' peut ne pas être initialisé** (`./modules/ui/rules/rule_audit.py:88`)
  - Accès à st.session_state['quick_audit_score'] sans vérification préalable ligne 88.
  - *Correction* : Initialiser avec: if 'quick_audit_score' not in st.session_state: st.session_state['quick_audit_score'] = default_value

- **Widget sans clé: checkbox** (`./pages/10_Nouveautés.py:88`)
  - Le widget checkbox ligne 88 n'a pas de clé explicite.
  - *Correction* : Ajouter key='checkbox_88'

- **Widget sans clé: button** (`./pages/4_Regles.py:88`)
  - Le widget button ligne 88 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_88'

- **Widget sans clé: button** (`./modules/ui/components/local_ml_manager.py:90`)
  - Le widget button ligne 90 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_90'

- **Widget sans clé: selectbox** (`./modules/ui/config/api_settings.py:91`)
  - Le widget selectbox ligne 91 n'a pas de clé explicite.
  - *Correction* : Ajouter key='selectbox_91'

- **Widget sans clé: text_area** (`./pages/10_Nouveautés.py:91`)
  - Le widget text_area ligne 91 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_area_91'

- **Widget sans clé: selectbox** (`./pages/4_Recurrence.py:92`)
  - Le widget selectbox ligne 92 n'a pas de clé explicite.
  - *Correction* : Ajouter key='selectbox_92'

- **Widget sans clé: text_input** (`./modules/ui/components/onboarding_modal.py:94`)
  - Le widget text_input ligne 94 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_94'

- **Widget sans clé: selectbox** (`./modules/ui/components/onboarding_modal.py:95`)
  - Le widget selectbox ligne 95 n'a pas de clé explicite.
  - *Correction* : Ajouter key='selectbox_95'

- **Widget sans clé: text_input** (`./modules/ui/config/notifications.py:96`)
  - Le widget text_input ligne 96 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_96'

- **Widget sans clé: metric** (`./modules/ui/dashboard/sections.py:97`)
  - Le widget metric ligne 97 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_97'

- **Session state 'quick_audit_score' peut ne pas être initialisé** (`./modules/ui/rules/rule_audit.py:97`)
  - Accès à st.session_state['quick_audit_score'] sans vérification préalable ligne 97.
  - *Correction* : Initialiser avec: if 'quick_audit_score' not in st.session_state: st.session_state['quick_audit_score'] = default_value

- **Widget sans clé: selectbox** (`./pages/4_Recurrence.py:98`)
  - Le widget selectbox ligne 98 n'a pas de clé explicite.
  - *Correction* : Ajouter key='selectbox_98'

- **Widget sans clé: metric** (`./modules/ui/dashboard/sections.py:99`)
  - Le widget metric ligne 99 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_99'

- **Session state 'temp_custom_tags' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_compact.py:99`)
  - Accès à st.session_state['temp_custom_tags'] sans vérification préalable ligne 99.
  - *Correction* : Initialiser avec: if 'temp_custom_tags' not in st.session_state: st.session_state['temp_custom_tags'] = default_value

- **Widget sans clé: button** (`./app.py:100`)
  - Le widget button ligne 100 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_100'

- **Widget sans clé: button** (`./modules/ui/feedback.py:100`)
  - Le widget button ligne 100 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_100'

- **Session state 'temp_custom_tags' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_compact.py:100`)
  - Accès à st.session_state['temp_custom_tags'] sans vérification préalable ligne 100.
  - *Correction* : Initialiser avec: if 'temp_custom_tags' not in st.session_state: st.session_state['temp_custom_tags'] = default_value

- **Session state 'audit_last_run' peut ne pas être initialisé** (`./modules/ui/rules/rule_audit.py:100`)
  - Accès à st.session_state['audit_last_run'] sans vérification préalable ligne 100.
  - *Correction* : Initialiser avec: if 'audit_last_run' not in st.session_state: st.session_state['audit_last_run'] = default_value

- **Session state 'onboarding_dismissed' peut ne pas être initialisé** (`./app.py:101`)
  - Accès à st.session_state['onboarding_dismissed'] sans vérification préalable ligne 101.
  - *Correction* : Initialiser avec: if 'onboarding_dismissed' not in st.session_state: st.session_state['onboarding_dismissed'] = default_value

- **Widget sans clé: metric** (`./modules/ui/dashboard/sections.py:101`)
  - Le widget metric ligne 101 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_101'

- **Session state 'onboarding_step' peut ne pas être initialisé** (`./app.py:102`)
  - Accès à st.session_state['onboarding_step'] sans vérification préalable ligne 102.
  - *Correction* : Initialiser avec: if 'onboarding_step' not in st.session_state: st.session_state['onboarding_step'] = default_value

- **Widget sans clé: text_input** (`./modules/ui/config/notifications.py:102`)
  - Le widget text_input ligne 102 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_102'

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_compact.py:102`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 102.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: button** (`./modules/ui/feedback.py:103`)
  - Le widget button ligne 103 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_103'

- **Session state 'pending_rename' peut ne pas être initialisé** (`./modules/ui/config/member_management.py:103`)
  - Accès à st.session_state['pending_rename'] sans vérification préalable ligne 103.
  - *Correction* : Initialiser avec: if 'pending_rename' not in st.session_state: st.session_state['pending_rename'] = default_value

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_compact.py:103`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 103.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: metric** (`./modules/ui/dashboard/sections.py:104`)
  - Le widget metric ligne 104 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_104'

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_compact.py:104`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 104.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: button** (`./modules/ui/components/local_ml_manager.py:104`)
  - Le widget button ligne 104 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_104'

- **Widget sans clé: selectbox** (`./pages/4_Recurrence.py:104`)
  - Le widget selectbox ligne 104 n'a pas de clé explicite.
  - *Correction* : Ajouter key='selectbox_104'

- **Widget sans clé: metric** (`./modules/ui/config/backup_restore.py:106`)
  - Le widget metric ligne 106 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_106'

- **Widget sans clé: button** (`./app.py:107`)
  - Le widget button ligne 107 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_107'

- **Widget sans clé: text_input** (`./modules/ui/config/api_settings.py:107`)
  - Le widget text_input ligne 107 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_107'

- **Widget sans clé: checkbox** (`./modules/ui/rules/rule_validator.py:108`)
  - Le widget checkbox ligne 108 n'a pas de clé explicite.
  - *Correction* : Ajouter key='checkbox_108'

- **Session state 'audit_results' peut ne pas être initialisé** (`./modules/ui/rules/rule_audit.py:108`)
  - Accès à st.session_state['audit_results'] sans vérification préalable ligne 108.
  - *Correction* : Initialiser avec: if 'audit_results' not in st.session_state: st.session_state['audit_results'] = default_value

- **Widget sans clé: number_input** (`./modules/ui/config/notifications.py:109`)
  - Le widget number_input ligne 109 n'a pas de clé explicite.
  - *Correction* : Ajouter key='number_input_109'

- **Widget sans clé: metric** (`./modules/ui/config/backup_restore.py:110`)
  - Le widget metric ligne 110 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_110'

- **Widget sans clé: button** (`./modules/ui/components/quick_actions.py:110`)
  - Le widget button ligne 110 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_110'

- **Widget sans clé: selectbox** (`./pages/2_Validation.py:111`)
  - Le widget selectbox ligne 111 n'a pas de clé explicite.
  - *Correction* : Ajouter key='selectbox_111'

- **Widget sans clé: text_input** (`./modules/ui/config/tags_rules.py:112`)
  - Le widget text_input ligne 112 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_112'

- **Widget sans clé: metric** (`./modules/ui/config/backup_restore.py:113`)
  - Le widget metric ligne 113 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_113'

- **Session state 'editing_member_id' peut ne pas être initialisé** (`./modules/ui/config/member_management.py:113`)
  - Accès à st.session_state['editing_member_id'] sans vérification préalable ligne 113.
  - *Correction* : Initialiser avec: if 'editing_member_id' not in st.session_state: st.session_state['editing_member_id'] = default_value

- **Widget sans clé: button** (`./modules/ui/config/log_viewer.py:115`)
  - Le widget button ligne 115 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_115'

- **Widget sans clé: text_input** (`./modules/ui/config/notifications.py:116`)
  - Le widget text_input ligne 116 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_116'

- **Session state 'audit_corrected' peut ne pas être initialisé** (`./pages/5_Assistant.py:116`)
  - Accès à st.session_state['audit_corrected'] sans vérification préalable ligne 116.
  - *Correction* : Initialiser avec: if 'audit_corrected' not in st.session_state: st.session_state['audit_corrected'] = default_value

- **Widget sans clé: text_input** (`./modules/ui/config/api_settings.py:117`)
  - Le widget text_input ligne 117 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_117'

- **Session state 'onboarding_step' peut ne pas être initialisé** (`./modules/ui/components/onboarding_modal.py:117`)
  - Accès à st.session_state['onboarding_step'] sans vérification préalable ligne 117.
  - *Correction* : Initialiser avec: if 'onboarding_step' not in st.session_state: st.session_state['onboarding_step'] = default_value

- **Session state 'last_test_result' peut ne pas être initialisé** (`./pages/98_Tests.py:117`)
  - Accès à st.session_state['last_test_result'] sans vérification préalable ligne 117.
  - *Correction* : Initialiser avec: if 'last_test_result' not in st.session_state: st.session_state['last_test_result'] = default_value

- **Session state 'audit_hidden' peut ne pas être initialisé** (`./pages/5_Assistant.py:118`)
  - Accès à st.session_state['audit_hidden'] sans vérification préalable ligne 118.
  - *Correction* : Initialiser avec: if 'audit_hidden' not in st.session_state: st.session_state['audit_hidden'] = default_value

- **Widget sans clé: button** (`./modules/ui/config/log_viewer.py:119`)
  - Le widget button ligne 119 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_119'

- **Widget sans clé: button** (`./modules/ui/config/backup_restore.py:119`)
  - Le widget button ligne 119 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_119'

- **Widget sans clé: text_input** (`./modules/ui/components/local_ml_manager.py:119`)
  - Le widget text_input ligne 119 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_119'

- **Widget sans clé: metric** (`./modules/ui/dashboard/sections.py:120`)
  - Le widget metric ligne 120 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_120'

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_compact.py:120`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 120.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_compact.py:121`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 121.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: metric** (`./modules/ui/dashboard/sections.py:122`)
  - Le widget metric ligne 122 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_122'

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_compact.py:122`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 122.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: button** (`./modules/ui/components/onboarding_modal.py:123`)
  - Le widget button ligne 123 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_123'

- **Widget sans clé: button** (`./pages/5_Assistant.py:123`)
  - Le widget button ligne 123 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_123'

- **Widget sans clé: button** (`./pages/2_Validation.py:123`)
  - Le widget button ligne 123 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_123'

- **Widget sans clé: text_input** (`./modules/ui/config/notifications.py:124`)
  - Le widget text_input ligne 124 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_124'

- **Session state 'editing_member_id' peut ne pas être initialisé** (`./modules/ui/config/member_management.py:124`)
  - Accès à st.session_state['editing_member_id'] sans vérification préalable ligne 124.
  - *Correction* : Initialiser avec: if 'editing_member_id' not in st.session_state: st.session_state['editing_member_id'] = default_value

- **Widget sans clé: metric** (`./modules/ui/dashboard/sections.py:124`)
  - Le widget metric ligne 124 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_124'

- **Session state 'onboarding_step' peut ne pas être initialisé** (`./modules/ui/components/onboarding_modal.py:124`)
  - Accès à st.session_state['onboarding_step'] sans vérification préalable ligne 124.
  - *Correction* : Initialiser avec: if 'onboarding_step' not in st.session_state: st.session_state['onboarding_step'] = default_value

- **Widget sans clé: text_input** (`./modules/ui/config/api_settings.py:126`)
  - Le widget text_input ligne 126 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_126'

- **Widget sans clé: button** (`./modules/ui/components/onboarding_modal.py:127`)
  - Le widget button ligne 127 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_127'

- **Session state 'confirm_delete_month' peut ne pas être initialisé** (`./modules/ui/config/data_operations.py:128`)
  - Accès à st.session_state['confirm_delete_month'] sans vérification préalable ligne 128.
  - *Correction* : Initialiser avec: if 'confirm_delete_month' not in st.session_state: st.session_state['confirm_delete_month'] = default_value

- **Session state 'onboarding_step' peut ne pas être initialisé** (`./modules/ui/components/onboarding_modal.py:128`)
  - Accès à st.session_state['onboarding_step'] sans vérification préalable ligne 128.
  - *Correction* : Initialiser avec: if 'onboarding_step' not in st.session_state: st.session_state['onboarding_step'] = default_value

- **Session state 'confirm_delete_month' peut ne pas être initialisé** (`./modules/ui/config/data_operations.py:130`)
  - Accès à st.session_state['confirm_delete_month'] sans vérification préalable ligne 130.
  - *Correction* : Initialiser avec: if 'confirm_delete_month' not in st.session_state: st.session_state['confirm_delete_month'] = default_value

- **Widget sans clé: button** (`./app.py:131`)
  - Le widget button ligne 131 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_131'

- **Session state 'confirm_delete_month' peut ne pas être initialisé** (`./modules/ui/config/data_operations.py:131`)
  - Accès à st.session_state['confirm_delete_month'] sans vérification préalable ligne 131.
  - *Correction* : Initialiser avec: if 'confirm_delete_month' not in st.session_state: st.session_state['confirm_delete_month'] = default_value

- **Widget sans clé: text_input** (`./modules/ui/components/quick_actions.py:132`)
  - Le widget text_input ligne 132 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_132'

- **Widget sans clé: button** (`./app.py:133`)
  - Le widget button ligne 133 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_133'

- **Widget sans clé: radio** (`./modules/ui/components/quick_actions.py:133`)
  - Le widget radio ligne 133 n'a pas de clé explicite.
  - *Correction* : Ajouter key='radio_133'

- **Session state 'audit_results' peut ne pas être initialisé** (`./pages/5_Assistant.py:133`)
  - Accès à st.session_state['audit_results'] sans vérification préalable ligne 133.
  - *Correction* : Initialiser avec: if 'audit_results' not in st.session_state: st.session_state['audit_results'] = default_value

- **Session state 'audit_corrected' peut ne pas être initialisé** (`./pages/5_Assistant.py:134`)
  - Accès à st.session_state['audit_corrected'] sans vérification préalable ligne 134.
  - *Correction* : Initialiser avec: if 'audit_corrected' not in st.session_state: st.session_state['audit_corrected'] = default_value

- **Widget sans clé: text_input** (`./modules/ui/config/api_settings.py:136`)
  - Le widget text_input ligne 136 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_136'

- **Session state 'editing_member_id' peut ne pas être initialisé** (`./modules/ui/config/member_management.py:137`)
  - Accès à st.session_state['editing_member_id'] sans vérification préalable ligne 137.
  - *Correction* : Initialiser avec: if 'editing_member_id' not in st.session_state: st.session_state['editing_member_id'] = default_value

- **Widget sans clé: button** (`./modules/ui/dashboard/ai_insights.py:138`)
  - Le widget button ligne 138 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_138'

- **Widget sans clé: button** (`./pages/98_Tests.py:139`)
  - Le widget button ligne 139 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_139'

- **Session state 'audit_results' peut ne pas être initialisé** (`./pages/5_Assistant.py:139`)
  - Accès à st.session_state['audit_results'] sans vérification préalable ligne 139.
  - *Correction* : Initialiser avec: if 'audit_results' not in st.session_state: st.session_state['audit_results'] = default_value

- **Widget sans clé: button** (`./modules/ui/config/backup_restore.py:140`)
  - Le widget button ligne 140 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_140'

- **Widget sans clé: slider** (`./modules/ui/config/notifications.py:144`)
  - Le widget slider ligne 144 n'a pas de clé explicite.
  - *Correction* : Ajouter key='slider_144'

- **Session state 'audit_results' peut ne pas être initialisé** (`./pages/5_Assistant.py:144`)
  - Accès à st.session_state['audit_results'] sans vérification préalable ligne 144.
  - *Correction* : Initialiser avec: if 'audit_results' not in st.session_state: st.session_state['audit_results'] = default_value

- **Widget sans clé: text_input** (`./modules/ui/config/api_settings.py:146`)
  - Le widget text_input ligne 146 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_146'

- **Widget sans clé: multiselect** (`./modules/ui/components/onboarding_modal.py:147`)
  - Le widget multiselect ligne 147 n'a pas de clé explicite.
  - *Correction* : Ajouter key='multiselect_147'

- **Widget sans clé: button** (`./pages/5_Assistant.py:150`)
  - Le widget button ligne 150 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_150'

- **Widget sans clé: button** (`./app.py:151`)
  - Le widget button ligne 151 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_151'

- **Session state 'audit_bulk_selection' peut ne pas être initialisé** (`./pages/5_Assistant.py:151`)
  - Accès à st.session_state['audit_bulk_selection'] sans vérification préalable ligne 151.
  - *Correction* : Initialiser avec: if 'audit_bulk_selection' not in st.session_state: st.session_state['audit_bulk_selection'] = default_value

- **Session state 'audit_results' peut ne pas être initialisé** (`./pages/5_Assistant.py:151`)
  - Accès à st.session_state['audit_results'] sans vérification préalable ligne 151.
  - *Correction* : Initialiser avec: if 'audit_results' not in st.session_state: st.session_state['audit_results'] = default_value

- **Session state 'onboarding_dismissed' peut ne pas être initialisé** (`./app.py:152`)
  - Accès à st.session_state['onboarding_dismissed'] sans vérification préalable ligne 152.
  - *Correction* : Initialiser avec: if 'onboarding_dismissed' not in st.session_state: st.session_state['onboarding_dismissed'] = default_value

- **Session state 'onboarding_step' peut ne pas être initialisé** (`./app.py:153`)
  - Accès à st.session_state['onboarding_step'] sans vérification préalable ligne 153.
  - *Correction* : Initialiser avec: if 'onboarding_step' not in st.session_state: st.session_state['onboarding_step'] = default_value

- **Widget sans clé: slider** (`./modules/ui/config/notifications.py:155`)
  - Le widget slider ligne 155 n'a pas de clé explicite.
  - *Correction* : Ajouter key='slider_155'

- **Session state 'confirm_delete_month' peut ne pas être initialisé** (`./modules/ui/config/data_operations.py:155`)
  - Accès à st.session_state['confirm_delete_month'] sans vérification préalable ligne 155.
  - *Correction* : Initialiser avec: if 'confirm_delete_month' not in st.session_state: st.session_state['confirm_delete_month'] = default_value

- **Widget sans clé: text_input** (`./modules/ui/components/quick_actions.py:155`)
  - Le widget text_input ligne 155 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_155'

- **Widget sans clé: button** (`./pages/5_Assistant.py:155`)
  - Le widget button ligne 155 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_155'

- **Session state 'audit_bulk_selection' peut ne pas être initialisé** (`./pages/5_Assistant.py:156`)
  - Accès à st.session_state['audit_bulk_selection'] sans vérification préalable ligne 156.
  - *Correction* : Initialiser avec: if 'audit_bulk_selection' not in st.session_state: st.session_state['audit_bulk_selection'] = default_value

- **Widget sans clé: text_input** (`./modules/ui/components/quick_actions.py:157`)
  - Le widget text_input ligne 157 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_157'

- **Widget sans clé: button** (`./modules/ui/config/config_dashboard.py:159`)
  - Le widget button ligne 159 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_159'

- **Widget sans clé: checkbox** (`./modules/ui/components/quick_actions.py:159`)
  - Le widget checkbox ligne 159 n'a pas de clé explicite.
  - *Correction* : Ajouter key='checkbox_159'

- **Session state 'last_test_result' peut ne pas être initialisé** (`./pages/98_Tests.py:159`)
  - Accès à st.session_state['last_test_result'] sans vérification préalable ligne 159.
  - *Correction* : Initialiser avec: if 'last_test_result' not in st.session_state: st.session_state['last_test_result'] = default_value

- **Session state 'config_jump_to' peut ne pas être initialisé** (`./modules/ui/config/config_dashboard.py:160`)
  - Accès à st.session_state['config_jump_to'] sans vérification préalable ligne 160.
  - *Correction* : Initialiser avec: if 'config_jump_to' not in st.session_state: st.session_state['config_jump_to'] = default_value

- **Session state 'confirm_delete_month' peut ne pas être initialisé** (`./modules/ui/config/data_operations.py:160`)
  - Accès à st.session_state['confirm_delete_month'] sans vérification préalable ligne 160.
  - *Correction* : Initialiser avec: if 'confirm_delete_month' not in st.session_state: st.session_state['confirm_delete_month'] = default_value

- **Widget sans clé: button** (`./pages/5_Assistant.py:160`)
  - Le widget button ligne 160 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_160'

- **Session state 'last_selected_month' peut ne pas être initialisé** (`./modules/ui/config/data_operations.py:161`)
  - Accès à st.session_state['last_selected_month'] sans vérification préalable ligne 161.
  - *Correction* : Initialiser avec: if 'last_selected_month' not in st.session_state: st.session_state['last_selected_month'] = default_value

- **Session state 'audit_hidden' peut ne pas être initialisé** (`./pages/5_Assistant.py:163`)
  - Accès à st.session_state['audit_hidden'] sans vérification préalable ligne 163.
  - *Correction* : Initialiser avec: if 'audit_hidden' not in st.session_state: st.session_state['audit_hidden'] = default_value

- **Widget sans clé: radio** (`./pages/1_Import.py:163`)
  - Le widget radio ligne 163 n'a pas de clé explicite.
  - *Correction* : Ajouter key='radio_163'

- **Widget sans clé: button** (`./modules/ui/config/config_dashboard.py:164`)
  - Le widget button ligne 164 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_164'

- **DataFrame sans contraintes d'affichage** (`./modules/ui/components/local_ml_manager.py:164`)
  - st.dataframe() ligne 164 sans pagination ou hauteur définie.
  - *Correction* : Ajouter height=400 et use_container_width=True, ou paginer les données

- **Session state 'audit_hidden' peut ne pas être initialisé** (`./pages/5_Assistant.py:164`)
  - Accès à st.session_state['audit_hidden'] sans vérification préalable ligne 164.
  - *Correction* : Initialiser avec: if 'audit_hidden' not in st.session_state: st.session_state['audit_hidden'] = default_value

- **Session state 'config_jump_to' peut ne pas être initialisé** (`./modules/ui/config/config_dashboard.py:165`)
  - Accès à st.session_state['config_jump_to'] sans vérification préalable ligne 165.
  - *Correction* : Initialiser avec: if 'config_jump_to' not in st.session_state: st.session_state['config_jump_to'] = default_value

- **Session state 'audit_bulk_selection' peut ne pas être initialisé** (`./pages/5_Assistant.py:165`)
  - Accès à st.session_state['audit_bulk_selection'] sans vérification préalable ligne 165.
  - *Correction* : Initialiser avec: if 'audit_bulk_selection' not in st.session_state: st.session_state['audit_bulk_selection'] = default_value

- **Widget sans clé: slider** (`./modules/ui/config/notifications.py:166`)
  - Le widget slider ligne 166 n'a pas de clé explicite.
  - *Correction* : Ajouter key='slider_166'

- **Widget sans clé: metric** (`./pages/98_Tests.py:166`)
  - Le widget metric ligne 166 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_166'

- **Widget sans clé: selectbox** (`./pages/1_Import.py:166`)
  - Le widget selectbox ligne 166 n'a pas de clé explicite.
  - *Correction* : Ajouter key='selectbox_166'

- **Session state 'temp_custom_tags' peut ne pas être initialisé** (`./pages/2_Validation.py:166`)
  - Accès à st.session_state['temp_custom_tags'] sans vérification préalable ligne 166.
  - *Correction* : Initialiser avec: if 'temp_custom_tags' not in st.session_state: st.session_state['temp_custom_tags'] = default_value

- **Widget sans clé: button** (`./pages/3_Synthese.py:166`)
  - Le widget button ligne 166 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_166'

- **Widget sans clé: text_input** (`./modules/ui/components/onboarding_modal.py:167`)
  - Le widget text_input ligne 167 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_167'

- **Session state 'editing_member_id' peut ne pas être initialisé** (`./modules/ui/config/member_management.py:168`)
  - Accès à st.session_state['editing_member_id'] sans vérification préalable ligne 168.
  - *Correction* : Initialiser avec: if 'editing_member_id' not in st.session_state: st.session_state['editing_member_id'] = default_value

- **Widget sans clé: text_input** (`./modules/ui/config/data_operations.py:168`)
  - Le widget text_input ligne 168 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_168'

- **Widget sans clé: button** (`./modules/ui/config/config_dashboard.py:169`)
  - Le widget button ligne 169 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_169'

- **Widget sans clé: metric** (`./pages/98_Tests.py:169`)
  - Le widget metric ligne 169 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_169'

- **Widget sans clé: button** (`./pages/5_Assistant.py:169`)
  - Le widget button ligne 169 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_169'

- **Widget sans clé: text_input** (`./pages/1_Import.py:169`)
  - Le widget text_input ligne 169 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_169'

- **Session state 'config_jump_to' peut ne pas être initialisé** (`./modules/ui/config/config_dashboard.py:170`)
  - Accès à st.session_state['config_jump_to'] sans vérification préalable ligne 170.
  - *Correction* : Initialiser avec: if 'config_jump_to' not in st.session_state: st.session_state['config_jump_to'] = default_value

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./pages/2_Validation.py:170`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 170.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: button** (`./modules/ui/components/onboarding_modal.py:171`)
  - Le widget button ligne 171 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_171'

- **Widget sans clé: metric** (`./pages/98_Tests.py:172`)
  - Le widget metric ligne 172 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_172'

- **Widget sans clé: button** (`./modules/ui/config/config_dashboard.py:174`)
  - Le widget button ligne 174 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_174'

- **Widget sans clé: metric** (`./modules/ui/rules/budget_manager.py:174`)
  - Le widget metric ligne 174 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_174'

- **Session state 'audit_results' peut ne pas être initialisé** (`./pages/5_Assistant.py:174`)
  - Accès à st.session_state['audit_results'] sans vérification préalable ligne 174.
  - *Correction* : Initialiser avec: if 'audit_results' not in st.session_state: st.session_state['audit_results'] = default_value

- **Session state 'bulk_selected_groups' peut ne pas être initialisé** (`./pages/2_Validation.py:174`)
  - Accès à st.session_state['bulk_selected_groups'] sans vérification préalable ligne 174.
  - *Correction* : Initialiser avec: if 'bulk_selected_groups' not in st.session_state: st.session_state['bulk_selected_groups'] = default_value

- **Session state 'config_jump_to' peut ne pas être initialisé** (`./modules/ui/config/config_dashboard.py:175`)
  - Accès à st.session_state['config_jump_to'] sans vérification préalable ligne 175.
  - *Correction* : Initialiser avec: if 'config_jump_to' not in st.session_state: st.session_state['config_jump_to'] = default_value

- **Session state 'audit_results' peut ne pas être initialisé** (`./pages/5_Assistant.py:175`)
  - Accès à st.session_state['audit_results'] sans vérification préalable ligne 175.
  - *Correction* : Initialiser avec: if 'audit_results' not in st.session_state: st.session_state['audit_results'] = default_value

- **Widget sans clé: metric** (`./modules/ui/rules/budget_manager.py:176`)
  - Le widget metric ligne 176 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_176'

- **Widget sans clé: text_input** (`./modules/ui/components/quick_actions.py:177`)
  - Le widget text_input ligne 177 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_177'

- **Session state 'bulk_selected_groups' peut ne pas être initialisé** (`./pages/2_Validation.py:177`)
  - Accès à st.session_state['bulk_selected_groups'] sans vérification préalable ligne 177.
  - *Correction* : Initialiser avec: if 'bulk_selected_groups' not in st.session_state: st.session_state['bulk_selected_groups'] = default_value

- **Widget sans clé: selectbox** (`./pages/1_Import.py:178`)
  - Le widget selectbox ligne 178 n'a pas de clé explicite.
  - *Correction* : Ajouter key='selectbox_178'

- **Session state 'bulk_selected_groups' peut ne pas être initialisé** (`./pages/2_Validation.py:178`)
  - Accès à st.session_state['bulk_selected_groups'] sans vérification préalable ligne 178.
  - *Correction* : Initialiser avec: if 'bulk_selected_groups' not in st.session_state: st.session_state['bulk_selected_groups'] = default_value

- **Widget sans clé: metric** (`./modules/ui/rules/budget_manager.py:179`)
  - Le widget metric ligne 179 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_179'

- **Widget sans clé: selectbox** (`./modules/ui/components/quick_actions.py:181`)
  - Le widget selectbox ligne 181 n'a pas de clé explicite.
  - *Correction* : Ajouter key='selectbox_181'

- **Widget sans clé: button** (`./modules/ui/config/notifications.py:182`)
  - Le widget button ligne 182 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_182'

- **Widget sans clé: metric** (`./modules/ui/rules/budget_manager.py:182`)
  - Le widget metric ligne 182 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_182'

- **Widget sans clé: selectbox** (`./pages/1_Import.py:182`)
  - Le widget selectbox ligne 182 n'a pas de clé explicite.
  - *Correction* : Ajouter key='selectbox_182'

- **Session state 'editing_member_id' peut ne pas être initialisé** (`./modules/ui/config/member_management.py:184`)
  - Accès à st.session_state['editing_member_id'] sans vérification préalable ligne 184.
  - *Correction* : Initialiser avec: if 'editing_member_id' not in st.session_state: st.session_state['editing_member_id'] = default_value

- **Session state 'audit_results' peut ne pas être initialisé** (`./pages/5_Assistant.py:186`)
  - Accès à st.session_state['audit_results'] sans vérification préalable ligne 186.
  - *Correction* : Initialiser avec: if 'audit_results' not in st.session_state: st.session_state['audit_results'] = default_value

- **Session state 'bulk_selected_groups' peut ne pas être initialisé** (`./pages/2_Validation.py:186`)
  - Accès à st.session_state['bulk_selected_groups'] sans vérification préalable ligne 186.
  - *Correction* : Initialiser avec: if 'bulk_selected_groups' not in st.session_state: st.session_state['bulk_selected_groups'] = default_value

- **Widget sans clé: button** (`./modules/ui/config/category_management.py:187`)
  - Le widget button ligne 187 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_187'

- **Widget sans clé: metric** (`./modules/ui/config/config_dashboard.py:188`)
  - Le widget metric ligne 188 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_188'

- **Widget sans clé: button** (`./modules/ui/config/notifications.py:189`)
  - Le widget button ligne 189 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_189'

- **Session state 'ml_mode_preference' peut ne pas être initialisé** (`./modules/ui/components/local_ml_manager.py:190`)
  - Accès à st.session_state['ml_mode_preference'] sans vérification préalable ligne 190.
  - *Correction* : Initialiser avec: if 'ml_mode_preference' not in st.session_state: st.session_state['ml_mode_preference'] = default_value

- **Widget sans clé: selectbox** (`./pages/9_Configuration.py:191`)
  - Le widget selectbox ligne 191 n'a pas de clé explicite.
  - *Correction* : Ajouter key='selectbox_191'

- **Widget sans clé: number_input** (`./pages/9_Configuration.py:192`)
  - Le widget number_input ligne 192 n'a pas de clé explicite.
  - *Correction* : Ajouter key='number_input_192'

- **Widget sans clé: button** (`./modules/ui/components/onboarding_modal.py:193`)
  - Le widget button ligne 193 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_193'

- **Widget sans clé: button** (`./modules/ui/config/backup_restore.py:194`)
  - Le widget button ligne 194 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_194'

- **Session state 'onboarding_step' peut ne pas être initialisé** (`./modules/ui/components/onboarding_modal.py:194`)
  - Accès à st.session_state['onboarding_step'] sans vérification préalable ligne 194.
  - *Correction* : Initialiser avec: if 'onboarding_step' not in st.session_state: st.session_state['onboarding_step'] = default_value

- **Session state 'editing_member_id' peut ne pas être initialisé** (`./modules/ui/config/member_management.py:195`)
  - Accès à st.session_state['editing_member_id'] sans vérification préalable ligne 195.
  - *Correction* : Initialiser avec: if 'editing_member_id' not in st.session_state: st.session_state['editing_member_id'] = default_value

- **st.write() dans une boucle** (`./modules/ui/config/config_dashboard.py:196`)
  - st.write() dans une boucle ligne 196. Peut ralentir l'affichage.
  - *Correction* : Collecter les données dans une liste et afficher avec st.table() ou st.dataframe()

- **Widget sans clé: text_area** (`./pages/98_Tests.py:196`)
  - Le widget text_area ligne 196 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_area_196'

- **Session state 'bulk_selected_groups' peut ne pas être initialisé** (`./pages/2_Validation.py:198`)
  - Accès à st.session_state['bulk_selected_groups'] sans vérification préalable ligne 198.
  - *Correction* : Initialiser avec: if 'bulk_selected_groups' not in st.session_state: st.session_state['bulk_selected_groups'] = default_value

- **Widget sans clé: metric** (`./modules/ui/rules/budget_manager.py:199`)
  - Le widget metric ligne 199 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_199'

- **Widget sans clé: button** (`./modules/ui/components/onboarding_modal.py:200`)
  - Le widget button ligne 200 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_200'

- **Widget sans clé: metric** (`./modules/ui/rules/budget_manager.py:200`)
  - Le widget metric ligne 200 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_200'

- **Session state 'onboarding_step' peut ne pas être initialisé** (`./modules/ui/components/onboarding_modal.py:201`)
  - Accès à st.session_state['onboarding_step'] sans vérification préalable ligne 201.
  - *Correction* : Initialiser avec: if 'onboarding_step' not in st.session_state: st.session_state['onboarding_step'] = default_value

- **Session state 'bulk_selected_groups' peut ne pas être initialisé** (`./pages/2_Validation.py:202`)
  - Accès à st.session_state['bulk_selected_groups'] sans vérification préalable ligne 202.
  - *Correction* : Initialiser avec: if 'bulk_selected_groups' not in st.session_state: st.session_state['bulk_selected_groups'] = default_value

- **Widget sans clé: button** (`./modules/ui/components/onboarding_modal.py:204`)
  - Le widget button ligne 204 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_204'

- **Session state 'onboarding_step' peut ne pas être initialisé** (`./modules/ui/components/onboarding_modal.py:205`)
  - Accès à st.session_state['onboarding_step'] sans vérification préalable ligne 205.
  - *Correction* : Initialiser avec: if 'onboarding_step' not in st.session_state: st.session_state['onboarding_step'] = default_value

- **Session state 'audit_bulk_selection' peut ne pas être initialisé** (`./pages/5_Assistant.py:207`)
  - Accès à st.session_state['audit_bulk_selection'] sans vérification préalable ligne 207.
  - *Correction* : Initialiser avec: if 'audit_bulk_selection' not in st.session_state: st.session_state['audit_bulk_selection'] = default_value

- **Session state 'editing_member_id' peut ne pas être initialisé** (`./modules/ui/config/member_management.py:208`)
  - Accès à st.session_state['editing_member_id'] sans vérification préalable ligne 208.
  - *Correction* : Initialiser avec: if 'editing_member_id' not in st.session_state: st.session_state['editing_member_id'] = default_value

- **Session state 'excluded_tx_ids' peut ne pas être initialisé** (`./pages/2_Validation.py:209`)
  - Accès à st.session_state['excluded_tx_ids'] sans vérification préalable ligne 209.
  - *Correction* : Initialiser avec: if 'excluded_tx_ids' not in st.session_state: st.session_state['excluded_tx_ids'] = default_value

- **Session state 'temp_custom_tags' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_smart.py:211`)
  - Accès à st.session_state['temp_custom_tags'] sans vérification préalable ligne 211.
  - *Correction* : Initialiser avec: if 'temp_custom_tags' not in st.session_state: st.session_state['temp_custom_tags'] = default_value

- **Widget sans clé: file_uploader** (`./modules/ui/components/quick_actions.py:212`)
  - Le widget file_uploader ligne 212 n'a pas de clé explicite.
  - *Correction* : Ajouter key='file_uploader_212'

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_smart.py:214`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 214.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: button** (`./modules/ui/config/data_operations.py:215`)
  - Le widget button ligne 215 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_215'

- **Session state 'propagation_shown' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_smart.py:217`)
  - Accès à st.session_state['propagation_shown'] sans vérification préalable ligne 217.
  - *Correction* : Initialiser avec: if 'propagation_shown' not in st.session_state: st.session_state['propagation_shown'] = default_value

- **Widget sans clé: button** (`./modules/ui/config/notifications.py:218`)
  - Le widget button ligne 218 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_218'

- **Widget sans clé: metric** (`./pages/98_Tests.py:220`)
  - Le widget metric ligne 220 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_220'

- **Widget sans clé: text_input** (`./modules/ui/rules/rule_manager.py:222`)
  - Le widget text_input ligne 222 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_222'

- **Widget sans clé: selectbox** (`./modules/ui/components/quick_actions.py:224`)
  - Le widget selectbox ligne 224 n'a pas de clé explicite.
  - *Correction* : Ajouter key='selectbox_224'

- **Widget sans clé: metric** (`./pages/98_Tests.py:224`)
  - Le widget metric ligne 224 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_224'

- **Widget sans clé: text_input** (`./modules/ui/components/quick_actions.py:226`)
  - Le widget text_input ligne 226 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_226'

- **st.write() dans une boucle** (`./modules/ui/config/notifications.py:228`)
  - st.write() dans une boucle ligne 228. Peut ralentir l'affichage.
  - *Correction* : Collecter les données dans une liste et afficher avec st.table() ou st.dataframe()

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_smart.py:228`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 228.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: metric** (`./pages/98_Tests.py:228`)
  - Le widget metric ligne 228 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_228'

- **Widget sans clé: selectbox** (`./modules/ui/rules/rule_manager.py:229`)
  - Le widget selectbox ligne 229 n'a pas de clé explicite.
  - *Correction* : Ajouter key='selectbox_229'

- **Session state 'audit_bulk_selection' peut ne pas être initialisé** (`./pages/5_Assistant.py:229`)
  - Accès à st.session_state['audit_bulk_selection'] sans vérification préalable ligne 229.
  - *Correction* : Initialiser avec: if 'audit_bulk_selection' not in st.session_state: st.session_state['audit_bulk_selection'] = default_value

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_smart.py:230`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 230.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: text_input** (`./modules/ui/config/member_management.py:232`)
  - Le widget text_input ligne 232 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_232'

- **Session state 'audit_bulk_selection' peut ne pas être initialisé** (`./pages/5_Assistant.py:233`)
  - Accès à st.session_state['audit_bulk_selection'] sans vérification préalable ligne 233.
  - *Correction* : Initialiser avec: if 'audit_bulk_selection' not in st.session_state: st.session_state['audit_bulk_selection'] = default_value

- **Session state 'audit_bulk_selection' peut ne pas être initialisé** (`./pages/5_Assistant.py:234`)
  - Accès à st.session_state['audit_bulk_selection'] sans vérification préalable ligne 234.
  - *Correction* : Initialiser avec: if 'audit_bulk_selection' not in st.session_state: st.session_state['audit_bulk_selection'] = default_value

- **Session state 'audit_bulk_selection' peut ne pas être initialisé** (`./pages/5_Assistant.py:235`)
  - Accès à st.session_state['audit_bulk_selection'] sans vérification préalable ligne 235.
  - *Correction* : Initialiser avec: if 'audit_bulk_selection' not in st.session_state: st.session_state['audit_bulk_selection'] = default_value

- **Session state 'audit_bulk_selection' peut ne pas être initialisé** (`./pages/5_Assistant.py:236`)
  - Accès à st.session_state['audit_bulk_selection'] sans vérification préalable ligne 236.
  - *Correction* : Initialiser avec: if 'audit_bulk_selection' not in st.session_state: st.session_state['audit_bulk_selection'] = default_value

- **Widget sans clé: radio** (`./modules/ui/config/member_management.py:237`)
  - Le widget radio ligne 237 n'a pas de clé explicite.
  - *Correction* : Ajouter key='radio_237'

- **Session state 'temp_custom_tags' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_smart.py:241`)
  - Accès à st.session_state['temp_custom_tags'] sans vérification préalable ligne 241.
  - *Correction* : Initialiser avec: if 'temp_custom_tags' not in st.session_state: st.session_state['temp_custom_tags'] = default_value

- **Session state 'quick_audit_score' peut ne pas être initialisé** (`./modules/ui/rules/rule_audit.py:244`)
  - Accès à st.session_state['quick_audit_score'] sans vérification préalable ligne 244.
  - *Correction* : Initialiser avec: if 'quick_audit_score' not in st.session_state: st.session_state['quick_audit_score'] = default_value

- **Session state 'notif_preview' peut ne pas être initialisé** (`./modules/ui/config/notifications.py:256`)
  - Accès à st.session_state['notif_preview'] sans vérification préalable ligne 256.
  - *Correction* : Initialiser avec: if 'notif_preview' not in st.session_state: st.session_state['notif_preview'] = default_value

- **Session state 'temp_custom_tags' peut ne pas être initialisé** (`./modules/ui/components/tag_manager.py:256`)
  - Accès à st.session_state['temp_custom_tags'] sans vérification préalable ligne 256.
  - *Correction* : Initialiser avec: if 'temp_custom_tags' not in st.session_state: st.session_state['temp_custom_tags'] = default_value

- **DataFrame sans contraintes d'affichage** (`./pages/1_Import.py:256`)
  - st.dataframe() ligne 256 sans pagination ou hauteur définie.
  - *Correction* : Ajouter height=400 et use_container_width=True, ou paginer les données

- **Widget sans clé: metric** (`./modules/impact_analyzer.py:258`)
  - Le widget metric ligne 258 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_258'

- **Session state 'propagation_shown' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_smart.py:258`)
  - Accès à st.session_state['propagation_shown'] sans vérification préalable ligne 258.
  - *Correction* : Initialiser avec: if 'propagation_shown' not in st.session_state: st.session_state['propagation_shown'] = default_value

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_manager.py:259`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 259.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: metric** (`./modules/impact_analyzer.py:260`)
  - Le widget metric ligne 260 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_260'

- **Widget sans clé: multiselect** (`./pages/4_Recurrence.py:260`)
  - Le widget multiselect ligne 260 n'a pas de clé explicite.
  - *Correction* : Ajouter key='multiselect_260'

- **Widget sans clé: button** (`./modules/ui/components/onboarding_modal.py:261`)
  - Le widget button ligne 261 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_261'

- **Widget sans clé: button** (`./modules/ui/components/quick_actions.py:261`)
  - Le widget button ligne 261 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_261'

- **Session state 'audit_corrected' peut ne pas être initialisé** (`./pages/5_Assistant.py:262`)
  - Accès à st.session_state['audit_corrected'] sans vérification préalable ligne 262.
  - *Correction* : Initialiser avec: if 'audit_corrected' not in st.session_state: st.session_state['audit_corrected'] = default_value

- **Widget sans clé: metric** (`./modules/impact_analyzer.py:263`)
  - Le widget metric ligne 263 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_263'

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_manager.py:263`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 263.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: checkbox** (`./pages/1_Import.py:263`)
  - Le widget checkbox ligne 263 n'a pas de clé explicite.
  - *Correction* : Ajouter key='checkbox_263'

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_manager.py:265`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 265.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: button** (`./modules/ui/components/onboarding_modal.py:266`)
  - Le widget button ligne 266 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_266'

- **Session state 'onboarding_step' peut ne pas être initialisé** (`./modules/ui/components/onboarding_modal.py:267`)
  - Accès à st.session_state['onboarding_step'] sans vérification préalable ligne 267.
  - *Correction* : Initialiser avec: if 'onboarding_step' not in st.session_state: st.session_state['onboarding_step'] = default_value

- **Session state 'audit_corrected' peut ne pas être initialisé** (`./pages/5_Assistant.py:267`)
  - Accès à st.session_state['audit_corrected'] sans vérification préalable ligne 267.
  - *Correction* : Initialiser avec: if 'audit_corrected' not in st.session_state: st.session_state['audit_corrected'] = default_value

- **st.write() dans une boucle** (`./modules/impact_analyzer.py:268`)
  - st.write() dans une boucle ligne 268. Peut ralentir l'affichage.
  - *Correction* : Collecter les données dans une liste et afficher avec st.table() ou st.dataframe()

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./pages/2_Validation.py:268`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 268.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./pages/2_Validation.py:271`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 271.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Session state 'audit_hidden' peut ne pas être initialisé** (`./pages/5_Assistant.py:273`)
  - Accès à st.session_state['audit_hidden'] sans vérification préalable ligne 273.
  - *Correction* : Initialiser avec: if 'audit_hidden' not in st.session_state: st.session_state['audit_hidden'] = default_value

- **DataFrame sans contraintes d'affichage** (`./modules/impact_analyzer.py:274`)
  - st.dataframe() ligne 274 sans pagination ou hauteur définie.
  - *Correction* : Ajouter height=400 et use_container_width=True, ou paginer les données

- **Session state 'temp_custom_tags' peut ne pas être initialisé** (`./modules/ui/components/tag_manager.py:274`)
  - Accès à st.session_state['temp_custom_tags'] sans vérification préalable ligne 274.
  - *Correction* : Initialiser avec: if 'temp_custom_tags' not in st.session_state: st.session_state['temp_custom_tags'] = default_value

- **Session state 'propagation_shown' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_smart.py:274`)
  - Accès à st.session_state['propagation_shown'] sans vérification préalable ligne 274.
  - *Correction* : Initialiser avec: if 'propagation_shown' not in st.session_state: st.session_state['propagation_shown'] = default_value

- **Widget sans clé: metric** (`./modules/ui/dashboard/sections.py:278`)
  - Le widget metric ligne 278 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_278'

- **Session state 'audit_hidden' peut ne pas être initialisé** (`./pages/5_Assistant.py:278`)
  - Accès à st.session_state['audit_hidden'] sans vérification préalable ligne 278.
  - *Correction* : Initialiser avec: if 'audit_hidden' not in st.session_state: st.session_state['audit_hidden'] = default_value

- **Session state 'bulk_selected_groups' peut ne pas être initialisé** (`./pages/2_Validation.py:278`)
  - Accès à st.session_state['bulk_selected_groups'] sans vérification préalable ligne 278.
  - *Correction* : Initialiser avec: if 'bulk_selected_groups' not in st.session_state: st.session_state['bulk_selected_groups'] = default_value

- **Widget sans clé: metric** (`./modules/ui/dashboard/sections.py:280`)
  - Le widget metric ligne 280 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_280'

- **Widget sans clé: metric** (`./modules/ui/dashboard/sections.py:282`)
  - Le widget metric ligne 282 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_282'

- **st.write() dans une boucle** (`./modules/ui/config/audit_tools.py:283`)
  - st.write() dans une boucle ligne 283. Peut ralentir l'affichage.
  - *Correction* : Collecter les données dans une liste et afficher avec st.table() ou st.dataframe()

- **Session state 'bulk_selected_groups' peut ne pas être initialisé** (`./pages/2_Validation.py:283`)
  - Accès à st.session_state['bulk_selected_groups'] sans vérification préalable ligne 283.
  - *Correction* : Initialiser avec: if 'bulk_selected_groups' not in st.session_state: st.session_state['bulk_selected_groups'] = default_value

- **Session state 'bulk_selected_groups' peut ne pas être initialisé** (`./pages/2_Validation.py:285`)
  - Accès à st.session_state['bulk_selected_groups'] sans vérification préalable ligne 285.
  - *Correction* : Initialiser avec: if 'bulk_selected_groups' not in st.session_state: st.session_state['bulk_selected_groups'] = default_value

- **Session state 'bulk_selected_groups' peut ne pas être initialisé** (`./pages/2_Validation.py:286`)
  - Accès à st.session_state['bulk_selected_groups'] sans vérification préalable ligne 286.
  - *Correction* : Initialiser avec: if 'bulk_selected_groups' not in st.session_state: st.session_state['bulk_selected_groups'] = default_value

- **Widget sans clé: button** (`./modules/ui/dashboard/sections.py:287`)
  - Le widget button ligne 287 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_287'

- **st.write() dans une boucle** (`./modules/ui/config/audit_tools.py:289`)
  - st.write() dans une boucle ligne 289. Peut ralentir l'affichage.
  - *Correction* : Collecter les données dans une liste et afficher avec st.table() ou st.dataframe()

- **Widget sans clé: button** (`./modules/ui/components/onboarding_modal.py:289`)
  - Le widget button ligne 289 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_289'

- **Session state 'audit_corrected' peut ne pas être initialisé** (`./pages/5_Assistant.py:289`)
  - Accès à st.session_state['audit_corrected'] sans vérification préalable ligne 289.
  - *Correction* : Initialiser avec: if 'audit_corrected' not in st.session_state: st.session_state['audit_corrected'] = default_value

- **Session state 'onboarding_dismissed' peut ne pas être initialisé** (`./modules/ui/components/onboarding_modal.py:290`)
  - Accès à st.session_state['onboarding_dismissed'] sans vérification préalable ligne 290.
  - *Correction* : Initialiser avec: if 'onboarding_dismissed' not in st.session_state: st.session_state['onboarding_dismissed'] = default_value

- **Session state 'onboarding_step' peut ne pas être initialisé** (`./modules/ui/components/onboarding_modal.py:291`)
  - Accès à st.session_state['onboarding_step'] sans vérification préalable ligne 291.
  - *Correction* : Initialiser avec: if 'onboarding_step' not in st.session_state: st.session_state['onboarding_step'] = default_value

- **Widget sans clé: metric** (`./modules/impact_analyzer.py:292`)
  - Le widget metric ligne 292 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_292'

- **DataFrame sans contraintes d'affichage** (`./pages/1_Import.py:296`)
  - st.dataframe() ligne 296 sans pagination ou hauteur définie.
  - *Correction* : Ajouter height=400 et use_container_width=True, ou paginer les données

- **Widget sans clé: metric** (`./modules/impact_analyzer.py:299`)
  - Le widget metric ligne 299 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_299'

- **Session state 'temp_custom_tags' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_smart.py:303`)
  - Accès à st.session_state['temp_custom_tags'] sans vérification préalable ligne 303.
  - *Correction* : Initialiser avec: if 'temp_custom_tags' not in st.session_state: st.session_state['temp_custom_tags'] = default_value

- **Session state 'temp_custom_tags' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_smart.py:304`)
  - Accès à st.session_state['temp_custom_tags'] sans vérification préalable ligne 304.
  - *Correction* : Initialiser avec: if 'temp_custom_tags' not in st.session_state: st.session_state['temp_custom_tags'] = default_value

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_smart.py:306`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 306.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: text_input** (`./modules/ui/config/member_management.py:307`)
  - Le widget text_input ligne 307 n'a pas de clé explicite.
  - *Correction* : Ajouter key='text_input_307'

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_smart.py:307`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 307.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **DataFrame sans contraintes d'affichage** (`./modules/impact_analyzer.py:308`)
  - st.dataframe() ligne 308 sans pagination ou hauteur définie.
  - *Correction* : Ajouter height=400 et use_container_width=True, ou paginer les données

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_smart.py:308`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 308.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Session state 'anomaly_results' peut ne pas être initialisé** (`./pages/5_Assistant.py:309`)
  - Accès à st.session_state['anomaly_results'] sans vérification préalable ligne 309.
  - *Correction* : Initialiser avec: if 'anomaly_results' not in st.session_state: st.session_state['anomaly_results'] = default_value

- **Widget sans clé: selectbox** (`./modules/ui/config/member_management.py:312`)
  - Le widget selectbox ligne 312 n'a pas de clé explicite.
  - *Correction* : Ajouter key='selectbox_312'

- **Session state 'anomaly_results' peut ne pas être initialisé** (`./pages/5_Assistant.py:313`)
  - Accès à st.session_state['anomaly_results'] sans vérification préalable ligne 313.
  - *Correction* : Initialiser avec: if 'anomaly_results' not in st.session_state: st.session_state['anomaly_results'] = default_value

- **Widget sans clé: checkbox** (`./pages/1_Import.py:315`)
  - Le widget checkbox ligne 315 n'a pas de clé explicite.
  - *Correction* : Ajouter key='checkbox_315'

- **Session state 'temp_custom_tags' peut ne pas être initialisé** (`./modules/ui/components/tag_manager.py:316`)
  - Accès à st.session_state['temp_custom_tags'] sans vérification préalable ligne 316.
  - *Correction* : Initialiser avec: if 'temp_custom_tags' not in st.session_state: st.session_state['temp_custom_tags'] = default_value

- **Session state 'temp_custom_tags' peut ne pas être initialisé** (`./modules/ui/components/tag_manager.py:317`)
  - Accès à st.session_state['temp_custom_tags'] sans vérification préalable ligne 317.
  - *Correction* : Initialiser avec: if 'temp_custom_tags' not in st.session_state: st.session_state['temp_custom_tags'] = default_value

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_manager.py:319`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 319.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_manager.py:320`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 320.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: button** (`./pages/1_Import.py:320`)
  - Le widget button ligne 320 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_320'

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_manager.py:321`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 321.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: metric** (`./modules/impact_analyzer.py:322`)
  - Le widget metric ligne 322 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_322'

- **Widget sans clé: metric** (`./modules/ui/components/quick_actions.py:323`)
  - Le widget metric ligne 323 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_323'

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_smart.py:323`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 323.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: metric** (`./modules/impact_analyzer.py:324`)
  - Le widget metric ligne 324 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_324'

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_smart.py:324`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 324.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: metric** (`./modules/ui/components/quick_actions.py:325`)
  - Le widget metric ligne 325 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_325'

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_selector_smart.py:325`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 325.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: metric** (`./modules/impact_analyzer.py:326`)
  - Le widget metric ligne 326 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_326'

- **Widget sans clé: metric** (`./modules/ui/components/quick_actions.py:328`)
  - Le widget metric ligne 328 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_328'

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_manager.py:336`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 336.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_manager.py:337`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 337.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_manager.py:338`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 338.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: metric** (`./modules/impact_analyzer.py:339`)
  - Le widget metric ligne 339 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_339'

- **Widget sans clé: metric** (`./modules/impact_analyzer.py:341`)
  - Le widget metric ligne 341 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_341'

- **Widget sans clé: checkbox** (`./pages/5_Assistant.py:343`)
  - Le widget checkbox ligne 343 n'a pas de clé explicite.
  - *Correction* : Ajouter key='checkbox_343'

- **Widget sans clé: metric** (`./modules/impact_analyzer.py:344`)
  - Le widget metric ligne 344 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_344'

- **Widget sans clé: button** (`./modules/ui/components/quick_actions.py:344`)
  - Le widget button ligne 344 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_344'

- **Widget sans clé: button** (`./pages/5_Assistant.py:349`)
  - Le widget button ligne 349 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_349'

- **Session state 'show_trends' peut ne pas être initialisé** (`./pages/5_Assistant.py:350`)
  - Accès à st.session_state['show_trends'] sans vérification préalable ligne 350.
  - *Correction* : Initialiser avec: if 'show_trends' not in st.session_state: st.session_state['show_trends'] = default_value

- **Widget sans clé: metric** (`./modules/impact_analyzer.py:357`)
  - Le widget metric ligne 357 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_357'

- **st.write() dans une boucle** (`./modules/impact_analyzer.py:362`)
  - st.write() dans une boucle ligne 362. Peut ralentir l'affichage.
  - *Correction* : Collecter les données dans une liste et afficher avec st.table() ou st.dataframe()

- **Session state 'trend_results' peut ne pas être initialisé** (`./pages/5_Assistant.py:378`)
  - Accès à st.session_state['trend_results'] sans vérification préalable ligne 378.
  - *Correction* : Initialiser avec: if 'trend_results' not in st.session_state: st.session_state['trend_results'] = default_value

- **Session state 'show_trends' peut ne pas être initialisé** (`./pages/5_Assistant.py:379`)
  - Accès à st.session_state['show_trends'] sans vérification préalable ligne 379.
  - *Correction* : Initialiser avec: if 'show_trends' not in st.session_state: st.session_state['show_trends'] = default_value

- **Session state 'trend_results' peut ne pas être initialisé** (`./pages/5_Assistant.py:383`)
  - Accès à st.session_state['trend_results'] sans vérification préalable ligne 383.
  - *Correction* : Initialiser avec: if 'trend_results' not in st.session_state: st.session_state['trend_results'] = default_value

- **Widget sans clé: metric** (`./pages/1_Import.py:385`)
  - Le widget metric ligne 385 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_385'

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_manager.py:387`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 387.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: metric** (`./pages/1_Import.py:387`)
  - Le widget metric ligne 387 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_387'

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_manager.py:388`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 388.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Widget sans clé: metric** (`./pages/1_Import.py:389`)
  - Le widget metric ligne 389 n'a pas de clé explicite.
  - *Correction* : Ajouter key='metric_389'

- **Widget sans clé: button** (`./modules/ui/components/tag_manager.py:393`)
  - Le widget button ligne 393 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_393'

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_manager.py:397`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 397.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_manager.py:398`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 398.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Session state 'chat_history' peut ne pas être initialisé** (`./pages/5_Assistant.py:420`)
  - Accès à st.session_state['chat_history'] sans vérification préalable ligne 420.
  - *Correction* : Initialiser avec: if 'chat_history' not in st.session_state: st.session_state['chat_history'] = default_value

- **Session state 'chat_history' peut ne pas être initialisé** (`./pages/5_Assistant.py:423`)
  - Accès à st.session_state['chat_history'] sans vérification préalable ligne 423.
  - *Correction* : Initialiser avec: if 'chat_history' not in st.session_state: st.session_state['chat_history'] = default_value

- **Session state 'chat_history' peut ne pas être initialisé** (`./pages/5_Assistant.py:430`)
  - Accès à st.session_state['chat_history'] sans vérification préalable ligne 430.
  - *Correction* : Initialiser avec: if 'chat_history' not in st.session_state: st.session_state['chat_history'] = default_value

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_manager.py:432`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 432.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Session state 'pending_tag_additions' peut ne pas être initialisé** (`./modules/ui/components/tag_manager.py:433`)
  - Accès à st.session_state['pending_tag_additions'] sans vérification préalable ligne 433.
  - *Correction* : Initialiser avec: if 'pending_tag_additions' not in st.session_state: st.session_state['pending_tag_additions'] = default_value

- **Session state 'chat_history' peut ne pas être initialisé** (`./pages/5_Assistant.py:435`)
  - Accès à st.session_state['chat_history'] sans vérification préalable ligne 435.
  - *Correction* : Initialiser avec: if 'chat_history' not in st.session_state: st.session_state['chat_history'] = default_value

- **Session state 'chat_history' peut ne pas être initialisé** (`./pages/5_Assistant.py:438`)
  - Accès à st.session_state['chat_history'] sans vérification préalable ligne 438.
  - *Correction* : Initialiser avec: if 'chat_history' not in st.session_state: st.session_state['chat_history'] = default_value

- **Widget sans clé: button** (`./pages/5_Assistant.py:442`)
  - Le widget button ligne 442 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_442'

- **Session state 'chat_history' peut ne pas être initialisé** (`./pages/5_Assistant.py:443`)
  - Accès à st.session_state['chat_history'] sans vérification préalable ligne 443.
  - *Correction* : Initialiser avec: if 'chat_history' not in st.session_state: st.session_state['chat_history'] = default_value

- **Widget sans clé: button** (`./pages/5_Assistant.py:450`)
  - Le widget button ligne 450 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_450'

- **Session state 'setup_candidates' peut ne pas être initialisé** (`./pages/5_Assistant.py:456`)
  - Accès à st.session_state['setup_candidates'] sans vérification préalable ligne 456.
  - *Correction* : Initialiser avec: if 'setup_candidates' not in st.session_state: st.session_state['setup_candidates'] = default_value

- **Session state 'setup_candidates' peut ne pas être initialisé** (`./pages/5_Assistant.py:460`)
  - Accès à st.session_state['setup_candidates'] sans vérification préalable ligne 460.
  - *Correction* : Initialiser avec: if 'setup_candidates' not in st.session_state: st.session_state['setup_candidates'] = default_value

- **Widget sans clé: button** (`./pages/5_Assistant.py:463`)
  - Le widget button ligne 463 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_463'

- **Session state 'setup_candidates' peut ne pas être initialisé** (`./pages/5_Assistant.py:532`)
  - Accès à st.session_state['setup_candidates'] sans vérification préalable ligne 532.
  - *Correction* : Initialiser avec: if 'setup_candidates' not in st.session_state: st.session_state['setup_candidates'] = default_value

- **Widget sans clé: button** (`./modules/ui/feedback.py:548`)
  - Le widget button ligne 548 n'a pas de clé explicite.
  - *Correction* : Ajouter key='button_548'

- **DataFrame sans contraintes d'affichage** (`./pages/5_Assistant.py:570`)
  - st.dataframe() ligne 570 sans pagination ou hauteur définie.
  - *Correction* : Ajouter height=400 et use_container_width=True, ou paginer les données

- **Utilisation de iterrows()** (`./tests/db/test_rules.py:25`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./tests/test_integration.py:31`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/ui/config/category_management.py:33`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/ui/dashboard/budget_tracker.py:34`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Concaténation de strings dans une boucle** (`./modules/ui/changelog_parser.py:35`)
  - Utilisation de '+' pour concaténer des strings ligne 35.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Concaténation de strings dans une boucle** (`./modules/ui/changelog_parser.py:35`)
  - Utilisation de '+' pour concaténer des strings ligne 35.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Concaténation de strings dans une boucle** (`./modules/ui/changelog_parser.py:36`)
  - Utilisation de '+' pour concaténer des strings ligne 36.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Concaténation de strings dans une boucle** (`./modules/ui/changelog_parser.py:36`)
  - Utilisation de '+' pour concaténer des strings ligne 36.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Utilisation de iterrows()** (`./modules/db/audit.py:41`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./scripts/audit_redux.py:43`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/ui/config/tags_rules.py:54`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/ui/components/quick_actions.py:58`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/ai/anomaly_detector.py:58`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/ui/rules/rule_validator.py:60`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/ui/components/tag_selector_smart.py:61`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/ai/budget_predictor.py:63`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./tests/db/test_tags.py:71`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Concaténation de strings dans une boucle** (`./modules/ai/rules_auditor.py:74`)
  - Utilisation de '+' pour concaténer des strings ligne 74.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Concaténation de strings dans une boucle** (`./modules/ai/rules_auditor.py:74`)
  - Utilisation de '+' pour concaténer des strings ligne 74.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Utilisation de iterrows()** (`./modules/db/audit.py:74`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Concaténation de strings dans une boucle** (`./modules/ui/components/quick_actions.py:79`)
  - Utilisation de '+' pour concaténer des strings ligne 79.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Utilisation de iterrows()** (`./modules/ui/config/member_management.py:84`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **List comprehension imbriquée** (`./modules/db/transactions.py:85`)
  - Comprehension avec 2 niveaux ligne 85.
  - *Correction* : Vérifier la complexité ou utiliser une boucle explicite avec early exit

- **Utilisation de iterrows()** (`./modules/ai/rules_auditor.py:89`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/db/rules.py:90`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/ai/smart_tagger.py:91`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/db/tags.py:107`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/db/transactions.py:112`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Concaténation de strings dans une boucle** (`./modules/ui/components/tag_selector_smart.py:125`)
  - Utilisation de '+' pour concaténer des strings ligne 125.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Utilisation de iterrows()** (`./pages/4_Recurrence.py:134`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./pages/9_Configuration.py:139`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/analytics.py:148`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/db/transactions_batch.py:148`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/db/categories.py:150`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Concaténation de strings dans une boucle** (`./modules/ui/components/tag_selector_smart.py:158`)
  - Utilisation de '+' pour concaténer des strings ligne 158.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Utilisation de iterrows()** (`./modules/analytics.py:164`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/ui/components/tag_manager.py:164`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/ui/config/member_management.py:166`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Requête réseau sans timeout** (`./modules/ai_manager.py:167`)
  - Requête HTTP ligne 167 sans timeout spécifié.
  - *Correction* : Ajouter timeout=30 (ou valeur appropriée)

- **Concaténation de strings dans une boucle** (`./modules/ui/config/audit_tools.py:168`)
  - Utilisation de '+' pour concaténer des strings ligne 168.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Utilisation de iterrows()** (`./modules/ui/rules/rule_manager.py:168`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/ai/conversational_assistant.py:175`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./pages/4_Recurrence.py:179`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Concaténation de strings dans une boucle** (`./modules/ui/components/tag_manager.py:183`)
  - Utilisation de '+' pour concaténer des strings ligne 183.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Concaténation de strings dans une boucle** (`./modules/ui/components/tag_manager.py:183`)
  - Utilisation de '+' pour concaténer des strings ligne 183.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Utilisation de iterrows()** (`./modules/notifications.py:186`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/ui/config/data_operations.py:186`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/ui/config/audit_tools.py:190`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Concaténation de strings dans une boucle** (`./modules/ui/rules/rule_manager.py:190`)
  - Utilisation de '+' pour concaténer des strings ligne 190.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Concaténation de strings dans une boucle** (`./tests/test_update_manager.py:194`)
  - Utilisation de '+' pour concaténer des strings ligne 194.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Utilisation de iterrows()** (`./modules/ui/config/config_dashboard.py:195`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/ui/config/audit_tools.py:196`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Concaténation de strings dans une boucle** (`./modules/update_manager.py:215`)
  - Utilisation de '+' pour concaténer des strings ligne 215.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Utilisation de iterrows()** (`./pages/1_Import.py:215`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Concaténation de strings dans une boucle** (`./modules/update_manager.py:216`)
  - Utilisation de '+' pour concaténer des strings ligne 216.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Utilisation de iterrows()** (`./modules/ui/dashboard/sections.py:222`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./pages/4_Recurrence.py:224`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Concaténation de strings dans une boucle** (`./pages/1_Import.py:226`)
  - Utilisation de '+' pour concaténer des strings ligne 226.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **List comprehension imbriquée** (`./modules/analytics_v2.py:227`)
  - Comprehension avec 2 niveaux ligne 227.
  - *Correction* : Vérifier la complexité ou utiliser une boucle explicite avec early exit

- **Concaténation de strings dans une boucle** (`./modules/error_tracking.py:230`)
  - Utilisation de '+' pour concaténer des strings ligne 230.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Concaténation de strings dans une boucle** (`./modules/error_tracking.py:233`)
  - Utilisation de '+' pour concaténer des strings ligne 233.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Requête réseau sans timeout** (`./modules/ai_manager.py:235`)
  - Requête HTTP ligne 235 sans timeout spécifié.
  - *Correction* : Ajouter timeout=30 (ou valeur appropriée)

- **Concaténation de strings dans une boucle** (`./modules/error_tracking.py:237`)
  - Utilisation de '+' pour concaténer des strings ligne 237.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Concaténation de strings dans une boucle** (`./modules/update_manager.py:246`)
  - Utilisation de '+' pour concaténer des strings ligne 246.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Concaténation de strings dans une boucle** (`./modules/update_manager.py:246`)
  - Utilisation de '+' pour concaténer des strings ligne 246.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Requête réseau sans timeout** (`./modules/ai_manager.py:263`)
  - Requête HTTP ligne 263 sans timeout spécifié.
  - *Correction* : Ajouter timeout=30 (ou valeur appropriée)

- **Utilisation de iterrows()** (`./modules/ui/components/quick_actions.py:265`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./pages/4_Recurrence.py:269`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Concaténation de strings dans une boucle** (`./pages/2_Validation.py:269`)
  - Utilisation de '+' pour concaténer des strings ligne 269.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Utilisation de iterrows()** (`./modules/ui/config/audit_tools.py:282`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/ui/config/audit_tools.py:288`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/ui/components/transaction_drill_down.py:288`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/ui/config/member_management.py:294`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Utilisation de iterrows()** (`./modules/ui/config/audit_tools.py:300`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Concaténation de strings dans une boucle** (`./scripts/versioning.py:332`)
  - Utilisation de '+' pour concaténer des strings ligne 332.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Utilisation de iterrows()** (`./pages/1_Import.py:333`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Concaténation de strings dans une boucle** (`./pages/1_Import.py:335`)
  - Utilisation de '+' pour concaténer des strings ligne 335.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Concaténation de strings dans une boucle** (`./pages/1_Import.py:336`)
  - Utilisation de '+' pour concaténer des strings ligne 336.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Concaténation de strings dans une boucle** (`./pages/1_Import.py:336`)
  - Utilisation de '+' pour concaténer des strings ligne 336.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Concaténation de strings dans une boucle** (`./pages/1_Import.py:337`)
  - Utilisation de '+' pour concaténer des strings ligne 337.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Concaténation de strings dans une boucle** (`./tests/test_integration.py:352`)
  - Utilisation de '+' pour concaténer des strings ligne 352.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Utilisation de iterrows()** (`./modules/ui/components/tag_manager.py:358`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Concaténation de strings dans une boucle** (`./modules/ui/components/tag_manager.py:364`)
  - Utilisation de '+' pour concaténer des strings ligne 364.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Concaténation de strings dans une boucle** (`./tests/test_integration.py:388`)
  - Utilisation de '+' pour concaténer des strings ligne 388.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Utilisation de iterrows()** (`./modules/ui/components/transaction_drill_down.py:393`)
  - iterrows() est lent. Préférer les opérations vectorisées.
  - *Correction* : Utiliser df.apply(), df.map() ou les opérations directes sur les colonnes

- **Concaténation de strings dans une boucle** (`./modules/ui/components/tag_manager.py:428`)
  - Utilisation de '+' pour concaténer des strings ligne 428.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()

- **Concaténation de strings dans une boucle** (`./tests/test_integration.py:548`)
  - Utilisation de '+' pour concaténer des strings ligne 548.
  - *Correction* : Utiliser ''.join() ou list.append() puis join()


## Optimisations suggérées

- **Import dans une fonction**
  - Import ligne 11 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 14 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 15 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 15 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 18 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 18 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 19 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 20 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 21 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 22 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 22 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 25 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 25. Vérifier si une opération vectorisée est possible.

- **apply() détecté**
  - df.apply() ligne 28. Vérifier si une opération vectorisée est possible.

- **apply() détecté**
  - df.apply() ligne 28. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 30 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 31 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 32 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 32. Vérifier si une opération vectorisée est possible.

- **apply() détecté**
  - df.apply() ligne 32. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 33 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 35 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 36 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 36 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 37 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 38 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 39 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 40 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 40. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 41 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 42 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 43 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 44. Vérifier si une opération vectorisée est possible.

- **apply() détecté**
  - df.apply() ligne 44. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 45 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 45 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 47 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 48. Vérifier si une opération vectorisée est possible.

- **apply() détecté**
  - df.apply() ligne 52. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 52 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 53 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 56 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 58. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 59 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 60. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 63 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 63 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 64 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 64 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 65 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 65. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 66 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 68. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 70 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 74 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 75 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 79. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 81 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 83 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 84 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 88. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 88 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 88 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 89. Vérifier si une opération vectorisée est possible.

- **apply() détecté**
  - df.apply() ligne 90. Vérifier si une opération vectorisée est possible.

- **apply() détecté**
  - df.apply() ligne 91. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 92 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 95 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 95 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 97 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 100 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 102 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 105 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 108. Vérifier si une opération vectorisée est possible.

- **apply() détecté**
  - df.apply() ligne 109. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 109 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 112. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 112 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 113. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 114 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 120. Vérifier si une opération vectorisée est possible.

- **apply() détecté**
  - df.apply() ligne 120. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 122 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 123 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 124 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 124 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 125 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 131 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 132 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 134 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 137 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 139 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 140 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 140 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 144 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 144 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 145 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 146 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 146. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 147 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 147. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 148 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 149 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 154 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 155 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 159 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 159 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 159 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 161. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 172 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 178 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 184. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 185 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 185. Vérifier si une opération vectorisée est possible.

- **apply() détecté**
  - df.apply() ligne 185. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 185 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 188 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 190 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 195. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 197 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 198 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 198 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 200 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 205 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 212 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 216 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 220 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 226. Vérifier si une opération vectorisée est possible.

- **apply() détecté**
  - df.apply() ligne 227. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 235 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 243 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 245 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 248 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 251 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 255. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 290 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 294 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 299 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 303 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 312 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 313 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 319 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 320 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 345 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 351 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 353 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 354 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 354 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 355 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 360 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 361 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 399 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 401 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 433 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 441 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 469 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 498 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 510 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 512 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 521 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 531 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 538 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 542 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 550 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **apply() détecté**
  - df.apply() ligne 568. Vérifier si une opération vectorisée est possible.

- **Import dans une fonction**
  - Import ligne 582 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 617 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 635 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 663 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 696 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 716 a l'interieur d'une fonction. Peut ralentir les appels répétés.

- **Import dans une fonction**
  - Import ligne 731 a l'interieur d'une fonction. Peut ralentir les appels répétés.


---

## Guide de correction pour IA

Ce rapport est disponible en format JSON pour traitement automatique.

### Ordre de correction recommandé :

1. **Problèmes critiques de performance** (PERFORMANCE, DB)
2. **Erreurs logiques** (LOGIC, STATE)
3. **Problèmes de sécurité** (SECURITY)
4. **Avertissements Streamlit** (STREAMLIT_*)
5. **Optimisations** (en dernier)
