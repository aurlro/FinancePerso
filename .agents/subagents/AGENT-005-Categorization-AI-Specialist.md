# AGENT-005: Categorization AI Specialist

## 🎯 Mission

Architecte du systeme de categorisation intelligent de FinancePerso. Responsable de la classification automatique des transactions via regles, Machine Learning local et IA cloud. Garant de la precision et de l'amelioration continue du systeme.

---

## 📚 Contexte: Architecture de Categorization

### Philosophie
> "La categorization est un apprentissage, pas une configuration. Chaque validation utilisateur enrichit le systeme."

### Cascade de Categorization

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CATEGORIZATION CASCADE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Priority 1: RULES (Fast & Deterministic)                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 1. User Learning Rules (DB) - Pre-compiled regex            │   │
│  │ 2. Hardcoded Rules (Code) - Internal transfers              │   │
│  │                                                             │   │
│  │ Speed: ~0.1ms | Precision: 100% (if match)                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ↓ No match                             │
│  Priority 2: LOCAL ML (Offline & Private)                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Scikit-learn Classifier (TF-IDF + SVM/Naive Bayes)          │   │
│  │                                                             │   │
│  │ Speed: ~5ms | Precision: 85-90% (if trained)                │   │
│  │ Condition: confidence >= 0.6                                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ↓ Low confidence                        │
│  Priority 3: AI CLOUD (Accurate & Context-aware)                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Gemini/OpenAI/DeepSeek via AI Manager                       │   │
│  │                                                             │   │
│  │ Speed: ~500ms | Precision: 92-95%                           │   │
│  │ Cost: API calls | Fallback: "Inconnu"                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Performance Comparison

| Methode | Latence | Precision | Cout | Offline | Privacy |
|---------|---------|-----------|------|---------|---------|
| **Rules** | ~0.1ms | 100%* | Free | Oui | Oui |
| **Local ML** | ~5ms | 85-90% | Free | Oui | Oui |
| **AI Cloud** | ~500ms | 92-95% | API | Non | Non |

*Si pattern match

---

## 📋 Module 1: Learning Rules System

### Architecture des Regles

```python
"""
Systeme de regles avec:
- Patterns regex pre-compiles (performance)
- Priorites (higher = first)
- Persistance en base
"""

# Table: learning_rules
# id INTEGER PRIMARY KEY
# pattern TEXT UNIQUE      -- Regex ou string simple
# category TEXT            -- Categorie cible
# priority INTEGER         -- 1-100, plus haut = prioritaire
# created_at TIMESTAMP
```

### Pre-compiled Regex (Performance)

```python
@st.cache_data(ttl="1h")
def get_compiled_learning_rules() -> list[tuple]:
    """
    Recupere les regles avec patterns pre-compiles.
    
    Performance: 90-95% plus rapide que compilation a la volee.
    
    Returns:
        List[(compiled_pattern, category, priority, original_pattern)]
    """
    df_rules = get_learning_rules()
    
    compiled_rules = []
    for _, row in df_rules.iterrows():
        pattern_str = row["pattern"]
        try:
            # Pre-compile avec IGNORECASE
            compiled = re.compile(pattern_str, re.IGNORECASE)
            compiled_rules.append((compiled, row["category"], row["priority"], pattern_str))
        except re.error as e:
            logger.warning(f"Invalid regex '{pattern_str}': {e}")
            compiled_rules.append((None, row["category"], row["priority"], pattern_str))
    
    # Sort by priority (highest first)
    compiled_rules.sort(key=lambda x: x[2], reverse=True)
    return compiled_rules
```

### Application des Regles

```python
def apply_rules(label: str) -> tuple[str | None, float]:
    """
    Applique les regles de categorization.
    
    Returns:
        (category, confidence)
        - Si match: (category, 1.0)
        - Si no match: (None, 0.0)
    """
    label_upper = label.upper()
    
    # Recuperer regles pre-compilees
    compiled_rules = get_compiled_learning_rules()
    
    for pattern_compiled, category, priority, pattern_str in compiled_rules:
        if pattern_compiled:
            if pattern_compiled.search(label_upper):
                return category, 1.0
        else:
            # Fallback: string matching simple
            if pattern_str.upper() in label_upper:
                return category, 1.0
    
    return None, 0.0
```

