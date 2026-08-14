from __future__ import annotations

import json
import subprocess
import sys


from PySide6.QtCore import QObject, Slot, QTimer, QCoreApplication
from app.database.database import SessionLocal
from app.services.exam_service import ExamService


class ExamBridge(QObject):
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
