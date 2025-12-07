# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File pour ChatBot BDM Desktop - Version Portable Windows
==========================================================================

Ce fichier configure la compilation de l'application en un exécutable Windows portable.

Pour compiler :
    pyinstaller ChatBot_BDM_Desktop.spec

Le résultat sera dans le dossier dist/ChatBot BDM Desktop/
"""

import sys
from pathlib import Path

block_cipher = None

# Répertoire de base du projet
project_dir = Path(__file__).parent

# Analyse des dépendances
a = Analysis(
    ['main.py'],
    pathex=[str(project_dir)],
    binaries=[],
    datas=[
        # Pas de fichiers de données à inclure pour le moment
        # Si vous avez des icônes, images, etc., ajoutez-les ici
        # Exemple: ('assets', 'assets'),
    ],
    hiddenimports=[
        # PyQt6 imports cachés
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtWebEngineCore',
        # Modules de l'application
        'core',
        'core.api_client',
        'core.database',
        'core.export_manager',
        'core.init_files',
        'core.logger',
        'core.main_controller',
        'core.paths',
        'core.settings_manager',
        'ui',
        'ui.chat_widget',
        'ui.export_dialog',
        'ui.input_widget',
        'ui.main_window',
        'ui.settings_dialog',
        'ui.sidebar_widget',
        'utils',
        'utils.code_parser',
        'utils.css_generator',
        'utils.html_generator',
        'workers',
        'workers.api_worker',
        # Autres dépendances
        'openai',
        'httpx',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclure les modules non nécessaires pour réduire la taille
        'matplotlib',
        'scipy',
        'numpy',
        'pandas',
        'PIL',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ChatBot BDM Desktop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # False = Application Windows (pas de console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Icône de l'application (à créer si nécessaire)
    # icon='assets/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ChatBot BDM Desktop',
)
