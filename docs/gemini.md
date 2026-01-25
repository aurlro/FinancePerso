# 🤖 Gemini Development Guidelines

Ce document contient les instructions de développement pour les futures sessions avec Gemini ou tout autre assistant IA.

## 📐 Architecture du projet

### Stack technique

- **Frontend** : Streamlit (Python)
- **Backend** : Python avec SQLite
- **IA** : API Gemini (ou autres via abstraction dans `categorization.py`)
- **Style** : Custom CSS injecté via `modules/ui.py`

### Principes de design

1. **Simplicité d'abord** : Interface épurée, workflow intuitif
2. **Compacité** : Minimiser le scrolling vertical, utiliser des layouts horizontaux
3. **Feedback immédiat** : Toasts, progress bars, réactivité
4. **Smart Defaults** : Pré-remplir intelligemment les champs
5. **Gamification** : Barre de progression, encouragements

## 🗂️ Organisation du code

### Modules principaux

#### `modules/data_manager.py`
**Rôle** : Gestion complète de la base de données SQLite.

**Fonctions critiques** :
- `init_db()` : Initialisation et migrations de schéma
- `get_pending_transactions()` : Récupération des transactions à valider
- `bulk_update_transaction_status()` : Validation en masse
- `mark_transaction_as_ungrouped()` : Exclusion permanente du groupement

**Guidelines** :
- Toujours utiliser `get_db_connection()` comme context manager
- Ajouter `st.cache_data.clear()` après toute modification de données
- Utiliser des migrations conditionnelles (`if column not in columns`) pour éviter les erreurs

#### `modules/categorization.py`
**Rôle** : IA de catégorisation des transactions.

**Fonctions** :
- `predict_category_ai()` : Catégorisation d'une transaction
- Support multi-provider (Gemini, Ollama, DeepSeek, OpenAI)

**Guidelines** :
- Toujours gérer les erreurs API (timeouts, limites de taux)
- Logger les échecs pour debugging
- Utiliser des prompts structurés et explicites

#### `modules/utils.py`
**Rôle** : Fonctions utilitaires partagées.

**Fonctions clés** :
- `clean_label()` : Nettoyage des libellés bancaires (regex)

**Guidelines** :
- Fonctions pures sans effets de bord
- Bien commenter les regex complexes

#### `modules/ui.py`
**Rôle** : Composants UI et styles réutilisables.

**Contenu** :
- `load_css()` : Injection de styles personnalisés
- Composants visuels partagés

**Guidelines** :
- CSS minimaliste et ciblé
- Utiliser `data-testid` pour sélecteurs robustes

### Pages Streamlit

#### `pages/2_Validation.py` (LA PLUS COMPLEXE)
**Architecture** :
1. **Initialisation** : Session state, CSS injection
2. **Chargement données** : `get_pending_transactions()`
3. **Filtres** : Sidebar avec multiselects
4. **Affichage** :
   - Fonction `show_validation_list()` décorée `@st.fragment` pour performance
   - Groupement intelligent dans `get_smart_group()`
   - Layout "Smart Expander" : Résumé + Bouton ✅ externe + Détails internes

**Points d'attention** :
- **Groupement** : Vérifier `is_manually_ungrouped` ET `session_state['excluded_tx_ids']`
- **État pré-calculé** : Initialiser les valeurs AVANT le rendu pour supporter la validation "aveugle"
- **CSS Smart** : Le bouton externe disparaît si l'expander est ouvert (`:has(details[open])`)

#### `pages/9_Configuration.py`
**Structure** : Tabs pour organiser les paramètres.

**Tabs** :
1. API & Services (provider, clés)
2. Membres & Cartes
3. Catégories
4. Tags & Règles (gestion cleanup)
5. Données & Danger (export, reset)

## 🔄 Workflow de développement

### 1. Planification
Toujours créer un `implementation_plan.md` avant de coder :
- Lister les fichiers à modifier
- Décrire les changements précis
- Définir un plan de vérification

### 2. Implémentation
- **Commits atomiques** : Un changement logique = un commit
- **Tests manuels** : Vérifier dans l'UI après chaque modif
- **Logs** : Utiliser `modules/logger.py` pour tracer les opérations critiques

### 3. Documentation
- Mettre à jour `walkthrough.md` après chaque feature
- Commenter le code complexe (surtout regex et logique métier)

## 🎨 Conventions de style

### Python
- PEP 8 (mais relaxed sur longueur de ligne si nécessaire pour lisibilité)
- Docstrings pour toutes les fonctions publiques
- Type hints là où c'est utile (pas obligatoire partout)

