# Phase 5 - Gestion Patrimoniale Holistique & IA Agentique

## 🎯 Objectifs atteints

Cette phase étend FinancePerso pour gérer le patrimoine global (multi-actifs) et implémente des capacités d'action autonomes via un système agentique.

---

## 📦 Modules créés

### 1. `src/wealth_manager.py` - Module Patrimoine Holistique

**Gestion de tous les types d'actifs:**

| Type d'actif | Classe | Caractéristiques |
|--------------|--------|------------------|
| 💰 Cash | `WealthManager.cash_balance` | Liquidités immédiates |
| 🏠 Immobilier | `RealEstateAsset` | Valeur, crédit, équité nette |
| 📈 Financier | `FinancialAsset` | PEA, CTO, Assurance Vie |
| ₿ Crypto | `CryptoAsset` | Bitcoin, Ethereum, etc. |
| 💳 Dettes | `Liability` | Crédits conso, étudiant |

**Classe `MortgageSchedule` :**
- Tableau d'amortissement complet
- Calcul du capital restant dû à date
- Équité nette : `Valeur du bien - Capital restant dû`
- Progression du remboursement

**Calculs patrimoniaux:**
```python
manager = WealthManager()
manager.add_real_estate(apartment)
manager.add_financial_asset(pea)

# Patrimoine net (équité immo - dettes)
net_worth = manager.get_total_net_worth()

# Répartition
allocation = manager.get_asset_allocation()

# Liquidité
liquidity = manager.get_liquidity_analysis()
```

### 2. `src/agent_core.py` - Orchestrateur d'IA Agentique

**Architecture Agentique:**

```
┌─────────────────┐
│  TriggerDetector │  ← Détecte anomalies/opportunités
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ AgentOrchestrator│  ← Raisonne et génère des missions
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Mission      │  ← Action concrète proposée
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│DocumentGenerator│  ← Lettres, documents pré-remplis
└─────────────────┘
```

**Types de triggers détectés:**

| Trigger | Détection | Action proposée |
|---------|-----------|-----------------|
| 📈 `PRICE_INCREASE` | Hausse >10% | Lettre de réclamation |
| 🔁 `DUPLICATE_SUBSCRIPTION` | Doublon catégorie | Résiliation |
| 💤 `UNUSED_SUBSCRIPTION` | Zombie >45j | Résiliation |
| 💡 `BETTER_ALTERNATIVE` | Offre -20% | Comparaison |
| 💰 `CASH_IDLE` | >20% cash | Suggestion invest. |
| ⚠️ `HIGH_DEBT_RATIO` | >33% endettement | Alertes |
| 📊 `DIVERSIFICATION_NEEDED` | Concentration | Rééquilibrage |

**Human-in-the-loop obligatoire:**
```python
# L'IA propose mais ne fait jamais d'action réelle sans validation
if action.requires_human_validation:
    show_confirmation_dialog(action)  # UI Streamlit
    
# Seules les actions marquées auto_executable=False nécessitent validation
```

### 3. `src/wealth_projection.py` - Intégration Phase 4×5

**Projections patrimoniales multi-actifs:**

```python
projection = project_wealth_evolution(
    wealth_manager=manager,
    years=20,
    monthly_contribution=1000,
)

# Résultats
projection.get_net_worth_at_year(10)  # Médiane à 10 ans
projection.get_probability_of_target(500000, 10)  # Probabilité objectif
```

**Rendements par défaut:**

| Actif | μ (rendement) | σ (volatilité) |
|-------|---------------|----------------|
| Cash | 2.5% | 0.5% |
| Immobilier | 3.5% | 8% |
| Actions | 7% | 15% |
| Crypto | 15% | 60% |

**Comparaison de stratégies:**
```python
strategies = [
    {'name': 'Conservateur', 'allocation': {...}},
    {'name': 'Équilibré', 'allocation': {...}},
    {'name': 'Agressif', 'allocation': {...}},
]

results = compare_allocation_strategies(
    wealth_manager=manager,
    strategies=strategies,
)
```

### 4. `views/wealth_view.py` - Dashboard Patrimoine 360°

**Onglets:**

1. **📊 Vue d'ensemble**
   - KPIs: Patrimoine net, actifs, dettes, liquidité
   - Treemap Plotly de répartition
   - Détails par classe d'actif

2. **🎯 Missions Agentiques**
   - Centre de contrôle des missions
   - Filtres par priorité
   - Actions one-click (avec validation)
   - Générateur de lettres intégré

3. **🏠 Immobilier**
   - Jauge de progression remboursement
   - Équité nette vs crédit restant
   - Tableau d'amortissement
   - Alertes LTV et sous-eau

4. **📈 Projections**
   - Monte Carlo intégré
   - Scénarios What-If
   - Probabilités d'atteinte des objectifs

---

## 🏗️ Architecture

### Pattern Repository & Unit of Work

```python
# Chaque classe d'actif a sa propre logique métier
class RealEstateAsset:
    def get_equity(self, as_of_date=None) -> float:
        """Équité nette = Valeur - Capital restant dû"""
        if self.mortgage:
            return self.mortgage.get_equity(self.current_value, as_of_date)
        return self.current_value

class Liability:
    @property
    def progress_percentage(self) -> float:
        """Pourcentage remboursé"""
        paid = self.total_amount - self.remaining_amount
        return (paid / self.total_amount * 100)
```

### Chiffrement des données sensibles

```python
from modules.encryption import encrypt_field, decrypt_field

# Données sensibles chiffrées
address_encrypted = encrypt_field(asset.address)
address_decrypted = decrypt_field(address_encrypted)
```

---

## 📊 Tests validés

