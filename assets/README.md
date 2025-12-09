# Assets - Ressources de l'Application

Ce dossier contient les ressources (assets) utilisées par l'application ChatBot BDM Desktop.

## 📂 Structure

```
assets/
├── avatars/                    # Avatars personnalisés du chat
│   ├── README.md
│   ├── user.png               # Avatar utilisateur (à créer)
│   └── assistant.png          # Avatar IA (à créer)
├── highlightjs/               # Bibliothèque de coloration syntaxique
│   ├── highlight.min.js
│   ├── languages/
│   └── styles/
└── ChatBot_BDM_Desktop.ico    # Icône de l'application Windows (REQUIS)
```

## 🎨 Fichier d'Icône Requis : `ChatBot_BDM_Desktop.ico`

### ⚠️ Important

Le fichier **`ChatBot_BDM_Desktop.ico`** doit être créé et placé dans le dossier `assets/` pour que le build portable fonctionne correctement.

Ce fichier est utilisé comme icône de l'application Windows dans :
- L'exécutable `.exe`
- La barre des tâches Windows
- Les raccourcis
- L'explorateur de fichiers

### 📋 Spécifications du Fichier .ico

| Propriété | Valeur Requise |
|-----------|----------------|
| **Format** | `.ico` (Windows Icon) |
| **Dimensions** | Multi-résolution (recommandé) |
| **Résolutions incluses** | 16×16, 32×32, 48×48, 256×256 |
| **Profondeur couleur** | 32-bit (avec canal alpha) |
| **Emplacement** | `assets/ChatBot_BDM_Desktop.ico` |

### 🔧 Comment Créer le Fichier .ico

#### Option 1 : Conversion en Ligne (Simple)

1. Créez ou trouvez une image PNG/JPG de votre logo (minimum 256×256 pixels)
2. Allez sur un convertisseur en ligne :
   - https://convertio.co/fr/png-ico/
   - https://www.icoconverter.com/
   - https://image.online-convert.com/convert-to-ico
3. Téléchargez votre image
4. Sélectionnez "Multi-résolution" ou "Toutes les tailles"
5. Téléchargez le fichier `.ico` généré
6. Renommez-le en `ChatBot_BDM_Desktop.ico`
7. Placez-le dans le dossier `assets/`

#### Option 2 : Avec GIMP (Gratuit)

1. Téléchargez et installez GIMP : https://www.gimp.org/
2. Ouvrez votre image source (PNG, JPG, etc.)
3. Redimensionnez à 256×256 : Image → Échelle et taille de l'image
4. Exportez : Fichier → Exporter sous...
5. Nommez le fichier `ChatBot_BDM_Desktop.ico`
6. Sélectionnez le format `.ico`
7. Dans les options, cochez toutes les résolutions (16, 32, 48, 256)
8. Placez le fichier dans `assets/`

#### Option 3 : Avec ImageMagick (Ligne de commande)

```bash
# Installer ImageMagick d'abord
# Windows: choco install imagemagick
# Linux: sudo apt install imagemagick
# Mac: brew install imagemagick

# Convertir une image PNG en .ico multi-résolution
magick convert votre_logo.png -define icon:auto-resize=256,128,64,48,32,16 assets/ChatBot_BDM_Desktop.ico
```

#### Option 4 : Avec Python (Pillow)

```python
from PIL import Image

# Charger l'image source
img = Image.open('votre_logo.png')

# Redimensionner et créer les différentes tailles
icon_sizes = [(16, 16), (32, 32), (48, 48), (256, 256)]

# Sauvegarder en .ico avec toutes les résolutions
img.save(
    'assets/ChatBot_BDM_Desktop.ico',
    format='ICO',
    sizes=icon_sizes
)
```

### 🎨 Recommandations de Design

- **Style** : Simple et reconnaissable
- **Couleurs** : Contrastées (visible sur fond clair et sombre)
- **Détails** : Évitez trop de détails (illisible à petite taille)
- **Fond** : Transparent (canal alpha) recommandé
- **Format source** : PNG ou SVG avec fond transparent

### ✅ Vérification

Après avoir créé le fichier, vérifiez :

```bash
# Le fichier doit exister à cet emplacement exact
ls -lh assets/ChatBot_BDM_Desktop.ico

# Pour compiler le build portable avec l'icône
pyinstaller ChatBot_BDM_Desktop.spec
```

### 🚨 Que se passe-t-il si le fichier est absent ?

Si le fichier `ChatBot_BDM_Desktop.ico` n'existe pas :
- ❌ PyInstaller échouera lors du build avec une erreur
- ❌ Le build portable ne pourra pas être créé
- ❌ L'exécutable utilisera l'icône par défaut de Python

**Solution** : Créez le fichier avant de lancer `pyinstaller ChatBot_BDM_Desktop.spec`

### 📖 Ressources Utiles

- Icônes gratuites : https://www.flaticon.com/
- Icônes open-source : https://icons8.com/
- Générateur d'icônes : https://favicon.io/
- Documentation PyInstaller : https://pyinstaller.org/en/stable/usage.html#icon

---

## 📁 Autres Ressources

### Avatars (`avatars/`)
Voir `avatars/README.md` pour les détails sur la personnalisation des avatars du chat.

### Highlight.js (`highlightjs/`)
Bibliothèque de coloration syntaxique pour les blocs de code dans le chat.
Inclut plusieurs langages et thèmes (clair/sombre).

---

**Note** : Ce dossier `assets/` et tout son contenu seront automatiquement inclus dans le build portable grâce à la configuration du fichier `ChatBot_BDM_Desktop.spec`.
