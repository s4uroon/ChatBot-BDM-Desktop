"""
ui/settings_dialog.py
=====================
Dialogue de paramètres — Apparence (coloration syntaxique)
La configuration API est gérée via ProfileManagerDialog.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QPushButton, QCheckBox, QMessageBox,
    QGroupBox, QFormLayout, QColorDialog, QComboBox, QLineEdit,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor
from core.logger import get_logger
from utils.css_generator import CSSGenerator


class SettingsDialog(QDialog):
    """
    Dialogue de configuration de l'application.

    Onglets:
    1. Apparence: Thème Highlight.js + couleurs de code avec prévisualisation
    """

    settings_saved = pyqtSignal(dict)

    def __init__(self, settings_manager, api_client=None, parent=None):
        super().__init__(parent)
        self.logger = get_logger()
        self.settings_manager = settings_manager
        self.css_generator = CSSGenerator()

        self.setWindowTitle("Paramètres")
        self.setModal(True)
        self.resize(700, 500)

        self.setup_ui()
        self.load_current_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_appearance_tab(), "🎨 Apparence Code")

        layout.addWidget(self.tabs)

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

    # === ONGLET APPARENCE ===

    def _create_appearance_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        theme_group = QGroupBox("Thème de Coloration Syntaxique")
        theme_layout = QFormLayout()

        self.hljs_theme_combo = QComboBox()
        self.hljs_theme_combo.addItem("🌙 Sombre (Dark)", "dark")
        self.hljs_theme_combo.addItem("☀️ Clair (Light)", "light")
        self.hljs_theme_combo.setToolTip("Choisissez le thème de coloration pour les blocs de code")
        theme_layout.addRow("Thème:", self.hljs_theme_combo)

        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        colors_group = QGroupBox("Couleurs de la Coloration Syntaxique")
        colors_layout = QFormLayout()

        self.color_inputs = {}

        color_types = [
            ('comment', '💬 Commentaires'),
            ('keyword', '🔑 Mots-clés'),
            ('string', '📝 Chaînes'),
            ('number', '🔢 Nombres'),
            ('function', '⚙️ Fonctions'),
        ]

        for color_key, label in color_types:
            input_layout = QHBoxLayout()

            color_input = QLineEdit()
            color_input.setPlaceholderText("#RRGGBB")
            color_input.setMaximumWidth(100)
            self.color_inputs[color_key] = color_input
            input_layout.addWidget(color_input)

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

        buttons_layout = QHBoxLayout()

        reset_btn = QPushButton("🔄 Réinitialiser")
        reset_btn.clicked.connect(self._on_reset_colors_clicked)
        buttons_layout.addWidget(reset_btn)
        buttons_layout.addStretch()

        preview_btn = QPushButton("👁️ Prévisualiser")
        preview_btn.clicked.connect(self._update_preview)
        preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 20px;
            }
        """)
        buttons_layout.addWidget(preview_btn)

        layout.addLayout(buttons_layout)

        preview_group = QGroupBox("Prévisualisation")
        preview_layout = QVBoxLayout()

        self.preview_web = QWebEngineView()
        self.preview_web.setMaximumHeight(200)
        preview_layout.addWidget(self.preview_web)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        self._update_preview()

        return widget

    # === MÉTHODES ===

    def load_current_settings(self):
        current_theme = self.settings_manager.get_hljs_theme()
        index = self.hljs_theme_combo.findData(current_theme)
        if index >= 0:
            self.hljs_theme_combo.setCurrentIndex(index)

        colors = self.settings_manager.get_all_colors()
        for key, value in colors.items():
            if key in self.color_inputs:
                self.color_inputs[key].setText(value)

    def _open_color_picker(self, color_key: str):
        current_color = self.color_inputs[color_key].text()
        if current_color and self.css_generator.validate_color(current_color):
            initial_color = QColor(current_color)
        else:
            initial_color = QColor("#ffffff")

        color = QColorDialog.getColor(initial_color, self, "Choisir une couleur")
        if color.isValid():
            self.color_inputs[color_key].setText(color.name())
            self._update_preview()

    def _on_reset_colors_clicked(self):
        reply = QMessageBox.question(
            self,
            "Réinitialiser les couleurs",
            "Voulez-vous réinitialiser toutes les couleurs aux valeurs par défaut ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            for key, value in self.css_generator.DEFAULT_COLORS.items():
                if key in self.color_inputs:
                    self.color_inputs[key].setText(value)
            self._update_preview()

    def _update_preview(self):
        colors = {}
        for key, input_widget in self.color_inputs.items():
            color = input_widget.text()
            if color and self.css_generator.validate_color(color):
                colors[key] = color
        self.preview_web.setHtml(self.css_generator.get_preview_html(colors))

    def _on_save_clicked(self):
        hljs_theme = self.hljs_theme_combo.currentData()

        colors = {}
        for key, input_widget in self.color_inputs.items():
            color = input_widget.text()
            if color and self.css_generator.validate_color(color):
                colors[key] = self.css_generator.normalize_color(color)

        self.settings_manager.set_hljs_theme(hljs_theme)
        self.settings_manager.set_all_colors(colors)

        self.settings_saved.emit({'hljs_theme': hljs_theme, 'colors': colors})

        self.logger.debug("[SETTINGS_DIALOG] Paramètres sauvegardés")

        QMessageBox.information(
            self,
            "Paramètres sauvegardés",
            "Les paramètres ont été sauvegardés avec succès.",
        )

        self.accept()
