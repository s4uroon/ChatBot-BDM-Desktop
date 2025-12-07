"""
Créer ces fichiers __init__.py dans chaque dossier de package:
=====================================================================

1. core/__init__.py
-------------------
"""
from .logger import LoggerSetup, get_logger
from .database import DatabaseManager
from .api_client import APIClient
from .settings_manager import SettingsManager
from .export_manager import ExportManager
from .main_controller import MainController

__all__ = [
    'LoggerSetup',
    'get_logger',
    'DatabaseManager',
    'APIClient',
    'SettingsManager',
    'ExportManager',
    'MainController'
]
"""

2. ui/__init__.py
-----------------
"""
from .main_window import MainWindow
from .sidebar_widget import SidebarWidget
from .chat_widget import ChatWidget
from .input_widget import InputWidget
from .settings_dialog import SettingsDialog

__all__ = [
    'MainWindow',
    'SidebarWidget',
    'ChatWidget',
    'InputWidget',
    'SettingsDialog'
]
"""

3. workers/__init__.py
----------------------
"""
from .api_worker import APIWorker

__all__ = ['APIWorker']
"""

4. utils/__init__.py
--------------------
"""
from .html_generator import HTMLGenerator
from .code_parser import CodeParser
from .css_generator import CSSGenerator

__all__ = [
    'HTMLGenerator',
    'CodeParser',
    'CSSGenerator'
]
"""
