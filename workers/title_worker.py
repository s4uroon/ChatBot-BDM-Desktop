"""
workers/title_worker.py
========================
Worker thread pour générer automatiquement un titre de conversation via l'API
"""

from PyQt6.QtCore import QThread, pyqtSignal
from core.logger import get_logger
from core.constants import AUTO_TITLE_PROMPT, AUTO_TITLE_MAX_LENGTH


class TitleWorker(QThread):
    """
    Worker thread pour générer un titre de conversation via l'API.
    S'exécute en arrière-plan après la première réponse de l'assistant.
    """

    title_generated = pyqtSignal(int, str)  # (conversation_id, title)
    error_occurred = pyqtSignal(str)

    def __init__(self, api_client, conversation_id: int, user_message: str):
        """
        Args:
            api_client: Instance de APIClient
            conversation_id: ID de la conversation à renommer
            user_message: Premier message de l'utilisateur
        """
        super().__init__()
        self.logger = get_logger()
        self.api_client = api_client
        self.conversation_id = conversation_id
        self.user_message = user_message

    def run(self):
        """Génère un titre via l'API."""
        try:
            self.logger.debug(f"[TITLE_WORKER] Génération titre pour conversation {self.conversation_id}")

            # Utiliser l'API pour générer un titre court
            messages = [
                {"role": "user", "content": AUTO_TITLE_PROMPT + self.user_message[:500]}
            ]

            response = self.api_client.chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=30
            )

            if response:
                # Nettoyer le titre (retirer guillemets, sauts de ligne, etc.)
                title = response.strip().strip('"').strip("'").strip()
                # Tronquer si trop long
                if len(title) > AUTO_TITLE_MAX_LENGTH:
                    title = title[:AUTO_TITLE_MAX_LENGTH] + "..."

                if title:
                    self.logger.debug(f"[TITLE_WORKER] Titre généré: '{title}'")
                    self.title_generated.emit(self.conversation_id, title)
                    return

            self.logger.warning("[TITLE_WORKER] Pas de titre généré par l'API")

        except Exception as e:
            self.logger.error(f"[TITLE_WORKER] Erreur génération titre", exc_info=True)
            self.error_occurred.emit(f"Erreur titre auto: {str(e)}")