---

## 🤖 Module 2: Local Machine Learning

### Architecture

```python
"""
Modele local Scikit-learn:
- Features: TF-IDF sur libelles nettoyes
- Model: SVM ou Naive Bayes (leger, rapide)
- Training: Sur transactions validees
- Inference: ~5ms
"""

class LocalTransactionClassifier:
    """Classifier local pour categorization offline."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words=french_stop_words
        )
        self.classifier = SVC(probability=True, kernel='linear')
        self.is_trained = False
        self.categories = []
    
    def train(self, df: pd.DataFrame):
        """Entraine le modele sur transactions validees."""
        train_df = df[df['category_validated'] != 'Inconnu']
        
        if len(train_df) < 50:
            logger.warning("Not enough data to train local ML")
            return
        
        # Vectorisation
        X = self.vectorizer.fit_transform(train_df['clean_label'])
        y = train_df['category_validated']
        
        # Entrainement
        self.classifier.fit(X, y)
        self.categories = list(self.classifier.classes_)
        self.is_trained = True
        
        self._save_model()
        logger.info(f"Local ML trained on {len(train_df)} transactions")
    
    def predict(self, label: str, amount: float, date) -> tuple[str | None, float]:
        """Predicit la categorie."""
        if not self.is_trained:
            return None, 0.0
        
        clean = clean_label(label)
        X = self.vectorizer.transform([clean])
        
        prediction = self.classifier.predict(X)[0]
        probabilities = self.classifier.predict_proba(X)[0]
        confidence = max(probabilities)
        
        return prediction, confidence
```

---

## ☁️ Module 3: AI Cloud Providers

### AI Manager Integration

```python
def predict_category_ai(label: str, amount: float, date) -> tuple[str, float]:
    """
    Categorization via IA cloud.
    
    Returns:
        (category, confidence)
    """
    cleaned_label = clean_label(label)
    categories = get_categories()
    
    prompt = f"""
Tu es un expert en categorization financiere francaise.
Analyse cette transaction et choisis la categorie la plus appropriee.

Transaction:
- Libelle: {cleaned_label}
- Montant: {amount:.2f} EUR
- Date: {date}

Categories possibles: {', '.join(categories)}

Reponds UNIQUEMENT en JSON:
{{
    "category": "nom de la categorie",
    "confidence": 0.0 a 1.0,
    "reasoning": "explication courte"
}}
"""
    
    try:
        provider = get_ai_provider()
        model = get_active_model_name()
        
        response = provider.generate_json(prompt, model_name=model)
        
        category = response.get("category", "Inconnu")
        confidence = float(response.get("confidence", 0.5))
        
        if category not in categories:
            logger.warning(f"AI returned unknown category: {category}")
            category = "Inconnu"
            confidence = 0.0
        
        return category, confidence
        
    except Exception as e:
        logger.error(f"AI categorization failed: {e}")
        return "Inconnu", 0.0
```

---

## 📊 Module 4: Quality & Improvement

### Metriques de Precision

```python
class CategorizationMetrics:
    """Metriques de qualite du systeme."""
    
    @classmethod
    def calculate_accuracy(cls, days: int = 30) -> dict:
        """Calcule la precision sur les dernieres validations."""
        df = get_recent_validated_transactions(days=days)
        
        if df.empty:
            return {}
        
        # Re-categoriser pour comparer
        df['predicted'] = df.apply(
            lambda row: categorize_transaction(row['label'], row['amount'], row['date'])[0],
            axis=1
        )
        
        total = len(df)
        correct = (df['category_validated'] == df['predicted']).sum()
        
        return {
            'overall_accuracy': correct / total,
            'total_evaluated': total,
            'by_source': df.groupby('categorization_source').apply(
                lambda x: (x['category_validated'] == x['predicted']).mean()
            ).to_dict()
        }
```

