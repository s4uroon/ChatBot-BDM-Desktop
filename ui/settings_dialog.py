"""
ui/settings_dialog.py
=====================
Dialogue de paramètres avec onglets (Connexion, Apparence)
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox,
    QGroupBox, QFormLayout, QColorDialog
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from typing import Dict
from core.logger import get_logger
from utils.css_generator import CSSGenerator


class SettingsDialog(QDialog):
    """
    Dialogue de configuration de l'application.
    
    Onglets:
    1. Connexion: API Key, URL, Modèle, Test
    2. Apparence: Couleurs de code avec prévisualisation
    """
    
    # Signaux
    settings_saved = pyqtSignal(dict)  # Paramètres sauvegardés
    
    def __init__(self, settings_manager, api_client=None, parent=None):
        super().__init__(parent)
        self.logger = get_logger()
        self.settings_manager = settings_manager
        self.api_client = api_client
        self.css_generator = CSSGenerator()
        
        self.setWindowTitle("Paramètres")
        self.setModal(True)
        self.resize(700, 500)
        
        self.setup_ui()
        self.load_current_settings()
    
    def setup_ui(self):
        """Initialise l'interface utilisateur."""
        layout = QVBoxLayout(self)
        
        # Onglets
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_connection_tab(), "🔌 Connexion")
        self.tabs.addTab(self._create_appearance_tab(), "🎨 Apparence Code")
        
        layout.addWidget(self.tabs)
        
        # Boutons Enregistrer / Annuler
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.clicked.connect(self._on_save_clicked)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 20px;
                font-weight: bold;
            }
        """)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    # === ONGLET CONNEXION ===
    
    def _create_connection_tab(self) -> QWidget:
        """Crée l'onglet de configuration de connexion."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Groupe API
        api_group = QGroupBox("Configuration API")
        api_layout = QFormLayout()
        
        # Clé API
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("sk-...")
        api_layout.addRow("Clé API:", self.api_key_input)
        
        # URL de base
        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("https://api.openai.com/v1")
        api_layout.addRow("URL de base:", self.base_url_input)
        
        # Modèle
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("gpt-4")
        api_layout.addRow("Modèle:", self.model_input)
        
        # Vérification SSL
        self.verify_ssl_checkbox = QCheckBox("Activer la vérification SSL")
        self.verify_ssl_checkbox.setToolTip(
            "Décocher pour les serveurs avec certificats auto-signés"
        )
        api_layout.addRow("", self.verify_ssl_checkbox)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # Bouton Test
        test_layout = QHBoxLayout()
        test_layout.addStretch()
        
        self.test_button = QPushButton("🔍 Tester la connexion")
        self.test_button.clicked.connect(self._on_test_clicked)
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 20px;
                font-weight: bold;
            }
        """)
        test_layout.addWidget(self.test_button)
        
        layout.addLayout(test_layout)
        
        # Label de statut
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        return widget
    
    # === ONGLET APPARENCE ===
    
    def _create_appearance_tab(self) -> QWidget:
        """Crée l'onglet de configuration de l'apparence."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Groupe Couleurs
        colors_group = QGroupBox("Couleurs de la Coloration Syntaxique")
        colors_layout = QFormLayout()
        
        # Dictionnaire des inputs couleurs
        self.color_inputs = {}
        
        color_types = [
            ('comment', '💬 Commentaires'),
            ('keyword', '🔑 Mots-clés'),
            ('string', '📝 Chaînes'),
            ('number', '🔢 Nombres'),
            ('function', '⚙️ Fonctions')
        ]
        
        for color_key, label in color_types:
            input_layout = QHBoxLayout()
            
            # Input texte
            color_input = QLineEdit()
            color_input.setPlaceholderText("#RRGGBB")
            color_input.setMaximumWidth(100)
            self.color_inputs[color_key] = color_input
            input_layout.addWidget(color_input)
            
            # Bouton sélecteur
            picker_btn = QPushButton("🎨")
            picker_btn.setMaximumWidth(40)
            picker_btn.clicked.connect(
                lambda checked, key=color_key: self._open_color_picker(key)
            )
            input_layout.addWidget(picker_btn)
            
            input_layout.addStretch()
            
            colors_layout.addRow(label, input_layout)
        
        colors_group.setLayout(colors_layout)
        layout.addWidget(colors_group)
        
        # Boutons Reset et Prévisualiser
        buttons_layout = QHBoxLayout()
        
        reset_btn = QPushButton("🔄 Réinitialiser")
        reset_btn.clicked.connect(self._on_reset_colors_clicked)
        buttons_layout.addWidget(reset_btn)
        
        buttons_layout.addStretch()
        
        preview_btn = QPushButton("👁️ Prévisualiser")
        preview_btn.clicked.connect(self._on_preview_clicked)
        preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 20px;
            }
        """)
        buttons_layout.addWidget(preview_btn)
        
        layout.addLayout(buttons_layout)
        
        # Zone de prévisualisation
        preview_group = QGroupBox("Prévisualisation")
        preview_layout = QVBoxLayout()
        
        self.preview_web = QWebEngineView()
        self.preview_web.setMaximumHeight(200)
        preview_layout.addWidget(self.preview_web)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Charger la prévisualisation initiale
        self._update_preview()
        
        return widget
    
    # === MÉTHODES ===
    
    def load_current_settings(self):
        """Charge les paramètres actuels."""
        # Connexion
        self.api_key_input.setText(self.settings_manager.get_api_key())
        self.base_url_input.setText(self.settings_manager.get_base_url())
        self.model_input.setText(self.settings_manager.get_model())
        self.verify_ssl_checkbox.setChecked(self.settings_manager.get_verify_ssl())
        
        # Apparence
        colors = self.settings_manager.get_all_colors()
        for key, value in colors.items():
            if key in self.color_inputs:
                self.color_inputs[key].setText(value)
    
    def _on_test_clicked(self):
        """Teste la connexion à l'API."""
        self.status_label.setText("⏳ Test en cours...")
        self.status_label.setStyleSheet("color: #ff9800;")
        self.test_button.setEnabled(False)
        
        # Récupérer les valeurs
        api_key = self.api_key_input.text()
        base_url = self.base_url_input.text()
        model = self.model_input.text()
        verify_ssl = self.verify_ssl_checkbox.isChecked()
        
        if not api_key:
            self.status_label.setText("❌ Veuillez entrer une clé API")
            self.status_label.setStyleSheet("color: #f44336;")
            self.test_button.setEnabled(True)
            return
        
        # Import et test
        from core.api_client import APIClient
        
        try:
            test_client = APIClient(
                api_key=api_key,
                base_url=base_url or "https://api.openai.com/v1",
                model=model or "gpt-4",
                verify_ssl=verify_ssl
            )
            
            success, message = test_client.test_connection()
            
            if success:
                self.status_label.setText(f"✅ {message}")
                self.status_label.setStyleSheet("color: #4CAF50;")
            else:
                self.status_label.setText(f"❌ {message}")
                self.status_label.setStyleSheet("color: #f44336;")
            
            test_client.close()
        
        except Exception as e:
            self.status_label.setText(f"❌ Erreur: {str(e)}")
            self.status_label.setStyleSheet("color: #f44336;")
            self.logger.error(f"[SETTINGS_DIALOG] Test connexion", exc_info=True)
        
        finally:
            self.test_button.setEnabled(True)
    
    def _open_color_picker(self, color_key: str):
        """Ouvre un sélecteur de couleur."""
        current_color = self.color_inputs[color_key].text()
        
        # Couleur initiale
        if current_color and self.css_generator.validate_color(current_color):
            initial_color = QColor(current_color)
        else:
            initial_color = QColor("#ffffff")
        
        # Dialogue
        color = QColorDialog.getColor(initial_color, self, f"Choisir une couleur")
        
        if color.isValid():
            hex_color = color.name()
            self.color_inputs[color_key].setText(hex_color)
            self._update_preview()
    
    def _on_reset_colors_clicked(self):
        """Réinitialise les couleurs aux valeurs par défaut."""
        reply = QMessageBox.question(
            self,
            "Réinitialiser les couleurs",
            "Voulez-vous réinitialiser toutes les couleurs aux valeurs par défaut ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            defaults = self.css_generator.DEFAULT_COLORS
            for key, value in defaults.items():
                if key in self.color_inputs:
                    self.color_inputs[key].setText(value)
            
            self._update_preview()
            self.logger.debug("[SETTINGS_DIALOG] Couleurs réinitialisées")
    
    def _on_preview_clicked(self):
        """Met à jour la prévisualisation."""
        self._update_preview()
    
    def _update_preview(self):
        """Met à jour la zone de prévisualisation."""
        colors = {}
        for key, input_widget in self.color_inputs.items():
            color = input_widget.text()
            if color and self.css_generator.validate_color(color):
                colors[key] = color
        
        preview_html = self.css_generator.get_preview_html(colors)
        self.preview_web.setHtml(preview_html)
    
    def _on_save_clicked(self):
        """Sauvegarde les paramètres."""
        # Connexion
        api_key = self.api_key_input.text()
        base_url = self.base_url_input.text() or "https://api.openai.com/v1"
        model = self.model_input.text() or "gpt-4"
        verify_ssl = self.verify_ssl_checkbox.isChecked()
        
        # Validation
        if not api_key:
            QMessageBox.warning(
                self,
                "Clé API manquante",
                "Veuillez entrer une clé API."
            )
            return
        
        # Apparence
        colors = {}
        for key, input_widget in self.color_inputs.items():
            color = input_widget.text()
            if color and self.css_generator.validate_color(color):
                colors[key] = self.css_generator.normalize_color(color)
        
        # Sauvegarde
        self.settings_manager.set_api_key(api_key)
        self.settings_manager.set_base_url(base_url)
        self.settings_manager.set_model(model)
        self.settings_manager.set_verify_ssl(verify_ssl)
        self.settings_manager.set_all_colors(colors)
        
        # Émettre le signal avec tous les paramètres
        settings_dict = {
            'api_key': api_key,
            'base_url': base_url,
            'model': model,
            'verify_ssl': verify_ssl,
            'colors': colors
        }
        self.settings_saved.emit(settings_dict)
        
        self.logger.debug("[SETTINGS_DIALOG] Paramètres sauvegardés")
        
        QMessageBox.information(
            self,
            "Paramètres sauvegardés",
            "Les paramètres ont été sauvegardés avec succès."
        )
        
        self.accept()
