#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# MyFinance Companion - Script d'Installation Complète
# ═══════════════════════════════════════════════════════════════════════════════
#
# Ce script effectue une installation complète from scratch :
# - Vérification des prérequis (Python 3.11+)
# - Création de l'environnement virtuel
# - Installation de toutes les dépendances
# - Configuration initiale (.env)
# - Création des dossiers nécessaires
# - Vérification finale
#
# Usage : ./setup.sh
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
PYTHON_VERSION_MIN="3.11"

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}       ${BOLD}${CYAN}💰 MyFinance Companion - Installation${NC}                     ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 1: Vérification de Python
# ═══════════════════════════════════════════════════════════════════════════════

echo -e "${CYAN}▶ Étape 1/6 : Vérification de Python${NC}"

if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo -e "${RED}❌ Python n'est pas installé${NC}"
    echo ""
    echo "Installez Python 3.11 ou supérieur :"
    echo "  macOS : brew install python@3.12"
    echo "  Linux : sudo apt install python3.12 python3.12-venv"
    echo "  Windows : https://python.org/downloads"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION détecté${NC}"

# Vérifier la version minimale
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]; then
    echo -e "${YELLOW}⚠️  Python $PYTHON_MAJOR.$PYTHON_MINOR détecté${NC}"
    echo -e "${YELLOW}   Python 3.11+ est recommandé pour de meilleures performances${NC}"
    read -p "Continuer quand même ? (o/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Oo]$ ]]; then
        exit 1
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 2: Création de l'environnement virtuel
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo -e "${CYAN}▶ Étape 2/6 : Création de l'environnement virtuel${NC}"

if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}⚠️  Environnement virtuel existant trouvé${NC}"
    read -p "Supprimer et recréer ? (o/N) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        rm -rf "$VENV_DIR"
        echo -e "${GREEN}✅ Ancien environnement supprimé${NC}"
    else
        echo -e "${YELLOW}Utilisation de l'environnement existant${NC}"
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "Création de .venv..."
    $PYTHON_CMD -m venv "$VENV_DIR" --prompt="MyFinance" || {
        echo -e "${RED}❌ Échec de la création de l'environnement virtuel${NC}"
        echo ""
        echo "Assurez-vous que le package 'venv' est installé :"
        echo "  macOS : brew install python@3.12"
        echo "  Ubuntu/Debian : sudo apt install python3-venv python3-full"
        echo "  Fedora : sudo dnf install python3-virtualenv"
        exit 1
    }
    echo -e "${GREEN}✅ Environnement virtuel créé${NC}"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 3: Installation des dépendances
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo -e "${CYAN}▶ Étape 3/6 : Installation des dépendances${NC}"

source "$VENV_DIR/bin/activate"

echo "Mise à jour de pip..."
pip install --upgrade pip -q

echo "Installation des packages..."
echo -e "${YELLOW}⏳ Cela peut prendre 3-5 minutes...${NC}"
echo ""

pip install -r "$PROJECT_DIR/requirements.txt" || {
    echo -e "${RED}❌ Échec de l'installation des dépendances${NC}"
    exit 1
}

echo ""
echo -e "${GREEN}✅ Dépendances installées${NC}"

# ═══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 4: Configuration
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo -e "${CYAN}▶ Étape 4/6 : Configuration${NC}"

# Créer le dossier Data
mkdir -p "$PROJECT_DIR/Data"
echo -e "${GREEN}✅ Dossier Data créé${NC}"

# Créer .env si nécessaire
if [ ! -f "$PROJECT_DIR/.env" ]; then
    if [ -f "$PROJECT_DIR/.env.example" ]; then
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
        echo -e "${GREEN}✅ Fichier .env créé${NC}"
        echo -e "${YELLOW}⚠️  N'oubliez pas d'éditer .env pour configurer vos clés API${NC}"
    fi
else
    echo -e "${GREEN}✅ Fichier .env existant conservé${NC}"
fi

# Créer les dossiers supplémentaires
mkdir -p "$PROJECT_DIR/Data/backups"
mkdir -p "$PROJECT_DIR/logs"
echo -e "${GREEN}✅ Dossiers supplémentaires créés${NC}"

# ═══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 5: Initialisation de la base de données
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo -e "${CYAN}▶ Étape 5/6 : Initialisation de la base de données${NC}"

python -c "from modules.db.migrations import init_db; init_db()" || {
    echo -e "${RED}❌ Échec de l'initialisation de la base de données${NC}"
    exit 1
}

echo -e "${GREEN}✅ Base de données initialisée${NC}"

# ═══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 6: Vérification finale
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo -e "${CYAN}▶ Étape 6/6 : Vérification finale${NC}"

# Test des imports critiques
python -c "
import sys
try:
    import streamlit
    import pandas
    import plotly
    import cryptography
    from modules.db.migrations import init_db
    print('✅ Tous les imports critiques OK')
    sys.exit(0)
except ImportError as e:
    print(f'❌ Import échoué: {e}')
    sys.exit(1)
" || {
    echo -e "${RED}❌ Vérification des imports échouée${NC}"
    exit 1
}

# ═══════════════════════════════════════════════════════════════════════════════
# RÉSUMÉ
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo -e "${GREEN}${BOLD}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}  ✅ Installation terminée avec succès !${NC}"
echo -e "${GREEN}${BOLD}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}Prochaines étapes :${NC}"
echo ""
echo "1. ${BOLD}Configurer les clés API${NC} (optionnel mais recommandé)"
echo "   Éditez le fichier : $PROJECT_DIR/.env"
echo "   - GEMINI_API_KEY (gratuit sur https://aistudio.google.com/app/apikey)"
echo "   - ENCRYPTION_KEY (générez avec : python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\")"
echo ""
echo "2. ${BOLD}Lancer l'application${NC}"
echo "   Double-cliquez sur : MyFinance.command"
echo "   Ou en ligne de commande :"
echo "     source .venv/bin/activate && streamlit run app.py"
echo ""
echo "3. ${BOLD}Importer vos données${NC}"
echo "   - Exportez vos relevés bancaires en CSV"
echo "   - Utilisez la page Import pour les charger"
echo ""
echo -e "${YELLOW}Documentation :${NC} https://github.com/votre-repo/FinancePerso#readme"
echo ""
echo -e "${GREEN}🚀 Prêt à démarrer !${NC}"
echo ""

# Proposer de lancer immédiatement
read -p "Lancer l'application maintenant ? (O/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo ""
    ./MyFinance.command
fi
