# from __future__ import annotations

# import json
# from pathlib import Path

# import pymupdf

# from PySide6.QtCore import QObject, Slot
# from PySide6.QtWidgets import QFileDialog

# from app.services.questions_importer import QuestionImporter

# import base64

# from app.services.ocr_ingestion.ocr_service import OCRService
# from app.services.ocr_ingestion.question_parser import QuestionParser
# from app.services.question_import_review import QuestionImportReviewService


# class QuestionImportBridge(QObject):

#     def __init__(self):
#         super().__init__()

#         self.pdf_path: Path | None = None
#         self.document = None
#         self.current_page = 0

#         self.zoom = 1.0

#         self.ocr_service = OCRService()
#         self.question_parser = QuestionParser()

#         self.import_data = {
#             "year": None,
#             "subjects": [],
#         }

#     # =========================================================
#     # OPEN QUESTION PAPER
#     # =========================================================

#     @Slot(result=str)
#     def open_question_paper(self):

#         path, _ = QFileDialog.getOpenFileName(
#             None,
#             "Open Question Paper",
#             "",
#             "Question Papers (*.pdf *.png *.jpg *.jpeg);;PDF Files (*.pdf);;Images (*.png *.jpg *.jpeg)",
#         )

#         if not path:
#             return self._success(
#                 {
#                     "cancelled": True,
#                 }
#             )

#         self.pdf_path = Path(path)

#         if self.pdf_path.suffix.lower() == ".pdf":

#             self.document = pymupdf.open(
#                 str(self.pdf_path)
#             )

#             self.current_page = 0

#             return self._success(
#                 {
#                     "type": "pdf",
#                     "path": str(self.pdf_path),
#                     "name": self.pdf_path.name,
#                     "page_count": len(self.document),
#                     "page": 0,
#                 }
#             )

#         return self._success(
#             {
#                 "type": "image",
#                 "path": str(self.pdf_path),
#                 "name": self.pdf_path.name,
#                 "page_count": 1,
#                 "page": 0,
#             }
#         )

#     # =========================================================
#     # GET PAGE
#     # =========================================================

#     @Slot(int, result=str)
#     def get_page(self, page_number: int):

#         if self.document is None:
#             return self._error(
#                 "No document loaded."
#             )

#         if page_number < 0 or page_number >= len(self.document):
#             return self._error(
#                 "Invalid page number."
#             )

#         page = self.document.load_page(
#             page_number
#         )

#         pixmap = page.get_pixmap(
#             matrix=pymupdf.Matrix(
#                 self.zoom,
#                 self.zoom,
#             ),
#             alpha=False,
#         )

#         image_data = pixmap.tobytes(
#             "png"
#         )

#         import base64

#         encoded = base64.b64encode(
#             image_data
#         ).decode("ascii")

#         self.current_page = page_number

#         return self._success(
#             {
#                 "page": page_number,
#                 "width": pixmap.width,
#                 "height": pixmap.height,
#                 "image": encoded,
#             }
#         )

#     # =========================================================
#     # THUMBNAILS
#     # =========================================================

#     @Slot(int, result=str)
#     def get_thumbnail(self, page_number: int):

#         if self.document is None:
#             return self._error(
#                 "No document loaded."
#             )

#         if page_number < 0 or page_number >= len(self.document):
#             return self._error(
#                 "Invalid page number."
#             )

#         page = self.document.load_page(
#             page_number
#         )

#         matrix = pymupdf.Matrix(
#             0.25,
#             0.25,
#         )

#         pixmap = page.get_pixmap(
#             matrix=matrix,
#             alpha=False,
#         )

#         import base64

#         encoded = base64.b64encode(
#             pixmap.tobytes("png")
#         ).decode("ascii")

#         return self._success(
#             {
#                 "page": page_number,
#                 "image": encoded,
#             }
#         )

#     # =========================================================
#     # ZOOM
#     # =========================================================

#     @Slot(float, result=str)
#     def set_zoom(self, zoom: float):

#         self.zoom = max(
#             0.25,
#             min(3.0, float(zoom)),
#         )

#         return self.get_page(
#             self.current_page
#         )

#     # =========================================================
#     # CROP
#     # =========================================================

#     @Slot(int, int, int, int, result=str)
#     def crop_region(
#         self,
#         x: int,
#         y: int,
#         width: int,
#         height: int,
#     ):

