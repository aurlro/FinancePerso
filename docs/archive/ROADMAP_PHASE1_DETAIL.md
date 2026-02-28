# 🚀 ROADMAP PHASE 1: FONDATIONS (Semaines 1-4)

> **Objectif**: Stabiliser l'application existante pour avoir une base solide

---

## 📅 SEMAINE 1: PERFORMANCE & STABILITÉ

### Jour 1-2: Audit et Profilage
**Responsable**: Développeur Backend

#### Tâches:
- [ ] **T1.1** - Exécuter un profilage complet de l'application
  ```python
  # Utiliser cProfile pour identifier les goulots d'étranglement
  python -m cProfile -o profile_stats.prof app.py
  ```
- [ ] **T1.2** - Identifier les 10 requêtes SQL les plus lentes
  - Outil: SQLite `EXPLAIN QUERY PLAN`
  - Fichiers à analyser: `modules/db/transactions.py`, `modules/db/stats.py`
- [ ] **T1.3** - Mesurer les temps de chargement par page
  - Dashboard (app.py)
  - Synthèse (pages/3_Synthèse.py)
  - Intelligence (pages/4_Intelligence.py)
  - Opérations (pages/1_Opérations.py)

#### Livrable:
- Rapport de performance avec graphiques (avant/après)
- Liste priorisée des optimisations

---

### Jour 3-4: Optimisation Base de Données
**Responsable**: Développeur Backend

#### Tâches:
- [ ] **T2.1** - Créer les index manquants
  ```sql
  -- Index pour requêtes fréquentes
  CREATE INDEX IF NOT EXISTS idx_transactions_date_category ON transactions(date, category_validated);
  CREATE INDEX IF NOT EXISTS idx_transactions_member ON transactions(member_id);
  CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
  CREATE INDEX IF NOT EXISTS idx_transactions_hash ON transactions(tx_hash);
  ```
- [ ] **T2.2** - Optimiser la fonction `get_all_transactions()`
  - Ajouter pagination par défaut (limit 1000)
  - Paramètre `date_range` optionnel
  - Lazy loading pour les grandes tables
- [ ] **T2.3** - Caching des résultats fréquents
  ```python
  @st.cache_data(ttl=300)  # 5 minutes
  def get_cached_stats():
      return get_global_stats()
  ```

#### Fichiers modifiés:
- `modules/db/connection.py`
- `modules/db/transactions.py`
- `modules/db/stats.py`

#### Tests:
- [ ] Temps de requête < 100ms pour 1000 transactions
- [ ] Temps de chargement dashboard < 2s

---

### Jour 5: Pagination et Lazy Loading
**Responsable**: Développeur Frontend

#### Tâches:
- [ ] **T3.1** - Composant `PaginatedDataFrame`
  ```python
  def paginated_dataframe(df, page_size=50, key="pagination"):
      total_pages = len(df) // page_size + 1
      page = st.number_input("Page", 1, total_pages, 1, key=f"{key}_page")
      start = (page - 1) * page_size
      end = start + page_size
      return df.iloc[start:end]
  ```
- [ ] **T3.2** - Intégrer dans les pages critiques
  - Validation (pages/1_Opérations.py)
  - Recherche (pages/8_Recherche.py)
- [ ] **T3.3** - Lazy loading pour les graphiques
  - Ne pas charger tous les graphiques en même temps
  - Utiliser `st.tabs()` avec chargement à la demande

#### Fichiers modifiés:
- `modules/ui/components/pagination.py` (nouveau)
- `pages/1_Opérations.py`
- `pages/8_Recherche.py`

---

## 📅 SEMAINE 2: IMPORT & VALIDATION

### Jour 1-2: Refactoring Parser CSV
**Responsable**: Développeur Fullstack

#### Tâches:
- [ ] **T4.1** - Architecture plugin pour parsers
  ```python
  class BankParser(ABC):
      @abstractmethod
      def detect(self, file_path) -> bool:
          """Détecte si ce parser peut gérer le fichier"""
          pass
      
      @abstractmethod
      def parse(self, file_path) -> pd.DataFrame:
          """Parse le fichier et retourne un DataFrame standardisé"""
          pass
  ```
- [ ] **T4.2** - Détection automatique du format
  - Analyser les en-têtes CSV
  - Détecter le séparateur (;, ,, tab)
  - Identifier la banque par patterns
- [ ] **T4.3** - Fallback intelligent
  - Si parsing échoue, proposer mapping manuel
  - Sauvegarder le mapping pour prochaine fois

#### Fichiers modifiés:
- `modules/ingestion.py` (refactoring majeur)
- `modules/parsers/` (nouveau répertoire)
  - `base.py`
  - `bnp.py`, `sg.py`, `ca.py`, etc.
  - `auto_detect.py`

---

### Jour 3-4: Preview d'Import
**Responsable**: Développeur Frontend

