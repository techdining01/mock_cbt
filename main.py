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

import os
import sys
from pathlib import Path
import ctypes

# Suppress Chromium D3D11 / DirectComposition HDR probe warnings and window flickering on Windows
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
    "--disable-gpu-compositing "
    "--disable-direct-composition "
    "--disable-direct-composition-video-overlays "
    "--disable-features=HardwareMediaKeyHandling,DirectCompositionVideoOverlays "
    "--log-level=3"
)

# Tells Windows to use the script's distinct AppUserModelID for taskbar grouping
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("alayande.cbt.v1")

from PySide6.QtCore import Qt, QCoreApplication, QUrl
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QIcon, QColor
from PySide6.QtWebChannel import QWebChannel
from app.bridge.exam_bridge import ExamBridge


base_dir = Path(__file__).parent


# This is the main function of our application.
def main():
    from app.database.database import init_database
    init_database()

    # Share OpenGL contexts to prevent driver context stall
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

    # Create the Qt application.
    app = QApplication(sys.argv)

    # Create the Python object that JavaScript will communicate with.
    exam_bridge = ExamBridge()

    # Create a WebChannel for communication between Python and JavaScript.
    channel = QWebChannel()

    # Register our Python bridge under the name "examBridge".
    channel.registerObject("examBridge", exam_bridge)

    # Set the icon for the application.
    app.setWindowIcon(QIcon(str(base_dir / "app" / "web" / "images" / "alayande.png")))

    # Create our desktop browser window.
    window = QWebEngineView()
    window.page().setBackgroundColor(QColor("#f8fafc"))

    # Connect bridge with window for direct print control
    exam_bridge.set_window(window)

    # Native Qt Print Handler for window.print() requests
    def handle_print_requested():
        try:
            from PySide6.QtPrintSupport import QPrintDialog, QPrinter
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            dialog = QPrintDialog(printer, window)
            dialog.setWindowTitle("Print CBT Examination Document")
            if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                window.page().print(printer, lambda res: None)
        except Exception as err:
            print("Native print handler error:", err)

    window.page().printRequested.connect(handle_print_requested)

    # Give the communication channel to the web page.
    window.page().setWebChannel(channel)

    # Set the title that appears on the Windows window.
    window.setWindowTitle("Mock CBT Examination Engine")

    # Set the initial size of the application window.
    # The first value is width and the second is height.
    window.resize(1200, 800)

    # Get the path to our local HTML file.
    # __file__ represents the location of this main.py file.
    # We use it to build the path to app/web/index.html.
    
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


