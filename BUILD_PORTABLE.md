# Guide de Build - Version Portable Windows

Ce guide explique comment créer une version portable de **ChatBot BDM Desktop** pour Windows. La version portable permet de placer l'application n'importe où sur l'ordinateur sans installation.

## 📋 Table des matières

1. [Caractéristiques de la version portable](#caractéristiques)
2. [Prérequis](#prérequis)
3. [Compilation de l'application](#compilation)
4. [Structure de la version portable](#structure)
5. [Distribution](#distribution)
6. [Dépannage](#dépannage)

---

## 🎯 Caractéristiques

La version portable de ChatBot BDM Desktop offre les avantages suivants :

- ✅ **Aucune installation requise** - Double-clic sur l'exe et c'est parti
- ✅ **Portable** - Peut être placé n'importe où (disque dur, clé USB, réseau)
- ✅ **Données utilisateur sécurisées** - Base de données et paramètres dans le profil utilisateur
- ✅ **Fichiers temporaires portables** - Logs et exports à côté de l'exe
- ✅ **Pas de modification du registre** - Aucune modification du registre Windows
- ✅ **Facile à désinstaller** - Supprimez le dossier et nettoyez ~/.ChatBot_BDM_Desktop/

---

## 📦 Prérequis

Avant de compiler l'application, assurez-vous d'avoir :

### 1. Python 3.8 ou supérieur

```bash
# Vérifier la version de Python
python --version
```

Si Python n'est pas installé, téléchargez-le depuis [python.org](https://www.python.org/downloads/)

### 2. Dépendances Python

```bash
# Installer toutes les dépendances
pip install -r requirements.txt

# Installer PyInstaller (si pas déjà inclus)
pip install pyinstaller
```

### 3. Environnement Windows

La compilation doit être effectuée sur Windows pour créer un exécutable Windows.

---

## 🔨 Compilation

Vous avez **3 options** pour compiler l'application :

### Option 1 : Script Batch (Recommandé pour débutants)

Double-cliquez simplement sur :

```
build_portable.bat
```

Le script va :
1. Vérifier que Python et PyInstaller sont installés
2. Nettoyer les anciens builds
3. Compiler l'application
4. Créer la structure de dossiers
5. Générer un fichier README

### Option 2 : Script PowerShell

Clic droit sur `build_portable.ps1` → **Exécuter avec PowerShell**

Ou en ligne de commande :

```powershell
PowerShell -ExecutionPolicy Bypass -File build_portable.ps1
```

### Option 3 : Ligne de commande manuelle

```bash
# 1. Nettoyer les anciens builds
rmdir /s /q build dist

# 2. Compiler avec PyInstaller
pyinstaller ChatBot_BDM_Desktop.spec

# 3. Créer le dossier data
mkdir "dist\ChatBot BDM Desktop\data"
```

---

## 📁 Structure de la version portable

Après compilation réussie, vous trouverez dans `dist/ChatBot BDM Desktop/` :

```
ChatBot BDM Desktop/
├── ChatBot BDM Desktop.exe    ← Exécutable principal
├── data/                       ← Fichiers temporaires (créé au premier lancement)
│   ├── logs/                  ← Fichiers de logs (si activés)
│   └── exports/               ← Exports des conversations
├── _internal/                  ← Bibliothèques et dépendances (PyInstaller)
│   ├── PyQt6/
│   ├── openai/
│   └── ...
└── README.txt                  ← Instructions pour l'utilisateur
```

**⚠️ IMPORTANT - Stockage des données utilisateur :**

Les fichiers de données utilisateur sont stockés dans un répertoire caché du profil utilisateur :

```
Windows: C:\Users\VOTRE_NOM\.ChatBot_BDM_Desktop\
├── chatbot.db                 ← Base de données des conversations
└── settings.ini               ← Configuration de l'application

Linux/Mac: ~/.ChatBot_BDM_Desktop/
├── chatbot.db
└── settings.ini
```

### Détails importants :

- **ChatBot BDM Desktop.exe** : L'exécutable à lancer
- **data/** : Dossier contenant les logs et exports (fichiers temporaires/portables)
- **~/.ChatBot_BDM_Desktop/** : Répertoire utilisateur caché contenant la base de données et les paramètres
- **_internal/** : Dépendances (ne pas modifier)
- **README.txt** : Instructions pour les utilisateurs finaux

### Pourquoi cette séparation ?

- **chatbot.db et settings.ini** sont stockés dans le profil utilisateur pour :
  - Garantir la persistance des données même si l'exécutable est déplacé
  - Éviter les problèmes de permissions sur certains emplacements (clé USB, réseau)
  - Permettre la sauvegarde facile via les outils de backup utilisateur

- **logs/ et exports/** restent portables pour :
  - Faciliter le débogage lors du support technique
  - Permettre l'export des conversations directement depuis le dossier portable

---

## 📤 Distribution

### Préparer le package pour distribution

1. **Compresser le dossier**

   ```bash
   # Le dossier à compresser est :
   dist\ChatBot BDM Desktop\
   ```

   - Clic droit → **Envoyer vers** → **Dossier compressé**
   - Ou utilisez 7-Zip, WinRAR, etc.

2. **Nommer le fichier ZIP**

   ```
   ChatBot-BDM-Desktop-v2.1.0-Portable-Windows.zip
   ```

3. **Distribuer le fichier**

   - Envoyez le ZIP par email, cloud, clé USB, etc.
   - Publiez sur GitHub Releases
   - Partagez sur votre site web

### Instructions pour les utilisateurs finaux

Incluez ces instructions avec la distribution :

```
=== INSTALLATION ===

1. Extraire le fichier ZIP dans un dossier de votre choix
   Exemple : C:\Programs\ChatBot BDM Desktop\

2. Double-cliquer sur "ChatBot BDM Desktop.exe"

=== UTILISATION ===

- L'application se lance directement, aucune installation nécessaire
- Vos conversations et paramètres sont stockés dans : C:\Users\VOTRE_NOM\.ChatBot_BDM_Desktop\
- Les logs et exports sont dans le dossier "data" à côté de l'exécutable
- Vous pouvez déplacer le dossier de l'application où vous voulez

=== STOCKAGE DES DONNÉES ===

- Base de données (chatbot.db) : C:\Users\VOTRE_NOM\.ChatBot_BDM_Desktop\chatbot.db
- Paramètres (settings.ini) : C:\Users\VOTRE_NOM\.ChatBot_BDM_Desktop\settings.ini
- Logs : Dans le dossier "data/logs" à côté de l'exécutable
- Exports : Dans le dossier "data/exports" à côté de l'exécutable

=== DÉSINSTALLATION ===

Pour désinstaller complètement l'application :

1. Supprimez le dossier de l'application
2. Supprimez le dossier C:\Users\VOTRE_NOM\.ChatBot_BDM_Desktop\ (contient vos données)
```

---

## 🔧 Dépannage

### Problème : PyInstaller n'est pas reconnu

**Solution :**

```bash
pip install --upgrade pyinstaller
```

### Problème : Erreur "Module not found" pendant la compilation

**Solution :**

Vérifiez que toutes les dépendances sont installées :

```bash
pip install -r requirements.txt --upgrade
```

### Problème : L'exe se lance mais se ferme immédiatement

**Solution :**

1. Lancez l'exe depuis une invite de commande pour voir les erreurs :

   ```bash
   cd "dist\ChatBot BDM Desktop"
   "ChatBot BDM Desktop.exe" --debug
   ```

2. Vérifiez les logs dans `data/logs/`

### Problème : L'application ne trouve pas les données

**Cause :** Le mode portable n'est pas activé correctement

**Solution :**

Le mode portable s'active automatiquement quand l'application est compilée avec PyInstaller. Si vous testez le script Python directement, créez un fichier `portable.txt` dans le répertoire du projet :

```bash
# Dans le répertoire du projet
echo. > portable.txt
python main.py --debug
```

### Problème : Antivirus bloque l'exécutable

**Cause :** Les exécutables PyInstaller peuvent être détectés comme faux positifs

**Solutions :**

1. Ajoutez une exception dans votre antivirus
2. Signez numériquement l'exécutable (nécessite un certificat)
3. Soumettez l'exe à VirusTotal et aux éditeurs d'antivirus

### Problème : Taille de l'exe trop grande

**Solution :**

Optimisez la compilation dans `ChatBot_BDM_Desktop.spec` :

- Ajoutez plus de modules dans la liste `excludes`
- Utilisez UPX pour compresser (déjà activé par défaut)
- Créez un installeur NSIS au lieu d'un dossier

---

## 🛠️ Personnalisation

### Changer l'icône de l'application

1. Créez ou obtenez un fichier `.ico` (16x16 à 256x256 pixels)

2. Placez-le dans le projet, par exemple : `assets/icon.ico`

3. Modifiez `ChatBot_BDM_Desktop.spec` :

   ```python
   exe = EXE(
       ...
       icon='assets/icon.ico',  # ← Décommenter et mettre le bon chemin
   )
   ```

4. Recompilez

### Inclure des fichiers supplémentaires

Dans `ChatBot_BDM_Desktop.spec`, section `datas` :

```python
datas=[
    ('assets', 'assets'),      # Inclure le dossier assets
    ('config.ini', '.'),       # Inclure un fichier de config
],
```

### Créer une version avec console (pour debug)

Dans `ChatBot_BDM_Desktop.spec`, changez :

```python
exe = EXE(
    ...
    console=True,  # ← Mettre True au lieu de False
)
```

---

## 📊 Comparaison des versions

| Fonctionnalité | Version normale | Version portable |
|----------------|-----------------|------------------|
| Installation | Non requise | Non requise |
| Base de données & Paramètres | `~/.ChatBot_BDM_Desktop/` | `~/.ChatBot_BDM_Desktop/` |
| Logs & Exports | `~/.ChatBot_BDM_Desktop/` | `./data/` (à côté de l'exe) |
| Mobilité de l'exe | Fixe | Complètement mobile |
| Données utilisateur | Profil utilisateur | Profil utilisateur |
| Traces système | Oui (dossier home) | Oui (dossier home pour DB/settings) |
| Taille | ~5 Mo (script) | ~150-200 Mo (exe+deps) |

---

## 📝 Notes techniques

### Détection du mode portable

Le mode portable est activé automatiquement dans ces cas :

1. **Exécutable PyInstaller** : Détecté via `sys.frozen`
2. **Fichier marqueur** : Présence de `portable.txt` dans le répertoire

Code de détection (dans `main.py`) :

```python
def is_portable_mode() -> bool:
    if getattr(sys, 'frozen', False):
        return True  # Mode frozen = portable
    else:
        portable_marker = Path(__file__).parent / 'portable.txt'
        return portable_marker.exists()
```

### Gestion des chemins

La classe `UserPaths` (dans `core/paths.py`) gère automatiquement :

**Mode normal :**
- Base de données : `~/.ChatBot_BDM_Desktop/chatbot.db`
- Paramètres : `~/.ChatBot_BDM_Desktop/settings.ini`
- Logs : `~/.ChatBot_BDM_Desktop/logs/`
- Exports : `~/.ChatBot_BDM_Desktop/exports/`

**Mode portable :**
- Base de données : `~/.ChatBot_BDM_Desktop/chatbot.db` (TOUJOURS dans le profil utilisateur)
- Paramètres : `~/.ChatBot_BDM_Desktop/settings.ini` (TOUJOURS dans le profil utilisateur)
- Logs : `{exe_dir}/data/logs/` (portable)
- Exports : `{exe_dir}/data/exports/` (portable)

**Raison de cette architecture :**
- Les données critiques (DB, settings) restent dans le profil utilisateur pour garantir leur persistance et éviter les problèmes de permissions
- Les fichiers temporaires (logs, exports) peuvent être portables pour faciliter le support technique

### PyInstaller - Comment ça marche

PyInstaller :

1. Analyse les imports Python
2. Collecte toutes les dépendances
3. Crée un exécutable autonome
4. Extrait les fichiers au lancement (mode onedir)
5. Lance l'application Python

---

## 🚀 Prochaines étapes

Après avoir créé la version portable :

1. ✅ Testez sur différentes machines Windows
2. ✅ Testez avec différentes versions de Windows (10, 11)
3. ✅ Vérifiez que les données sont bien stockées dans `data/`
4. ✅ Testez le déplacement du dossier vers un autre emplacement
5. ✅ Créez une release GitHub avec le ZIP
6. ✅ Documentez pour les utilisateurs finaux

---

## 📞 Support

Pour toute question ou problème :

- 🐛 **Bugs** : Ouvrez une issue sur GitHub
- 💬 **Questions** : Consultez le README principal
- 📧 **Contact** : Voir le fichier CONTRIBUTING.md

---

**Dernière mise à jour** : 2024

**Auteur** : ChatBot BDM Team

**Licence** : Voir LICENSE