#         if self.document is None:
#             return self._error(
#                 "No document loaded."
#             )

#         page = self.document.load_page(
#             self.current_page
#         )

#         rect = pymupdf.Rect(
#             x / self.zoom,
#             y / self.zoom,
#             (x + width) / self.zoom,
#             (y + height) / self.zoom,
#         )

#         pixmap = page.get_pixmap(
#             clip=rect,
#             matrix=pymupdf.Matrix(
#                 2,
#                 2,
#             ),
#             alpha=False,
#         )

#         import base64

#         encoded = base64.b64encode(
#             pixmap.tobytes("png")
#         ).decode("ascii")

#         return self._success(
#             {
#                 "image": encoded,
#                 "page": self.current_page,
#                 "x": x,
#                 "y": y,
#                 "width": width,
#                 "height": height,
#             }
#         )

# # =========================================================
# # SAVE CROPPED DIAGRAM TO REVIEW
# # =========================================================


#     @Slot(
#         str,
#         int,
#         int,
#         int,
#         int,
#         result=str,
#     )
#     def save_diagram(
#         self,
#         question_number: str,
#         x: int,
#         y: int,
#         width: int,
#         height: int,
#     ):

#         if self.document is None:
#             return self._error("No document loaded.")

#         try:
#             question_number = int(question_number)

#             page = self.document.load_page(self.current_page)

#             rect = pymupdf.Rect(
#                 x / self.zoom,
#                 y / self.zoom,
#                 (x + width) / self.zoom,
#                 (y + height) / self.zoom,
#             )

#             pixmap = page.get_pixmap(
#                 clip=rect,
#                 matrix=pymupdf.Matrix(
#                     2,
#                     2,
#                 ),
#                 alpha=False,
#             )

#             output_dir = Path("data") / "question_import_review"

#             output_dir.mkdir(
#                 parents=True,
#                 exist_ok=True,
#             )

#             filename = f"question_{question_number}_page_{self.current_page + 1}.png"

#             output_path = output_dir / filename

#             pixmap.save(str(output_path))

#             relative_path = str(output_path).replace("\\", "/")

#             # -----------------------------------------------
#             # Attach image to temporary review data
#             # -----------------------------------------------

#             for subject in self.import_data.get(
#                 "subjects",
#                 [],
#             ):
#                 for question in subject.get(
#                     "questions",
#                     [],
#                 ):
#                     if question["number"] == question_number:
#                         question.setdefault("images", [])

#                         question["images"].append(relative_path)

#                         question["source_page"] = self.current_page + 1

#                         return self._success(
#                             {
#                                 "question_number": question_number,
#                                 "page": self.current_page + 1,
#                                 "path": relative_path,
#                             }
#                         )

#             return self._error(f"Question {question_number} was not found in the review.")

#         except Exception as exc:
#             return self._error(exc)

#     # =========================================================
#     # CLOSE DOCUMENT
#     # =========================================================

#     @Slot(result=str)
#     def reset_document(self):

#         if self.document is not None:
#             self.document.close()

#         self.document = None
#         self.pdf_path = None
#         self.current_page = 0
#         self.zoom = 1.0

#         return self._success(
#             {
#                 "document": None,
#             }
#         )

#     # =========================================================
#     # HELPERS
#     # =========================================================

#     @staticmethod
#     def _success(data):

#         return json.dumps(
#             {
#                 "success": True,
#                 **data,
#             }
#         )

#     @staticmethod
#     def _error(message):

#         return json.dumps(
#             {
#                 "success": False,
#                 "error": str(message),
#             }
#         )


# # =========================================================
# # OCR CURRENT PAGE
# # =========================================================

# @Slot(result=str)
# def ocr_current_page(self):

#     if self.document is None:
#         return self._error("No document loaded.")

#     try:
#         page = self.document.load_page(self.current_page)

#         pixmap = page.get_pixmap(
#             matrix=pymupdf.Matrix(
#                 2,
#                 2,
#             ),
#             alpha=False,
#         )

#         image_bytes = pixmap.tobytes("png")

#         text = self.ocr_service.extract_bytes(image_bytes)

#         return self._success(
#             {
#                 "page": self.current_page,
#                 "text": text,
#             }
#         )

#     except Exception as exc:
#         return self._error(exc)


# # =========================================================
# # EXTRACT QUESTIONS
# # =========================================================


