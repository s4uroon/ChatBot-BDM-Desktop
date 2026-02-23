# ChatBot BDM Desktop

Application de bureau professionnelle pour interagir avec des API OpenAI compatibles — interface graphique moderne PyQt6, streaming en temps réel, rendu Markdown complet et coloration syntaxique locale.

## Fonctionnalités

### Cœur de l'Application
- **Streaming en temps réel** — Réponses progressives via QThread (sans blocage UI)
- **SSL Bypass** — Support des certificats auto-signés (serveurs entreprise)
- **Multi-conversations** — Gestion illimitée avec historique SQLite local
- **Export JSON/Markdown** — Export sélectif ou complet des conversations
- **Auto-titrage** — Génération automatique du titre de conversation par l'API

### Interface Utilisateur
- **Rendu Markdown complet** — Headers, tableaux, listes, blockquotes, code, règles, task-lists
- **Coloration syntaxique locale** — 17 langages via Highlight.js bundlé (aucune connexion internet requise)
- **Thème clair/sombre** — Bascule entre atom-one-dark et atom-one-light
- **Sidebar avec sélection multiple** — Shift+Clic, Shift+Flèches, suppression groupée
- **Avatars personnalisables** — Placez `user.png` et `assistant.png` dans `assets/avatars/`
- **Panneau redimensionnable** — Splitter entre la zone de chat et la saisie
- **Compteur de tokens** — Estimation en temps réel de l'usage API

### Technique
- **Architecture MVC** — Séparation claire UI / Business / Data
- **Signaux/Slots PyQt6** — Communication asynchrone propre entre threads
- **Gestion d'erreurs robuste** — Messages utilisateur contextuels avec suggestions
- **Logging avancé** — Mode DEBUG activable via `--debug`
- **Mode portable** — Données à côté de l'exe ou dans le profil utilisateur

## Prérequis

- **Python 3.9+**
- **Système d'exploitation** : Windows / macOS / Linux

## Installation

### 1. Cloner le projet

```bash
git clone <repo_url>
cd ChatBot-BDM-Desktop
```

### 2. Créer un environnement virtuel (recommandé)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

## Lancement

```bash
# Mode normal
python main.py

# Mode debug (logs détaillés dans la console)
python main.py --debug

# Base de données personnalisée
python main.py --db /chemin/vers/custom.db

# Forcer le mode portable
python main.py --portable

# Afficher l'aide
python main.py --help
```

## Configuration

### Premier Lancement

1. Menu `Paramètres` → `Configuration...` (ou `Ctrl+,`)
2. **Onglet Connexion** :
   - Clé API
   - URL de base (défaut : `https://api.openai.com/v1`)
   - Modèle (ex : `gpt-4`, `gpt-4o-mini`)
   - Décocher "Vérification SSL" si serveur auto-signé
3. Tester avec le bouton `Tester la connexion`
4. **Onglet Apparence Code** : personnaliser les couleurs de syntaxe

### Serveurs avec certificats auto-signés

Décocher `Activer la vérification SSL` dans les paramètres → utilise `httpx.Client(verify=False)`.

> Avertissement : N'utiliser cette option que pour des serveurs de confiance.

## Raccourcis Clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl+N` | Nouvelle conversation |
| `Ctrl+E` | Exporter |
| `Ctrl+,` | Paramètres |
| `Ctrl+Q` | Quitter |
| `Entrée` | Envoyer message |
| `Shift+Entrée` | Nouvelle ligne |
| `Suppr` | Supprimer sélection |

## Langages de Coloration Syntaxique

Python, JavaScript, Bash/Shell, PowerShell, Java, JSON, HTML/XML, PHP, Perl, SQL, C, C++, C#, Ruby, Go, Rust (17 langages, bundlés localement — aucune connexion internet requise)

## Structure du Projet

