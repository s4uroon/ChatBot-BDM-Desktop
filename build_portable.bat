@echo off
REM ============================================================================
REM Script de Build - ChatBot BDM Desktop - Version Portable Windows
REM ============================================================================
REM
REM Ce script compile l'application ChatBot BDM Desktop en un exécutable
REM Windows portable qui peut être placé n'importe où sur l'ordinateur.
REM
REM Prérequis :
REM   - Python 3.8 ou supérieur installé
REM   - PyInstaller installé (pip install pyinstaller)
REM   - Toutes les dépendances installées (pip install -r requirements.txt)
REM
REM Usage :
REM   Double-cliquez sur ce fichier ou exécutez : build_portable.bat
REM
REM ============================================================================

echo.
echo ============================================================================
echo  CHATBOT BDM DESKTOP - BUILD PORTABLE WINDOWS
echo ============================================================================
echo.

REM Vérifier si Python est disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installé ou n'est pas dans le PATH
    echo.
    echo Veuillez installer Python 3.8 ou supérieur depuis https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python détecté
python --version
echo.

REM Vérifier si PyInstaller est installé
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] PyInstaller n'est pas installé
    echo.
    echo Installation de PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERREUR] Impossible d'installer PyInstaller
        pause
        exit /b 1
    )
)

echo [OK] PyInstaller est installé
echo.

REM Nettoyer les anciens builds
echo [1/4] Nettoyage des anciens builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
echo [OK] Nettoyage terminé
echo.

REM Compiler l'application
echo [2/4] Compilation de l'application avec PyInstaller...
echo.
pyinstaller ChatBot_BDM_Desktop.spec

if errorlevel 1 (
    echo.
    echo [ERREUR] La compilation a échoué
    echo Vérifiez les messages d'erreur ci-dessus
    pause
    exit /b 1
)

echo.
echo [OK] Compilation réussie
echo.

REM Créer le dossier data dans la distribution
echo [3/4] Création du dossier de données...
if not exist "dist\ChatBot BDM Desktop\data" mkdir "dist\ChatBot BDM Desktop\data"
echo [OK] Dossier data créé
echo.

REM Créer un fichier README dans la distribution
echo [4/4] Création du fichier README...
(
echo ============================================================================
echo  CHATBOT BDM DESKTOP - VERSION PORTABLE
echo ============================================================================
echo.
echo Cette version portable peut être placée n'importe où sur votre ordinateur.
echo.
echo UTILISATION :
echo   Double-cliquez sur "ChatBot BDM Desktop.exe" pour lancer l'application
echo.
echo DONNÉES :
echo   Toutes vos données ^(conversations, paramètres, etc.^) sont stockées
echo   dans le dossier "data" à côté de l'exécutable.
echo.
echo DÉPLACEMENT :
echo   Vous pouvez déplacer tout le dossier "ChatBot BDM Desktop" où vous
echo   voulez sur votre ordinateur ou même sur une clé USB.
echo.
echo DÉSINSTALLATION :
echo   Supprimez simplement le dossier "ChatBot BDM Desktop" pour désinstaller
echo   complètement l'application.
echo.
echo ============================================================================
echo  Version : 1.0.0
echo  Date : %date%
echo ============================================================================
) > "dist\ChatBot BDM Desktop\README.txt"
echo [OK] README créé
echo.

echo ============================================================================
echo  BUILD TERMINÉ AVEC SUCCÈS !
echo ============================================================================
echo.
echo L'application portable se trouve dans :
echo   dist\ChatBot BDM Desktop\
echo.
echo Pour lancer l'application :
echo   1. Ouvrez le dossier "dist\ChatBot BDM Desktop"
echo   2. Double-cliquez sur "ChatBot BDM Desktop.exe"
echo.
echo Pour distribuer l'application :
echo   - Compressez le dossier "dist\ChatBot BDM Desktop" en ZIP
echo   - Envoyez le fichier ZIP aux utilisateurs
echo   - Ils n'auront qu'à extraire et lancer l'exe
echo.
echo ============================================================================
echo.

pause
