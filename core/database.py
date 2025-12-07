"""
core/database.py
================
Gestionnaire de base de données SQLite pour conversations et messages
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from .logger import get_logger


class DatabaseManager:
    """
    Gestionnaire de base de données SQLite.
    
    Structure:
    - Table conversations: id, title, created_at
    - Table messages: id, conversation_id, role, content, timestamp
    """
    
    def __init__(self, db_path: str = "chatbot.db"):
        """
        Initialise la connexion à la base de données.
        
        Args:
            db_path: Chemin du fichier de base de données
        """
        self.logger = get_logger()
        self.db_path = db_path
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialise la base de données et crée les tables."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            
            cursor = self.connection.cursor()
            
            # Table conversations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Table messages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                        ON DELETE CASCADE
                )
            """)
            
            # Index pour performances
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation 
                ON messages(conversation_id)
            """)
            
            self.connection.commit()
            self.logger.debug(f"[DATABASE] INIT: Base de données '{self.db_path}' initialisée")
        
        except Exception as e:
            self.logger.error(f"[DATABASE] Initialisation base de données", exc_info=True)
            raise
    
    # === CONVERSATIONS ===
    
    def create_conversation(self, title: str) -> int:
        """
        Crée une nouvelle conversation.
        
        Args:
            title: Titre de la conversation
        
        Returns:
            ID de la conversation créée
        """
        try:
            cursor = self.connection.cursor()
            created_at = datetime.now().isoformat()
            
            cursor.execute(
                "INSERT INTO conversations (title, created_at) VALUES (?, ?)",
                (title, created_at)
            )
            self.connection.commit()
            
            conv_id = cursor.lastrowid
            self.logger.debug(f"[DATABASE] CREATE: Conversation ID {conv_id}")
            
            return conv_id
        
        except Exception as e:
            self.logger.error(f"[DATABASE] Création conversation", exc_info=True)
            raise
    
    def get_conversation(self, conv_id: int) -> Optional[Dict]:
        """
        Récupère une conversation par son ID.
        
        Args:
            conv_id: ID de la conversation
        
        Returns:
            Dict {'id', 'title', 'created_at'} ou None
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT id, title, created_at FROM conversations WHERE id = ?",
                (conv_id,)
            )
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        
        except Exception as e:
            self.logger.error(f"[DATABASE] Récupération conversation", exc_info=True)
            return None
    
    def get_all_conversations(self) -> List[Dict]:
        """
        Récupère toutes les conversations.
        
        Returns:
            Liste de dicts {'id', 'title', 'created_at'}
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT id, title, created_at FROM conversations ORDER BY created_at DESC"
            )
            
            rows = cursor.fetchall()
            conversations = [dict(row) for row in rows]
            
            self.logger.debug(f"[DATABASE] SELECT: {len(conversations)} conversation(s)")
            return conversations
        
        except Exception as e:
            self.logger.error(f"[DATABASE] Récupération conversations", exc_info=True)
            return []
    
    def update_conversation_title(self, conv_id: int, new_title: str) -> bool:
        """
        Met à jour le titre d'une conversation.
        
        Args:
            conv_id: ID de la conversation
            new_title: Nouveau titre
        
        Returns:
            True si succès
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE conversations SET title = ? WHERE id = ?",
                (new_title, conv_id)
            )
            self.connection.commit()
            
            self.logger.debug(f"[DATABASE] UPDATE: Titre conversation ID {conv_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"[DATABASE] Mise à jour titre", exc_info=True)
            return False
    
    def delete_conversation(self, conv_id: int) -> bool:
        """
        Supprime une conversation et tous ses messages (CASCADE).
        
        Args:
            conv_id: ID de la conversation
        
        Returns:
            True si succès
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
            self.connection.commit()
            
            self.logger.debug(f"[DATABASE] DELETE: Conversation ID {conv_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"[DATABASE] Suppression conversation", exc_info=True)
            return False
    
    # === MESSAGES ===
    
    def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str
    ) -> int:
        """
        Ajoute un message à une conversation.
        
        Args:
            conversation_id: ID de la conversation
            role: 'user' ou 'assistant' ou 'system'
            content: Contenu du message
        
        Returns:
            ID du message créé
        """
        try:
            cursor = self.connection.cursor()
            timestamp = datetime.now().isoformat()
            
            cursor.execute(
                """
                INSERT INTO messages (conversation_id, role, content, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (conversation_id, role, content, timestamp)
            )
            self.connection.commit()
            
            msg_id = cursor.lastrowid
            self.logger.debug(f"[DATABASE] INSERT: Message ID {msg_id} ({role}) dans conversation {conversation_id}")
            
            return msg_id
        
        except Exception as e:
            self.logger.error(f"[DATABASE] Ajout message", exc_info=True)
            raise
    
    def get_messages(self, conversation_id: int) -> List[Dict]:
        """
        Récupère tous les messages d'une conversation.
        
        Args:
            conversation_id: ID de la conversation
        
        Returns:
            Liste de dicts {'id', 'role', 'content', 'timestamp'}
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT id, role, content, timestamp
                FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp ASC
                """,
                (conversation_id,)
            )
            
            rows = cursor.fetchall()
            messages = [dict(row) for row in rows]
            
            self.logger.debug(f"[DATABASE] SELECT: {len(messages)} message(s) pour conversation {conversation_id}")
            
            return messages
        
        except Exception as e:
            self.logger.error(f"[DATABASE] Récupération messages", exc_info=True)
            return []
    
    def get_conversation_with_messages(self, conv_id: int) -> Optional[Dict]:
        """
        Récupère une conversation complète avec tous ses messages.
        
        Args:
            conv_id: ID de la conversation
        
        Returns:
            Dict {'id', 'title', 'created_at', 'messages': [...]} ou None
        """
        try:
            conversation = self.get_conversation(conv_id)
            if not conversation:
                return None
            
            messages = self.get_messages(conv_id)
            
            # Format pour l'API (sans id et timestamp)
            api_messages = [
                {'role': msg['role'], 'content': msg['content']}
                for msg in messages
            ]
            
            conversation['messages'] = api_messages
            return conversation
        
        except Exception as e:
            self.logger.error(f"[DATABASE] Récupération conversation complète", exc_info=True)
            return None
    
    def delete_message(self, message_id: int) -> bool:
        """
        Supprime un message spécifique.
        
        Args:
            message_id: ID du message
        
        Returns:
            True si succès
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM messages WHERE id = ?", (message_id,))
            self.connection.commit()
            
            self.logger.debug(f"[DATABASE] DELETE: Message ID {message_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"[DATABASE] Suppression message", exc_info=True)
            return False
    
    # === UTILITAIRES ===
    
    def get_conversation_count(self) -> int:
        """Retourne le nombre total de conversations."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversations")
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            self.logger.error(f"[DATABASE] Comptage conversations", exc_info=True)
            return 0
    
    def get_message_count(self, conversation_id: Optional[int] = None) -> int:
        """
        Retourne le nombre de messages.
        
        Args:
            conversation_id: Si spécifié, compte pour cette conversation seulement
        
        Returns:
            Nombre de messages
        """
        try:
            cursor = self.connection.cursor()
            
            if conversation_id:
                cursor.execute(
                    "SELECT COUNT(*) FROM messages WHERE conversation_id = ?",
                    (conversation_id,)
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM messages")
            
            count = cursor.fetchone()[0]
            return count
        
        except Exception as e:
            self.logger.error(f"[DATABASE] Comptage messages", exc_info=True)
            return 0
    
    def search_conversations(self, query: str) -> List[Dict]:
        """
        Recherche dans les titres et contenus de messages.
        
        Args:
            query: Terme de recherche
        
        Returns:
            Liste de conversations correspondantes
        """
        try:
            cursor = self.connection.cursor()
            search_pattern = f"%{query}%"
            
            cursor.execute(
                """
                SELECT DISTINCT c.id, c.title, c.created_at
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                WHERE c.title LIKE ? OR m.content LIKE ?
                ORDER BY c.created_at DESC
                """,
                (search_pattern, search_pattern)
            )
            
            rows = cursor.fetchall()
            conversations = [dict(row) for row in rows]
            
            self.logger.debug(f"[DATABASE] SEARCH: {len(conversations)} résultat(s) pour '{query}'")
            
            return conversations
        
        except Exception as e:
            self.logger.error(f"[DATABASE] Recherche conversations", exc_info=True)
            return []
    
    def vacuum(self):
        """Optimise la base de données (récupère l'espace)."""
        try:
            self.connection.execute("VACUUM")
            self.logger.debug(f"[DATABASE] VACUUM: Base de données optimisée")
        except Exception as e:
            self.logger.error(f"[DATABASE] Vacuum database", exc_info=True)
    
    def close(self):
        """Ferme la connexion à la base de données."""
        try:
            if self.connection:
                self.connection.close()
                self.logger.debug(f"[DATABASE] CLOSE: Connexion fermée")
        except Exception as e:
            self.logger.error(f"[DATABASE] Fermeture connexion", exc_info=True)
