# Changelog - Chatbot Desktop

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [1.0.0] - 2024-11-29

### 🎉 Version Initiale

#### Ajouté
- ✅ Interface graphique PyQt6 complète avec sidebar et zone de chat
- ✅ Streaming en temps réel des réponses API
- ✅ Support SSL bypass pour certificats auto-signés (serveurs entreprise)
- ✅ Base de données SQLite pour persistance des conversations
- ✅ Sélection multiple de conversations avec Shift+Clic
- ✅ Export JSON et Markdown (sélectif ou complet)
- ✅ Coloration syntaxique avec Highlight.js (10+ langages)
- ✅ Boutons "Copier" automatiques sur les blocs de code
- ✅ Scroll intelligent vers la dernière question posée
- ✅ Personnalisation des couleurs de code (5 catégories)
- ✅ Prévisualisation en temps réel des couleurs
- ✅ Mode DEBUG avec logging détaillé en console
- ✅ Arguments CLI (--debug, --db)
- ✅ QSettings pour persistance des paramètres
- ✅ Architecture MVC propre et modulaire
- ✅ Gestion d'erreurs robuste avec try/catch
- ✅ Worker threads pour éviter le blocage UI
- ✅ Signaux/Slots PyQt6 pour communication asynchrone
- ✅ Raccourcis clavier (Ctrl+N, Ctrl+E, Ctrl+Q, etc.)
- ✅ Barre de statut avec feedback utilisateur
- ✅ Support Entrée = Envoyer / Shift+Entrée = Nouvelle ligne
- ✅ Compteur de caractères avec limite configurable
- ✅ Test de connexion API intégré
- ✅ Dialogue de paramètres avec onglets
- ✅ Documentation complète (README, QUICKSTART)
- ✅ Scripts d'installation et de lancement (Windows/Linux)

#### Langages Supportés
- Python
- JavaScript / TypeScript  
- Bash / Shell
- PowerShell
- Java
- JSON
- HTML / CSS
- PHP
- Perl
- SQL
- C / C++ / C#
- Ruby
- Go
- Rust

#### Logging Catégories
- [CONFIG] - État de la configuration
- [API] - Requêtes et chunks streaming
- [PARSER] - Détection des blocs de code
- [DATABASE] - Opérations SQLite
- [EXPORT] - Exports fichiers
- [ERREUR] - Stack traces complètes

#### Architecture Technique
- **Frontend**: PyQt6, QWebEngineView, Highlight.js
- **Backend**: SQLite, OpenAI API, httpx
- **Async**: QThread workers, Signaux/Slots
- **Persistance**: QSettings cross-platform
- **Logging**: Module logging standard Python

### 🔒 Sécurité
- SSL bypass optionnel pour environnements entreprise
- Clés API stockées dans QSettings sécurisé
- Conversations en local uniquement (SQLite)

### 📦 Dépendances
- PyQt6 >= 6.6.1
- PyQt6-WebEngine >= 6.6.0
- openai >= 1.12.0
- httpx >= 0.26.0

### 🎯 Fonctionnalités Futures Prévues
- [ ] Support d'images (vision models)
- [ ] Support de PDFs et documents
- [ ] Mode collaboratif multi-utilisateurs
- [ ] Plugins et extensions
- [ ] Thèmes visuels (dark mode)
- [ ] Recherche full-text dans conversations
- [ ] Assistant vocal (STT/TTS)
- [ ] Mode hors-ligne avec modèles locaux
- [ ] Synchronisation cloud optionnelle
- [ ] Chiffrement des conversations sensibles

---

## Format du Changelog

### Types de Changements
- **Ajouté** : Nouvelles fonctionnalités
- **Modifié** : Changements dans les fonctionnalités existantes
- **Déprécié** : Fonctionnalités bientôt supprimées
- **Supprimé** : Fonctionnalités retirées
- **Corrigé** : Corrections de bugs
- **Sécurité** : Corrections de vulnérabilités

### Format des Versions
- **MAJOR.MINOR.PATCH** (ex: 1.2.3)
  - MAJOR : Changements incompatibles
  - MINOR : Nouvelles fonctionnalités compatibles
  - PATCH : Corrections de bugs compatibles
