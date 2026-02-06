#!/bin/bash

# Script de lancement et d'installation pour MyFinance Companion
# Ce script détecte si l'application est installée et l'installe si nécessaire

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
echo -e "${BLUE}  MyFinance Companion - Installation et Lancement${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo ""

# 1. Se placer dans le dossier du projet
cd "$PROJECT_DIR" || {
    echo -e "${RED}❌ Erreur : Impossible d'accéder au dossier $PROJECT_DIR${NC}"
    read -p "Appuyez sur Entrée pour quitter..."
    exit 1
}

echo -e "📂 Dossier du projet : $(pwd)"
echo ""

# 2. Détecter Python 3
echo -e "${BLUE}🔍 Vérification de Python 3...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo -e "${RED}❌ Erreur : Python 3 n'est pas installé.${NC}"
    echo -e "${YELLOW}💡 Veuillez installer Python 3 depuis https://www.python.org/downloads/${NC}"
    read -p "Appuyez sur Entrée pour quitter..."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo -e "${GREEN}✅ $PYTHON_VERSION détecté${NC}"
echo ""

# 3. Vérifier si l'environnement virtuel existe
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}⚠️  Environnement virtuel non trouvé à : $VENV_DIR${NC}"
    echo -e "${BLUE}📦 Création de l'environnement virtuel...${NC}"
    
    $PYTHON_CMD -m venv "$VENV_DIR" || {
        echo -e "${RED}❌ Erreur lors de la création de l'environnement virtuel${NC}"
        echo -e "${YELLOW}💡 Essayez de lancer : $PYTHON_CMD -m pip install --user virtualenv${NC}"
        read -p "Appuyez sur Entrée pour quitter..."
        exit 1
    }
    
    echo -e "${GREEN}✅ Environnement virtuel créé${NC}"
    echo ""
fi

# 4. Activer l'environnement virtuel
echo -e "${BLUE}🔄 Activation de l'environnement virtuel...${NC}"
source "$VENV_DIR/bin/activate" || {
    echo -e "${RED}❌ Erreur : Impossible d'activer l'environnement virtuel${NC}"
    read -p "Appuyez sur Entrée pour quitter..."
    exit 1
}
echo -e "${GREEN}✅ Environnement virtuel activé${NC}"
echo ""

# 5. Vérifier si les dépendances sont installées
echo -e "${BLUE}🔍 Vérification des dépendances...${NC}"

# Vérifier si streamlit est installé
if ! $PYTHON_CMD -c "import streamlit" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Dépendances non installées${NC}"
    
    if [ -f "$REQUIREMENTS_FILE" ]; then
        echo -e "${BLUE}📦 Installation des dépendances depuis requirements.txt...${NC}"
        echo -e "${YELLOW}⏳ Cette opération peut prendre quelques minutes...${NC}"
        echo ""
        
        pip install --upgrade pip
        pip install -r "$REQUIREMENTS_FILE" || {
            echo -e "${RED}❌ Erreur lors de l'installation des dépendances${NC}"
            read -p "Appuyez sur Entrée pour quitter..."
            exit 1
        }
        
        echo ""
        echo -e "${GREEN}✅ Dépendances installées avec succès${NC}"
    else
        echo -e "${RED}❌ Fichier requirements.txt non trouvé${NC}"
        read -p "Appuyez sur Entrée pour quitter..."
        exit 1
    fi
else
    echo -e "${GREEN}✅ Dépendances déjà installées${NC}"
fi

echo ""

# 6. Vérifier le fichier .env
echo -e "${BLUE}🔍 Vérification de la configuration...${NC}"
if [ ! -f "$PROJECT_DIR/.env" ] && [ -f "$PROJECT_DIR/.env.example" ]; then
    echo -e "${YELLOW}⚠️  Fichier .env non trouvé, création depuis .env.example...${NC}"
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo -e "${GREEN}✅ Fichier .env créé${NC}"
    echo -e "${YELLOW}💡 Vous pouvez modifier ce fichier pour configurer vos clés API${NC}"
else
    echo -e "${GREEN}✅ Configuration OK${NC}"
fi

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  🚀 Lancement de MyFinance Companion...${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
echo ""

# 7. Lancer l'application
$PYTHON_CMD -m streamlit run app.py || {
    echo ""
    echo -e "${RED}❌ L'application s'est arrêtée avec une erreur${NC}"
    read -p "Appuyez sur Entrée pour fermer..."
    exit 1
}

# 8. En cas d'arrêt normal
echo ""
echo -e "${BLUE}👋 Application arrêtée${NC}"
read -p "Appuyez sur Entrée pour fermer cette fenêtre..."
