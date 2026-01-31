# 💰 FinancePerso - Personal Finance Manager

Un assistant intelligent de gestion financière personnelle développé avec Streamlit et alimenté par l'IA.

## 📋 Vue d'ensemble

FinancePerso est une application web complète de gestion de finances personnelles qui automatise la catégorisation des transactions bancaires, offre des analyses visuelles et facilite le suivi budgétaire grâce à l'intelligence artificielle.

### ✨ Fonctionnalités principales

- **🔄 Import automatique** : Importation CSV depuis vos relevés bancaires
- **🤖 Catégorisation IA** : Classification automatique des transactions avec apprentissage progressif
- **✅ Validation rapide** : Interface intelligente avec regroupement automatique et validation en masse
- **📊 Analyses visuelles** : Tableaux de bord et graphiques interactifs
- **🏷️ Gestion flexible** : Tags personnalisés, catégories configurables, multi-comptes
- **👥 Multi-membres** : Attribution des dépenses par membre du foyer
- **💾 Sauvegardes automatiques** : Protection de vos données avec historique de versions
- **🧠 Apprentissage** : Mémorisation des règles de catégorisation pour amélioration continue

### 🚀 Nouvelles Fonctionnalités IA (v2.0)

- **🎯 Détection d'Anomalies** : Identification automatique des montants inhabituels
- **💡 Tags Intelligents** : Suggestions contextuelles de tags par IA
- **📊 Analyse de Tendances** : Comparaison automatique des périodes et insights narratifs
- **💬 Chat IA** : Assistant conversationnel pour interroger vos finances en langage naturel
- **📈 Prédictions Budgétaires** : Alertes de dépassement de budget en temps réel

### 🤖 Machine Learning Local (v3.6)

Alternative **100% offline** à l'IA cloud pour la catégorisation des transactions :

- **🔒 Confidentialité totale** : Aucune donnée ne quitte votre ordinateur
- **⚡ Latence nulle** : Prédictions instantanées
- **📈 Auto-amélioration** : S'entraîne sur vos transactions validées
- **💰 Gratuit** : Aucun coût API

**Installation :**
```bash
pip install -r requirements-ml.txt
```

Puis dans **Configuration > IA & Services**, choisissez le mode "ML Local".

## 🚀 Installation

### Prérequis

- Python 3.8+
- pip

### Installation rapide

```bash
# Cloner le dépôt
git clone <repository-url>
cd FinancePerso

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run Accueil.py
```

## ⚙️ Configuration

### Configuration de l'IA

1. Accédez à l'onglet **Configuration > IA & Services**
2. Choisissez votre mode de catégorisation :
   - **🤖 Auto** : Local si disponible, sinon Cloud
   - **🏠 ML Local** : 100% offline (nécessite `pip install scikit-learn`)
   - **☁️ IA Cloud** : Meilleure précision via API externe
   - **📋 Règles uniquement** : Pas de ML, uniquement les règles définies

3. Pour l'IA Cloud, choisissez votre fournisseur :
   - **Gemini** (recommandé) : Rapide et gratuit
   - **Ollama** : 100% local et privé
   - **DeepSeek** : Excellent rapport qualité/prix
   - **OpenAI** : Standard de l'industrie

4. Entrez votre clé API (ou URL pour Ollama)

### Configuration des membres

1. Allez dans **Configuration > Foyer & Membres**
2. Ajoutez les membres de votre foyer
3. (Optionnel) Associez les numéros de carte pour attribution automatique

## 📂 Structure du projet

```
FinancePerso/
├── Accueil.py                 # Page d'accueil principale
├── pages/
│   ├── 1_Import.py           # Import de transactions CSV
│   ├── 2_Validation.py       # Validation et catégorisation
│   ├── 3_Synthese.py         # Tableaux de bord et analyses
│   ├── 4_Regles.py           # Gestion des règles d'apprentissage
│   ├── 5_Assistant.py        # Assistant IA conversationnel
│   └── 9_Configuration.py    # Paramètres système
├── modules/
│   ├── ai/                   # 🆕 Suite IA complète (v2.0)
│   │   ├── anomaly_detector.py
│   │   ├── smart_tagger.py
│   │   ├── budget_predictor.py
│   │   ├── trend_analyzer.py
│   │   └── conversational_assistant.py
│   ├── categorization.py     # Logique IA de catégorisation
│   ├── data_manager.py       # Gestion base de données SQLite
│   ├── backup_manager.py     # Gestion des sauvegardes
│   ├── ui.py                 # Composants UI réutilisables
│   ├── utils.py              # Fonctions utilitaires
│   └── logger.py             # Système de logs
├── Data/
│   ├── finance.db            # Base de données SQLite
│   ├── backups/              # Sauvegardes automatiques
│   └── samples/              # Fichiers d'exemple
├── docs/                     # Documentation technique
├── .streamlit/
│   └── config.toml           # Configuration Streamlit
├── .env                      # Variables d'environnement (API keys)
├── requirements.txt          # Dépendances Python
├── CHANGELOG.md              # 🆕 Historique des versions
└── README.md                 # Ce fichier
```

## 🎯 Utilisation

### 1. Import de transactions

1. Exportez vos transactions bancaires au format CSV
2. Accédez à **Import**
3. Sélectionnez votre fichier CSV
4. Configurez le mapping des colonnes
5. Importez !

### 2. Validation

1. Accédez à **Validation**
2. Les transactions sont automatiquement regroupées par similitude
3. Utilisez le bouton ✅ pour valider rapidement
4. Ou ouvrez l'expander pour affiner (catégorie, tags, bénéficiaire)
5. Le système mémorise vos choix pour les prochaines fois

### 3. Analyse

1. Accédez à **Synthèse**
2. Visualisez vos dépenses par catégorie, membre, période
3. Suivez vos budgets et objectifs

## 🗄️ Base de données

### Tables principales

- **transactions** : Toutes les opérations bancaires
- **categories** : Catégories de dépenses configurables
- **learning_rules** : Règles d'apprentissage automatique
- **members** : Membres du foyer
- **member_mappings** : Association cartes → membres
- **budgets** : Objectifs budgétaires par catégorie

## 🔐 Sécurité & Confidentialité

- Toutes les données sont stockées **localement** dans une base SQLite
- Aucune donnée bancaire n'est transmise à l'extérieur (sauf à l'API IA pour catégorisation)
- Les clés API sont stockées dans `.env` (à ne jamais commiter)
- Sauvegardes automatiques quotidiennes

## 🛠️ Développement

### Lancer en mode développement

```bash
streamlit run Accueil.py --server.runOnSave true
```

### Contribuer

Voir `gemini.md` pour les guidelines de développement et l'architecture du code.

## 📝 Licence

Projet personnel - Tous droits réservés

## 🤝 Support

Pour toute question ou suggestion, créez une issue sur le dépôt.

---

**Développé avec ❤️ et alimenté par l'IA Gemini**