---

## 🔧 Responsabilites

### Quand consulter cet agent

- Nouvelle logique de categorization
- Modification des regles d'apprentissage
- Entrainement/retraining ML
- Changement de provider IA
- Analyse de qualite/precision
- Nouvelle categorie metier

---

**Version**: 1.0
**Date**: 2026-02-25
**Statut**: PRET A L'EMPLOI

---

## 🔧 Module Additionnel: Auto-Learning & Amelioration

### Extraction Automatique de Regles

```python
"""
Extraction automatique de regles depuis les validations utilisateur.
"""

from collections import Counter
import re

def extract_rule_from_validation(label: str, category: str) -> tuple[bool, str]:
    """
    Extrait une regle potentielle d'un libelle valide.
    
    Strategy:
    1. Nettoyer le label (enlever dates, numéros)
    2. Extraire mots significatifs (2-3 mots)
    3. Verifier unicite à la categorie
    4. Creer regle si pertinent
    
    Returns:
        (success, pattern)
    """
    # Nettoyage
    cleaned = clean_for_learning(label)
    words = cleaned.split()
    
    if len(words) < 1:
        return False, ""
    
    # Candidats: 1-gram, 2-gram, 3-gram
    candidates = []
    for n in range(1, min(4, len(words) + 1)):
        for i in range(len(words) - n + 1):
            ngram = " ".join(words[i:i+n]).upper()
            candidates.append(ngram)
    
    # Selectionner le meilleur
    for candidate in sorted(candidates, key=len, reverse=True):
        # Verifier si unique à cette categorie
        if is_pattern_unique(candidate, category):
            # Valider comme regex
            if validate_safe_pattern(candidate):
                add_learning_rule(candidate, category, priority=1)
                return True, candidate
    
    return False, ""

def clean_for_learning(label: str) -> str:
    """Nettoie pour extraction regles."""
    # Enlever dates
    label = re.sub(r'\d{2}/\d{2}(/\d{2,4})?', '', label)
    label = re.sub(r'\d{4}-\d{2}-\d{2}', '', label)
    
    # Enlever numéros
    label = re.sub(r'\b\d{4,}\b', '', label)
    
    # Enlever ponctuation
    label = re.sub(r'[^\w\s]', ' ', label)
    
    # Mots vides
    stop_words = {'le', 'la', 'les', 'de', 'des', 'du', 'et', 'en', 'un', 'une'}
    words = [w for w in label.split() if w.lower() not in stop_words and len(w) > 2]
    
    return ' '.join(words)

def is_pattern_unique(pattern: str, category: str) -> bool:
    """Verifie si pattern est unique à cette categorie."""
    # Compter occurrences dans autres categories
    from modules.db.transactions import get_transactions_by_criteria
    
    other_count = 0
    same_count = 0
    
    # Rechercher pattern
    df = get_transactions_by_criteria(label_contains=pattern)
    
    for _, row in df.iterrows():
        if row['category_validated'] == category:
            same_count += 1
        else:
            other_count += 1
    
    # Unique si > 80% dans categorie cible
    total = same_count + other_count
    if total < 3:
        return False
    
    return (same_count / total) > 0.8

def validate_safe_pattern(pattern: str) -> bool:
    """Valide qu'un pattern est sur (pas ReDoS)."""
    # Longueur raisonnable
    if len(pattern) > 100:
        return False
    
    # Pas de caracteres speciaux dangereux
    dangerous = ['.*', '.+', '(', ')', '[', ']', '{', '}']
    for d in dangerous:
        if d in pattern:
            return False
    
    return True
```

### Training Pipeline Complet

