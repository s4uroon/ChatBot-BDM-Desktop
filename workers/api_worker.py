"""
workers/api_worker.py
=====================
Worker thread pour les requêtes API en streaming
"""

import time
from PyQt6.QtCore import QThread, pyqtSignal
from typing import List, Dict
from core.logger import get_logger


class APIWorker(QThread):
    """
    Worker thread pour exécuter les requêtes API en streaming.
    
    Évite le blocage de l'interface utilisateur pendant les appels API.
    Émet des signaux pour chaque chunk reçu et la complétion.
    """
    
    # Signaux émis
    chunk_received = pyqtSignal(str)  # Fragment de réponse
    response_complete = pyqtSignal(str)  # Réponse complète
    error_occurred = pyqtSignal(str)  # Erreur rencontrée
    progress_updated = pyqtSignal(int)  # Progression (nombre de chunks)
    
    def __init__(
        self,
        api_client,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = None
    ):
        """
        Initialise le worker.
        
        Args:
            api_client: Instance de APIClient
            messages: Liste des messages du contexte
            temperature: Créativité du modèle
            max_tokens: Limite de tokens (None = pas de limite)
        """
        super().__init__()
        self.logger = get_logger()
        self.api_client = api_client
        self.messages = messages
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        self._is_running = False
        self._full_response = ""
    
    def run(self):
        """Exécute le streaming API dans le thread."""
        self._is_running = True
        self._full_response = ""
        chunk_count = 0
        start_time = time.time()
        
        try:
            self.logger.debug(f"[WORKER] Démarrage du streaming pour {len(self.messages)} messages")
            
            # Streaming depuis l'API
            for chunk in self.api_client.chat_completion_stream(
                messages=self.messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            ):
                if not self._is_running:
                    self.logger.debug("[WORKER] Thread arrêté par l'utilisateur")
                    break
                
                # Accumuler la réponse
                self._full_response += chunk
                chunk_count += 1
                
                # Émettre le chunk
                self.chunk_received.emit(chunk)
                
                # Progression
                if chunk_count % 5 == 0:  # Mise à jour tous les 5 chunks
                    self.progress_updated.emit(chunk_count)
            
            # Calcul de la durée
            duration = time.time() - start_time
            
            if self._is_running:
                # Succès
                self.logger.debug(f"[WORKER] Stream terminé: {chunk_count} chunks en {duration:.2f}s")
                self.response_complete.emit(self._full_response)
            
        except Exception as e:
            self.logger.error(f"[WORKER] Streaming API", exc_info=True)
            self.error_occurred.emit(f"Erreur API: {str(e)}")
        
        finally:
            self._is_running = False
    
    def stop(self):
        """Arrête le thread proprement."""
        self._is_running = False
        self.logger.debug("[WORKER] Arrêt demandé")
    
    def get_full_response(self) -> str:
        """Retourne la réponse complète accumulée."""
        return self._full_response
    
    def is_running(self) -> bool:
        """Vérifie si le thread est en cours d'exécution."""
        return self._is_running
