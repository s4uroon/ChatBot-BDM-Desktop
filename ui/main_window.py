"""
ui/main_window.py
=================
Fenêtre principale de l'application
"""

from typing import Optional
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QMenuBar, QMenu, QFileDialog, QMessageBox, QStatusBar,
    QComboBox, QPushButton, QLabel
)
from PyQt6.QtCore import Qt, QTimer, QMutex
from PyQt6.QtGui import QAction, QKeySequence, QKeyEvent, QShortcut, QIcon
from .sidebar_widget import SidebarWidget
from .chat_widget import ChatWidget
from .input_widget import InputWidget, estimate_tokens
from .settings_dialog import SettingsDialog
from workers.api_worker import APIWorker
from workers.title_worker import TitleWorker
from core.main_controller import MainController
from core.logger import get_logger
from core.paths import get_icon_path
from core.constants import APP_NAME, APP_VERSION, APP_CREATOR, WORKER_WAIT_TIMEOUT_MS
from utils.logo_utils import get_logo_base64


class MainWindow(QMainWindow):
    """
    Fenêtre principale de l'application Chatbot Desktop.
    
    Architecture:
    - Sidebar gauche: Historique conversations
    - Zone centrale: Chat + Input
    - Menus: Fichier, Paramètres, Aide
    """
    
    def __init__(self, db_path: Optional[str] = None, settings_file: Optional[str] = None):
        """
        Initialise la fenêtre principale.

        Args:
            db_path: Chemin de la base de données (optionnel)
            settings_file: Chemin du fichier de configuration (optionnel)
        """
        super().__init__()
        self.logger = get_logger()

        # Contrôleur
        self.controller = MainController(db_path=db_path, settings_file=settings_file)

        # Worker API (sera créé à chaque requête)
        self.api_worker: APIWorker = None
        self.title_worker: TitleWorker = None
        self.current_response = ""
        self.response_mutex = QMutex()  # Protection thread-safe pour current_response

        self.setWindowTitle("ChatBot BDM Desktop")
        self.resize(1200, 800)

        # Configuration de l'icône de la fenêtre
        try:
            icon_path = get_icon_path()
            if Path(icon_path).exists():
                self.setWindowIcon(QIcon(icon_path))
                self.logger.debug(f"[MAIN_WINDOW] Icône de la fenêtre chargée: {icon_path}")
            else:
                self.logger.warning(f"[MAIN_WINDOW] Fichier d'icône introuvable: {icon_path}")
        except Exception as e:
            self.logger.warning(f"[MAIN_WINDOW] Impossible de charger l'icône: {e}")

        self.setup_ui()
        self.setup_menus()
        self.setup_shortcuts()
        self.connect_signals()
        self.load_initial_data()

        self.logger.debug("[MAIN_WINDOW] Fenêtre principale initialisée")
    
    def setup_ui(self):
        """Initialise l'interface utilisateur."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Splitter horizontal (sidebar | zone centrale)
        self.sidebar_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Sidebar
        self.sidebar = SidebarWidget()
        self.sidebar.search_requested.connect(self._on_search_in_messages)
        self.sidebar_splitter.addWidget(self.sidebar)

        # Zone centrale (Chat + Input) avec splitter vertical redimensionnable
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(5, 5, 5, 5)

        # Barre de sélection de profil API
        profile_bar = QHBoxLayout()
        profile_bar.setContentsMargins(0, 0, 0, 4)
        profile_bar.setSpacing(6)

        profile_label = QLabel("Profil API :")
        profile_label.setStyleSheet("color: #909090; font-size: 11px;")
        profile_bar.addWidget(profile_label)

        self.profile_combo = QComboBox()
        self.profile_combo.setFixedWidth(200)
        self.profile_combo.setToolTip("Sélectionner le profil API actif")
        self.profile_combo.setStyleSheet("font-size: 12px;")
        profile_bar.addWidget(self.profile_combo)

        manage_profiles_btn = QPushButton("⚙ Gérer")
        manage_profiles_btn.setFixedWidth(80)
        manage_profiles_btn.setToolTip("Gérer les profils API")
        manage_profiles_btn.clicked.connect(self._on_manage_profiles)
        manage_profiles_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                padding: 2px 6px;
            }
        """)
        profile_bar.addWidget(manage_profiles_btn)
        profile_bar.addStretch()

        center_layout.addLayout(profile_bar)

        # Splitter vertical entre chat et input
        self.chat_input_splitter = QSplitter(Qt.Orientation.Vertical)

        # Récupérer le thème Highlight.js depuis les settings
        hljs_theme = self.controller.settings_manager.get_hljs_theme()
        self.chat_widget = ChatWidget(hljs_theme=hljs_theme)
        self.chat_input_splitter.addWidget(self.chat_widget)

        self.input_widget = InputWidget()
        self.chat_input_splitter.addWidget(self.input_widget)

        # Le chat prend la majorité de l'espace, l'input reste plus petit
        self.chat_input_splitter.setStretchFactor(0, 1)  # Chat extensible
        self.chat_input_splitter.setStretchFactor(1, 0)  # Input taille minimale

        # Restaurer les tailles sauvegardées par l'utilisateur
        saved_sizes = self.controller.settings_manager.get_chat_splitter_sizes()
        if saved_sizes:
            self.chat_input_splitter.setSizes(saved_sizes)

        # Sauvegarder automatiquement quand l'utilisateur déplace le splitter
        self.chat_input_splitter.splitterMoved.connect(self._on_chat_splitter_moved)

        center_layout.addWidget(self.chat_input_splitter)

        self.sidebar_splitter.addWidget(center_widget)

        # Tailles du splitter sidebar
        self.sidebar_splitter.setStretchFactor(0, 0)  # Sidebar fixe
        self.sidebar_splitter.setStretchFactor(1, 1)  # Centre extensible

        # Restaurer la position sauvegardée ou utiliser les valeurs par défaut
        saved_sidebar_sizes = self.controller.settings_manager.get_sidebar_splitter_sizes()
        if saved_sidebar_sizes:
            self.sidebar_splitter.setSizes(saved_sidebar_sizes)
        else:
            self.sidebar_splitter.setSizes([190, 1010])

        # Sauvegarder automatiquement quand l'utilisateur déplace le splitter sidebar
        self.sidebar_splitter.splitterMoved.connect(self._on_sidebar_splitter_moved)

        main_layout.addWidget(self.sidebar_splitter)
        
        # Barre de statut
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def setup_menus(self):
        """Configure les menus."""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("📝 New Session", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self._on_new_conversation)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("💾 Export...", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self._on_export)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("❌ Quit", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Menu Paramètres
        settings_menu = menubar.addMenu("&Settings")
        
        config_action = QAction("⚙️ Configuration...", self)
        config_action.setShortcut(QKeySequence("Ctrl+,"))
        config_action.triggered.connect(self._on_settings)
        settings_menu.addAction(config_action)
        
        # Menu Aide
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("ℹ️ About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def setup_shortcuts(self):
        """Configure les raccourcis clavier globaux."""
        # Escape pour annuler le streaming
        escape_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        escape_shortcut.activated.connect(self._on_cancel_streaming)

        # Ctrl+F pour focus sur la recherche
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self._on_focus_search)

    # === TAGS ===

    def _refresh_tags(self):
        """Rafraîchit la liste des tags dans la sidebar."""
        tags = self.controller.tag_manager.get_all_tags()
        self.sidebar.load_tags(tags)

    def _on_tag_filter_changed(self, tag_id: int):
        """Filtre les conversations par tag."""
        if tag_id == -1:
            self.controller.refresh_conversations_list()
        else:
            conversations = self.controller.tag_manager.get_conversations_by_tag(tag_id)
            self.sidebar.load_conversations(conversations)

    def _on_tag_conversation(self, conversation_id: int, tag_id: int):
        """Ajoute un tag à une conversation."""
        self.controller.tag_manager.add_tag_to_conversation(conversation_id, tag_id)
        tags = self.controller.tag_manager.get_conversation_tags(conversation_id)
        self.sidebar.set_conversation_tags(conversation_id, tags)

    def _on_untag_conversation(self, conversation_id: int, tag_id: int):
        """Retire un tag d'une conversation."""
        self.controller.tag_manager.remove_tag_from_conversation(conversation_id, tag_id)
        tags = self.controller.tag_manager.get_conversation_tags(conversation_id)
        self.sidebar.set_conversation_tags(conversation_id, tags)

    def _on_create_tag(self, name: str, color: str):
        """Crée un nouveau tag."""
        self.controller.tag_manager.create_tag(name, color)
        self._refresh_tags()
        self.status_bar.showMessage(f"Tag '{name}' created", 3000)

    def _on_delete_tag(self, tag_id: int):
        """Supprime un tag."""
        self.controller.tag_manager.delete_tag(tag_id)
        self._refresh_tags()
        self.status_bar.showMessage("Tag deleted", 3000)

    # === DRAFT ===

    def _on_draft_changed(self):
        """Déclenche la sauvegarde du brouillon avec debounce."""
        self._draft_save_timer.stop()
        self._draft_save_timer.start()

    def _save_draft(self):
        """Sauvegarde le brouillon dans les settings."""
        text = self.input_widget.text_edit.toPlainText()
        self.controller.settings_manager.set_draft(text)

    def _start_title_worker(self, conversation_id: int, user_message: str):
        """Lance le worker de génération de titre en arrière-plan."""
        try:
            # Nettoyer un éventuel ancien title worker
            if self.title_worker and self.title_worker.isRunning():
                self.title_worker.wait(2000)

            self.title_worker = TitleWorker(
                self.controller.api_client,
                conversation_id,
                user_message
            )
            self.title_worker.title_generated.connect(self._on_title_generated)
            self.title_worker.start()
            self.logger.debug(f"[MAIN_WINDOW] Title worker lancé pour conversation {conversation_id}")
        except Exception as e:
            self.logger.warning(f"[MAIN_WINDOW] Erreur lancement title worker: {e}")

    def _on_title_generated(self, conversation_id: int, title: str):
        """Callback quand un titre est généré par l'API."""
        try:
            self.controller.db_manager.update_conversation_title(conversation_id, title)
            self.controller.refresh_conversations_list()
            self.logger.debug(f"[MAIN_WINDOW] Titre auto-généré: '{title}' pour conversation {conversation_id}")
        except Exception as e:
            self.logger.warning(f"[MAIN_WINDOW] Erreur mise à jour titre auto: {e}")

    def _on_chat_splitter_moved(self, pos: int, index: int):
        """Sauvegarde la position du splitter chat/input quand l'utilisateur le déplace."""
        sizes = self.chat_input_splitter.sizes()
        self.controller.settings_manager.set_chat_splitter_sizes(sizes)

    def _on_sidebar_splitter_moved(self, pos: int, index: int):
        """Sauvegarde la position du splitter sidebar/centre quand l'utilisateur le déplace."""
        sizes = self.sidebar_splitter.sizes()
        self.controller.settings_manager.set_sidebar_splitter_sizes(sizes)

    def _on_cancel_streaming(self):
        """Annule le streaming en cours si actif."""
        if self.api_worker and self.api_worker.isRunning():
            self.logger.debug("[MAIN_WINDOW] Annulation du streaming par l'utilisateur")
            self.api_worker.stop()
            # La réponse partielle sera émise via response_complete par le worker
            self.status_bar.showMessage("⏹ Arrêt de la génération...", 2000)

    def _on_focus_search(self):
        """Donne le focus à la barre de recherche."""
        self.sidebar.search_input.setFocus()
        self.sidebar.search_input.selectAll()

    def connect_signals(self):
        """Connecte les signaux entre composants."""
        # Sidebar
        self.sidebar.conversation_selected.connect(self._on_conversation_selected)
        self.sidebar.new_conversation_requested.connect(self._on_new_conversation)
        self.sidebar.delete_conversations_requested.connect(self._on_delete_conversations)
        self.sidebar.rename_conversation_requested.connect(self._on_rename_conversation)
        self.sidebar.tag_filter_changed.connect(self._on_tag_filter_changed)
        self.sidebar.tag_conversation_requested.connect(self._on_tag_conversation)
        self.sidebar.untag_conversation_requested.connect(self._on_untag_conversation)
        self.sidebar.create_tag_requested.connect(self._on_create_tag)
        self.sidebar.delete_tag_requested.connect(self._on_delete_tag)

        # Input
        self.input_widget.message_submitted.connect(self._on_message_submitted)
        self.input_widget.stop_generation_requested.connect(self._on_cancel_streaming)
        self.input_widget.text_edit.textChanged.connect(self._on_draft_changed)

        # Timer debounce pour sauvegarde du brouillon (500ms)
        self._draft_save_timer = QTimer()
        self._draft_save_timer.setSingleShot(True)
        self._draft_save_timer.setInterval(500)
        self._draft_save_timer.timeout.connect(self._save_draft)

        # Profil combo
        self.profile_combo.currentIndexChanged.connect(self._on_profile_combo_changed)

        # Contrôleur
        self.controller.conversation_loaded.connect(self._on_conversation_loaded)
        self.controller.conversations_list_updated.connect(self._on_conversations_list_updated)
        self.controller.error_occurred.connect(self._on_error)
        self.controller.status_changed.connect(self._on_status_changed)
    
    def load_initial_data(self):
        """Charge les données initiales."""
        self.controller.refresh_conversations_list()

        # Charger les tags
        self._refresh_tags()

        # Charger les profils dans le combo
        self._refresh_profile_combo()

        # Restaurer le brouillon sauvegardé
        draft = self.controller.settings_manager.get_draft()
        if draft:
            self.input_widget.text_edit.setPlainText(draft)
            self.logger.debug(f"[MAIN_WINDOW] Brouillon restauré ({len(draft)} chars)")
    
    # === GESTION DES CONVERSATIONS ===
    
    def _on_new_conversation(self):
        """Crée une nouvelle conversation."""
        # Réinitialiser la recherche
        self.sidebar.clear_search()
        
        conv_id = self.controller.create_new_conversation()
        if conv_id > 0:
            self.sidebar.select_conversation(conv_id)
            # Déclencher le pipeline complet : _restore_conversation_profile + _refresh_profile_combo
            self.controller.load_conversation(conv_id)
            self.input_widget.set_focus()
            self.status_bar.showMessage("New session created")
    
    def _on_conversation_selected(self, conv_id: int):
        """Charge une conversation sélectionnée."""
        self.controller.load_conversation(conv_id)
    
    def _on_conversation_loaded(self, conv_data: dict):
        """Affiche une conversation chargée."""
        messages = conv_data.get('messages', [])
        self.chat_widget.load_conversation(messages)

        # Synchroniser le combo de profil avec le profil restauré
        self._refresh_profile_combo()

        total_tokens = self._calculate_conversation_tokens(messages)
        msg_count = len(messages)
        token_str = self._build_token_status(total_tokens)

        self.status_bar.showMessage(
            f"Session '{conv_data['title']}' loaded | {msg_count} messages | {token_str}"
        )
    
    def _on_delete_conversations(self, conv_ids: list):
        """Supprime des conversations."""
        self.controller.delete_conversations(conv_ids)
        self.chat_widget.clear_conversation()

    def _on_rename_conversation(self, conv_id: int, new_title: str):
        """Renomme une conversation."""
        success = self.controller.db_manager.update_conversation_title(conv_id, new_title)
        if success:
            self.controller.refresh_conversations_list()
            self.status_bar.showMessage(f"Session renamed to '{new_title}'", 3000)
        else:
            QMessageBox.warning(self, "Error", "Failed to rename the session.")
    
    def _on_conversations_list_updated(self, conversations: list):
        """Met à jour la liste des conversations."""
        self.sidebar.load_conversations(conversations)

        # Mettre à jour le cache des tags pour chaque conversation visible
        for conv in conversations:
            tags = self.controller.tag_manager.get_conversation_tags(conv['id'])
            self.sidebar.set_conversation_tags(conv['id'], tags)
    
    def _on_search_in_messages(self, query: str):
        """Recherche dans les messages des conversations."""
        if not query:
            # Recherche vide, recharger tout
            self.controller.refresh_conversations_list()
            return
        
        # Rechercher dans la base de données (titre + contenu des messages)
        results = self.controller.db_manager.search_conversations(query)
        self.sidebar.load_conversations(results)
        self.status_bar.showMessage(f"Search: {len(results)} result(s)", 3000)
    
    # === GESTION DES MESSAGES ===
    
    def _on_message_submitted(self, message: str):
        """Traite l'envoi d'un message utilisateur."""
        # Effacer le brouillon
        self.controller.settings_manager.set_draft('')

        # Ajouter le message à l'affichage
        self.chat_widget.append_message('user', message)

        # Sauvegarder dans la BD via le contrôleur
        self.controller.send_message(message)

        # Désactiver l'input pendant le traitement
        self.input_widget.set_enabled(False)
        self.status_bar.showMessage("⏳ Generating response...")

        # Démarrer le worker API
        self._start_api_worker()
    
    def _start_api_worker(self):
        """Démarre le worker pour le streaming API."""
        if not self.controller.api_client:
            self._on_error("API Client not initialized. Check your settings.")
            self.input_widget.set_enabled(True)
            return
        
        self.logger.debug("[MAIN_WINDOW] ===== DÉMARRAGE REQUÊTE API =====")
        
        # Préparer les messages pour l'API
        messages = self.controller.current_messages
        self.logger.debug(f"[MAIN_WINDOW] Nombre de messages dans le contexte: {len(messages)}")

        # Afficher l'indicateur de frappe animé
        self.chat_widget.show_typing_indicator()

        # Créer le worker
        self.api_worker = APIWorker(
            api_client=self.controller.api_client,
            messages=messages,
            temperature=self.controller.get_active_temperature(),
            max_tokens=self.controller.get_active_max_tokens(),
        )
        
        # Connecter les signaux
        self.api_worker.chunk_received.connect(self._on_chunk_received)
        self.api_worker.response_complete.connect(self._on_response_complete)
        self.api_worker.error_occurred.connect(self._on_api_error)
        self.api_worker.finished.connect(self._on_worker_finished)
        
        # Démarrer
        self.current_response = ""
        self.api_worker.start()
        self.logger.debug("[MAIN_WINDOW] Worker API démarré")
    
    def _on_chunk_received(self, chunk: str):
        """Reçoit un chunk du streaming - ACCUMULATION SANS AFFICHAGE."""
        # Protection thread-safe de l'accumulation
        self.response_mutex.lock()
        try:
            self.current_response += chunk
            current_length = len(self.current_response)
        finally:
            self.response_mutex.unlock()

        # Ne pas afficher pendant le streaming - on attend la fin
        self.logger.debug(f"[MAIN_WINDOW] Chunk reçu, taille totale: {current_length} chars")
    
    def _cleanup_worker(self):
        """Nettoie le worker API de manière thread-safe."""
        if self.api_worker:
            if self.api_worker.is_running():
                self.logger.debug("[MAIN_WINDOW] Arrêt du worker en cours...")
                self.api_worker.stop()
                if not self.api_worker.wait(WORKER_WAIT_TIMEOUT_MS):
                    self.logger.warning("[MAIN_WINDOW] Worker n'a pas terminé dans le délai imparti, terminaison forcée")
                    self.api_worker.terminate()
                    self.api_worker.wait(2000)
            self.api_worker = None
            self.logger.debug("[MAIN_WINDOW] Worker nettoyé")

    def _on_response_complete(self, full_response: str):
        """Réponse complète reçue - MAINTENANT ON AFFICHE."""
        self.logger.debug("[MAIN_WINDOW] ===== RÉPONSE COMPLÈTE REÇUE =====")
        self.logger.debug(f"[MAIN_WINDOW] Taille: {len(full_response)} caractères")

        # Cacher l'indicateur de frappe
        self.chat_widget.hide_typing_indicator()

        # Sauvegarder dans la BD
        self.controller.save_assistant_message(full_response)

        # MAINTENANT afficher le message assistant complet
        self.logger.debug("[MAIN_WINDOW] Ajout du message assistant au chat widget")
        self.chat_widget.append_message('assistant', full_response)

        self.logger.debug("[MAIN_WINDOW] Message ajouté, le scroll sera géré automatiquement par chat_widget")

        total_tokens = self._calculate_conversation_tokens(self.controller.current_messages)
        msg_count = len(self.controller.current_messages)
        token_str = self._build_token_status(total_tokens)
        self.status_bar.showMessage(
            f"✅ Response generated | {msg_count} messages | {token_str}", 5000
        )

        # Auto-titrage : si c'est la première réponse (2 messages : user + assistant)
        if (len(self.controller.current_messages) == 2
                and self.controller.api_client
                and self.controller.current_conversation_id):
            first_user_msg = self.controller.current_messages[0].get('content', '')
            self._start_title_worker(self.controller.current_conversation_id, first_user_msg)

    def _on_worker_finished(self):
        """
        Appelé automatiquement par QThread.finished quand run() retourne, quelle
        que soit la cause (succès, erreur, arrêt utilisateur — y compris arrêt
        avant le 1er chunk). Source unique de vérité pour la remise à zéro de l'UI.
        """
        try:
            self.chat_widget.hide_typing_indicator()
        except Exception as e:
            self.logger.warning(f"[MAIN_WINDOW] Erreur lors du masquage de l'indicateur: {e}")

        self.input_widget.set_enabled(True)
        self.input_widget.set_focus()

        # Le thread est terminé : on peut lâcher la référence sans wait()
        self.api_worker = None

        self.response_mutex.lock()
        try:
            self.current_response = ""
        finally:
            self.response_mutex.unlock()

        self.logger.debug("[MAIN_WINDOW] Worker terminé, UI réinitialisée")

    def _on_api_error(self, error_msg: str):
        """Erreur lors de l'appel API."""
        try:
            self.chat_widget.hide_typing_indicator()
        except Exception as e:
            self.logger.warning(f"[MAIN_WINDOW] Erreur lors du masquage de l'indicateur: {e}")
        self._on_error(error_msg)
    
    # === GESTION DES PROFILS API ===

    def _refresh_profile_combo(self):
        """Met à jour le QComboBox des profils sans déclencher le signal."""
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        profiles = self.controller.settings_manager.get_profiles()
        active_id = self.controller.settings_manager.get_active_profile_id()
        for p in profiles:
            self.profile_combo.addItem(p.name, p.profile_id)
        idx = self.profile_combo.findData(active_id)
        if idx >= 0:
            self.profile_combo.setCurrentIndex(idx)
        self.profile_combo.blockSignals(False)

    def _on_profile_combo_changed(self, index: int):
        """Bascule vers le profil sélectionné."""
        profile_id = self.profile_combo.currentData()
        if profile_id:
            self.controller.switch_profile(profile_id)

    def _on_manage_profiles(self):
        """Ouvre le dialog de gestion des profils."""
        from .profile_manager_dialog import ProfileManagerDialog
        dlg = ProfileManagerDialog(self.controller.settings_manager, self)
        dlg.profiles_updated.connect(self._on_profiles_updated)
        dlg.exec()

    def _on_profiles_updated(self):
        """Rafraîchit le client et le combo après modification des profils."""
        self.controller._initialize_api_client()
        self._refresh_profile_combo()

    # === MENUS ===

    def _on_export(self):
        """Ouvre le dialogue d'export."""
        selected_ids = self.sidebar.get_selected_conversation_ids()
        
        if not selected_ids and self.controller.db_manager.get_conversation_count() == 0:
            QMessageBox.information(
                self,
                "No Sessions",
                "There are no sessions to export."
            )
            return
        
        # Dialogue de choix
        msg = QMessageBox()
        msg.setWindowTitle("Export Sessions")
        msg.setText("What do you want to export?")
        
        if selected_ids:
            selected_btn = msg.addButton(
                f"Selection ({len(selected_ids)} session(s))",
                QMessageBox.ButtonRole.ActionRole
            )
        else:
            selected_btn = None
        
        all_btn = msg.addButton("All sessions", QMessageBox.ButtonRole.ActionRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        
        msg.exec()
        
        if msg.clickedButton() == cancel_btn:
            return
        
        # Déterminer quoi exporter
        export_ids = selected_ids if msg.clickedButton() == selected_btn else None
        
        # Choix du format
        format_choice = QMessageBox.question(
            self,
            "Format d'export",
            "Quel format souhaitez-vous ?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel
        )
        
        if format_choice == QMessageBox.StandardButton.Cancel:
            return
        
        # Dialogue de sauvegarde
        filters = "JSON (*.json);;Markdown (*.md)"
        filepath, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Exporter les conversations",
            "",
            filters
        )
        
        if not filepath:
            return
        
        # Déterminer le format
        format_type = 'json' if 'json' in selected_filter.lower() else 'markdown'
        
        # Exporter
        success, message = self.controller.export_conversations(
            format_type,
            filepath,
            export_ids
        )
        
        if success:
            QMessageBox.information(self, "Export réussi", message)
        else:
            QMessageBox.critical(self, "Erreur d'export", message)
    
    def _on_settings(self):
        """Ouvre le dialogue de paramètres."""
        dialog = SettingsDialog(
            self.controller.settings_manager,
            self.controller.api_client,
            self
        )
        dialog.settings_saved.connect(self._on_settings_saved)
        dialog.exec()
    
    def _on_settings_saved(self, settings: dict):
        """Paramètres d'apparence sauvegardés."""
        if 'hljs_theme' in settings:
            self.chat_widget.set_hljs_theme(settings['hljs_theme'])

        if 'colors' in settings and settings['colors']:
            self.chat_widget.set_custom_colors(settings['colors'])

        self.status_bar.showMessage("✅ Paramètres mis à jour", 3000)

    def _on_about(self):
        """Affiche la fenêtre À propos."""
        logo_src = get_logo_base64()
        logo_img = f"<img src='{logo_src}' width='32' height='32' style='vertical-align: middle; margin-right: 10px;'/>" if logo_src else "🤖"

        about_text = (
            f"<div style='font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, Oxygen-Sans, Ubuntu, Cantarell, sans-serif;'>"
            f"  <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 20px;'>"
            f"    <h1 style='margin: 0; font-size: 28px;'>{logo_img} ChatBot BDM Desktop</h1>"
            f"    <p style='margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;'>Professional AI Assistant</p>"
            f"  </div>"
            f"  "
            f"  <div style='padding: 15px; border-radius: 8px; margin-bottom: 15px;'>"
            f"    <p style='margin: 5px 0;'><b>Version:</b> {APP_VERSION}</p>"
            f"    <p style='margin: 5px 0;'><b>Creator:</b> {APP_CREATOR}</p>"
            f"    <p style='margin: 5px 0;'><b>Framework:</b> PyQt6 + Qt WebEngine</p>"
            f"    <p style='margin: 5px 0;'><b>API:</b> OpenAI Compatible</p>"
            f"  </div>"
            f"  "
            f"  <h3 style='color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 5px;'>✨ Core Features</h3>"
            f"  <ul style='line-height: 1.8;'>"
            f"    <li>🚀 <b>Real-time Streaming</b> - Instant response generation</li>"
            f"    <li>💬 <b>Multi-Session Management</b> - Organize multiple conversations</li>"
            f"    <li>🔍 <b>Full-Text Search</b> - Find messages across all sessions</li>"
            f"    <li>✏️ <b>Session Renaming</b> - Customize conversation titles</li>"
            f"    <li>🗑️ <b>Batch Delete</b> - Remove multiple sessions at once</li>"
            f"  </ul>"
            f"  "
            f"  <h3 style='color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 5px;'>🎨 Interface & UX</h3>"
            f"  <ul style='line-height: 1.8;'>"
            f"    <li>🌈 <b>Syntax Highlighting</b> - Powered by Highlight.js</li>"
            f"    <li>🎨 <b>Customizable Themes</b> - Choose from 20+ code themes</li>"
            f"    <li>🎭 <b>Custom Colors</b> - Personalize message appearance</li>"
            f"    <li>⌨️ <b>Keyboard Shortcuts</b> - Boost productivity (Ctrl+N, Ctrl+F, Esc...)</li>"
            f"    <li>📊 <b>Token Counter</b> - Track conversation usage</li>"
            f"    <li>⏸️ <b>Cancel Streaming</b> - Stop responses anytime (Esc)</li>"
            f"  </ul>"
            f"  "
            f"  <h3 style='color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 5px;'>💾 Export & Data</h3>"
            f"  <ul style='line-height: 1.8;'>"
            f"    <li>📄 <b>JSON Export</b> - Machine-readable format</li>"
            f"    <li>📝 <b>Markdown Export</b> - Human-readable documentation</li>"
            f"    <li>📦 <b>Selective Export</b> - Export single or multiple sessions</li>"
            f"    <li>🗄️ <b>SQLite Database</b> - Reliable local storage</li>"
            f"  </ul>"
            f"  "
            f"  <h3 style='color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 5px;'>🔒 Security & Performance</h3>"
            f"  <ul style='line-height: 1.8;'>"
            f"    <li>🔐 <b>SSL/TLS Support</b> - Secure API connections</li>"
            f"    <li>⚡ <b>SSL Bypass Option</b> - For self-signed certificates</li>"
            f"    <li>🛡️ <b>Rate Limiting</b> - API protection</li>"
            f"    <li>🔧 <b>Connection Testing</b> - Verify API settings</li>"
            f"  </ul>"
            f"  "
            f"  <div style='margin-top: 20px; padding: 15px; background: #e8f5e9; border-left: 4px solid #4caf50; border-radius: 5px;'>"
            f"    <p style='margin: 0; color: #2e7d32;'><b>💡 Tip:</b> Press <code>Ctrl+F</code> to search, <code>Ctrl+N</code> for new session, <code>Esc</code> to cancel streaming</p>"
            f"  </div>"
            f"</div>"
        )

        QMessageBox.about(
            self,
            "About ChatBot BDM Desktop",
            about_text
        )
    
    # === UTILITAIRES ===

    def _calculate_conversation_tokens(self, messages: list) -> int:
        """Calcule le nombre total de tokens estimés dans une conversation."""
        total = 0
        for msg in messages:
            content = msg.get('content', '')
            total += estimate_tokens(content)
        return total

    def _build_token_status(self, total_tokens: int) -> str:
        """Retourne une chaîne d'affichage des tokens avec max_tokens si défini sur le profil."""
        profile = self.controller.settings_manager.get_active_profile()
        max_tok = profile.max_tokens if profile and profile.max_tokens else None
        if max_tok:
            pct = int(total_tokens / max_tok * 100)
            return f"~{total_tokens} / {max_tok} tokens ({pct}%)"
        return f"~{total_tokens} tokens"

    def _get_user_friendly_error(self, error_msg: str) -> tuple[str, str]:
        """
        Convertit un message d'erreur technique en message utilisateur avec suggestion.

        Returns:
            tuple[str, str]: (message_principal, suggestion)
        """
        error_lower = error_msg.lower()

        # Erreurs de connexion réseau
        if any(keyword in error_lower for keyword in ['connection', 'connexion', 'timeout', 'unreachable']):
            return (
                "Impossible de se connecter au serveur API",
                "• Vérifiez votre connexion Internet\n"
                "• Vérifiez l'URL du serveur dans les paramètres\n"
                "• Le serveur est peut-être temporairement indisponible"
            )

        # Erreurs d'authentification
        if any(keyword in error_lower for keyword in ['unauthorized', '401', 'api key', 'authentication']):
            return (
                "Erreur d'authentification",
                "• Vérifiez que votre clé API est correcte\n"
                "• La clé a peut-être expiré\n"
                "• Allez dans Paramètres > Connexion pour la mettre à jour"
            )

        # Erreurs de quota/limite
        if any(keyword in error_lower for keyword in ['quota', 'rate limit', 'too many requests', '429']):
            return (
                "Limite de requêtes atteinte",
                "• Vous avez atteint votre quota API\n"
                "• Attendez quelques minutes avant de réessayer\n"
                "• Vérifiez votre plan d'abonnement API"
            )

        # Erreurs SSL
        if any(keyword in error_lower for keyword in ['ssl', 'certificate', 'certificat']):
            return (
                "Erreur de certificat SSL",
                "• Si vous utilisez un serveur avec certificat auto-signé,\n"
                "  désactivez la vérification SSL dans les paramètres\n"
                "• Sinon, le serveur a peut-être un problème de sécurité"
            )

        # Erreur de modèle
        if any(keyword in error_lower for keyword in ['model', 'modèle', 'not found', '404']):
            return (
                "Modèle introuvable",
                "• Vérifiez le nom du modèle dans les paramètres\n"
                "• Le modèle n'est peut-être pas disponible avec votre plan\n"
                "• Exemples: gpt-4, gpt-3.5-turbo, claude-3-opus"
            )

        # Erreur générique
        return (
            "Une erreur s'est produite",
            f"Détails techniques:\n{error_msg}\n\n"
            "Si le problème persiste:\n"
            "• Vérifiez vos paramètres de connexion\n"
            "• Consultez les logs de l'application"
        )

    def _on_error(self, error_msg: str):
        """Affiche une erreur avec message utilisateur amélioré."""
        title, suggestion = self._get_user_friendly_error(error_msg)

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Erreur")
        msg_box.setText(title)
        msg_box.setInformativeText(suggestion)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

        self.status_bar.showMessage(f"❌ {title}", 5000)
    
    def _on_status_changed(self, status_msg: str):
        """Met à jour la barre de statut."""
        self.status_bar.showMessage(status_msg, 3000)
    
    def closeEvent(self, event):
        """Événement de fermeture de la fenêtre."""
        # Vérifier si un streaming est en cours
        if self.api_worker and self.api_worker.is_running():
            reply = QMessageBox.question(
                self,
                "Streaming in Progress",
                "A response is currently being generated.\n\n"
                "Do you really want to quit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return

        # Arrêter le worker si actif
        self._cleanup_worker()

        # Cleanup du contrôleur
        self.controller.cleanup()

        self.logger.debug("[MAIN_WINDOW] Application fermée")
        event.accept()
