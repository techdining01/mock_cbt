from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class IngestionWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CBT Question Ingestion")

        self.resize(1024, 768)

        self.current_file: Path | None = None

        self.build_ui()

    def build_ui(self):

        central = QWidget()

        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        # -------------------------------------------------
        # TOP BAR
        # -------------------------------------------------

        top_layout = QHBoxLayout()

        self.file_label = QLabel("No source selected")

        open_button = QPushButton("Open Source")

        open_button.clicked.connect(self.open_source)

        top_layout.addWidget(self.file_label)

        top_layout.addWidget(open_button)

        main_layout.addLayout(top_layout)

        # -------------------------------------------------
        # MAIN AREA
        # -------------------------------------------------

        content_layout = QHBoxLayout()

        # PAGE LIST

        self.page_list = QListWidget()

        content_layout.addWidget(
            self.page_list,
            1,
        )

        # PAGE PREVIEW

        self.page_preview = QLabel("Page preview")

        self.page_preview.setMinimumWidth(500)

        self.page_preview.setStyleSheet("border: 1px solid gray;")

        content_layout.addWidget(
            self.page_preview,
            3,
        )

        # QUESTION EDITOR

        editor = QWidget()

        editor_layout = QVBoxLayout(editor)

        editor_layout.addWidget(QLabel("Question Number"))

        self.question_number = QLineEdit()

        editor_layout.addWidget(self.question_number)

        editor_layout.addWidget(QLabel("Question"))

        self.question_text = QTextEdit()

        editor_layout.addWidget(self.question_text)

        self.option_fields = {}

        for label in "ABCD":
            editor_layout.addWidget(QLabel(f"Option {label}"))

            field = QLineEdit()

            self.option_fields[label] = field

            editor_layout.addWidget(field)

        select_image_button = QPushButton("Select Diagram Region")

        select_image_button.clicked.connect(self.select_image_region)

        editor_layout.addWidget(select_image_button)

        save_button = QPushButton("Save Question Draft")

        save_button.clicked.connect(self.save_question)

        editor_layout.addWidget(save_button)

        content_layout.addWidget(
            editor,
            3,
        )

        main_layout.addLayout(content_layout)

    def open_source(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Past Question",
            "",
            "Documents (*.pdf *.png *.jpg *.jpeg)",
        )

        if not file_path:
            return

        self.current_file = Path(file_path)

        self.file_label.setText(str(self.current_file))

    def select_image_region(self):

        QMessageBox.information(
            self,
            "Diagram Selection",
            "Region selection will be enabled when the page canvas is added.",
        )

    def save_question(self):

        QMessageBox.information(
            self,
            "Saved",
            "Question draft saved.",
        )
