# Guide de Recette UAT - User Acceptance Testing

> **Version**: 5.4.0  
> **Date**: 21 Février 2026  
> **Objectif**: Vérifier la circulation des données du "cerveau" (IA) vers le "moteur" (Maths) jusqu'à l'"interface" (Vibe UI)

---

## 🛠️ Protocole de Test de Bout en Bout (End-to-End)

### Scénario 1 : Le cycle de vie d'une transaction "Mystère"

**Chaîne testée**: Nettoyage ➔ Cascade ➔ IA Locale ➔ Stockage

#### 🔧 Action
Importez une transaction brute complexe:
```
DBIT-2026-02-21-PARIS-CB-7342-STARBUCKS
```

#### ✅ Vérifications attendues

- [ ] **Phase 2 - Nettoyage**: Le module `data_cleaning` extrait uniquement "STARBUCKS"
  ```python
  from src import clean_transaction_label
  result = clean_transaction_label("DBIT-2026-02-21-PARIS-CB-7342-STARBUCKS")
  # Attendu: "STARBUCKS"
  ```

- [ ] **Phase 2 - Cascade**: La cascade tente une recherche floue avant d'appeler l'IA
  - Vérifier dans les logs: "Tentative de correspondance floue"
  - Si échec: appel IA avec contexte enrichi

- [ ] **Phase 2 - IA**: Le modèle renvoie un JSON valide avec la catégorie `Food & Drink > Coffee Shops`
  ```json
  {
    "category": "Food & Drink",
    "subcategory": "Coffee Shops",
    "confidence": 0.95,
    "risk_flag": 0
  }
  ```

- [ ] **Sécurité**: Le `risk_flag` est à 0 (Normal)
  - Si montant > €10k ou pays à risque: flag > 0

---

### Scénario 2 : La détection de "l'Abonnement Zombie"

**Chaîne testée**: Historique ➔ Moteur de Récurrence ➔ UI Alertes

#### 🔧 Action
Ajoutez manuellement trois transactions "Netflix":
```python
from src import Subscription
from datetime import date

transactions = [
    Subscription(
        merchant="NETFLIX",
        frequency="monthly",
        average_amount=17.99,
        last_date="2026-01-12",
        next_expected_date="2026-02-12",
        status="ACTIF",
    ),
    Subscription(
        merchant="NETFLIX", 
        frequency="monthly",
        average_amount=17.99,
        last_date="2026-01-15",
        next_expected_date="2026-02-15",
        status="ACTIF",
    ),
    Subscription(
        merchant="NETFLIX",
        frequency="monthly", 
        average_amount=17.99,
        last_date="2026-01-14",
        next_expected_date="2026-02-14",
        status="ZOMBIE",  # Pas de transaction depuis >45j
    ),
]
```

#### ✅ Vérifications attendues

- [ ] **Phase 3 - Détection**: Le `SubscriptionDetector` identifie le pattern "Mensuel"
  ```python
  from src import SubscriptionDetector
  detector = SubscriptionDetector()
  subs = detector.detect_from_dataframe(df_transactions)
  # Attendu: 1 abonnement Netflix détecté, fréquence="monthly"
  ```

- [ ] **Phase 3 - UI**: Le tableau de bord affiche Netflix dans la section "Charges Fixes"
  - Vérifier dans `views/subscriptions.py`
  - Badge "ACTIF" ou "ZOMBIE" visible

- [ ] **Phase 3 - Reste à Vivre**: Le calcul déduit le montant de Netflix
  ```python
  from src import calculate_remaining_budget
  result = calculate_remaining_budget(
      current_balance=1500.0,
      subscriptions=subs,
      days_ahead=30
  )
  # Attendu: result.remaining_budget = 1500 - 17.99 = 1482.01
  ```

- [ ] **Phase 5 - Agent**: Une mission d'optimisation apparaît si Netflix est ZOMBIE
  - Alerte: "💤 Abonnement dormant: Netflix"
  - Action proposée: Générer lettre de résiliation

---

### Scénario 3 : La Projection Patrimoniale "Choc"

**Chaîne testée**: Actifs 360 ➔ Monte Carlo ➔ Plotly

#### 🔧 Action
Dans la vue "Projections", simulez un crash boursier:
```python
from src import project_wealth_evolution, WealthManager

manager = WealthManager()
manager.set_cash_balance(10000)

# Simulation avec volatilité augmentée (crash -20%)
projection = project_wealth_evolution(
    wealth_manager=manager,
    years=5,
    monthly_contribution=500,
    n_simulations=1000,
    # Paramètres stress test
    custom_returns={
        AssetType.SECURITIES: {'mu': 0.07, 'sigma': 0.30},  # Volatilité x2
    }
)
```

