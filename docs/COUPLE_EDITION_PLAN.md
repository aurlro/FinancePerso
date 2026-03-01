# 📋 CAHIER DES CHARGES TECHNIQUE - FinancePerso Couple Edition

> **Version:** 2.0  
> **Date:** 2026-02-28  
> **Statut:** ✅ TOUS les modules implémentés et testés

---

## 📝 RÉSUMÉ DE L'IMPLÉMENTATION

### ✅ Modules complétés

| Module | Description | Statut |
|--------|-------------|--------|
| **Module 1** | Configuration initiale (mappings cartes, paramètres couple) | ✅ Terminé |
| **Module 2** | Dashboard Couple avec confidentialité | ✅ Terminé |
| **Module 3** | Détection des virements internes | ✅ Terminé |
| **Module 4** | Vue Emprunts simplifiée | ✅ Terminé |

### 📁 Fichiers créés/modifiés

**Nouveaux fichiers :**
- `migrations/008_couple_edition.sql` - Tables couple (cartes, paramètres, virements)
- `migrations/009_loans.sql` - Tables emprunts (loans, loan_transactions)
- `modules/couple/__init__.py` - Package couple
- `modules/couple/card_mappings.py` - CRUD mappings cartes
- `modules/couple/couple_settings.py` - Paramètres couple
- `modules/couple/transfer_detector.py` - Détection virements
- `modules/couple/privacy_filters.py` - Filtres confidentialité
- `modules/couple/loans.py` - CRUD emprunts et liaison transactions
- `modules/ui/couple/__init__.py` - Package UI couple
- `modules/ui/couple/setup_wizard.py` - Assistant configuration
- `modules/ui/couple/dashboard.py` - Dashboard couple
- `modules/ui/couple/widgets.py` - Widgets réutilisables
- `modules/ui/couple/loans_view.py` - Vue emprunts
- `tests/test_couple_edition.py` - Tests modules 1-3
- `tests/test_couple_loans.py` - Tests module 4

**Fichiers modifiés :**
- `pages/9_Configuration.py` - Onglet Couple ajouté
- `pages/3_Synthèse.py` - Onglet Vue Couple ajouté
- `tests/conftest.py` - Migration SQL automatique pour tests

### 🧪 Tests

```bash
# Tests essentiels
pytest tests/test_essential.py -v  # ✅ 13 passed

# Tests Couple Edition (Modules 1-3)
pytest tests/test_couple_edition.py -v  # ✅ 11 passed

# Tests Emprunts (Module 4)
pytest tests/test_couple_loans.py -v  # ✅ 9 passed

# Tous les tests
pytest tests/test_essential.py tests/test_couple_edition.py tests/test_couple_loans.py -v  # ✅ 33 passed
```

---

---

## 🎯 OBJECTIF

Créer un dashboard "Couple" où :
- **Chacun voit ses propres détails** (transactions, catégories)
- **L'autre est visible en agrégats uniquement** (totaux, pas de libellés)
- **Le commun est détaillé** (transactions jointes)
- **Les virements internes sont identifiés et exclus** des stats de dépenses

---

## 🏗️ ARCHITECTURE DES DONNÉES

### Schéma minimal (réutilisation maximale)

```sql
-- ============================================
-- EXISTANT (à exploiter)
-- ============================================
-- transactions.card_suffix → "1234", "5678"
-- transactions.account_label → "COMPTE JOINT", "COURANT AURELIEN"
-- members → déjà configuré avec HOUSEHOLD/EXTERNAL

-- ============================================
-- NOUVEAU : Mappings Carte → Membre
-- ============================================
CREATE TABLE card_member_mappings (
    id INTEGER PRIMARY KEY,
    card_suffix TEXT UNIQUE NOT NULL,  -- "1234"
    member_id INTEGER,                 -- NULL = carte jointe/inconnue
    account_type TEXT,                 -- 'PERSONAL_A' | 'PERSONAL_B' | 'JOINT'
    label TEXT,                        -- "CB Perso Aurélien"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(id)
);

-- Index pour perf
CREATE INDEX idx_card_member ON card_member_mappings(card_suffix);
CREATE INDEX idx_tx_member ON transactions(card_suffix);

-- ============================================
-- NOUVEAU : Configuration Couple
-- ============================================
CREATE TABLE couple_settings (
    id INTEGER PRIMARY KEY,
    member_a_id INTEGER,  -- Référence vers members
    member_b_id INTEGER,
    joint_account_labels TEXT,  -- JSON ["COMPTE JOINT", "LIVRET COMMUN"]
    created_at TIMESTAMP
);
```

