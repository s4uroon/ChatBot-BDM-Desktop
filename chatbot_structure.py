"""
STRUCTURE DU PROJET CHATBOT DESKTOP
====================================

chatbot_desktop/
│
├── main.py                          # Point d'entrée principal
├── requirements.txt                 # Dépendances Python
├── config.ini                       # Configuration (généré auto)
│
├── core/
│   ├── __init__.py
│   ├── logger.py                    # Configuration logging
│   ├── database.py                  # Gestion SQLite
│   ├── api_client.py                # Client OpenAI avec SSL bypass
│   ├── settings_manager.py          # Gestion QSettings
│   └── export_manager.py            # Export JSON/Markdown
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py               # Fenêtre principale
│   ├── sidebar_widget.py            # Historique conversations
│   ├── chat_widget.py               # Zone de chat (QWebEngineView)
│   ├── input_widget.py              # Zone de saisie
│   ├── settings_dialog.py           # Dialogue paramètres
│   └── export_dialog.py             # Dialogue export
│
├── workers/
│   ├── __init__.py
│   └── api_worker.py                # Thread pour streaming API
│
├── utils/
│   ├── __init__.py
│   ├── html_generator.py            # Génération HTML dynamique
│   ├── code_parser.py               # Détection blocs de code
│   └── css_generator.py             # CSS personnalisé
│
└── resources/
    ├── styles.qss                   # Styles Qt
    └── templates/
        └── chat_template.html       # Template HTML de base

"""