# @Slot(int, str, result=str)
# def extract_questions(
#     self,
#     year: int,
#     subject_name: str,
# ):

#     if self.document is None:
#         return self._error("No document loaded.")

#     try:
#         all_text = []

#         for page_number in range(len(self.document)):
#             page = self.document.load_page(page_number)

#             pixmap = page.get_pixmap(
#                 matrix=pymupdf.Matrix(
#                     2,
#                     2,
#                 ),
#                 alpha=False,
#             )

#             image_bytes = pixmap.tobytes("png")

#             text = self.ocr_service.extract_bytes(image_bytes)

#             if text:
#                 all_text.append(text)

#         combined_text = "\n".join(all_text)

#         parsed_questions = self.question_parser.parse(combined_text)

#         questions = []

#         for parsed in parsed_questions:
#             options = []

#             for label, option_text in parsed["options"].items():
#                 options.append(
#                     {
#                         "label": label,
#                         "text": option_text,
#                         "is_correct": False,
#                     }
#                 )

#             questions.append(
#                 {
#                     "number": parsed["question_number"],
#                     "text": parsed["text"],
#                     "options": options,
#                     "images": [],
#                     "source_page": None,
#                 }
#             )

#         self.import_data = {
#             "year": int(year),
#             "subjects": [
#                 {
#                     "name": subject_name,
#                     "questions": questions,
#                 }
#             ],
#         }

#         return self._success(
#             {
#                 "year": int(year),
#                 "subject": subject_name,
#                 "questions": questions,
#             }
#         )

#     except Exception as exc:
#         return self._error(exc)


# # =========================================================
# # SAVE REVIEW
# # =========================================================


# @Slot(str, result=str)
# def save_review(
#     self,
#     review_json: str,
# ):

#     try:
#         data = json.loads(review_json)

#         # Basic validation
#         if not isinstance(
#             data,
#             dict,
#         ):
#             raise ValueError("Invalid review data.")

#         if "year" not in data:
#             raise ValueError("Examination year is required.")

#         if "subjects" not in data:
#             raise ValueError("Subject data is required.")

#         from app.database.database import SessionLocal

#         with SessionLocal() as db:
#             importer = QuestionImporter(db)

#             result = importer.import_data(data)

#         return self._success(
#             {
#                 "imported": result["imported"],
#                 "skipped": result["skipped"],
#             }
#         )

#     except Exception as exc:
#         return self._error(exc)


# # =========================================================
# # GET REVIEW
# # =========================================================


# @Slot(result=str)
# def get_review(self):

#     return self._success({"review": self.import_data})


from __future__ import annotations

import base64
import json
import tempfile
import uuid
from pathlib import Path

import pymupdf

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QFileDialog

from app.database.database import SessionLocal
from app.services.ocr_ingestion.ocr_service import OCRService
from app.services.ocr_ingestion.question_parser import QuestionParser
from app.services.questions_importer import QuestionImporter


