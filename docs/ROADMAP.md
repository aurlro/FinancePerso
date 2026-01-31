# 🗺️ Roadmap FinancePerso - Plan d'Action Stratégique

> Ce document présente les évolutions planifiées pour l'application FinancePerso, classées par priorité et complexité.

---

## 🚨 PHASE 1: Sécurité & Robustesse (Sprint 1-2)

### 1.1 Chiffrement des données sensibles
**Priorité:** 🔴 Haute  
**Complexité:** Moyenne  
**Description:** Chiffrer les champs sensibles en base de données (notes, libellés personnalisés).

**Tâches:**
- [ ] Implémenter un chiffrement AES-256 pour les champs sensibles
- [ ] Générer et stocker la clé de chiffrement dans `.env`
- [ ] Migration des données existantes
- [ ] Fonctions utilitaires `encrypt_field()` / `decrypt_field()`

**Fichiers concernés:**
- `modules/db/transactions.py`
- `modules/db/connection.py`

---

### 1.2 Validation des entrées utilisateur
**Priorité:** 🔴 Haute  
**Complexité:** Faible  
**Description:** Ajouter une validation stricte sur tous les inputs utilisateur.

**Tâches:**
- [ ] Créer `modules/validators.py` avec des schémas Pydantic
- [ ] Valider les montants (pas de NaN, pas d'infini)
- [ ] Valider les dates (format ISO, pas de dates futures > 1 an)
- [ ] Sanitiser les libellés (XSS protection)
- [ ] Limiter la taille des champs texte (max 500 chars)

**Exemple d'implémentation:**
```python
from pydantic import BaseModel, Field, validator
from datetime import date

class TransactionInput(BaseModel):
    label: str = Field(..., min_length=1, max_length=500)
    amount: float = Field(..., gt=-1e9, lt=1e9)
    date: date
    
    @validator('label')
    def sanitize_label(cls, v):
        return html.escape(v.strip())
```

---

### 1.3 Gestion des erreurs centralisée
**Priorité:** 🟡 Moyenne  
**Complexité:** Moyenne  
**Description:** Système de gestion d'erreurs uniforme avec retry automatique.

**Tâches:**
- [ ] Créer `modules/error_handler.py`
- [ ] Décorateur `@with_retry(max_attempts=3)`
- [ ] Décorateur `@with_fallback(default_value)`
- [ ] Logging structuré avec corrélation d'ID
- [ ] Page d'erreur utilisateur friendly

---

## ⚡ PHASE 2: Performance & Scalabilité (Sprint 3-4)

### 2.1 Cache multi-niveaux
**Priorité:** 🔴 Haute  
**Complexité:** Moyenne  
**Description:** Implémenter une stratégie de cache LRU et persistant.

**Tâches:**
- [ ] Cache disque pour les données peu fréquentes (Redis ou SQLite)
- [ ] Cache mémoire LRU pour les requêtes fréquentes
- [ ] Invalidation intelligente du cache (pattern-based)
- [ ] Métriques de hit/miss rate

**Architecture proposée:**
```
UI Request → Cache Mémoire → Cache Disque → Database
                ↑                 ↑
           (1-5 min TTL)     (1-24h TTL)
```

---

### 2.2 Traitement asynchrone
**Priorité:** 🟡 Moyenne  
**Complexité:** Élevée  
**Description:** Déplacer les opérations lourdes en arrière-plan.

**Tâches:**
- [ ] File de tâches pour l'import CSV (tâches > 100 transactions)
- [ ] Catégorisation IA en batch asynchrone
- [ ] Génération de rapports en arrière-plan
- [ ] Notifications de progression (WebSocket ou polling)

**Technologies:**
- `asyncio` pour l'asynchronisme
- `aiohttp` pour les appels API
- `streamlit-server-state` pour la persistance des tâches

---

### 2.3 Optimisation des requêtes SQL
**Priorité:** 🟡 Moyenne  
**Complexité:** Moyenne  
**Description:** Indexation et optimisation des requêtes lentes.

**Tâches:**
- [ ] Analyser les requêtes lentes avec `EXPLAIN QUERY PLAN`
- [ ] Ajouter des index sur `date`, `category_validated`, `member`
- [ ] Pagination côté serveur pour les grandes listes
- [ ] Requêtes comptages optimisées (COUNT(*))

**Index à créer:**
```sql
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_category ON transactions(category_validated);
CREATE INDEX idx_transactions_member ON transactions(member);
CREATE INDEX idx_transactions_composite ON transactions(date, category_validated);
```

---

## 🎨 PHASE 3: Expérience Utilisateur (Sprint 5-6)

### 3.1 Interface responsive mobile
**Priorité:** 🔴 Haute  
**Complexité:** Moyenne  
**Description:** Adapter l'interface pour une utilisation mobile.

**Tâches:**
- [ ] Breakpoints CSS pour mobile/tablette
- [ ] Navigation adaptée (drawer menu)
- [ ] Formulaires optimisés tactile
- [ ] Upload de fichiers via appareil photo (OCR)

---

### 3.2 Mode hors-ligne (PWA)
**Priorité:** 🟡 Moyenne  
**Complexité:** Élevée  
**Description:** Fonctionnement partiel sans connexion internet.

**Tâches:**
- [ ] Service Worker pour le caching
- [ ] Synchronisation des données en différé
- [ ] Stockage local (IndexedDB) pour les transactions en attente
- [ ] Indicateur de connectivité

---

### 3.3 Personnalisation avancée
**Priorité:** 🟢 Faible  
**Complexité:** Moyenne  
**Description:** Thèmes et personnalisation de l'interface.

**Tâches:**
- [ ] Thème sombre/clair automatique
- [ ] Couleurs des catégories personnalisables
- [ ] Dashboard configurable (drag & drop widgets)
- [ ] Raccourcis clavier

---

## 🤖 PHASE 4: Intelligence Artificielle (Sprint 7-8)

### 4.1 Modèle de catégorisation local
**Priorité:** 🟡 Moyenne  
**Complexité:** Élevée  
**Description:** Entraîner un modèle léger pour la catégorisation offline.

**Tâches:**
- [ ] Collecter les données d'entraînement (transactions validées)
- [ ] Entraîner un modèle scikit-learn (TF-IDF + SVM)
- [ ] Export ONNX pour inférence rapide
- [ ] Fallback sur le modèle local si API indisponible

**Performance cible:**
- Précision > 90% sur les catégories principales
- Temps d'inférence < 10ms

---

### 4.2 Prédictions budgétaires
**Priorité:** 🟡 Moyenne  
**Complexité:** Moyenne  
**Description:** Prédire les dépenses futures et détecter les anomalies.

**Tâches:**
- [ ] Modèle de séries temporelles (Prophet ou ARIMA)
- [ ] Prévision des dépenses par catégorie
- [ ] Détection des dépassements de budget anticipés
- [ ] Alertes proactives ("Vous dépassez votre rythme habituel")

---

### 4.3 Chat IA contextuel
**Priorité:** 🟢 Faible  
**Complexité:** Moyenne  
**Description:** Assistant conversationnel avec mémoire à long terme.

**Tâches:**
- [ ] Intégration RAG (Retrieval Augmented Generation)
- [ ] Base vectorielle des transactions (embeddings)
- [ ] Contexte utilisateur persistant
- [ ] Actions via chat ("Catégorise mes dernières transactions")

---

## 🔧 PHASE 5: Intégrations & API (Sprint 9-10)

### 5.1 API REST
**Priorité:** 🟡 Moyenne  
**Complexité:** Moyenne  
**Description:** Exposer une API pour les intégrations tierces.

**Tâches:**
- [ ] Framework FastAPI
- [ ] Authentification JWT
- [ ] Rate limiting
- [ ] Documentation Swagger/OpenAPI

**Endpoints prévus:**
```
GET    /api/v1/transactions
POST   /api/v1/transactions
GET    /api/v1/categories
GET    /api/v1/stats/monthly
POST   /api/v1/import/csv
```

---

### 5.2 Connecteurs bancaires
**Priorité:** 🟡 Moyenne  
**Complexité:** Élevée  
**Description:** Connexion directe aux banques via PSD2.

**Tâches:**
- [ ] Intégration Bridge ou Budget Insight
- [ ] Authentification OAuth2
- [ ] Synchronisation automatique des transactions
- [ ] Gestion des consentements RGPD

---

### 5.3 Export/Import avancés
**Priorité:** 🟢 Faible  
**Complexité:** Faible  
**Description:** Formats d'export supplémentaires.

**Tâches:**
- [ ] Export PDF (rapports mensuels)
- [ ] Export Excel avec graphiques
- [ ] Import QIF/OFX (Quicken, Money)
- [ ] Backup chiffré automatisé (S3, Google Drive)

---

## 📊 PHASE 6: Analytics & Reporting (Sprint 11-12)

### 6.1 Tableaux de bord avancés
**Priorité:** 🟡 Moyenne  
**Complexité:** Moyenne  
**Description:** Visualisations enrichies et personnalisables.

**Tâches:**
- [ ] Graphique Sankey (flux financiers)
- [ ] Heatmap des dépenses par jour/mois
- [ ] Comparaison annuelle (YoY)
- [ ] Objectifs d'épargne avec suivi visuel

---

### 6.2 Rapports automatisés
**Priorité:** 🟢 Faible  
**Complexité:** Moyenne  
**Description:** Génération et envoi automatique de rapports.

**Tâches:**
- [ ] Rapport mensuel par email
- [ ] Alertes de dépassement de budget
- [ ] Résumé hebdomadaire (SMS/Email)
- [ ] Rapport fiscal annuel (PDF)

---

## 📋 Backlog & Idées Futures

### Fonctionnalités proposées
- [ ] **Gestion multi-utilisateur** avec permissions
- [ ] **Scanner de reçus** (OCR avec Tesseract)
- [ ] **Géolocalisation** des transactions
- [ ] **Partage de dépenses** (splitwise-like)
- [ ] **Simulation de crédit** (prêt immobilier, etc.)
- [ ] **Import automatique** des factures (email scanning)
- [ ] **Intégration calendrier** pour échéances
- [ ] **Mode vacances** (catégories temporaires)
- [ ] **Défis d'épargne** (gamification)

### Refactoring technique
- [ ] Migration vers SQLAlchemy ORM
- [ ] Tests E2E avec Playwright
- [ ] CI/CD GitHub Actions
- [ ] Conteneurisation Docker
- [ ] Migration vers PostgreSQL (option cloud)

---

## 📅 Planning Global

| Phase | Sprints | Durée estimée | Focus |
|-------|---------|---------------|-------|
| Phase 1 | 1-2 | 2-4 semaines | Sécurité, robustesse |
| Phase 2 | 3-4 | 2-4 semaines | Performance |
| Phase 3 | 5-6 | 2-4 semaines | UX/UI |
| Phase 4 | 7-8 | 2-4 semaines | IA/ML |
| Phase 5 | 9-10 | 2-4 semaines | Intégrations |
| Phase 6 | 11-12 | 2-4 semaines | Analytics |

**Total:** 12 sprints (≈ 6-12 mois selon disponibilité)

---

## 🎯 Métriques de Succès

### Performance technique
- [ ] Temps de chargement page < 2s
- [ ] Couverture de tests > 85%
- [ ] Zero erreurs critiques en production
- [ ] Uptime > 99.5%

### Satisfaction utilisateur
- [ ] NPS (Net Promoter Score) > 50
- [ ] Temps moyen de validation < 30 min/semaine
- [ ] Taux de rétention > 80% (utilisateurs actifs après 3 mois)

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour proposer une fonctionnalité :

1. Créer une issue GitHub avec le label `enhancement`
2. Discuter de l'implémentation avec les maintainers
3. Suivre les guidelines de contribution (AGENTS.md)

---

**Dernière mise à jour:** 2026-01-31  
**Prochaine review:** 2026-02-28
