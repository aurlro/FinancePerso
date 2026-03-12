#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# MyFinance Companion - Script de Lancement Intelligent
# ═══════════════════════════════════════════════════════════════════════════════
# 
# Ce script gère :
# - Détection et création de l'environnement virtuel (.venv)
# - Installation automatique des dépendances si nécessaire
# - Vérification de santé de l'application
# - Lancement de Streamlit avec les bonnes options
# - Gestion des erreurs courantes (permissions macOS, ports occupés, etc.)
#
# Usage : Double-cliquez sur ce fichier ou exécutez : ./MyFinance.command
#
# ═══════════════════════════════════════════════════════════════════════════════

set -e  # Arrêt sur erreur

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

PROJECT_DIR="/Users/aurelien/Documents/Projets/FinancePerso"
VENV_DIR="$PROJECT_DIR/.venv"
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"
ENV_FILE="$PROJECT_DIR/.env"
ENV_EXAMPLE="$PROJECT_DIR/.env.example"
DATA_DIR="$PROJECT_DIR/Data"
DEFAULT_PORT=8501

# ═══════════════════════════════════════════════════════════════════════════════
# COULEURS ET STYLES
# ═══════════════════════════════════════════════════════════════════════════════

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ═══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════════════════════════

print_header() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}            ${BOLD}${CYAN}💰 MyFinance Companion${NC}                              ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}              ${MAGENTA}Gestion Financière Personnelle${NC}                    ${BLUE}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_step() {
    echo -e "${CYAN}▶ $1${NC}"
}

# ═══════════════════════════════════════════════════════════════════════════════
# VÉRIFICATIONS PRÉLIMINAIRES
# ═══════════════════════════════════════════════════════════════════════════════

check_python() {
    print_step "Vérification de Python 3..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD=python3
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION détecté"
    elif command -v python &> /dev/null; then
        PYTHON_CMD=python
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
        # Vérifier que c'est Python 3
        if [[ $PYTHON_VERSION == 3.* ]]; then
            print_success "Python $PYTHON_VERSION détecté"
        else
            print_error "Python 3 est requis (version $PYTHON_VERSION détectée)"
            exit 1
        fi
    else
        print_error "Python 3 n'est pas installé"
        echo ""
        echo -e "${YELLOW}💡 Installez Python 3 depuis :${NC}"
        echo "   - https://www.python.org/downloads/"
        echo "   - Ou avec Homebrew : brew install python@3.12"
        echo ""
        read -p "Appuyez sur Entrée pour quitter..."
        exit 1
    fi
    
    # Vérifier la version minimale (3.11)
    PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
    PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
        print_warning "Python ${PYTHON_MAJOR}.${PYTHON_MINOR} détecté (3.11+ recommandé)"
    fi
}

check_project_directory() {
    print_step "Vérification du répertoire projet..."
    
    if [ ! -d "$PROJECT_DIR" ]; then
        print_error "Répertoire projet introuvable : $PROJECT_DIR"
        read -p "Appuyez sur Entrée pour quitter..."
        exit 1
    fi
    
    cd "$PROJECT_DIR" || {
        print_error "Impossible d'accéder au dossier $PROJECT_DIR"
        read -p "Appuyez sur Entrée pour quitter..."
        exit 1
    }
    
    print_success "Répertoire projet OK"
}

# ═══════════════════════════════════════════════════════════════════════════════
# GESTION DE L'ENVIRONNEMENT VIRTUEL
# ═══════════════════════════════════════════════════════════════════════════════

setup_virtualenv() {
    print_step "Configuration de l'environnement virtuel..."
    
    # Vérifier si le venv existe déjà
    if [ -d "$VENV_DIR" ]; then
        print_info "Environnement virtuel existant détecté"
        
        # Vérifier s'il est fonctionnel
        if [ ! -f "$VENV_DIR/bin/python" ]; then
            print_warning "Environnement corrompu, recréation..."
            rm -rf "$VENV_DIR"
            create_venv
        elif [ ! -f "$VENV_DIR/bin/activate" ]; then
            print_warning "Activation manquante, recréation..."
            rm -rf "$VENV_DIR"
            create_venv
        else
            print_success "Environnement virtuel OK"
        fi
    else
        create_venv
    fi
}

create_venv() {
    print_info "Création de l'environnement virtuel..."
    
    $PYTHON_CMD -m venv "$VENV_DIR" --prompt="MyFinance" || {
        print_error "Échec de la création de l'environnement virtuel"
        echo ""
        echo "Solutions possibles :"
        echo "  - Vérifiez les permissions du dossier"
        echo "  - Installez le package python3-venv :"
        echo "    brew install python@3.12  (macOS)"
        echo "    sudo apt install python3-venv  (Linux)"
        echo ""
        read -p "Appuyez sur Entrée pour quitter..."
        exit 1
    }
    
    print_success "Environnement virtuel créé"
}

