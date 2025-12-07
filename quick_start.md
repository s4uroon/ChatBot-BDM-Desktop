# 🚀 Guide de Démarrage Rapide - Chatbot Desktop

## Installation Express (5 minutes)

### Windows

1. **Télécharger Python 3.8+** (si pas installé)
   - https://www.python.org/downloads/
   - ✅ Cocher "Add Python to PATH"

2. **Ouvrir PowerShell/CMD dans le dossier du projet**

3. **Créer l'environnement virtuel**
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

4. **Installer les dépendances**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Lancer l'application**
   ```powershell
   python main.py
   ```

### Linux / macOS

1. **Ouvrir un terminal dans le dossier du projet**

2. **Créer l'environnement virtuel**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Lancer l'application**
   ```bash
   python main.py
   ```

## ⚙️ Configuration Initiale (2 minutes)

### 1. Obtenir une Clé API

**Option A - OpenAI** (officiel)
- Aller sur https://platform.openai.com/api-keys
- Créer une clé API
- Format : `sk-proj-...`

**Option B - Serveur Local** (ex: LM Studio, Ollama)
- Installer LM Studio : https://lmstudio.ai/
- Lancer le serveur local (port 1234 par défaut)
- URL : `http://localhost:1234/v1`
- Clé : `lm-studio` (ou n'importe quoi)

### 2. Configurer dans l'Application

1. **Lancer** : `python main.py`
2. **Menu** : `Paramètres` → `Configuration...`
3. **Remplir** :
   ```
   Clé API: sk-proj-... (ou lm-studio pour local)
   URL de base: https://api.openai.com/v1 (ou http://localhost:1234/v1)
   Modèle: gpt-4 (ou nom du modèle local)
   SSL: ☐ Décocher si serveur local
   ```
4. **Tester** : Bouton `🔍 Tester la connexion`
5. **Enregistrer** : `💾 Enregistrer`

## 💬 Premier Message

1. **Nouvelle conversation** : `Ctrl+N` ou bouton `➕ Nouvelle`
2. **Taper un message** dans la zone en bas
3. **Envoyer** : Appuyer sur `Entrée`
4. **Voir la réponse** en streaming en temps réel ! ✨

## 🎨 Personnalisation (optionnel)

### Changer les Couleurs de Code

1. `Paramètres` → Onglet `🎨 Apparence Code`
2. Cliquer sur les boutons `🎨` pour choisir des couleurs
3. Voir la prévisualisation en direct
4. `💾 Enregistrer`

## 📤 Export

1. **Sélectionner** des conversations (Shift+Clic)
2. `Fichier` → `Exporter...` (Ctrl+E)
3. Choisir **JSON** ou **Markdown**
4. Sauvegarder

## 🐛 Problèmes Courants

### "Module PyQt6 not found"
```bash
pip install --upgrade PyQt6 PyQt6-WebEngine
```

### "API Connection Failed"
- Vérifier la clé API
- Si serveur local : décocher "Vérification SSL"
- Tester avec : `python main.py --debug`

### Pas de coloration syntaxique
- Internet requis pour CDN Highlight.js
- Utiliser des blocs code : \`\`\`python

### L'app ne se lance pas
```bash
# Mode debug pour voir les erreurs
python main.py --debug
```

## 📖 Aide Complète

Voir **README.md** pour la documentation complète.

## 🎯 Prochaines Étapes

- ✅ Créer plusieurs conversations
- ✅ Tester les exports JSON/Markdown
- ✅ Personnaliser les couleurs
- ✅ Explorer les raccourcis (Ctrl+N, Ctrl+E, etc.)

---

**Temps total d'installation : ~5 minutes**  
**Premier message : ~2 minutes**  
**Total : 7 minutes pour être opérationnel ! 🚀**