```
ChatBot-BDM-Desktop/
│
├── main.py                          # Point d'entrée
├── requirements.txt                 # Dépendances runtime (Python 3.9+)
├── ChatBot_BDM_Desktop.spec         # Configuration PyInstaller
├── README.md
├── CHANGELOG.md
│
├── core/                            # Logique métier
│   ├── api_client.py                # Client OpenAI (SSL bypass)
│   ├── constants.py                 # Constantes globales
│   ├── conversation_manager.py      # Gestion des conversations
│   ├── database.py                  # Gestionnaire SQLite
│   ├── export_manager.py            # Export JSON/Markdown
│   ├── init_files.py                # Initialisation
│   ├── logger.py                    # Système de logging
│   ├── main_controller.py           # Contrôleur principal
│   ├── paths.py                     # Gestion des chemins (portable/normal)
│   ├── settings_manager.py          # QSettings wrapper
│   └── tag_manager.py               # Gestion des tags
│
├── ui/                              # Interface utilisateur
│   ├── chat_widget.py               # Zone de chat (QWebEngineView)
│   ├── export_dialog.py             # Dialogue d'export
│   ├── input_widget.py              # Zone de saisie
│   ├── main_window.py               # Fenêtre principale
│   ├── settings_dialog.py           # Dialogue paramètres
│   └── sidebar_widget.py            # Historique des conversations
│
├── workers/                         # Threads asynchrones
│   ├── api_worker.py                # Streaming API (QThread)
│   └── title_worker.py              # Auto-titrage (QThread)
│
├── utils/                           # Utilitaires
│   ├── code_parser.py               # Détection blocs de code
│   ├── css_generator.py             # CSS personnalisé
│   ├── html_generator.py            # Génération HTML + Markdown
│   └── logo_utils.py                # Encodage base64 images
│
├── assets/                          # Ressources statiques
│   ├── ChatBot_BDM_Desktop.ico      # Icône Windows
│   ├── ChatBot_BDM_Desktop.png      # Logo
│   ├── style.qss                    # Thème Qt (dark)
│   ├── avatars/                     # Avatars personnalisables
│   │   ├── user.png
│   │   └── assistant.png
│   └── highlightjs/                 # Highlight.js bundlé localement
│       ├── highlight.min.js
│       ├── languages/               # 17 langages
│       └── styles/                  # Thèmes clair/sombre
│
├── build_scripts/                   # Scripts et config de build
│   ├── build_portable.bat           # Build Windows (Batch)
│   ├── build_portable.ps1           # Build Windows (PowerShell)
│   └── requirements-build.txt       # Dépendances de compilation
│
└── docs/                            # Documentation secondaire
    ├── BUILD.md                     # Guide de build détaillé
    ├── BUILD_PORTABLE.md            # Guide build version portable
    ├── QUICKSTART_PORTABLE.md       # Guide rapide
    ├── CUSTOMISATION_AVATARS.md     # Personnalisation avatars
    ├── DEBUG_AVATARS.md             # Dépannage avatars
    ├── USER_GUIDE_PORTABLE.txt      # Guide utilisateur (exe portable)
    └── contributing.md              # Guide de contribution
```

## Build Windows (Exécutable Portable)

```bash
# Installer les dépendances de build
pip install -r build_scripts/requirements-build.txt

# Compiler (Windows — double-clic ou ligne de commande)
build_scripts\build_portable.bat

# Ou via PowerShell
PowerShell -ExecutionPolicy Bypass -File build_scripts\build_portable.ps1

# Ou manuellement (depuis la racine du projet)
pyinstaller ChatBot_BDM_Desktop.spec
```

Le résultat se trouve dans `dist/ChatBot BDM Desktop/`.

Pour plus de détails : `docs/BUILD.md` et `docs/BUILD_PORTABLE.md`

## Stockage des Données

| Fichier | Mode normal | Mode portable |
|---------|-------------|---------------|
| Base de données | `~/.ChatBot_BDM_Desktop/chatbot.db` | `~/.ChatBot_BDM_Desktop/chatbot.db` |
| Paramètres | `~/.ChatBot_BDM_Desktop/settings.ini` | `~/.ChatBot_BDM_Desktop/settings.ini` |
| Logs | `~/.ChatBot_BDM_Desktop/logs/` | `{exe_dir}/data/logs/` |
| Exports | `~/.ChatBot_BDM_Desktop/exports/` | `{exe_dir}/data/exports/` |

En mode portable, la base de données et les paramètres restent dans le profil utilisateur pour garantir leur persistance même si le dossier de l'exe est déplacé.

## Dépannage

### L'application ne démarre pas

```bash
pip install --upgrade -r requirements.txt
python main.py --debug
```

### Erreur de connexion API

1. Vérifier la clé API dans les paramètres
2. Tester l'URL avec curl : `curl -I https://api.openai.com/v1`
3. Si certificat auto-signé : décocher `Vérification SSL`

### Avatars absents

Vérifier que `assets/avatars/user.png` et `assets/avatars/assistant.png` existent.
Voir `docs/CUSTOMISATION_AVATARS.md` pour les spécifications.

## Sécurité

- Les clés API sont stockées dans `QSettings` (registre Windows / fichiers config Linux/macOS)
- **SSL Bypass** : à utiliser uniquement pour des serveurs de confiance internes
- Les conversations sont stockées en clair dans SQLite local

## Licence

À définir selon vos besoins.

---

**Version** : 2.2.0 | **Framework** : PyQt6 | **Compatibilité API** : OpenAI Compatible