```python
"""
Pipeline complet d'entrainement ML.
"""

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import joblib

class MLTrainingPipeline:
    """Pipeline d'entrainement du modele ML."""
    
    def __init__(self):
        self.model = LocalTransactionClassifier()
        self.metrics = {}
    
    def prepare_data(self, min_samples_per_class: int = 5) -> pd.DataFrame:
        """
        Prepare les donnees d'entrainement.
        
        Args:
            min_samples_per_class: Minimum d'echantillons par categorie
        """
        # Recuperer transactions validees
        df = get_all_transactions(filters={'status': 'validated'})
        
        # Nettoyer labels
        df['clean_label'] = df['label'].apply(clean_label)
        
        # Filtrer categories avec assez d'echantillons
        counts = df['category_validated'].value_counts()
        valid_cats = counts[counts >= min_samples_per_class].index
        
        df = df[df['category_validated'].isin(valid_cats)]
        
        # Equilibrage (optionnel)
        df = self._balance_dataset(df)
        
        return df
    
    def _balance_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Equilibre les classes par sur-echantillonnage."""
        from sklearn.utils import resample
        
        balanced = []
        max_size = df['category_validated'].value_counts().max()
        
        for category in df['category_validated'].unique():
            cat_df = df[df['category_validated'] == category]
            
            if len(cat_df) < max_size:
                # Sur-echantillonner
                cat_df = resample(
                    cat_df,
                    replace=True,
                    n_samples=max_size,
                    random_state=42
                )
            
            balanced.append(cat_df)
        
        return pd.concat(balanced)
    
    def train_and_evaluate(self, df: pd.DataFrame) -> dict:
        """
        Entraine et evalue le modele.
        
        Returns:
            Metriques d'evaluation
        """
        # Split train/test
        X = df['clean_label']
        y = df['category_validated']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Vectorisation
        vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)
        
        # Entrainement
        classifier = SVC(probability=True, kernel='linear')
        classifier.fit(X_train_vec, y_train)
        
        # Evaluation
        y_pred = classifier.predict(X_test_vec)
        
        self.metrics = {
            'accuracy': classifier.score(X_test_vec, y_test),
            'cross_val_score': cross_val_score(classifier, X_train_vec, y_train, cv=5).mean(),
            'classification_report': classification_report(y_test, y_pred, output_dict=True),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'num_classes': len(classifier.classes_),
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
        
        # Sauvegarder
        self.model.vectorizer = vectorizer
        self.model.classifier = classifier
        self.model.is_trained = True
        self.model.categories = list(classifier.classes_)
        
        return self.metrics
    
    def should_retrain(self) -> bool:
        """Determine si reentrainement necessaire."""
        # Recuperer stats
        last_training = get_last_training_date()
        new_validations = count_validations_since(last_training)
        
        # Retrainer si:
        # - Plus de 100 nouvelles validations
        # - Dernier entrainement > 7 jours
        # - Precision actuelle < 0.8
        
        if new_validations > 100:
            return True
        
        if (datetime.now() - last_training).days > 7:
            return True
        
        current_acc = get_current_model_accuracy()
        if current_acc and current_acc < 0.8:
            return True
        
        return False

# Scheduler de reentrainement
def scheduled_retrain():
    """Verifie et lance reentrainement si necessaire."""
    pipeline = MLTrainingPipeline()
    
    if pipeline.should_retrain():
        logger.info("Lancement reentrainement ML...")
        
        df = pipeline.prepare_data()
        metrics = pipeline.train_and_evaluate(df)
        
        # Sauvegarder si amelioration
        if metrics['accuracy'] > get_current_model_accuracy():
            pipeline.model._save_model()
            logger.info(f"Modele reentraine: accuracy={metrics['accuracy']:.2%}")
        else:
            logger.warning("Nouveau modele moins performant, conservation ancien")
```

### Fallback Strategies

