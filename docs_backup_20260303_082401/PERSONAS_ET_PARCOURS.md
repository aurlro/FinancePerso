# 👥 PERSONAS ET PARCOURS UTILISATEURS

> **Guide visuel** - Comprendre les utilisateurs de FinancePerso

---

## 🎯 LES 4 PERSONAS

```
┌─────────────────────────────────────────────────────────────────┐
│ MARIE - "La Contrôleuse"                                        │
├─────────────────────────────────────────────────────────────────┤
│ 👤 35 ans, salariée, suit ses dépenses chaque semaine          │
│ 📱 Usage: 2-3x/semaine, sessions courtes (5-10 min)            │
│ 💪 Force: Discipline, veut rester maîtriser                    │
│ 😰 Frustration: Peut pas explorer rapidement une anomalie      │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│ THOMAS - "L'Optimiseur"                                         │
├─────────────────────────────────────────────────────────────────┤
│ 👤 42 ans, cadre, cherche à optimiser ses finances             │
│ 📱 Usage: Quotidien, sessions longues (20-30 min)              │
│ 💪 Force: Technique, explore toutes les features               │
│ 😰 Frustration: Pas d'historique des prix d'abonnements        │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│ SOPHIE - "La Débutante"                                         │
├─────────────────────────────────────────────────────────────────┤
│ 👤 28 ans, freelance, débute dans la gestion financière        │
│ 📱 Usage: Irrégulier, besoin de réassurance                    │
│ 💪 Force: Motivée à apprendre                                  │
│ 😰 Frustration: Complexe, peur de faire des erreurs            │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│ PIERRE - "Le Famille"                                           │
├─────────────────────────────────────────────────────────────────┤
│ 👤 45 ans, en couple, gère les finances familiales             │
│ 📱 Usage: Hebdomadaire, focus répartition                      │
│ 💪 Force: Organisé, vue globale                                │
│ 😰 Frustration: Attribution des dépenses laborieuse            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛤️ PARCOURS MARIE (Contrôleuse)

### Scénario: Elle détecte une augmentation de dépenses

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Ouvre   │────▶│ Voir    │────▶│ Clique  │────▶│ Explore │
│ l'app   │     │ alerte  │     │ Explorer│     │ les tx  │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │                                              │
     │                                              ▼
     │                                         ┌─────────┐
     │                                         │ Comprend│
     │                                         │ d'où    │
     │                                         │ vient   │
     │                                         │ l'excès │
     │                                         └─────────┘
     │                                              │
     │                                              ▼
     │                                         ┌─────────┐
     │                                         │ Décide: │
     │                                         │ Règle   │
     │                                         │ ou      │
     │                                         │Exception│
     │                                         └─────────┘
     │                                              │
     └──────────────────────────────────────────────┘
                      Satisfaction!
```

### Points de friction actuels:
❌ "Explorer" ne montrait rien avant (maintenant ✅)  
❌ Dashboard lent à charger  
❌ Pas de contexte historique  

### Solutions mises en place:
✅ Vue d'exploration avec métriques  
⚠️ Pagination en cours (Phase 1)  
⚠️ Caching en cours (Phase 1)  

---

## 🛤️ PARCOURS THOMAS (Optimiseur)

### Scénario: Il veut optimiser ses abonnements

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Reçoit  │────▶│ Voir    │────▶│ Analyse │
│ alerte  │     │évolution│     │ historiq│
│ +20%    │     │ prix    │     │ ue      │
└─────────┘     └─────────┘     └─────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
              ┌─────────┐       ┌─────────┐       ┌─────────┐
              │ Accepte │       │ Négocie │       │ Résilie │
              │ prix    │       │ (rappel)│       │         │
              └─────────┘       └─────────┘       └─────────┘
```

### Points de friction actuels:
❌ Aucun historique des prix avant (maintenant ✅)  
❌ Pas d'actions concrètes sur les zombies  
❌ Requêtes analytiques lentes  

### Solutions mises en place:
✅ Vue évolution avec timeline des changements  
⚠️ Actions zombies en cours (Phase 2)  
⚠️ Index DB en cours (Phase 1)  

---

## 🛤️ PARCOURS SOPHIE (Débutante)

### Scénario: Premier import de relevé bancaire

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Premier │────▶│ Téléchar│────▶│ VOIT    │────▶│ Corrige │
│ import  │     │ ge CSV  │     │ PREVIEW │     │ si      │
│         │     │         │     │ avant   │     │ besoin  │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
                                                 │
                                                 ▼
┌─────────┐     ┌─────────┐     ┌─────────┐
│✅ Import │◀────│ Confirme│◀────│ Valide  │
│  réussi │     │ définit.│     │ données │
└─────────┘     └─────────┘     └─────────┘
     │
     ▼
┌─────────┐
│ Guide   │
│ vers    │
│ validation
└─────────┘
```

### Points de friction actuels:
❌ Pas de preview avant (maintenant ✅)  
❌ Peur de faire des erreurs  
❌ Pas de "undo" possible  

### Solutions prévues:
✅ Preview d'import  
⚠️ Corbeille (Semaine 3)  
⚠️ Onboarding guidé (Phase 2)  

---

## 🛤️ PARCOURS PIERRE (Famille)

### Scénario: Attribution des dépenses du week-end

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Import  │────▶│ Voir    │────▶│ Attribue│────▶│ Vérifie │
│ week-end│     │ tx sans │     │ rapide  │     │ répart. │
│         │     │ membre  │     │ par lot │     │         │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
                                                       │
                                                       ▼
                                                ┌─────────┐
                                                │ Vue     │
                                                │ perso   │
                                                │ /conjoint│
                                                └─────────┘
