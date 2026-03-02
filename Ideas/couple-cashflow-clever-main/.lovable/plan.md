

# 💰 FinCouple — Gestionnaire Financier de Couple

## Phase 1 : Fondations
- **Design System** : Thème premium Apple-esque avec mode sombre/clair natif, palette gris neutres + accent émeraude
- **Auth & Profils** : Inscription/connexion sécurisée, profils couple (Personne A / Personne B), gestion de session
- **Base de données** : Tables pour comptes bancaires, transactions, catégories, règles de catégorisation, virements internes détectés

## Phase 2 : Import & Moteur de données
- **Import CSV multi-banques** : Upload avec mapping dynamique des colonnes (Date, Libellé, Montant), prévisualisation avant import, support 3-4 formats bancaires
- **Attribution automatique** : Chaque import est lié à un compte (Perso A, Perso B, Joint)
- **Détection virements internes** : Matching automatique par montant inverse + date proche + comptes différents → exclusion des calculs
- **Moteur de catégorisation Regex** : ~15 catégories standard pré-configurées (Alimentation, Transport, Logement, Loisirs, Santé, etc.), application automatique à l'import avec possibilité de correction manuelle

## Phase 3 : Dashboard & Visualisations
- **Vue globale mensuelle** : Reste à vivre, total dépenses, épargne nette (hors virements internes et remboursements d'emprunt)
- **Graphiques** : Répartition par catégorie (donut chart), évolution mensuelle (line chart), comparatif mois par mois (bar chart)
- **Comparatif Perso vs Commun** : Vue séparée des dépenses Personne A / Personne B / Joint avec top catégories pour chacun

## Phase 4 : Gestion & Configuration
- **Gestion des comptes bancaires** : Ajouter/modifier les comptes et leur type (Perso A, Perso B, Joint)
- **Gestion des règles Regex** : Interface pour créer, tester et modifier les règles de catégorisation
- **Liste des transactions** : Tableau filtrable/triable avec recherche, modification manuelle de catégorie, marquage des transactions ambiguës

## Navigation & UX
- **Sidebar minimaliste** : Dashboard, Transactions, Import, Comptes, Règles, Paramètres
- **Responsive** : Desktop-first avec adaptation mobile fluide
- **Feedback** : Toasts de confirmation, états de chargement élégants

