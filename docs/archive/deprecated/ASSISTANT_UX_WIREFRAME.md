# Wireframe UX - Refonte Page Assistant

## 🎨 Vue d'ensemble : AVANT vs APRÈS

---

## ❌ AVANT (Structure Actuelle)

```
┌─────────────────────────────────────────────────────────────────┐
│  🕵️ Assistant d'Audit                                [layout]   │  ← Titre trompeur
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [🔎 Analyse & Anomalies] [📊 Tendances & Chat] [⚙️ Config]     │  ← Onglets confus
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  ONGLET 1 : Analyse & Anomalies                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  [🔎 Lancer l'analyse complète]              [Options]  │   │  ← Bouton énorme
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  --- Actions en masse ---                                       │
│  [Sélectionner tout] [Désélectionner] [Ignorer] [Créer règles] │  ← Trop dense
│                                                                 │
│  ⚠️ Incohérence : Uber                                       │
│  ├─ Détails : Classé comme : Transport, Alimentation         │
│  ├─ [ ] Checkbox [Corriger] [Ignorer] [Appliquer]            │
│  └─ 10 transactions similaires...                            │
│                                                                 │
│  ⚠️ Suspicion IA : McDo                                      │
│  ├─ ...                                                      │
│                                                                 │
│  --- (scroll infini) ---                                        │
│                                                                 │
│  🎯 Anomalies de Montant                                        │
│  [Analyser les anomalies 🔍]                                    │
│  (encore une section avec des expanders similaires)            │  ← Répétitif
│                                                                 │
│  ═══════════════════════════════════════════════════════════   │
│                                                                 │
│  ONGLET 2 : Tendances & Chat                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  [ ] Exclure virements internes                         │   │
│  │  [Analyser les tendances 📈]                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  📊 Insights Détectés                                           │
│  ▶ Augmentation des dépenses Alimentation (+23%)             │
│                                                                 │
│  ──────────────────────────────────────────────────────────    │
│  💬 Assistant Conversationnel                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  💡 Commencez par une question suggérée :               │   │
│  │  [Quelles sont mes grosses dépenses ?]                  │   │
│  │  [Combien en restaurants ?]                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  👤 Quelles sont mes plus grosses dépenses ?            │   │
│  │  🤖 Vos plus grosses dépenses ce mois sont...           │   │
│  └─────────────────────────────────────────────────────────┘   │
│  [Posez votre question...________________________] [Envoyer]   │
│                                                                 │
│  ═══════════════════════════════════════════════════════════   │
│                                                                 │
│  ONGLET 3 : Configuration                                       │
│  [🤖 Config Auto] [📅 Abonnements] [⚙️ Manuel]                 │
│                                                                 │
│  --- SOUS-ONGLET 1 : Config Auto ---                            │
│  🏗️ Configuration Assistée                                      │
│  [Lancer l'analyse 🚀]                                          │
│  ...                                                            │
│                                                                 │
│  --- SOUS-ONGLET 2 : Abonnements ---                            │
│  📅 Détection des Abonnements                                   │
│  [KPI] [KPI]                                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Tableau des abonnements...                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  --- (BUG : Section abonnements DUPLIQUÉE en bas !) ---        │  ← 🔴 CRITIQUE
│  Détection des Abonnements                                      │
│  [KPI] [KPI]                                                    │
│  ...                                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ APRÈS (Nouvelle Structure Proposée)

```
┌─────────────────────────────────────────────────────────────────┐
│  🤖 Assistant IA                                          [⚙️]  │  ← Titre cohérent
│  Votre conseiller financier intelligent                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┬────────────────┬────────────────┬───────────┐ │
│  │ 🤖 Tableau   │ 📊 Analytics   │ 🎯 Audit       │ ⚙️ Config │ │  ← Navigation claire
│  │   de bord    │    & Trends    │               │           │ │
│  └──────────────┴────────────────┴────────────────┴───────────┘ │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🏠 TABLEAU DE BORD (Vue par défaut)                           │
│  ═══════════════════════════════════════════════════════════   │
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │ 📊 STATUT GLOBAL    │  │ 🎯 ACTIONS RAPIDES  │              │
│  │                     │  │                     │              │
│  │  1,234 transactions │  │  🎬 Lancer un audit │  ← CTA clair │
│  │  12 règles actives  │  │     complet         │              │
│  │  3 budgets définis  │  │                     │              │
│  │                     │  │  📈 Voir tendances  │              │
│  │  [Dernier import    │  │                     │              │
│  │   il y a 2 jours]   │  │  💬 Poser une Q     │              │
│  └─────────────────────┘  └─────────────────────┘              │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  📋 RÉSUMÉ DES ANOMALIES DÉTECTÉES                      │   │
│  │                                                         │   │
│  │  ┌──────────┬──────────┬──────────┬──────────────────┐ │   │
│  │  │ ⚠️ 5     │ 🤖 3     │ ✅ 12    │ [Voir détails →] │ │   │
│  │  │ Incohér. │ Suspic.  │ Corrigés│                  │ │   │
│  │  └──────────┴──────────┴──────────┴──────────────────┘ │   │
│  │                                                         │   │
│  │  Dernière analyse : il y a 3 jours                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  💡 INSIGHT DU JOUR                                     │   │
│  │                                                         │   │
│  │  "Vos dépenses Alimentation ont augmenté de 23% ce      │   │
│  │   mois. Cela correspond à 4 restaurants de plus."       │   │
│  │                                                         │   │
│  │                              [Explorer →]               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 ONGLET : ANALYTICS & TRENDS

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 Analytics & Trends                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  FILTRES RAPIDES                                        │   │
│  │  Période : [Ce mois ▼]  vs  [Mois précédent ▼]         │   │
│  │  [✓] Exclure virements internes  [✓] Exclure épargne   │   │
│  │                                          [🔄 Analyser] │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │  📈 ÉVOLUTION       │  │  🔄 COMPARAISON     │              │
│  │                     │  │                     │              │
│  │   [Graphique        │  │   Ce mois    vs     │              │
│  │    courbe]          │  │   ─────────────     │              │
│  │                     │  │   Alim.   €1,234    │              │
│  │                     │  │   →  +€234 (+23%)   │  ← En vert   │
│  │                     │  │   ─────────────     │              │
│  │                     │  │   Transp. €456      │              │
│  │                     │  │   →  -€50  (-10%)   │  ← En vert   │
│  │                     │  │   ─────────────     │              │
│  │                     │  │   [Voir tout →]     │              │
│  └─────────────────────┘  └─────────────────────┘              │
│                                                                 │
│  ═══════════════════════════════════════════════════════════   │
│                                                                 │
│  🎯 INSIGHTS DÉTECTÉS                                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  🔥 Anomalie détectée                                   │   │
│  │                                                         │   │
│  │  "Vous avez dépensé 3x plus en Shopping cette semaine"  │   │
│  │                                                         │   │
│  │  [Voir les 12 transactions]  [Créer une alerte]         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  📅 Pattern détecté                                     │   │
│  │                                                         │   │
│  │  "Netflix prélevé le 5 de chaque mois - €15.99"         │   │
│  │                                                         │   │
│  │  [Gérer l'abonnement]  [Voir l'historique]              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 ONGLET : AUDIT (Vue détaillée)

