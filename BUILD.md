# 🛠️ Guide de Build Portable - ChatBot BDM Desktop

Ce document explique comment créer un build portable (exécutable Windows) de l'application ChatBot BDM Desktop.

## 📋 Prérequis

### Logiciels Requis

- **Python 3.10+** installé
- **PyInstaller** installé : `pip install pyinstaller`
- **Toutes les dépendances** : `pip install -r requirements.txt`

### Fichiers Requis

Avant de lancer le build, assurez-vous que les fichiers suivants existent :

#### ⚠️ OBLIGATOIRE : Icône de l'application

```
assets/ChatBot_BDM_Desktop.ico
```

**Ce fichier est REQUIS** pour le build. Sans lui, PyInstaller échouera.

📖 Consultez `assets/README.md` pour savoir comment créer ce fichier.

#### 📁 Dossier Assets Complet

Le dossier `assets/` doit contenir :
```
assets/
├── ChatBot_BDM_Desktop.ico    ✅ REQUIS
├── highlightjs/               ✅ Déjà présent
│   ├── highlight.min.js
│   ├── languages/
│   └── styles/
└── avatars/                   ✅ Automatiquement créé
    ├── README.md
    ├── user.png              (optionnel)
    └── assistant.png         (optionnel)
```

## 🚀 Processus de Build

### Étape 1 : Vérifier les Prérequis

```bash
# Vérifier que Python est installé
python --version

# Vérifier que PyInstaller est installé
pyinstaller --version

# Vérifier que le fichier .ico existe
ls -lh assets/ChatBot_BDM_Desktop.ico
```

### Étape 2 : Installer les Dépendances

```bash
# Installer toutes les dépendances du projet
pip install -r requirements.txt

# Installer PyInstaller si ce n'est pas déjà fait
pip install pyinstaller
```

### Étape 3 : Nettoyer les Builds Précédents (Optionnel)

```bash
# Supprimer les anciens builds
rm -rf build/
rm -rf dist/

# Ou sous Windows
rmdir /s /q build
rmdir /s /q dist
```

### Étape 4 : Lancer le Build

```bash
# Compiler l'application avec PyInstaller
pyinstaller ChatBot_BDM_Desktop.spec
```

### Étape 5 : Vérifier le Build

Le build sera créé dans :
```
dist/ChatBot BDM Desktop/
├── ChatBot BDM Desktop.exe    # Exécutable principal
├── assets/                    # Dossier assets inclus
│   ├── avatars/
│   └── highlightjs/
├── _internal/                 # Dépendances Python et bibliothèques
└── [autres fichiers DLL et dépendances]
```

### Étape 6 : Tester l'Exécutable

```bash
# Lancer l'application
cd "dist/ChatBot BDM Desktop"
"./ChatBot BDM Desktop.exe"
```

## 📦 Configuration du Build

Le fichier `ChatBot_BDM_Desktop.spec` configure PyInstaller :

### Fichiers Inclus Automatiquement

```python
datas=[
    # Dossier assets (avatars + highlightjs)
    ('assets', 'assets'),
],
```

Cela garantit que :
- ✅ Les avatars personnalisés dans `assets/avatars/` sont inclus
- ✅ Les fichiers Highlight.js dans `assets/highlightjs/` sont inclus
- ✅ L'icône de l'application est utilisée pour l'exécutable

### Icône de l'Application

```python
exe = EXE(
    ...
    # Icône de l'application Windows (.ico)
    icon='assets/ChatBot_BDM_Desktop.ico',
)
```

## 🎨 Personnalisation Avant le Build

### Ajouter vos Avatars Personnalisés

Avant de compiler, vous pouvez ajouter vos propres avatars :

```bash
# Copier vos images d'avatar
cp mes_avatars/user.png assets/avatars/user.png
cp mes_avatars/assistant.png assets/avatars/assistant.png
```

Ces fichiers seront automatiquement inclus dans le build.

📖 Consultez `CUSTOMISATION_AVATARS.md` pour les spécifications des avatars.

### Personnaliser l'Icône de l'Application

Remplacez `assets/ChatBot_BDM_Desktop.ico` par votre propre icône :

```bash
# Remplacer l'icône
cp mon_icone.ico assets/ChatBot_BDM_Desktop.ico
```

## 🔧 Compatibilité PyInstaller

Le code a été optimisé pour fonctionner à la fois :
- ✅ En mode développement (script Python)
- ✅ En mode exécutable (PyInstaller)

