"""
core/tag_manager.py
====================
Gestionnaire de tags pour les conversations
"""

from PyQt6.QtCore import QObject, pyqtSignal
from typing import List, Dict
from .logger import get_logger


class TagManager(QObject):
    """
    Gestion des tags : création, suppression, association aux conversations.
    """

    tags_updated = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, db_manager):
        super().__init__()
        self.logger = get_logger()
        self.db_manager = db_manager

    def create_tag(self, name: str, color: str = '#4CAF50') -> int:
        """Crée un tag et retourne son ID."""
        tag_id = self.db_manager.create_tag(name, color)
        if tag_id > 0:
            self.tags_updated.emit(self.get_all_tags())
        return tag_id

    def delete_tag(self, tag_id: int) -> bool:
        """Supprime un tag."""
        result = self.db_manager.delete_tag(tag_id)
        if result:
            self.tags_updated.emit(self.get_all_tags())
        return result

    def get_all_tags(self) -> List[Dict]:
        """Retourne tous les tags."""
        return self.db_manager.get_all_tags()

    def add_tag_to_conversation(self, conversation_id: int, tag_id: int) -> bool:
        """Associe un tag à une conversation."""
        return self.db_manager.add_tag_to_conversation(conversation_id, tag_id)

    def remove_tag_from_conversation(self, conversation_id: int, tag_id: int) -> bool:
        """Retire un tag d'une conversation."""
        return self.db_manager.remove_tag_from_conversation(conversation_id, tag_id)

    def get_conversation_tags(self, conversation_id: int) -> List[Dict]:
        """Retourne les tags d'une conversation."""
        return self.db_manager.get_conversation_tags(conversation_id)

    def get_conversations_by_tag(self, tag_id: int) -> List[Dict]:
        """Retourne les conversations filtrées par tag."""
        return self.db_manager.get_conversations_by_tag(tag_id)