```python
"""
Strategies de fallback pour categorization.
"""

class FallbackCategorizer:
    """Categorizer avec cascade de fallbacks."""
    
    def categorize(self, label: str, amount: float, date) -> tuple[str, float, str]:
        """
        Categorization avec fallback.
        
        Returns:
            (category, confidence, source)
        """
        # 1. Rules (toujours premier)
        result = self._try_rules(label)
        if result:
            return (*result, 'rules')
        
        # 2. Local ML (si disponible et confiant)
        result = self._try_local_ml(label, amount, date)
        if result and result[1] >= 0.6:
            return (*result, 'local_ml')
        
        # 3. Similarite avec transactions existantes
        result = self._try_similarity(label)
        if result and result[1] >= 0.7:
            return (*result, 'similarity')
        
        # 4. Heuristiques simples
        result = self._try_heuristics(label, amount)
        if result:
            return (*result, 'heuristics')
        
        # 5. AI Cloud (dernier recours)
        if is_online():
            result = self._try_ai_cloud(label, amount, date)
            if result:
                return (*result, 'ai_cloud')
        
        return 'Inconnu', 0.0, 'default'
    
    def _try_rules(self, label: str) -> tuple[str, float] | None:
        """Essaye les regles."""
        category, confidence = apply_rules(label)
        if category:
            return category, confidence
        return None
    
    def _try_local_ml(self, label: str, amount: float, date) -> tuple[str, float] | None:
        """Essaye le ML local."""
        classifier = get_classifier()
        if classifier.is_trained:
            return classifier.predict(label, amount, date)
        return None
    
    def _try_similarity(self, label: str) -> tuple[str, float] | None:
        """Recherche transactions similaires."""
        # Trouver transactions avec libelle similaire
        similar = find_similar_transactions(label, top_n=5)
        
        if not similar:
            return None
        
        # Vote majoritaire
        categories = [tx['category_validated'] for tx in similar]
        most_common = Counter(categories).most_common(1)[0]
        
        confidence = most_common[1] / len(categories)
        
        return most_common[0], confidence
    
    def _try_heuristics(self, label: str, amount: float) -> tuple[str, float] | None:
        """Heuristiques simples."""
        label_upper = label.upper()
        
        # Heuristiques montant
        if amount > 1000:
            if any(word in label_upper for word in ['SALAIRE', 'VIREMENT']):
                return 'Revenus', 0.6
        
        if amount < -500 and 'LOYER' in label_upper:
            return 'Logement', 0.7
        
        if 'AMAZON' in label_upper or 'FNAC' in label_upper or 'CDISCOUNT' in label_upper:
            return 'Achats', 0.5
        
        return None
    
    def _try_ai_cloud(self, label: str, amount: float, date) -> tuple[str, float] | None:
        """Essaye IA cloud."""
        try:
            return predict_category_ai(label, amount, date)
        except Exception as e:
            logger.error(f"AI Cloud failed: {e}")
            return None
```

---

**Version**: 1.1 - **COMPLETED**
**Ajouts**: Auto-learning, Training pipeline, Fallback strategies, Similarity matching


---

## 🔗 Module Additionnel: Intégration AGENT-007 (AI Provider)

### Utilisation du Multi-Provider Manager

