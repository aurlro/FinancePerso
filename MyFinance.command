#!/bin/bash

# Script de lancement intelligent pour MyFinance Companion
# Détecte si l'app est déjà installée et ne réinstalle que si nécessaire

# Configuration
PROJECT_DIR="/Users/aurelien/Documents/Projets/FinancePerso"
VENV_DIR="$PROJECT_DIR/venv"
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"

# Couleurs pour les messages
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  MyFinance Companion${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo ""

# 1. Se placer dans le dossier du projet
cd "$PROJECT_DIR" || {
    echo -e "${RED}❌ Erreur : Impossible d'accéder au dossier $PROJECT_DIR${NC}"
    read -p "Appuyez sur Entrée pour quitter..."
    exit 1
}

# 2. Détecter Python 3
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo -e "${RED}❌ Python 3 n'est pas installé.${NC}"
    echo -e "${YELLOW}💡 https://www.python.org/downloads/${NC}"
    read -p "Appuyez sur Entrée pour quitter..."
    exit 1
fi

# 3. FONCTION CLÉ : Vérifier si on peut déjà lancer l'app
check_if_ready() {
    # Vérifier si streamlit est disponible (globalement ou via un venv existant)
    if $PYTHON_CMD -c "import streamlit" 2>/dev/null; then
        return 0  # Prêt !
    fi
    
    # Vérifier si un venv existe et contient streamlit
    if [ -d "$VENV_DIR" ]; then
        if "$VENV_DIR/bin/python" -c "import streamlit" 2>/dev/null; then
            return 0  # Prêt via venv existant !
        fi
    fi
    
    return 1  # Pas prêt, besoin d'installation
}

# 4. Si tout est prêt, lancer directement !
if check_if_ready; then
    echo -e "${GREEN}✅ Application détectée, lancement rapide...${NC}"
    echo ""
    
    # Si le venv existe et a streamlit, l'utiliser
    if [ -d "$VENV_DIR" ] && "$VENV_DIR/bin/python" -c "import streamlit" 2>/dev/null; then
        source "$VENV_DIR/bin/activate"
    fi
    
    echo -e "${GREEN}🚀 Lancement de MyFinance Companion...${NC}"
    echo ""
    $PYTHON_CMD -m streamlit run app.py
    
    echo ""
    read -p "Appuyez sur Entrée pour fermer..."
    exit 0
fi

# 5. Sinon, procéder à l'installation
echo -e "${YELLOW}⚠️  Application non détectée ou installation incomplète${NC}"
echo -e "${BLUE}📦 Démarrage de l'installation...${NC}"
echo ""

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${BLUE}📦 Création de l'environnement virtuel...${NC}"
    $PYTHON_CMD -m venv "$VENV_DIR" || {
        echo -e "${RED}❌ Erreur lors de la création du venv${NC}"
        read -p "Appuyez sur Entrée pour quitter..."
        exit 1
    }
    echo -e "${GREEN}✅ Environnement créé${NC}"
    echo ""
fi

# Activer l'environnement
source "$VENV_DIR/bin/activate"

# Installer les dépendances
echo -e "${BLUE}📦 Installation des dépendances...${NC}"
echo -e "${YELLOW}⏳ Cela peut prendre quelques minutes (une seule fois)...${NC}"
echo ""

pip install --upgrade pip -q
pip install -r "$REQUIREMENTS_FILE" || {
    echo -e "${RED}❌ Erreur lors de l'installation${NC}"
    read -p "Appuyez sur Entrée pour quitter..."
    exit 1
}

echo ""
echo -e "${GREEN}✅ Installation terminée !${NC}"
echo ""

# Créer .env si nécessaire
if [ ! -f "$PROJECT_DIR/.env" ] && [ -f "$PROJECT_DIR/.env.example" ]; then
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo -e "${GREEN}✅ Configuration créée${NC}"
fi

# Lancer
echo -e "${GREEN}🚀 Lancement de MyFinance Companion...${NC}"
echo ""
$PYTHON_CMD -m streamlit run app.py

echo ""
read -p "Appuyez sur Entrée pour fermer..."
