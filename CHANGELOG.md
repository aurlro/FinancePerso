# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

---

## [4.0.0] - 2026-02-02

### Nouvelles fonctionnalités - 8 ajouts

**✨ Ajouté**
- - feat: Implement comprehensive UI/UX redesign, introduce gamification and enhanced feedback, and update core database modules for improved tag, category, rule, and transaction management.
- - ✨ feat: Amélioration feedback actions rapides (quick_actions)
- - ✨ feat: Amélioration UI/UX et feedback - Configuration
- - ✨ feat: ML Local, Mobile Responsive & PWA Mode Hors-ligne
- - ✨ Système de mise à jour complet - v3.6.0
- - ✨ feat: Add scroll-to-top button on all pages
- - ✨ feat: Add comprehensive visual feedback system and quick actions popups
- - feat: Implement enhanced audit functionality with bulk actions, filtering, and a new analytics module.

**🐛 Corrigé**
- - fix: correction imports modules/ui et analyse auto changements
- - 🐛 fix: Correction imports render_scroll_to_top
- - 🐛 fix: Correction erreur SQL merge_categories - colonne id budgets
- - 🐛 fix: Système de logs - fichier et viewer
- - 🔧 fix: Audit corrections - version sync, cleanup, docs
- - 🔧 fix: Improve email notification error handling and user feedback
- - fix: Correct cache invalidation import errors

**⚡ Performance**
- - 🔒 Implémentation complète : Chiffrement, Cache, Validateurs - v3.5.0
- - 🔒 Sécurité & Optimisation: Refactorisation majeure v3.2.0

*Fichiers modifiés* : .agents/skills/financeperso-specific/SKILL.md, .agents/skills/financeperso-specific/references/architecture.md, AGENTS.md, CHANGELOG.md, CONTRIBUTING.md, EMAIL_TROUBLESHOOTING.md, GUIDE_UTILISATEUR.md, INDISPENSABILITY_UPGRADES.md, README.md, app.py, assets/offline.html, assets/pwa.js, assets/service-worker.js, assets/style.css, docs/AUDIT_FIXES_SUMMARY.md, docs/COMPLETE_AUDIT_REPORT.md, docs/FINAL_AUDIT_SUMMARY.md, docs/FINAL_CORRECTIONS_REPORT.md, docs/N1_FIX_PLAN.md, docs/NEW_FEATURES.md

---

## [3.1.0] - 2026-01-30

### ✨ Analyse des Récurrences V2 - Refonte Complète

**🔧 Corrections de Bugs**
- **Drill-down fonctionnel** : Correction du bug "Aucune transaction trouvée" dans l'historique détaillé
- Stockage des IDs de transactions pour un affichage fiable
- Matching précis entre récurrences détectées et transactions réelles

**💰 Détection des Revenus Améliorée**
- Détection des salaires (patterns : SALAIRE, REMUNERATION, CAPGEMINI...)
- Détection des allocations chômage (patterns : FRANCE TRAVAIL, POLE EMPLOI, ARE)
- Détection des pensions (patterns : CNAV, CARSAT, RETRAITE)
- Tolérance accrue pour les variations de montant sur les revenus

**📂 Nouvelles Vues d'Analyse**
- **Vue "Par opération"** : Liste détaillée avec filtres (Type, Fréquence, Montant)
- **Vue "Par catégorie"** : Regroupement et agrégation par catégorie
- **Vue "Par tag"** : Analyse des récurrences par tags associés

**🎨 Améliorations UX**
- Cartes de résumé mensuel (charges, revenus, balance)
- Indicateurs visuels 🟢 Fixe / 🟡 Variable
- Affichage des variantes de libellés (+N variantes)
- Filtres interactifs dans la sidebar
- Expandables avec transactions éditables

*Fichiers modifiés* : `pages/4_Recurrence.py`, `modules/analytics_v2.py` (nouveau)

---

## [3.0.1] - 2026-01-30

### 🔄 Améliorations Techniques

**Phase 3 - Function extraction and type safety**
- ## Refactorisation Majeure
- Reduce render_transaction_drill_down() from 341 to ~40 lines
- Extract 5 helper functions for better separation of concerns:
- * _fetch_and_filter_transactions() - Data fetching (16 lines)
- * _display_summary_metrics() - Metrics display (15 lines)
- * _render_transaction_row() - Single row rendering (31 lines)
- * _handle_validated_transactions() - Validated section (81 lines)
- * _handle_pending_transactions() - Pending section (67 lines)
- Replace st.cache_data.clear() with selective invalidation
- ## Extraction de Fonction Analytics
- Extract detect_frequency() from detect_recurring_payments()

*Fichiers modifiés* : `- Reduce cyclomatic complexity in analytics.py`, `modules/analytics.py`, `modules/ingestion.py` (+1 autres)

**Phase 2 - Code cleanup and optimization**
- ## Extraction et Réutilisabilité


### ⚡ Performances