#### ✅ Vérifications attendues

- [ ] **Phase 4 - Performance**: Le calcul se lance en moins de 2 secondes
  ```python
  import time
  start = time.time()
  result = quick_simulation(10000, 500, 5, ScenarioType.MODERATE, 1000)
  elapsed = time.time() - start
  # Attendu: elapsed < 2.0
  ```

- [ ] **Phase 4 - Visualisation**: Le graphique Plotly affiche le **cône de probabilité**
  - Percentile 5% (scénario catastrophe)
  - Percentile 50% (médiane)
  - Percentile 95% (scénario optimiste)

- [ ] **Phase 4 - Cohérence mathématique**: La médiane suit l'équation GBM
  ```
  S_t = S_0 * exp((μ - 0.5σ²)t + σW_t)
  
  Pour S_0=10000, μ=7%, σ=15%, t=5 ans:
  - Médiane attendue: ~€14,000
  - Intervalle 90%: [€9,000 - €22,000]
  ```

- [ ] **Phase 4 - UI Vibe**: Le graphique s'affiche avec le thème sombre
  - Couleurs cohérentes avec le Design System
  - Tooltips explicatifs visibles

---

### Scénario 4 : L'Optimisation Agentique "Doublon"

**Chaîne testée**: Détection ➔ Raisonnement ➔ Action

#### 🔧 Action
Créez deux abonnements similaires:
```python
from src import Subscription, AgentOrchestrator

subscriptions = [
    Subscription(
        merchant="NETFLIX",
        frequency="monthly",
        average_amount=17.99,
        status="ACTIF",
    ),
    Subscription(
        merchant="AMAZON PRIME",
        frequency="monthly", 
        average_amount=12.99,
        status="ACTIF",
    ),
    # Doublon: deux services streaming
]

orchestrator = AgentOrchestrator()
missions = orchestrator.analyze_and_generate_missions(
    subscriptions=subscriptions,
    wealth_manager=WealthManager(),
)
```

#### ✅ Vérifications attendues

- [ ] **Phase 5 - Détection**: Le système détecte le doublon de catégorie "streaming"
  - Flag: `DUPLICATE_SUBSCRIPTION`
  - Économie potentielle calculée

- [ ] **Phase 5 - Mission**: Une mission apparaît dans l'UI
  - Titre: "🔁 Doublon détecté: streaming"
  - Description claire des deux services

- [ ] **Phase 5 - Action**: Bouton "Générer lettre de résiliation" disponible
  - Lettre pré-remplie avec données utilisateur
  - Human-in-the-loop: confirmation requise

---

### Scénario 5 : Le Hard Delete RGPD

**Chaîne testée**: Demande ➔ Suppression ➔ Vérification

#### 🔧 Action
Demandez la suppression complète des données:
```python
from modules.privacy import GDPRManager

gdpr = GDPRManager()

# Avant: compter les données
before_count = len(gdpr.export_user_data('user-123')['transactions'])

# Hard Delete
record = gdpr.purge_user_data(
    user_id='user-123',
    requested_by='user',
    reason='right_to_be_forgotten',
)

# Après: vérifier suppression
after_data = gdpr.export_user_data('user-123')  # Doit être vide ou erreur
```

#### ✅ Vérifications attendues

- [ ] **Phase 6 - Suppression**: Toutes les entrées SQL sont supprimées
  - Tables: transactions, categories, settings, etc.
  - Aucune trace de `user_id` en base

- [ ] **Phase 6 - Fichiers**: Les fichiers locaux sont supprimés
  - Imports: `Data/imports/user-123/`
  - Exports: `Data/exports/user-123/`

- [ ] **Phase 6 - Cache**: Les entrées de cache sont invalidées
  - Pattern: `*user-123*` supprimé

- [ ] **Phase 6 - Preuve**: Un hash de preuve est généré
  ```python
  record.proof_hash  # Hash SHA-256 unique
  # Vérification possible via gdpr.verify_deletion(hash)
  ```

---

## 📊 Tableau de bord de Validation des Modules

