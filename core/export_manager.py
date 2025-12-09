"""
core/export_manager.py
======================
Gestion des exports de conversations en JSON ou Markdown
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from .logger import get_logger


class ExportManager:
    """
    Gestionnaire d'export des conversations.
    Formats supportés: JSON, Markdown
    """
    
    def __init__(self):
        self.logger = get_logger()

    def _get_role_info(self, role: str) -> tuple[str, str]:
        """
        Retourne l'icône et le label pour un rôle donné.

        Args:
            role: Le rôle ('user', 'assistant', 'system')

        Returns:
            tuple: (icon, role_label)
        """
        if role == 'user':
            return "👤", "Utilisateur"
        elif role == 'assistant':
            return "🤖", "Assistant"
        elif role == 'system':
            return "⚙️", "Système"
        else:
            return "❓", role.capitalize()

    def export_conversations_json(
        self,
        conversations: List[Dict],
        filepath: str
    ) -> tuple[bool, str]:
        """
        Export des conversations en format JSON.
        
        Args:
            conversations: Liste de dictionnaires conversation
                Format: {
                    'id': int,
                    'title': str,
                    'created_at': str,
                    'messages': [{'role': str, 'content': str}, ...]
                }
            filepath: Chemin du fichier de sortie
        
        Returns:
            (success: bool, message: str)
        """
        try:
            export_data = {
                'export_date': datetime.now().isoformat(),
                'version': '1.0',
                'conversation_count': len(conversations),
                'conversations': conversations
            }
            
            # Écriture avec indentation pour lisibilité
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"[EXPORT] JSON: {len(conversations)} conversation(s) -> {filepath}")
            return True, f"{len(conversations)} conversation(s) exportée(s) avec succès"
            
        except Exception as e:
            error_msg = f"Erreur lors de l'export JSON: {str(e)}"
            self.logger.error(f"[EXPORT] JSON", exc_info=True)
            return False, error_msg
    
    def export_conversations_markdown(
        self,
        conversations: List[Dict],
        filepath: str
    ) -> tuple[bool, str]:
        """
        Export des conversations en format Markdown.
        
        Args:
            conversations: Liste de dictionnaires conversation
            filepath: Chemin du fichier de sortie
        
        Returns:
            (success: bool, message: str)
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # En-tête du document
                f.write("# Export des Conversations\n\n")
                f.write(f"**Date d'export:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Nombre de conversations:** {len(conversations)}\n\n")
                f.write("---\n\n")
                
                # Itération sur les conversations
                for idx, conv in enumerate(conversations, 1):
                    self._write_conversation_markdown(f, conv, idx)
            
            self.logger.info(f"[EXPORT] Markdown: {len(conversations)} conversation(s) -> {filepath}")
            return True, f"{len(conversations)} conversation(s) exportée(s) avec succès"
            
        except Exception as e:
            error_msg = f"Erreur lors de l'export Markdown: {str(e)}"
            self.logger.error(f"[EXPORT] Markdown", exc_info=True)
            return False, error_msg
    
    def _write_conversation_markdown(
        self,
        file,
        conversation: Dict,
        index: int
    ) -> None:
        """
        Écrit une conversation au format Markdown.
        
        Args:
            file: Objet fichier ouvert en écriture
            conversation: Dictionnaire de la conversation
            index: Numéro de la conversation
        """
        # Titre de la conversation
        file.write(f"## {index}. {conversation['title']}\n\n")
        
        # Métadonnées
        file.write(f"**ID:** {conversation['id']}  \n")
        file.write(f"**Créée le:** {conversation['created_at']}  \n")
        file.write(f"**Messages:** {len(conversation['messages'])}\n\n")
        
        # Messages
        for msg_idx, message in enumerate(conversation['messages'], 1):
            role = message['role']
            content = message['content']

            # Icône selon le rôle
            icon, role_label = self._get_role_info(role)

            file.write(f"### {icon} {role_label} (Message {msg_idx})\n\n")
            file.write(f"{content}\n\n")
        
        file.write("---\n\n")
    
    def export_single_conversation_markdown(
        self,
        conversation: Dict,
        filepath: str
    ) -> tuple[bool, str]:
        """
        Export d'une seule conversation en Markdown.
        
        Args:
            conversation: Dictionnaire de la conversation
            filepath: Chemin du fichier de sortie
        
        Returns:
            (success: bool, message: str)
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # En-tête
                f.write(f"# {conversation['title']}\n\n")
                f.write(f"**Créée le:** {conversation['created_at']}  \n")
                f.write(f"**ID:** {conversation['id']}  \n\n")
                f.write("---\n\n")
                
                # Messages
                for msg_idx, message in enumerate(conversation['messages'], 1):
                    role = message['role']
                    content = message['content']

                    # Icône selon le rôle
                    icon, role_label = self._get_role_info(role)

                    f.write(f"## {icon} {role_label}\n\n")
                    f.write(f"{content}\n\n")
                    f.write("---\n\n")
            
            self.logger.info(f"[EXPORT] Markdown (single): 1 conversation -> {filepath}")
            return True, "Conversation exportée avec succès"
            
        except Exception as e:
            error_msg = f"Erreur lors de l'export: {str(e)}"
            self.logger.error(f"[EXPORT] Conversation unique", exc_info=True)
            return False, error_msg
    
    def prepare_conversations_for_export(
        self,
        db_manager,
        conversation_ids: Optional[List[int]] = None
    ) -> List[Dict]:
        """
        Prépare les conversations pour l'export depuis la base de données.
        
        Args:
            db_manager: Instance du gestionnaire de base de données
            conversation_ids: Liste des IDs à exporter (None = toutes)
        
        Returns:
            Liste de conversations formatées
        """
        conversations = []
        
        try:
            if conversation_ids:
                # Export sélectif
                for conv_id in conversation_ids:
                    conv_data = db_manager.get_conversation_with_messages(conv_id)
                    if conv_data:
                        conversations.append(conv_data)
            else:
                # Export complet
                all_convs = db_manager.get_all_conversations()
                for conv in all_convs:
                    conv_data = db_manager.get_conversation_with_messages(conv['id'])
                    if conv_data:
                        conversations.append(conv_data)
            
            self.logger.debug(f"[EXPORT] {len(conversations)} conversation(s) préparée(s)")
            
        except Exception as e:
            self.logger.error(f"[EXPORT] Préparation export", exc_info=True)
        
        return conversations
    
    @staticmethod
    def generate_filename(base_name: str, extension: str) -> str:
        """
        Génère un nom de fichier avec timestamp.
        
        Args:
            base_name: Nom de base du fichier
            extension: Extension (.json ou .md)
        
        Returns:
            Nom de fichier formaté
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{base_name}_{timestamp}.{extension}"