#### Tâches:
- [ ] **T5.1** - Écran de preview avant import
  ```
  ┌─────────────────────────────────────┐
  │ 📊 Import Preview                   │
  ├─────────────────────────────────────┤
  │ Fichier: releve_2024_01.csv        │
  │ Banque détectée: BNP Paribas       │
  │ Transactions trouvées: 42          │
  ├─────────────────────────────────────┤
  │ Aperçu (5 premières lignes):       │
  │ ... table ...                      │
  ├─────────────────────────────────────┤
  │ ⚠️  Doublons potentiels: 3         │
  │ ✅ Nouvelles transactions: 39      │
  ├─────────────────────────────────────┤
  │ [⬅️ Corriger]  [✅ Confirmer Import]│
  └─────────────────────────────────────┘
  ```
- [ ] **T5.2** - Détection des doublons avant import
  - Comparer avec transactions existantes (tx_hash)
  - Afficher les doublons détectés
  - Option "Ignorer les doublons"
- [ ] **T5.3** - Mapping manuel des colonnes
  - Interface drag-and-drop des colonnes
  - Preview en temps réel
  - Sauvegarde du mapping

#### Fichiers modifiés:
- `modules/ui/importing/main.py` (refactoring)
- `modules/ui/importing/preview.py` (nouveau)
- `modules/ui/importing/mapping.py` (nouveau)

---

### Jour 5: Feedback et Progression
**Responsable**: Développeur Frontend

#### Tâches:
- [ ] **T6.1** - Barre de progression détaillée
  ```python
  with st.progress(0) as progress_bar:
      for i, step in enumerate(steps):
          progress_bar.progress((i + 1) / len(steps))
          st.text(f"Étape {i+1}/{len(steps)}: {step['label']}")
  ```
- [ ] **T6.2** - Étapes d'import visibles
  1. Lecture du fichier
  2. Détection du format
  3. Parsing des transactions
  4. Détection des doublons
  5. Catégorisation automatique
  6. Enregistrement
- [ ] **T6.3** - Résumé post-import
  - Nombre de transactions importées
  - Nombre de catégories assignées
  - Alertes éventuelles
  - Lien vers validation

#### Fichiers modifiés:
- `modules/ui/components/loading_states.py`
- `modules/ui/importing/main.py`

---

## 📅 SEMAINE 3: SAUVEGARDE & SÉCURITÉ

### Jour 1-2: Backup Automatique
**Responsable**: Développeur Backend

#### Tâches:
- [ ] **T7.1** - Système de backup automatique
  ```python
  def create_backup():
      timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
      backup_path = f"Data/backups/finance_{timestamp}.db"
      shutil.copy("Data/finance.db", backup_path)
      # Garder seulement les 10 derniers backups
      cleanup_old_backups(keep=10)
  ```
- [ ] **T7.2** - Planification quotidienne
  - Backup à 3h du matin
  - Si fichier a changé depuis dernier backup
  - Notification en cas d'échec
- [ ] **T7.3** - Interface de gestion des backups
  - Liste des backups disponibles
  - Téléchargement
  - Restauration (avec confirmation)
  - Suppression

#### Fichiers modifiés:
- `modules/backup_manager.py` (amélioration)
- `modules/ui/config/backup_restore.py`

---

### Jour 3: Corbeille (Soft Delete)
**Responsable**: Développeur Backend

#### Tâches:
- [ ] **T8.1** - Système de corbeille
  ```sql
  -- Nouvelle table
  CREATE TABLE deleted_transactions (
      id INTEGER PRIMARY KEY,
      original_id INTEGER,
      data JSON,  -- Transaction complète
      deleted_at TIMESTAMP,
      deleted_by TEXT,
      expires_at TIMESTAMP  -- Suppression définitive après 30j
  );
  ```
- [ ] **T8.2** - Modification des suppressions
  - `delete_transaction()` → déplace vers corbeille
  - `restore_transaction()` → restaure depuis corbeille
  - `purge_old_deleted()` → suppression définitive après 30j
- [ ] **T8.3** - Interface corbeille
  - Liste des transactions supprimées
  - Restauration (avec undo possible)
  - Suppression définitive

#### Fichiers modifiés:
- `modules/db/transactions.py`
- `modules/db/migrations.py` (nouvelle migration)
- `modules/ui/components/` (interface corbeille)

---

### Jour 4-5: Export de Données
**Responsable**: Développeur Fullstack

#### Tâches:
- [ ] **T9.1** - Export CSV complet
  - Toutes les transactions
  - Filtres possibles (date, catégorie, membre)
  - Format compatible import
- [ ] **T9.2** - Export Excel avec onglets
  - Onglet Transactions
  - Onglet Catégories
  - Onglet Budgets
  - Onglet Statistiques
- [ ] **T9.3** - Export JSON (pour développeurs)
  - Format complet avec métadonnées
  - Option anonymisée (sans données sensibles)

#### Fichiers modifiés:
- `modules/export.py` (nouveau)
- `modules/ui/config/data_operations.py`

---

## 📅 SEMAINE 4: TESTS & DOCUMENTATION

### Jour 1-2: Tests Automatisés
**Responsable**: QA / Développeur

#### Tâches:
- [ ] **T10.1** - Tests unitaires modules critiques
  ```python
  # modules/db/test_transactions.py
  def test_get_transactions_pagination():
      # Test pagination
      pass
  
  def test_transaction_crud():
      # Test CRUD complet
      pass
  ```
