# 🗺️ Roadmap FinancePerso - Plan Stratégique de Développement

> Ce document présente la feuille de route complète de l'application FinancePerso sur 12-18 mois, organisée en 6 phases thématiques.

---

## 📋 Vue d'ensemble

| Phase | Thème | Durée | Sprint | Statut |
|-------|-------|-------|--------|--------|
| Phase 1 | 🔒 Sécurité & Robustesse | 4-6 semaines | 1-2 | 🟡 En cours |
| Phase 2 | ⚡ Performance & Scalabilité | 4-6 semaines | 3-4 | ⚪ Planifié |
| Phase 3 | 🎨 Expérience Utilisateur | 4-6 semaines | 5-6 | ⚪ Planifié |
| Phase 4 | 🤖 Intelligence Artificielle | 6-8 semaines | 7-9 | ⚪ Planifié |
| Phase 5 | 🔌 Intégrations & API | 6-8 semaines | 10-12 | ⚪ Planifié |
| Phase 6 | 📊 Analytics Avancés | 4-6 semaines | 13-14 | ⚪ Planifié |

**Durée totale estimée :** 12-18 mois  
**Métrique de succès :** Couverture tests >85%, Temps de chargement <2s, NPS >50

---

## 🔒 PHASE 1 : Sécurité & Robustesse

**Durée :** 4-6 semaines  
**Sprints :** 1-2  
**Priorité :** 🔴 Critique

### 1.1 Chiffrement AES-256 des données sensibles

**Objectif :** Protéger les données confidentielles en base de données

**Tâches détaillées :**
- [ ] Créer `modules/encryption.py` avec chiffrement AES-256-GCM
- [ ] Générer clé maître via ` Fernet.generate_key()` ou dérivée de mot de passe
- [ ] Chiffrer les champs sensibles : `notes`, `labels_personnalisés`, `beneficiary`
- [ ] Migration transparente des données existantes (chiffrement à la volée)
- [ ] Fonctions utilitaires : `encrypt_field()`, `decrypt_field()`, `rotate_key()`

**Implémentation proposée :**
```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class FieldEncryption:
    def __init__(self, master_key: str):
        self.cipher = Fernet(self._derive_key(master_key))
    
    def encrypt(self, plaintext: str) -> str:
        return self.cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        return self.cipher.decrypt(ciphertext.encode()).decode()
```

**Fichiers concernés :**
- `modules/encryption.py` (nouveau)
- `modules/db/transactions.py` (modification requêtes)
- `modules/db/migrations.py` (migration données)

**Critères d'acceptation :**
- [ ] Les notes sont chiffrées en base
- [ ] Performance : <10ms par opération de chiffrement
- [ ] Tests : 100% couverture du module encryption

---

### 1.2 Validation Pydantic des inputs

**Objectif :** Validation stricte et uniforme de toutes les entrées utilisateur

**Tâches détaillées :**
- [x] ✅ Créer `modules/validators.py` avec schémas Pydantic v2
- [x] ✅ Implémenter `TransactionInput`, `CategoryInput`, `LearningRuleInput`
- [ ] Intégrer validation dans les pages Streamlit
- [ ] Ajouter messages d'erreur en français
- [ ] Validation côté client (JavaScript) pour UX fluide

**Schémas à implémenter :**
```python
class TransactionInput(BaseModel):
    label: str = Field(..., min_length=1, max_length=500)
    amount: float = Field(..., gt=-1e9, lt=1e9)
    date: date
    category: Optional[str] = Field(None, max_length=100)
```

**Validation métier :**
- Montant réaliste (-1M à +1M €)
- Dates entre 2000 et +1 an
- Labels sans injection XSS
- Catégories sans mots réservés

**Fichiers concernés :**
- `modules/validators.py` (existe ✅)
- `pages/1_Import.py` (intégration)
- `pages/2_Validation.py` (intégration)

---

### 1.3 Gestion d'erreurs centralisée

**Objectif :** Système robuste de gestion des erreurs avec retry et fallback

