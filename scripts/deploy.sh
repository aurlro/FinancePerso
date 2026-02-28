#!/bin/bash
# =============================================================================
# Script de déploiement FinancePerso
# =============================================================================
# Ce script permet de déployer l'application FinancePerso avec Docker
# Usage: ./scripts/deploy.sh [environment]
#   environment: development (défaut) | production | staging
# =============================================================================

set -e  # Arrêter en cas d'erreur

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
ENVIRONMENT="${1:-development}"
COMPOSE_FILE="docker-compose.yml"
APP_NAME="financeperso"
HEALTH_URL="http://localhost:8501/_stcore/health"
MAX_RETRIES=30
RETRY_DELAY=2

# =============================================================================
# Fonctions utilitaires
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# =============================================================================
# Vérification des prérequis
# =============================================================================

check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé"
        echo "  → Installation: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Vérifier Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose n'est pas installé"
        echo "  → Installation: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Vérifier que le fichier .env existe
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            log_warning "Fichier .env manquant"
            echo "  → Création à partir de .env.example..."
            cp .env.example .env
            log_warning "Veuillez éditer le fichier .env avec vos vraies valeurs avant de continuer"
            exit 1
        else
            log_error "Aucun fichier .env ou .env.example trouvé"
            exit 1
        fi
    fi
    
    # Vérifier le docker-compose.yml
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Fichier $COMPOSE_FILE non trouvé"
        exit 1
    fi
    
    log_success "Tous les prérequis sont satisfaits"
}

# =============================================================================
# Nettoyage
# =============================================================================

cleanup() {
    log_info "Nettoyage des ressources inutilisées..."
    docker system prune -f --volumes &> /dev/null || true
    log_success "Nettoyage terminé"
}

# =============================================================================
# Build de l'image
# =============================================================================

build_image() {
    log_info "Construction de l'image Docker..."
    log_info "Environment: $ENVIRONMENT"
    
    # Définir les arguments de build selon l'environnement
    if [ "$ENVIRONMENT" = "production" ]; then
        export DOCKER_BUILDKIT=1
        BUILD_OPTS="--no-cache"
    else
        BUILD_OPTS=""
    fi
    
    docker-compose -f "$COMPOSE_FILE" build $BUILD_OPTS
    
    if [ $? -eq 0 ]; then
        log_success "Image construite avec succès"
    else
        log_error "Échec de la construction de l'image"
        exit 1
    fi
}

# =============================================================================
# Démarrage des containers
# =============================================================================

start_containers() {
    log_info "Démarrage des containers..."
    
    # Arrêter les containers existants
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans
    
    # Démarrer les nouveaux containers
    if [ "$ENVIRONMENT" = "development" ]; then
        docker-compose -f "$COMPOSE_FILE" up -d
    else
        docker-compose -f "$COMPOSE_FILE" up -d --remove-orphans
    fi
    
    if [ $? -eq 0 ]; then
        log_success "Containers démarrés"
    else
        log_error "Échec du démarrage des containers"
        exit 1
    fi
}

# =============================================================================
# Vérification de santé
# =============================================================================

check_health() {
    log_info "Vérification de la santé de l'application..."
    log_info "URL de santé: $HEALTH_URL"
    
    local retries=0
    local healthy=false
    
    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -sf "$HEALTH_URL" &> /dev/null; then
            healthy=true
            break
        fi
        
        retries=$((retries + 1))
        log_info "Tentative $retries/$MAX_RETRIES... (attente ${RETRY_DELAY}s)"
        sleep $RETRY_DELAY
    done
    
    if [ "$healthy" = true ]; then
        log_success "Application en bonne santé !"
        return 0
    else
        log_error "L'application ne répond pas après $MAX_RETRIES tentatives"
        show_logs
        return 1
    fi
}

# =============================================================================
# Affichage des logs
# =============================================================================

show_logs() {
    log_info "Affichage des logs récents..."
    docker-compose -f "$COMPOSE_FILE" logs --tail=50
}

# =============================================================================
# Affichage des informations
# =============================================================================

show_info() {
    echo ""
    echo "============================================================================="
    echo -e "${GREEN}  FinancePerso déployé avec succès !${NC}"
    echo "============================================================================="
    echo ""
    echo "  🌐 Application URL: http://localhost:8501"
    echo "  🔧 Environment:     $ENVIRONMENT"
    echo "  📊 Health Check:    $HEALTH_URL"
    echo ""
    echo "  Commandes utiles:"
    echo "    - Voir les logs:    docker-compose logs -f"
    echo "    - Arrêter:          docker-compose down"
    echo "    - Redémarrer:       docker-compose restart"
    echo ""
    echo "============================================================================="
}

# =============================================================================
# Main
# =============================================================================

main() {
    echo "============================================================================="
    echo "  FinancePerso - Script de déploiement"
    echo "============================================================================="
    echo ""
    
    # Aller au répertoire racine du projet
    cd "$(dirname "$0")/.."
    
    # Exécuter les étapes
    check_prerequisites
    cleanup
    build_image
    start_containers
    
    # Vérification santé avec timeout
    if check_health; then
        show_info
    else
        log_error "Le déploiement a échoué"
        exit 1
    fi
}

# Gestion des interruptions
trap 'log_error "Déploiement interrompu"; exit 1' INT TERM

# Lancer le script
main "$@"
