# 🎨 Guide de Personnalisation des Avatars

Ce guide explique comment personnaliser les avatars (icônes) de l'utilisateur et de l'IA dans l'interface du chat.

## ⚡ Correctif Important (Décembre 2025)

**Problème résolu** : Les avatars utilisent maintenant l'**encodage base64** au lieu du protocole `file:///`.
**Raison** : QWebEngineView bloque le chargement d'images locales via `file:///` pour des raisons de sécurité.
**Solution** : Les images sont automatiquement encodées en base64 et intégrées directement dans le HTML.

## 📁 Emplacement des Images

Les images d'avatar doivent être placées dans le dossier :
```
assets/avatars/
```

## 📝 Fichiers Requis

Créez les fichiers suivants dans `assets/avatars/` :

| Fichier | Description | Utilisation |
|---------|-------------|-------------|
| `user.png` | Avatar de l'utilisateur | Messages de l'utilisateur |
| `assistant.png` | Avatar de l'IA/Assistant | Réponses de l'IA |
| `system.png` | Avatar système (optionnel) | Messages système |

## 🎯 Caractéristiques des Images

### Formats Supportés
- **PNG** (recommandé) - Supporte la transparence
- **JPG/JPEG** - Sans transparence
- **WebP** - Format moderne, bonne compression
- **SVG** - Vectoriel, scalable (nécessite extension `.png` dans le nom de fichier)

### Spécifications Techniques

| Propriété | Valeur Recommandée | Notes |
|-----------|-------------------|-------|
| **Dimensions** | 48×48 pixels | Taille optimale pour l'affichage |
| **Ratio** | 1:1 (carré) | Images circulaires à l'affichage |
| **Résolution** | 72-96 DPI | Standard web |
| **Poids** | < 50 KB | Pour performances optimales |
| **Fond** | Transparent | PNG avec canal alpha |
| **Colorimétrie** | RGB ou RGBA | Pas de CMYK |

### Dimensions Alternatives Acceptées
- 32×32 pixels (minimum)
- 64×64 pixels
- 128×128 pixels (haute résolution)

## 🎨 Recommandations de Design

