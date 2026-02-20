# ============================================================================
# Script de Build - ChatBot BDM Desktop - Version Portable Windows (PowerShell)
# ============================================================================
#
# Ce script compile l'application ChatBot BDM Desktop en un exécutable
# Windows portable qui peut être placé n'importe où sur l'ordinateur.
#
# Prérequis :
#   - Python 3.8 ou supérieur installé
#   - PyInstaller installé (pip install pyinstaller)
#   - Toutes les dépendances installées (pip install -r requirements.txt)
#
# Usage :
#   PowerShell -ExecutionPolicy Bypass -File build_portable.ps1
#   OU clic droit > Exécuter avec PowerShell
#
# ============================================================================

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host " CHATBOT BDM DESKTOP - BUILD PORTABLE WINDOWS" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Fonction pour afficher les messages
function Write-Step {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Error-Message {
    param([string]$Message)
    Write-Host "[ERREUR] $Message" -ForegroundColor Red
}

# Vérifier si Python est disponible
Write-Step "Vérification de Python..."
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python non trouvé"
    }
    Write-Success "Python détecté : $pythonVersion"
} catch {
    Write-Error-Message "Python n'est pas installé ou n'est pas dans le PATH"
    Write-Host ""
    Write-Host "Veuillez installer Python 3.8 ou supérieur depuis https://www.python.org/" -ForegroundColor White
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}
Write-Host ""

# Vérifier si PyInstaller est installé
Write-Step "Vérification de PyInstaller..."
try {
    python -c "import PyInstaller" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller non trouvé"
    }
    Write-Success "PyInstaller est installé"
} catch {
    Write-Error-Message "PyInstaller n'est pas installé"
    Write-Host ""
    Write-Host "Installation de PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Message "Impossible d'installer PyInstaller"
        Read-Host "Appuyez sur Entrée pour quitter"
        exit 1
    }
    Write-Success "PyInstaller installé"
}
Write-Host ""

# Nettoyer les anciens builds
Write-Step "[1/4] Nettoyage des anciens builds..."
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}
Write-Success "Nettoyage terminé"
Write-Host ""

# Compiler l'application
Write-Step "[2/4] Compilation de l'application avec PyInstaller..."
Write-Host ""
pyinstaller ChatBot_BDM_Desktop.spec

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Error-Message "La compilation a échoué"
    Write-Host "Vérifiez les messages d'erreur ci-dessus" -ForegroundColor White
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

Write-Host ""
Write-Success "Compilation réussie"
Write-Host ""

# Note : Le dossier data/ sera créé automatiquement par l'application si nécessaire
Write-Step "[3/4] Préparation de la distribution..."
Write-Success "Distribution prête"
Write-Host ""

# Créer un fichier README dans la distribution
Write-Step "[4/4] Création du fichier README..."
$readmeContent = @"
============================================================================
 CHATBOT BDM DESKTOP - VERSION PORTABLE
============================================================================

Cette version portable peut être placée n'importe où sur votre ordinateur.

UTILISATION :
  Double-cliquez sur "ChatBot BDM Desktop.exe" pour lancer l'application

STOCKAGE DES DONNÉES :
  - Base de données et paramètres : Stockés dans votre profil utilisateur
    Windows : C:\Users\VOTRE_NOM\.ChatBot_BDM_Desktop\
    (chatbot.db et settings.ini)

  - Logs et exports : Stockés dans le dossier "data" à côté de l'exécutable
    (créé automatiquement lors de la première utilisation)

DÉPLACEMENT :
  Vous pouvez déplacer le dossier "ChatBot BDM Desktop" où vous voulez.
  Vos conversations et paramètres resteront dans votre profil utilisateur.

DÉSINSTALLATION :
  1. Supprimez le dossier "ChatBot BDM Desktop"
  2. Si souhaité, supprimez aussi C:\Users\VOTRE_NOM\.ChatBot_BDM_Desktop\
     pour effacer toutes vos conversations et paramètres

============================================================================
 Version : 2.1.0
 Date : $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
============================================================================
"@

Set-Content -Path "dist\ChatBot BDM Desktop\README.txt" -Value $readmeContent -Encoding UTF8
Write-Success "README créé"
Write-Host ""

Write-Host "============================================================================" -ForegroundColor Green
Write-Host " BUILD TERMINÉ AVEC SUCCÈS !" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "L'application portable se trouve dans :" -ForegroundColor White
Write-Host "  dist\ChatBot BDM Desktop\" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pour lancer l'application :" -ForegroundColor White
Write-Host "  1. Ouvrez le dossier 'dist\ChatBot BDM Desktop'" -ForegroundColor White
Write-Host "  2. Double-cliquez sur 'ChatBot BDM Desktop.exe'" -ForegroundColor White
Write-Host ""
Write-Host "Pour distribuer l'application :" -ForegroundColor White
Write-Host "  - Compressez le dossier 'dist\ChatBot BDM Desktop' en ZIP" -ForegroundColor White
Write-Host "  - Envoyez le fichier ZIP aux utilisateurs" -ForegroundColor White
Write-Host "  - Ils n'auront qu'à extraire et lancer l'exe" -ForegroundColor White
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Green
Write-Host ""

Read-Host "Appuyez sur Entrée pour quitter"