activate_venv() {
    print_step "Activation de l'environnement virtuel..."
    
    # Source avec vérification d'erreur
    if ! source "$VENV_DIR/bin/activate" 2>/dev/null; then
        print_error "Impossible d'activer l'environnement virtuel"
        read -p "Appuyez sur Entrée pour quitter..."
        exit 1
    fi
    
    # Vérifier que nous sommes bien dans le venv
    if [ -z "$VIRTUAL_ENV" ]; then
        print_error "Activation de l'environnement virtuel échouée"
        read -p "Appuyez sur Entrée pour quitter..."
        exit 1
    fi
    
    print_success "Environnement activé ($VIRTUAL_ENV)"
}

# ═══════════════════════════════════════════════════════════════════════════════
# INSTALLATION DES DÉPENDANCES
# ═══════════════════════════════════════════════════════════════════════════════

install_dependencies() {
    print_step "Vérification des dépendances..."
    
    # Vérifier si les dépendances sont déjà installées
    local needs_install=false
    
    if ! python -c "import streamlit" 2>/dev/null; then
        needs_install=true
        print_warning "Streamlit non détecté"
    fi
    
    if ! python -c "import pandas" 2>/dev/null; then
        needs_install=true
        print_warning "Pandas non détecté"
    fi
    
    if ! python -c "import plotly" 2>/dev/null; then
        needs_install=true
        print_warning "Plotly non détecté"
    fi
    
    if [ "$needs_install" = true ]; then
        print_info "Installation des dépendances..."
        echo ""
        
        # Mettre à jour pip
        pip install --upgrade pip -q || {
            print_warning "Mise à jour de pip échouée, continuation..."
        }
        
        # Installer les requirements
        if [ -f "$REQUIREMENTS_FILE" ]; then
            echo -e "${YELLOW}⏳ Installation en cours (cela peut prendre 2-3 minutes)...${NC}"
            echo ""
            
            pip install -r "$REQUIREMENTS_FILE" || {
                print_error "Échec de l'installation des dépendances"
                echo ""
                echo "Solutions :"
                echo "  1. Vérifiez votre connexion internet"
                echo "  2. Essayez de supprimer le dossier .venv et relancez"
                echo "  3. Vérifiez les erreurs ci-dessus"
                echo ""
                read -p "Appuyez sur Entrée pour quitter..."
                exit 1
            }
            
            print_success "Dépendances installées avec succès"
        else
            print_error "Fichier requirements.txt introuvable"
            read -p "Appuyez sur Entrée pour quitter..."
            exit 1
        fi
    else
        print_success "Toutes les dépendances sont installées"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

setup_environment() {
    print_step "Vérification de la configuration..."
    
    # Créer le dossier Data s'il n'existe pas
    if [ ! -d "$DATA_DIR" ]; then
        mkdir -p "$DATA_DIR"
        print_info "Dossier Data créé"
    fi
    
    # Créer .env si nécessaire
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$ENV_EXAMPLE" ]; then
            cp "$ENV_EXAMPLE" "$ENV_FILE"
            print_warning "Fichier .env créé depuis .env.example"
            print_info "⚠️  Éditez $ENV_FILE pour configurer vos clés API"
        else
            print_warning "Fichier .env.example introuvable"
        fi
    else
        print_success "Configuration existante (.env)"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# VÉRIFICATIONS DE SANTÉ
# ═══════════════════════════════════════════════════════════════════════════════

run_health_checks() {
    print_step "Vérifications de santé..."
    echo ""
    
    local checks_passed=0
    local checks_total=5
    
    # Test 1: Imports critiques
    echo -n "  📦 Imports Python... "
    if python -c "import streamlit, pandas, plotly, cryptography" 2>/dev/null; then
        echo -e "${GREEN}OK${NC}"
        ((checks_passed++))
    else
        echo -e "${RED}ÉCHEC${NC}"
    fi
    
    # Test 2: Structure du projet
    echo -n "  📁 Structure projet... "
    if [ -f "app.py" ] && [ -d "modules" ] && [ -d "pages" ]; then
        echo -e "${GREEN}OK${NC}"
        ((checks_passed++))
    else
        echo -e "${RED}ÉCHEC${NC}"
    fi
    
    # Test 3: Base de données
    echo -n "  💾 Base de données... "
    if python -c "from modules.db.migrations import init_db; init_db()" 2>/dev/null; then
        echo -e "${GREEN}OK${NC}"
        ((checks_passed++))
    else
        echo -e "${RED}ÉCHEC${NC}"
    fi
    
    # Test 4: Permissions Data
    echo -n "  🔐 Permissions Data... "
    if [ -w "$DATA_DIR" ]; then
        echo -e "${GREEN}OK${NC}"
        ((checks_passed++))
    else
        echo -e "${RED}ÉCHEC${NC}"
    fi
    
    # Test 5: Configuration
    echo -n "  ⚙️  Configuration... "
    if [ -f "$ENV_FILE" ]; then
        echo -e "${GREEN}OK${NC}"
        ((checks_passed++))
    else
        echo -e "${YELLOW}AVERTISSEMENT${NC}"
        ((checks_passed++))
    fi
    
    echo ""
    print_success "Vérifications terminées ($checks_passed/$checks_total)"
    
    if [ $checks_passed -lt $checks_total ]; then
        print_warning "Certains tests ont échoué, mais l'application peut toujours fonctionner"
        echo ""
        read -p "Continuer malgré tout ? (o/N) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Oo]$ ]]; then
            exit 1
        fi
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# LANCEMENT DE L'APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

launch_app() {
    print_step "Lancement de MyFinance Companion..."
    echo ""
    
    # Déterminer le port
    local port=$DEFAULT_PORT
    
    # Vérifier si le port est déjà utilisé
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $port déjà utilisé"
        port=$((port + 1))
        print_info "Utilisation du port alternatif : $port"
    fi
    
    # Afficher les informations de connexion
    echo -e "${GREEN}${BOLD}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}${BOLD}  🚀 Application prête !${NC}"
    echo -e "${GREEN}${BOLD}═══════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${CYAN}URL Locale:${NC}    http://localhost:$port"
    echo -e "  ${CYAN}URL Réseau:${NC}   http://$(hostname -I | awk '{print $1}'):$port"
    echo ""
    echo -e "  ${YELLOW}Appuyez sur Ctrl+C pour arrêter l'application${NC}"
    echo ""
    echo -e "${GREEN}${BOLD}═══════════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Lancer Streamlit avec les bonnes options
    # Utiliser exec pour remplacer le processus et capturer correctement Ctrl+C
    exec python -m streamlit run app.py \
        --server.port=$port \
        --server.address=0.0.0.0 \
        --browser.gatherUsageStats=false \
        --server.headless=false \
        --server.fileWatcherType=none \
        --theme.base=light
}

# ═══════════════════════════════════════════════════════════════════════════════
# GESTION DES ERREURS MACOS
# ═══════════════════════════════════════════════════════════════════════════════

handle_macos_permission_error() {
    print_error "Erreur de permission macOS détectée"
    echo ""
    echo -e "${YELLOW}Sur macOS, les fichiers téléchargés depuis internet sont en quarantaine.${NC}"
    echo ""
    echo "Pour corriger, ouvrez un terminal et exécutez :"
    echo ""
    echo -e "${CYAN}  xattr -d com.apple.quarantine \"$PROJECT_DIR/MyFinance.command\"${NC}"
    echo ""
    echo "Ou faites un clic droit sur le fichier → Ouvrir (accepter l'avertissement)"
    echo ""
    read -p "Appuyez sur Entrée pour quitter..."
    exit 1
}

# ═══════════════════════════════════════════════════════════════════════════════
# MENU INTERACTIF (OPTIONNEL)
# ═══════════════════════════════════════════════════════════════════════════════

show_menu() {
    echo ""
    echo -e "${BLUE}Options disponibles :${NC}"
    echo "  1. Lancer l'application (défaut)"
    echo "  2. Lancer avec réinstallation des dépendances"
    echo "  3. Exécuter les tests"
    echo "  4. Réinitialiser la base de données"
    echo "  5. Quitter"
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# FONCTION PRINCIPALE
# ═══════════════════════════════════════════════════════════════════════════════

main() {
    # Capturer les erreurs de permission macOS
    trap 'if [[ $? -eq 126 ]]; then handle_macos_permission_error; fi' EXIT
    
    print_header
    
    # Vérifications préliminaires
    check_project_directory
    check_python
    
    # Configuration de l'environnement
    setup_virtualenv
    activate_venv
    install_dependencies
    setup_environment
    
    # Vérifications de santé
    run_health_checks
    
    # Lancement
    launch_app
}

# ═══════════════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

# Si des arguments sont passés, les traiter
if [ "$1" = "--test" ] || [ "$1" = "-t" ]; then
    print_header
    check_project_directory
    activate_venv 2>/dev/null || setup_virtualenv && activate_venv
    print_step "Exécution des tests..."
    python -m pytest tests/test_essential.py -v
    read -p "Appuyez sur Entrée pour quitter..."
    exit 0
fi

if [ "$1" = "--reset" ]; then
    print_header
    print_warning "Réinitialisation de l'environnement..."
    rm -rf "$VENV_DIR"
    print_success "Environnement supprimé. Relancez le script pour recréer."
    exit 0
fi

if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: ./MyFinance.command [OPTION]"
    echo ""
    echo "Options:"
    echo "  --test, -t     Exécuter les tests essentiels"
    echo "  --reset        Supprimer et recréer l'environnement virtuel"
    echo "  --help, -h     Afficher cette aide"
    echo ""
    exit 0
fi

# Lancement principal
main