### Logique d'attribution (règles métier)

```python
def get_transaction_owner(transaction, current_user_id):
    """
    Détermine à qui appartient une transaction
    Retourne: 'ME', 'PARTNER', 'JOINT', 'UNKNOWN'
    """
    # 1. Chercher mapping carte → membre
    mapping = get_card_mapping(transaction.card_suffix)
    
    if mapping:
        if mapping.member_id == current_user_id:
            return 'ME'
        elif mapping.member_id is not None:
            return 'PARTNER'
        else:
            return 'JOINT'  # Carte explicitement jointe
    
    # 2. Fallback : libellé du compte
    if is_joint_account_label(transaction.account_label):
        return 'JOINT'
    
    # 3. Pattern fallback (si pas encore mappé)
    if 'ELISE' in transaction.label.upper():
        return 'PARTNER' if current_user_id == member_a_id else 'ME'
    
    return 'UNKNOWN'
```

---

## 📊 STRUCTURE DU DASHBOARD COUPLE

### Navigation par onglets

```
┌─────────────────────────────────────────────────────────────┐
│  🏠 ACCUEIL  │  📊 COUPLE  │  👤 MA VUE  │  ⚙️ CONFIG      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Onglet actif : 📊 COUPLE]                                 │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  FILTRE ACTIF : Février 2024  │  [▼ Mois] [▼ Année]    ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  💰 ÉPARGNE NETTE RÉELLE DU COUPLE                      ││
│  │                                                         ││
│  │  Revenus :     +5,000€    │  Commun :    +3,000€      ││
│  │  Dépenses :    -3,200€    │  Perso A :   +1,500€      ││
│  │  ──────────────────────   │  Perso B :   +500€        ││
│  │  Net :         +1,800€    │                           ││
│  │                             (détail cache des sources)  ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  ┌────────────────────────┐  ┌──────────────────────────┐   │
│  │   MES DÉPENSES         │  │   DÉPENSES PARTENAIRE    │   │
│  │   (détaillé)           │  │   (agrégé uniquement)    │   │
│  │                        │  │                          │   │
│  │  🍽️ Alimentation 450€  │  │  🍽️ Alimentation 380€   │   │
│  │  🚗 Transport    120€  │  │  🚗 Transport    200€   │   │
│  │  🎮 Loisirs       80€  │  │  🎮 Loisirs      150€   │   │
│  │  ──────────────        │  │  ──────────────          │   │
│  │  Total perso : 650€    │  │  Total perso :   730€   │   │
│  │  [Voir détail →]       │  │  [Confidentialité 🔒]    │   │
│  └────────────────────────┘  └──────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  💳 DÉPENSES COMMUNES (détaillé - visible par tous)    ││
│  │                                                         ││
│  │  🏠 Loyer        1,200€  │  ⚡ Électricité   120€      ││
│  │  🛒 Courses        450€  │  📱 Internet       40€      ││
│  │  ─────────────────────────────────────────────          ││
│  │  Total commun : 1,810€                                  ││
│  │  [Voir toutes les transactions →]                       ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  🔄 VIREMENTS INTERNES DÉTECTÉS (exclus des stats)      ││
│  │                                                         ││
│  │  15/02 : -500€ (Perso A → Joint)  │  [Valider ✓]       ││
│  │  10/02 : -200€ (Perso B → Joint)  │  [Valider ✓]       ││
│  │                                                         ││
│  │  Total masqué : 700€ (ne fausse pas le reste à vivre)   ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔒 RÈGLES DE CONFIDENTIALITÉ

```python
COUPLE_PRIVACY_RULES = {
    'ME': {
        'can_see_details': True,
        'can_see_transactions': True,
        'can_see_categories': True,
        'can_see_trends': True
    },
    'PARTNER': {
        'can_see_details': False,           # Pas les libellés individuels
        'can_see_transactions': False,      # Pas la liste des achats
        'can_see_categories': True,         # Oui : répartition par catégorie
        'can_see_trends': True,             # Oui : évolution mensuelle
        'can_see_total': True,              # Oui : montant total
        'can_see_count': True               # Oui : nombre de transactions
    },
    'JOINT': {
        'can_see_details': True,            # Tout est visible
        'can_see_transactions': True,
        'can_see_categories': True
    }
}
```

### Exemple de requête SQL filtrée

```sql
-- Vue pour le dashboard Couple (agrégats uniquement pour l'autre)
WITH transaction_ownership AS (
    SELECT 
        t.*,
        CASE 
            WHEN cm.member_id = :current_user_id THEN 'ME'
            WHEN cm.member_id IS NOT NULL THEN 'PARTNER'
            WHEN cm.member_id IS NULL AND cm.account_type = 'JOINT' THEN 'JOINT'
            ELSE 'UNKNOWN'
        END as owner_type
    FROM transactions t
    LEFT JOIN card_member_mappings cm ON t.card_suffix = cm.card_suffix
    WHERE t.date BETWEEN :start_date AND :end_date
      AND t.status = 'validated'
)

-- Mes détails (complet)
SELECT * FROM transaction_ownership 
WHERE owner_type = 'ME';

-- Partenaire (agrégats uniquement)
SELECT 
    category,
    COUNT(*) as transaction_count,
    SUM(amount) as total_amount
FROM transaction_ownership 
WHERE owner_type = 'PARTNER'
GROUP BY category;

-- Commun (détail complet)
SELECT * FROM transaction_ownership 
WHERE owner_type = 'JOINT';
```

---

## 🎯 MODULES À DÉVELOPPER (priorisés)

### Module 1 : Configuration initiale (1 jour)

**Page : `pages/9_Configuration.py` - Onglet "Comptes Couple"**

```python
def render_couple_setup():
    """Premier lancement : mapper les cartes"""
    st.header("🔧 Configuration Couple")
    
    # Étape 1 : Identifier qui est "Moi" vs "Partenaire"
    current_user = st.selectbox("Je suis :", ["Aurélien", "Elise"])
    
    # Étape 2 : Mapper les cartes détectées
    detected_cards = get_all_card_suffixes()
    
    for card in detected_cards:
        cols = st.columns([2, 2, 1])
        with cols[0]:
            st.text(f"Carte ****{card}")
        with cols[1]:
            owner = st.selectbox(
                "Propriétaire",
                ["Moi", "Partenaire", "Carte jointe", "Inconnu"],
                key=f"card_owner_{card}"
            )
        with cols[2]:
            if st.button("💾", key=f"save_card_{card}"):
                save_card_mapping(card, owner)
```

**Fichiers à créer :**
- `modules/db/card_mappings.py` - CRUD pour la table `card_member_mappings`
- `modules/db/couple_settings.py` - CRUD pour la table `couple_settings`

### Module 2 : Dashboard Couple (2-3 jours)

**Nouveau fichier : `modules/ui/couple_dashboard.py`**

```python
def render_couple_dashboard():
    """Dashboard principal avec confidentialité"""
    
    # Tabs : Vue Couple | Ma Vue | Emprunts
    tab_couple, tab_personal, tab_loans = st.tabs([
        "📊 Vue Couple", "👤 Ma Vue", "🏦 Emprunts"
    ])
    
    with tab_couple:
        render_couple_summary()  # Agrégats uniquement
    
    with tab_personal:
        render_personal_detail()  # Détail complet de l'utilisateur connecté
    
    with tab_loans:
        render_loans_overview()  # Vue simplifiée des emprunts


def render_couple_summary():
    """Vue agrégée respectant la confidentialité"""
    
    metrics = calculate_couple_metrics(
        user_id=st.session_state.current_user_id,
        month=st.session_state.selected_month
    )
    
    # KPIs globaux (visibles par tous)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Revenus couples", format_eur(metrics['total_income']))
    col2.metric("Dépenses totales", format_eur(metrics['total_expenses']))
    col3.metric("Épargne nette", format_eur(metrics['net_savings']))
    col4.metric("Reste à vivre", format_eur(metrics['remaining']))
    
    # Comparaison côte à côte (confidentialité respectée)
    cols = st.columns(2)
    
    with cols[0]:
        st.subheader("👤 Moi")
        render_personal_card(
            details=metrics['me'], 
            show_details=True
        )
    
    with cols[1]:
        st.subheader("👤 Partenaire")
        render_personal_card(
            details=metrics['partner'], 
            show_details=False  # 🔒 Agrégats uniquement
        )
```

### Module 3 : Détection des virements (1-2 jours)

**Fichier : `modules/couple/transfer_detector.py`**

```python
def detect_internal_transfers(start_date, end_date, threshold_days=2):
    """
    Algo simple : même montant, dates proches, comptes différents
    """
    query = """
    SELECT 
        t1.id as from_id,
        t2.id as to_id,
        t1.amount,
        t1.date as from_date,
        t2.date as to_date,
        ABS(JULIANDAY(t1.date) - JULIANDAY(t2.date)) as day_diff
    FROM transactions t1
    JOIN transactions t2 ON (
        t1.amount = -t2.amount  -- Montant opposé
        AND t1.card_suffix != t2.card_suffix  -- Cartes différentes
        AND ABS(JULIANDAY(t1.date) - JULIANDAY(t2.date)) <= :threshold
    )
    WHERE t1.date BETWEEN :start AND :end
      AND t1.amount < 0  -- t1 est un débit (sortie)
      AND t2.amount > 0  -- t2 est un crédit (entrée)
    ORDER BY day_diff ASC
    """
    
    return db.execute(query, {
        'threshold': threshold_days,
        'start': start_date,
        'end': end_date
    })
```

### Module 4 : Vue Emprunts simplifiée (1 jour)

**Fichier : `modules/couple/loan_view.py`**

```python
def render_loan_simple_view():
    """
    Vue simplifiée : juste le total restant dû et mensualité
    Pas besoin du tableau d'amortissement complet pour l'instant
    """
    
    loans = get_active_loans()
    
    for loan in loans:
        with st.container(border=True):
            cols = st.columns([3, 2, 2, 2])
            
            with cols[0]:
                st.markdown(f"**{loan['name']}**")
                st.caption(f"{loan['lender']}")
            
            with cols[1]:
                st.metric(
                    "Mensualité", 
                    f"{loan['monthly_payment']}€",
                    f"{loan['interest_rate']}%"
                )
            
            with cols[2]:
                st.metric(
                    "Capital restant", 
                    f"{loan['remaining_capital']}€"
                )
            
            with cols[3]:
                progress = (loan['paid_capital'] / loan['total_capital']) * 100
                st.progress(progress / 100, text=f"{progress:.0f}% remboursé")
```

---

## 📱 FLUX UTILISATEUR

### Premier lancement

```
1. Import CSV → Détection auto des cartes présentes
2. Configuration Couple :
   ├─ "Qui es-tu ?" (A ou B)
   ├─ "Quelle carte est à qui ?" (mapping visuel)
   └─ "Quels comptes sont communs ?"
3. Dashboard Couple disponible
```

### Usage quotidien

```
1. Import nouvelles transactions
2. Dashboard Couple s'actualise automatiquement
3. Vérification : "Virements internes détectés" → Valider
4. Discussion : "Tu as dépensé 800€ ce mois" (agrégat visible)
   (sans voir que c'était un cadeau surprise 😉)
```

---

## 🔧 DÉPENDANCES & INTÉGRATION

### Réutilisation du code existant

| Composant existant | Utilisation |
|-------------------|-------------|
| `members` | Utilisé pour définir Membre A / Membre B |
| `card_suffix` dans transactions | Clé pour l'attribution |
| `learning_rules` | Déjà utilisé, pas de changement |
| `budgets` | Sera filtré par membre/compte |
| Design System Vibe | Réutilisé pour la cohérence |

### Nouveaux fichiers à créer

```
modules/
├── couple/
│   ├── __init__.py
│   ├── transfer_detector.py      # Algo détection virements
│   ├── privacy_filters.py        # Règles confidentialité
│   └── metrics_calculator.py     # KPIs couple
└── ui/
    └── couple/
        ├── dashboard.py           # Vue principale
        ├── setup_wizard.py        # Config initiale
        └── widgets.py             # Composants réutilisables

pages/
└── (modifications)
    ├── 3_Synthèse.py             # + Onglet "Vue Couple"
    └── 9_Configuration.py        # + Section "Couple"
```

---

## ✅ CHECKLIST DE VALIDATION

**Avant livraison, vérifier :**

- [ ] Les cartes sont bien mappées à l'initialisation
- [ ] Je ne vois pas les transactions détaillées de l'autre
- [ ] Je vois bien mes propres détails
- [ ] Les transactions communes sont détaillées pour tous
- [ ] Les virements internes sont identifiés et masqués
- [ ] Le "Reste à vivre" est correct (hors virements)
- [ ] Les totaux s'additionnent correctement (A + B + Commun = Total)

---

## 📝 NOTES DE DÉVELOPPEMENT

### Points d'attention

1. **Migration DB** : Les nouvelles tables doivent être créées via le système de migrations existant
2. **Performance** : Les requêtes doivent rester rapides (< 200ms) même avec 10k+ transactions
3. **Cache** : Utiliser `@st.cache_data(ttl=60)` pour les calculs de métriques
4. **Tests** : Ajouter des tests pour les filtres de confidentialité

### Décisions validées ✅

- [x] **Le mapping des cartes** est déduit automatiquement des transactions existantes
- [x] **Système de validation des virements** : Oui, avec validation manuelle (UI dédiée)
- [x] **Les emprunts** peuvent être rattachés à un membre (PERSONAL_A/B) ou être communs (JOINT)

---

## 🚀 GUIDE D'UTILISATION

### 1. Première configuration

Aller dans **⚙️ Configuration → 💑 Couple** :
1. Définir **Membre A** et **Membre B**
2. Choisir **"Je suis..."** (celui qui utilise l'app)
3. Mapper les cartes détectées :
   - Perso A / Perso B / Commun
4. Définir les **libellés de comptes communs**

### 2. Dashboard Couple

Aller dans **📊 Synthèse → 💑 Vue Couple** :
- **Onglet Vue d'ensemble** :
  - Résumé global du foyer
  - Comparatif côte à côte (respect confidentialité)
  - Dépenses communes (détaillées)
  - Virements internes détectés
- **Onglet Emprunts** :
  - Liste des emprunts actifs
  - Progression de remboursement
  - Mensualités totales
  - Liaison transactions → emprunts

### 3. Confidentialité respectée

| Rôle | Visible |
|------|---------|
| **Moi** | Tout (transactions, libellés, catégories) |
| **Partenaire** | Agrégats uniquement (catégories, totaux) 🔒 |
| **Commun** | Tout (transactions jointes détaillées) |

### 4. Gestion des emprunts

Dans l'onglet **Emprunts** :
1. **Ajouter un emprunt** :
   - Nom, organisme, capital
   - Mensualité, taux, durée
   - Attribution (Perso A/B ou Commun)
2. **Lier des paiements** :
   - Détection auto des mensualités
   - Liaison manuelle possible
   - Suivi capital remboursé vs intérêts

---

*Dernière mise à jour : 2026-02-28*