```python
✅ WealthManager: Multi-actifs avec équité nette
   - Cash: €25,000
   - Immobilier: €420,000 (équité: €169,640)
   - Patrimoine net: €260,890

✅ AgentOrchestrator: 4 missions générées
   - Économie potentielle: €828/an
   - Top mission: Doublon streaming (+€360/an)

✅ Projections Monte Carlo
   - Patrimoine initial: €260,890
   - Médiane 10 ans: €670,490
   - Probabilité > €500k: 86.6%

✅ Comparaison de stratégies
   - Conservateur: €680,262
   - Équilibré: €692,281

✅ Documents générés
   - Lettre de résiliation: 874 caractères
```

---

## 🚀 Utilisation

### Créer un patrimoine

```python
from src import WealthManager, RealEstateAsset, MortgageSchedule
from datetime import date

manager = WealthManager()
manager.set_cash_balance(25000)

# Immobilier avec crédit
mortgage = MortgageSchedule(
    principal=300000,
    monthly_payment=1200,
    interest_rate=0.023,
    start_date=date(2020, 1, 15),
    duration_months=240,
)

apartment = RealEstateAsset(
    id='apt-001',
    name='Appartement Paris',
    address='12 Rue...',  # Sera chiffré
    purchase_price=350000,
    current_value=420000,
    purchase_date=date(2020, 1, 15),
    mortgage=mortgage,
)
manager.add_real_estate(apartment)

print(f"Patrimoine net: €{manager.get_total_net_worth():,.2f}")
```

### Générer des missions

```python
from src import AgentOrchestrator

orchestrator = AgentOrchestrator()
missions = orchestrator.analyze_and_generate_missions(
    subscriptions=subscriptions,
    wealth_manager=manager,
    monthly_income=3500,
)

for mission in missions:
    print(f"🎯 {mission.title}: +€{mission.potential_savings:.0f}/an")
```

### Projeter le patrimoine

```python
from src import project_wealth_evolution

projection = project_wealth_evolution(
    wealth_manager=manager,
    years=20,
    monthly_contribution=1000,
)

print(f"Dans 10 ans: €{projection.get_net_worth_at_year(10):,.2f}")
print(f"Proba > 500k€: {projection.get_probability_of_target(500000, 10):.1%}")
```

### Dashboard Streamlit

```python
from views.wealth_view import render_wealth_dashboard

# Dans votre app Streamlit
render_wealth_dashboard(
    wealth_manager=manager,
    subscriptions=subscriptions,
    monthly_income=3500,
)
```

---

## 🔒 Sécurité

### Human-in-the-loop obligatoire

Toutes les actions financières nécessitent une validation explicite:

```python
@dataclass
class Action:
    type: ActionType
    label: str
    requires_human_validation: bool = True  # Par défaut
    auto_executable: bool = False

# Exécution
if action.requires_human_validation:
    if not user_confirm(action.label):
        return  # Action annulée
```

### Chiffrement AES-256

```python
from modules.encryption import encrypt_field

# Données sensibles automatiquement chiffrées
asset.address = encrypt_field("12 Rue de la Santé, 75014 Paris")
```

---

## 📈 Intégrations

### Phase 3 → Phase 5

```python
from src import SubscriptionDetector, get_default_monthly_contribution

# Détecter les abonnements
detector = SubscriptionDetector()
subscriptions = detector.detect_from_dataframe(df)

# Calculer le versement disponible
monthly = get_default_monthly_contribution(
    current_balance=1500,
    subscriptions=subscriptions,
)
```

### Phase 4 → Phase 5

```python
from src import project_wealth_evolution

# Projeter le patrimoine (pas seulement le cash)
projection = project_wealth_evolution(
    wealth_manager=manager,
    years=20,
    monthly_contribution=1000,
)
```

---

## 📁 Fichiers créés

```
FinancePerso/
├── src/
│   ├── __init__.py              # ← Exports mis à jour
│   ├── wealth_manager.py        # Phase 5 ⭐ NOUVEAU
│   ├── agent_core.py            # Phase 5 ⭐ NOUVEAU
│   └── wealth_projection.py     # Phase 5 ⭐ NOUVEAU
├── views/
│   └── wealth_view.py           # Phase 5 ⭐ NOUVEAU
└── PHASE5_WEALTH_AGENTIC.md     # Documentation
```

---

## 🎓 Concepts clés

### Équité nette immobilière

```
Équité = Valeur actuelle du bien - Capital restant dû

Exemple:
- Appartement acheté: €350k
- Valeur actuelle: €420k (+20%)
- Crédit restant: €250k
- Équité nette: €420k - €250k = €170k
```

### Loan-to-Value (LTV)

```
LTV = Capital restant dû / Valeur actuelle × 100

Alertes:
- LTV > 80%: Risque de sous-eau
- LTV > 100%: Bien sous l'eau (équité négative)
```

### Missions Agentiques

```
Observation → Raisonnement → Action
     ↓              ↓            ↓
  "Prix +15%"   "Alternative   "Générer lettre
                -20% dispo"    de résiliation"
```

### Projections Multi-actifs

```
Patrimoine net(t) = Σ Actifs_i(t) - Σ Dettes_j(t)

Où:
- Cash(t): GBM(μ=2.5%, σ=0.5%)
- Immo(t): GBM(μ=3.5%, σ=8%)
- Actions(t): GBM(μ=7%, σ=15%)
- Crypto(t): GBM(μ=15%, σ=60%)
- Dettes(t): Amortissement linéaire
```

---

**Version**: 5.3.0  
**Dernière mise à jour**: 21 Février 2026  
**Dépendances**: Phase 3 (Subscriptions), Phase 4 (Monte Carlo)