### Streamlit
- **Keys uniques** : `f"{widget_type}_{unique_id}"` (ex: `f"btn_ext_{group_id}"`)
- **Session state** : Initialiser avec `if 'key' not in st.session_state`
- **Fragments** : Utiliser `@st.fragment` pour les listes longues (performance)

### CSS
- Préfixer les classes custom par `fp-` (ex: `fp-card`)
- Utiliser `data-testid` pour ciblage robuste
- Inline styles en dernier recours seulement

## 🐛 Patterns à éviter

### ❌ Anti-patterns

1. **Modifier session_state dans un callback** sans `st.rerun()` → État incohérent
2. **Requêtes DB dans des boucles** → Utiliser `bulk_*` ou `executemany`
3. **Clés de widgets non-uniques** → Streamlit warnings et bugs
4. **Oublier `st.cache_data.clear()`** après modif DB → Données obsolètes
5. **Import circulaires** → Restructurer les modules

### ✅ Best practices

1. **Context managers** : Toujours pour DB (`with get_db_connection()`)
2. **Defensive coding** : Vérifier existence colonnes avant accès (`row.get('col', default)`)
3. **User feedback** : Toast pour toute action (`st.toast()`)
4. **Graceful degradation** : Gérer les erreurs API (fallback sur "Inconnu")

## 📊 Données et schéma

### Table `transactions`
**Colonnes clés** :
- `id` : PRIMARY KEY
- `date`, `label`, `amount` : Données bancaires
- `category_validated` : Catégorie finale
- `status` : 'pending' ou 'validated'
- `member` : Qui a payé
- `beneficiary` : Pour qui
- `tags` : CSV string
- `is_manually_ungrouped` : Flag pour exclusion groupe (INTEGER 0/1)
- `tx_hash` : Hash unique pour déduplication

### Règles métier

1. **Groupement intelligent** :
   - Par défaut : `clean_label(label)`
   - Chèques : `clean_label(label) + amount`
   - Si `is_manually_ungrouped == 1` : `single_{id}`

2. **Validation** :
   - Toujours `bulk_update_transaction_status()` même pour 1 tx (cohérence)
   - Si "Mémoriser" : Créer rule dans `learning_rules`

3. **Tags** :
   - Stockés comme CSV : `"Tag1, Tag2, Tag3"`
   - Fonctions : `get_all_tags()` parse et déduplique

## 🚀 Features futures (Roadmap IA)

Voir la liste des 10 idées proposées dans la conversation (Chatbot, Forecasting, Détection anomalies, etc.). Pour implémenter une nouvelle feature IA :

1. **Créer un module dédié** : `modules/ai_<feature>.py`
2. **Abstraction provider** : Utiliser le pattern de `categorization.py`
3. **UI séparée** : Nouvelle page ou section dans Assistant
4. **Configuration** : Paramètres dans Config si nécessaire

## 🔧 Debugging

### Logs
```python
from modules.logger import logger
logger.info("Message informatif")
logger.error("Erreur critique", exc_info=True)
```

### Streamlit Debugging
- `st.write(variable)` : Affichage rapide
- `st.json(data)` : Pour structures complexes
- Vérifier les logs console du navigateur (F12) pour erreurs JS

### Base de données
```bash
sqlite3 Data/finance.db
.tables
.schema transactions
SELECT * FROM transactions WHERE status='pending' LIMIT 5;
```

## 📦 Dépendances

### Core
- `streamlit` : Framework UI
- `pandas` : Manipulation de données
- `google-generativeai` : API Gemini

### Optionnelles (selon provider IA)
- `openai` : Pour OpenAI
- `requests` : Pour DeepSeek et Ollama

### Utilitaires
- `python-dotenv` : Variables d'environnement

## 🎯 Checklist de Pull Request

Avant de finaliser une feature :

- [ ] Code formaté et commenté
- [ ] Tests manuels effectués
- [ ] `implementation_plan.md` et `walkthrough.md` à jour
- [ ] Pas de `print()` ou de code debug
- [ ] Migrations DB testées (si applicable)
- [ ] Clés API non hardcodées
- [ ] Messages utilisateur clairs et en français
- [ ] Performance vérifiée (pas de lag avec 1000+ transactions)

## 💡 Tips pour Gemini

### Quand modifier ce fichier

- Après chaque architectural decision importante
- Quand un nouveau pattern émerge
- Si une erreur récurrente est identifiée

### Comment l'utiliser

1. **Début de session** : Lire ce fichier pour contexte
2. **Durant dev** : S'y référer pour conventions
3. **Fin de session** : Le mettre à jour si nécessaire

---

**Dernière mise à jour** : 2026-01-17
**Développé par** : Aurélien (avec l'aide de Gemini)
