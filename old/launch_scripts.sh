#!/bin/bash
# ============================================================================
# 1. run.bat - Script Windows
# ============================================================================
# Sauvegarder ce contenu dans "run.bat" à la racine du projet

@echo off
title Chatbot Desktop
echo.
echo ========================================
echo   CHATBOT DESKTOP - LANCEMENT
echo ========================================
echo.

REM Vérifier si l'environnement virtuel existe
if not exist "venv\" (
    echo [ERREUR] Environnement virtuel non trouve
    echo Veuillez executer setup.bat d'abord
    pause
    exit /b 1
)

REM Activer l'environnement virtuel
echo [INFO] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Lancer l'application
echo [INFO] Demarrage de l'application...
echo.
python main.py %*

REM Désactiver l'environnement
deactivate

echo.
echo ========================================
echo   APPLICATION FERMEE
echo ========================================
pause


# ============================================================================
# 2. run_debug.bat - Script Windows Mode Debug
# ============================================================================
# Sauvegarder ce contenu dans "run_debug.bat"

@echo off
title Chatbot Desktop - Debug Mode
echo.
echo ========================================
echo   CHATBOT DESKTOP - MODE DEBUG
echo ========================================
echo.

if not exist "venv\" (
    echo [ERREUR] Environnement virtuel non trouve
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
echo [INFO] Demarrage en mode DEBUG...
echo.
python main.py --debug

deactivate
pause


# ============================================================================
# 3. setup.bat - Script d'Installation Windows
# ============================================================================
# Sauvegarder ce contenu dans "setup.bat"

@echo off
title Chatbot Desktop - Installation
echo.
echo ========================================
echo   CHATBOT DESKTOP - INSTALLATION
echo ========================================
echo.

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH
    echo Telechargez Python depuis: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python detecte
python --version
echo.

REM Créer l'environnement virtuel
echo [INFO] Creation de l'environnement virtuel...
python -m venv venv

if errorlevel 1 (
    echo [ERREUR] Echec de creation de l'environnement virtuel
    pause
    exit /b 1
)

echo [OK] Environnement virtuel cree
echo.

REM Activer et installer les dépendances
echo [INFO] Installation des dependances...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERREUR] Echec de l'installation des dependances
    pause
    exit /b 1
)

echo.
echo ========================================
echo   INSTALLATION TERMINEE !
echo ========================================
echo.
echo Pour lancer l'application:
echo   - Double-cliquez sur run.bat
echo   - Ou executez: python main.py
echo.
echo Pour le mode debug:
echo   - Double-cliquez sur run_debug.bat
echo.
pause


# ============================================================================
# 4. run.sh - Script Linux/macOS
# ============================================================================
# Sauvegarder ce contenu dans "run.sh" et faire: chmod +x run.sh

#!/bin/bash

echo ""
echo "========================================"
echo "  CHATBOT DESKTOP - LANCEMENT"
echo "========================================"
echo ""

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "[ERREUR] Environnement virtuel non trouvé"
    echo "Veuillez exécuter setup.sh d'abord"
    exit 1
fi

# Activer l'environnement virtuel
echo "[INFO] Activation de l'environnement virtuel..."
source venv/bin/activate

# Lancer l'application
echo "[INFO] Démarrage de l'application..."
echo ""
python main.py "$@"

# Désactiver l'environnement
deactivate

echo ""
echo "========================================"
echo "  APPLICATION FERMÉE"
echo "========================================"


# ============================================================================
# 5. run_debug.sh - Script Linux/macOS Mode Debug
# ============================================================================
# Sauvegarder ce contenu dans "run_debug.sh" et faire: chmod +x run_debug.sh

#!/bin/bash

echo ""
echo "========================================"
echo "  CHATBOT DESKTOP - MODE DEBUG"
echo "========================================"
echo ""

if [ ! -d "venv" ]; then
    echo "[ERREUR] Environnement virtuel non trouvé"
    exit 1
fi

source venv/bin/activate
echo "[INFO] Démarrage en mode DEBUG..."
echo ""
python main.py --debug

deactivate


# ============================================================================
# 6. setup.sh - Script d'Installation Linux/macOS
# ============================================================================
# Sauvegarder ce contenu dans "setup.sh" et faire: chmod +x setup.sh

#!/bin/bash

echo ""
echo "========================================"
echo "  CHATBOT DESKTOP - INSTALLATION"
echo "========================================"
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "[ERREUR] Python 3 n'est pas installé"
    echo "Installez Python depuis: https://www.python.org/downloads/"
    exit 1
fi

echo "[OK] Python détecté"
python3 --version
echo ""

# Créer l'environnement virtuel
echo "[INFO] Création de l'environnement virtuel..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "[ERREUR] Échec de création de l'environnement virtuel"
    exit 1
fi

echo "[OK] Environnement virtuel créé"
echo ""

# Activer et installer les dépendances
echo "[INFO] Installation des dépendances..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[ERREUR] Échec de l'installation des dépendances"
    exit 1
fi

# Rendre les scripts exécutables
chmod +x run.sh
chmod +x run_debug.sh

echo ""
echo "========================================"
echo "  INSTALLATION TERMINÉE !"
echo "========================================"
echo ""
echo "Pour lancer l'application:"
echo "  - Exécutez: ./run.sh"
echo "  - Ou: python main.py"
echo ""
echo "Pour le mode debug:"
echo "  - Exécutez: ./run_debug.sh"
echo ""

deactivate
