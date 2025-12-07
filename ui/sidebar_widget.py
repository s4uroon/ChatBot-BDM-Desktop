"""
ui/sidebar_widget.py
====================
Widget de la barre latérale avec historique des conversations
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
    QPushButton, QListWidgetItem, QLabel, QMessageBox, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime
from typing import List, Optional
from core.logger import get_logger


class ConversationItem(QWidget):
    """
    Widget personnalisé pour afficher une conversation dans la liste.
    Format: Titre (Gras) + Date (Gris, petite ligne)
    """
    
    def __init__(self, conv_id: int, title: str, created_at: str, parent=None):
        super().__init__(parent)
        self.conv_id = conv_id
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(3)
        
        # Titre en gras
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(10)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)
        
        # Date en gris et plus petite
        date_label = QLabel(self._format_date(created_at))
        date_font = QFont()
        date_font.setPointSize(8)
        date_label.setFont(date_font)
        date_label.setStyleSheet("color: #909090;")
        
        layout.addWidget(title_label)
        layout.addWidget(date_label)
    
    def _format_date(self, date_str: str) -> str:
        """Formate la date pour affichage."""
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime('%d/%m/%Y %H:%M')
        except:
            return date_str


class SidebarWidget(QWidget):
    """
    Barre latérale gauche avec historique des conversations.
    
    Fonctionnalités:
    - QListWidget avec sélection multiple (ExtendedSelection)
    - Items personnalisés (Titre + Date)
    - Boutons: Nouvelle conversation, Supprimer
    - Signaux pour communication avec MainWindow
    """
    
    # Signaux émis
    conversation_selected = pyqtSignal(int)  # ID de la conversation sélectionnée
    new_conversation_requested = pyqtSignal()
    delete_conversations_requested = pyqtSignal(list)  # Liste des IDs à supprimer
    search_requested = pyqtSignal(str)  # Terme de recherche
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger()
        self.all_conversations = []  # Stockage de toutes les conversations
        self.setup_ui()
    
    def setup_ui(self):
        """Initialise l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # En-tête (on garde juste pour cohérence, mais le vrai bouton New est en bas)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(5, 5, 5, 5)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Barre de recherche
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(5, 0, 5, 5)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search in sessions...")
        self.search_input.textChanged.connect(self._on_search_changed)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #252525;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 6px;
                color: #e0e0e0;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
        """)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        # Message "No sessions found" juste après la recherche
        self.info_label = QLabel("No sessions found")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("color: #707070; padding: 10px;")
        self.info_label.hide()  # Caché par défaut
        layout.addWidget(self.info_label)
        
        # Liste des conversations avec sélection multiple
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                background-color: #252525;
            }
            QListWidget::item {
                border-bottom: 1px solid #3d3d3d;
                padding: 4px;
                color: #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #2d5f2d;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #2d2d2d;
            }
        """)
        
        layout.addWidget(self.list_widget)
        
        # Boutons en bas : New (gauche) et Delete (droite)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)
        
        # Bouton New à gauche
        new_bottom_btn = QPushButton("➕ New")
        new_bottom_btn.setToolTip("Create a new session (Ctrl+N)")
        new_bottom_btn.clicked.connect(self.new_conversation_requested.emit)
        new_bottom_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        buttons_layout.addWidget(new_bottom_btn)
        
        # Bouton Delete à droite
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setToolTip("Delete selected sessions (Del)")
        delete_btn.clicked.connect(self._on_delete_clicked)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        buttons_layout.addWidget(delete_btn)
        
        layout.addLayout(buttons_layout)
        
        # Label d'information
        self.info_label = QLabel("No sessions")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("color: #707070; padding: 10px;")
        layout.addWidget(self.info_label)
    
    def load_conversations(self, conversations: List[dict]):
        """
        Charge les conversations dans la liste.
        
        Args:
            conversations: Liste de dicts {'id': int, 'title': str, 'created_at': str}
        """
        self.all_conversations = conversations  # Sauvegarder toutes les conversations
        self._display_conversations(conversations)
    
    def _display_conversations(self, conversations: List[dict]):
        """Affiche les conversations filtrées."""
        self.list_widget.clear()
        
        if not conversations:
            self.info_label.setText("No sessions found")
            self.info_label.show()
            self.logger.debug("[SIDEBAR] No sessions to display")
            return
        
        self.info_label.hide()
        
        # Tri par date décroissante (plus récent en premier)
        sorted_convs = sorted(
            conversations,
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )
        
        for conv in sorted_convs:
            self._add_conversation_item(
                conv['id'],
                conv['title'],
                conv['created_at']
            )
        
        self.logger.debug(f"[SIDEBAR] {len(conversations)} conversation(s) affichée(s)")
    
    def _on_search_changed(self, search_text: str):
        """Filtre les conversations selon le texte de recherche."""
        # Émettre le signal pour que MainWindow fasse une vraie recherche en DB
        self.search_requested.emit(search_text)
        self.logger.debug(f"[SIDEBAR] Search requested: '{search_text}'")
    
    def _add_conversation_item(self, conv_id: int, title: str, created_at: str):
        """Ajoute un item de conversation à la liste."""
        item = QListWidgetItem(self.list_widget)
        
        # Widget personnalisé
        widget = ConversationItem(conv_id, title, created_at)
        item.setSizeHint(widget.sizeHint())
        
        # Stockage de l'ID dans les données de l'item
        item.setData(Qt.ItemDataRole.UserRole, conv_id)
        
        self.list_widget.setItemWidget(item, widget)
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """Gère le clic sur un item (sélection simple)."""
        selected_items = self.list_widget.selectedItems()
        
        # Si une seule conversation sélectionnée, émettre le signal
        if len(selected_items) == 1:
            conv_id = item.data(Qt.ItemDataRole.UserRole)
            self.conversation_selected.emit(conv_id)
            self.logger.debug(f"[SIDEBAR] Conversation sélectionnée: ID {conv_id}")
    
    def _on_delete_clicked(self):
        """Gère le clic sur le bouton Supprimer."""
        selected_items = self.list_widget.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select at least one session to delete."
            )
            return
        
        # Confirmation
        count = len(selected_items)
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Do you really want to delete {count} session(s)?\n"
            "This action is irreversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Récupération des IDs
            ids_to_delete = [
                item.data(Qt.ItemDataRole.UserRole)
                for item in selected_items
            ]
            
            self.logger.debug(f"[SIDEBAR] Suppression demandée: {ids_to_delete}")
            self.delete_conversations_requested.emit(ids_to_delete)
    
    def get_selected_conversation_ids(self) -> List[int]:
        """Retourne les IDs des conversations sélectionnées."""
        selected_items = self.list_widget.selectedItems()
        return [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]
    
    def select_conversation(self, conv_id: int):
        """Sélectionne une conversation par son ID."""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == conv_id:
                self.list_widget.setCurrentItem(item)
                self.logger.debug(f"[SIDEBAR] Conversation ID {conv_id} sélectionnée")
                break
    
    def refresh(self, conversations: List[dict]):
        """Rafraîchit la liste des conversations."""
        current_selection = self.get_selected_conversation_ids()
        self.load_conversations(conversations)
        
        # Restaurer la sélection si possible
        if current_selection and conversations:
            self.select_conversation(current_selection[0])
    
    def clear_search(self):
        """Efface la recherche."""
        self.search_input.clear()
    
    def keyPressEvent(self, event):
        """Gère les raccourcis clavier."""
        # Suppr pour supprimer
        if event.key() == Qt.Key.Key_Delete:
            self._on_delete_clicked()
        else:
            super().keyPressEvent(event)
