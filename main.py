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
from core.constants import APP_NAME, APP_VERSION, APP_ORGANIZATION, APP_ID


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
        version=f'Chatbot Desktop v{APP_VERSION}'
    )

    return parser.parse_args()


def setup_application_style():
    """
    Configure le style global de l'application.
    Charge le fichier QSS externe depuis assets/style.qss.
    """
    style_path = Path(__file__).parent / 'assets' / 'style.qss'
    try:
        if style_path.exists():
            return style_path.read_text(encoding='utf-8')
        # Fallback pour mode PyInstaller
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            style_path = Path(sys._MEIPASS) / 'assets' / 'style.qss'
            if style_path.exists():
                return style_path.read_text(encoding='utf-8')
        return ""
    except Exception:
        return ""


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
    logger.info(f"Version: {APP_VERSION}")
    logger.info(f"Mode: {'PORTABLE' if portable else 'NORMAL'}")
    logger.info(f"Mode debug: {'ACTIVÉ' if args.debug else 'DÉSACTIVÉ'}")
    logger.info(f"Répertoire application: {user_paths.get_app_dir()}")
    logger.info(f"Base de données: {user_paths.get_db_path()}")
    logger.info(f"Fichier de configuration: {user_paths.get_settings_file()}")
    logger.info("="*70)
    
    # Création de l'application Qt
    app = QApplication(sys.argv)

    # Configuration de l'application
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_ORGANIZATION)
    app.setApplicationVersion(APP_VERSION)

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
            myappid = APP_ID
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
