# ❓ Questionnaire - Plan de Migration

Réponds à ces questions pour établir le plan précis de migration de v5.6 Streamlit vers FinCouple React.

---

## 1. OBJECTIFS & VISION

### 1.1 Pourquoi migrer ?
- [ ] UI moderne et meilleure UX
- [ ] Performance (Streamlit trop lent)
- [ ] Fonctionnalités mobiles
- [ ] Apprendre React/TypeScript
- [ ] Préparer un déploiement web
- [ ] Autre : ________________

### 1.2 Quelle est la cible ?
- [ ] Remplacement complet de v5.6
- [ ] Coexistence (v5.6 pour admin, React pour usage)
- [ ] MVP rapide puis itération
- [ ] Autre : ________________

### 1.3 Timeline acceptable ?
- [ ] 2-3 semaines (core uniquement)
- [ ] 1-2 mois (fonctionnel complet)
- [ ] 3+ mois (tout porter)
- [ ] Pas de pression, qualité avant délai

---

## 2. ARCHITECTURE TECHNIQUE

### 2.1 Backend - Supabase remplacement
**Contexte** : FinCouple utilise Supabase (cloud), tu veux du local

- [ ] **Option A** : SQLite via Python FastAPI (comme v5.6)
  - Avantage : Même logique métier, migration données facile
  - Inconvénient : Nécessite Python backend en plus
  
- [ ] **Option B** : IndexedDB côté client uniquement
  - Avantage : 100% frontend, pas de backend
  - Inconvénient : Pas de sync, limité en taille
  
- [ ] **Option C** : Electron/Tauri (app desktop)
  - Avantage : App native avec SQLite embarqué
  - Inconvénient : Plus complexe, build nécessaire
  
- [ ] **Option D** : Autre ? ________________

### 2.2 Authentification
**Contexte** : v5.6 = session simple, FinCouple = Supabase Auth

- [ ] Pas d'auth (usage personnel uniquement)
- [ ] Auth simple (password local, 1 utilisateur)
- [ ] Auth multi-utilisateurs (comme FinCouple avec foyer)
- [ ] OAuth (Google, GitHub...)

### 2.3 Stockage données
- [ ] Une seule base (monoposte)
- [ ] Multi-device (sync nécessaire)
- [ ] Cloud optionnel (backup)

---

## 3. FEATURES - Quoi garder ?

### 3.1 Core (indispensable) - Tout cocher ce qui est MUST HAVE

**Import & Transactions**
- [ ] Import CSV multi-banques
- [ ] Mapping colonnes dynamique
- [ ] Catégorisation automatique (regex)
- [ ] Validation transactions
- [ ] Édition transactions
- [ ] Recherche transactions

**Dashboard & Analytics**
- [ ] KPIs (solde, revenus, dépenses, épargne)
- [ ] Graphique répartition (donut)
- [ ] Graphique évolution (line)
- [ ] Comparaison périodes

**Gestion**
- [ ] Comptes bancaires (perso/joint)
- [ ] Catégories custom
- [ ] Règles de catégorisation

### 3.2 Avancées (nice to have)

**Budget**
- [ ] Suivi budget vs réel
- [ ] Alertes dépassement
- [ ] Prévisions

**Couple**
- [ ] Validation croisée (transactions > 500€)
- [ ] Commentaires sur transactions
- [ ] Répartition équitable

**IA & Automation**
- [ ] Détection anomalies
- [ ] Prédiction budgets
- [ ] Suggestions catégorisation
- [ ] Assistant IA (API KIM)

**Export & Reporting**
- [ ] Export PDF
- [ ] Export Excel/CSV
- [ ] Rapports mensuels

**Gamification**
- [ ] Badges/défis
- [ ] Objectifs épargne
- [ ] Streaks

**Autres**
- [ ] Open Banking (import auto)
- [ ] Notifications
- [ ] Audit complet
- [ ] Recherche avancée

---

## 4. IA & API KIM

### 4.1 Quelles features IA veux-tu ?
- [ ] Catégorisation intelligente (supplément regex)
- [ ] Détection d'anomalies (transactions suspectes)
- [ ] Prédiction budgets mensuels
- [ ] Analyse de dépenses (insights)
- [ ] Assistant conversationnel (chat avec tes données)
- [ ] Génération de rapports

### 4.2 Quand l'IA doit-elle intervenir ?
- [ ] En temps réel (chaque import)
- [ ] Sur demande (bouton "Analyser")
- [ ] Périodique (récap hebdo/mensuel)

### 4.3 Contraintes API KIM
- [ ] Offline first (IA optionnelle)
- [ ] Cache des résultats
- [ ] Limite de coût/période

---

## 5. UX & DESIGN

### 5.1 Priorité UX
- [ ] Desktop first (comme v5.6)
- [ ] Mobile first (usage smartphone)
- [ ] Égal desktop/mobile

### 5.2 Thème
- [ ] Light only
- [ ] Dark only
- [ ] Toggle light/dark (actuellement dans FinCouple)