| Module | Point de contrôle critique | Statut (✅/❌) | Notes |
|--------|---------------------------|---------------|-------|
| **IA Locale** | Absence de texte "bavard" dans le JSON | ✅ | `temperature=0.1` pour déterminisme |
| **PFCv2** | Pas de catégorie "Inconnu" | ✅ | Tout doit être mappé |
| **Immobilier** | L'équité nette augmente après chaque mensualité | ✅ | `equity = value - remaining` |
| **Agentique** | Notification si doublon créé | ✅ | Mission générée automatiquement |
| **Sécurité** | Bouton "Hard Delete" supprime les fichiers | ✅ | Suppression irréversible |
| **Cache** | TTL adaptatif par type de donnée | ✅ | Monte Carlo: 10min, Transactions: 1min |
| **Performance** | Monte Carlo <2s pour 1000 sims | ✅ | Vectorisation numpy |
| **UI Vibe** | Dark Mode cohérent | ✅ | Palette Slate/Indigo |

---

## ⚡ Check-list de la "Vibe" & Performance

### Performance

- [ ] **Temps de chargement**: L'UI ne "freeze" pas lors de l'inférence IA
  - Utilisation de `st.spinner()` pendant les calculs
  - Cache actif pour éviter les recalculs

- [ ] **Efficience énergétique**: Le CPU ne monte pas à 100% lors de la navigation
  - Cache strict entre les pages
  - Lazy loading des données lourdes

- [ ] **Scalabilité**: L'application reste fluide avec 50k+ transactions
  - Pagination des résultats
  - Requêtes SQL optimisées avec LIMIT/OFFSET

### Esthétique

- [ ] **Micro-animations**: Pas de décalage visuel (jank)
  - Transitions CSS fluides (300ms)
  - Utilisation de `transform` et `opacity` (GPU accelerated)

- [ ] **Cohérence visuelle**: Toutes les pages suivent le Design System
  - Couleurs: Slate 900 (bg), Indigo 500 (primary)
  - Typographie: Inter (text), JetBrains Mono (numbers)
  - Espacements: 8px grid system

- [ ] **Responsive**: L'application est utilisable sur mobile
  - Breakpoints: 768px (tablet), 480px (mobile)
  - Composants adaptatifs

---

## 🔧 Procédure de Test Automatisé

### Lancer tous les tests

```bash
# Tests unitaires
pytest tests/ -v --tb=short

# Tests d'intégration
pytest tests/test_integration.py -v

# Tests de performance
python scripts/benchmark_monte_carlo.py

# Tests de sécurité
python scripts/test_security_flags.py
```

### Validation manuelle rapide

```python
# 1. Test end-to-end complet
from src import (
    clean_transaction_label,  # Phase 2
    SubscriptionDetector,      # Phase 3
    quick_simulation,          # Phase 4
    WealthManager,             # Phase 5
    AgentOrchestrator,         # Phase 5
)
from modules.ui import DesignSystem      # Phase 6
from modules.performance import AdvancedCache  # Phase 6
from src.security_monitor import SecurityMonitor  # Phase 6
from modules.privacy import GDPRManager  # Phase 6

print("✅ Tous les imports réussis - Architecture OK")

# 2. Test chaîne de données
tx_raw = "CB-2026-02-21-PARIS-STARBUCKS"
tx_clean = clean_transaction_label(tx_raw)
print(f"✅ Nettoyage: {tx_raw} -> {tx_clean}")

# 3. Test performances
import time
start = time.time()
result = quick_simulation(10000, 500, 10, ScenarioType.MODERATE, 1000)
elapsed = time.time() - start
print(f"✅ Performance: {elapsed:.2f}s pour 1000 simulations")
```

---

## 🚨 Troubleshooting

### Problème: L'IA invente des catégories

**Solution**: Vérifier la `temperature` dans la configuration
```python
# modules/ai_manager.py
response = provider.generate_json(
    prompt,
    temperature=0.1,  # DOIT être 0.0 ou 0.1 pour du JSON
)
```

### Problème: Le cache ne fonctionne pas

**Solution**: Vérifier les clés de cache
```python
from modules.performance import get_cache_stats
print(get_cache_stats())
# Si hit_rate = 0%, vérifier que les fonctions sont décorées avec @cache_monte_carlo
```

### Problème: Les montants négatifs apparaissent

**Solution**: Vérifier la normalisation des dépenses
```python
# Les dépenses doivent être négatives, revenus positifs
amount = -abs(amount) if is_expense else abs(amount)
```

---

## ✅ Sign-off

| Rôle | Nom | Date | Signature |
|------|-----|------|-----------|
| Product Owner | | | |
| Tech Lead | | | |
| QA Engineer | | | |
| Security Officer | | | |

---

**Note**: Ce guide doit être exécuté avant chaque release majeure.  
**Fréquence**: À chaque version x.y.0 (releases mineures)  
**Durée estimée**: 2-3 heures pour un test complet
