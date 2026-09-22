
import ctypes
import json
import os
import sys
import time
import threading
from pathlib import Path

import requests
from dotenv import load_dotenv


# ==============================================================================
# APPLICATION PATHS
# ==============================================================================

def _get_app_base_dir() -> Path:
    """
    Resolve the application base directory.

    PyInstaller one-dir:
        <application>/_internal

    Development:
        project directory
    """
    if getattr(sys, "frozen", False):
        meipass = Path(
            getattr(sys, "_MEIPASS", sys.executable)
        ).resolve()

        if meipass.is_dir():
            return meipass

        return meipass.parent

    return Path(__file__).resolve().parent


def _get_user_data_dir() -> Path:
    """
    Directory for user-editable application files.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


# ==============================================================================
# ENVIRONMENT
# ==============================================================================

def _load_environment() -> None:
    """
    Load .env variables.

    Priority:
        1. Existing process environment
        2. Bundled .env
        3. .env beside executable
    """

    app_dir = _get_app_base_dir()
    user_dir = _get_user_data_dir()

    candidate_paths = [
        app_dir / ".env",
        user_dir / ".env",
        (app_dir.parent / ".env")
        if app_dir.name == "_internal"
        else None,
    ]

    for candidate in candidate_paths:

        if candidate is None:
            continue

        if candidate.is_file():

            try:
                load_dotenv(
                    candidate,
                    override=False,
                    encoding="utf-8",
                )

                print(
                    f"[env] Loaded: {candidate}",
                    flush=True,
                )

            except Exception as exc:

                print(
                    f"[env] Failed to load {candidate}: {exc}",
                    flush=True,
                )

    _fix_ssl_cert_path(app_dir)


def _fix_ssl_cert_path(app_dir: Path) -> None:
    """
    Configure CA certificate locations for HTTPS clients.
    """

    try:
        import certifi
    except Exception:
        return

    pem_candidates = [
        Path(certifi.where()),
        app_dir / "certifi" / "cacert.pem",
    ]

    for pem in pem_candidates:

        if pem and pem.is_file():

            os.environ.setdefault(
                "SSL_CERT_FILE",
                str(pem),
            )

            os.environ.setdefault(
                "REQUESTS_CA_BUNDLE",
                str(pem),
            )

            os.environ.setdefault(
                "CURL_CA_BUNDLE",
                str(pem),
            )

            break


_load_environment()


# ==============================================================================
# PYQT / PYSIDE
# ==============================================================================

from PySide6.QtWidgets import (
    QApplication,
    QSplashScreen,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtCore import (
    QUrl,
    QTimer,
    Qt,
)
from PySide6.QtGui import (
    QIcon,
    QPixmap,
)


# ==============================================================================
# APPLICATION BASE DIRECTORY
# ==============================================================================

base_dir = _get_app_base_dir()


# ==============================================================================
# ICON
# ==============================================================================

icon_candidates = [
    base_dir
    / "app"
    / "web"
    / "images"
    / "company_logo.ico",
]

icon_file = next(
    (
        file
        for file in icon_candidates
        if file.exists()
    ),
    None,
)

# ==============================================================================
# SPLASH SCREEN
# ==============================================================================


class LLSSplash(QSplashScreen):
    """
    Native LLS-CBT startup splash.
    """

    def __init__(self, pixmap: QPixmap):
        super().__init__(
            pixmap,
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint,
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground,
            False,
        )

        self.setStyleSheet(
            """
            QSplashScreen {
                background: white;
                border: none;
            }
            """
        )

    def set_status(self, message: str) -> None:
        self.showMessage(
            message,
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
            Qt.GlobalColor.darkGray,
        )

        QApplication.processEvents()


def create_splash() -> LLSSplash:
    """
    Create a proper branded LLS-CBT splash.

    The company ICO is used as the logo rather than being used
    as the entire splash image.
    """

    from PySide6.QtGui import (
        QPainter,
        QFont,
    )

    # --------------------------------------------------------------------------
    # Splash dimensions
    # --------------------------------------------------------------------------

    width = 560
    height = 360

    splash_pixmap = QPixmap(
        width,
        height,
    )

    splash_pixmap.fill(Qt.GlobalColor.white)

    # --------------------------------------------------------------------------
    # Painter
    # --------------------------------------------------------------------------

    painter = QPainter(splash_pixmap)

    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    # --------------------------------------------------------------------------
    # Logo
    # --------------------------------------------------------------------------

    if icon_file and icon_file.exists():
        logo = QIcon(str(icon_file)).pixmap(
            150,
            150,
        )

        logo_x = (width - logo.width()) // 2

        logo_y = 45

        painter.drawPixmap(
            logo_x,
            logo_y,
            logo,
        )

    # --------------------------------------------------------------------------
    # Application name
    # --------------------------------------------------------------------------

    title_font = QFont(
        "Segoe UI",
        24,
        QFont.Weight.Bold,
    )

    painter.setFont(title_font)

    painter.setPen(Qt.GlobalColor.black)

    title_rect = painter.boundingRect(
        0,
        205,
        width,
        45,
        Qt.AlignmentFlag.AlignCenter,
        "LLS-CBT",
    )

    painter.drawText(
        title_rect,
        Qt.AlignmentFlag.AlignCenter,
        "LLS-CBT",
    )

    # --------------------------------------------------------------------------
    # Subtitle
    # --------------------------------------------------------------------------

    subtitle_font = QFont(
        "Segoe UI",
        11,
        QFont.Weight.Normal,
    )

    painter.setFont(subtitle_font)

    painter.setPen(Qt.GlobalColor.darkGray)

    subtitle_rect = painter.boundingRect(
        0,
        245,
        width,
        30,
        Qt.AlignmentFlag.AlignCenter,
        "Computer Based Testing",
    )

    painter.drawText(
        subtitle_rect,
        Qt.AlignmentFlag.AlignCenter,
        "Computer Based Testing",
    )

    # --------------------------------------------------------------------------
    # Loading/status area
    # --------------------------------------------------------------------------

    status_font = QFont(
        "Segoe UI",
        9,
        QFont.Weight.Normal,
    )

    painter.setFont(status_font)

    painter.setPen(Qt.GlobalColor.gray)

    status_rect = painter.boundingRect(
        0,
        310,
        width,
        25,
        Qt.AlignmentFlag.AlignCenter,
        "Starting LLS-CBT...",
    )

    painter.drawText(
        status_rect,
        Qt.AlignmentFlag.AlignCenter,
        "Starting LLS-CBT...",
    )

    painter.end()

    return LLSSplash(splash_pixmap)


# ==============================================================================
# AI TUTOR SERVER
# ==============================================================================

def start_ai_tutor_server():

    import traceback
    log_file = Path(sys.executable).parent / "ai_tutor_server.log"

    def log(msg):
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
        print(msg, flush=True)

    log("[AI Tutor Server] Starting...")

    try:

        import asyncio

        # Required on Windows in a frozen PyInstaller EXE.
        # The default ProactorEventLoop is incompatible with uvicorn's asyncio loop.
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        import uvicorn

        log("[AI Tutor Server] Imports OK")

        from app.ai_tutor.main import app as tutor_app

        log("[AI Tutor Server] App imported OK")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        config = uvicorn.Config(
            tutor_app,
            host="127.0.0.1",
            port=8000,
            log_level="warning",
            loop="asyncio",
            log_config=None,
        )

        server = uvicorn.Server(config)

        log("[AI Tutor Server] Server created, serving...")

        loop.run_until_complete(server.serve())

    except Exception as exc:

        log(f"[AI Tutor Server Error]: {exc}")
        log(f"[AI Tutor Server Traceback]: {traceback.format_exc()}")


# ==============================================================================
# WINDOWS APP USER MODEL ID
# ==============================================================================

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
    "logiclanesolutions.cbt.v1"
)


# ==============================================================================
# LOCAL API
# ==============================================================================

LOCAL_API_BASE_URL = os.getenv(
    "LOCAL_API_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


def wait_for_server(
    url: str | None = None,
    max_retries: int = 10,
    delay: float = 0.5,
) -> bool:
    """
    Wait for FastAPI to become reachable.
    """

    if not url:
        url = LOCAL_API_BASE_URL

    for _ in range(max_retries):

        try:

            response = requests.get(
                f"{url}/",
                timeout=1,
            )

            if response.status_code == 200:
                return True

        except requests.RequestException:

            time.sleep(delay)

    return False


# ==============================================================================
# LICENSE
# ==============================================================================

def check_license() -> bool:

    try:

        from app.services.licensing.client import LicenseClient

        client = LicenseClient()

        # Existing local license.
        if client.is_licensed():

            print(
                "License validated successfully.",
                flush=True,
            )

            return True

        # Development bypass.
        if os.getenv("SKIP_LICENSE_CHECK") == "true":

            print(
                "License check skipped (development mode)",
                flush=True,
            )

            return True

        # Environment activation.
        license_key = os.getenv(
            "PRODUCT_KEY"
        )

        if license_key:

            print(
                "Attempting to activate license with environment key...",
                flush=True,
            )

            result = client.activate_license(
                license_key
            )

            if result["success"]:

                print(
                    "License activated successfully. "
                    f"Remaining credits: "
                    f"{result['remaining_credits']}",
                    flush=True,
                )

                return True

            print(
                f"License activation failed: "
                f"{result['message']}",
                flush=True,
            )

        return False

    except Exception as exc:

        print(
            f"License check error: {exc}",
            flush=True,
        )

        if os.getenv("SKIP_LICENSE_CHECK") == "true":

            print(
                "License check skipped due to error "
                "(development mode)",
                flush=True,
            )

            return True

        return False


# ==============================================================================
# MAIN APPLICATION
# ==============================================================================

def main():

    # ==========================================================================
    # CHROMIUM FLAGS
    #
    # MUST BE SET BEFORE QApplication.
    # ==========================================================================

    chromium_flags = [
        "--disable-web-security",
        "--allow-file-access-from-files",
        "--allow-running-insecure-content",
        "--disable-features=BlockInsecurePrivateNetworkRequests",
        "--enable-system-color-emoji",
        "--disable-gpu-compositing",
    ]

    for flag in chromium_flags:

        if flag not in sys.argv:
            sys.argv.append(flag)

    # ==========================================================================
    # QT APPLICATION
    # ==========================================================================

    app = QApplication(sys.argv)

    app.setApplicationName(
        "LLS-CBT"
    )

    app.setApplicationDisplayName(
        "LLS CBT"
    )

    if icon_file:

        app.setWindowIcon(
            QIcon(str(icon_file))
        )

    # ==========================================================================
    # SPLASH
    # ==========================================================================

    splash = create_splash()

    splash.show()

    QApplication.processEvents()

    splash.set_status(
        "Starting LLS-CBT..."
    )

    # ==========================================================================
    # DATABASE
    # ==========================================================================

    splash.set_status(
        "Initializing database..."
    )

    from app.database.database import init_database

    init_database()

    QApplication.processEvents()

    # ==========================================================================
    # LOCAL FASTAPI SERVER
    # ==========================================================================

    splash.set_status(
        "Starting application services..."
    )

    server_thread = threading.Thread(
        target=start_ai_tutor_server,
        daemon=True,
    )

    server_thread.start()

    # ==========================================================================
    # WAIT FOR API
    # ==========================================================================

    splash.set_status(
        "Starting AI services..."
    )

    server_ready = wait_for_server(
        LOCAL_API_BASE_URL,
        max_retries=20,
        delay=0.5,
    )

    if server_ready:

        splash.set_status(
            "Application services ready..."
        )

    else:

        print(
            "Warning: Local API did not become ready "
            "within the startup timeout.",
            flush=True,
        )

        splash.set_status(
            "Continuing startup..."
        )

    # ==========================================================================
    # LICENSE
    # ==========================================================================

    splash.set_status(
        "Checking product license..."
    )

    license_valid = check_license()

    if not license_valid:

        splash.hide()

        print(
            "License validation failed. "
            "Showing activation dialog...",
            flush=True,
        )

        from app.services.licensing.client import LicenseClient

        from app.ui.license_activation_dialog import (
            show_activation_dialog,
        )

        license_client = LicenseClient()

        activation_success = show_activation_dialog(
            license_client
        )

        if not activation_success:

            print(
                "License activation cancelled or failed. "
                "Exiting application.",
                flush=True,
            )

            sys.exit(1)

        print(
            "License activated successfully. "
            "Starting application...",
            flush=True,
        )

        splash.show()

        splash.set_status(
            "License activated. Loading application..."
        )

    # ==========================================================================
    # BRIDGES
    # ==========================================================================

    splash.set_status(
        "Preparing application interface..."
    )

    from PySide6.QtWebChannel import QWebChannel

    from app.bridge.exam_bridge import (
        ExamBridge,
    )

    from app.bridge.question_import_bridge import (
        QuestionImportBridge,
    )

    exam_bridge = ExamBridge()

    import_bridge = QuestionImportBridge()

    # ==========================================================================
    # WEB CHANNEL
    # ==========================================================================

    channel = QWebChannel()

    channel.registerObject(
        "examBridge",
        exam_bridge,
    )

    channel.registerObject(
        "questionImportBridge",
        import_bridge,
    )

    # ==========================================================================
    # WEB ENGINE
    # ==========================================================================

    splash.set_status(
        "Loading LLS-CBT interface..."
    )

    window = QWebEngineView()

    # Keep completely invisible until HTML has rendered.
    window.setWindowOpacity(
        0.0
    )

    # ==========================================================================
    # WEB ENGINE SETTINGS
    # ==========================================================================

    settings = window.settings()

    settings.setAttribute(
        QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls,
        True,
    )

    settings.setAttribute(
        QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls,
        True,
    )

    # ==========================================================================
    # EXAM BRIDGE
    # ==========================================================================

    exam_bridge.set_web_view(
        window
    )

    # ==========================================================================
    # PRINT HANDLER
    # ==========================================================================

    def handle_print_requested():

        try:

            from PySide6.QtPrintSupport import (
                QPrintDialog,
                QPrinter,
            )

            printer = QPrinter(
                QPrinter.PrinterMode.HighResolution
            )

            dialog = QPrintDialog(
                printer,
                window,
            )

            dialog.setWindowTitle(
                "Print CBT Document"
            )

            if dialog.exec() == QPrintDialog.DialogCode.Accepted:

                window.page().print(
                    printer,
                    lambda result: None,
                )

        except Exception as err:

            print(
                f"Native print handler error: {err}",
                flush=True,
            )

    window.page().printRequested.connect(
        handle_print_requested
    )

    # ==========================================================================
    # WEB CHANNEL
    # ==========================================================================

    window.page().setWebChannel(
        channel
    )

    # ==========================================================================
    # WINDOW
    # ==========================================================================

    window.setWindowTitle(
        "LLS CBT"
    )

    if icon_file:

        window.setWindowIcon(
            QIcon(str(icon_file))
        )

    window.resize(
        800,
        600,
    )

    # ==========================================================================
    # HTML
    # ==========================================================================

    html_file = (
        base_dir
        / "app"
        / "web"
        / "index.html"
    )

    html_url = QUrl.fromLocalFile(
        str(html_file)
    )

    html_content = html_file.read_text(
        encoding="utf-8"
    )

    # ==========================================================================
    # INJECT APPLICATION CONFIGURATION
    # ==========================================================================

    config_script = (
        '<script id="__INJECTED_APP_CONFIG__" '
        'type="application/json">'
        + json.dumps(
            {
                "apiBaseUrl": LOCAL_API_BASE_URL
            },
            ensure_ascii=False,
        )
        + "</script>"
        "<script>"
        'try { '
        'const el = document.getElementById('
        '"__INJECTED_APP_CONFIG__"'
        ");"
        "if (el) { "
        "window.__APP_CONFIG__ = "
        "JSON.parse(el.textContent); "
        "}"
        "} catch (_) { }"
        "</script>"
    )

    head_index = html_content.find(
        "<head"
    )

    if head_index >= 0:

        after_head = html_content.find(
            ">",
            head_index,
        )

        if after_head >= 0:

            html_content = (
                html_content[
                    :after_head + 1
                ]
                + config_script
                + html_content[
                    after_head + 1:
                ]
            )

    else:

        html_content = (
            config_script
            + html_content
        )

    # ==========================================================================
    # PAGE LOAD
    # ==========================================================================

    page_ready = {
        "done": False
    }

    def reveal_window(ok: bool):

        if not ok:

            splash.set_status(
                "Unable to load application interface."
            )

            print(
                "ERROR: index.html failed to load.",
                flush=True,
            )

            # Give the user a moment to see the error.
            QTimer.singleShot(
                1500,
                splash.close,
            )

            return

        if page_ready["done"]:
            return

        page_ready["done"] = True

        splash.set_status(
            "LLS-CBT ready."
        )

        def show_main_window():

            splash.close()

            window.setWindowOpacity(
                1.0
            )

            window.show()

            window.raise_()

            window.activateWindow()

        # Small grace period allows Chromium to finish its
        # first rasterization/paint.
        QTimer.singleShot(
            300,
            show_main_window,
        )

    window.loadFinished.connect(
        reveal_window
    )

    # ==========================================================================
    # LOAD CONTENT
    # ==========================================================================

    window.page().setContent(
        html_content.encode("utf-8"),
        "text/html;charset=utf-8",
        html_url,
    )

    # ==========================================================================
    # FAILSAFE
    # ==========================================================================

    def startup_failsafe():

        if page_ready["done"]:
            return

        print(
            "Warning: WebEngine startup timeout.",
            flush=True,
        )

        splash.set_status(
            "Finalizing application..."
        )

        splash.close()

        window.setWindowOpacity(
            1.0
        )

        window.show()

        window.raise_()

        window.activateWindow()

    QTimer.singleShot(
        15000,
        startup_failsafe,
    )

    # ==========================================================================
    # START EVENT LOOP
    # ==========================================================================

    sys.exit(
        app.exec()
    )


# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    main()

