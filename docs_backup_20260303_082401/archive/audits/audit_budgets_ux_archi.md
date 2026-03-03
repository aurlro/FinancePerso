# Audit : Page "Suivi des Budgets" 
## Vue Architecte + Designer

---

## 🔴 Problèmes Critiques Identifiés

### 1. Alertes Budgétaires - Déséquilibre Information/Action

**Fichier:** `modules/ui/dashboard/sections.py` (lignes 78-138)

**Problèmes Architecte:**
- Logique d'affichage lourde : `render_transaction_drill_down` dans une boucle d'alertes
- Chaque alerte charge toutes les transactions (N+1 potentiel)
- Cache au niveau des prédictions mais pas au niveau des drill-downs
- Pas de gestion d'erreur si `df_month` filtré est vide

**Problèmes Designer:**
- 4 métriques en haut (trop abstraites), puis liste interminable
- Pas de priorisation visuelle (une alerte à 120% est traitée comme une à 85%)
- Drill-down effrayant : affiche TOUTES les transactions d'un coup
- Pas d'action corrective suggérée (juste de l'information)

**Recommandation:**
```python
# Structure proposée:
┌─────────────────────────────────────┐
│ 🔴 ALERTES CRITIQUES (>100%)        │  ← Prioritaire
│ [Action rapide] [Voir détails]      │
├─────────────────────────────────────┤
│ 🟠 ATTENTION (80-100%)              │  ← Secondaire  
│ [Conseil] [Ignorer]                 │
├─────────────────────────────────────┤
│ 🟢 OK - Conseils d'optimisation     │  ← Tertiaire
└─────────────────────────────────────┘
```

---

### 2. Prévisions Fin de Mois - Algorithme Naïf

**Fichier:** `modules/ui/dashboard/ai_insights.py` (lignes 8-81)

**Problèmes Architecte:**
- Calcul simpliste : `moyenne_journalière * jours_restants`
- Ne distingue pas les dépenses fixes déjà payées vs à venir
- Pas de prise en compte des saisonnalités
- Pas de validation croisée avec l'historique

**Problèmes Designer:**
- 3 cartes KPI sans contexte comparatif (vs mois précédent)
- Pas de scénarios (optimiste/réaliste/pessimiste)
- Message "💡 Moyenne..." trop technique
- Pas d'action suggérée ("Réduire les dépenses de X€")

**Exemple du problème:**
```python
# Actuel (simpliste):
avg_daily = exp_var / days_passed
proj_var = avg_daily * days_in_month  # ❌ Ignore que certains jours ont 0 dépense

# Devrait être:
# - Moyenne sur jours avec dépenses uniquement
# - Poids différent selon jour de semaine
# - Détection des dépenses fixes déjà passées
```

**Recommandation:**
- Scénarios : "Si vous continuez → X€ | Si vous réduisez de 10% → Y€"
- Alertes contextuelles : "Vos courses sont 20% plus élevées que d'habitude"
- Actions : boutons "Voir où économiser"

---

### 3. Budget Tracker - Manque de Contexte

**Fichier:** `modules/ui/dashboard/budget_tracker.py`

**Problèmes Architecte:**
- Pas de comparaison avec période précédente
- Calcul `num_months` fragile (dépend de `date_dt` présent)
- Pas de cache pour les calculs de dépenses
- Mapping catégorie/emoji pas cohérent avec le reste de l'app

**Problèmes Designer:**
- Barres de progression sans repères historiques
- "Dépassé de 50€" sans dire si c'est habituel ou non
- Pas de tendance (en augmentation/baisse)
- Affichage grille 3 colonnes cassé sur mobile
- Message "Aucun budget défini" sans CTA clair

**Recommandation:**
```
┌────────────────────────────────────┐
│ 🍽️ Alimentation    [=====>] 85%   │
│   850€ / 1000€    ↑ vs mars: +5%  │
│   [💡 Conseil] [📊 Détails]        │
└────────────────────────────────────┘
```

---

### 4. Évolution des Flux - Manque d'Insights

**Fichier:** `modules/ui/dashboard/evolution_chart.py`

**Problèmes Architecte:**
- Bon graphique mais pas d'analyse des données affichées
- Pas de détection d'anomalies (mois atypique)
- Pas de projection future

**Problèmes Designer:**
- Graphique "passif" - l'utilisateur doit interpréter
- Pas d'annotations sur les événements importants
- Zones surplus/déficit pas expliquées
- Pas de comparaison YoY (Year over Year)

---

## 🟡 Problèmes de Cohérence

### 5. Incohérences entre modules

| Aspect | Budget Tracker | Alertes | Prévisions |
|--------|---------------|---------|------------|
| Période | Multi-mois | Mois courant uniquement | Mois courant |
| Calcul dépenses | Sum brute | Avec prédiction | Variable uniquement |
| Fixed/Variable | ❌ Non | ❌ Non | ✅ Oui |
| Historique | ❌ Non | ❌ Non | ❌ Non |

**Problème:** L'utilisateur voit 3 visions différentes de ses budgets qui ne se parlent pas.

