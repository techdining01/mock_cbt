import ctypes
import os
from pathlib import Path


from PySide6.QtWidgets import QApplication  # pyright: ignore[reportMissingImports]
from PySide6.QtWebEngineWidgets import QWebEngineView  # pyright: ignore[reportMissingImports]
from PySide6.QtWebEngineCore import QWebEngineSettings  # pyright: ignore[reportMissingImports]
from PySide6.QtCore import QUrl, QTimer  # pyright: ignore[reportMissingImports]
from PySide6.QtGui import QIcon  # pyright: ignore[reportMissingImports]

from PySide6.QtWebChannel import QWebChannel  # pyright: ignore[reportMissingImports]
from app.bridge.exam_bridge import ExamBridge
from app.bridge.question_import_bridge import QuestionImportBridge

from app.services.pdf_processor import PDFProcessor

base_dir = Path(__file__).parent


def start_ai_tutor_server():
    import asyncio
    import sys
    import uvicorn
    from app.ai_tutor.main import app as tutor_app

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    config = uvicorn.Config(
        tutor_app,
        host="127.0.0.1",
        port=8000,
        log_level="warning",
        loop="asyncio",
    )
    server = uvicorn.Server(config)
    loop.run_until_complete(server.serve())


# Tells Windows to use the script's distinct AppUserModelID for taskbar grouping
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("logiclanesolutions.cbt.v1")


def check_license() -> bool:
    """
    Check if the application is properly licensed.
    
    Returns:
        True if licensed, False otherwise
    """
    try:
        from app.services.licensing.client import LicenseClient
        
        # Get license server URL from environment or use default
        license_server_url = os.getenv("LICENSE_SERVER_URL", "http://127.0.0.1:8000")
        
        client = LicenseClient(license_server_url=license_server_url)
        
        # Check if already licensed
        if client.is_licensed():
            print("License validated successfully.")
            return True
        
        # Check if we should skip license check (development mode)
        if os.getenv("SKIP_LICENSE_CHECK") == "true":
            print("License check skipped (development mode)")
            return True
        
        # Try to activate if license key is provided via environment
        license_key = os.getenv("PRODUCT_KEY")
        if license_key:
            print(f"Attempting to activate license with environment key...")
            result = client.activate_license(license_key)
            
            if result["success"]:
                print(f"License activated successfully. Remaining credits: {result['remaining_credits']}")
                return True
            else:
                print(f"License activation failed: {result['message']}")
                # Fall through to show activation dialog
        
        # No valid license found - will show activation dialog in main()
        return False
        
    except Exception as e:
        print(f"License check error: {e}")
        # For development, you might want to continue anyway
        if os.getenv("SKIP_LICENSE_CHECK") == "true":
            print("License check skipped due to error (development mode)")
            return True
        return False


# This is the main function of our application.
def main():
    import sys
    from dotenv import load_dotenv

    load_dotenv(".env")

    from app.database.database import init_database

    init_database()
    
    # Start local backend server thread (handles licensing and AI tutor APIs)
    import threading
    server_thread = threading.Thread(target=start_ai_tutor_server, daemon=True)
    server_thread.start()
    
    # Create the Qt application first (needed for activation dialog)
    app = QApplication(sys.argv)
    
    # Check license before starting application
    license_valid = check_license()
    
    if not license_valid:
        print("License validation failed. Showing activation dialog...")
        
        # Import license components
        from app.services.licensing.client import LicenseClient
        from app.ui.license_activation_dialog import show_activation_dialog
        
        license_server_url = os.getenv("LICENSE_SERVER_URL", "http://127.0.0.1:8000")
        license_client = LicenseClient(license_server_url=license_server_url)
        
        # Show activation dialog
        activation_success = show_activation_dialog(license_client)
        
        if not activation_success:
            print("License activation cancelled or failed. Exiting application.")
            sys.exit(1)
        
        print("License activated successfully. Starting application...")
    # Qt application was already created earlier for license check

    # Create the Python object that JavaScript will communicate with.
    exam_bridge = ExamBridge()
    import_bridge = QuestionImportBridge()

    # Create a WebChannel for communication between Python and JavaScript.
    channel = QWebChannel()

    # Register our Python bridge for exam and question import
    channel.registerObject("examBridge", exam_bridge)
    channel.registerObject("questionImportBridge", import_bridge)

    # Set the icon for the application.
    icon_candidates = [
        base_dir / "app" / "web" / "images" / "company_logo.ico",
    ]
    icon_file = next((f for f in icon_candidates if f.exists()), None)
    if icon_file:
        app.setWindowIcon(QIcon(str(icon_file)))

    # Allow file:// pages to fetch http://127.0.0.1 (needed for AI Tutor API)
    import sys as _sys
    if "--disable-web-security" not in _sys.argv:
        _sys.argv.append("--disable-web-security")

    # Create our desktop browser window.
    # This will eventually display our HTML + Tailwind + Alpine.js interface.
    window = QWebEngineView()

    # Allow local file pages to make requests to remote/local HTTP URLs
    settings = window.settings()
    settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
    settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)

    # Set the web view on the exam bridge for PDF export functionality
    exam_bridge.set_web_view(window)

    # Native Qt Print Handler for window.print() requests
    def handle_print_requested():
        try:
            from PySide6.QtPrintSupport import QPrintDialog, QPrinter
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            dialog = QPrintDialog(printer, window)
            dialog.setWindowTitle("Print CBT Document")
            if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                window.page().print(printer, lambda res: None)
        except Exception as err:
            print("Native print handler error:", err)

    window.page().printRequested.connect(handle_print_requested)

    # ---- CRITICAL: Attach the channel BEFORE setUrl() so that qt.webChannelTransport
    # is injected into the main page AND all same-origin sub-frame documents (iframes)
    # as soon as each page loads. When attached after setUrl, sub-frames sometimes
    # miss the transport injection.
    window.page().setWebChannel(channel)

    # Re-attach the channel to the top-level page after every load to cover any
    # scenario where it was dropped during navigation, screen changes, or iframe
    # creation. Iframes inside QWebEngineView share the QWebChannel transport of
    # their top-level page when the channel is installed before the sub-frame
    # document is created; the parent-then-standalone fallback strategy in
    # question_import.html handles the case where the timing is off.
    _reattach_counter = [0]

    def reattach():
        try:
            window.page().setWebChannel(channel)
        except Exception:
            pass

    fast_timer = QTimer(window)
    fast_counter = [30]

    def _fast_tick():
        reattach()
        fast_counter[0] -= 1
        if fast_counter[0] <= 0:
            fast_timer.stop()

    fast_timer.timeout.connect(_fast_tick)
    fast_timer.start(250)

    slow_timer = QTimer(window)
    slow_timer.timeout.connect(reattach)
    slow_timer.start(2000)

    window.loadFinished.connect(lambda _ok: reattach())

    # Set the title and icon that appears on the Windows window.
    window.setWindowTitle("LLS CBT")
    if icon_file:
        window.setWindowIcon(QIcon(str(icon_file)))

    # Set the initial size of the application window.
    # The first value is width and the second is height.
    window.resize(800, 600)

    # Build the full path to index.html.
    html_file = base_dir / "app" / "web" / "index.html"

    # Convert the local Windows file path into a QUrl.
    html_url = QUrl.fromLocalFile(str(html_file))

    # Load the HTML page.
    window.setUrl(html_url)

    # Make the application window visible.
    window.show()

    # Start Qt's event loop.
    # The application keeps running here until the user closes the window.
    sys.exit(app.exec())


# This checks whether Python is running this file directly.
# If it is, call our main() function.
if __name__ == "__main__":
    main()
