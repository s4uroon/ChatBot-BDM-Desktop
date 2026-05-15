"""
ui/profile_manager_dialog.py
=============================
Dialog de gestion des profils API (CRUD multi-fournisseurs)
"""

from urllib.parse import urlparse

from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QFormLayout,
    QListWidget, QListWidgetItem, QPushButton, QLineEdit,
    QLabel, QCheckBox, QComboBox, QDoubleSpinBox, QSpinBox,
    QGroupBox, QMessageBox, QDialogButtonBox, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal

from core.api_profile import APIProfile, Provider
from core.api_client import create_api_client


class ProfileManagerDialog(QDialog):
    """
    Dialog de gestion des profils API.
    Permet de créer, modifier, supprimer et tester des profils.
    """

    profiles_updated = pyqtSignal()

    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.profiles: list[APIProfile] = list(settings_manager.get_profiles())
        self._current_index: int = -1

        self.setWindowTitle("Gestion des profils API")
        self.setMinimumSize(720, 480)
        self.setModal(True)

        self._build_ui()
        self._load_list()
        if self.profiles:
            self.profile_list.setCurrentRow(0)

    # ------------------------------------------------------------------
    # Construction de l'interface
    # ------------------------------------------------------------------

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(12)

        # --- Colonne gauche : liste + boutons ---
        left = QVBoxLayout()
        left.setSpacing(6)

        self.profile_list = QListWidget()
        self.profile_list.setFixedWidth(200)
        self.profile_list.currentRowChanged.connect(self._on_row_changed)
        left.addWidget(self.profile_list)

        btn_row = QHBoxLayout()
        self.btn_new = QPushButton("➕ Nouveau")
        self.btn_new.clicked.connect(self._on_new)
        btn_row.addWidget(self.btn_new)

        self.btn_delete = QPushButton("🗑 Supprimer")
        self.btn_delete.clicked.connect(self._on_delete)
        btn_row.addWidget(self.btn_delete)
        left.addLayout(btn_row)

        root.addLayout(left)

        # --- Colonne droite : formulaire ---
        right = QVBoxLayout()
        right.setSpacing(8)

        form_group = QGroupBox("Configuration du profil")
        form = QFormLayout(form_group)
        form.setSpacing(8)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: OpenAI GPT-4o")
        form.addRow("Nom :", self.name_input)

        self.provider_combo = QComboBox()
        for p in Provider.ALL:
            self.provider_combo.addItem(Provider.LABELS[p], p)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        form.addRow("Fournisseur :", self.provider_combo)

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("sk-... / clé API")
        form.addRow("Clé API :", self.api_key_input)

        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("https://api.openai.com/v1")
        form.addRow("URL de base :", self.base_url_input)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("gpt-4o")
        form.addRow("Modèle :", self.model_input)

        self.verify_ssl_check = QCheckBox("Activer la vérification SSL")
        form.addRow("", self.verify_ssl_check)

        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.05)
        self.temperature_spin.setDecimals(2)
        self.temperature_spin.setValue(0.7)
        form.addRow("Température :", self.temperature_spin)

        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(0, 128000)
        self.max_tokens_spin.setSpecialValueText("Illimité")
        self.max_tokens_spin.setValue(0)
        form.addRow("Max tokens :", self.max_tokens_spin)

        right.addWidget(form_group)

        # Test de connexion
        test_row = QHBoxLayout()
        self.btn_test = QPushButton("🔍 Tester la connexion")
        self.btn_test.clicked.connect(self._on_test)
        test_row.addWidget(self.btn_test)
        test_row.addStretch()
        right.addLayout(test_row)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        right.addWidget(self.status_label)

        right.addStretch()

        # Boutons Annuler / Sauvegarder
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        right.addWidget(buttons)

        root.addLayout(right)

    # ------------------------------------------------------------------
    # Gestion de la liste
    # ------------------------------------------------------------------

    def _load_list(self):
        self.profile_list.blockSignals(True)
        self.profile_list.clear()
        for p in self.profiles:
            item = QListWidgetItem(p.name)
            item.setData(Qt.ItemDataRole.UserRole, p.profile_id)
            self.profile_list.addItem(item)
        self.profile_list.blockSignals(False)

    def _on_row_changed(self, row: int):
        self._save_current_to_memory()
        self._current_index = row
        if 0 <= row < len(self.profiles):
            self._populate_form(self.profiles[row])
            self.btn_delete.setEnabled(True)
            self.btn_test.setEnabled(True)
        else:
            self._clear_form()
            self.btn_delete.setEnabled(False)
            self.btn_test.setEnabled(False)
        self.status_label.setText("")

    def _save_current_to_memory(self):
        """Sauvegarde les valeurs du formulaire dans self.profiles[_current_index]."""
        idx = self._current_index
        if idx < 0 or idx >= len(self.profiles):
            return
        p = self.profiles[idx]
        p.name = self.name_input.text().strip() or p.name
        p.provider = self.provider_combo.currentData()
        p.api_key = self.api_key_input.text().strip()
        p.base_url = self.base_url_input.text().strip()
        p.model = self.model_input.text().strip()
        p.verify_ssl = self.verify_ssl_check.isChecked()
        p.temperature = self.temperature_spin.value()
        mt = self.max_tokens_spin.value()
        p.max_tokens = mt if mt > 0 else None
        # Mettre à jour le nom dans la liste
        item = self.profile_list.item(idx)
        if item:
            item.setText(p.name or "Sans nom")

    def _populate_form(self, profile: APIProfile):
        self.name_input.setText(profile.name)
        idx = self.provider_combo.findData(profile.provider)
        self.provider_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.api_key_input.setText(profile.api_key)
        self.base_url_input.setText(profile.base_url)
        self.model_input.setText(profile.model)
        self.verify_ssl_check.setChecked(profile.verify_ssl)
        self.temperature_spin.setValue(profile.temperature)
        self.max_tokens_spin.setValue(profile.max_tokens or 0)

    def _clear_form(self):
        self.name_input.clear()
        self.provider_combo.setCurrentIndex(0)
        self.api_key_input.clear()
        self.base_url_input.clear()
        self.model_input.clear()
        self.verify_ssl_check.setChecked(False)
        self.temperature_spin.setValue(0.7)
        self.max_tokens_spin.setValue(0)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _on_new(self):
        self._save_current_to_memory()
        provider = Provider.OPENAI
        new_profile = APIProfile(
            name="Nouveau profil",
            provider=provider,
            api_key="",
            base_url=Provider.DEFAULT_URLS[provider],
            model=Provider.DEFAULT_MODELS[provider],
        )
        self.profiles.append(new_profile)
        item = QListWidgetItem(new_profile.name)
        item.setData(Qt.ItemDataRole.UserRole, new_profile.profile_id)
        self.profile_list.addItem(item)
        self.profile_list.setCurrentRow(len(self.profiles) - 1)

    def _on_delete(self):
        idx = self._current_index
        if idx < 0 or idx >= len(self.profiles):
            return
        if len(self.profiles) == 1:
            QMessageBox.warning(self, "Impossible", "Vous devez conserver au moins un profil.")
            return
        name = self.profiles[idx].name
        reply = QMessageBox.question(
            self, "Confirmer",
            f"Supprimer le profil « {name} » ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.profiles.pop(idx)
        self._current_index = -1
        self._load_list()
        row = min(idx, len(self.profiles) - 1)
        self.profile_list.setCurrentRow(row)

    def _on_provider_changed(self, _index: int):
        provider = self.provider_combo.currentData()
        self.base_url_input.setText(Provider.DEFAULT_URLS.get(provider, ""))
        self.model_input.setText(Provider.DEFAULT_MODELS.get(provider, ""))

    def _on_test(self):
        self._save_current_to_memory()
        idx = self._current_index
        if idx < 0 or idx >= len(self.profiles):
            return
        profile = self.profiles[idx]
        valid, err = self._validate(profile)
        if not valid:
            self._set_status(f"❌ {err}", error=True)
            return

        self.btn_test.setEnabled(False)
        self._set_status("⏳ Test en cours...", error=False)

        try:
            client = create_api_client(profile)
            success, message = client.test_connection()
            client.close()
            if success:
                self._set_status(f"✅ {message}", error=False)
            else:
                self._set_status(f"❌ {message}", error=True)
        except Exception as e:
            self._set_status(f"❌ Erreur: {e}", error=True)
        finally:
            self.btn_test.setEnabled(True)

    def _on_save(self):
        self._save_current_to_memory()
        # Valider tous les profils
        for p in self.profiles:
            valid, err = self._validate(p)
            if not valid:
                QMessageBox.warning(self, f"Profil « {p.name} »", err)
                return
        self.settings_manager.save_profiles(self.profiles)
        # Si le profil actif a été supprimé, pointer sur le premier
        active_id = self.settings_manager.get_active_profile_id()
        ids = {p.profile_id for p in self.profiles}
        if active_id not in ids and self.profiles:
            self.settings_manager.set_active_profile_id(self.profiles[0].profile_id)
        self.profiles_updated.emit()
        self.accept()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _validate(self, profile: APIProfile):
        if not profile.name.strip():
            return False, "Le nom du profil est obligatoire."
        if not profile.api_key.strip():
            return False, "La clé API est obligatoire."
        if len(profile.api_key.strip()) < 5:
            return False, "La clé API semble trop courte."
        if not profile.base_url.strip():
            return False, "L'URL de base est obligatoire."
        try:
            parsed = urlparse(profile.base_url)
            if parsed.scheme not in ('http', 'https'):
                return False, "L'URL doit commencer par http:// ou https://"
            if not parsed.netloc:
                return False, "URL invalide (domaine manquant)."
        except Exception as e:
            return False, f"URL invalide : {e}"
        if not profile.model.strip():
            return False, "Le nom du modèle est obligatoire."
        return True, ""

    def _set_status(self, text: str, error: bool):
        color = "#f44336" if error else "#4CAF50"
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; font-size: 12px;")
