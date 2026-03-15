#!/bin/bash
# Script pour créer les issues GitHub pour les TODOs du projet
# Usage: ./scripts/create-github-issues.sh

set -e

echo "🔧 Création des issues GitHub pour les TODOs..."
echo ""

# Vérifier si gh est installé
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) n'est pas installé"
    echo "Installez-le: https://cli.github.com/"
    exit 1
fi

# Vérifier l'authentification
if ! gh auth status &> /dev/null; then
    echo "❌ Vous devez vous authentifier avec: gh auth login"
    exit 1
fi

REPO="aurlro/FinancePerso"

# Issue 1: Bouton supprimer lien prêt
echo "📋 Création de l'issue TODO-001..."
gh issue create \
    --repo "$REPO" \
    --title "[TODO-001] Bouton supprimer lien prêt" \
    --body "## Contexte
Fichier: \`modules/ui/couple/loans_view.py:260\`

## Description
Le bouton pour supprimer un lien entre prêts n'est pas fonctionnel.

## Tâches
- [ ] Implémenter la méthode \`delete_loan_link()\`
- [ ] Ajouter confirmation (dialog)
- [ ] Mettre à jour la base de données
- [ ] Rafraîchir l'affichage
- [ ] Ajouter tests

## Priorité
🔴 HIGH

## Labels
bug, couple, loans, todo" \
    --label "bug,todo"

# Issue 2: Récupération DB des objectifs d'épargne
echo "📋 Création de l'issue TODO-002..."
gh issue create \
    --repo "$REPO" \
    --title "[TODO-002] Récupération DB des objectifs d'épargne V5.5" \
    --body "## Contexte
Fichier: \`modules/ui/v5_5/components/savings_goals.py:118\`

## Description
Les objectifs d'épargne sont en dur (mockés) au lieu d'être récupérés depuis la base de données.

## Tâches
- [ ] Créer les méthodes CRUD dans \`modules/db/savings_goals.py\`
- [ ] Connecter le composant à la DB
- [ ] Gérer les états de chargement
- [ ] Gérer les erreurs
- [ ] Ajouter tests

## Priorité
🔴 HIGH

## Labels
bug, v5.5, savings, todo" \
    --label "bug,todo"

# Issue 3: Suppression définitive historique
echo "📋 Création de l'issue TODO-003..."
gh issue create \
    --repo "$REPO" \
    --title "[TODO-003] Suppression définitive de l'historique" \
    --body "## Contexte
Fichier: \`modules/ui/automation/history_tab.py:212\`

## Description
La suppression définitive des transactions de l'historique n'est pas implémentée.

## Tâches
- [ ] Implémenter \`permanently_delete_transactions()\`
- [ ] Ajouter confirmation avec avertissement
- [ ] Supprimer de la DB + corbeille
- [ ] Logger l'action
- [ ] Ajouter tests

## Priorité
🔴 HIGH

## Labels
bug, history, todo" \
    --label "bug,todo"

# Issue 4: Déconnexion Open Banking
echo "📋 Création de l'issue TODO-004..."
gh issue create \
    --repo "$REPO" \
    --title "[TODO-004] Déconnexion Open Banking" \
    --body "## Contexte
Fichier: \`modules/open_banking/sync.py:470\`

## Description
La fonctionnalité de déconnexion d'un compte Open Banking n'est pas encore implémentée.

## Tâches
- [ ] Implémenter \`disconnect_account()\` dans \`OpenBankingSync\`
- [ ] Supprimer les tokens d'accès stockés
- [ ] Révoquer les accès côté provider (API)
- [ ] Mettre à jour le statut de synchronisation
- [ ] Ajouter tests unitaires

## Priorité
🟡 MEDIUM

## Labels
enhancement, open-banking, todo" \
    --label "enhancement,todo"

# Issue 5: Fusion de notifications
echo "📋 Création de l'issue TODO-005..."
gh issue create \
    --repo "$REPO" \
    --title "[TODO-005] Fusion de notifications similaires" \
    --body "## Contexte
Fichier: \`modules/notifications/ui.py:303\`

## Description
La fonction de fusion (merge) des notifications similaires n'est pas implémentée.

## Tâches
- [ ] Créer \`merge_similar_notifications()\`
- [ ] Détecter les notifications similaires (même type, même entité)
- [ ] Fusionner les messages avec compteur (ex: \"3 nouvelles transactions\")
- [ ] Mettre à jour l'UI pour afficher les notifications fusionnées
- [ ] Ajouter tests

## Priorité
🟡 MEDIUM

## Labels
enhancement, notifications, todo" \
    --label "enhancement,todo"

# Issue 6: Settings utilisateur Dashboard V5.5
echo "📋 Création de l'issue TODO-006..."
gh issue create \
    --repo "$REPO" \
    --title "[TODO-006] Settings utilisateur Dashboard V5.5" \
    --body "## Contexte
Fichier: \`modules/ui/v5_5/pages/dashboard_controller.py:52\`

## Description
Les préférences utilisateur sont en dur au lieu d'être récupérées depuis les settings.

## Tâches
- [ ] Connecter à \`modules/db/settings.py\`
- [ ] Créer les méthodes CRUD pour les préférences
- [ ] Charger les préférences au démarrage
- [ ] Sauvegarder automatiquement les changements
- [ ] Ajouter tests

## Priorité
🟡 MEDIUM

## Labels
enhancement, v5.5, settings, todo" \
    --label "enhancement,todo"

# Issue 7: Alerts zombie/increase
echo "📋 Création de l'issue TODO-007..."
gh issue create \
    --repo "$REPO" \
    --title "[TODO-007] Alerts zombie/increase dans inbox" \
    --body "## Contexte
Fichier: \`modules/ui/automation/inbox_tab.py:115\`

## Description
Ajouter des alerts pour les transactions zombie et les augmentations de dépenses.

## Tâches
- [ ] Implémenter détecteur de transactions zombie (non catégorisées depuis longtemps)
- [ ] Implémenter détecteur d'augmentation de dépenses
- [ ] Ajouter affichage des alerts dans l'UI
- [ ] Configurer seuils d'alerte
- [ ] Ajouter tests

## Priorité
🟢 LOW

## Labels
enhancement, alerts, todo" \
    --label "enhancement,todo"

echo ""
echo "✅ Toutes les issues ont été créées !"
echo ""
echo "📊 Récapitulatif:"
echo "  - 🔴 HIGH: 3 issues"
echo "  - 🟡 MEDIUM: 3 issues"
echo "  - 🟢 LOW: 1 issue"
echo ""
echo "🔗 Voir les issues: https://github.com/$REPO/issues"
