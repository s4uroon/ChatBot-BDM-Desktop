"""
ui/export_dialog.py
===================
Export dialog for sessions
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QRadioButton, QComboBox, QPushButton, QLabel,
    QMessageBox, QFileDialog, QFormLayout
)
from pathlib import Path
from core.logger import get_logger
from core.export_manager import ExportManager


class ExportDialog(QDialog):
    """
    Dialog for exporting sessions.
    
    Features:
    - Export selection or all sessions
    - JSON or Markdown format
    - File save dialog
    """
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.logger = get_logger()
        self.controller = controller
        self._current_session_id = None  # For single session export
        
        self.setWindowTitle("💾 Export Sessions")
        self.setMinimumWidth(500)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Export scope group
        scope_group = QGroupBox("Export Scope")
        scope_layout = QVBoxLayout()
        
        self.selection_radio = QRadioButton("Selected sessions only")
        self.all_radio = QRadioButton("All sessions")
        self.selection_radio.setChecked(True)
        
        scope_layout.addWidget(self.selection_radio)
        scope_layout.addWidget(self.all_radio)
        
        scope_group.setLayout(scope_layout)
        layout.addWidget(scope_group)
        
        # Format group
        format_group = QGroupBox("Export Format")
        format_layout = QFormLayout()
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["JSON", "Markdown"])
        
        format_layout.addRow("Format:", self.format_combo)
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # Info label
        info_label = QLabel(
            "💡 JSON format preserves complete structure.\n"
            "📝 Markdown format is human-readable."
        )
        info_label.setStyleSheet("color: #909090; font-size: 11px; padding: 10px;")
        layout.addWidget(info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        export_btn = QPushButton("💾 Export")
        export_btn.clicked.connect(self._on_export)
        export_btn.setDefault(True)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(export_btn)
        
        layout.addLayout(button_layout)
    
    def _on_export(self):
        """Handles the export action."""
        # Determine format
        format_type = self.format_combo.currentText().lower()
        
        # Determine IDs to export
        if self.all_radio.isChecked():
            conversation_ids = None  # All sessions
        else:
            # Export selection
            if self._current_session_id:
                # Export current session (from context menu)
                conversation_ids = [self._current_session_id]
            else:
                # Export selected sessions from sidebar
                from ui.main_window import MainWindow
                main_window = self.parent()
                if isinstance(main_window, MainWindow):
                    conversation_ids = main_window.sidebar.get_selected_conversation_ids()
                    
                    if not conversation_ids:
                        QMessageBox.warning(
                            self,
                            "No Selection",
                            "Please select at least one session to export."
                        )
                        return
                else:
                    QMessageBox.warning(self, "Error", "Unable to get selected sessions.")
                    return
        
        # Generate filename
        filename = ExportManager.generate_filename("sessions_export", format_type)
        default_path = str(Path.home() / "Downloads" / filename)
        
        # File dialog
        if format_type == "json":
            filter_str = "JSON files (*.json)"
        else:
            filter_str = "Markdown files (*.md)"
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Export File",
            default_path,
            filter_str
        )
        
        if not filepath:
            return
        
        # Execute export
        success, message = self.controller.export_conversations(
            format_type,
            filepath,
            conversation_ids
        )
        
        if success:
            QMessageBox.information(
                self,
                "Export Successful",
                f"{message}\n\nFile saved: {filepath}"
            )
            self.logger.debug(f"[EXPORT_DIALOG] Export successful: {filepath}")
            self.accept()
        else:
            QMessageBox.critical(self, "Export Error", message)
            self.logger.error(f"[EXPORT_DIALOG] Export failed: {message}")
    
    def reset(self):
        """Resets the form to default values."""
        self.format_combo.setCurrentIndex(0)
        self.selection_radio.setChecked(True)
        self.all_radio.setChecked(False)
        self._current_session_id = None
        self.all_radio.setEnabled(True)
    
    def set_current_session_only(self, conversation_id: int):
        """
        Configures the dialog to export only the current session.
        
        Args:
            conversation_id: ID of the session to export
        """
        # Pre-select "Selection" and disable "All"
        self.selection_radio.setChecked(True)
        self.all_radio.setEnabled(False)
        
        # Store the ID for export
        self._current_session_id = conversation_id
        
        self.logger.debug(f"[EXPORT_DIALOG] Configured for single session: {conversation_id}")
