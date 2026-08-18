# from pathlib import Path
# base_dir = Path(__file__).parent

# # Import sys so we can pass command-line arguments to the Qt application
# # and exit the program cleanly when the window closes.
# import sys

# # Import QApplication.
# # This creates and manages the main desktop application.
# from PySide6.QtWidgets import QApplication

# # Import QWebEngineView.
# # This is the desktop browser component that will display our HTML page.
# from PySide6.QtWebEngineWidgets import QWebEngineView

# # Import QUrl.
# # QUrl allows us to convert our local HTML file path into a URL
# # that Qt WebEngine can understand.
# from PySide6.QtCore import QUrl

# from PySide6.QtGui import QIconimport sys

from pathlib import Path


from PySide6.QtWidgets import QApplication  # pyright: ignore[reportMissingImports]
from PySide6.QtWebEngineWidgets import QWebEngineView  # pyright: ignore[reportMissingImports]
from PySide6.QtCore import QUrl, QTimer  # pyright: ignore[reportMissingImports]
from PySide6.QtGui import QIcon  # pyright: ignore[reportMissingImports]

from PySide6.QtWebChannel import QWebChannel  # pyright: ignore[reportMissingImports]
from app.bridge.exam_bridge import ExamBridge
from app.bridge.question_import_bridge import QuestionImportBridge

from app.services.pdf_processor import PDFProcessor

base_dir = Path(__file__).parent

import ctypes

# Tells Windows to use the script's distinct AppUserModelID for taskbar grouping
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("al-mumeen.cbt.v1")


# This is the main function of our application.
def main():
    import sys
    from app.database.database import init_database

    init_database()
    # Create the Qt application.
    # sys.argv contains any arguments passed when starting the program.
    app = QApplication(sys.argv)

    # Create the Python object that JavaScript will communicate with.
    exam_bridge = ExamBridge()
    import_bridge = QuestionImportBridge()

    # Create a WebChannel for communication between Python and JavaScript.
    channel = QWebChannel()

    # Register our Python bridge for exam and question import
    channel.registerObject("examBridge", exam_bridge)
    channel.registerObject("questionImportBridge", import_bridge)

    # Set the icon for the application.
    icon_file = base_dir / "app" / "web" / "images" / "school_logo.ico"
    if not icon_file.exists():
        icon_file = base_dir / "app" / "web" / "images" / "al-mumeen.ico"
    if icon_file.exists():
        app.setWindowIcon(QIcon(str(icon_file)))

    # Create our desktop browser window.
    # This will eventually display our HTML + Tailwind + Alpine.js interface.
    window = QWebEngineView()

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

    # Set the title that appears on the Windows window.
    window.setWindowTitle("Al-Mumeen CBT")

    # Set the initial size of the application window.
    # The first value is width and the second is height.
    window.resize(1024, 768)

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
