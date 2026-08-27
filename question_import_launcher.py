import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
from PySide6.QtGui import QIcon

from PySide6.QtWebChannel import QWebChannel
from app.bridge.question_import_bridge import QuestionImportBridge

base_dir = Path(__file__).parent

def main():
    from app.database.database import init_database

    init_database()
    
    # Create the Qt application
    app = QApplication(sys.argv)

    # Create the Python object for question import bridge
    import_bridge = QuestionImportBridge()

    # Create a WebChannel for communication
    channel = QWebChannel()

    # Register the question import bridge
    channel.registerObject("questionImportBridge", import_bridge)

    # Set the icon
    app.setWindowIcon(QIcon(str(base_dir / "app" / "web" / "images" / "company_logo.ico")))

    # Create the browser window
    window = QWebEngineView()

    # Give the communication channel to the web page
    window.page().setWebChannel(channel)

    # Set the title
    window.setWindowTitle("Question Import")

    # Set the initial size
    window.resize(800, 600)

    # Build the full path to question_import.html
    html_file = base_dir / "app" / "web" / "question_import.html"

    # Convert to QUrl
    html_url = QUrl.fromLocalFile(str(html_file))

    # Load the HTML page
    window.setUrl(html_url)

    # Make the window visible
    window.show()

    # Start Qt's event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