**Tâches détaillées :**
- [x] ✅ Créer `modules/error_tracking.py` avec Sentry
- [x] ✅ Implémenter décorateurs `@with_retry`, `@with_fallback`
- [ ] Configurer Sentry DSN en production
- [ ] Page d'erreur utilisateur friendly (404, 500, maintenance)
- [ ] Alerting Slack/Email pour erreurs critiques

**Décorateurs disponibles :**
```python
@with_retry(max_attempts=3, exceptions=(RequestException,))
def call_ai_api(prompt):
    pass

@with_fallback(default_value=[])
def get_recommendations():
    pass
```

**Niveaux d'erreur :**
- 🟢 INFO : Logs normaux
- 🟡 WARNING : Échec retry, fallback utilisé
- 🟠 ERROR : Erreur utilisateur (affichée)
- 🔴 CRITICAL : Erreur système (alerte admin)

**Fichiers concernés :**
- `modules/error_tracking.py` (existe ✅)
- `pages/98_Tests.py` (page d'erreur)

---

### 1.4 Authentification & Autorisation (Optionnel)

**Objectif :** Sécuriser l'accès à l'application

**Tâches détaillées :**
- [ ] Authentification par mot de passe (bcrypt)
- [ ] Sessions sécurisées avec JWT
- [ ] Rôles : admin, utilisateur, lecture seule
- [ ] 2FA (TOTP) pour accès sensible

---

## ⚡ PHASE 2 : Performance & Scalabilité

**Durée :** 4-6 semaines  
**Sprints :** 3-4  
**Priorité :** 🟠 Haute

### 2.1 Cache multi-niveaux

**Objectif :** Réduire les requêtes DB et accélérer les temps de réponse

**Architecture cible :**
```
Requête → Cache Mémoire (5 min) → Cache Disque (1h) → Database
```

**Tâches détaillées :**
- [ ] Implémenter `modules/cache_multitier.py`
- [ ] Cache LRU en mémoire pour données fréquentes
- [ ] Cache disque SQLite pour données persistantes
- [ ] Invalidation intelligente par pattern (clés type `transactions:*`)
- [ ] Métriques : hit rate, miss rate, temps moyen

**Stratégie de cache :**
| Donnée | TTL Mémoire | TTL Disque | Invalidation |
|--------|-------------|------------|--------------|
| Catégories | 5 min | 24h | Manuelle |
| Règles | 5 min | 1h | Sur modification |
| Stats mensuelles | 1 min | 5 min | Périodique |
| Transactions | Non | Non | Jamais (données brutes) |

**Implémentation :**
```python
from functools import lru_cache
import diskcache

class MultiTierCache:
    def __init__(self):
        self.memory = {}  # Dict simple avec TTL
        self.disk = diskcache.Cache('Data/cache')
    
    def get(self, key, fetch_func, ttl_memory=300, ttl_disk=3600):
        # Logique de récupération multi-niveaux
        pass
```

---

### 2.2 Traitement asynchrone

**Objectif :** Déplacer les opérations lourdes en arrière-plan

**Tâches détaillées :**
- [ ] Intégrer `asyncio` pour les I/O non-bloquants
- [ ] File de tâches pour imports CSV >100 transactions
- [ ] Progress bar temps réel via WebSocket ou polling
- [ ] Gestionnaire de tâches avec `celery` ou `arq`

**Opérations à rendre asynchrones :**
1. Import CSV volumineux (analyse + catégorisation)
2. Génération de rapports PDF
3. Audit IA complet (analyse de toutes les transactions)
4. Export de données (CSV, Excel)

**Workflow import async :**
```python
async def process_import(file_path, account_id):
    # 1. Validation rapide (sync)
    validate_csv(file_path)
    
    # 2. Traitement async avec progress
    total_rows = count_rows(file_path)
    for batch in read_batches(file_path):
        await categorize_batch(batch)
        update_progress(current=len(batch), total=total_rows)
    
    # 3. Notification fin
    send_notification(f"Import {total_rows} transactions terminé")
```

---

### 2.3 Optimisation SQL

**Objectif :** Indexation et requêtes optimisées

**Tâches détaillées :**
- [ ] Analyse `EXPLAIN QUERY PLAN` sur requêtes lentes
- [ ] Créer index composites stratégiques
- [ ] Pagination côté serveur (LIMIT/OFFSET)
- [ ] Comptages optimisés avec tables de statistiques

**Index à créer :**
```sql
-- Index de base
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_category ON transactions(category_validated);
CREATE INDEX idx_transactions_member ON transactions(member);

-- Index composites
CREATE INDEX idx_tx_date_category ON transactions(date, category_validated);
CREATE INDEX idx_tx_status_date ON transactions(status, date);
CREATE INDEX idx_tx_account_date ON transactions(account_label, date);

-- Index pour recherche texte (future)
-- CREATE VIRTUAL TABLE transactions_fts USING fts5(label, content=transactions);
```

**Optimisations requêtes :**
```sql
-- Avant (lent sur grandes tables)
SELECT * FROM transactions ORDER BY date DESC LIMIT 10;

-- Après (avec index couvrant)
SELECT date, label, amount, category_validated 
FROM transactions 
WHERE date >= date('now', '-1 month')
ORDER BY date DESC 
LIMIT 10;
```

---

### 2.4 Compression et Archivage

**Objectif :** Gérer la croissance de la base de données

**Tâches détaillées :**
- [ ] Compression automatique des transactions >2 ans
- [ ] Archivage mensuel en fichiers parquet
- [ ] Requêtes cross-archive (Vue unifiée)
- [ ] Politique de rétention configurable

---

## 🎨 PHASE 3 : Expérience Utilisateur

**Durée :** 4-6 semaines  
**Sprints :** 5-6  
**Priorité :** 🟡 Moyenne

### 3.1 Interface Mobile Responsive

**Objectif :** Utilisation fluide sur smartphone et tablette

**Tâches détaillées :**
- [ ] Breakpoints CSS : Mobile (<768px), Tablet (768-1024px), Desktop (>1024px)
- [ ] Navigation adaptée (drawer menu sur mobile)
- [ ] Formulaires optimisés tactile (inputs plus grands)
- [ ] Upload par appareil photo avec OCR (reçus)

**Design mobile :**
```css
/* Mobile first */
@media (max-width: 768px) {
  .sidebar { display: none; }
  .mobile-nav { display: flex; }
  .transaction-card { width: 100%; }
  .validate-button { min-height: 44px; }
}
```

**Composants mobiles :**
- Bottom navigation bar (5 icônes principales)
- Swipe actions sur transactions (glisser pour valider)
- Pull to refresh sur listes
- Infinite scroll pour historique

---

### 3.2 Mode Hors-Ligne (PWA)

**Objectif :** Fonctionnement partiel sans connexion internet

**Tâches détaillées :**
- [ ] Service Worker pour caching des assets
- [ ] Manifest.json pour installation app
- [ ] IndexedDB pour stockage local des transactions
- [ ] Synchronisation différée (sync when online)
- [ ] Indicateur de connectivité

**Architecture PWA :**
```
┌─────────────────┐
│   Service Worker │
│  (Cache strategie)│
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│ Cache  │ │ IndexedDB │
│ Assets │ │ (Offline) │
└────────┘ └──────────┘
```

**Stratégie de cache :**
- **Cache First :** Assets statiques (CSS, JS, images)
- **Network First :** Données temps réel (budgets actuels)
- **Stale While Revalidate :** Données historiques

---

### 3.3 Personnalisation Avancée

**Objectif :** Adapter l'interface aux préférences utilisateur

**Tâches détaillées :**
- [ ] Thème sombre/clair automatique (selon heure ou préférence système)
- [ ] Couleurs des catégories personnalisables
- [ ] Dashboard configurable (drag & drop widgets)
- [ ] Raccourcis clavier personnalisables
- [ ] Langue (FR/EN/ES)

**Personnalisation thème :**
```python
theme_config = {
    'primary_color': '#22c55e',
    'background': '#0f172a',
    'card_background': '#1e293b',
    'text_primary': '#f8fafc',
    'category_colors': {
        'Alimentation': '#ef4444',
        'Transport': '#3b82f6',
        # ...
    }
}
```

---

### 3.4 Onboarding Amélioré

**Objectif :** Guidage interactif pour nouveaux utilisateurs

**Tâches détaillées :**
- [ ] Tour guidé interactif (shepherd.js)
- [ ] Import guidé étape par étape
- [ ] Configuration assistée automatique
- [ ] Tutoriels vidéo embarqués

---

## 🤖 PHASE 4 : Intelligence Artificielle

**Durée :** 6-8 semaines  
**Sprints :** 7-9  
**Priorité :** 🟡 Moyenne

### 4.1 Modèle de Catégorisation Local

**Objectif :** Catégorisation offline sans dépendance API externe

**Tâches détaillées :**
- [ ] Collecter dataset d'entraînement (transactions validées)
- [ ] Prétraitement : TF-IDF sur libellés
- [ ] Entraîner modèle SVM ou Random Forest
- [ ] Export ONNX pour inférence rapide
- [ ] Fallback automatique si API indisponible

**Pipeline ML :**
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline

# Entraînement
model = Pipeline([
    ('tfidf', TfidfVectorizer(ngram_range=(1, 2))),
    ('svm', SVC(probability=True))
])
model.fit(X_labels, y_categories)

# Export ONNX
import skl2onnx
onnx_model = skl2onnx.convert_sklearn(model, ...)
```

**Performance cible :**
- Précision >90% sur top 10 catégories
- Temps d'inférence <10ms
- Taille modèle <10MB

---

### 4.2 Prédictions Budgétaires

**Objectif :** Anticiper les dépenses et détecter les anomalies

**Tâches détaillées :**
- [ ] Implémenter modèle Prophet (Facebook) pour prévisions
- [ ] Prédire dépenses par catégorie pour mois suivant
- [ ] Détecter dépassements de budget anticipés
- [ ] Alertes proactives personnalisées

**Prévisions Prophet :**
```python
from prophet import Prophet

df = pd.DataFrame({
    'ds': transaction_dates,
    'y': daily_amounts
})

model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True
)
model.fit(df)

