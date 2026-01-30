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
- `escape_html()` : Échappe les caractères HTML pour prévenir XSS
- `safe_html_template()` : Interpolation sécurisée dans templates HTML
- `validate_csv_file()` : Validation de fichiers CSV uploadés

**Guidelines** :
- Fonctions pures sans effets de bord
- Bien commenter les regex complexes
- **TOUJOURS** utiliser `escape_html()` avant d'insérer du contenu utilisateur dans du HTML

#### `modules/exceptions.py` ⚡ NOUVEAU (v2.8.0)
**Rôle** : Classes d'exceptions personnalisées pour meilleure gestion d'erreurs.

**Classes disponibles** :
- `FinancePersoException` : Exception de base
- `DatabaseError` : Erreurs de base de données
- `ValidationError` : Erreurs de validation d'entrées
- `ImportError` : Erreurs d'import CSV/fichiers
- `AIProviderError` : Erreurs d'API IA
- `ConfigurationError` : Erreurs de configuration
- `CategorizationError` : Erreurs de catégorisation
- `RuleError` : Erreurs de règles d'apprentissage

**Guidelines** :
- Utiliser ces exceptions spécifiques plutôt que `Exception` générique
- **JAMAIS** de clause `except:` nue - toujours spécifier le type d'exception

#### `modules/db/settings.py` ⚡ NOUVEAU (v2.8.0)
**Rôle** : Gestion des paramètres utilisateur en base de données.

**Fonctions clés** :
- `get_setting(key, default)` : Récupérer une valeur
- `set_setting(key, value, description)` : Définir une valeur
- `get_internal_transfer_targets()` : Récupérer mots-clés de virements internes
- `set_internal_transfer_targets(targets)` : Définir mots-clés de virements internes

**Guidelines** :
- Utiliser pour toute configuration utilisateur (éviter hardcoding)
- Fournir toujours des valeurs par défaut
- Documenter les settings avec `description`

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

## 🔒 Sécurité et Bonnes Pratiques (v2.8.0)

### Gestion des secrets
- **JAMAIS** hardcoder de clés API ou données personnelles dans le code
- Utiliser `python-dotenv` pour charger les variables d'environnement
- Le fichier `.env` doit avoir les permissions 0600 (lecture/écriture propriétaire uniquement)
- Valider le format des clés API avant de les sauvegarder

**Exemple** :
```python
from modules.ui.config.api_settings import validate_api_key

if validate_api_key(api_key, "Gemini"):
    # Clé valide
    set_key(".env", "GEMINI_API_KEY", api_key)
    set_secure_env_permissions(".env")
```

### Validation des entrées
- **TOUJOURS** valider les entrées utilisateur avant traitement
- Patterns regex : vérifier avec `re.compile()` et tester sur échantillons
- Détecter les patterns dangereux (catastrophic backtracking)
- CSV : valider le mapping et échantillonner les données

**Exemple** :
```python
def validate_regex_pattern(pattern: str) -> tuple[bool, str]:
    try:
        compiled = re.compile(pattern, re.IGNORECASE)
        # Test sur échantillons
        for test in ["TEST", "test 123", ""]:
            compiled.search(test)
        return True, ""
    except re.error as e:
        return False, f"Pattern invalide: {e}"
```

### Gestion d'erreurs
- **JAMAIS** utiliser `except:` nu - toujours spécifier le type
- Utiliser les classes d'exceptions de `modules/exceptions.py`
- Logger les erreurs avec contexte via `modules/logger.py`
- Fournir des messages d'erreur clairs et actionnables

**Anti-pattern** ❌ :
```python
try:
    risky_operation()
except:  # Attrape TOUT, y compris KeyboardInterrupt !
    pass
```

**Bon pattern** ✅ :
```python
try:
    risky_operation()
except (ValueError, TypeError) as e:
    logger.error(f"Operation failed: {e}")
    raise ValidationError(f"Invalid input: {e}")
```

### Protection XSS
- Utiliser `escape_html()` pour tout contenu utilisateur dans HTML
- Préférer `safe_html_template()` pour interpolation complexe
- Auditer tous les usages de `unsafe_allow_html=True`

**Exemple** :
```python
from modules.utils import safe_html_template

safe_html = safe_html_template(
    "<div class='item'><h3>{title}</h3><p>{description}</p></div>",
    title=user_title,  # Automatiquement échappé
    description=user_description
)
st.markdown(safe_html, unsafe_allow_html=True)
```

### Configuration utilisateur
- Stocker la config sensible en base de données (table `settings`)
- Ne jamais hardcoder de noms, emails, ou identifiants personnels
- Fournir une UI pour modifier la configuration
- Assurer la rétrocompatibilité avec des valeurs par défaut

