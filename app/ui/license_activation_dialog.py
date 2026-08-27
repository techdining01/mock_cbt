from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QMessageBox, QProgressBar, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QIcon
from pathlib import Path

base_dir = Path(__file__).parent.parent.parent


class ActivationThread(QThread):
    """Background thread for license activation to avoid UI freezing."""
    
    success = Signal(bool, str, dict)  # success, message, result_data
    
    def __init__(self, license_client, product_key, user_email, user_name):
        super().__init__()
        self.license_client = license_client
        self.product_key = product_key
        self.user_email = user_email
        self.user_name = user_name
    
    def run(self):
        """Perform activation in background thread."""
        try:
            result = self.license_client.activate_license(
                self.product_key,
                self.user_email,
                self.user_name
            )
            self.success.emit(result.get("success", False), result.get("message", ""), result)
        except Exception as e:
            self.success.emit(False, f"Activation error: {str(e)}", {})


class LicenseActivationDialog(QDialog):
    """Dialog for product license activation."""
    
    def __init__(self, license_client, parent=None):
        super().__init__(parent)
        self.license_client = license_client
        self.activation_thread = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the activation dialog UI."""
        self.setWindowTitle("Product Activation")
        
        # Set the icon for the application.
        icon_candidates = [
            base_dir / "app" / "web" / "images" / "company_logo.ico",
            base_dir / "app" / "web" / "images" / "company.ico",
            base_dir / "app" / "web" / "images" / "company_icon.ico",
        ]
        icon_file = next((f for f in icon_candidates if f.exists()), None)
        if icon_file:
            self.setWindowIcon(QIcon(str(icon_file)))
            
        self.setMinimumWidth(500)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("Activate Your Product")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Instructions
        instructions = QLabel(
            "Enter your product key and contact information to activate your license. "
            "Your license can be activated on up to 2 different machines."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; padding: 10px;")
        layout.addWidget(instructions)
        
        # Form group
        form_group = QGroupBox("Activation Details")
        form_layout = QFormLayout()
        
        # Product key
        self.product_key_input = QLineEdit()
        self.product_key_input.setPlaceholderText("Paste your product key here...")
        self.product_key_input.setMaxLength(4096)  # Allow full formatted product keys
        form_layout.addRow("Product Key:", self.product_key_input)
        
        # User email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your.email@example.com")
        form_layout.addRow("Email (required):", self.email_input)
        
        # User name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Your Name")
        form_layout.addRow("Name (optional):", self.name_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.progress_bar)
        
        # Status message
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("padding: 10px;")
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.activate_button = QPushButton("Activate")
        self.activate_button.setMinimumHeight(40)
        self.activate_button.clicked.connect(self.start_activation)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.activate_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        # License info (shown after successful activation)
        self.license_info_group = QGroupBox("License Information")
        self.license_info_group.setVisible(False)
        license_info_layout = QVBoxLayout()
        
        self.license_info_text = QTextEdit()
        self.license_info_text.setReadOnly(True)
        self.license_info_text.setMaximumHeight(150)
        license_info_layout.addWidget(self.license_info_text)
        
        self.license_info_group.setLayout(license_info_layout)
        layout.addWidget(self.license_info_group)
        
        self.setLayout(layout)
        
        # Check if already activated
        self.check_existing_license()
    
    def check_existing_license(self):
        """Check if license is already activated and show info."""
        try:
            license_info = self.license_client.get_license_info()
            if license_info:
                self.show_license_info(license_info)
                self.activate_button.setText("Reactivate")
                self.product_key_input.setText(license_info.get("product_key", ""))
                self.email_input.setText(license_info.get("user_email", ""))
                self.name_input.setText(license_info.get("user_name", ""))
        except Exception:
            pass  # No existing license
    
    def show_license_info(self, license_info):
        """Display license information."""
        self.license_info_group.setVisible(True)
        
        info_text = f"""
        <b>Product:</b> {license_info.get('license_data', {}).get('product', 'N/A')}<br>
        <b>Version:</b> {license_info.get('license_data', {}).get('version', 'N/A')}<br>
        <b>Expires:</b> {license_info.get('expiry_date', 'N/A')}<br>
        <b>Machine ID:</b> {license_info.get('machine_fingerprint', 'N/A')[:16]}...<br>
        <b>Last Validated:</b> {license_info.get('last_validated', 'N/A')}
        """
        
        self.license_info_text.setHtml(info_text)
    
    def start_activation(self):
        """Start the license activation process."""
        # Validate inputs
        product_key = self.product_key_input.text().strip()
        email = self.email_input.text().strip()
        name = self.name_input.text().strip()
        
        if not product_key:
            QMessageBox.warning(self, "Missing Information", "Please enter your product key.")
            return
        
        if not email:
            QMessageBox.warning(self, "Missing Information", "Please enter your email address.")
            return
        
        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address.")
            return
        
        # Disable UI and show progress
        self.activate_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.product_key_input.setEnabled(False)
        self.email_input.setEnabled(False)
        self.name_input.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Activating license... Please wait.")
        self.status_label.setStyleSheet("color: #0066cc; padding: 10px;")
        
        # Start activation thread
        self.activation_thread = ActivationThread(
            self.license_client, product_key, email, name
        )
        self.activation_thread.success.connect(self.on_activation_complete)
        self.activation_thread.start()
    
    def on_activation_complete(self, success, message, result_data):
        """Handle activation completion."""
        # Re-enable UI
        self.activate_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        self.product_key_input.setEnabled(True)
        self.email_input.setEnabled(True)
        self.name_input.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText(message)
            self.status_label.setStyleSheet("color: #009900; padding: 10px; font-weight: bold;")
            
            # Show license info
            license_info = self.license_client.get_license_info()
            if license_info:
                self.show_license_info(license_info)
            
            QMessageBox.information(
                self, 
                "Activation Successful", 
                f"{message}\n\nRemaining credits: {result_data.get('remaining_credits', 0)}"
            )
            
            # Accept dialog (return true)
            self.accept()
        else:
            self.status_label.setText(message)
            self.status_label.setStyleSheet("color: #cc0000; padding: 10px; font-weight: bold;")
            
            QMessageBox.critical(
                self, 
                "Activation Failed", 
                message
            )
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        if self.activation_thread and self.activation_thread.isRunning():
            self.activation_thread.terminate()
        event.accept()


def show_activation_dialog(license_client, parent=None):
    """
    Convenience function to show the activation dialog.
    
    Args:
        license_client: LicenseClient instance
        parent: Parent widget
        
    Returns:
        True if activation was successful, False otherwise
    """
    dialog = LicenseActivationDialog(license_client, parent)
    result = dialog.exec()
    return result == QDialog.DialogCode.Accepted