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
from PySide6.QtCore import QUrl  # pyright: ignore[reportMissingImports]
from PySide6.QtGui import QIcon  # pyright: ignore[reportMissingImports]

from PySide6.QtWebChannel import QWebChannel  # pyright: ignore[reportMissingImports]
from app.bridge.exam_bridge import ExamBridge



base_dir = Path(__file__).parent


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

    # Create a WebChannel for communication between Python and JavaScript.
    channel = QWebChannel()

    # Register our Python bridge under the name "exam_bridge".
    channel.registerObject("examBridge", exam_bridge)

    # Set the icon for the application.
    app.setWindowIcon(QIcon(str(base_dir / "app" / "assets" / "alayande.png")))

    # Create our desktop browser window.
    # This will eventually display our HTML + Tailwind + Alpine.js interface.
    window = QWebEngineView()

    # Give the communication channel to the web page.
    window.page().setWebChannel(channel)

    # Set the title that appears on the Windows window.
    window.setWindowTitle("Mock CBT")

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