### 5.3 Workflow import
Comment tu importes tes données ?
- [ ] Batch mensuel (tout d'un coup)
- [ ] Régulier (plusieurs fois par mois)
- [ ] En temps réel (Open Banking)

### 5.4 Notifications
- [ ] Pas besoin
- [ ] In-app uniquement
- [ ] Email
- [ ] Push mobile (si PWA)

---

## 6. DONNÉES

### 6.1 Migration données v5.6
- [ ] Oui, tout migrer (471 transactions)
- [ ] Partiel (derniers 12 mois)
- [ ] Non, repartir à zéro

### 6.2 Si migration, quelles données ?
- [ ] Transactions
- [ ] Catégories custom
- [ ] Règles de catégorisation
- [ ] Comptes
- [ ] Budgets
- [ ] Historique/Stats

### 6.3 Archivage
- [ ] Garder v5.6 en parallèle (lecture)
- [ ] Exporter données v5.6 (backup)
- [ ] Pas besoin, migration suffit

---

## 7. DÉVELOPPEMENT

### 7.1 Approche
- [ ] Tout d'un coup (big bang)
- [ ] Par features (itérations)
- [ ] MVP rapide puis améliorations

### 7.2 Features MVP (minimum viable product)
Si tu devais choisir 5 features pour un MVP :
1. ___________________
2. ___________________
3. ___________________
4. ___________________
5. ___________________

### 7.3 Tests
- [ ] Tests unitaires obligatoires
- [ ] Tests E2E critiques
- [ ] Pas de tests (projet perso)
- [ ] Tests manuels uniquement

### 7.4 Documentation
- [ ] Complète (comme v5.6)
- [ ] Minimaliste
- [ ] Pas besoin (code clair)

---

## 8. DÉPLOIEMENT

### 8.1 Cible de déploiement
- [ ] Local uniquement (dev)
- [ ] Serveur perso (VPS)
- [ ] Cloud (Vercel/Netlify + backend)
- [ ] Electron (app desktop)
- [ ] Pas de déploiement (local only)

### 8.2 Multi-utilisateurs
- [ ] Moi uniquement
- [ ] Couple (2 personnes)
- [ ] Famille (3+ personnes)
- [ ] Potentiellement extensible

### 8.3 Sécurité
- [ ] Basique (projet perso)
- [ ] Standard (auth, validation)
- [ ] Renforcée (données sensibles)

---

## 9. CONTRAINTES

### 9.1 Budget
- [ ] Gratuit uniquement
- [ ] Peut payer pour hébergement/API
- [ ] Peut payer pour développement accéléré

### 9.2 Compétences
- [ ] Je veux apprendre React/TS
- [ ] Je veux solution clé en main
- [ ] Mix : apprendre + utiliser rapidement

### 9.3 Maintenance future
- [ ] Je maintiens moi-même
- [ ] Solution low-maintenance
- [ ] OK pour évolutions régulières

---

## 10. PRIORITÉS FINALES

### Classe ces aspects par priorité (1 = plus important)

| Aspect | Priorité (1-10) |
|--------|-----------------|
| Performance | ___ |
| UI moderne | ___ |
| Features complètes | ___ |
| Rapidité de dev | ___ |
| Mobile-friendly | ___ |
| Offline capable | ___ |
| Multi-utilisateurs | ___ |
| IA intégrée | ___ |
| Facilité maintenance | ___ |
| Sécurité | ___ |

---

## RÉPONSES ATTENDUES

Copie ce tableau et remplis tes réponses :

```markdown
## Mes choix

### 1. Objectifs
- 1.1 : [ ]
- 1.2 : [ ]
- 1.3 : [ ]

### 2. Architecture
- 2.1 : [ ]
- 2.2 : [ ]
- 2.3 : [ ]

### 3. Features Core (cocher)
- [ ] Import CSV
- [ ] ...

### 3. Features Avancées (cocher)
- [ ] Budget
- [ ] ...

### 4. IA
- 4.1 : [ ]
- 4.2 : [ ]
- 4.3 : [ ]

### 5. UX
- 5.1 : [ ]
- 5.2 : [ ]
- 5.3 : [ ]
- 5.4 : [ ]

### 6. Données
- 6.1 : [ ]
- 6.2 : [ ]
- 6.3 : [ ]

### 7. Développement
- 7.1 : [ ]
- 7.2 MVP : 1) 2) 3) 4) 5)
- 7.3 : [ ]
- 7.4 : [ ]

### 8. Déploiement
- 8.1 : [ ]
- 8.2 : [ ]
- 8.3 : [ ]

### 9. Contraintes
- 9.1 : [ ]
- 9.2 : [ ]
- 9.3 : [ ]

### 10. Priorités
- Performance : [1-10]
- UI moderne : [1-10]
- ...
```

---

**Prochaine étape** : Une fois ce questionnaire rempli, je génère le PLAN DE MIGRATION détaillé avec :
- Architecture technique choisie
- Schéma de données
- Roadmap par phase
- Estimations précises
- Tâches détaillées