future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)
```

**Alertes intelligentes :**
- "À ce rythme, vous dépasserez votre budget Alimentation de 15%"
- "Dépense inhabituelle détectée : 200€ chez Électronique"
- "Virement récurrent manquant : Salaire attendu"

---

### 4.3 Chat IA Contextuel avec RAG

**Objectif :** Assistant conversationnel avec mémoire des transactions

**Tâches détaillées :**
- [ ] Vectorisation des transactions (embeddings OpenAI/Gemini)
- [ ] Base vectorielle locale (ChromaDB ou FAISS)
- [ ] Retrieval Augmented Generation (RAG)
- [ ] Actions via chat naturel

**Architecture RAG :**
```
Question utilisateur
        ↓
  Embedding
        ↓
Recherche similarité → Transactions pertinentes
        ↓
   Prompt enrichi
        ↓
    LLM API
        ↓
   Réponse
```

**Exemples d'interactions :**
- "Combien ai-je dépensé en restaurants ce mois-ci ?"
- "Compare mes dépenses essence avec janvier dernier"
- "Quelles sont mes abonnements récurrents ?"
- "Catégorise mes 10 dernières transactions en attente"

---

### 4.4 Détection d'Anomalies Avancée

**Objectif :** Identifier les transactions suspectes ou inhabituelles

**Tâches détaillées :**
- [ ] Algorithme Isolation Forest pour outliers
- [ ] Détection de doublons intelligente (fuzzy matching)
- [ ] Alertes fraude (montants inhabituels, horaires suspects)
- [ ] Tableau de bord anomalies

---

## 🔌 PHASE 5 : Intégrations & API

**Durée :** 6-8 semaines  
**Sprints :** 10-12  
**Priorité :** 🟢 Faible à moyenne

### 5.1 API REST (FastAPI)

**Objectif :** Exposer une API publique pour intégrations tierces

**Tâches détaillées :**
- [ ] Monter serveur FastAPI parallèle à Streamlit
- [ ] Authentification JWT (OAuth2)
- [ ] Rate limiting (100 req/min par défaut)
- [ ] Documentation Swagger/OpenAPI auto-générée
- [ ] Versioning API (v1, v2)

**Endpoints prévus :**
```yaml
/api/v1/transactions:
  GET:    Lister les transactions (pagination)
  POST:   Créer une transaction
  
