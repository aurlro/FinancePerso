
# 💰 FinCouple — Gestionnaire Financier de Couple

## ✅ Phase 1 : Fondations (terminé)
- **Design System** : Thème premium Apple-esque avec mode sombre/clair natif, palette gris neutres + accent émeraude
- **Auth & Profils** : Inscription/connexion sécurisée, profils couple (Personne A / Personne B), gestion de session
- **Base de données** : Tables pour comptes bancaires, transactions, catégories, règles de catégorisation, virements internes détectés

## ✅ Phase 2 : Import & Moteur de données (terminé)
- **Import CSV multi-banques** : Upload avec mapping dynamique des colonnes, prévisualisation avant import, support multi-formats
- **Attribution automatique** : Chaque import est lié à un compte (Perso A, Perso B, Joint)
- **Détection virements internes** : Matching automatique par montant inverse + date proche + comptes différents
- **Moteur de catégorisation Regex** : ~15 catégories standard, application automatique à l'import
- **Catégorisation IA** : Edge Function pour catégoriser les transactions par lot via IA

## ✅ Phase 3 : Dashboard & Visualisations (terminé)
- **Vue globale mensuelle** : Reste à vivre, total dépenses, épargne nette (hors virements internes)
- **Graphiques** : Répartition par catégorie (donut), évolution mensuelle (line chart), comparatif par type de compte
- **Bilan mensuel** : Récapitulatif automatique du mois avec widget sur le dashboard
- **Équilibre du couple** : Balance des contributions avec ratio configurable

## ✅ Phase 4 : Gestion & Configuration (terminé)
- **Gestion des comptes bancaires** : Ajouter/modifier les comptes et leur type
- **Gestion des règles Regex** : Interface pour créer, tester et modifier les règles avec prévisualisation live
- **Liste des transactions** : Tableau filtrable/triable avec recherche, modification inline, actions groupées
- **Attribution IA** : Edge Function pour attribuer les transactions aux membres par analyse des libellés
- **Budgets par catégorie** : Définition de plafonds mensuels avec alertes visuelles
- **Objectifs d'épargne** : Suivi des objectifs avec progression visuelle
- **Abonnements** : Détection et suivi des dépenses récurrentes

## ✅ Phase 5 : Onboarding & Polish (terminé)
- **Onboarding guidé** : Stepper 5 étapes (Bienvenue → Foyer → Membres → Comptes → Import)
- **Persistance onboarding** : `onboarding_completed_at` en DB, ne réapparaît plus après complétion
- **Animations de transition** : `slide-in-up` entre les étapes du stepper
- **Cache cleanup** : Vidage React Query au signOut pour éviter les données stale

## ✅ Phase 6 : Intelligence & Automatisation (terminé)
- **Catégorisation auto-apprenante** : Quand un utilisateur corrige une catégorie, une règle regex est créée automatiquement à partir des mots-clés du libellé (`auto-rule-generator.ts`)
- **Attribution auto-apprenante** : Quand un utilisateur attribue manuellement une transaction, une règle d'attribution regex est créée automatiquement
- **Cascade d'attribution à l'import** : 1) Compte personnel → owner, 2) Card identifier → membre, 3) Règles regex d'attribution, 4) Sinon null (IA ou manuel)
- **IA enrichie par l'historique** : L'Edge Function `attribute-ai` inclut les 50 dernières attributions confirmées dans le prompt pour un contexte amélioré
- **Prévisions budgétaires** : Widget `BudgetForecast` sur le dashboard — projection linéaire des dépenses par catégorie basée sur le rythme du mois en cours vs moyenne des 3 derniers mois, avec barres de progression double (réel vs projeté)
- **Alertes intelligentes améliorées** : 3 niveaux (info >60%, warning >80%, danger >100%) avec icônes distinctes et projection de fin de mois intégrée dans chaque alerte
- **Apprentissage automatique des cartes** : Lors de l'attribution manuelle d'une transaction, si le libellé contient un identifiant de carte (CB *1234), proposition automatique d'associer la carte au membre via toast interactif

## Navigation & UX
- **Sidebar minimaliste** : Dashboard, Transactions, Import, Comptes, Règles, Analytics, Bilan mensuel, Équilibre, Abonnements, Paramètres
- **Responsive** : Desktop-first avec adaptation mobile
- **Feedback** : Toasts de confirmation, états de chargement élégants

---

## ✅ Phase 7 : Collaboration & Partage (terminé)
- **Notifications in-app** : Table `notifications` avec Realtime, icône cloche avec badge dans la sidebar, popover avec marquage lu/tout lu
- **Commentaires sur transactions** : Table `transaction_comments`, Sheet latéral chat-like, compteur par transaction
- **Validation croisée** : Colonnes `validation_status` + `last_modified_by`, badges visuels, boutons valider/contester, filtre "À valider"
- **Notifications automatiques** : Notification au partenaire lors de changement de catégorie/attribution

### Phase 8 : Connexions & Intégrations
- **Import automatique** : Connexion bancaire directe (API bancaire type GoCardless/Plaid)
- **Multi-devises** : Support des comptes en devises étrangères avec conversion
- **Export comptable** : Export au format compatible avec des logiciels comptables
- **Rapport PDF** : Export mensuel automatique en PDF avec graphiques et résumé