```python
"""
Intégration avec AGENT-007 pour utilisation robuste des providers IA.
Cette section définit comment AGENT-005 utilise les capacités de AGENT-007.
"""

from modules.ai.providers import MultiProviderManager, AIProvider
from modules.ai.circuit_breaker import CircuitBreaker

class CategorizationAIClient:
    """
    Client IA pour la catégorisation utilisant AGENT-007.
    
    Responsabilités:
    - Utilise MultiProviderManager pour fallback automatique
    - Respecte les rate limits définis par AGENT-007
    - Gère les erreurs via CircuitBreaker
    """
    
    def __init__(self):
        self.provider_manager = MultiProviderManager()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60
        )
    
    def categorize_with_fallback(self, label: str, amount: float, context: dict = None) -> dict:
        """
        Catégorise avec fallback multi-providers.
        
        Flow:
        1. Essayer provider primaire (Gemini)
        2. Si indisponible → provider secondaire (OpenAI)
        3. Si indisponible → provider tertiaire (DeepSeek)
        4. Si tous indisponibles → Ollama local
        5. Si échec total → retourner "Inconnu"
        
        Returns:
            {
                'category': str,
                'confidence': float,
                'provider_used': str,
                'latency_ms': float
            }
        """
        import time
        start = time.time()
        
        # Vérifier circuit breaker
        if not self.circuit_breaker.can_execute():
            logger.warning("Circuit breaker OPEN, using local fallback")
            return self._local_fallback(label, amount)
        
        # Construire prompt
        prompt = self._build_categorization_prompt(label, amount, context)
        
        try:
            # Utiliser AGENT-007 pour génération avec fallback
            result = self.provider_manager.generate_with_fallback(prompt)
            
            # Parser résultat
            parsed = self._parse_ai_response(result)
            
            # Enregistrer succès
            self.circuit_breaker.record_success()
            
            latency = (time.time() - start) * 1000
            
            return {
                'category': parsed.get('category', 'Inconnu'),
                'confidence': parsed.get('confidence', 0.5),
                'provider_used': self.provider_manager.last_used_provider,
                'latency_ms': latency
            }
            
        except Exception as e:
            # Enregistrer échec
            self.circuit_breaker.record_failure()
            logger.error(f"AI categorization failed: {e}")
            
            return self._local_fallback(label, amount)
    
    def _build_categorization_prompt(self, label: str, amount: float, context: dict = None) -> str:
        """Construit le prompt pour l'IA."""
        categories = get_categories()
        
        context_str = ""
        if context:
            context_str = f"""
Contexte additionnel:
- Historique: {context.get('similar_transactions', [])}
- Membre: {context.get('member', 'Inconnu')}
- Compte: {context.get('account', 'Inconnu')}
"""
        
        return f"""Tu es un expert en catégorisation financière française.
Analyse cette transaction et choisis la catégorie la plus appropriée.

Transaction:
- Libellé: {label}
- Montant: {amount:.2f} EUR
{context_str}

Catégories possibles: {', '.join(categories)}

Réponds UNIQUEMENT en JSON:
{{
    "category": "nom de la catégorie",
    "confidence": 0.0 à 1.0,
    "reasoning": "explication courte"
}}
"""
    
    def _parse_ai_response(self, response: str) -> dict:
        """Parse la réponse JSON de l'IA."""
        import json
        try:
            # Extraire JSON si entouré de texte
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                response = response.split('```')[1].split('```')[0]
            
            return json.loads(response.strip())
        except json.JSONDecodeError:
            logger.error(f"Failed to parse AI response: {response}")
            return {'category': 'Inconnu', 'confidence': 0.0}
    
    def _local_fallback(self, label: str, amount: float) -> dict:
        """Fallback local si tous les providers échouent."""
        # Utiliser règles simples
        category, _ = apply_rules(label)
        
        if category:
            return {
                'category': category,
                'confidence': 0.5,
                'provider_used': 'local_rules',
                'latency_ms': 1
            }
        
        return {
            'category': 'Inconnu',
            'confidence': 0.0,
            'provider_used': 'none',
            'latency_ms': 0
        }

# Singleton pour utilisation globale
_categorization_ai_client = None

def get_categorization_ai_client() -> CategorizationAIClient:
    """Retourne le client IA catégorisation (singleton)."""
    global _categorization_ai_client
    if _categorization_ai_client is None:
        _categorization_ai_client = CategorizationAIClient()
    return _categorization_ai_client
```

### Dépendances AGENT-007

```python
# requirements.txt additions for AGENT-005
# Ces dépendances sont gérées par AGENT-007 mais utilisées par AGENT-005

# AGENT-007 AI Providers
google-generativeai>=0.7.0  # Gemini
openai>=1.0.0               # OpenAI
ollama>=0.1.0               # Ollama local
```

### Coordination avec AGENT-007

| Aspect | AGENT-007 Responsabilité | AGENT-005 Utilisation |
|--------|-------------------------|----------------------|
| Provider Selection | Priorité, fallback | Appel via manager |
| Rate Limiting | Throttling, queues | Respecte limites |
| Error Handling | Circuit breaker | Gère résultat |
| Cost Tracking | Monitoring | Reçoit métriques |
| API Keys | Configuration | Utilise via abstraction |

---

**Version**: 1.1 - **COORDINATION AJOUTÉE**  
**Dépendances**: AGENT-007 (AI Provider Manager)
