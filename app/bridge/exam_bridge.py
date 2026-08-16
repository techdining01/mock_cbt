from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Slot, QTimer, QCoreApplication, QUrl
from PySide6.QtWidgets import QFileDialog
from sqlalchemy import distinct, select

from app.database.database import SessionLocal
from app.database.models import ExamSession
from app.services.exam_service import ExamService
from app.services.pdf_processor import PDFProcessor


class ExamBridge(QObject):
    def __init__(self):
        super().__init__()
        self._web_view = None

    def set_web_view(self, web_view):
        self._web_view = web_view

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

                exam = service.create_exam(
                    year=int(year),
                    subject_ids=subject_ids,
                    duration_minutes=int(duration_minutes),
                    student_name=(student_name.strip() if student_name else None),
                )

                return json.dumps(
                    {
                        "success": True,
                        "exam_id": exam.id,
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
                        "started_at": last.started_at.isoformat(),
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
                        students_dict[name]["last_exam"] = session.started_at.isoformat() if session.started_at else None
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
                        "completed_at": session.completed_at.isoformat() if session.completed_at else None,
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