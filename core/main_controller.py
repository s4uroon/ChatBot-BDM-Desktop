"""
core/main_controller.py
=======================
Contrôleur principal de l'application - Orchestration
"""

from typing import Optional, List
from PyQt6.QtCore import QObject, pyqtSignal
from .logger import get_logger
from .database import DatabaseManager
from .api_client import APIClient, create_api_client
from .settings_manager import SettingsManager
from .export_manager import ExportManager
from .conversation_manager import ConversationManager
from .tag_manager import TagManager
from .constants import AUTO_TITLE_MAX_LENGTH


class MainController(QObject):
    """
    Contrôleur principal de l'application.
    
    Responsabilités:
    - Orchestration entre UI, Database, et API
    - Gestion du cycle de vie des conversations
    - Coordination des opérations asynchrones
    - État global de l'application
    """
    
    # Signaux pour communication avec l'UI
    conversation_loaded = pyqtSignal(dict)  # Conversation chargée
    conversations_list_updated = pyqtSignal(list)  # Liste mise à jour
    message_received = pyqtSignal(str)  # Message reçu du streaming
    error_occurred = pyqtSignal(str)  # Erreur à afficher
    status_changed = pyqtSignal(str)  # Changement de statut
    
    def __init__(self, db_path: Optional[str] = None, settings_file: Optional[str] = None):
        """
        Initialise le contrôleur principal.

        Args:
            db_path: Chemin de la base de données (optionnel)
            settings_file: Chemin du fichier de configuration (optionnel)
        """
        super().__init__()
        self.logger = get_logger()

        # Managers
        if db_path:
            self.db_manager = DatabaseManager(db_path)
        else:
            self.db_manager = DatabaseManager()

        if settings_file:
            self.settings_manager = SettingsManager(settings_file)
        else:
            self.settings_manager = SettingsManager()

        self.export_manager = ExportManager()

        # Sous-gestionnaires dédiés
        self.conversation_manager = ConversationManager(self.db_manager)
        self.tag_manager = TagManager(self.db_manager)

        # État
        self.current_conversation_id: Optional[int] = None
        self.current_messages: List[dict] = []
        self.api_client: Optional[APIClient] = None

        # Initialisation
        self._initialize_api_client()
        self.logger.debug("[CONTROLLER] Initialisé")
    
    def _initialize_api_client(self):
        """Initialise le client API depuis le profil actif."""
        try:
            profile = self.settings_manager.get_active_profile()
            if profile and profile.api_key:
                if self.api_client:
                    self.api_client.close()
                self.api_client = create_api_client(profile)
                self.logger.debug(
                    f"[CONFIG] Profil actif: '{profile.name}' "
                    f"({profile.provider}) → {profile.model}"
                )
            else:
                self.logger.debug("[CONTROLLER] Aucun profil actif configuré")

        except Exception as e:
            self.logger.error(f"[CONTROLLER] Initialisation API Client", exc_info=True)

    def switch_profile(self, profile_id: str):
        """
        Bascule vers un autre profil API à chaud.

        Si la conversation courante n'a encore reçu aucun message, on met
        également à jour son api_profile_id en DB pour suivre le choix de
        l'utilisateur. Une fois qu'un message a été envoyé, la liaison
        devient permanente et seul le profil actif change.
        """
        self.settings_manager.set_active_profile_id(profile_id)
        self._initialize_api_client()
        profile = self.settings_manager.get_active_profile()
        name = profile.name if profile else "?"

        if self.current_conversation_id and len(self.current_messages) == 0:
            self.db_manager.set_conversation_profile_id(
                self.current_conversation_id, profile_id
            )
            self.logger.debug(
                f"[CONTROLLER] Conv {self.current_conversation_id} (vide) "
                f"re-liée au profil {profile_id!r}"
            )

        self.status_changed.emit(f"Profil API changé : {name}")

    def get_active_temperature(self) -> float:
        """Retourne la température du profil actif."""
        profile = self.settings_manager.get_active_profile()
        return profile.temperature if profile else 0.7

    def get_active_max_tokens(self) -> Optional[int]:
        """Retourne le max_tokens du profil actif."""
        profile = self.settings_manager.get_active_profile()
        return profile.max_tokens if profile else None
    
    # === GESTION DES CONVERSATIONS ===
    
    def create_new_conversation(self, title: Optional[str] = None) -> int:
        """
        Crée une nouvelle conversation.

        Le profil API attaché est toujours le profil "par défaut" configuré dans
        les paramètres. Le profil actif est basculé sur ce défaut pour que l'UI
        le reflète immédiatement. Tant que la session reste vide, l'utilisateur
        peut changer de profil via le sélecteur (cf. switch_profile), et la
        liaison sera mise à jour ; le choix devient permanent au premier message.

        Args:
            title: Titre de la conversation (généré auto si None)

        Returns:
            ID de la nouvelle conversation
        """
        try:
            if not title:
                title = "New session"

            default_profile = self.settings_manager.get_default_profile()
            profile_id = default_profile.profile_id if default_profile else None

            if default_profile and \
                    self.settings_manager.get_active_profile_id() != default_profile.profile_id:
                self.switch_profile(default_profile.profile_id)

            conv_id = self.db_manager.create_conversation(title, api_profile_id=profile_id)
            self.current_conversation_id = conv_id
            self.current_messages = []

            self.logger.debug(
                f"[CONTROLLER] Nouvelle conversation créée: ID {conv_id} "
                f"(profil défaut={profile_id!r})"
            )

            # Mise à jour de la liste
            self.refresh_conversations_list()

            return conv_id

        except Exception as e:
            self.logger.error(f"[CONTROLLER] Création conversation", exc_info=True)
            self.error_occurred.emit(f"Erreur lors de la création: {str(e)}")
            return -1
    
    def load_conversation(self, conv_id: int):
        """
        Charge une conversation existante.

        Args:
            conv_id: ID de la conversation à charger
        """
        try:
            conv_data = self.db_manager.get_conversation_with_messages(conv_id)

            if conv_data:
                self.current_conversation_id = conv_id
                # IMPORTANT: Faire une copie pour éviter le partage de référence
                self.current_messages = [msg.copy() for msg in conv_data['messages']]

                self.logger.debug(f"[CONTROLLER] Conversation {conv_id} chargée: "
                                f"{len(self.current_messages)} messages")

                # Restaurer le profil API lié à cette conversation
                self._restore_conversation_profile(conv_id)

                self.conversation_loaded.emit(conv_data)
            else:
                self.error_occurred.emit(f"Conversation {conv_id} introuvable")
        
        except Exception as e:
            self.logger.error(f"[CONTROLLER] Chargement conversation", exc_info=True)
            self.error_occurred.emit(f"Erreur lors du chargement: {str(e)}")
    
    def _restore_conversation_profile(self, conv_id: int):
        """Restaure le profil API associé à une conversation, avec fallback sur le profil par défaut."""
        stored_id = self.db_manager.get_conversation_profile_id(conv_id)
        profiles = self.settings_manager.get_profiles()
        known_ids = {p.profile_id for p in profiles}

        self.logger.debug(
            f"[CONTROLLER] Restauration profil conv {conv_id}: "
            f"stored={stored_id!r}, known={len(known_ids)}, "
            f"active={self.settings_manager.get_active_profile_id()!r}"
        )

        if stored_id and stored_id in known_ids:
            # Profil connu → basculer si différent du profil actif
            if stored_id != self.settings_manager.get_active_profile_id():
                self.logger.debug(f"[CONTROLLER] Bascule vers profil {stored_id!r}")
                self.switch_profile(stored_id)
        else:
            default = self.settings_manager.get_default_profile()
            if default:
                # Profil supprimé OU jamais lié → persister le défaut en DB
                self.db_manager.set_conversation_profile_id(conv_id, default.profile_id)
                self.logger.debug(
                    f"[CONTROLLER] Conv {conv_id} re-liée au profil par défaut "
                    f"{default.profile_id!r} (ancien={stored_id!r})"
                )
                if default.profile_id != self.settings_manager.get_active_profile_id():
                    self.switch_profile(default.profile_id)

    def delete_conversations(self, conv_ids: List[int]):
        """
        Supprime plusieurs conversations.
        
        Args:
            conv_ids: Liste des IDs à supprimer
        """
        try:
            for conv_id in conv_ids:
                self.db_manager.delete_conversation(conv_id)
                
                # Si c'était la conversation courante, réinitialiser
                if conv_id == self.current_conversation_id:
                    self.current_conversation_id = None
                    self.current_messages = []
            
            self.logger.debug(f"[CONTROLLER] {len(conv_ids)} conversation(s) supprimée(s)")
            
            # Mise à jour de la liste
            self.refresh_conversations_list()
            self.status_changed.emit(f"{len(conv_ids)} conversation(s) supprimée(s)")
        
        except Exception as e:
            self.logger.error(f"[CONTROLLER] Suppression conversations", exc_info=True)
            self.error_occurred.emit(f"Erreur lors de la suppression: {str(e)}")
    
    def refresh_conversations_list(self):
        """Rafraîchit la liste des conversations."""
        try:
            conversations = self.db_manager.get_all_conversations()
            self.conversations_list_updated.emit(conversations)
            self.logger.debug(f"[CONTROLLER] Liste mise à jour: {len(conversations)} conversation(s)")
        
        except Exception as e:
            self.logger.error(f"[CONTROLLER] Rafraîchissement liste", exc_info=True)
    
    # === GESTION DES MESSAGES ===
    
    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Estime le nombre de tokens (~4 caractères par token)."""
        return max(1, len(text) // 4) if text else 0

    def send_message(self, user_message: str):
        """
        Envoie un message et déclenche la réponse de l'API.

        Args:
            user_message: Message de l'utilisateur
        """
        if not self.api_client:
            self.error_occurred.emit("Client API non initialisé. Vérifiez vos paramètres.")
            return

        is_first_message = not self.current_conversation_id or len(self.current_messages) == 0

        if not self.current_conversation_id:
            title = self._generate_title_from_message(user_message)
            self.create_new_conversation(title)
        elif len(self.current_messages) == 0:
            new_title = self._generate_title_from_message(user_message)
            self.db_manager.update_conversation_title(self.current_conversation_id, new_title)
            self.refresh_conversations_list()
            self.logger.debug(f"[CONTROLLER] Titre mis à jour: '{new_title}'")

        if is_first_message and self.current_conversation_id:
            active = self.settings_manager.get_active_profile()
            if active:
                self.db_manager.set_conversation_profile_id(
                    self.current_conversation_id, active.profile_id
                )
                self.logger.debug(
                    f"[CONTROLLER] Conv {self.current_conversation_id} liée "
                    f"au profil actif {active.profile_id!r} (premier message)"
                )

        try:
            tokens = self._estimate_tokens(user_message)
            self.db_manager.add_message(
                self.current_conversation_id,
                'user',
                user_message,
                tokens
            )

            self.current_messages.append({
                'role': 'user',
                'content': user_message
            })

            self.logger.debug(f"[CONTROLLER] Message utilisateur ajouté (~{tokens} tokens)")

        except Exception as e:
            self.logger.error(f"[CONTROLLER] Envoi message", exc_info=True)
            self.error_occurred.emit(f"Erreur lors de l'envoi: {str(e)}")
    
    def save_assistant_message(self, content: str):
        """
        Sauvegarde la réponse complète de l'assistant.

        Args:
            content: Contenu de la réponse
        """
        try:
            if self.current_conversation_id:
                tokens = self._estimate_tokens(content)
                self.db_manager.add_message(
                    self.current_conversation_id,
                    'assistant',
                    content,
                    tokens
                )

                self.current_messages.append({
                    'role': 'assistant',
                    'content': content
                })

                self.logger.debug(f"[CONTROLLER] Réponse assistant sauvegardée (~{tokens} tokens)")

        except Exception as e:
            self.logger.error(f"[CONTROLLER] Sauvegarde réponse", exc_info=True)
    
    def _generate_title_from_message(self, message: str, max_length: int = AUTO_TITLE_MAX_LENGTH) -> str:
        """Génère un titre de conversation à partir du premier message (fallback sans API)."""
        title = message.strip()
        if len(title) > max_length:
            title = title[:max_length] + "..."
        return title if title else "New session"
    
    # === GESTION DES PARAMÈTRES ===
    
    def update_api_settings(
        self,
        api_key: str,
        base_url: str,
        model: str,
        verify_ssl: bool
    ):
        """
        Met à jour les paramètres de l'API.
        
        Args:
            api_key: Clé API
            base_url: URL de base
            model: Modèle à utiliser
            verify_ssl: Vérification SSL
        """
        try:
            self.settings_manager.set_api_key(api_key)
            self.settings_manager.set_base_url(base_url)
            self.settings_manager.set_model(model)
            self.settings_manager.set_verify_ssl(verify_ssl)
            
            # Réinitialiser le client API
            self._initialize_api_client()
            
            self.logger.debug("[CONTROLLER] Paramètres API mis à jour")
            self.status_changed.emit("Paramètres API sauvegardés")
        
        except Exception as e:
            self.logger.error(f"[CONTROLLER] Mise à jour paramètres", exc_info=True)
            self.error_occurred.emit(f"Erreur lors de la sauvegarde: {str(e)}")
    
    def test_api_connection(self) -> tuple[bool, str]:
        """
        Test la connexion à l'API.
        
        Returns:
            (success: bool, message: str)
        """
        if not self.api_client:
            return False, "Client API non initialisé"
        
        return self.api_client.test_connection()
    
    # === EXPORT ===
    
    def export_conversations(
        self,
        format_type: str,
        filepath: str,
        conversation_ids: Optional[List[int]] = None
    ) -> tuple[bool, str]:
        """
        Exporte les conversations.
        
        Args:
            format_type: 'json' ou 'markdown'
            filepath: Chemin du fichier de sortie
            conversation_ids: IDs à exporter (None = toutes)
        
        Returns:
            (success: bool, message: str)
        """
        try:
            conversations = self.export_manager.prepare_conversations_for_export(
                self.db_manager,
                conversation_ids
            )
            
            if not conversations:
                return False, "Aucune conversation à exporter"
            
            if format_type.lower() == 'json':
                return self.export_manager.export_conversations_json(
                    conversations,
                    filepath
                )
            elif format_type.lower() == 'markdown':
                return self.export_manager.export_conversations_markdown(
                    conversations,
                    filepath
                )
            else:
                return False, f"Format inconnu: {format_type}"
        
        except Exception as e:
            self.logger.error(f"[CONTROLLER] Export", exc_info=True)
            return False, f"Erreur lors de l'export: {str(e)}"
    
    # === CLEANUP ===
    
    def cleanup(self):
        """Nettoyage lors de la fermeture de l'application."""
        try:
            if self.api_client:
                self.api_client.close()
            
            self.db_manager.close()
            self.logger.debug("[CONTROLLER] Nettoyage effectué")
        
        except Exception as e:
            self.logger.error(f"[CONTROLLER] Cleanup", exc_info=True)