### Style Visuel
- **Cohérence** : Les deux avatars doivent avoir un style similaire
- **Contraste** : Bien visible sur fond sombre (#1e1e1e)
- **Simplicité** : Design épuré et reconnaissable
- **Couleurs** : Compatibles avec le thème sombre de l'interface

### Exemples de Concepts
- **Utilisateur** : Silhouette, initiales, photo de profil
- **Assistant** : Robot, cerveau, icône IA, logo personnalisé

## 🚀 Création Rapide d'Avatars de Test

### Méthode 1 : Avec Python (Pillow)

Si vous avez Python et Pillow installés :

```python
from PIL import Image, ImageDraw, ImageFont

def create_avatar(filename, bg_color, text):
    img = Image.new('RGBA', (48, 48), bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()

    # Centrer le texte
    bbox = draw.textbbox((0, 0), text, font=font)
    x = (48 - (bbox[2] - bbox[0])) // 2
    y = (48 - (bbox[3] - bbox[1])) // 2 - 2

    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    img.save(filename, 'PNG')

# Créer les avatars
create_avatar('assets/avatars/user.png', (33, 150, 243, 255), 'U')
create_avatar('assets/avatars/assistant.png', (76, 175, 80, 255), 'AI')
```

### Méthode 2 : Téléchargement Gratuit

Sites avec des avatars gratuits :
- **Flaticon** : https://www.flaticon.com/free-icons/user
- **Icons8** : https://icons8.com/icons/set/avatar
- **Freepik** : https://www.freepik.com/icons/avatar

### Méthode 3 : Générateurs en Ligne

- **Avatar Maker** : https://avatarmaker.com/
- **Picrew** : https://picrew.me/
- **DiceBear** : https://www.dicebear.com/ (API génératrice d'avatars)

### Méthode 4 : Outils Graphiques

- **GIMP** (gratuit) : Créez un carré 48×48, ajoutez du texte/formes, exportez en PNG
- **Paint.NET** (Windows) : Similaire à GIMP
- **Photopea** (en ligne) : https://www.photopea.com/ - comme Photoshop, gratuit

## 🔧 Comment Modifier les Avatars

### Étape 1 : Préparer vos Images
1. Créez ou obtenez vos images d'avatar
2. Redimensionnez-les à 48×48 pixels
3. Assurez-vous qu'elles ont un fond transparent (si PNG)
4. Nommez-les exactement : `user.png` et `assistant.png`

### Étape 2 : Placer les Fichiers
```bash
# Copiez vos fichiers dans le dossier assets/avatars/
cp votre_avatar_utilisateur.png assets/avatars/user.png
cp votre_avatar_assistant.png assets/avatars/assistant.png
```

### Étape 3 : Redémarrer l'Application
Les nouveaux avatars seront chargés au prochain démarrage de l'application.

## 🔄 Fallback vers Emojis

Si les fichiers images ne sont **pas trouvés**, l'application utilisera automatiquement des emojis par défaut :

| Rôle | Emoji | Description |
|------|-------|-------------|
| Utilisateur | 👤 | Silhouette de personne |
| Assistant | 🤖 | Robot |
| Système | ⚙️ | Engrenage |

Cela permet de :
- Tester l'application sans images personnalisées
- Avoir un affichage par défaut fonctionnel
- Éviter les erreurs si les images sont supprimées

## 🖼️ Rendu des Avatars

### CSS Appliqué
Les images sont affichées avec les styles suivants :
```css
.avatar-img {
    width: 32px;
    height: 32px;
    border-radius: 50%;          /* Forme circulaire */
    object-fit: cover;           /* Recadrage automatique */
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    border: 2px solid #3d3d3d;
}
```

### Caractéristiques d'Affichage
- **Forme** : Circulaire (border-radius: 50%)
- **Taille** : 32×32 pixels à l'écran
- **Position** : Centré au-dessus de chaque message
- **Ombre** : Légère pour effet de profondeur
- **Bordure** : 2px gris foncé (#3d3d3d)

## 🛠️ Dépannage

### Les images ne s'affichent pas

**Note** : Depuis le correctif de décembre 2025, les images sont encodées en base64 au lieu d'utiliser `file:///`.

Vérifications :
1. ✅ Les fichiers sont dans `assets/avatars/`
2. ✅ Les noms sont exacts : `user.png`, `assistant.png`
3. ✅ Les fichiers sont au format PNG, JPG, ou WebP
4. ✅ Les fichiers ne sont pas corrompus (ouvrez-les dans un visualiseur d'images)
5. ✅ Redémarrez complètement l'application

Si les images ne se chargent toujours pas, consultez les logs :
- Cherchez `[HTML_GEN] Erreur chargement avatar` dans les logs
- Vérifiez les permissions de lecture : `ls -l assets/avatars/`

### Les images sont déformées
- Utilisez des images carrées (ratio 1:1)
- Le `object-fit: cover` recadrera automatiquement

### Les images sont floues
- Utilisez au minimum 48×48 pixels
- Vérifiez la qualité de l'image source
- Utilisez PNG ou SVG pour la meilleure netteté

## 📂 Structure des Fichiers Modifiés

Les avatars sont gérés par ces fichiers :

```
ChatBot-BDM-Desktop/
├── assets/
│   └── avatars/               # Dossier des images d'avatar
│       ├── README.md          # Instructions
│       ├── user.png           # Avatar utilisateur (à créer)
│       ├── assistant.png      # Avatar assistant (à créer)
│       └── system.png         # Avatar système (optionnel)
├── utils/
│   └── html_generator.py      # Génération HTML avec avatars
├── core/
│   └── export_manager.py      # Export (utilise emojis)
└── CUSTOMISATION_AVATARS.md   # Ce guide
```

## 💡 Exemples d'Utilisation

### Utiliser un Logo d'Entreprise
```bash
# Utilisez le logo de votre entreprise comme avatar assistant
cp logo_entreprise.png assets/avatars/assistant.png
```

### Utiliser des Initiales
Créez une image avec vos initiales (ex: "AB") sur fond coloré :
- Police : 24px, bold
- Couleur de fond : #2196F3 (bleu)
- Couleur texte : blanc
- Export : 48×48 pixels, PNG transparent

### Utiliser des Icônes
Téléchargez des icônes depuis :
- [Flaticon](https://www.flaticon.com/)
- [Icons8](https://icons8.com/)
- [Feather Icons](https://feathericons.com/)

## 🎓 Notes Techniques

### Chemin d'Accès
Le code utilise un chemin absolu avec protocole `file:///` :
```python
file:///chemin/absolu/vers/assets/avatars/user.png
```

### Support Multi-Format
L'extension `.png` est utilisée par défaut, mais vous pouvez modifier le code pour supporter d'autres extensions dans `utils/html_generator.py:344-347`.

### Performance
- Images en cache par le navigateur (QWebEngineView)
- Chargement asynchrone
- Pas d'impact sur les performances si images < 50KB

## 📞 Support

Pour toute question ou problème :
1. Consultez les logs de l'application
2. Vérifiez la console de développement (F12)
3. Consultez `utils/html_generator.py` pour le code source

---

**Dernière mise à jour** : 2025-12-09
**Version** : 1.0
