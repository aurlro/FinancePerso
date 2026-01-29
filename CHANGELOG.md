# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

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