- [ ] **T10.2** - Tests d'intégration import
  - Test avec différents fichiers CSV
  - Test gestion d'erreurs
  - Test détection doublons
- [ ] **T10.3** - Tests de performance
  - Temps de réponse < 100ms pour requêtes courantes
  - Import de 1000 transactions < 10s

#### Fichiers créés/modifiés:
- `tests/db/test_transactions.py`
- `tests/test_ingestion.py`
- `tests/test_performance.py`

---

### Jour 3-4: Documentation
**Responsable**: Technical Writer / Développeur

#### Tâches:
- [ ] **T11.1** - Documentation utilisateur
  - Guide de démarrage rapide
  - FAQ des problèmes courants
  - Guide de résolution des erreurs d'import
- [ ] **T11.2** - Documentation technique
  - Architecture des modules
  - Guide de contribution
  - Standards de code
- [ ] **T11.3** - Guide de troubleshooting
  ```
  ## Problème: Import échoue
  ### Symptômes: ...
  ### Causes possibles: ...
  ### Solutions: ...
  ```

#### Fichiers créés:
- `docs/USER_GUIDE.md`
- `docs/ARCHITECTURE.md`
- `docs/TROUBLESHOOTING.md`

---

### Jour 5: Revue et Stabilisation
**Responsable**: Équipe complète

#### Tâches:
- [ ] **T12.1** - Revue de code
  - Pair review des changements majeurs
  - Audit de sécurité
  - Vérification des performances
- [ ] **T12.2** - Tests manuels
  - Parcours complet (onboarding à utilisation)
  - Tests avec données réelles (anonymisées)
  - Tests sur différents navigateurs
- [ ] **T12.3** - Mise à jour du CHANGELOG
  ```markdown
  ## [5.3.0] - Phase 1: Fondations
  ### Améliorations
  - Performance: Pagination des transactions
  - Import: Preview avant import
  - Sécurité: Backup automatique
  - UX: Feedback de progression
  ```

#### Livrables:
- Code review validée
- Rapport de tests
- CHANGELOG mis à jour

---

## ✅ CHECKLIST DE VALIDATION PHASE 1

### Performance
- [ ] Temps de chargement dashboard < 2s
- [ ] Requêtes SQL < 100ms
- [ ] Import 1000 transactions < 10s
- [ ] Mémoire < 500MB en utilisation normale

### Fiabilité
- [ ] Backup automatique quotidien fonctionnel
- [ ] Corbeille opérationnelle (soft delete)
- [ ] Export de données testé
- [ ] Gestion d'erreurs robuste

### Import
- [ ] Preview avant import fonctionnelle
- [ ] Détection automatique des formats
- [ ] Mapping manuel possible
- [ ] Progression visible
- [ ] Résumé post-import

### Tests
- [ ] Couverture de tests > 60%
- [ ] Tests de performance passent
- [ ] Tests d'intégration import passent
- [ ] Tests manuels validés

### Documentation
- [ ] Guide utilisateur à jour
- [ ] Guide de troubleshooting complet
- [ ] Documentation technique à jour
- [ ] CHANGELOG mis à jour

---

## 📊 MÉTRIQUES DE SUCCÈS

### Avant / Après

| Métrique | Avant | Objectif Après |
|----------|-------|----------------|
| Temps chargement dashboard | 5-8s | < 2s |
| Temps import 1000 tx | 30s+ | < 10s |
| Requête SQL moyenne | 500ms+ | < 100ms |
| Taux d'import réussi | 85% | > 95% |
| Temps de récupération données | Impossible | < 5min |

### Monitoring
- [ ] Mettre en place `timing.log` pour tracking
- [ ] Dashboard de monitoring interne
- [ ] Alertes si temps de réponse > seuil

---

## 🚨 RISQUES ET MITIGATIONS

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Régression fonctionnalités | Moyenne | Élevé | Tests complets avant merge |
| Migration base de données | Faible | Élevé | Backup avant migration, rollback possible |
| Performance non atteinte | Moyenne | Moyen | Profilage régulier, optimisation ciblée |
| Retard de livraison | Moyenne | Moyen | Déscope des tâches non-critiques |

---

## 📞 POINTS DE CONTRÔLE

### Daily Standup (15 min)
- Hier: qu'est-ce qui a été fait?
- Aujourd'hui: qu'est-ce qui est prévu?
- Blocages?

### Review Hebdomadaire (1h)
- Démonstration des avancées
- Feedback rapide
- Ajustement du planning si nécessaire

### Rétrospective (2h)
- À la fin de la Phase 1
- Ce qui a bien fonctionné
- Ce qui peut être amélioré
- Actions pour la Phase 2

---

## 🎯 DÉFINITION DE "TERMINÉ"

Une tâche est considérée comme **terminée** quand:
1. Le code est écrit et testé localement
2. Les tests automatisés passent
3. La revue de code est validée
4. La documentation est mise à jour
5. Le CHANGELOG est mis à jour
6. Déployé en environnement de test
7. Validé par QA

---

**Document opérationnel - Phase 1**  
*À imprimer et suivre quotidiennement*
