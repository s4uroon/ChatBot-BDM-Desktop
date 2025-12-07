"""
core/paths.py
=============
Gestion centralisée des chemins de fichiers utilisateur.
Les fichiers sont stockés dans le répertoire home de l'utilisateur.
Supporte également le mode portable pour Windows.
"""

import os
import sys
from pathlib import Path
from typing import Optional
from .logger import get_logger


class UserPaths:
    """
    Gestion des chemins pour les fichiers de données utilisateur.

    Structure en mode normal:
    - Windows: C:\\Users\\USERNAME\\.ChatBot_BDM_Desktop\\
    - Linux/Mac: ~/.ChatBot_BDM_Desktop/

    Structure en mode portable:
    - chatbot.db et settings.ini: Toujours dans ~/.ChatBot_BDM_Desktop/
    - logs/ et exports/: Dans data/ à côté de l'exécutable
    """

    # Nom du répertoire de l'application (caché avec le point initial)
    APP_DIR_NAME = ".ChatBot_BDM_Desktop"

    # Nom du répertoire en mode portable
    PORTABLE_DIR_NAME = "data"

    def __init__(self, custom_db_path: Optional[str] = None, portable_mode: bool = False):
        """
        Initialise les chemins utilisateur.

        Args:
            custom_db_path: Chemin personnalisé pour la base de données (optionnel)
            portable_mode: Si True, utilise le mode portable pour les fichiers temporaires
        """
        self.logger = get_logger()
        self.portable_mode = portable_mode

        # Le répertoire utilisateur est TOUJOURS dans le home pour les données persistantes
        self.home_dir = Path.home()
        self.user_data_dir = self.home_dir / self.APP_DIR_NAME

        # Créer le répertoire utilisateur s'il n'existe pas
        self._ensure_directory(self.user_data_dir)

        # En mode portable, on utilise aussi un répertoire portable pour les fichiers temporaires
        if self.portable_mode:
            # Mode portable : utiliser le répertoire de l'exécutable pour logs et exports
            if getattr(sys, 'frozen', False):
                # Exécuté comme exécutable PyInstaller
                exe_dir = Path(sys.executable).parent
            else:
                # Exécuté comme script Python (pour les tests)
                exe_dir = Path(__file__).parent.parent

            self.portable_dir = exe_dir / self.PORTABLE_DIR_NAME
            self._ensure_directory(self.portable_dir)
            self.logger.info(f"[PATHS] MODE PORTABLE activé")
            self.logger.info(f"[PATHS] Répertoire données utilisateur: {self.user_data_dir}")
            self.logger.info(f"[PATHS] Répertoire portable (logs/exports): {self.portable_dir}")
        else:
            # Mode normal : tout dans le répertoire utilisateur
            self.portable_dir = None
            self.logger.info(f"[PATHS] Mode normal - Répertoire: {self.user_data_dir}")

        # IMPORTANT: chatbot.db et settings.ini sont TOUJOURS dans le répertoire utilisateur
        # même en mode portable
        if custom_db_path:
            # Si un chemin personnalisé est fourni, l'utiliser tel quel
            self.db_path = Path(custom_db_path)
        else:
            # TOUJOURS dans le répertoire utilisateur
            self.db_path = self.user_data_dir / "chatbot.db"

        # TOUJOURS dans le répertoire utilisateur
        self.settings_file = self.user_data_dir / "settings.ini"

        # logs et exports: dans le répertoire portable si activé, sinon dans le répertoire utilisateur
        if self.portable_mode and self.portable_dir:
            self.logs_dir = self.portable_dir / "logs"
            self.exports_dir = self.portable_dir / "exports"
        else:
            self.logs_dir = self.user_data_dir / "logs"
            self.exports_dir = self.user_data_dir / "exports"

        self.logger.info(f"[PATHS] Base de données: {self.db_path}")
        self.logger.info(f"[PATHS] Fichier de configuration: {self.settings_file}")
        self.logger.info(f"[PATHS] Répertoire logs: {self.logs_dir}")
        self.logger.info(f"[PATHS] Répertoire exports: {self.exports_dir}")

    def _ensure_directory(self, directory: Path) -> None:
        """Crée un répertoire s'il n'existe pas."""
        try:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"[PATHS] Répertoire vérifié/créé: {directory}")
        except Exception as e:
            self.logger.error(f"[PATHS] Erreur création répertoire {directory}: {e}", exc_info=True)
            raise

    def ensure_logs_directory(self) -> Path:
        """
        Crée le répertoire de logs s'il n'existe pas.

        Returns:
            Chemin du répertoire de logs
        """
        try:
            self.logs_dir.mkdir(parents=True, exist_ok=True)
            return self.logs_dir
        except Exception as e:
            self.logger.error(f"[PATHS] Erreur création répertoire logs: {e}")
            raise

    def ensure_exports_directory(self) -> Path:
        """
        Crée le répertoire d'exports s'il n'existe pas.

        Returns:
            Chemin du répertoire d'exports
        """
        try:
            self.exports_dir.mkdir(parents=True, exist_ok=True)
            return self.exports_dir
        except Exception as e:
            self.logger.error(f"[PATHS] Erreur création répertoire exports: {e}")
            raise

    def get_db_path(self) -> str:
        """
        Retourne le chemin de la base de données sous forme de string.

        Returns:
            Chemin absolu de la base de données
        """
        return str(self.db_path.resolve())

    def get_settings_file(self) -> str:
        """
        Retourne le chemin du fichier de configuration sous forme de string.

        Returns:
            Chemin absolu du fichier de configuration
        """
        return str(self.settings_file.resolve())

    def get_app_dir(self) -> str:
        """
        Retourne le répertoire de l'application sous forme de string.

        Returns:
            Chemin absolu du répertoire de l'application (répertoire utilisateur)
        """
        return str(self.user_data_dir.resolve())

    def get_exports_dir(self) -> str:
        """
        Retourne le répertoire d'exports sous forme de string.

        Returns:
            Chemin absolu du répertoire d'exports
        """
        self.ensure_exports_directory()
        return str(self.exports_dir.resolve())

    def get_logs_dir(self) -> str:
        """
        Retourne le répertoire de logs sous forme de string.

        Returns:
            Chemin absolu du répertoire de logs
        """
        self.ensure_logs_directory()
        return str(self.logs_dir.resolve())


# Instance globale (sera initialisée dans main.py)
_user_paths_instance: Optional[UserPaths] = None


def init_user_paths(custom_db_path: Optional[str] = None, portable_mode: bool = False) -> UserPaths:
    """
    Initialise l'instance globale de UserPaths.

    Args:
        custom_db_path: Chemin personnalisé pour la base de données (optionnel)
        portable_mode: Si True, utilise le mode portable (données à côté de l'exe)

    Returns:
        Instance de UserPaths
    """
    global _user_paths_instance
    _user_paths_instance = UserPaths(custom_db_path, portable_mode)
    return _user_paths_instance


def get_user_paths() -> UserPaths:
    """
    Retourne l'instance globale de UserPaths.

    Returns:
        Instance de UserPaths

    Raises:
        RuntimeError: Si UserPaths n'a pas été initialisé
    """
    if _user_paths_instance is None:
        raise RuntimeError(
            "UserPaths n'a pas été initialisé. "
            "Appelez init_user_paths() dans main.py avant d'utiliser get_user_paths()."
        )
    return _user_paths_instance