### Détection Automatique du Mode

Le code détecte automatiquement s'il est exécuté comme script ou comme exécutable :

```python
if getattr(sys, 'frozen', False):
    # Mode exécutable PyInstaller
    base_path = Path(sys._MEIPASS)
else:
    # Mode script Python
    base_path = Path(__file__).parent.parent
```

Cela garantit que les assets sont chargés correctement dans les deux cas.

## 📊 Taille du Build

### Taille Estimée

- **Build complet** : ~200-300 MB (avec toutes les dépendances PyQt6)
- **Exécutable seul** : ~50-100 MB
- **Assets** : ~500 KB (highlightjs + avatars)

### Réduire la Taille

Pour réduire la taille du build, modifiez `ChatBot_BDM_Desktop.spec` :

```python
excludes=[
    # Modules déjà exclus
    'matplotlib', 'scipy', 'numpy', 'pandas', 'PIL', 'tkinter',
    # Ajoutez d'autres modules non utilisés
],
```

## 🐛 Dépannage

### Erreur : "FileNotFoundError: assets/ChatBot_BDM_Desktop.ico"

**Cause** : Le fichier `.ico` n'existe pas.

**Solution** : Créez le fichier `assets/ChatBot_BDM_Desktop.ico` (voir `assets/README.md`)

### Erreur : "ModuleNotFoundError: No module named 'PyQt6'"

**Cause** : Dépendances manquantes.

**Solution** :
```bash
pip install -r requirements.txt
```

### Les Avatars ne s'affichent pas dans le Build

**Vérifications** :
1. ✅ Les fichiers sont dans `assets/avatars/`
2. ✅ Le dossier `assets/` est bien inclus dans `datas=` du `.spec`
3. ✅ Les chemins sont corrects (pas de `/` en dur)

**Solution** : Vérifiez que le code utilise `_get_base_path()` pour les chemins.

### Les Fichiers Highlight.js ne se chargent pas

**Cause** : Chemins incorrects ou fichiers non inclus.

**Solution** :
```bash
# Vérifier que les fichiers existent
ls -R assets/highlightjs/
```

Le dossier doit contenir `highlight.min.js` et les sous-dossiers `languages/` et `styles/`.

## 📝 Distribution

### Créer une Archive ZIP

```bash
# Windows (PowerShell)
Compress-Archive -Path "dist/ChatBot BDM Desktop" -DestinationPath "ChatBot_BDM_Desktop_Portable.zip"

# Linux/Mac
cd dist
zip -r ChatBot_BDM_Desktop_Portable.zip "ChatBot BDM Desktop"
```

### Structure de Distribution Recommandée

```
ChatBot_BDM_Desktop_Portable.zip
└── ChatBot BDM Desktop/
    ├── ChatBot BDM Desktop.exe
    ├── README.txt               # Instructions pour l'utilisateur
    ├── assets/
    ├── _internal/
    └── data/                    # Créé automatiquement au premier lancement
        ├── logs/
        └── exports/
```

### Créer un README pour les Utilisateurs

Créez un fichier `README.txt` à inclure dans la distribution :

```text
ChatBot BDM Desktop - Version Portable
======================================

Installation :
1. Extraire l'archive ZIP
2. Lancer "ChatBot BDM Desktop.exe"

Configuration :
- Base de données : ~/.ChatBot_BDM_Desktop/chatbot.db
- Paramètres : ~/.ChatBot_BDM_Desktop/settings.ini
- Logs : ./data/logs/
- Exports : ./data/exports/

Support :
[Votre email ou site web de support]
```

## 🔄 Mise à Jour du Build

Pour mettre à jour le build après des modifications du code :

```bash
# 1. Nettoyer les anciens builds
rm -rf build/ dist/

# 2. Mettre à jour les dépendances si nécessaire
pip install -r requirements.txt --upgrade

# 3. Recompiler
pyinstaller ChatBot_BDM_Desktop.spec

# 4. Tester
cd "dist/ChatBot BDM Desktop"
"./ChatBot BDM Desktop.exe"
```

## 📚 Ressources

- **PyInstaller Documentation** : https://pyinstaller.org/
- **Guide des Avatars** : `CUSTOMISATION_AVATARS.md`
- **Guide de l'Icône** : `assets/README.md`
- **Configuration Build** : `ChatBot_BDM_Desktop.spec`

---

**Dernière mise à jour** : 2025-12-09
**Version PyInstaller** : 6.0+
**Version Python** : 3.10+
