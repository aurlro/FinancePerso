# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

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