/api/v1/transactions/{id}:
  GET:    Détail transaction
  PUT:    Modifier transaction
  DELETE: Supprimer transaction

/api/v1/categories:
  GET:    Lister catégories
  
/api/v1/stats:
  GET:    Statistiques mensuelles
  
/api/v1/import/csv:
  POST:   Import CSV
  
/api/v1/export:
  GET:    Export données (JSON/CSV)
```

**Exemple d'utilisation :**
```bash
curl -X GET "https://api.financeperso.local/v1/transactions?start_date=2024-01-01&limit=100" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

---

### 5.2 Connecteurs Bancaires PSD2

**Objectif :** Synchronisation automatique des comptes bancaires

**Tâches détaillées :**
- [ ] Intégration Bridge API ou Budget Insight
- [ ] Authentification OAuth2 bancaire
- [ ] Synchronisation périodique (quotidienne)
- [ ] Gestion des consentements RGPD
- [ ] Support multi-banques (principales banques françaises)

**Flux PSD2 :**
```
Utilisateur
    ↓
Sélection banque
    ↓
Redirection auth banque
    ↓
Consentement (90-180 jours)
    ↓
Récupération transactions
    ↓
Import automatique
```

**Banques supportées :**
- BoursoBank (via Bridge)
- BNP Paribas
- Société Générale
- Crédit Agricole
- Hello bank!
- N26, Revolut (via Open Banking)

