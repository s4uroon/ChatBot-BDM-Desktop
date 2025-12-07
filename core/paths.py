"""
core/paths.py
=============
Gestion centralisée des chemins de fichiers utilisateur.
Les fichiers sont stockés dans le répertoire home de l'utilisateur.
"""

import os
from pathlib import Path
from typing import Optional
from .logger import get_logger


class UserPaths:
    """
    Gestion des chemins pour les fichiers de données utilisateur.

    Structure:
    - Windows: C:\\Users\\USERNAME\\.ChatBot_BDM_Desktop\\
    - Linux/Mac: ~/.ChatBot_BDM_Desktop/
    """

    # Nom du répertoire de l'application (caché avec le point initial)
    APP_DIR_NAME = ".ChatBot_BDM_Desktop"

    def __init__(self, custom_db_path: Optional[str] = None):
        """
        Initialise les chemins utilisateur.

        Args:
            custom_db_path: Chemin personnalisé pour la base de données (optionnel)
        """
        self.logger = get_logger()

        # Déterminer le répertoire home de l'utilisateur
        self.home_dir = Path.home()

        # Répertoire de l'application dans le home
        self.app_dir = self.home_dir / self.APP_DIR_NAME

        # Créer le répertoire s'il n'existe pas
        self._ensure_app_directory()

        # Chemins des fichiers
        if custom_db_path:
            # Si un chemin personnalisé est fourni, l'utiliser tel quel
            self.db_path = Path(custom_db_path)
        else:
            # Sinon, utiliser le répertoire de l'application
            self.db_path = self.app_dir / "chatbot.db"

        # Fichier de configuration
        self.settings_file = self.app_dir / "settings.ini"

        # Chemin pour les logs (optionnel)
        self.logs_dir = self.app_dir / "logs"

        # Chemin pour les exports
        self.exports_dir = self.app_dir / "exports"

        self.logger.info(f"[PATHS] Répertoire application: {self.app_dir}")
        self.logger.info(f"[PATHS] Base de données: {self.db_path}")
        self.logger.info(f"[PATHS] Fichier de configuration: {self.settings_file}")

    def _ensure_app_directory(self) -> None:
        """Crée le répertoire de l'application s'il n'existe pas."""
        try:
            self.app_dir.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"[PATHS] Répertoire vérifié/créé: {self.app_dir}")
        except Exception as e:
            self.logger.error(f"[PATHS] Erreur création répertoire: {e}", exc_info=True)
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
            Chemin absolu du répertoire de l'application
        """
        return str(self.app_dir.resolve())

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


def init_user_paths(custom_db_path: Optional[str] = None) -> UserPaths:
    """
    Initialise l'instance globale de UserPaths.

    Args:
        custom_db_path: Chemin personnalisé pour la base de données (optionnel)

    Returns:
        Instance de UserPaths
    """
    global _user_paths_instance
    _user_paths_instance = UserPaths(custom_db_path)
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
