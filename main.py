"""
main.py
=======
Point d'entrée principal de l'application Chatbot Desktop
"""

import sys
import argparse
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow
from core.logger import LoggerSetup
from core.paths import init_user_paths, get_icon_path


def is_portable_mode() -> bool:
    """
    Détecte si l'application doit s'exécuter en mode portable.

    Le mode portable est activé si :
    1. L'application est exécutée comme un exécutable PyInstaller (frozen)
    2. OU un fichier marqueur 'portable.txt' existe dans le répertoire de l'exe/script

    Returns:
        True si le mode portable doit être activé, False sinon
    """
    # Déterminer le répertoire de l'exécutable ou du script
    if getattr(sys, 'frozen', False):
        # Exécuté comme exécutable PyInstaller
        app_dir = Path(sys.executable).parent
        # En mode frozen, activer automatiquement le mode portable
        return True
    else:
        # Exécuté comme script Python
        app_dir = Path(__file__).parent
        # Vérifier la présence du fichier marqueur
        portable_marker = app_dir / 'portable.txt'
        return portable_marker.exists()


def parse_arguments():
    """
    Parse les arguments de ligne de commande.

    Returns:
        Namespace avec les arguments
    """
    parser = argparse.ArgumentParser(
        description='Chatbot Desktop - Assistant virtuel professionnel',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python main.py                    # Lancement normal
  python main.py --debug            # Mode debug avec logs console
  python main.py --db custom.db     # Base de données personnalisée
  python main.py --portable         # Force le mode portable
        """
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Active le mode debug avec logs détaillés dans la console'
    )

    parser.add_argument(
        '--db',
        type=str,
        default=None,
        metavar='PATH',
        help='Chemin vers le fichier de base de données (défaut: ~/.ChatBot_BDM_Desktop/chatbot.db)'
    )

    parser.add_argument(
        '--portable',
        action='store_true',
        help='Force le mode portable (données stockées à côté de l\'exécutable)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='Chatbot Desktop v1.0.0'
    )

    return parser.parse_args()


def setup_application_style():
    """Configure le style global de l'application - MODE SOMBRE."""
    # Style Qt moderne - Thème Sombre
    style = """
    /* === FENÊTRE PRINCIPALE === */
    QMainWindow {
        background-color: #1e1e1e;
    }
    
    QWidget {
        background-color: #1e1e1e;
        color: #e0e0e0;
    }
    
    /* === MENUS === */
    QMenuBar {
        background-color: #2d2d2d;
        border-bottom: 1px solid #3d3d3d;
        padding: 4px;
        color: #e0e0e0;
    }
    
    QMenuBar::item {
        padding: 6px 12px;
        background: transparent;
        color: #e0e0e0;
    }
    
    QMenuBar::item:selected {
        background-color: #3d3d3d;
        color: #ffffff;
    }
    
    QMenu {
        background-color: #2d2d2d;
        border: 1px solid #3d3d3d;
        color: #e0e0e0;
    }
    
    QMenu::item {
        padding: 8px 25px;
        color: #e0e0e0;
    }
    
    QMenu::item:selected {
        background-color: #3d3d3d;
        color: #ffffff;
    }
    
    /* === BARRE DE STATUT === */
    QStatusBar {
        background-color: #2d2d2d;
        border-top: 1px solid #3d3d3d;
        font-size: 12px;
        color: #b0b0b0;
    }
    
    /* === SPLITTER === */
    QSplitter::handle {
        background-color: #3d3d3d;
        width: 2px;
    }
    
    QSplitter::handle:hover {
        background-color: #4d4d4d;
    }
    
    /* === GROUPBOX === */
    QGroupBox {
        border: 1px solid #3d3d3d;
        border-radius: 4px;
        margin-top: 10px;
        padding-top: 10px;
        font-weight: bold;
        color: #e0e0e0;
        background-color: #252525;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
        color: #4CAF50;
    }
    
    /* === SCROLLBAR === */
    QScrollBar:vertical {
        border: none;
        background: #2d2d2d;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background: #4d4d4d;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: #5d5d5d;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QScrollBar:horizontal {
        border: none;
        background: #2d2d2d;
        height: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:horizontal {
        background: #4d4d4d;
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background: #5d5d5d;
    }
    
    /* === LABELS === */
    QLabel {
        color: #e0e0e0;
        background-color: transparent;
    }
    
    /* === INPUTS === */
    QLineEdit, QTextEdit {
        background-color: #2d2d2d;
        border: 1px solid #3d3d3d;
        border-radius: 4px;
        padding: 6px;
        color: #e0e0e0;
        selection-background-color: #4CAF50;
        selection-color: #ffffff;
    }
    
    QLineEdit:focus, QTextEdit:focus {
        border: 1px solid #4CAF50;
    }
    
    QLineEdit:disabled, QTextEdit:disabled {
        background-color: #252525;
        color: #707070;
    }
    
    /* === BOUTONS === */
    QPushButton {
        background-color: #3d3d3d;
        color: #e0e0e0;
        border: 1px solid #4d4d4d;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: normal;
    }
    
    QPushButton:hover {
        background-color: #4d4d4d;
        border: 1px solid #5d5d5d;
    }
    
    QPushButton:pressed {
        background-color: #2d2d2d;
    }
    
    QPushButton:disabled {
        background-color: #252525;
        color: #606060;
        border: 1px solid #353535;
    }
    
    /* === CHECKBOX === */
    QCheckBox {
        color: #e0e0e0;
        spacing: 8px;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 1px solid #4d4d4d;
        border-radius: 3px;
        background-color: #2d2d2d;
    }
    
    QCheckBox::indicator:checked {
        background-color: #4CAF50;
        border: 1px solid #4CAF50;
    }
    
    QCheckBox::indicator:hover {
        border: 1px solid #5d5d5d;
    }
    
    /* === TABS === */
    QTabWidget::pane {
        border: 1px solid #3d3d3d;
        background-color: #252525;
    }
    
    QTabBar::tab {
        background-color: #2d2d2d;
        color: #b0b0b0;
        padding: 8px 20px;
        border: 1px solid #3d3d3d;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: #252525;
        color: #4CAF50;
        border-bottom: 2px solid #4CAF50;
    }
    
    QTabBar::tab:hover {
        background-color: #3d3d3d;
    }
    
    /* === DIALOG === */
    QDialog {
        background-color: #1e1e1e;
    }
    
    /* === MESSAGEBOX === */
    QMessageBox {
        background-color: #1e1e1e;
    }
    
    QMessageBox QLabel {
        color: #e0e0e0;
    }
    """
    
    return style


def main():
    """
    Fonction principale de l'application.
    """
    # Parse des arguments
    args = parse_arguments()

    # Déterminer si on est en mode portable
    portable = args.portable or is_portable_mode()

    # Configuration du logger
    logger_setup = LoggerSetup()
    logger_setup.setup_console_logging(debug=args.debug)

    logger = logger_setup.get_logger()

    # Initialisation des chemins utilisateur
    user_paths = init_user_paths(custom_db_path=args.db, portable_mode=portable)

    # Log du démarrage
    logger.info("="*70)
    logger.info("CHATBOT DESKTOP - DÉMARRAGE")
    logger.info("="*70)
    logger.info(f"Version: 1.0.0")
    logger.info(f"Mode: {'PORTABLE' if portable else 'NORMAL'}")
    logger.info(f"Mode debug: {'ACTIVÉ' if args.debug else 'DÉSACTIVÉ'}")
    logger.info(f"Répertoire application: {user_paths.get_app_dir()}")
    logger.info(f"Base de données: {user_paths.get_db_path()}")
    logger.info(f"Fichier de configuration: {user_paths.get_settings_file()}")
    logger.info("="*70)
    
    # Création de l'application Qt
    app = QApplication(sys.argv)

    # Configuration de l'application
    app.setApplicationName("ChatBot BDM Desktop")
    app.setOrganizationName("ChatbotBDM")
    app.setApplicationVersion("1.0.0")

    # Configuration de l'icône de l'application
    try:
        icon_path = get_icon_path()
        if Path(icon_path).exists():
            app.setWindowIcon(QIcon(icon_path))
            logger.debug(f"Icône de l'application chargée: {icon_path}")
        else:
            logger.warning(f"Fichier d'icône introuvable: {icon_path}")
    except Exception as e:
        logger.warning(f"Impossible de charger l'icône: {e}")

    # Configuration Windows pour l'icône de la barre des tâches
    # Nécessaire pour que Windows affiche correctement l'icône dans la barre des tâches
    if sys.platform == 'win32':
        try:
            import ctypes
            # Définir l'AppUserModelID pour Windows 7+
            # Cela permet à Windows de regrouper correctement l'application dans la barre des tâches
            myappid = 'ChatbotBDM.ChatBotBDMDesktop.1.0.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            logger.debug(f"AppUserModelID Windows configuré: {myappid}")
        except Exception as e:
            logger.warning(f"Impossible de configurer l'AppUserModelID Windows: {e}")
    
    # Style global
    app.setStyleSheet(setup_application_style())
    
    # Attributs Qt pour de meilleures performances (Qt6 compatible)
    # AA_UseHighDpiPixmaps est déprécié dans Qt6 (activé par défaut)
    # On garde seulement les attributs compatibles Qt6
    try:
        app.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
    except AttributeError:
        pass  # Ignorer si l'attribut n'existe pas
    
    try:
        # Création de la fenêtre principale
        logger.debug("Création de la fenêtre principale...")
        window = MainWindow(
            db_path=user_paths.get_db_path(),
            settings_file=user_paths.get_settings_file()
        )

        # Affichage - Approche compatible Windows
        # Sur Windows, il faut d'abord show() puis setWindowState()
        window.show()
        window.setWindowState(Qt.WindowState.WindowMaximized)
        logger.info("✅ Application démarrée avec succès")
        
        # Boucle d'événements
        exit_code = app.exec()
        
        logger.info(f"Application fermée avec le code: {exit_code}")
        sys.exit(exit_code)
    
    except Exception as e:
        logger.error("ERREUR FATALE lors du démarrage", exc_info=True)
        
        # Affichage d'une erreur à l'utilisateur
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(
            None,
            "Erreur Fatale",
            f"Impossible de démarrer l'application:\n\n{str(e)}\n\n"
            "Consultez les logs pour plus de détails."
        )
        
        sys.exit(1)


if __name__ == '__main__':
    main()