---

### 5.3 Export/Import Avancés

**Objectif :** Formats d'export riches et imports universels

**Tâches détaillées :**
- [ ] Export PDF avec graphiques (ReportLab ou WeasyPrint)
- [ ] Export Excel avec formules et styles
- [ ] Import QIF/OFX (Quicken, Microsoft Money)
- [ ] Backup chiffré automatisé (S3, Google Drive, Dropbox)
- [ ] API webhook pour intégrations (Zapier, Make)

**Export PDF :**
- Rapport mensuel stylisé
- Tableaux de dépenses par catégorie
- Graphiques intégrés
- Signature numérique (optionnel)

---

## 📊 PHASE 6 : Analytics Avancés

**Durée :** 4-6 semaines  
**Sprints :** 13-14  
**Priorité :** 🟢 Faible

### 6.1 Dashboards Personnalisables

**Objectif :** Widgets configurables par l'utilisateur

**Tâches détaillées :**
- [ ] Système de widgets (grid layout)
- [ ] Drag & drop pour réorganiser
- [ ] Widgets disponibles : KPI, graphiques, listes, calendrier
- [ ] Sauvegarde configuration par utilisateur
- [ ] Templates prédéfinis ("Vue famille", "Vue investissement")

**Widgets prévus :**
- Solde évolutif (line chart)
- Répartition dépenses (pie/donut)
- Top dépenses du mois (bar chart)
- Prochaines échéances (liste)
- Budget vs Réel (bullet chart)
- Objectifs d'épargne (progress bars)

---

### 6.2 Rapports Automatisés

**Objectif :** Génération et envoi périodique de rapports

**Tâches détaillées :**
- [ ] Templates de rapports personnalisables
- [ ] Envoi email périodique (mensuel/hebdomadaire)
- [ ] Format PDF et HTML
- [ ] Résumé vocal (TTS) pour rapports audio
- [ ] Planificateur de tâches intégré

**Types de rapports :**
- Rapport mensuel complet (PDF 5-10 pages)
- Résumé hebdomadaire (email HTML)
- Alerte dépassement budget (SMS/push)
- Bilan fiscal annuel (PDF officiel)

---

### 6.3 Visualisations Avancées

**Objectif :** Graphiques sophistiqués pour analyse approfondie

