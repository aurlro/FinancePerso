@echo off
chcp 65001 >nul
cls

:: ═══════════════════════════════════════════════════════════════════════════════
:: MyFinance Companion - Script de Lancement Windows
:: ═══════════════════════════════════════════════════════════════════════════════

echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║              💰 MyFinance Companion - Windows                        ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

:: Configuration
set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%.venv"
set "REQUIREMENTS_FILE=%PROJECT_DIR%requirements.txt"
set "PYTHON_CMD=python"

:: Vérifier Python
echo ▶ Vérification de Python...
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou n'est pas dans le PATH
    echo.
    echo Installez Python 3.11+ depuis : https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%a in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%a
echo ✅ %PYTHON_VERSION% détecté

:: Se placer dans le dossier
cd /d "%PROJECT_DIR%"

:: Vérifier/Créer l'environnement virtuel
echo.
echo ▶ Configuration de l'environnement virtuel...

if not exist "%VENV_DIR%" (
    echo 📦 Création de l'environnement virtuel...
    %PYTHON_CMD% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo ❌ Échec de la création de l'environnement virtuel
        pause
        exit /b 1
    )
    echo ✅ Environnement créé
) else (
    echo ✅ Environnement virtuel existant
)

:: Activer l'environnement
call "%VENV_DIR%\Scripts\activate.bat"

:: Vérifier Streamlit
echo.
echo ▶ Vérification des dépendances...
%PYTHON_CMD% -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installation des dépendances...
    pip install --upgrade pip -q
    pip install -r "%REQUIREMENTS_FILE%"
    if errorlevel 1 (
        echo ❌ Échec de l'installation
        pause
        exit /b 1
    )
    echo ✅ Dépendances installées
) else (
    echo ✅ Dépendances OK
)

:: Créer Data si nécessaire
if not exist "%PROJECT_DIR%Data" mkdir "%PROJECT_DIR%Data"

:: Créer .env si nécessaire
if not exist "%PROJECT_DIR%.env" (
    if exist "%PROJECT_DIR%.env.example" (
        copy "%PROJECT_DIR%.env.example" "%PROJECT_DIR%.env" >nul
        echo ⚠️  Fichier .env créé - Éditez-le pour configurer vos clés API
    )
)

:: Lancer
echo.
echo ════════════════════════════════════════════════════════════════════
echo   🚀 Lancement de MyFinance Companion...
echo ════════════════════════════════════════════════════════════════════
echo.
echo URL : http://localhost:8501
echo Appuyez sur Ctrl+C pour arrêter
echo.

%PYTHON_CMD% -m streamlit run app.py --server.port=8501 --browser.gatherUsageStats=false

pause
