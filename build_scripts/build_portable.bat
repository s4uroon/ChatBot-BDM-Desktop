@echo off
REM ============================================================================
REM Script de Build - ChatBot BDM Desktop - Version Portable Windows
REM ============================================================================
REM Se déplacer vers le répertoire racine du projet (parent de build_scripts)
cd /d "%~dp0\.."
REM
REM Ce script compile l'application ChatBot BDM Desktop en un exécutable
REM Windows portable qui peut être placé n'importe où sur l'ordinateur.
REM
REM Prérequis :
REM   - Python 3.9 ou supérieur installé
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
    echo Veuillez installer Python 3.9 ou supérieur depuis https://www.python.org/
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

REM Note : Le dossier data/ sera créé automatiquement par l'application si nécessaire
echo [3/4] Préparation de la distribution...
echo [OK] Distribution prête
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
echo STOCKAGE DES DONNÉES :
echo   - Base de données et paramètres : Stockés dans votre profil utilisateur
echo     Windows : C:\Users\VOTRE_NOM\.ChatBot_BDM_Desktop\
echo     ^(chatbot.db et settings.ini^)
echo.
echo   - Logs et exports : Stockés dans le dossier "data" à côté de l'exécutable
echo     ^(créé automatiquement lors de la première utilisation^)
echo.
echo DÉPLACEMENT :
echo   Vous pouvez déplacer le dossier "ChatBot BDM Desktop" où vous voulez.
echo   Vos conversations et paramètres resteront dans votre profil utilisateur.
echo.
echo DÉSINSTALLATION :
echo   1. Supprimez le dossier "ChatBot BDM Desktop"
echo   2. Si souhaité, supprimez aussi C:\Users\VOTRE_NOM\.ChatBot_BDM_Desktop\
echo      pour effacer toutes vos conversations et paramètres
echo.
echo ============================================================================
echo  Version : 2.2.0
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