---

## 🟢 Opportunités d'Amélioration

### 6. Système de Recommandations Manquant

**Actuel:** L'app montre des données sans proposer d'actions.

**Devrait être:**
```
"Vous dépassez votre budget Courses de 20%"
    ↓
"3 transactions inhabituelles ce mois :"
  - Carrefour 150€ (habituellement 80€)
  - [Exclure] [Modifier catégorie] [Ignorer]"
    ↓
"Conseil : Activez les alertes en temps réel"
```

---

## 📐 Architecture Proposée (Refactoring)

### Nouvelle Structure

```
modules/ui/dashboard/budget/
├── __init__.py              # Export public
├── overview.py              # Vue d'ensemble (cartes principales)
├── alerts.py                # Gestion des alertes intelligentes
├── forecast.py              # Prévisions améliorées (scénarios)
├── tracking.py              # Suivi détaillé par catégorie
└── insights.py              # Recommandations et conseils
```

### Flux de Données Unifié

```python
# 1. Couche Données (cache 5min)
@st.cache_data(ttl=300)
def get_budget_context():
    return {
        'budgets': get_budgets(),
        'current_month': get_month_data(),
        'history': get_last_6_months(),
        'predictions': compute_predictions(),
        'patterns': detect_spending_patterns()
    }

# 2. Couche Métier
class BudgetAnalyzer:
    def detect_anomalies(self): ...
    def generate_scenarios(self): ...
    def get_recommendations(self): ...

# 3. Couche Présentation
render_budget_overview(context)
render_alerts_priority(context)
render_forecast_scenarios(context)
```

---

## 🎨 Design Proposé (Wireframes)

### Vue Mobile-First (1 colonne)

```
┌────────────────────────────┐
│ 🎯 Budgets & Prévisions    │
├────────────────────────────┤
│ 🔴 2 ALERTES CRITIQUES     │
│ Courses: 120% du budget    │
│ [Voir pourquoi] [Ajuster]  │
├────────────────────────────┤
│ 📊 Vue d'Ensemble          │
│ [Mini graphique trends]    │
│ ↑ +5% vs mois dernier      │
├────────────────────────────┤
│ 🔮 Projection Fin de Mois  │
│ Scénario actuel: -200€     │
│ [Si réduit courses → +50€] │
├────────────────────────────┤
│ 📋 Suivi par Catégorie     │
│ [Liste accordéon]          │
└────────────────────────────┘
```

### Vue Desktop (3 colonnes)

```
┌────────────┬────────────┬────────────┐
│ 🔴 Alertes │ 📈 Trends  │ 🔮 Prév.   │
│            │            │            │
│ [Liste     │ [Graph     │ [3 scénar. │
│  priorisée]│  histo]    │  cards]    │
│            │            │            │
├────────────┴────────────┴────────────┤
│ 📋 Détail par Catégorie              │
│ [Tableau interactif]                 │
└──────────────────────────────────────┘
```

---

## 🛠️ Plan d'Action Priorisé

### Phase 1: Quick Wins (1-2 jours)
1. **Corriger l'algorithme de prévision**
   - Distinction fixes/variables
   - Moyenne sur jours avec dépenses uniquement
   
2. **Améliorer les alertes**
   - Trier par sévérité (dépassement > 100% en premier)
   - Limiter le drill-down (5 dernières transactions)
   - Ajouter un bouton "Voir tout" qui ouvre page Validation

3. **Ajouter contexte historique**
   - "vs mois dernier" sur chaque budget
   - Flèche tendance ↑ ↓ →

### Phase 2: Amélioration UX (3-5 jours)
4. **Recommandations intelligentes**
   - Détecter transactions inhabituelles
   - Proposer actions contextuelles
   
5. **Scénarios de prévision**
   - Optimiste / Réaliste / Pessimiste
   - Slider "Et si je réduisais de X% ?"

6. **Refactoring composants**
   - Créer module `budget/` séparé
   - Unifier la logique métier

### Phase 3: Features Avancées (1-2 semaines)
7. **Alertes temps réel** (notifications)
8. **Budgets dynamiques** (ajustement auto selon saison)
9. **Objectifs d'épargne** liés aux budgets

---

## 📊 Métriques de Succès

- **Temps de chargement** : < 2s pour l'onglet complet
- **Taux d'action** : % d'utilisateurs qui cliquent sur une alerte
- **Précision prévisions** : écart < 10% à fin de mois
- **Satisfaction UX** : test utilisateur avec score SUS > 70

---

## Fichiers à Modifier

| Fichier | Priorité | Type |
|---------|----------|------|
| `modules/ui/dashboard/budget_tracker.py` | P0 | Refonte |
| `modules/ui/dashboard/sections.py` | P0 | Refactor |
| `modules/ui/dashboard/ai_insights.py` | P0 | Refonte algo |
| `modules/ai/budget_predictor.py` | P1 | Amélioration |
| `modules/ui/dashboard/budget/` (nouveau) | P1 | Création |

---

*Audit réalisé le 2 février 2026*
*Par: Architecte + Designer UX*
