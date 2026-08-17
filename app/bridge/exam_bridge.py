from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Slot, QTimer, QCoreApplication, QUrl
from PySide6.QtWidgets import QApplication, QMessageBox, QFileDialog
from sqlalchemy import distinct, select, func

from app.database.database import SessionLocal
from app.database.models import ExamSession, User, Subject, Question, Option
from app.services.exam_service import ExamService
from app.services.pdf_processor import PDFProcessor
from app.services.auth_service import AuthService


class ExamBridge(QObject):
    def __init__(self):
        super().__init__()
        self._web_view = None
        self._current_user = None

    def set_web_view(self, web_view):
        self._web_view = web_view

    # ========================================================
    # REPORTLAB SERVICE (lazy-loaded, defensive)
    # ========================================================

    @staticmethod
    def _get_reportlab_service():
        """Attempt to import and construct ReportlabReportService.

        Returns a tuple of (service, error_message). If the reportlab
        dependency is missing, ``service`` is None and the error
        message contains an actionable pip install instruction the
        JS bridge can surface to the user.
        """
        try:
            from app.services.reportlab_report_service import (
                ReportlabReportService,
            )
        except ModuleNotFoundError as exc:
            missing = getattr(exc, "name", "reportlab")
            if missing == "reportlab":
                msg = (
                    "ReportLab is not installed in this environment. "
                    "Please run:  python -m pip install reportlab"
                )
            else:
                msg = (
                    f"Missing module '{missing}' required for PDF export. "
                    f"Please install required dependencies."
                )
            return None, msg
        except Exception as exc:  # pragma: no cover - defensive
            return None, f"Unable to load PDF report service: {exc}"

        try:
            base_dir = Path(__file__).resolve().parents[2]
            logo_path = base_dir / "app" / "web" / "images" / "alayande.png"
            logo = logo_path if logo_path.exists() else None
            return ReportlabReportService(logo_path=logo), None
        except Exception as exc:
            return None, f"Failed to initialise PDF report service: {exc}"

    # ========================================================
    # YEARS
    # ========================================================

    @Slot(result=str)
    def get_years(self):

        try:
            with SessionLocal() as db:
                service = ExamService(db)

                years = service.get_available_years()

                return json.dumps(
                    {
                        "success": True,
                        "years": years,
                    }
                )

        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # SUBJECTS
    # ========================================================

    @Slot(int, result=str)
    def get_subjects_for_year(
        self,
        year: int,
    ):

        try:
            with SessionLocal() as db:
                service = ExamService(db)

                subjects = service.get_subjects_for_year(int(year))

                return json.dumps(
                    {
                        "success": True,
                        "subjects": subjects,
                    }
                )

        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # CREATE
    # ========================================================

    @Slot(int, "QVariant", int, str, result=str)
    def create_exam(
        self,
        year: int,
        subject_ids,
        duration_minutes: int,
        student_name: str = "",
    ):

        try:
            subject_ids = [int(value) for value in subject_ids]

            with SessionLocal() as db:
                service = ExamService(db)
                raw_name = student_name.strip() if student_name else ""

                # Look up user if matching username or full_name exists
                matched_user = None
                if raw_name:
                    matched_user = db.scalar(
                        select(User).where(
                            (User.username == raw_name)
                            | (func.lower(User.username) == raw_name.lower())
                            | (User.full_name == raw_name)
                            | (func.lower(User.full_name) == raw_name.lower())
                        )
                    )

                user_id = matched_user.id if matched_user else None
                full_student_name = (
                    matched_user.full_name
                    if (matched_user and matched_user.full_name)
                    else (raw_name if raw_name else None)
                )

                exam = service.create_exam(
                    year=int(year),
                    subject_ids=subject_ids,
                    duration_minutes=int(duration_minutes),
                    student_name=full_student_name,
                    user_id=user_id,
                )

                db.commit()

                return json.dumps(
                    {
                        "success": True,
                        "exam_id": exam.id,
                        "student_name": full_student_name,
                    }
                )

        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # START
    # ========================================================

    @Slot(int, result=str)
    def start_exam(
        self,
        exam_id: int,
    ):

        try:
            with SessionLocal() as db:
                service = ExamService(db)

                exam = service.start_exam(int(exam_id))

                remaining = service.get_remaining_seconds(exam.id)

                return json.dumps(
                    {
                        "success": True,
                        "exam_id": exam.id,
                        "remaining_seconds": (remaining),
                        "expires_at": (
                            exam.expires_at.isoformat() if exam.expires_at else None
                        ),
                    }
                )

        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # GET EXAM
    # ========================================================

    @Slot(int, result=str)
    def get_exam(
        self,
        exam_id: int,
    ):

        try:
            with SessionLocal() as db:
                service = ExamService(db)

                payload = service.get_exam_payload(int(exam_id))

                return json.dumps(
                    {
                        "success": True,
                        "exam": payload,
                    }
                )

        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # SAVE ANSWER
    # ========================================================

    @Slot(int, int, result=str)
    def save_answer(
        self,
        exam_question_id: int,
        option_id: int,
    ):

        try:
            with SessionLocal() as db:
                service = ExamService(db)

                answer = service.save_answer(
                    int(exam_question_id),
                    int(option_id),
                )

                return json.dumps(
                    {
                        "success": True,
                        "exam_question_id": (answer.exam_question_id),
                        "selected_option_id": (answer.selected_option_id),
                    }
                )

        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # SAVE POSITION
    # ========================================================

    @Slot(int, int, result=str)
    def save_question_position(
        self,
        exam_subject_id: int,
        position: int,
    ):

        try:
            with SessionLocal() as db:
                service = ExamService(db)

                subject = service.save_question_position(
                    int(exam_subject_id),
                    int(position),
                )

                return json.dumps(
                    {
                        "success": True,
                        "exam_subject_id": (subject.id),
                        "position": (subject.current_question_position),
                    }
                )

        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # REMAINING TIME
    # ========================================================

    @Slot(int, result=str)
    def get_remaining_time(
        self,
        exam_id: int,
    ):

        try:
            with SessionLocal() as db:
                service = ExamService(db)

                expired = service.check_exam_expired(int(exam_id))

                remaining = service.get_remaining_seconds(int(exam_id))

                return json.dumps(
                    {
                        "success": True,
                        "expired": expired,
                        "remaining_seconds": (remaining),
                    }
                )

        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # COMPLETE
    # ========================================================

    @Slot(int, result=str)
    def complete_exam(
        self,
        exam_id: int,
    ):

        try:
            with SessionLocal() as db:
                service = ExamService(db)

                service.complete_exam(int(exam_id))

                result = service.get_result(int(exam_id))

                return json.dumps(
                    {
                        "success": True,
                        "result": result,
                    }
                )

        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # RESULT
    # ========================================================

    @Slot(int, result=str)
    def get_result(
        self,
        exam_id: int,
    ):

        try:
            with SessionLocal() as db:
                service = ExamService(db)

                result = service.get_result(int(exam_id))

                return json.dumps(
                    {
                        "success": True,
                        "result": result,
                    }
                )

        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # RESTART APPLICATION
    # ========================================================

    @Slot(result=str)
    def restart_application(self):

        try:
            subprocess.Popen(
                [
                    sys.executable,
                    *sys.argv,
                ],
                cwd=None,
            )

            # Give the new process a moment to start,
            # then close the current Qt application.

            QTimer.singleShot(
                300,
                self._quit_current_application,
            )

            return json.dumps(
                {
                    "success": True,
                }
            )

        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # QUIT CURRENT APPLICATION
    # ========================================================

    @staticmethod
    def _quit_current_application():

        app = QCoreApplication.instance()

        if app is not None:
            app.quit()

    # ========================================================
    # DOWNLOAD RESULT PDF
    # ========================================================

    @Slot(str, result=str)
    def download_result_pdf(self, default_name: str = "exam_result.pdf"):
        try:
            if self._web_view is None:
                return self._error("Web view is not available for PDF export.")

            default_name = str(default_name or "exam_result.pdf")
            if not default_name.lower().endswith(".pdf"):
                default_name += ".pdf"

            file_path, _ = QFileDialog.getSaveFileName(
                None,
                "Save Result as PDF",
                default_name,
                "PDF Files (*.pdf)",
            )

            if not file_path:
                return json.dumps({"success": False, "cancelled": True})

            path = Path(file_path)
            path_str = str(path.resolve())

            def on_pdf_ready(data):
                try:
                    path.write_bytes(bytes(data))
                except Exception:
                    pass

            self._web_view.page().printToPdf(on_pdf_ready)

            return json.dumps(
                {
                    "success": True,
                    "path": path_str,
                    "name": path.name,
                }
            )

        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # PRINT HTML CONTENT VIA NATIVE PRINT DIALOG
    # ========================================================

    @Slot(str, str, result=str)
    def print_html(self, html_content: str, title: str = "Mock CBT"):
        try:
            from PySide6.QtGui import QTextDocument
            from PySide6.QtPrintSupport import QPrinter, QPrintDialog

            doc = QTextDocument()
            doc.setHtml(html_content or "")

            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            doc_title = str(title or "Mock CBT Examination")
            printer.setDocName(doc_title)

            dialog = QPrintDialog(printer, self._web_view if hasattr(self, '_web_view') else None)
            dialog.setWindowTitle(f"Print - {doc_title}")

            if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                doc.print_(printer)
                return json.dumps({"success": True, "printed": True})
            else:
                return json.dumps({"success": False, "cancelled": True})
        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # GENERATE RESULT PDF (REPORTLAB)
    # ========================================================

    @Slot(str, str, result=str)
    def generate_result_pdf_reportlab(
        self,
        result_json: str,
        default_name: str = "exam_result.pdf",
    ):
        try:
            service, service_err = self._get_reportlab_service()
            if service is None:
                return self._error(service_err or "PDF service unavailable.")

            result = json.loads(result_json or "{}")
            if not result:
                return self._error("No result data provided for PDF generation.")

            full_name = str(
                result.get("student_full_name")
                or result.get("student_name")
                or "Student"
            ).strip()
            result["student_name"] = full_name

            safe_name = "".join(
                c for c in full_name if c.isalnum() or c in (" ", "_", "-")
            ).strip().replace(" ", "_") or "student"
            year = result.get("year", "")
            suggested_name = f"exam_result_{safe_name}_{year}.pdf" if year else f"exam_result_{safe_name}.pdf"

            file_path, _ = QFileDialog.getSaveFileName(
                None,
                "Save Result as PDF",
                suggested_name,
                "PDF Files (*.pdf)",
            )

            if not file_path:
                return json.dumps({"success": False, "cancelled": True})

            output = Path(file_path)
            service.generate_exam_result_pdf(str(output), result)

            return json.dumps(
                {
                    "success": True,
                    "path": str(output.resolve()),
                    "name": output.name,
                }
            )

        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # GENERATE STUDENT HISTORY PDF (REPORTLAB)
    # ========================================================

    @Slot(str, str, str, result=str)
    def generate_student_history_pdf_reportlab(
        self,
        student_name: str,
        history_json: str,
        default_name: str = "student_history.pdf",
    ):
        try:
            service, service_err = self._get_reportlab_service()
            if service is None:
                return self._error(service_err or "PDF service unavailable.")

            history = json.loads(history_json or "[]")
            if not history:
                return self._error("No history data provided for PDF generation.")

            sname = str(student_name or "Student").strip() or "Student"

            safe_name = "".join(c for c in sname if c.isalnum() or c in (" ", "_", "-")).strip() or "student"
            default_name = str(default_name or f"{safe_name}_history.pdf")
            if not default_name.lower().endswith(".pdf"):
                default_name += ".pdf"

            file_path, _ = QFileDialog.getSaveFileName(
                None,
                "Save Student History as PDF",
                default_name,
                "PDF Files (*.pdf)",
            )

            if not file_path:
                return json.dumps({"success": False, "cancelled": True})

            output = Path(file_path)
            service.generate_student_history_pdf(str(output), sname, history)

            return json.dumps(
                {
                    "success": True,
                    "path": str(output.resolve()),
                    "name": output.name,
                }
            )

        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # CHECK STUDENT REGISTERED (WELCOME BACK)
    # ========================================================

    @Slot(str, result=str)
    def check_student_registered(self, student_name: str):
        try:
            name = str(student_name or "").strip()
            if not name:
                return json.dumps(
                    {
                        "success": True,
                        "registered": False,
                        "sessions": 0,
                        "last_exam": None,
                    }
                )

            with SessionLocal() as db:
                statement = (
                    select(ExamSession)
                    .where(ExamSession.student_name == name)
                    .order_by(ExamSession.started_at.desc())
                )
                rows = list(db.scalars(statement).all())

                if not rows:
                    return json.dumps(
                        {
                            "success": True,
                            "registered": False,
                            "sessions": 0,
                            "last_exam": None,
                        }
                    )

                last = rows[0]
                last_exam = None
                if last.started_at:
                    last_exam = {
                        "year": int(last.year),
                        "started_at": last.started_at.isoformat() if last.started_at else None,
                        "completed_at": (
                            last.completed_at.isoformat()
                            if last.completed_at
                            else None
                        ),
                        "is_completed": bool(last.is_completed),
                    }

                return json.dumps(
                    {
                        "success": True,
                        "registered": True,
                        "sessions": len(rows),
                        "last_exam": last_exam,
                        "student_name": name,
                    }
                )

        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # CHECK ADMIN IDENTITY
    # ========================================================

    @Slot(str, result=str)
    def check_admin_identity(self, name: str):
        """Check if the provided name matches any admin username or full_name.

        Returns is_admin=True if the input matches (case-insensitive)
        any admin user's username or full_name.
        """
        try:
            name_normalized = str(name or "").strip().lower()
            if not name_normalized:
                return json.dumps(
                    {
                        "success": True,
                        "is_admin": False,
                    }
                )

            with SessionLocal() as db:
                # Query all admin users
                statement = select(User).where(User.role == "admin")
                admins = list(db.scalars(statement).all())

                matched_admin = None
                for admin in admins:
                    if (
                        (admin.username and admin.username.lower() == name_normalized)
                        or (admin.full_name and admin.full_name.lower() == name_normalized)
                    ):
                        matched_admin = admin
                        break

                return json.dumps(
                    {
                        "success": True,
                        "is_admin": matched_admin is not None,
                        "matched_user": (
                            {
                                "username": matched_admin.username,
                                "full_name": matched_admin.full_name,
                            }
                            if matched_admin is not None
                            else None
                        ),
                    }
                )

        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # CHECK USERNAME & STUDENT REGISTRATION
    # ========================================================

    @Slot(str, result=str)
    def check_username(self, username: str):
        """Check if a username exists in the database.
        Returns details if exists, indicates if admin or student.
        """
        try:
            raw_username = str(username or "").strip()
            if not raw_username:
                return json.dumps({
                    "success": True,
                    "exists": False,
                })

            with SessionLocal() as db:
                user = db.scalar(
                    select(User).where(User.username == raw_username)
                )

                if not user:
                    # Also try case-insensitive
                    user = db.scalar(
                        select(User).where(func.lower(User.username) == raw_username.lower())
                    )

                if user:
                    if not user.is_active:
                        return json.dumps({
                            "success": False,
                            "error": "This account is inactive. Please contact an administrator.",
                        })

                    return json.dumps({
                        "success": True,
                        "exists": True,
                        "is_admin": user.role == "admin",
                        "user": {
                            "id": user.id,
                            "username": user.username,
                            "full_name": user.full_name,
                            "role": user.role,
                            "student_class": user.student_class,
                            "admission_year": user.admission_year,
                        }
                    })
                else:
                    return json.dumps({
                        "success": True,
                        "exists": False,
                    })
        except Exception as exc:
            return self._error(exc)

    @Slot(str, str, str, str, str, result=str)
    def register_student(
        self,
        username: str,
        password: str,
        full_name: str,
        student_class: str = "",
        admission_year: str = "",
    ):
        """Register a new student."""
        try:
            u_name = str(username or "").strip()
            f_name = str(full_name or "").strip()
            pwd = str(password or "").strip() or "password123"

            if not u_name:
                return json.dumps({"success": False, "error": "Username is required."})
            if not f_name:
                return json.dumps({"success": False, "error": "Full name is required."})

            with SessionLocal() as db:
                auth_service = AuthService(db)

                # Check if username exists
                existing = db.scalar(
                    select(User).where(
                        (func.lower(User.username) == u_name.lower())
                    )
                )
                if existing:
                    return json.dumps({
                        "success": False,
                        "error": "Username already exists. Please choose another username or log in."
                    })

                s_class = student_class.strip() if student_class and student_class.strip() else None
                adm_year = int(admission_year) if admission_year and str(admission_year).strip().isdigit() else None

                user = auth_service.create_user(
                    username=u_name,
                    password=pwd,
                    full_name=f_name,
                    role="student",
                    student_class=s_class,
                    admission_year=adm_year,
                )

                return json.dumps({
                    "success": True,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "full_name": user.full_name,
                        "role": user.role,
                        "student_class": user.student_class,
                        "admission_year": user.admission_year,
                    }
                })
        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # ERROR
    # ========================================================

    @staticmethod
    def _error(
        exc: Exception,
    ):

        return json.dumps(
            {
                "success": False,
                "error": str(exc),
            }
        )

    # ========================================================
    # OPEN QUESTION PAPER
    # ========================================================

    @Slot(result=str)
    def open_question_paper(self):

        try:
            file_path, _ = QFileDialog.getOpenFileName(
                None,
                "Open Question Paper",
                "",
                "PDF Files (*.pdf)",
            )

            if not file_path:
                return json.dumps(
                    {
                        "success": False,
                        "cancelled": True,
                    }
                )

            processor = PDFProcessor()

            result = processor.prepare_document(file_path)

            # Convert filesystem paths to local file URLs
            # so Qt WebEngine can display them.

            for page in result["pages"]:
                page["image_url"] = QUrl.fromLocalFile(page["image_path"]).toString()

                page["thumbnail_url"] = QUrl.fromLocalFile(
                    page["thumbnail_path"]
                ).toString()

            return json.dumps(
                {
                    "success": True,
                    "document": result,
                }
            )

        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # RENDER SINGLE PAGE
    # ========================================================

    @Slot(str, int, result=str)
    def render_question_page(
        self,
        pdf_path: str,
        page_number: int,
    ):

        try:
            processor = PDFProcessor()

            pdf = Path(pdf_path)

            output_dir = pdf.parent / "imports" / pdf.stem / "pages"

            output_path = output_dir / f"page_{page_number + 1:03d}.png"

            result = processor.render_page(
                pdf_path=pdf_path,
                page_number=page_number,
                output_path=output_path,
            )

            return json.dumps(
                {
                    "success": True,
                    "image_url": QUrl.fromLocalFile(result["path"]).toString(),
                    "width": result["width"],
                    "height": result["height"],
                }
            )

        except Exception as exc:
            return self._error(exc)

    # ============================================================

    # CROP DIAGRAM
    # ============================================================

    @Slot(str, int, float, float, float, float, int, str, result=str)
    def crop_diagram(
        self,
        pdf_path: str,
        page_number: int,
        x: float,
        y: float,
        width: float,
        height: float,
        question_id: int,
        image_type: str = "diagram",
    ):

        try:
            base_dir = Path(__file__).resolve().parents[2]

            pdf_path = Path(pdf_path)

            if not pdf_path.is_absolute():
                pdf_path = base_dir / pdf_path

            # ----------------------------------------------------
            # Find question
            # ----------------------------------------------------

            with SessionLocal() as db:
                from app.database.models import (
                    Question,
                    QuestionImage,
                )

                question = db.get(
                    Question,
                    int(question_id),
                )

                if question is None:
                    raise ValueError(f"Question {question_id} does not exist.")

                # ------------------------------------------------
                # Determine next image position
                # ------------------------------------------------

                next_position = len(question.images) + 1

                # ------------------------------------------------
                # Output directory
                # ------------------------------------------------

                document_name = pdf_path.stem

                images_dir = base_dir / "imports" / document_name / "images"

                images_dir.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                image_filename = (
                    f"question_{question.question_number}_image_{next_position}.png"
                )

                image_path = images_dir / image_filename

                # ------------------------------------------------
                # Crop
                # ------------------------------------------------

                processor = PDFProcessor(base_dir)

                processor.crop_page(
                    pdf_path=pdf_path,
                    page_number=int(page_number),
                    x=float(x),
                    y=float(y),
                    width=float(width),
                    height=float(height),
                    output_path=image_path,
                )

                # ------------------------------------------------
                # Save DB record
                # ------------------------------------------------

                relative_path = image_path.relative_to(base_dir).as_posix()

                image = QuestionImage(
                    question_id=question.id,
                    image_path=relative_path,
                    position=next_position,
                    image_type=image_type,
                    source_page=int(page_number),
                )

                db.add(image)

                db.commit()

                db.refresh(image)

                return json.dumps(
                    {
                        "success": True,
                        "image": {
                            "id": image.id,
                            "question_id": image.question_id,
                            "path": image.image_path,
                            "position": image.position,
                            "type": image.image_type,
                            "source_page": image.source_page,
                        },
                    }
                )

        except Exception as exc:
            return self._error(exc)


    #=======================================
    # ADMIN DASHBOARD AND FEATURES
    #=======================================

    @Slot(str, result=str)
    def search_students(self, search_name: str = ""):
        try:
            with SessionLocal() as db:
                from sqlalchemy import or_
                
                query = select(ExamSession)
                if search_name and search_name.strip():
                    search_pattern = f"%{search_name.strip()}%"
                    query = query.where(ExamSession.student_name.like(search_pattern))
                
                query = query.order_by(ExamSession.started_at.desc())
                sessions = list(db.scalars(query).all())
                
                # Group by student name
                students_dict = {}
                for session in sessions:
                    name = session.student_name or "Unknown"
                    if name not in students_dict:
                        students_dict[name] = {
                            "name": name,
                            "session_count": 0,
                            "last_exam": None,
                            "last_exam_datetime": None,
                        }
                    students_dict[name]["session_count"] += 1
                    if students_dict[name]["last_exam_datetime"] is None or (session.started_at and session.started_at > students_dict[name]["last_exam_datetime"]):
                        students_dict[name]["last_exam"] = session.started_at.strftime("%d-%m-%Y %H:%M:%S") if session.started_at else None
                        students_dict[name]["last_exam_datetime"] = session.started_at
                
                # Remove datetime field before JSON serialization
                for student_data in students_dict.values():
                    if "last_exam_datetime" in student_data:
                        del student_data["last_exam_datetime"]
                
                students = list(students_dict.values())
                
                return json.dumps({
                    "success": True,
                    "students": students,
                })
        except Exception as exc:
            return self._error(exc)

    @Slot(str, result=str)
    def get_student_history(self, student_name: str):
        try:
            with SessionLocal() as db:
                from app.services.exam_service import ExamService
                
                service = ExamService(db)
                
                sessions = list(db.scalars(
                    select(ExamSession)
                    .where(ExamSession.student_name == student_name)
                    .where(ExamSession.is_completed == True)
                    .order_by(ExamSession.completed_at.desc())
                ).all())
                
                history = []
                for session in sessions:
                    result = service.get_result(session.id)
                    
                    # Extract per-subject breakdown from existing result
                    subjects_data = []
                    for subject_result in result.get("subjects", []):
                        subjects_data.append({
                            "name": subject_result.get("subject_name", ""),
                            "total": subject_result.get("total", 0),
                            "correct": subject_result.get("correct", 0),
                            "percentage": subject_result.get("percentage", 0),
                        })
                    
                    history.append({
                        "id": session.id,
                        "year": session.year,
                        "completed_at": session.completed_at.strftime("%d-%m-%Y %H:%M:%S") if session.completed_at else None,
                        "subject_count": len(session.subjects),
                        "total": result.get("total", 0),
                        "correct": result.get("correct", 0),
                        "percentage": result.get("percentage", 0),
                        "subjects": subjects_data,
                    })
                
                return json.dumps({
                    "success": True,
                    "history": history,
                })
        except Exception as exc:
            return self._error(exc)

    @Slot(str, result=str)
    def delete_student(self, student_name: str):
        try:
            with SessionLocal() as db:
                sessions = list(db.scalars(
                    select(ExamSession)
                    .where(ExamSession.student_name == student_name)
                ).all())
                
                for session in sessions:
                    db.delete(session)
                
                db.commit()
                
                return json.dumps({
                    "success": True,
                    "deleted": len(sessions),
                })
        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # AUTHENTICATION
    # ========================================================

    @Slot(str, str, result=str)
    def login(self, username: str, password: str):
        try:
            with SessionLocal() as db:
                auth_service = AuthService(db)
                user = auth_service.authenticate(username, password)
                
                if user:
                    self._current_user = user
                    return json.dumps({
                        "success": True,
                        "user": {
                            "id": user.id,
                            "username": user.username,
                            "full_name": user.full_name,
                            "role": user.role,
                            "student_class": user.student_class,
                            "admission_year": user.admission_year,
                        }
                    })
                else:
                    return json.dumps({
                        "success": False,
                        "error": "Invalid username or password"
                    })
        except Exception as exc:
            return self._error(exc)

    @Slot(result=str)
    def logout(self):
        try:
            self._current_user = None
            return json.dumps({
                "success": True,
                "message": "Logged out successfully"
            })
        except Exception as exc:
            return self._error(exc)

    @Slot(result=str)
    def get_current_user(self):
        try:
            if self._current_user:
                return json.dumps({
                    "success": True,
                    "user": {
                        "id": self._current_user.id,
                        "username": self._current_user.username,
                        "full_name": self._current_user.full_name,
                        "role": self._current_user.role,
                        "student_class": self._current_user.student_class,
                        "admission_year": self._current_user.admission_year,
                    }
                })
            else:
                return json.dumps({
                    "success": False,
                    "error": "No user logged in"
                })
        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # USER MANAGEMENT (ADMIN ONLY)
    # ========================================================

    @Slot(str, str, str, str, str, str, result=str)
    def create_user(self, username: str, password: str, full_name: str, role: str, student_class: str, admission_year: str):
        """Create a new user (admin only)."""
        try:
            if not self._current_user or self._current_user.role != "admin":
                return json.dumps({
                    "success": False,
                    "error": "Access denied. Admin only."
                })
            
            with SessionLocal() as db:
                auth_service = AuthService(db)
                
                # Parse optional fields
                student_class_parsed = student_class if student_class else None
                admission_year_parsed = int(admission_year) if admission_year else None
                
                user = auth_service.create_user(
                    username=username,
                    password=password,
                    full_name=full_name,
                    role=role,
                    student_class=student_class_parsed,
                    admission_year=admission_year_parsed,
                )
                
                return json.dumps({
                    "success": True,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "full_name": user.full_name,
                        "role": user.role,
                        "student_class": user.student_class,
                        "admission_year": user.admission_year,
                    }
                })
        except Exception as exc:
            return self._error(exc)

    @Slot(str, str, str, str, str, str, str, result=str)
    def update_user(self, user_id: str, full_name: str, role: str, student_class: str, admission_year: str, is_active: str, password: str):
        try:
            if not self._current_user or self._current_user.role != "admin":
                return json.dumps({
                    "success": False,
                    "error": "Access denied. Admin only."
                })
            
            with SessionLocal() as db:
                auth_service = AuthService(db)
                
                # Parse optional fields
                full_name_parsed = full_name if full_name else None
                role_parsed = role if role else None
                student_class_parsed = student_class if student_class else None
                admission_year_parsed = int(admission_year) if admission_year else None
                is_active_parsed = is_active.lower() == "true" if is_active else None
                password_parsed = password if password else None
                
                user = auth_service.update_user(
                    user_id=int(user_id),
                    full_name=full_name_parsed,
                    role=role_parsed,
                    student_class=student_class_parsed,
                    admission_year=admission_year_parsed,
                    is_active=is_active_parsed,
                    password=password_parsed,
                )
                
                return json.dumps({
                    "success": True,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "full_name": user.full_name,
                        "role": user.role,
                        "student_class": user.student_class,
                        "admission_year": user.admission_year,
                        "is_active": user.is_active,
                    }
                })
        except Exception as exc:
            return self._error(exc)

    @Slot(str, result=str)
    def delete_user(self, user_id: str):
        try:
            if not self._current_user or self._current_user.role != "admin":
                return json.dumps({
                    "success": False,
                    "error": "Access denied. Admin only."
                })
            
            with SessionLocal() as db:
                auth_service = AuthService(db)
                success = auth_service.delete_user(int(user_id))
                
                return json.dumps({
                    "success": success,
                    "message": "User deleted successfully" if success else "User not found"
                })
        except Exception as exc:
            return self._error(exc)

    @Slot(result=str)
    def get_all_users(self):
        if not self._current_user or self._current_user.role != "admin":
            return self._error("Only admins can view users.")

        try:
            with SessionLocal() as db:
                auth_service = AuthService(db)
                users = auth_service.get_all_users()
                users_data = []
                for user in users:
                    users_data.append({
                        "id": user.id,
                        "username": user.username,
                        "full_name": user.full_name,
                        "role": user.role,
                        "student_class": user.student_class,
                        "admission_year": user.admission_year,
                        "is_active": user.is_active,
                        "created_at": user.created_at.isoformat() if user.created_at else None,
                    })
                
                return json.dumps({
                    "success": True,
                    "users": users_data
                })
        except Exception as exc:
            return self._error(exc)

    @Slot(result=str)
    def launch_question_import(self):
        """Launch the question import interface as a separate window."""
        try:
            base_dir = Path(__file__).resolve().parents[2]
            launcher_script = base_dir / "question_import_launcher.py"

            if not launcher_script.exists():
                return self._error("Question import launcher not found.")

            # Launch the question import as a separate process
            subprocess.Popen(
                [sys.executable, str(launcher_script)],
                cwd=str(base_dir),
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            )

            return json.dumps({
                "success": True,
                "message": "Question import window launched.",
            })
        except Exception as exc:
            return self._error(f"Failed to launch question import: {exc}")

    # ========================================================
    # SUBJECT MANAGEMENT
    # ========================================================

    @Slot(result=str)
    def get_all_subjects(self):
        """Get all subjects with their question count."""
        try:
            with SessionLocal() as db:
                subjects = list(db.scalars(
                    select(Subject).order_by(Subject.name.asc())
                ).all())

                subjects_data = []
                for s in subjects:
                    q_count = db.scalar(
                        select(func.count(Question.id)).where(Question.subject_id == s.id)
                    ) or 0

                    subjects_data.append({
                        "id": s.id,
                        "name": s.name,
                        "code": s.code,
                        "is_active": s.is_active,
                        "question_count": q_count,
                    })

                return json.dumps({
                    "success": True,
                    "subjects": subjects_data,
                })
        except Exception as exc:
            return self._error(exc)

    @Slot(str, str, result=str)
    def create_subject(self, name: str, code: str = ""):
        """Create a new subject."""
        try:
            s_name = str(name or "").strip()
            s_code = str(code or "").strip().upper() if code and code.strip() else None

            if not s_name:
                return json.dumps({"success": False, "error": "Subject name is required."})

            with SessionLocal() as db:
                existing = db.scalar(select(Subject).where(func.lower(Subject.name) == s_name.lower()))
                if existing:
                    return json.dumps({"success": False, "error": f"Subject '{s_name}' already exists."})

                if s_code:
                    existing_code = db.scalar(select(Subject).where(func.upper(Subject.code) == s_code))
                    if existing_code:
                        return json.dumps({"success": False, "error": f"Subject code '{s_code}' is already used by '{existing_code.name}'."})

                subject = Subject(name=s_name, code=s_code, is_active=True)
                db.add(subject)
                db.commit()
                db.refresh(subject)

                return json.dumps({
                    "success": True,
                    "subject": {
                        "id": subject.id,
                        "name": subject.name,
                        "code": subject.code,
                        "is_active": subject.is_active,
                        "question_count": 0,
                    }
                })
        except Exception as exc:
            return self._error(exc)

    @Slot(int, str, str, str, result=str)
    def update_subject(self, subject_id: int, name: str, code: str = "", is_active: str = "true"):
        """Update an existing subject."""
        try:
            s_name = str(name or "").strip()
            s_code = str(code or "").strip().upper() if code and code.strip() else None
            active_bool = is_active.lower() == "true" if is_active else True

            if not s_name:
                return json.dumps({"success": False, "error": "Subject name is required."})

            with SessionLocal() as db:
                subject = db.get(Subject, int(subject_id))
                if not subject:
                    return json.dumps({"success": False, "error": "Subject not found."})

                dup = db.scalar(
                    select(Subject).where(
                        func.lower(Subject.name) == s_name.lower(),
                        Subject.id != subject.id
                    )
                )
                if dup:
                    return json.dumps({"success": False, "error": f"Another subject with name '{s_name}' already exists."})

                if s_code:
                    dup_code = db.scalar(
                        select(Subject).where(
                            func.upper(Subject.code) == s_code,
                            Subject.id != subject.id
                        )
                    )
                    if dup_code:
                        return json.dumps({"success": False, "error": f"Subject code '{s_code}' is already used by '{dup_code.name}'."})

                subject.name = s_name
                subject.code = s_code
                subject.is_active = active_bool
                db.commit()
                db.refresh(subject)

                return json.dumps({
                    "success": True,
                    "subject": {
                        "id": subject.id,
                        "name": subject.name,
                        "code": subject.code,
                        "is_active": subject.is_active,
                    }
                })
        except Exception as exc:
            return self._error(exc)

    @Slot(int, result=str)
    def delete_subject(self, subject_id: int):
        """Delete a subject if it has no questions."""
        try:
            with SessionLocal() as db:
                subject = db.get(Subject, int(subject_id))
                if not subject:
                    return json.dumps({"success": False, "error": "Subject not found."})

                q_count = db.scalar(select(func.count(Question.id)).where(Question.subject_id == subject.id)) or 0
                if q_count > 0:
                    return json.dumps({
                        "success": False,
                        "error": f"Cannot delete '{subject.name}' because it contains {q_count} question(s). Please delete its questions first."
                    })

                db.delete(subject)
                db.commit()

                return json.dumps({"success": True, "message": "Subject deleted successfully."})
        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # MANUAL QUESTION MANAGEMENT
    # ========================================================

    @Slot(int, int, result=str)
    def get_next_question_number(self, year: int, subject_id: int):
        """Get the next suggested question number for a subject and year."""
        try:
            with SessionLocal() as db:
                max_num = db.scalar(
                    select(func.max(Question.question_number)).where(
                        Question.year == int(year),
                        Question.subject_id == int(subject_id),
                    )
                )
                next_num = (max_num or 0) + 1
                return json.dumps({"success": True, "next_number": next_num})
        except Exception as exc:
            return self._error(exc)

    @Slot(str, str, str, int, int, result=str)
    def get_questions_by_filter(
        self,
        year_str: str = "",
        subject_id_str: str = "",
        search_query: str = "",
        page: int = 1,
        page_size: int = 10,
    ):
        """Get questions filtered by year, subject, and search query with pagination."""
        try:
            with SessionLocal() as db:
                from sqlalchemy.orm import joinedload

                query = select(Question).options(
                    joinedload(Question.subject),
                    joinedload(Question.options)
                )

                if year_str and str(year_str).strip() and str(year_str).strip() != "all":
                    query = query.where(Question.year == int(year_str))

                if subject_id_str and str(subject_id_str).strip() and str(subject_id_str).strip() != "all":
                    query = query.where(Question.subject_id == int(subject_id_str))

                if search_query and str(search_query).strip():
                    pattern = f"%{str(search_query).strip()}%"
                    query = query.where(
                        (Question.text.like(pattern)) | (Question.explanation.like(pattern))
                    )

                count_query = select(func.count(Question.id))
                if year_str and str(year_str).strip() and str(year_str).strip() != "all":
                    count_query = count_query.where(Question.year == int(year_str))
                if subject_id_str and str(subject_id_str).strip() and str(subject_id_str).strip() != "all":
                    count_query = count_query.where(Question.subject_id == int(subject_id_str))
                if search_query and str(search_query).strip():
                    pattern = f"%{str(search_query).strip()}%"
                    count_query = count_query.where(
                        (Question.text.like(pattern)) | (Question.explanation.like(pattern))
                    )

                total_count = db.scalar(count_query) or 0

                page = max(1, int(page))
                page_size = max(1, min(100, int(page_size)))
                offset = (page - 1) * page_size

                query = query.order_by(
                    Question.year.desc(),
                    Question.subject_id.asc(),
                    Question.question_number.asc()
                ).offset(offset).limit(page_size)

                questions = list(db.scalars(query).unique().all())

                items = []
                for q in questions:
                    sorted_options = sorted(q.options, key=lambda o: o.position)
                    correct_opt = next((o for o in sorted_options if o.is_correct), None)
                    items.append({
                        "id": q.id,
                        "year": q.year,
                        "subject_id": q.subject_id,
                        "subject_name": q.subject.name if q.subject else "Unknown",
                        "question_number": q.question_number,
                        "text": q.text,
                        "explanation": q.explanation,
                        "options": [
                            {
                                "id": opt.id,
                                "label": opt.label,
                                "position": opt.position,
                                "text": opt.text,
                                "is_correct": opt.is_correct,
                            }
                            for opt in sorted_options
                        ],
                        "correct_label": correct_opt.label if correct_opt else "",
                    })

                total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1

                return json.dumps({
                    "success": True,
                    "questions": items,
                    "total": total_count,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                })
        except Exception as exc:
            return self._error(exc)

    @Slot(int, int, int, str, str, str, str, result=str)
    def create_question_manual(
        self,
        year: int,
        subject_id: int,
        question_number: int,
        text: str,
        options_json: str,
        correct_label: str,
        explanation: str = "",
    ):
        """Create a new question manually with flexible options (A, B, C, D, E, etc.)."""
        try:
            y = int(year)
            s_id = int(subject_id)
            q_num = int(question_number)
            q_text = str(text or "").strip()
            c_label = str(correct_label or "").strip().upper()
            expl = str(explanation or "").strip() if explanation else None

            if not q_text:
                return json.dumps({"success": False, "error": "Question text is required."})
            if not c_label:
                return json.dumps({"success": False, "error": "Please select the correct option."})

            try:
                options_list = json.loads(options_json or "[]")
            except Exception:
                return json.dumps({"success": False, "error": "Invalid options data."})

            if not options_list or len(options_list) < 2:
                return json.dumps({"success": False, "error": "At least 2 options are required."})

            with SessionLocal() as db:
                subject = db.get(Subject, s_id)
                if not subject:
                    return json.dumps({"success": False, "error": "Subject does not exist."})

                existing = db.scalar(
                    select(Question).where(
                        Question.subject_id == s_id,
                        Question.year == y,
                        Question.question_number == q_num,
                    )
                )
                if existing:
                    return json.dumps({
                        "success": False,
                        "error": f"Question {q_num} already exists for {subject.name} ({y}). Please choose another question number."
                    })

                question = Question(
                    subject_id=s_id,
                    year=y,
                    question_number=q_num,
                    text=q_text,
                    explanation=expl,
                    is_active=True,
                )
                db.add(question)
                db.flush()

                for idx, opt_item in enumerate(options_list, start=1):
                    label = str(opt_item.get("label", "")).strip().upper() or chr(64 + idx)
                    opt_text = str(opt_item.get("text", "")).strip()
                    is_corr = (label == c_label)

                    option = Option(
                        question_id=question.id,
                        label=label,
                        position=idx,
                        text=opt_text,
                        is_correct=is_corr,
                    )
                    db.add(option)

                db.commit()
                db.refresh(question)

                return json.dumps({
                    "success": True,
                    "question_id": question.id,
                    "message": f"Question {q_num} created successfully.",
                })
        except Exception as exc:
            return self._error(exc)

    @Slot(int, int, int, int, str, str, str, str, result=str)
    def update_question_manual(
        self,
        question_id: int,
        year: int,
        subject_id: int,
        question_number: int,
        text: str,
        options_json: str,
        correct_label: str,
        explanation: str = "",
    ):
        """Update an existing question and its options."""
        try:
            q_id = int(question_id)
            y = int(year)
            s_id = int(subject_id)
            q_num = int(question_number)
            q_text = str(text or "").strip()
            c_label = str(correct_label or "").strip().upper()
            expl = str(explanation or "").strip() if explanation else None

            if not q_text:
                return json.dumps({"success": False, "error": "Question text is required."})
            if not c_label:
                return json.dumps({"success": False, "error": "Please select the correct option."})

            try:
                options_list = json.loads(options_json or "[]")
            except Exception:
                return json.dumps({"success": False, "error": "Invalid options data."})

            if not options_list or len(options_list) < 2:
                return json.dumps({"success": False, "error": "At least 2 options are required."})

            with SessionLocal() as db:
                question = db.get(Question, q_id)
                if not question:
                    return json.dumps({"success": False, "error": "Question not found."})

                dup = db.scalar(
                    select(Question).where(
                        Question.subject_id == s_id,
                        Question.year == y,
                        Question.question_number == q_num,
                        Question.id != q_id,
                    )
                )
                if dup:
                    return json.dumps({
                        "success": False,
                        "error": f"Question {q_num} already exists for this subject and year."
                    })

                question.year = y
                question.subject_id = s_id
                question.question_number = q_num
                question.text = q_text
                question.explanation = expl

                for old_opt in list(question.options):
                    db.delete(old_opt)
                db.flush()

                for idx, opt_item in enumerate(options_list, start=1):
                    label = str(opt_item.get("label", "")).strip().upper() or chr(64 + idx)
                    opt_text = str(opt_item.get("text", "")).strip()
                    is_corr = (label == c_label)

                    option = Option(
                        question_id=question.id,
                        label=label,
                        position=idx,
                        text=opt_text,
                        is_correct=is_corr,
                    )
                    db.add(option)

                db.commit()

                return json.dumps({
                    "success": True,
                    "question_id": question.id,
                    "message": f"Question {q_num} updated successfully.",
                })
        except Exception as exc:
            return self._error(exc)

    @Slot(int, result=str)
    def delete_question_manual(self, question_id: int):
        """Delete a question and its options."""
        try:
            with SessionLocal() as db:
                question = db.get(Question, int(question_id))
                if not question:
                    return json.dumps({"success": False, "error": "Question not found."})

                db.delete(question)
                db.commit()

                return json.dumps({
                    "success": True,
                    "message": "Question deleted successfully.",
                })
        except Exception as exc:
            return self._error(exc)