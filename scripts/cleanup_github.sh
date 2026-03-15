#!/bin/bash
# =============================================================================
# Script de nettoyage GitHub local
# Supprime les branches locales et remote obsolètes
# =============================================================================

set -euo pipefail

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
DRY_RUN=false
VERBOSE=false
REMOTE_NAME="origin"
DEFAULT_BRANCH="main"

# =============================================================================
# Fonctions utilitaires
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Nettoie les branches Git locales et remote obsolètes.

OPTIONS:
    -d, --dry-run       Mode simulation (affiche sans supprimer)
    -v, --verbose       Mode verbeux
    -r, --remote NAME   Nom du remote (défaut: origin)
    -b, --branch NAME   Nom de la branche principale (défaut: main)
    -h, --help          Affiche cette aide

EXEMPLES:
    $(basename "$0")                    # Nettoyage normal
    $(basename "$0") --dry-run          # Simulation sans suppression
    $(basename "$0") -r upstream -b master  # Remote et branche custom

EOF
}

# =============================================================================
# Parse arguments
# =============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -r|--remote)
            REMOTE_NAME="$2"
            shift 2
            ;;
        -b|--branch)
            DEFAULT_BRANCH="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "Option inconnue: $1"
            show_help
            exit 1
            ;;
    esac
done

# =============================================================================
# Vérifications initiales
# =============================================================================

if [[ "$DRY_RUN" == true ]]; then
    log_warn "MODE SIMULATION - Aucune suppression réelle ne sera effectuée"
fi

# Vérifier que nous sommes dans un repo git
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_error "Ce n'est pas un dépôt Git"
    exit 1
fi

# Vérifier le remote
if ! git remote | grep -q "^${REMOTE_NAME}$"; then
    log_error "Remote '${REMOTE_NAME}' non trouvé"
    log_info "Remotes disponibles:"
    git remote -v
    exit 1
fi

# Récupérer la branche par défaut si main n'existe pas
if ! git show-ref --verify --quiet "refs/heads/${DEFAULT_BRANCH}"; then
    if git show-ref --verify --quiet "refs/heads/master"; then
        DEFAULT_BRANCH="master"
        log_info "Utilisation de 'master' comme branche principale"
    else
        log_error "Ni 'main' ni 'master' trouvé comme branche principale"
        exit 1
    fi
fi

# =============================================================================
# Fonctions de nettoyage
# =============================================================================