```

### Points de friction actuels:
❌ Attribution une par une lente  
❌ Pas de vue consolidée par membre  
❌ Pas de répartition automatique  

### Solutions prévues:
⚠️ Attribution par lot (Phase 3)  
⚠️ Vue famille (Phase 3)  
⚠️ Règles d'attribution automatique (Phase 4)  

---

## 📊 MATRICE DES BESOINS

| Besoin | Marie | Thomas | Sophie | Pierre | Priorité |
|--------|:-----:|:------:|:------:|:------:|:--------:|
| Performance | 🔴 | 🔴 | 🟡 | 🟡 | **P0** |
| Preview import | 🟡 | 🟡 | 🔴 | 🟡 | **P0** |
| Exploration anomalies | 🔴 | 🔴 | 🟡 | 🟡 | **P1** |
| Suivi abonnements | 🟡 | 🔴 | 🟢 | 🟡 | **P1** |
| Onboarding guidé | 🟢 | 🟢 | 🔴 | 🟢 | **P1** |
| Multi-membres | 🟢 | 🟢 | 🟢 | 🔴 | **P2** |
| Prédictions IA | 🟡 | 🔴 | 🟢 | 🟡 | **P2** |

**Légende**: 🔴 Critique | 🟡 Important | 🟢 Secondaire

---

## 🎯 SYNTHÈSE DES PRIORITÉS PAR PERSONA

### Marie veut:
1. ⚡ Une app rapide (dashboard < 2s)
2. 🔍 Explorer rapidement une anomalie
3. 📊 Comprendre d'où viennent les variations

### Thomas veut:
1. 📈 Suivre l'évolution de ses abonnements
2. ⚡ Analyses rapides (requêtes < 100ms)
3. 🤖 Automatisation des tâches répétitives

### Sophie veut:
1. 🛡️ Ne pas avoir peur de faire des erreurs
2. 📖 Être guidée pas à pas
3. ✅ Vérifier avant de valider

### Pierre veut:
1. 👥 Gérer facilement les membres de sa famille
2. 📊 Vue consolidée par personne
3. ⚡ Attribution rapide des dépenses

---

## ✅ CE QUI EST DÉJÀ EN PLACE

### ✅ Pour Marie
- [x] Exploration des pics de dépenses fonctionnelle
- [x] Vue détaillée avec transactions

### ✅ Pour Thomas
- [x] Suivi des évolutions d'abonnements
- [x] Historique des changements de prix
- [x] Tableau mensuel des montants

### ✅ Pour tous
- [x] Actions concrètes sur les suggestions
- [x] Feedback visuel après action
- [x] Interface de mapping membre fonctionnelle

---

## ⚠️ CE QUI RESTE À FAIRE (Phase 1)

### Pour tous (Critique)
- [ ] **Performance**: Index DB, pagination, caching
- [ ] **Sécurité**: Backup automatique quotidien
- [ ] **Fiabilité**: Corbeille (soft delete)

### Pour Sophie (Important)
- [ ] **Preview import**: Voir avant de valider
- [ ] **Feedback**: Barre de progression
- [ ] **Documentation**: Guide débutant

### Pour Pierre (Phase 2-3)
- [ ] **Multi-membres**: Attribution par lot
- [ ] **Vue famille**: Consolidation par membre

---

## 📈 MÉTRIQUES DE SUCCÈS PAR PERSONA

### Marie sera satisfaite quand:
- [ ] Dashboard charge en < 2s
- [ ] Peut explorer une anomalie en 3 clics
- [ ] Ne perd pas de temps à attendre

### Thomas sera satisfait quand:
- [ ] Requêtes analytiques < 100ms
- [ ] Voir historique complet d'un abonnement
- [ ] Peut exporter ses analyses

### Sophie sera satisfaite quand:
- [ ] Import avec preview la rassure
- [ ] Peut annuler une erreur (corbeille)
- [ ] Trouve de l'aide facilement

### Pierre sera satisfait quand:
- [ ] Attribution par lot fonctionne
- [ ] Vue famille claire
- [ ] Répartition automatique possible

---

## 🎨 PRINCIPES DE DESIGN PAR PERSONA

### Pour Marie: "Efficacité"
- Actions rapides (1-2 clics)
- Feedback immédiat
- Pas de distractions

### Pour Thomas: "Contrôle"
- Toutes les données disponibles
- Personnalisation possible
- Historique complet

### Pour Sophie: "Rassurance"
- Preview avant action
- Confirmations claires
- Possibilité d'annuler

### Pour Pierre: "Clarté"
- Vue consolidée
- Attribution simple
- Distinction claire des membres

---

## 🔮 VISION FUTURE

```
Phase 1 (Maintenant): Fondations
├── Performance ⚡
├── Sécurité 🔒
└── Fiabilité ✅

Phase 2 (Mois 2): UX
├── Onboarding guidé 🎓
├── Intelligence actionnable 🧠
└── Configuration simplifiée ⚙️

Phase 3 (Mois 3): Features
├── Gestion abonnements 📊
├── Multi-membres 👥
└── Projections 📈

Phase 4 (Mois 4): IA
├── Prédictions 🔮
├── Automatisation 🤖
└── Insights personnalisés 💡
```

---

**Document de référence**  
*À consulter avant chaque développement de feature*
