#!/bin/bash
#
# Script de test local des workflows GitHub Actions avec 'act'
# Usage: ./scripts/test_workflows_locally.sh [job_name]
#

set -e

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de logging
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérifier les dépendances
check_dependencies() {
    log_info "Vérification des dépendances..."
    
    if ! command -v act &> /dev/null; then
        log_error "act n'est pas installé"
        echo "   Installation: brew install act  (macOS)"
        echo "                 curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash  (Linux)"
        exit 1
    fi
    log_success "act trouvé: $(act --version)"
    
    if ! docker ps &> /dev/null; then
        log_error "Docker n'est pas en cours d'exécution"
        echo "   Veuillez lancer Docker Desktop ou le service docker"
        exit 1
    fi
    log_success "Docker est en cours d'exécution"
}

# Afficher l'aide
show_help() {
    cat << EOF
Usage: $0 [OPTIONS] [JOB_NAME]

Teste les workflows GitHub Actions localement avec 'act'

OPTIONS:
    -h, --help          Affiche cette aide
    -l, --list          Liste les jobs disponibles
    -n, --dry-run       Mode simulation (ne pas exécuter)
    -j, --job JOB       Spécifie le job à exécuter
    -w, --workflow FILE Spécifie le fichier workflow (défaut: ci.yml)

EXEMPLES:
    $0                  # Teste tous les jobs
    $0 lint             # Teste uniquement le job 'lint'
    $0 -l               # Liste les jobs disponibles
    $0 -n lint          # Simulation du job 'lint'
    $0 -w release.yml release  # Teste le job 'release'

JOBS DISPONIBLES (ci.yml):
    lint        🎨 Lint & Format (rapide, recommandé pour test)
    test        🧪 Tests (Python matrix 3.11, 3.12)
    security    🔒 Security Audit
    build       🏗️ Build & Verify
    notify      📊 CI Summary

JOBS DISPONIBLES (release.yml):
    release     🚀 Create Release
    docker      🐳 Docker Build & Push

EOF
}

# Liste les jobs disponibles
list_jobs() {
    echo ""
    log_info "Jobs disponibles dans .github/workflows/ci.yml:"
    act -l --workflows .github/workflows/ci.yml 2>/dev/null | grep -E "^\s+[0-9]" || echo "   (act -l a échoué, vérifiez que Docker est lancé)"
    
    echo ""
    log_info "Jobs disponibles dans .github/workflows/release.yml:"
    act -l --workflows .github/workflows/release.yml 2>/dev/null | grep -E "^\s+[0-9]" || true
}

# Teste un job spécifique
test_job() {
    local job=$1
    local workflow=$2
    local dry_run=$3
    
    log_info "Test du job '$job' ($workflow)..."
    
    local cmd="act -j $job --workflows .github/workflows/$workflow"
    
    if [ "$dry_run" = true ]; then
        cmd="$cmd -n"
        log_info "Mode simulation (dry-run)"
    fi
    
    # Ajouter des options pour macOS M1/M2/M3 si nécessaire
    if [[ $(uname -m) == "arm64" ]]; then
        log_warning "Architecture ARM64 détectée, utilisation de --container-architecture linux/amd64"
        cmd="$cmd --container-architecture linux/amd64"
    fi
    
    echo ""
    echo "Commande: $cmd"
    echo "----------------------------------------"
    
    if $cmd; then
        echo ""
        log_success "Job '$job' terminé avec succès!"
        return 0
    else
        echo ""
        log_error "Job '$job' a échoué!"
        return 1
    fi
}

# Test rapide avec une image légère
test_quick() {
    log_info "Test rapide (utilise une image Node légère)..."
    
    # Pour Python, on utilise l'image par défaut car il faut Python installé
    local cmd="act -j lint --workflows .github/workflows/ci.yml"
    
    if [[ $(uname -m) == "arm64" ]]; then
        cmd="$cmd --container-architecture linux/amd64"
    fi
    
    echo "Commande: $cmd"
    $cmd
}

# Fonction principale
main() {
    local job=""
    local workflow="ci.yml"
    local dry_run=false
    local list=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -l|--list)
                list=true
                shift
                ;;
            -n|--dry-run)
                dry_run=true
                shift
                ;;
            -j|--job)
                job="$2"
                shift 2
                ;;
            -w|--workflow)
                workflow="$2"
                shift 2
                ;;
            -*)
                log_error "Option inconnue: $1"
                show_help
                exit 1
                ;;
            *)
                job="$1"
                shift
                ;;
        esac
    done
    
    # Afficher le banner
    echo "=============================================="
    echo "🧪 Test Local des Workflows GitHub Actions"
    echo "=============================================="
    echo ""
    
    check_dependencies
    
    if [ "$list" = true ]; then
        list_jobs
        exit 0
    fi
    
    if [ -n "$job" ]; then
        test_job "$job" "$workflow" "$dry_run"
    else
        echo ""
        log_info "Aucun job spécifié"
        echo ""
        echo "Pour tester un job spécifique:"
        echo "  $0 lint       # Test rapide (recommandé)"
        echo "  $0 test       # Tests complets"
        echo "  $0 security   # Scan de sécurité"
        echo ""
        echo "Pour voir tous les jobs:"
        echo "  $0 -l"
        echo ""
        
        # Proposer de tester le job lint par défaut
        read -p "Voulez-vous tester le job 'lint' (rapide)? [Y/n] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            test_job "lint" "$workflow" "$dry_run"
        fi
    fi
}

# Exécuter
cd "$(dirname "$0")/.."
main "$@"
