#!/bin/bash

# Script de lancement robuste pour MyFinance Companion

# 1. Se placer dans le dossier du projet (chemin absolu)
PROJECT_DIR="/Users/aurelien/Documents/Projets/FinancePerso"
cd "$PROJECT_DIR" || exit

echo "🚀 Lancement de MyFinance Companion..."
echo "📂 Dossier : $(pwd)"

# 2. Détecter Python 3
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
else
    echo "❌ Erreur : Python 3 n'est pas trouvé."
    read -p "Appuyez sur Entrée pour quitter..."
    exit 1
fi

echo "✅ Utilisation de : $($PYTHON_CMD --version)"

# 3. Lancer l'application directement via le module python
# C'est plus fiable que d'appeler l'exécutable 'streamlit' qui peut ne pas être dans le PATH
$PYTHON_CMD -m streamlit run app.py

# 4. En cas d'erreur ou d'arrêt
read -p "Application arrêtée. Appuyez sur Entrée pour fermer cette fenêtre..."