class QuestionImportBridge(QObject):
    def __init__(self):
        super().__init__()

        self.pdf_path: Path | None = None
        self.document = None
        self.current_page = 0
        self.zoom = 1.0

        self.import_id: str | None = None
        self.import_dir: Path | None = None
        self.import_data = {
            "year": None,
            "subjects": [],
        }

        self.ocr_service = OCRService()
        self.question_parser = QuestionParser()

    # =========================================================
    # OPEN QUESTION PAPER
    # =========================================================

    @Slot(result=str)
    def open_question_paper(self):

        path, _ = QFileDialog.getOpenFileName(
            None,
            "Open Question Paper",
            "",
            (
                "Question Papers "
                "(*.pdf *.png *.jpg *.jpeg *.webp);;"
                "PDF Files (*.pdf);;"
                "Images (*.png *.jpg *.jpeg *.webp)"
            ),
        )

        if not path:
            return self._success(
                {
                    "cancelled": True,
                }
            )

        self.reset_state()

        self.pdf_path = Path(path)

        self.import_id = uuid.uuid4().hex

        base_dir = Path(__file__).resolve().parents[2]

        self.import_dir = base_dir / "data" / "question_imports" / self.import_id

        self.import_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        if self.pdf_path.suffix.lower() == ".pdf":
            self.document = pymupdf.open(str(self.pdf_path))

            self.current_page = 0

            return self._success(
                {
                    "type": "pdf",
                    "path": str(self.pdf_path),
                    "name": self.pdf_path.name,
                    "page_count": len(self.document),
                    "page": 0,
                    "import_id": self.import_id,
                }
            )

        return self._success(
            {
                "type": "image",
                "path": str(self.pdf_path),
                "name": self.pdf_path.name,
                "page_count": 1,
                "page": 0,
                "import_id": self.import_id,
            }
        )

    # =========================================================
    # GET PAGE
    # =========================================================

    @Slot(int, result=str)
    def get_page(
        self,
        page_number: int,
    ):

        if self.document is None:
            if (
                self.pdf_path
                and self.pdf_path.suffix.lower() != ".pdf"
                and page_number == 0
            ):
                try:
                    image_bytes = self.pdf_path.read_bytes()

                    encoded = base64.b64encode(image_bytes).decode("ascii")

                    self.current_page = 0

                    return self._success(
                        {
                            "page": 0,
                            "width": 0,
                            "height": 0,
                            "image": encoded,
                        }
                    )

                except Exception as exc:
                    return self._error(exc)

            return self._error("No document loaded.")

        if page_number < 0 or page_number >= len(self.document):
            return self._error("Invalid page number.")

        page = self.document.load_page(page_number)

        pixmap = page.get_pixmap(
            matrix=pymupdf.Matrix(
                self.zoom,
                self.zoom,
            ),
            alpha=False,
        )

        image_data = pixmap.tobytes("png")

        encoded = base64.b64encode(image_data).decode("ascii")

        self.current_page = page_number

        return self._success(
            {
                "page": page_number,
                "width": pixmap.width,
                "height": pixmap.height,
                "image": encoded,
            }
        )

    # =========================================================
    # THUMBNAILS
    # =========================================================

    @Slot(int, result=str)
    def get_thumbnail(
        self,
        page_number: int,
    ):

        if self.document is None:
            return self._error("No PDF document loaded.")

        if page_number < 0 or page_number >= len(self.document):
            return self._error("Invalid page number.")

        page = self.document.load_page(page_number)

        pixmap = page.get_pixmap(
            matrix=pymupdf.Matrix(
                0.25,
                0.25,
            ),
            alpha=False,
        )

        encoded = base64.b64encode(pixmap.tobytes("png")).decode("ascii")

        return self._success(
            {
                "page": page_number,
                "image": encoded,
            }
        )

    # =========================================================
    # ZOOM
    # =========================================================

    @Slot(float, result=str)
    def set_zoom(
        self,
        zoom: float,
    ):

        self.zoom = max(
            0.25,
            min(3.0, float(zoom)),
        )

        return self.get_page(self.current_page)

    # =========================================================
    # OCR
    # =========================================================

    def _collect_pdf_text(
        self,
        mode: str = "prefer_text_layer",
    ) -> list[str]:
        chunks: list[str] = []
        if self.document is None:
            return chunks
        ocr = self.ocr_service
        has_ocr = ocr.is_available()
        for page_index in range(len(self.document)):
            page = self.document.load_page(page_index)
            page_text = ""
            if mode in ("prefer_text_layer", "text_layer_only"):
                page_text = self._get_page_text(page) or ""
            if (
                mode == "ocr_only"
                or (
                    mode == "prefer_text_layer"
                    and not page_text.strip()
                    and has_ocr
                )
            ):
                if not has_ocr:
                    continue
                try:
                    pixmap = page.get_pixmap(
                        matrix=pymupdf.Matrix(2, 2),
                        alpha=False,
                    )
                    image_bytes = pixmap.tobytes("png")
                    with tempfile.NamedTemporaryFile(
                        suffix=".png", delete=False
                    ) as temp_file:
                        temp_path = Path(temp_file.name)
                        temp_file.write(image_bytes)
                    try:
                        page_text = ocr.extract_text(temp_path) or ""
                    finally:
                        try:
                            temp_path.unlink(missing_ok=True)
                        except Exception:
                            pass
                except Exception:
                    pass
            if page_text.strip():
                chunks.append(page_text)
        return chunks

    def _collect_image_text(self) -> list[str]:
        chunks: list[str] = []
        if self.pdf_path is None or self.pdf_path.suffix.lower() == ".pdf":
            return chunks
        if not self.ocr_service.is_available():
            return chunks
        try:
            image_text = self.ocr_service.extract_text(self.pdf_path) or ""
            if image_text.strip():
                chunks.append(image_text)
        except Exception:
            pass
        return chunks

    @Slot(int, str, result=str)
    def extract_questions(
        self,
        year: int,
        subject_name: str,
    ):

        if self.document is None and self.pdf_path is None:
            return self._error("No document loaded.")

        try:
            is_pdf = self.document is not None
            is_image = (
                self.pdf_path is not None
                and self.pdf_path.suffix.lower() != ".pdf"
            )

            if is_pdf:
                all_text = self._collect_pdf_text("prefer_text_layer")
            elif is_image:
                if not self.ocr_service.is_available():
                    return self._error(
                        "Tesseract OCR is required to extract text from images. "
                        "Please install Tesseract OCR."
                    )
                all_text = self._collect_image_text()
                if not all_text:
                    return self._error(
                        "Failed to process image with OCR. "
                        "Try a clearer image or install Tesseract."
                    )
            else:
                all_text = []

            combined_text = "\n".join(all_text)

            if is_pdf and self.ocr_service.is_available():
                parsed = self.question_parser.parse(combined_text)
                if len(parsed) == 0:
                    ocr_chunks = self._collect_pdf_text("ocr_only")
                    if ocr_chunks:
                        combined_text = "\n".join(ocr_chunks)

            if self.import_dir:
                try:
                    debug_file = self.import_dir / "extracted_text.txt"
                    debug_file.write_text(combined_text, encoding="utf-8")
                except Exception:
                    pass

            if not combined_text.strip():
                return self._error(
                    "No readable text found. Install Tesseract OCR or use a text-based PDF."
                )

            parsed = self.question_parser.parse(combined_text)

            if not parsed:
                return self._error(
                    "No questions could be extracted from the document. "
                    "Try a clearer scan or a text-based PDF."
                )

            questions = []

            for item in parsed:
                options = []

                for label in (
                    "A",
                    "B",
                    "C",
                    "D",
                    "E",
                ):
                    options.append(
                        {
                            "label": label,
                            "text": item["options"].get(
                                label,
                                "",
                            ),
                            "is_correct": False,
                        }
                    )

                questions.append(
                    {
                        "number": item["question_number"],
                        "text": item["text"],
                        "options": options,
                        "images": [],
                        "explanation": None,
                        "source_reference": (
                            self.pdf_path.name if self.pdf_path else None
                        ),
                        "source_page": None,
                    }
                )

            self.import_data = {
                "year": int(year),
                "subjects": [
                    {
                        "name": subject_name,
                        "questions": questions,
                    }
                ],
            }

            return self._success(
                {
                    "year": int(year),
                    "subject": subject_name,
                    "text": combined_text,
                    "questions": questions,
                    "count": len(questions),
                }
            )

        except Exception as exc:
            return self._error(exc)

    # =========================================================
    # CROP PREVIEW
    # =========================================================

    @Slot(
        int,
        int,
        int,
        int,
        result=str,
    )
    def crop_region(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
    ):

        if self.document is None:
            return self._error("No PDF document loaded.")

        if width <= 0 or height <= 0:
            return self._error("Invalid crop dimensions.")

        page = self.document.load_page(self.current_page)

        rect = pymupdf.Rect(
            x / self.zoom,
            y / self.zoom,
            (x + width) / self.zoom,
            (y + height) / self.zoom,
        )

        rect &= page.rect

        if rect.is_empty:
            return self._error("Selected region is outside the page.")

        pixmap = page.get_pixmap(
            clip=rect,
            matrix=pymupdf.Matrix(
                2,
                2,
            ),
            alpha=False,
        )

        encoded = base64.b64encode(pixmap.tobytes("png")).decode("ascii")

        return self._success(
            {
                "image": encoded,
                "page": self.current_page,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
            }
        )

    # =========================================================
    # SAVE DIAGRAM TO IMPORT STAGING
    # =========================================================

    @Slot(
        str,
        int,
        int,
        int,
        int,
        result=str,
    )
    def save_diagram(
        self,
        question_number: str,
        x: int,
        y: int,
        width: int,
        height: int,
    ):

        if self.document is None:
            return self._error("No PDF document loaded.")

        if self.import_dir is None:
            return self._error("No active question import.")

        try:
            question_number = int(question_number)

        except ValueError:
            return self._error("Question number must be a number.")

        if question_number <= 0:
            return self._error("Question number must be greater than zero.")

        page = self.document.load_page(self.current_page)

        rect = pymupdf.Rect(
            x / self.zoom,
            y / self.zoom,
            (x + width) / self.zoom,
            (y + height) / self.zoom,
        )

        rect &= page.rect

        if rect.is_empty:
            return self._error("Selected crop is outside the page.")

        pixmap = page.get_pixmap(
            clip=rect,
            matrix=pymupdf.Matrix(
                2,
                2,
            ),
            alpha=False,
        )

        image_dir = self.import_dir / "images"

        image_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        filename = (
            f"question_{question_number}_"
            f"page_{self.current_page + 1}_"
            f"{uuid.uuid4().hex[:8]}.png"
        )

        image_path = image_dir / filename

        pixmap.save(str(image_path))

        base_dir = Path(__file__).resolve().parents[2]

        relative_path = image_path.relative_to(base_dir).as_posix()

        if not self.import_data.get("subjects"):
            self.import_data = {
                "year": None,
                "subjects": [
                    {
                        "name": "Imported Questions",
                        "questions": [],
                    }
                ],
            }

        for subject in self.import_data["subjects"]:
            for item in subject.get("questions", []):
                if int(item.get("number", 0)) == question_number:
                    images = item.setdefault("images", [])
                    if not any(img.get("path") == relative_path for img in images):
                        images.append(
                            {
                                "path": relative_path,
                                "page": self.current_page + 1,
                            }
                        )
                    item["source_page"] = self.current_page + 1
                    break
            else:
                continue
            break
        else:
            first_subject = self.import_data["subjects"][0]
            first_subject.setdefault("questions", []).append(
                {
                    "number": question_number,
                    "text": "",
                    "options": [],
                    "images": [
                        {
                            "path": relative_path,
                            "page": self.current_page + 1,
                        }
                    ],
                    "explanation": None,
                    "source_reference": (self.pdf_path.name if self.pdf_path else None),
                    "source_page": self.current_page + 1,
                }
            )

        return self._success(
            {
                "path": relative_path,
                "question_number": question_number,
                "page": self.current_page + 1,
            }
        )

    # =========================================================
    # APPROVE / IMPORT REVIEW
    # =========================================================

    @Slot(str, result=str)
    def save_review(
        self,
        review_json: str,
    ):

        try:
            data = json.loads(review_json)

            if not isinstance(data, dict):
                raise ValueError("Invalid review data.")

            if "year" not in data:
                raise ValueError("Examination year is required.")

            if "subjects" not in data:
                raise ValueError("Subject data is required.")

            self.import_data = data

            with SessionLocal() as db:
                importer = QuestionImporter(db)
                result = importer.import_data(data)

            return self._success(
                {
                    "imported": result.get("imported", 0),
                    "skipped": result.get("skipped", 0),
                }
            )

        except Exception as exc:
            return self._error(exc)

    @Slot(result=str)
    def get_review(self):

        return self._success(
            {
                "review": self.import_data,
            }
        )

    @Slot(str, result=str)
    def approve_import(
        self,
        payload_json: str,
    ):

        try:
            payload = json.loads(payload_json)

            year = int(payload["year"])

            subjects = payload["subjects"]

            data = {
                "year": year,
                "subjects": subjects,
            }

            with SessionLocal() as db:
                importer = QuestionImporter(db)

                result = importer.import_data(data)

            return self._success(
                {
                    "result": result,
                }
            )

        except Exception as exc:
            return self._error(exc)

    # =========================================================
    # CLOSE / RESET
    # =========================================================

    @Slot(result=str)
    def reset_document(self):

        self.reset_state()

        return self._success(
            {
                "document": None,
            }
        )

    # =========================================================
    # INTERNAL RESET
    # =========================================================

    def reset_state(self):

        if self.document is not None:
            try:
                self.document.close()
            except Exception:
                pass

        self.document = None
        self.pdf_path = None
        self.current_page = 0
        self.zoom = 1.0
        self.import_id = None
        self.import_dir = None
        self.import_data = {
            "year": None,
            "subjects": [],
        }

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _success(
        data,
    ):

        return json.dumps(
            {
                "success": True,
                **data,
            }
        )

    @staticmethod
    def _error(
        message,
    ):

        return json.dumps(
            {
                "success": False,
                "error": str(message),
            }
        )

    @staticmethod
    def _get_page_text(
        page,
    ) -> str:

        try:
            return (
                page.get_text("text") or ""
            ).strip()
        except Exception:
            return ""