**Critical business logic optimizations (90-95% faster)**
- Implemented two major performance optimizations based on comprehensive analysis:
- 1. Rule Caching with Pre-compiled Regex (90-95% gain)


---

## [3.0.0] - 2026-01-30

### ✨ Nouvelles Fonctionnalités

**Improve versioning script to generate detailed changelog entries**
- Parse full commit bodies and extract detailed bullet points
- Add emoji-based sections (🔒 Security, ✨ Features, 🐛 Fixes, etc.)
- Include file modification information
- Generate rich, narrative changelog entries like v2.0-2.2 format
- Add breaking changes section with detailed explanations
- Support multiple commit types (security, perf, refactor, etc.)
- The new script generates comprehensive changelogs automatically from git
- commits with proper formatting, sections, and context, matching the detailed
- style of historical changelog entries.

*Fichiers modifiés* : `scripts/versioning.py`


### ⚡ Performances

**Add database pagination, composite indexes, and selective cache invalidation**
- **Database Query Pagination**

*Fichiers modifiés* : `- Add pagination support to get_all_transactions() with limit/offset parameters`, `*Fichiers modifiés* : `modules/db/transactions.py`, `modules/db/migrations.py`, `modules/cache_manager.py` (nouveau)`, `modules/cache_manager.py` (+2 autres)


### ⚠️ Breaking Changes

**Improve versioning script to generate detailed changelog entries**

- - Add breaking changes section with detailed explanations
- - Parse full commit bodies and extract detailed bullet points
- - Add emoji-based sections (🔒 Security, ✨ Features, 🐛 Fixes, etc.)
- - Include file modification information
- - Generate rich, narrative changelog entries like v2.0-2.2 format
- - Support multiple commit types (security, perf, refactor, etc.)
- The new script generates comprehensive changelogs automatically from git
- commits with proper formatting, sections, and context, matching the detailed
- style of historical changelog entries.

---

## [2.8.0] - 2026-01-30

### 🔒 Sécurité et Validation Renforcées

**Gestion sécurisée des secrets**
- Implémentation de `python-dotenv` pour la gestion du fichier `.env`
- Permissions sécurisées automatiques (0600) sur le fichier de configuration
- Validation des formats de clés API (Gemini, OpenAI, DeepSeek)
- Messages d'erreur clairs et informatifs pour la configuration

**Validation des entrées utilisateur**
- Validation complète des patterns regex pour les règles d'apprentissage
- Détection des patterns dangereux (catastrophic backtracking)
- Validation du mapping CSV avec vérification des données échantillons
- Vérification de la cohérence des colonnes sélectionnées

**Gestion d'erreurs améliorée**
- Remplacement de toutes les clauses `except:` nues (6 occurrences)
- Gestion spécifique des exceptions (subprocess, réseau, parsing dates)
- Nouvelles classes d'exceptions personnalisées (`modules/exceptions.py`)
- Logging amélioré dans l'AI manager et l'auditeur de règles

### ✨ Nouvelles Fonctionnalités

**Configuration des virements internes**
- Table `settings` créée pour stocker la configuration utilisateur
- Module de gestion des paramètres (`modules/db/settings.py`)
- Interface utilisateur complète dans Configuration → Tags & Règles
- Migration des données personnelles hardcodées vers la base de données
- Possibilité d'ajouter/supprimer des mots-clés de détection

**Utilitaires de sécurité**
- `escape_html()` - Protection contre les attaques XSS
- `safe_html_template()` - Interpolation sécurisée dans les templates HTML
- Documentation complète avec exemples d'utilisation

### 🔄 Améliorations Techniques

- Centralisation de la configuration (plus de données personnelles dans le code)
- Amélioration de la modularité avec les nouvelles classes d'exceptions
- Retro-compatibilité assurée avec valeurs par défaut automatiques
- Feedback utilisateur amélioré avec validation temps réel

### ⚠️ Notes de Migration

**BREAKING CHANGE** : La détection des virements internes utilise maintenant la configuration en base de données. Les installations existantes recevront automatiquement les valeurs par défaut lors de la première exécution.

---

## [2.7.0] - 2026-01-30

### Ajouté
- Add comprehensive input validation and security utilities

---

## [2.6.0] - 2026-01-29

### Ajouté
- Implement `st.toast` for user feedback, refactor tag suggestion UI, and enhance rules auditor with stale rule detection and health scoring.

---

## [2.5.0] - 2026-01-29

### Ajouté
- Implement `st.toast` for user feedback, refactor tag suggestion UI, and enhance rules auditor with stale rule detection and health scoring.

---

## [2.4.0] - 2026-01-29

### Ajouté
- Implement `st.toast` for user feedback, refactor tag suggestion UI, and enhance rules auditor with stale rule detection and health scoring.

---

## [2.2.0] - 2026-01-29

### 🕵️ Audit et Qualité des Données
- **Audit Assistant IA** (`pages/4_Regles.py`) : Nouvelle fonctionnalité pour analyser la base de règles.
- Détection automatique des **conflits** (même mot-clé, catégories différentes).
- Identification des **doublons** et des patterns **trop vagues**.
- Affichage de la date de dernière mise à jour de l'analyse.

