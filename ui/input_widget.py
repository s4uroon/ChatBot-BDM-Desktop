"""
ui/input_widget.py
==================
Zone de saisie des messages avec bouton d'envoi
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent
from core.constants import MAX_INPUT_CHARS


def estimate_tokens(text: str) -> int:
    """
    Estime le nombre de tokens pour un texte.
    Approximation: ~4 caractères par token en moyenne.

    Returns:
        int: Estimation du nombre de tokens
    """
    if not text:
        return 0
    # Règle approximative : 1 token ≈ 4 caractères pour l'anglais/français
    return max(1, len(text) // 4)


class CustomTextEdit(QTextEdit):
    """
    QTextEdit personnalisé pour gérer Entrée vs Shift+Entrée.
    - Entrée : Envoie le message
    - Shift+Entrée : Insère un saut de ligne
    """
    
    enter_pressed = pyqtSignal()
    
    def keyPressEvent(self, event: QKeyEvent):
        """Gère les événements clavier."""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Si Shift est pressé, insérer un saut de ligne
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                super().keyPressEvent(event)
            else:
                # Sinon, émettre le signal d'envoi
                self.enter_pressed.emit()
        else:
            super().keyPressEvent(event)


class InputWidget(QWidget):
    """
    Widget de saisie des messages utilisateur.
    
    Fonctionnalités:
    - Zone de texte multi-lignes
    - Compteur de caractères (max 100000)
    - Bouton Envoyer
    - Raccourcis: Entrée = Envoyer, Shift+Entrée = Nouvelle ligne
    """
    
    message_submitted = pyqtSignal(str)
    stop_generation_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.max_chars = MAX_INPUT_CHARS
        self.setup_ui()
    
    def setup_ui(self):
        """Initialise l'interface utilisateur."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(8)
        
        # === LIGNE 1 : Compteur de caractères ===
        counter_layout = QHBoxLayout()
        counter_layout.setContentsMargins(0, 0, 0, 0)
        
        self.char_counter = QLabel(f"0 chars (~0 tokens) / {self.max_chars}")
        self.char_counter.setStyleSheet("color: #909090; font-size: 11px;")
        counter_layout.addStretch()
        counter_layout.addWidget(self.char_counter)
        
        main_layout.addLayout(counter_layout)
        
        # === LIGNE 2 : TextEdit + Bouton Send (côte à côte) ===
        input_send_layout = QHBoxLayout()
        input_send_layout.setSpacing(10)
        input_send_layout.setContentsMargins(0, 0, 0, 0)
        
        # TextEdit (prend tout l'espace disponible)
        self.text_edit = CustomTextEdit()
        self.text_edit.setAcceptRichText(False)  # Désactiver le formatage riche (couleurs, etc.)
        self.text_edit.setPlaceholderText(
            "Type your message here...\n"
            "Enter = Send | Shift+Enter = New line"
        )
        self.text_edit.setMinimumHeight(60)
        self.text_edit.textChanged.connect(self._on_text_changed)
        self.text_edit.enter_pressed.connect(self._on_send_clicked)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                background-color: #252525;
                color: #e0e0e0;
            }
            QTextEdit:focus {
                border-color: #4CAF50;
            }
        """)
        
        # Bouton Send (taille fixe, à DROITE du TextEdit)
        self.send_button = QPushButton("📤 Send")
        self.send_button.setToolTip("Send message (Enter)")
        self.send_button.clicked.connect(self._on_send_clicked)
        self.send_button.setEnabled(False)
        self.send_button.setFixedWidth(100)
        self.send_button.setMinimumHeight(60)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #2d2d2d;
                color: #666666;
            }
        """)
        
        # Bouton Stop (visible uniquement pendant la génération)
        self.stop_button = QPushButton("⏹ Stop")
        self.stop_button.setToolTip("Arrêter la génération (Échap)")
        self.stop_button.setFixedWidth(100)
        self.stop_button.setMinimumHeight(60)
        self.stop_button.setVisible(False)
        self.stop_button.clicked.connect(self.stop_generation_requested)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
            QPushButton:pressed {
                background-color: #c62828;
            }
        """)

        # Ajouter TextEdit puis Stop puis Send (Send caché pendant génération)
        input_send_layout.addWidget(self.text_edit, stretch=1)
        input_send_layout.addWidget(self.stop_button, stretch=0)
        input_send_layout.addWidget(self.send_button, stretch=0)
        
        main_layout.addLayout(input_send_layout)
        
        # === LIGNE 3 : Indication ===
        hint_label = QLabel("💡 Tip: Use Shift+Enter to insert a line break")
        hint_label.setStyleSheet("color: #707070; font-size: 10px; font-style: italic;")
        main_layout.addWidget(hint_label)
    
    def _on_text_changed(self):
        """Gère le changement de texte."""
        text = self.text_edit.toPlainText()
        char_count = len(text)
        token_count = estimate_tokens(text)

        # Mise à jour compteur avec tokens estimés
        self.char_counter.setText(f"{char_count} chars (~{token_count} tokens) / {self.max_chars}")

        # Couleur du compteur selon la limite
        if char_count > self.max_chars:
            self.char_counter.setStyleSheet("color: #f44336; font-size: 11px; font-weight: bold;")
        elif char_count > self.max_chars * 0.9:
            self.char_counter.setStyleSheet("color: #ff9800; font-size: 11px;")
        else:
            self.char_counter.setStyleSheet("color: #909090; font-size: 11px;")

        # Activer/désactiver le bouton
        self.send_button.setEnabled(len(text.strip()) > 0 and char_count <= self.max_chars)
    
    def _on_send_clicked(self):
        """Gère le clic sur Envoyer ou la touche Entrée."""
        text = self.text_edit.toPlainText().strip()
        
        if text and len(text) <= self.max_chars:
            self.message_submitted.emit(text)
            self.text_edit.clear()
    
    def set_enabled(self, enabled: bool):
        """Active/désactive le widget. False = streaming en cours (affiche Stop)."""
        self.text_edit.setEnabled(enabled)
        if enabled:
            self.send_button.setVisible(True)
            self.stop_button.setVisible(False)
            self.send_button.setEnabled(len(self.text_edit.toPlainText().strip()) > 0)
        else:
            self.send_button.setVisible(False)
            self.stop_button.setVisible(True)
    
    def set_focus(self):
        """Donne le focus au champ de saisie."""
        self.text_edit.setFocus()
    
    def clear(self):
        """Efface le contenu."""
        self.text_edit.clear()