**Tâches détaillées :**
- [ ] Graphique Sankey (flux financiers entrants/sortants)
- [ ] Heatmap calendrier des dépenses
- [ ] Comparaison annuelle YoY (Year over Year)
- [ ] Treemap hiérarchique des catégories
- [ ] Graphique waterfall (cascades de trésorerie)

**Sankey Diagram :**
```
Salaire ──┬──► Alimentation ──► Courses
          ├──► Logement ─────► Loyer
          ├──► Transport ────► Essence
          └──► Épargne ──────► Livret A
```

**Heatmap calendrier :**
- Chaque jour = case colorée selon montant dépensé
- Permet de visualiser les habitudes de dépense
- Identification des jours de forte consommation

---

## 📈 Métriques de Succès Globales

### Performance technique
| Métrique | Cible | Actuel | Deadline |
|----------|-------|--------|----------|
| Temps de chargement page | <2s | ~3s | Phase 2 |
| Couverture tests | >85% | ~72% | Phase 4 |
| Uptime | >99.5% | N/A | Phase 1 |
| Temps réponse API | <200ms | N/A | Phase 5 |

### Satisfaction utilisateur
| Métrique | Cible | Méthode de mesure |
|----------|-------|-------------------|
| NPS (Net Promoter Score) | >50 | Questionnaire trimestriel |
| Temps validation hebdo | <30 min | Analytics in-app |
| Taux rétention (3 mois) | >80% | Cohort analysis |
| Score App Store | >4.5/5 | Reviews |

---

## 🛠️ Stack Technique Évolution

### Actuel
- **Backend :** Python 3.12, Streamlit, SQLite
- **Frontend :** Streamlit natif, CSS custom
- **ML/IA :** Google Gemini API
- **Tests :** pytest

### Futur (par phase)
| Phase | Ajouts technologiques |
|-------|----------------------|
| Phase 1 | cryptography (AES), pydantic ✅ |
| Phase 2 | diskcache, asyncio, aiohttp |
| Phase 3 | PWA (Service Workers), IndexedDB |
| Phase 4 | scikit-learn, Prophet, ChromaDB, ONNX |
| Phase 5 | FastAPI, OAuth2, Bridge API |
| Phase 6 | ReportLab, Plotly advanced, Celery |

---

## 📅 Planning Détaillé

### 2024 - Fondations
- **Q1 :** Phase 1 (Sécurité) + Phase 2 (Performance)
- **Q2 :** Phase 3 (UX) + Début Phase 4 (IA)
- **Q3 :** Phase 4 (IA) + Phase 5 (Intégrations)
- **Q4 :** Phase 6 (Analytics) + Optimisations

### 2025 - Expansion
- **Q1 :** Mobile App (React Native ou Flutter)
- **Q2 :** Multi-utilisateurs, cloud sync
- **Q3 :** Marketplace d'intégrations
- **Q4 :** Internationalisation (EN, ES, DE)

---

## 🤝 Contribution & Feedback

### Comment proposer une fonctionnalité
1. Créer une issue GitHub avec label `enhancement`
2. Décrire le cas d'usage et la valeur utilisateur
3. Discuter de l'implémentation avec les maintainers
4. Soumettre une PR suivant les guidelines

### Suivi de la roadmap
- **Review trimestrielle** des priorités
- **Mise à jour** de ce document après chaque phase
- **Retours utilisateurs** intégrés via formulaire in-app

---

## 📚 Ressources

### Documentation
- [Architecture Technique](./ARCHITECTURE.md)
- [Guide Contributeur](./CONTRIBUTING.md)
- [Changelog](../CHANGELOG.md)
- [API Reference](./API.md) (à venir Phase 5)

### Outils de planification
- GitHub Projects pour le kanban
- Milestones pour les releases
- Discussions GitHub pour les décisions architecturales

---

**Dernière mise à jour :** 2026-01-31  
**Prochaine review :** 2026-04-30  
**Responsable roadmap :** Équipe Core FinancePerso

---

> *"La meilleure façon de prédire l'avenir est de le créer."* — Alan Kay
