# 🐛 Guide de Débogage des Avatars

Ce guide vous aide à diagnostiquer pourquoi vos avatars ne se chargent pas.

## 🔍 Logs de Débogage Détaillés

Le système inclut désormais des logs très détaillés pour tracer chaque étape du chargement des avatars.

### Activer les Logs de Debug

Les logs de debug sont affichés dans la console et dans le fichier de log de l'application.

**Emplacement des logs** :
- Mode normal : `~/.ChatBot_BDM_Desktop/logs/`
- Mode portable : `data/logs/` (à côté de l'exécutable)

### Ce que Vous Verrez dans les Logs

Quand un avatar est chargé, vous verrez ces lignes dans les logs :

```
[HTML_GEN][AVATAR] Chargement avatar pour rôle: user
[HTML_GEN][AVATAR] Base path: /chemin/vers/ChatBot-BDM-Desktop
[HTML_GEN][AVATAR] Avatar directory: /chemin/vers/ChatBot-BDM-Desktop/assets/avatars
[HTML_GEN][AVATAR] Avatar directory exists: True
[HTML_GEN][AVATAR] Fichiers dans .../assets/avatars: ['user.png', 'assistant.png', 'README.md']
[HTML_GEN][AVATAR] Recherche fichier: user.png
[HTML_GEN][AVATAR] Chemin complet: .../assets/avatars/user.png
[HTML_GEN][AVATAR] Fichier existe: True
[HTML_GEN][AVATAR] ✓ Fichier trouvé: .../assets/avatars/user.png
[HTML_GEN][AVATAR] Permissions lecture: True
[HTML_GEN][AVATAR] Taille fichier: 2048 octets
[HTML_GEN][AVATAR] Lecture fichier...
[HTML_GEN][AVATAR] Données lues: 2048 octets
[HTML_GEN][AVATAR] Base64 encodé: 2732 caractères
[HTML_GEN][AVATAR] Base64 preview: iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHA...
[HTML_GEN][AVATAR] Type MIME détecté: image/png
[HTML_GEN][AVATAR] ✓ Avatar user chargé avec succès (base64)
[HTML_GEN][AVATAR] HTML tag length: 2850 caractères
```

## 🔎 Diagnostic Étape par Étape

### Étape 1 : Vérifier que les Fichiers Existent

```bash
# Lister les fichiers dans le dossier avatars
ls -lh assets/avatars/

# Devrait afficher :
# -rw-r--r-- 1 user user 2.0K Dec  9 20:00 user.png
# -rw-r--r-- 1 user user 1.8K Dec  9 20:00 assistant.png
```

**✅ Fichiers trouvés** → Passez à l'étape 2
**❌ Fichiers manquants** → Créez-les (voir `CUSTOMISATION_AVATARS.md`)

### Étape 2 : Vérifier le Contenu des Fichiers

```bash
# Vérifier que ce sont bien des images PNG
file assets/avatars/user.png
file assets/avatars/assistant.png

# Devrait afficher :
# assets/avatars/user.png: PNG image data, 48 x 48, 8-bit/color RGBA, non-interlaced
```

**✅ Fichiers PNG valides** → Passez à l'étape 3
**❌ Fichiers corrompus** → Recréez-les

### Étape 3 : Vérifier les Permissions

```bash
# Vérifier les permissions de lecture
ls -l assets/avatars/*.png

# Devrait avoir 'r' (lecture) pour user/group/other :
# -rw-r--r-- ou -rw-rw-r--
```

**✅ Permissions OK** → Passez à l'étape 4
**❌ Pas de permissions** → Corrigez avec `chmod 644 assets/avatars/*.png`

### Étape 4 : Consulter les Logs

Lancez l'application et envoyez un message. Consultez les logs :

```bash
# Afficher les logs en temps réel
tail -f ~/.ChatBot_BDM_Desktop/logs/chatbot_YYYYMMDD.log | grep AVATAR

# Ou rechercher dans le fichier de log le plus récent
grep AVATAR ~/.ChatBot_BDM_Desktop/logs/chatbot_*.log | tail -50
```

### Étape 5 : Interpréter les Logs

#### Cas 1 : Fichier Non Trouvé

```
[HTML_GEN][AVATAR] Fichier existe: False
[HTML_GEN][AVATAR] ✗ Fichier non trouvé: .../user.png, utilisation emoji fallback
```

**Problème** : Le fichier n'existe pas ou le chemin est incorrect
**Solution** : Vérifiez que le fichier est bien nommé `user.png` (pas `User.png` ou autre)

#### Cas 2 : Erreur de Permissions

```
[HTML_GEN][AVATAR] Permissions lecture: False
[HTML_GEN][AVATAR] ✗ Erreur permissions pour .../user.png
```

**Problème** : Pas de permissions de lecture
**Solution** : `chmod 644 assets/avatars/*.png`

#### Cas 3 : Fichier Vide

```
[HTML_GEN][AVATAR] Taille fichier: 0 octets
[HTML_GEN][AVATAR] ⚠ Fichier vide: .../user.png
```

**Problème** : Le fichier existe mais est vide
**Solution** : Recréez le fichier image

#### Cas 4 : Erreur d'Encodage

```
[HTML_GEN][AVATAR] Données lues: 2048 octets
[HTML_GEN][AVATAR] ✗ Erreur chargement avatar user: [erreur détaillée]
```

**Problème** : Erreur lors de l'encodage base64
**Solution** : Vérifiez que l'image n'est pas corrompue

#### Cas 5 : Succès

```
[HTML_GEN][AVATAR] ✓ Avatar user chargé avec succès (base64)
```

**✅ L'avatar devrait s'afficher !**

Si l'avatar ne s'affiche toujours pas, le problème vient d'ailleurs (voir ci-dessous).

## 🐞 Problèmes Courants et Solutions

### Problème : Les logs disent "chargé avec succès" mais l'avatar ne s'affiche pas

**Causes possibles** :

1. **Cache du navigateur** : QWebEngineView peut avoir mis en cache l'ancien HTML
   - **Solution** : Redémarrez complètement l'application
   - Ou créez une nouvelle conversation

2. **Problème CSS** : La classe `.avatar-img` n'est pas appliquée
   - **Solution** : Vérifiez les logs pour voir si le CSS est bien chargé

3. **Image trop grande** : Le base64 est trop long (> 50KB recommandé)
   - **Solution** : Réduisez la taille de vos images à 48×48 pixels

### Problème : "Avatar directory exists: False"

**Cause** : Le dossier `assets/avatars/` n'existe pas

**Solution** :
```bash
mkdir -p assets/avatars
```

### Problème : "Base path: /tmp/..."

**Cause** : Mode PyInstaller détecté, fichiers dans un dossier temporaire

**Solution** : C'est normal en mode exécutable. Vérifiez que les fichiers sont inclus dans le build (voir `BUILD.md`)

### Problème : Warnings "Langage introuvable: html/css"

**Cause** : Fichiers `html.min.js` et `css.min.js` non disponibles dans Highlight.js

**Solution** : Ces warnings ont été supprimés dans la dernière version. Le langage `xml` est utilisé à la place pour HTML.

## 🧪 Test Manuel

Créez un script de test pour vérifier le chargement :

```python
# test_avatar_loading.py
import sys
from pathlib import Path
from utils.html_generator import HTMLGenerator
from core.logger import get_logger

# Initialiser le logger
logger = get_logger()

# Créer le générateur HTML
gen = HTMLGenerator()

# Tester les avatars
print("Test des avatars:")
print("-" * 50)

for role in ['user', 'assistant', 'system']:
    avatar_html = gen._get_avatar(role)
    print(f"{role}: ", end="")

    if '<img' in avatar_html:
        # Image chargée
        if 'base64' in avatar_html:
            print("✓ Image base64 chargée")
            # Afficher la longueur
            length = len(avatar_html)
            print(f"  Longueur HTML: {length} caractères")
        else:
            print("⚠ Image chargée mais pas en base64")
    else:
        # Emoji fallback
        print(f"Emoji fallback: {avatar_html}")

print("-" * 50)
```

Exécutez-le :
```bash
python test_avatar_loading.py
```

## 📊 Informations Système pour le Debug

Si vous demandez de l'aide, incluez ces informations :

```bash
# Version Python
python --version

# Système d'exploitation
uname -a  # Linux/Mac
# ou
systeminfo | findstr /B /C:"OS"  # Windows

# Contenu du dossier avatars
ls -laR assets/avatars/

# Vérifier les types de fichiers
file assets/avatars/*

# Dernières lignes des logs avec AVATAR
tail -100 ~/.ChatBot_BDM_Desktop/logs/chatbot_*.log | grep -A 5 -B 5 AVATAR
```

## 🔧 Mode Debug Avancé

Pour activer encore plus de logs, modifiez le niveau de log dans `core/logger.py` :

```python
# Changer de INFO à DEBUG
logging.basicConfig(level=logging.DEBUG)
```

Puis relancez l'application. Vous verrez **tous** les logs de debug, y compris ceux des avatars.

## 📝 Ce qui a Changé (Version Décembre 2025)

### Améliorations du Debug

1. **Logs détaillés** : Chaque étape du chargement est tracée
2. **Vérifications multiples** : Permissions, taille, encodage
3. **Messages clairs** : ✓ pour succès, ✗ pour échec
4. **Préfixe `[AVATAR]`** : Facile à filtrer dans les logs

### Corrections Appliquées

1. **Encodage base64** : Remplace `file:///` pour compatibilité QWebEngineView
2. **Gestion d'erreurs** : Try/catch autour de chaque opération
3. **Fallback intelligent** : Revient toujours aux emojis en cas d'échec
4. **Warnings HTML/CSS** : Changés en debug (pas critique)

## 💡 Conseils Finaux

- **Commencez simple** : Testez avec des petites images PNG 48×48
- **Vérifiez les logs** : C'est votre meilleur outil de diagnostic
- **Utilisez les emojis** : Ils fonctionnent toujours comme fallback
- **Testez progressivement** : Un avatar à la fois

---

**Si le problème persiste**, créez un issue GitHub avec :
- Les logs complets (filtrés sur `[AVATAR]`)
- Les informations système
- Une capture d'écran des fichiers (`ls -la assets/avatars/`)