```
┌─────────────────────────────────────────────────────────────────┐
│  🎯 Audit Qualité des Données                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  PROGRESSION DE L'AUDIT                                 │   │
│  │                                                         │   │
│  │  Analyse des incohérences ████████████░░░░░░  67%      │   │
│  │  Analyse IA               ████████░░░░░░░░░░  50%      │   │
│  │  Anomalies de montant     En attente...                │   │
│  │                                                         │   │
│  │              [⏸️ Pause]  [🔄 Relancer l'audit complet] │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────┬──────────┬──────────┬──────────┐                 │
│  │ [🔴 5]   │ [🟡 3]   │ [🔵 12]  │ [⚫ 8]   │                 │
│  │ À        │ En       │ Corrigés │ Ignorés  │                 │
│  │ corriger │ cours    │          │          │                 │
│  └──────────┴──────────┴──────────┴──────────┘                 │
│                                                                 │
│  ═══════════════════════════════════════════════════════════   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  🔴 INCOHÉRENCE DE CATÉGORISATION                       │   │  ← Carte claire
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │   │
│  │                                                         │   │
│  │  Libellé : UBER                                         │   │
│  │  Problème : Classé comme "Transport" ET "Loisirs"      │   │
│  │                                                         │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │  📋 Transactions concernées (12)                │   │   │
│  │  │  ─────────────────────────────────────────────  │   │   │
│  │  │  15/01  UBER TRIP    €12.50  → Transport   [✏️] │   │   │
│  │  │  14/01  UBER EATS    €24.90  → Loisirs     [✏️] │   │   │
│  │  │  10/01  UBER TRIP    €8.50   → Transport   [✏️] │   │   │
│  │  │  ...                                            │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                                                         │   │
│  │  [✅ Tout mettre en Transport]  [🏷️ Tout mettre en     │   │
│  │       Loisirs]  [🧠 Créer règle auto]  [🗑️ Ignorer]   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  🤔 SUSPICION IA                                        │   │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │   │
│  │                                                         │   │
│  │  Libellé : MCDONALD'S                                   │   │
│  │  Catégorie actuelle : Santé ⚠️                          │   │
│  │  Suggestion : Alimentation                              │   │
│  │  Confiance : 94%                                        │   │
│  │                                                         │   │
│  │  [✅ Appliquer]  [❌ Refuser]  [🏷️ Autre catégorie]     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [📋 Sélectionner tout]  [🗑️ Ignorer la sélection]             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💬 CHAT INTÉGRÉ (Mode conversationnel)

```
┌─────────────────────────────────────────────────────────────────┐
│  💬 Assistant Conversationnel                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  🤖 Bonjour ! Je suis votre assistant financier.        │   │
│  │     Que souhaitez-vous savoir aujourd'hui ?            │   │
│  │                                                         │   │
│  │     Voici ce que je peux faire pour vous :             │   │
│  │     • Analyser vos tendances de dépenses               │   │
│  │     • Identifier des anomalies                         │   │
│  │     • Vous aider à catégoriser vos transactions        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  👤 Quelles sont mes plus grosses dépenses ce mois ?   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  🤖 Voici vos 3 plus grosses catégories ce mois :      │   │
│  │                                                         │   │
│  │     1. 🏠 Logement      : €1,200  (Loyer)              │   │
│  │     2. 🍽️ Alimentation  : €534   (+23% vs mois dernier)│   │
│  │     3. 🚗 Transport     : €289   (-5% vs mois dernier) │   │
│  │                                                         │   │
│  │     📊 [Voir le graphique]  [💾 Exporter]              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  👤 Pourquoi j'ai dépensé plus en alimentation ?       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  🤐 J'ai analysé vos données :                          │   │
│  │                                                         │   │
│  │     Cette augmentation vient principalement de :       │   │
│  │     • 4 restaurants supplémentaires                    │   │
│  │     • Uber Eats : +€67 (3 commandes de plus)           │   │
│  │                                                         │   │
│  │     🔍 [Explorer les transactions]                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  💡 Suggestions rapides :                               │   │
│  │  [📈 Tendances] [🎯 Budgets] [⚠️ Anomalies] [📅 Récurrences]│  │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Posez votre question...                        [📎] [➤] │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ ONGLET : CONFIGURATION

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚙️ Configuration de l'Assistant                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  🤖 MODÈLE IA ACTIF                                     │   │
│  │                                                         │   │
│  │  Gemini 1.5 Flash (Google)                              │   │
│  │  Status : ✅ Connecté                                   │   │
│  │                                                         │   │
│  │  [Changer de modèle]  [Tester la connexion]             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────┬──────────────┬──────────────┐                │
│  │ [🤖 Auto]    │ [📅 Abon.]   │ [⚙️ Manuel]  │                │
│  └──────────────┴──────────────┴──────────────┘                │
│                                                                 │
│  ─── SOUS-ONGLET : CONFIGURATION AUTO ─────────────────────   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  🏗️ DÉTECTION AUTOMATIQUE                               │   │
│  │                                                         │   │
│  │  L'IA analysera vos transactions pour détecter :       │   │
│  │  ✓ Vos revenus réguliers (salaire, etc.)               │   │
│  │  ✓ Vos charges fixes (loyer, électricité, etc.)        │   │
│  │  ✓ Vos abonnements (Netflix, Spotify, etc.)            │   │
│  │                                                         │   │
│  │  [🚀 Lancer la détection]                               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  📋 RÉSULTATS DE L'ANALYSE (3 trouvés)                  │   │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │   │
│  │                                                         │   │
│  │  💰 SALAIRE (Revenus)              ✅ Confirmé         │   │
│  │     ~€2,500/mois - Dernière : 01/02/2025               │   │
│  │     [Voir] [Modifier]                                  │   │
│  │                                                         │   │
│  │  🏠 LOYER (Logement)               ⏳ À confirmer      │   │
│  │     ~€850/mois - Dernière : 05/02/2025                 │   │
│  │     [✅ C'est bien ça] [❌ Non] [✏️ Modifier]            │   │
│  │                                                         │   │
│  │  📺 NETFLIX (Abonnements)          ✅ Confirmé         │   │
│  │     €15.99/mois - Prélèvement le 12                    │   │
│  │     [Voir] [Modifier]                                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Changements UX Clés

### 1. **Navigation Clarifiée**

| Avant | Après |
|-------|-------|
| "Analyse & Anomalies" | "🤖 Tableau de bord" - Vue d'ensemble |
| "Tendances & Chat" | "📊 Analytics & Trends" - Focus insights |
| "Configuration" | "🎯 Audit" - Contrôle qualité dédié |
| (Mélangé) | "⚙️ Config" - Paramétrage IA |

### 2. **Hiérarchie Visuelle**

```
AVANT : Tout au même niveau, surcharge visuelle
APRÈS : 
├── 🏠 Dashboard (arrivée par défaut)
│   └── Vue résumée + CTA vers les actions
├── 📊 Analytics (analyse approfondie)
│   └── Tendances + Insights + Chat intégré
├── 🎯 Audit (contrôle qualité)
│   └── Anomalies + Corrections en masse
└── ⚙️ Config (paramétrage)
    └── IA + Auto-config + Manuel
```

### 3. **Patterns d'Interaction**

| Élément | Avant | Après |
|---------|-------|-------|
| **Audit** | Bouton géant + liste interminable | Progression visible + cartes d'anomalies |
| **Anomalies** | Expander dense | Carte avec actions contextuelles |
| **Chat** | Section basique | Interface conversationnelle avec suggestions |
| **Résultats** | Affichage immédiat | Vue résumée + "Voir détails" |

### 4. **Micro-interactions**

- ✅ **Progress bar** pendant l'analyse avec étapes explicites
- ✅ **Badges visuels** pour le statut (🔴🟡🟢) 
- ✅ **Actions groupées** : corriger/ignorer par lot
- ✅ **Suggestions contextuelles** dans le chat

---

## 🔧 Architecture Technique (Refonte)

```
pages/5_Assistant.py
├── render_dashboard()      # Vue d'accueil
├── render_analytics()      # Tendances + Chat
├── render_audit()          # Contrôle qualité
└── render_config()         # Paramétrage

modules/ui/assistant/
├── dashboard_tab.py        # Logique tableau de bord
├── analytics_tab.py        # Logique analytics
├── audit_tab.py            # Logique audit
├── config_tab.py           # Logique configuration
├── components.py           # Composants réutilisables
│   ├── AnomalyCard()
│   ├── InsightCard()
│   ├── ChatInterface()
│   └── ProgressTracker()
└── state.py                # Gestion état centralisée

modules/ai/audit_engine.py  # Logique métier déplacée
```

---

## ✅ Checklist Implémentation

- [ ] Créer les nouveaux modules dans `modules/ui/assistant/`
- [ ] Déplacer la logique métier dans `modules/ai/audit_engine.py`
- [ ] Refondre `pages/5_Assistant.py` (~150 lignes max)
- [ ] Corriger le bug de duplication (section abonnements)
- [ ] Unifier la gestion du state
- [ ] Ajouter les composants de carte/insight
- [ ] Tests de non-régression

---

*Document généré pour validation UX avant implémentation*
