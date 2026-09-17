from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QMessageBox, QProgressBar,
    QGroupBox, QFormLayout,
)

base_dir = Path(__file__).parent.parent.parent


class _ActivationThread(QThread):
    done = Signal(bool, str, dict)

    def __init__(self, client, key, name):
        super().__init__()
        self.client = client
        self.key    = key
        self.name   = name

    def run(self):
        try:
            result = self.client.activate_license(self.key, user_name=self.name)
            self.done.emit(result.get("success", False), result.get("message", ""), result)
        except Exception as exc:
            self.done.emit(False, f"Activation error: {exc}", {})


class LicenseActivationDialog(QDialog):

    def __init__(self, license_client, parent=None):
        super().__init__(parent)
        self.license_client    = license_client
        self._activation_thread = None
        self._setup_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _setup_ui(self):
        self.setWindowTitle("Product Activation — LLS CBT")
        self.setMinimumWidth(520)
        self.setModal(True)

        icon_path = next(
            (p for p in [
                base_dir / "app" / "web" / "images" / "company_logo.ico",
            ] if p.exists()),
            None,
        )
        if icon_path:
            self.setWindowIcon(QIcon(str(icon_path)))

        layout = QVBoxLayout(self)

        # --- Header ---
        title = QLabel("Activate LLS CBT")
        font  = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel(
            "Enter your product key to activate. "
            "Each key allows activation on up to 2 machines for 1 year."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color:#555; padding:6px 0;")
        layout.addWidget(subtitle)

        # --- Machine ID (read-only, so customer can send it to you) ---
        mid_group  = QGroupBox("Your Machine ID  (share this to get a machine-locked key)")
        mid_layout = QHBoxLayout()
        self._machine_id_label = QLineEdit(self.license_client.machine_fingerprint)
        self._machine_id_label.setReadOnly(True)
        self._machine_id_label.setStyleSheet("color:#333; background:#f5f5f5;")
        copy_btn = QPushButton("Copy")
        copy_btn.setFixedWidth(60)
        copy_btn.clicked.connect(self._copy_machine_id)
        mid_layout.addWidget(self._machine_id_label)
        mid_layout.addWidget(copy_btn)
        mid_group.setLayout(mid_layout)
        layout.addWidget(mid_group)

        # --- Activation form ---
        form_group  = QGroupBox("Activation Details")
        form_layout = QFormLayout()

        self._key_input = QLineEdit()
        self._key_input.setPlaceholderText("XXXXX-XXXXX-XXXXX-XXXXX  (paste your product key)")
        self._key_input.setMaxLength(8192)
        form_layout.addRow("Product Key:", self._key_input)

        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("School / Organisation name (optional)")
        form_layout.addRow("Name:", self._name_input)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # --- Progress ---
        self._progress = QProgressBar()
        self._progress.setVisible(False)
        self._progress.setRange(0, 0)
        layout.addWidget(self._progress)

        # --- Status ---
        self._status = QLabel("")
        self._status.setWordWrap(True)
        self._status.setStyleSheet("padding:6px 0;")
        layout.addWidget(self._status)

        # --- Buttons ---
        btn_row = QHBoxLayout()
        self._activate_btn = QPushButton("Activate")
        self._activate_btn.setMinimumHeight(38)
        self._activate_btn.clicked.connect(self._start_activation)
        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setMinimumHeight(38)
        self._cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self._activate_btn)
        btn_row.addWidget(self._cancel_btn)
        layout.addLayout(btn_row)

        # --- License info (shown after activation) ---
        self._info_group = QGroupBox("License Information")
        self._info_group.setVisible(False)
        info_layout = QVBoxLayout()
        self._info_text = QTextEdit()
        self._info_text.setReadOnly(True)
        self._info_text.setMaximumHeight(130)
        info_layout.addWidget(self._info_text)
        self._info_group.setLayout(info_layout)
        layout.addWidget(self._info_group)

        self._prefill_existing()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _prefill_existing(self):
        info = self.license_client.get_license_info()
        if not info:
            return
        self._key_input.setText(info.get("product_key", ""))
        self._name_input.setText(info.get("user_name", ""))
        self._activate_btn.setText("Reactivate")
        self._show_license_info(info)

    def _show_license_info(self, info: dict):
        payload = info.get("payload") or info.get("license_data") or {}
        self._info_group.setVisible(True)
        self._info_text.setHtml(
            f"<b>Product:</b> {payload.get('product', 'N/A')}<br>"
            f"<b>Expires:</b> {info.get('expiry_date', payload.get('expiry', 'N/A'))}<br>"
            f"<b>Credits used:</b> {info.get('credits_used', 1)} / {payload.get('credits', 2)}<br>"
            f"<b>Activated:</b> {info.get('activated_at', info.get('last_validated', 'N/A'))}<br>"
            f"<b>Machine:</b> {info.get('machine_fingerprint', 'N/A')[:20]}..."
        )

    def _copy_machine_id(self):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.license_client.machine_fingerprint)
        self._status.setText("Machine ID copied to clipboard.")
        self._status.setStyleSheet("color:#0066cc; padding:6px 0;")

    def _set_busy(self, busy: bool):
        for w in (self._activate_btn, self._cancel_btn, self._key_input, self._name_input):
            w.setEnabled(not busy)
        self._progress.setVisible(busy)

    # ------------------------------------------------------------------
    # Activation
    # ------------------------------------------------------------------

    def _start_activation(self):
        key  = self._key_input.text().strip()
        name = self._name_input.text().strip()

        if not key:
            QMessageBox.warning(self, "Missing Key", "Please enter your product key.")
            return

        self._set_busy(True)
        self._status.setText("Verifying product key…")
        self._status.setStyleSheet("color:#0066cc; padding:6px 0;")

        self._activation_thread = _ActivationThread(self.license_client, key, name)
        self._activation_thread.done.connect(self._on_done)
        self._activation_thread.start()

    def _on_done(self, success: bool, message: str, result: dict):
        self._set_busy(False)

        if success:
            self._status.setText(message)
            self._status.setStyleSheet("color:#007700; font-weight:bold; padding:6px 0;")
            self._show_license_info(self.license_client.get_license_info() or {})
            QMessageBox.information(
                self, "Activation Successful",
                f"{message}\n\nRemaining credits: {result.get('remaining_credits', 0)}\n"
                f"Expires: {result.get('expiry_date', 'N/A')}",
            )
            self.accept()
        else:
            self._status.setText(message)
            self._status.setStyleSheet("color:#cc0000; font-weight:bold; padding:6px 0;")
            QMessageBox.critical(self, "Activation Failed", message)

    def closeEvent(self, event):
        if self._activation_thread and self._activation_thread.isRunning():
            self._activation_thread.terminate()
        event.accept()


def show_activation_dialog(license_client, parent=None) -> bool:
    dialog = LicenseActivationDialog(license_client, parent)
    return dialog.exec() == QDialog.DialogCode.Accepted