cleanup_local_merged_branches() {
    log_info "Recherche des branches locales mergées dans '${DEFAULT_BRANCH}'..."
    
    local branches_to_delete=()
    
    # Récupérer les branches mergées (sauf la branche courante et les branches protégées)
    while IFS= read -r branch; do
        # Skip si vide
        [[ -z "$branch" ]] && continue
        
        # Skip les branches protégées
        if [[ "$branch" == "$DEFAULT_BRANCH" || "$branch" == "develop" || "$branch" == "master" ]]; then
            [[ "$VERBOSE" == true ]] && log_warn "Branche protégée ignorée: $branch"
            continue
        fi
        
        # Skip la branche courante
        if [[ "$branch" == "$(git branch --show-current)" ]]; then
            log_warn "Impossible de supprimer la branche courante: $branch"
            continue
        fi
        
        branches_to_delete+=("$branch")
    done < <(git branch --merged "$DEFAULT_BRANCH" | grep -v '^\*' | sed 's/^[[:space:]]*//')
    
    if [[ ${#branches_to_delete[@]} -eq 0 ]]; then
        log_success "Aucune branche locale mergée à supprimer"
        return 0
    fi
    
    log_info "Branches locales mergées trouvées: ${#branches_to_delete[@]}"
    
    for branch in "${branches_to_delete[@]}"; do
        if [[ "$DRY_RUN" == true ]]; then
            echo "  [DRY-RUN] git branch -d '$branch'"
        else
            if git branch -d "$branch" 2>/dev/null; then
                log_success "Supprimée: $branch"
            else
                log_error "Échec suppression: $branch"
            fi
        fi
    done
}

cleanup_remote_dependabot_branches() {
    log_info "Recherche des branches remote dependabot obsolètes..."
    
    local branches_to_delete=()
    
    # Récupérer les branches dependabot du remote
    while IFS= read -r branch; do
        [[ -z "$branch" ]] && continue
        branches_to_delete+=("$branch")
    done < <(git branch -r --merged "${REMOTE_NAME}/${DEFAULT_BRANCH}" | \
             grep "${REMOTE_NAME}/dependabot/" | \
             sed "s|${REMOTE_NAME}/||" | \
             sed 's/^[[:space:]]*//')
    
    if [[ ${#branches_to_delete[@]} -eq 0 ]]; then
        log_success "Aucune branche dependabot obsolète trouvée"
        return 0
    fi
    
    log_info "Branches dependabot à supprimer: ${#branches_to_delete[@]}"
    
    for branch in "${branches_to_delete[@]}"; do
        if [[ "$DRY_RUN" == true ]]; then
            echo "  [DRY-RUN] git push ${REMOTE_NAME} --delete '$branch'"
        else
            if git push "$REMOTE_NAME" --delete "$branch" 2>/dev/null; then
                log_success "Supprimée remote: $branch"
            else
                log_error "Échec suppression remote: $branch"
            fi
        fi
    done
}

cleanup_design_branch() {
    log_info "Vérification de la branche 'Design'..."
    
    # Vérifier si la branche existe en remote
    if ! git branch -r | grep -q "${REMOTE_NAME}/Design"; then
        log_info "Branche 'Design' non trouvée sur le remote"
        return 0
    fi
    
    # Vérifier si elle est mergée
    if git branch -r --merged "${REMOTE_NAME}/${DEFAULT_BRANCH}" | grep -q "${REMOTE_NAME}/Design"; then
        log_info "La branche 'Design' est mergée dans '${DEFAULT_BRANCH}'"
        
        if [[ "$DRY_RUN" == true ]]; then
            echo "  [DRY-RUN] git push ${REMOTE_NAME} --delete 'Design'"
            echo "  [DRY-RUN] git branch -d 'Design' (si existe localement)"
        else
            # Supprimer la branche remote
            if git push "$REMOTE_NAME" --delete "Design" 2>/dev/null; then
                log_success "Supprimée remote: Design"
            else
                log_error "Échec suppression remote: Design"
            fi
            
            # Supprimer la branche locale si elle existe
            if git branch | grep -q "Design"; then
                if git branch -d "Design" 2>/dev/null; then
                    log_success "Supprimée locale: Design"
                fi
            fi
        fi
    else
        log_warn "La branche 'Design' n'est pas mergée - conservation"
    fi
}

cleanup_stale_local_branches() {
    log_info "Recherche des branches locales sans tracking (obsolètes)..."
    
    local branches_to_delete=()
    
    while IFS= read -r branch; do
        [[ -z "$branch" ]] && continue
        
        # Skip les branches protégées
        if [[ "$branch" == "$DEFAULT_BRANCH" || "$branch" == "develop" || "$branch" == "master" ]]; then
            continue
        fi
        
        # Skip la branche courante
        if [[ "$branch" == "$(git branch --show-current)" ]]; then
            continue
        fi
        
        # Vérifier si la branche a un remote tracking
        if ! git config --get "branch.${branch}.remote" > /dev/null 2>&1; then
            branches_to_delete+=("$branch")
        fi
    done < <(git branch | grep -v '^\*' | sed 's/^[[:space:]]*//')
    
    if [[ ${#branches_to_delete[@]} -eq 0 ]]; then
        log_success "Aucune branche locale orpheline"
        return 0
    fi
    
    log_info "Branches locales orphelines: ${#branches_to_delete[@]}"
    
    for branch in "${branches_to_delete[@]}"; do
        if [[ "$DRY_RUN" == true ]]; then
            echo "  [DRY-RUN] git branch -D '$branch'"
        else
            if git branch -D "$branch" 2>/dev/null; then
                log_success "Supprimée: $branch"
            else
                log_error "Échec suppression: $branch"
            fi
        fi
    done
}

prune_remote() {
    log_info "Nettoyage des références remote obsolètes..."
    
    if [[ "$DRY_RUN" == true ]]; then
        echo "  [DRY-RUN] git remote prune ${REMOTE_NAME}"
    else
        git remote prune "$REMOTE_NAME"
        log_success "Remote nettoyé: ${REMOTE_NAME}"
    fi
}

# =============================================================================
# Exécution principale
# =============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         NETTOYAGE GITHUB - FinancePerso                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

log_info "Remote: ${REMOTE_NAME}"
log_info "Branche principale: ${DEFAULT_BRANCH}"
echo ""

# Fetch pour avoir les dernières informations
log_info "Récupération des dernières modifications..."
git fetch --all --prune 2>/dev/null || true

# Exécuter les nettoyages
cleanup_local_merged_branches
echo ""

cleanup_stale_local_branches
echo ""

cleanup_remote_dependabot_branches
echo ""

cleanup_design_branch
echo ""

prune_remote
echo ""

# =============================================================================
# Résumé
# =============================================================================

echo "╔════════════════════════════════════════════════════════════╗"
if [[ "$DRY_RUN" == true ]]; then
    echo "║              SIMULATION TERMINÉE                           ║"
    log_warn "Relancer sans --dry-run pour effectuer les suppressions"
else
    echo "║              NETTOYAGE TERMINÉ                             ║"
fi
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Afficher le statut des branches
log_info "Branches locales restantes:"
git branch | wc -l | xargs echo "  - Total:"

echo ""
log_info "Branches remote:"
git branch -r | grep "${REMOTE_NAME}/" | wc -l | xargs echo "  - Total sur ${REMOTE_NAME}:"

echo ""