### 🧠 Apprentissage
- Amélioration de l'apprentissage automatique depuis les corrections manuelles (v2.1 feature refined).

---

## [2.1.0] - 2026-01-29

### 🎨 Amélioration de l'Expérience Utilisateur

#### 💎 Édition en Masse dans le Drill-Down
- Modification des catégories de transactions **validées** directement depuis le drill-down
- Sélecteur de catégorie individuel pour chaque transaction
- Bouton "💾 Sauvegarder" pour appliquer toutes les modifications en une fois
- Fonctionne pour les insights de tendances dans l'onglet Assistant

#### 🔄 Détection des Virements Internes
- Nouvelle fonction `detect_internal_transfers()` dans `modules/analytics.py`
- Patterns détectés : "VIR SEPA AURELIEN", "ALIMENTATION COMPTE JOINT", "VIREMENT", etc.
- Fonction `exclude_internal_transfers()` pour nettoyer les analyses
- Toggle "🔄 Exclure les virements internes" dans l'onglet Tendances

#### 🧠 Apprentissage depuis les Corrections (Nouveau)
- Option "**🧠 Mémoriser ces choix pour le futur**" dans le drill-down
- Génère automatiquement des règles d'apprentissage lors de la correction manuelle
- Priorité haute (5) pour les règles générées afin de remplacer les anciennes habitudes
- Transforme la session de correction en session d'entraînement de l'IA

#### 📅 Contexte Temporel Enrichi
- Affichage précis des périodes comparées dans l'analyse de tendances
- Format : "2026-01-01 → 2026-01-31 (31 jours) vs 2025-12-01 → 2025-12-31 (31 jours)"
- Meilleure compréhension des variations détectées

### 🐛 Corrections
- **Anomaly Detector** : Correction du conflit de nom de variable `clean_label`

---

## [2.0.0] - 2026-01-28

### 🚀 Nouvelles Fonctionnalités Majeures - Assistant IA Enrichi

#### 🎯 Détection d'Anomalies de Montant
- Analyse statistique automatique des transactions
- Identification des montants inhabituels (> 2σ)
- Classification par sévérité (high/medium)
- Nouvel onglet "🎯 Anomalies" dans l'Assistant

#### 💡 Suggestions de Tags Intelligentes
- Analyse contextuelle par IA (libellé, montant, catégorie)
- Suggestions parmi: Remboursement, Professionnel, Cadeau, Urgent, Récurrent, etc.
- Mode batch pour traiter plusieurs transactions

#### 📊 Analyse de Tendances
- Comparaison automatique période actuelle vs précédente
- Détection des variations significatives (> 30%)
- Insights narratifs générés par IA
- Nouvel onglet "📊 Tendances" dans l'Assistant

#### 💬 Assistant Conversationnel
- Chat IA pour interroger vos finances en langage naturel
- Fonctions outils: dépenses par catégorie, statut budgets, top dépenses
- Historique de conversation
- Nouvel onglet "💬 Chat IA" dans l'Assistant

#### 📈 Prédictions Budgétaires
- Projection linéaire des dépenses jusqu'à fin de mois
- Alertes: 🟢 OK (<80%), 🟠 Attention (80-100%), 🔴 Dépassement (>100%)
- Widget "Alertes Budgétaires" dans la page Synthèse
- Calcul de moyenne journalière

### 🏗️ Architecture
- Nouveau module `modules/ai/` avec 5 sous-modules
- Structure modulaire et extensible
- Exports centralisés dans `modules/ai/__init__.py`

### 📝 Configuration Manuelle du Profil Financier
- Formulaire de configuration pour Revenus, Logement, Abonnements
- Intégré dans l'onboarding initial
- Accessible dans l'Assistant (Configuration Assistée)
- Création automatique de règles et budgets

### 🐛 Corrections
- **Fusion de catégories** : Ajout de `COLLATE NOCASE` pour insensibilité à la casse
- **Persistance Audit** : Corrections dans l'Assistant d'Audit maintenant sauvegardées correctement
- Cast explicite des IDs de transaction en `int`
- Nettoyage du cache Streamlit après modifications

---

## [1.5.0] - 2026-01-XX

### Ajouté
- Support multi-fournisseurs IA (Gemini, Ollama, DeepSeek, OpenAI)
- Gestion des membres du foyer avec mapping de cartes
- Tags personnalisés pour transactions
- Détection automatique du profil financier
- Analyse des abonnements récurrents

### Amélioré
- Interface de validation avec regroupement intelligent
- Tableaux de bord avec filtres avancés
- Système de sauvegardes automatiques

---

## [1.0.0] - 2026-01-XX

### Première version stable
- Import CSV multi-formats
- Catégorisation IA avec apprentissage
- Validation en masse
- Tableaux de bord interactifs
- Gestion des budgets
- Base de données SQLite locale
