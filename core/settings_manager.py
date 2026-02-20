"""
core/settings_manager.py
========================
Gestionnaire de paramètres avec QSettings (persistance)
"""

from PyQt6.QtCore import QSettings
from typing import Optional
from pathlib import Path
from .logger import get_logger


class SettingsManager:
    """
    Gestionnaire centralisé des paramètres de l'application.
    Utilise QSettings pour la persistance cross-platform.
    """

    # Valeurs par défaut
    DEFAULTS = {
        # API Settings
        'api/key': '',
        'api/base_url': 'https://api.openai.com/v1',
        'api/model': 'gpt-4',
        'api/verify_ssl': False,
        'api/temperature': 0.7,
        'api/max_tokens': None,
        
        # Appearance - Code Colors
        'appearance/color_comment': '#6a9955',
        'appearance/color_keyword': '#569cd6',
        'appearance/color_string': '#ce9178',
        'appearance/color_number': '#b5cea8',
        'appearance/color_function': '#dcdcaa',
        'appearance/hljs_theme': 'dark',  # Thème Highlight.js: 'light' ou 'dark'

        # UI Settings
        'ui/window_width': 1200,
        'ui/window_height': 800,
        'ui/sidebar_width': 280,
        'ui/theme': 'light',
        'ui/chat_splitter_top': 0,       # Taille du panneau chat (0 = défaut automatique)
        'ui/chat_splitter_bottom': 0,    # Taille du panneau input (0 = défaut automatique)
        'ui/sidebar_splitter_left': 0,   # Taille sidebar (0 = défaut automatique)
        'ui/sidebar_splitter_right': 0,  # Taille zone centrale (0 = défaut automatique)
        
        # Behavior
        'behavior/auto_scroll': True,
        'behavior/confirm_delete': True,
        'behavior/max_displayed_messages': 100,  # Limite pour éviter les ralentissements

        # Draft (brouillon du champ de saisie)
        'draft/content': '',  # Texte du brouillon sauvegardé
    }
    
    def __init__(self, settings_file: Optional[str] = None):
        """
        Initialise QSettings.

        Args:
            settings_file: Chemin du fichier de configuration (optionnel).
                          Si None, utilise l'emplacement par défaut de QSettings.
        """
        self.logger = get_logger()

        if settings_file:
            # Utiliser un fichier .ini spécifique
            self.settings = QSettings(settings_file, QSettings.Format.IniFormat)
            self.logger.debug(f"[SETTINGS] Initialisé avec fichier: {settings_file}")
        else:
            # Utiliser l'emplacement par défaut de QSettings
            self.settings = QSettings('ChatbotDesktop', 'ChatbotApp')
            self.logger.debug("[SETTINGS] Initialisé avec emplacement par défaut")
    
    # === API SETTINGS ===
    
    def get_api_key(self) -> str:
        """Retourne la clé API."""
        return self._get('api/key', str)
    
    def set_api_key(self, key: str):
        """Définit la clé API."""
        self._set('api/key', key)
    
    def get_base_url(self) -> str:
        """Retourne l'URL de base de l'API."""
        return self._get('api/base_url', str)
    
    def set_base_url(self, url: str):
        """Définit l'URL de base de l'API."""
        self._set('api/base_url', url)
    
    def get_model(self) -> str:
        """Retourne le modèle sélectionné."""
        return self._get('api/model', str)
    
    def set_model(self, model: str):
        """Définit le modèle."""
        self._set('api/model', model)
    
    def get_verify_ssl(self) -> bool:
        """Retourne l'état de la vérification SSL."""
        return self._get('api/verify_ssl', bool)
    
    def set_verify_ssl(self, verify: bool):
        """Définit l'état de la vérification SSL."""
        self._set('api/verify_ssl', verify)
    
    def get_temperature(self) -> float:
        """Retourne la température du modèle."""
        return self._get('api/temperature', float)
    
    def set_temperature(self, temp: float):
        """Définit la température."""
        self._set('api/temperature', temp)
    
    def get_max_tokens(self) -> Optional[int]:
        """Retourne la limite de tokens (None si pas de limite)."""
        value = self._get('api/max_tokens', int)
        return value if value else None
    
    def set_max_tokens(self, tokens: Optional[int]):
        """Définit la limite de tokens."""
        self._set('api/max_tokens', tokens if tokens else None)
    
    # === APPEARANCE SETTINGS ===
    
    def get_color_comment(self) -> str:
        """Retourne la couleur des commentaires."""
        return self._get('appearance/color_comment', str)
    
    def set_color_comment(self, color: str):
        """Définit la couleur des commentaires."""
        self._set('appearance/color_comment', color)
    
    def get_color_keyword(self) -> str:
        """Retourne la couleur des mots-clés."""
        return self._get('appearance/color_keyword', str)
    
    def set_color_keyword(self, color: str):
        """Définit la couleur des mots-clés."""
        self._set('appearance/color_keyword', color)
    
    def get_color_string(self) -> str:
        """Retourne la couleur des chaînes de caractères."""
        return self._get('appearance/color_string', str)
    
    def set_color_string(self, color: str):
        """Définit la couleur des chaînes."""
        self._set('appearance/color_string', color)
    
    def get_color_number(self) -> str:
        """Retourne la couleur des nombres."""
        return self._get('appearance/color_number', str)
    
    def set_color_number(self, color: str):
        """Définit la couleur des nombres."""
        self._set('appearance/color_number', color)
    
    def get_color_function(self) -> str:
        """Retourne la couleur des fonctions."""
        return self._get('appearance/color_function', str)
    
    def set_color_function(self, color: str):
        """Définit la couleur des fonctions."""
        self._set('appearance/color_function', color)
    
    def get_all_colors(self) -> dict:
        """Retourne toutes les couleurs de code."""
        return {
            'comment': self.get_color_comment(),
            'keyword': self.get_color_keyword(),
            'string': self.get_color_string(),
            'number': self.get_color_number(),
            'function': self.get_color_function(),
        }
    
    def set_all_colors(self, colors: dict):
        """Définit toutes les couleurs de code."""
        if 'comment' in colors:
            self.set_color_comment(colors['comment'])
        if 'keyword' in colors:
            self.set_color_keyword(colors['keyword'])
        if 'string' in colors:
            self.set_color_string(colors['string'])
        if 'number' in colors:
            self.set_color_number(colors['number'])
        if 'function' in colors:
            self.set_color_function(colors['function'])
    
    def reset_colors_to_default(self):
        """Réinitialise les couleurs aux valeurs par défaut."""
        self.set_color_comment(self.DEFAULTS['appearance/color_comment'])
        self.set_color_keyword(self.DEFAULTS['appearance/color_keyword'])
        self.set_color_string(self.DEFAULTS['appearance/color_string'])
        self.set_color_number(self.DEFAULTS['appearance/color_number'])
        self.set_color_function(self.DEFAULTS['appearance/color_function'])
        self.logger.debug("[SETTINGS] Couleurs réinitialisées aux valeurs par défaut")

    def get_hljs_theme(self) -> str:
        """Retourne le thème Highlight.js ('light' ou 'dark')."""
        return self._get('appearance/hljs_theme', str)

    def set_hljs_theme(self, theme: str):
        """Définit le thème Highlight.js."""
        if theme not in ['light', 'dark']:
            self.logger.warning(f"[SETTINGS] Thème invalide: {theme}, utilisation de 'dark'")
            theme = 'dark'
        self._set('appearance/hljs_theme', theme)

    # === UI SETTINGS ===
    
    def get_window_size(self) -> tuple[int, int]:
        """Retourne la taille de la fenêtre (width, height)."""
        width = self._get('ui/window_width', int)
        height = self._get('ui/window_height', int)
        return width, height
    
    def set_window_size(self, width: int, height: int):
        """Définit la taille de la fenêtre."""
        self._set('ui/window_width', width)
        self._set('ui/window_height', height)
    
    def get_sidebar_width(self) -> int:
        """Retourne la largeur de la sidebar."""
        return self._get('ui/sidebar_width', int)
    
    def set_sidebar_width(self, width: int):
        """Définit la largeur de la sidebar."""
        self._set('ui/sidebar_width', width)
    
    def get_theme(self) -> str:
        """Retourne le thème ('light' ou 'dark')."""
        return self._get('ui/theme', str)

    def set_theme(self, theme: str):
        """Définit le thème."""
        self._set('ui/theme', theme)

    def get_chat_splitter_sizes(self) -> list[int]:
        """Retourne les tailles du splitter chat/input [top, bottom]. Retourne [] si non défini."""
        top = self._get('ui/chat_splitter_top', int)
        bottom = self._get('ui/chat_splitter_bottom', int)
        if top > 0 and bottom > 0:
            return [top, bottom]
        return []

    def set_chat_splitter_sizes(self, sizes: list[int]):
        """Sauvegarde les tailles du splitter chat/input."""
        if len(sizes) == 2:
            self._set('ui/chat_splitter_top', sizes[0])
            self._set('ui/chat_splitter_bottom', sizes[1])

    def get_sidebar_splitter_sizes(self) -> list[int]:
        """Retourne les tailles du splitter sidebar/centre [left, right]. Retourne [] si non défini."""
        left = self._get('ui/sidebar_splitter_left', int)
        right = self._get('ui/sidebar_splitter_right', int)
        if left > 0 and right > 0:
            return [left, right]
        return []

    def set_sidebar_splitter_sizes(self, sizes: list[int]):
        """Sauvegarde les tailles du splitter sidebar/centre."""
        if len(sizes) == 2:
            self._set('ui/sidebar_splitter_left', sizes[0])
            self._set('ui/sidebar_splitter_right', sizes[1])

    # === DRAFT SETTINGS ===

    def get_draft(self) -> str:
        """Retourne le brouillon sauvegardé."""
        return self._get('draft/content', str)

    def set_draft(self, content: str):
        """Sauvegarde le brouillon du champ de saisie."""
        self._set('draft/content', content)

    # === BEHAVIOR SETTINGS ===

    def get_auto_scroll(self) -> bool:
        """Retourne l'état de l'auto-scroll."""
        return self._get('behavior/auto_scroll', bool)
    
    def set_auto_scroll(self, enabled: bool):
        """Définit l'auto-scroll."""
        self._set('behavior/auto_scroll', enabled)
    
    def get_confirm_delete(self) -> bool:
        """Retourne l'état de la confirmation de suppression."""
        return self._get('behavior/confirm_delete', bool)
    
    def set_confirm_delete(self, enabled: bool):
        """Définit la confirmation de suppression."""
        self._set('behavior/confirm_delete', enabled)

    def get_max_displayed_messages(self) -> int:
        """Retourne le nombre maximum de messages affichés dans le chat."""
        return self._get('behavior/max_displayed_messages', int)

    def set_max_displayed_messages(self, count: int):
        """Définit le nombre maximum de messages affichés dans le chat."""
        self._set('behavior/max_displayed_messages', count)

    # === MÉTHODES PRIVÉES ===
    
    def _get(self, key: str, value_type: type):
        """
        Récupère une valeur depuis QSettings avec valeur par défaut.
        
        Args:
            key: Clé du paramètre
            value_type: Type attendu (str, int, bool, float)
        
        Returns:
            Valeur du paramètre ou valeur par défaut
        """
        default = self.DEFAULTS.get(key)
        value = self.settings.value(key, default)
        
        # Conversion de type si nécessaire
        if value_type == bool:
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes')
            return bool(value)
        elif value_type == int:
            return int(value) if value else 0
        elif value_type == float:
            return float(value) if value else 0.0
        else:
            return str(value) if value else ''
    
    def _set(self, key: str, value):
        """
        Sauvegarde une valeur dans QSettings.
        
        Args:
            key: Clé du paramètre
            value: Valeur à sauvegarder
        """
        self.settings.setValue(key, value)
        self.settings.sync()
        self.logger.debug(f"[SETTINGS] Paramètre sauvegardé: {key}")
    
    # === UTILITAIRES ===
    
    def reset_all(self):
        """Réinitialise tous les paramètres aux valeurs par défaut."""
        self.settings.clear()
        self.logger.debug("[SETTINGS] Tous les paramètres réinitialisés")
    
    def export_settings(self) -> dict:
        """Exporte tous les paramètres sous forme de dictionnaire."""
        exported = {}
        for key in self.DEFAULTS.keys():
            value = self.settings.value(key, self.DEFAULTS[key])
            exported[key] = value
        
        self.logger.debug(f"[SETTINGS] {len(exported)} paramètres exportés")
        return exported
    
    def import_settings(self, settings_dict: dict):
        """
        Importe des paramètres depuis un dictionnaire.
        
        Args:
            settings_dict: Dictionnaire de paramètres
        """
        for key, value in settings_dict.items():
            if key in self.DEFAULTS:
                self.settings.setValue(key, value)
        
        self.settings.sync()
        self.logger.debug(f"[SETTINGS] {len(settings_dict)} paramètres importés")
    
    def get_all_api_settings(self) -> dict:
        """Retourne tous les paramètres API."""
        return {
            'api_key': self.get_api_key(),
            'base_url': self.get_base_url(),
            'model': self.get_model(),
            'verify_ssl': self.get_verify_ssl(),
            'temperature': self.get_temperature(),
            'max_tokens': self.get_max_tokens(),
        }
