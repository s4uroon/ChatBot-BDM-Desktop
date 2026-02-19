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
            # check_same_thread=False permet l'accès depuis plusieurs threads (API worker)
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row

            cursor = self.connection.cursor()

            # Activer les clés étrangères pour que ON DELETE CASCADE fonctionne
            cursor.execute("PRAGMA foreign_keys = ON")
            # Activer le mode WAL pour de meilleures performances en lecture concurrente
            cursor.execute("PRAGMA journal_mode = WAL")

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
                    tokens_estimated INTEGER DEFAULT 0,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                        ON DELETE CASCADE
                )
            """)

            # Table tags
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    color TEXT DEFAULT '#4CAF50'
                )
            """)

            # Table de liaison conversations <-> tags
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_tags (
                    conversation_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    PRIMARY KEY (conversation_id, tag_id),
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                )
            """)

            # Index pour performances
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation
                ON messages(conversation_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_timestamp
                ON messages(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_created_at
                ON conversations(created_at)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_tags_conv
                ON conversation_tags(conversation_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_tags_tag
                ON conversation_tags(tag_id)
            """)

            # Migration: ajouter la colonne tokens_estimated si elle n'existe pas
            self._migrate_add_column(cursor, 'messages', 'tokens_estimated', 'INTEGER DEFAULT 0')

            self.connection.commit()
            self.logger.debug(f"[DATABASE] INIT: Base de données '{self.db_path}' initialisée")

        except Exception as e:
            self.logger.error(f"[DATABASE] Initialisation base de données", exc_info=True)
            raise

    def _migrate_add_column(self, cursor, table: str, column: str, column_type: str):
        """Ajoute une colonne si elle n'existe pas (migration)."""
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [row[1] for row in cursor.fetchall()]
            if column not in columns:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
                self.logger.debug(f"[DATABASE] Migration: colonne '{column}' ajoutée à '{table}'")
        except Exception as e:
            self.logger.warning(f"[DATABASE] Migration colonne {column}: {e}")
    
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
        content: str,
        tokens_estimated: int = 0
    ) -> int:
        """
        Ajoute un message à une conversation.

        Args:
            conversation_id: ID de la conversation
            role: 'user' ou 'assistant' ou 'system'
            content: Contenu du message
            tokens_estimated: Estimation du nombre de tokens

        Returns:
            ID du message créé
        """
        try:
            cursor = self.connection.cursor()
            timestamp = datetime.now().isoformat()

            cursor.execute(
                """
                INSERT INTO messages (conversation_id, role, content, timestamp, tokens_estimated)
                VALUES (?, ?, ?, ?, ?)
                """,
                (conversation_id, role, content, timestamp, tokens_estimated)
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
            search_pattern = f"%{query.lower()}%"

            cursor.execute(
                """
                SELECT DISTINCT c.id, c.title, c.created_at
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                WHERE LOWER(c.title) LIKE ? OR LOWER(m.content) LIKE ?
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
    
    # === TAGS ===

    def create_tag(self, name: str, color: str = '#4CAF50') -> int:
        """Crée un nouveau tag. Retourne l'ID du tag."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO tags (name, color) VALUES (?, ?)", (name, color))
            self.connection.commit()
            tag_id = cursor.lastrowid
            self.logger.debug(f"[DATABASE] CREATE TAG: '{name}' (ID {tag_id})")
            return tag_id
        except sqlite3.IntegrityError:
            # Tag existe déjà, retourner son ID
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM tags WHERE name = ?", (name,))
            row = cursor.fetchone()
            return row['id'] if row else -1
        except Exception as e:
            self.logger.error(f"[DATABASE] Création tag", exc_info=True)
            return -1

    def get_all_tags(self) -> List[Dict]:
        """Retourne tous les tags."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id, name, color FROM tags ORDER BY name ASC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"[DATABASE] Récupération tags", exc_info=True)
            return []

    def delete_tag(self, tag_id: int) -> bool:
        """Supprime un tag."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
            self.connection.commit()
            return True
        except Exception as e:
            self.logger.error(f"[DATABASE] Suppression tag", exc_info=True)
            return False

    def add_tag_to_conversation(self, conversation_id: int, tag_id: int) -> bool:
        """Associe un tag à une conversation."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO conversation_tags (conversation_id, tag_id) VALUES (?, ?)",
                (conversation_id, tag_id)
            )
            self.connection.commit()
            return True
        except Exception as e:
            self.logger.error(f"[DATABASE] Ajout tag à conversation", exc_info=True)
            return False

    def remove_tag_from_conversation(self, conversation_id: int, tag_id: int) -> bool:
        """Retire un tag d'une conversation."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM conversation_tags WHERE conversation_id = ? AND tag_id = ?",
                (conversation_id, tag_id)
            )
            self.connection.commit()
            return True
        except Exception as e:
            self.logger.error(f"[DATABASE] Retrait tag", exc_info=True)
            return False

    def get_conversation_tags(self, conversation_id: int) -> List[Dict]:
        """Retourne les tags d'une conversation."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT t.id, t.name, t.color
                FROM tags t
                JOIN conversation_tags ct ON t.id = ct.tag_id
                WHERE ct.conversation_id = ?
                ORDER BY t.name ASC
            """, (conversation_id,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"[DATABASE] Récupération tags conversation", exc_info=True)
            return []

    def get_conversations_by_tag(self, tag_id: int) -> List[Dict]:
        """Retourne les conversations associées à un tag."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT c.id, c.title, c.created_at
                FROM conversations c
                JOIN conversation_tags ct ON c.id = ct.conversation_id
                WHERE ct.tag_id = ?
                ORDER BY c.created_at DESC
            """, (tag_id,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"[DATABASE] Conversations par tag", exc_info=True)
            return []

    def get_conversation_token_total(self, conversation_id: int) -> int:
        """Retourne le total de tokens estimés pour une conversation."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT COALESCE(SUM(tokens_estimated), 0) FROM messages WHERE conversation_id = ?",
                (conversation_id,)
            )
            return cursor.fetchone()[0]
        except Exception as e:
            self.logger.error(f"[DATABASE] Total tokens conversation", exc_info=True)
            return 0

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
