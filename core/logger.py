"""
core/logger.py
==============
Système de logging centralisé avec support CLI
"""

import logging
import sys
from typing import Optional


class LoggerSetup:
    """
    Configuration centralisée du système de logging.
    Supporte l'activation via CLI et affichage console formaté.
    """
    
    _instance: Optional['LoggerSetup'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not LoggerSetup._initialized:
            self.logger = logging.getLogger('ChatbotDesktop')
            self.logger.setLevel(logging.DEBUG)
            LoggerSetup._initialized = True
    
    def setup_console_logging(self, debug: bool = False) -> None:
        """
        Configure le logging console avec format personnalisé.
        
        Args:
            debug: Active le mode DEBUG avec affichage détaillé
        """
        if debug:
            # Handler console avec formatage coloré
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            
            # Format détaillé pour le debug
            formatter = logging.Formatter(
                fmt='%(asctime)s [%(levelname)-8s] [%(name)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            
            # Éviter les doublons
            if not any(isinstance(h, logging.StreamHandler) for h in self.logger.handlers):
                self.logger.addHandler(console_handler)
            
            self.logger.info("="*70)
            self.logger.info("MODE DEBUG ACTIVÉ - Logging console démarré")
            self.logger.info("="*70)
        else:
            # En mode normal, on log seulement les erreurs
            self.logger.setLevel(logging.WARNING)
    
    def log_config(self, config: dict) -> None:
        """Log l'état de la configuration au démarrage."""
        self.logger.debug("[CONFIG] État de la configuration:")
        for key, value in config.items():
            # Masquer les clés API
            if 'api_key' in key.lower() or 'key' in key.lower():
                display_value = f"{value[:8]}..." if value else "Non définie"
            else:
                display_value = value
            self.logger.debug(f"  - {key}: {display_value}")
    
    def log_api_request(self, model: str, messages_count: int) -> None:
        """Log le début d'une requête API."""
        self.logger.debug(f"[API] Démarrage requête vers modèle '{model}' ({messages_count} messages)")
    
    def log_api_chunk(self, chunk_num: int, content: str) -> None:
        """Log la réception d'un chunk streaming."""
        preview = content[:50] + "..." if len(content) > 50 else content
        self.logger.debug(f"[API] Chunk #{chunk_num} reçu: {preview}")
    
    def log_api_complete(self, total_chunks: int, duration: float) -> None:
        """Log la fin d'une requête API."""
        self.logger.debug(f"[API] Requête terminée: {total_chunks} chunks en {duration:.2f}s")
    
    def log_code_block_detected(self, language: str, line_count: int) -> None:
        """Log la détection d'un bloc de code."""
        self.logger.debug(f"[PARSER] Bloc de code détecté: {language} ({line_count} lignes)")
    
    def log_error(self, context: str, error: Exception) -> None:
        """Log une erreur avec stacktrace complète."""
        self.logger.error(f"[ERREUR] {context}", exc_info=True)
    
    def log_database_operation(self, operation: str, details: str) -> None:
        """Log une opération base de données."""
        self.logger.debug(f"[DATABASE] {operation}: {details}")
    
    def log_export(self, format_type: str, conversation_count: int, filepath: str) -> None:
        """Log une opération d'export."""
        self.logger.info(f"[EXPORT] Export {format_type}: {conversation_count} conversation(s) -> {filepath}")
    
    @staticmethod
    def get_logger() -> logging.Logger:
        """Retourne l'instance du logger."""
        if LoggerSetup._instance is None:
            LoggerSetup()
        return LoggerSetup._instance.logger


# Fonction d'accès rapide
def get_logger() -> logging.Logger:
    """Fonction helper pour accéder au logger depuis n'importe où."""
    return LoggerSetup.get_logger()
