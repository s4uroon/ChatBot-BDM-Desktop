"""
core/conversation_manager.py
=============================
Gestionnaire de conversations (CRUD, recherche, titrage)
Extrait de MainController pour une meilleure séparation des responsabilités.
"""

from PyQt6.QtCore import QObject, pyqtSignal
from typing import List, Dict, Optional
from .logger import get_logger
from .constants import AUTO_TITLE_MAX_LENGTH


class ConversationManager(QObject):
    """
    Gestion des conversations : création, chargement, suppression, recherche, renommage.
    """

    # Signaux
    conversations_updated = pyqtSignal(list)
    conversation_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, db_manager):
        super().__init__()
        self.logger = get_logger()
        self.db_manager = db_manager

        self.current_conversation_id: Optional[int] = None
        self.current_messages: List[Dict] = []

    def create_conversation(self, title: str = "Nouvelle conversation") -> Optional[int]:
        """Crée une nouvelle conversation et retourne son ID."""
        try:
            conv_id = self.db_manager.create_conversation(title)
            self.current_conversation_id = conv_id
            self.current_messages = []
            self.logger.debug(f"[CONV_MGR] Conversation créée: ID {conv_id}")
            self.refresh_conversations_list()
            return conv_id
        except Exception as e:
            self.logger.error(f"[CONV_MGR] Création conversation", exc_info=True)
            self.error_occurred.emit(f"Erreur lors de la création: {str(e)}")
            return None

    def load_conversation(self, conversation_id: int) -> List[Dict]:
        """Charge les messages d'une conversation."""
        try:
            messages = self.db_manager.get_messages(conversation_id)
            self.current_conversation_id = conversation_id
            self.current_messages = messages
            self.logger.debug(f"[CONV_MGR] Conversation {conversation_id} chargée: {len(messages)} messages")
            return messages
        except Exception as e:
            self.logger.error(f"[CONV_MGR] Chargement conversation", exc_info=True)
            self.error_occurred.emit(f"Erreur chargement: {str(e)}")
            return []

    def delete_conversations(self, conversation_ids: List[int]) -> bool:
        """Supprime une ou plusieurs conversations."""
        try:
            for conv_id in conversation_ids:
                self.db_manager.delete_conversation(conv_id)
                if conv_id == self.current_conversation_id:
                    self.current_conversation_id = None
                    self.current_messages = []
            self.logger.debug(f"[CONV_MGR] {len(conversation_ids)} conversation(s) supprimée(s)")
            self.refresh_conversations_list()
            return True
        except Exception as e:
            self.logger.error(f"[CONV_MGR] Suppression conversations", exc_info=True)
            self.error_occurred.emit(f"Erreur suppression: {str(e)}")
            return False

    def rename_conversation(self, conversation_id: int, new_title: str) -> bool:
        """Renomme une conversation."""
        try:
            self.db_manager.update_conversation_title(conversation_id, new_title)
            self.logger.debug(f"[CONV_MGR] Conversation {conversation_id} renommée: '{new_title}'")
            self.refresh_conversations_list()
            return True
        except Exception as e:
            self.logger.error(f"[CONV_MGR] Renommage conversation", exc_info=True)
            self.error_occurred.emit(f"Erreur renommage: {str(e)}")
            return False

    def search_conversations(self, query: str) -> List[Dict]:
        """Recherche dans les conversations."""
        try:
            if not query.strip():
                return self.db_manager.get_all_conversations()
            return self.db_manager.search_conversations(query)
        except Exception as e:
            self.logger.error(f"[CONV_MGR] Recherche conversations", exc_info=True)
            return []

    def save_user_message(self, content: str, tokens: int = 0) -> Optional[int]:
        """Sauvegarde un message utilisateur."""
        if not self.current_conversation_id:
            return None
        try:
            msg_id = self.db_manager.add_message(
                self.current_conversation_id, 'user', content, tokens
            )
            self.current_messages.append({'role': 'user', 'content': content})
            return msg_id
        except Exception as e:
            self.logger.error(f"[CONV_MGR] Sauvegarde message user", exc_info=True)
            return None

    def save_assistant_message(self, content: str, tokens: int = 0) -> Optional[int]:
        """Sauvegarde un message assistant."""
        if not self.current_conversation_id:
            return None
        try:
            msg_id = self.db_manager.add_message(
                self.current_conversation_id, 'assistant', content, tokens
            )
            self.current_messages.append({'role': 'assistant', 'content': content})
            return msg_id
        except Exception as e:
            self.logger.error(f"[CONV_MGR] Sauvegarde message assistant", exc_info=True)
            return None

    def refresh_conversations_list(self):
        """Émet la liste des conversations mise à jour."""
        try:
            conversations = self.db_manager.get_all_conversations()
            self.conversations_updated.emit(conversations)
        except Exception as e:
            self.logger.error(f"[CONV_MGR] Rafraîchissement liste", exc_info=True)

    def generate_title_from_message(self, message: str, max_length: int = AUTO_TITLE_MAX_LENGTH) -> str:
        """Génère un titre court à partir du premier message (fallback sans API)."""
        title = message.strip()
        if len(title) > max_length:
            title = title[:max_length] + "..."
        return title if title else "New session"

    def get_messages_for_api(self) -> List[Dict]:
        """Retourne les messages au format API (role + content)."""
        return [{'role': m['role'], 'content': m['content']} for m in self.current_messages]