**Exemple** :
```python
from modules.db.settings import get_setting, set_setting

# Récupérer avec fallback
api_url = get_setting("api_url", default="http://localhost:8000")

# Sauvegarder
set_setting("api_url", new_url, "URL de l'API backend")
```

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

### ✅ Implémenté (v2.0.0)

#### `modules/ai/` - Suite IA Complète
**Architecture** : 5 modules spécialisés avec exports centralisés dans `__init__.py`

1. **`anomaly_detector.py`** - Détection d'Anomalies de Montant
   - Fonction : `detect_amount_anomalies(df, threshold_sigma=2.0)`
   - Analyse statistique (moyenne + écart-type par libellé)
   - Classification par sévérité (high/medium)
   - Retourne : Liste de dicts avec `type`, `label`, `details`, `rows`, `severity`

2. **`smart_tagger.py`** - Suggestions de Tags Intelligentes
   - Fonction : `suggest_tags_for_transaction(tx_row)`
   - Fonction batch : `suggest_tags_batch(df, limit=20)`
   - Analyse contextuelle via IA (libellé, montant, catégorie, date)
   - Tags disponibles : Remboursement, Professionnel, Cadeau, Urgent, Récurrent, etc.

3. **`budget_predictor.py`** - Prédictions Budgétaires
   - Fonction : `predict_budget_overruns(df_month, budgets)`
   - Fonction : `get_budget_alerts_summary(predictions)`
   - Projection linéaire jusqu'à fin de mois
   - Alertes : 🟢 OK (<80%), 🟠 Attention (80-100%), 🔴 Dépassement (>100%)

### Modules AI
- `anomaly_detector.py`: Détection statistique des montants abérrants. Désormais persistant via le tag `ignore_anomaly`.
- `rules_auditor.py`: Audit de l'intégrité des règles d'apprentissage.
- `conversational_assistant.py`: Moteur de chat ReAct avec appels d'outils.

### Tests & Qualité
Les outils de test sont intégrés dans `pages/98_Tests.py` et couvrent désormais les modules d'IA (audit, assistant) en plus de la base de données et de l'UI.
- Total : ~195 tests.
- Couverture : ~78%.

4. **`trend_analyzer.py`** - Analyse de Tendances
   - Fonction : `analyze_spending_trends(df_current, df_previous, threshold_pct=30.0)`
   - Fonction : `get_top_categories_comparison(df_current, df_previous, top_n=5)`
   - Comparaison période actuelle vs précédente
   - Génération d'insights narratifs

5. **`conversational_assistant.py`** - Assistant Conversationnel
   - Fonction : `chat_with_assistant(user_message, conversation_history)`
   - Fonctions outils : `get_expenses_by_category()`, `get_budget_status()`, `get_top_expenses()`
   - Chat IA pour interroger finances en langage naturel

**Intégrations UI** :
- `pages/5_Assistant.py` : 3 nouveaux onglets (🎯 Anomalies, 📊 Tendances, 💬 Chat IA)
- `pages/3_Synthese.py` : Widget "📈 Alertes Budgétaires"

**Drill-Down Interactif** (v2.1) :
- Composant : `modules/ui/components/transaction_drill_down.py`
- Permet de cliquer sur un insight de tendance pour voir les transactions
- **Édition en masse** : Modifier les catégories de transactions validées
- Sélecteur individuel par transaction + bouton "💾 Sauvegarder"
- Fonctionne aussi pour les transactions en attente avec "✅ Valider Tout"

**Guidelines d'utilisation** :
```python
from modules.ai import detect_amount_anomalies, predict_budget_overruns, chat_with_assistant

# Détection d'anomalies
anomalies = detect_amount_anomalies(df)

# Prédictions budgétaires
predictions = predict_budget_overruns(df_month, budgets)

# Chat IA
response = chat_with_assistant("Combien j'ai dépensé en alimentation ?")

# Drill-down interactif
from modules.ui.components.transaction_drill_down import render_category_drill_down_expander
render_category_drill_down_expander(insight, period_start, period_end, key_prefix="trend_0")
```

**Détection des Virements Internes** (v2.1) :
- Module : `modules/analytics.py`
- Fonctions : `detect_internal_transfers()`, `exclude_internal_transfers()`
- Patterns détectés : "VIR SEPA AURELIEN", "ALIMENTATION COMPTE JOINT", "VIREMENT", etc.
- Toggle dans l'onglet Tendances pour exclure/inclure les virements

### 🔮 Futures améliorations possibles

- Function calling avancé pour le Chat IA
- Smart Tagger UI dans page Validation
- Anomaly Learning (marquer comme "normal")
- Trend Visualization avec graphiques
- Notifications push/email pour alertes budgétaires
- Drill-down dans la page Synthèse (graphiques)

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

**Dernière mise à jour** : 2026-01-28
**Développé par** : Aurélien (avec l'aide de Gemini)

