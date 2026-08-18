from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QObject, QTimer, Slot
from sqlalchemy import desc, func, select

from app.database.database import SessionLocal
from app.database.models import (
    ExamQuestion,
    ExamSession,
    ExamSubject,
    Option,
    Question,
    StudentAnswer,
    Subject,
    User,
)
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
                return json.dumps({
                    "success": True,
                    "years": years,
                })
        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # SUBJECTS
    # ========================================================

    @Slot(int, result=str)
    def get_subjects_for_year(self, year: int):
        try:
            with SessionLocal() as db:
                service = ExamService(db)
                subjects = service.get_subjects_for_year(int(year))
                return json.dumps({
                    "success": True,
                    "subjects": subjects,
                })
        except Exception as exc:
            return self._error(exc)

    @Slot(result=str)
    def get_all_subjects(self):
        """Returns all subjects registered in the system."""
        try:
            with SessionLocal() as db:
                subjects = db.scalars(select(Subject).order_by(Subject.name.asc())).all()
                return json.dumps({
                    "success": True,
                    "subjects": [
                        {"id": s.id, "name": s.name, "code": s.code, "is_active": s.is_active}
                        for s in subjects
                    ],
                })
        except Exception as exc:
            return self._error(exc)

    @Slot(str, str, result=str)
    def create_subject(self, name: str, code: str):
        """Registers a new examination subject."""
        try:
            s_name = str(name or "").strip()
            s_code = str(code or "").strip().upper()
            if not s_name:
                return json.dumps({"success": False, "error": "Subject name is required."})
            if not s_code:
                return json.dumps({"success": False, "error": "Subject code is required."})

            with SessionLocal() as db:
                existing = db.scalar(
                    select(Subject).where((func.lower(Subject.name) == s_name.lower()) | (func.upper(Subject.code) == s_code))
                )
                if existing:
                    return json.dumps({"success": False, "error": f"Subject '{s_name}' or code '{s_code}' already exists."})

                subj = Subject(name=s_name, code=s_code, is_active=True)
                db.add(subj)
                db.commit()
                db.refresh(subj)
                return json.dumps({
                    "success": True,
                    "subject": {"id": subj.id, "name": subj.name, "code": subj.code, "is_active": subj.is_active},
                })
        except Exception as exc:
            return self._error(exc)

    @Slot(int, int, result=str)
    def get_next_question_number(self, year: int, subject_id: int):
        """Returns the next sequential question number for a subject and year."""
        try:
            with SessionLocal() as db:
                max_num = db.scalar(
                    select(func.max(Question.question_number))
                    .where(Question.year == int(year), Question.subject_id == int(subject_id))
                ) or 0
                return json.dumps({"success": True, "next_number": max_num + 1})
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
        """Creates a question with progressive options (A-E) and educational explanation."""
        try:
            q_text = str(text or "").strip()
            if not q_text:
                return json.dumps({"success": False, "error": "Question text is required."})

            options_data = json.loads(options_json) if isinstance(options_json, str) else options_json
            if not options_data or len(options_data) < 2:
                return json.dumps({"success": False, "error": "At least 2 options (e.g. A, B) are required."})

            corr_lbl = str(correct_label or "").strip().upper()

            with SessionLocal() as db:
                subj = db.get(Subject, int(subject_id))
                if not subj:
                    return json.dumps({"success": False, "error": "Subject not found."})

                existing = db.scalar(
                    select(Question).where(
                        Question.year == int(year),
                        Question.subject_id == int(subject_id),
                        Question.question_number == int(question_number),
                    )
                )
                if existing:
                    return json.dumps({
                        "success": False,
                        "error": f"Question #{question_number} already exists for this subject in year {year}."
                    })

                question = Question(
                    subject_id=int(subject_id),
                    year=int(year),
                    question_number=int(question_number),
                    text=q_text,
                    explanation=str(explanation or "").strip(),
                    is_active=True,
                )
                db.add(question)
                db.flush()

                for idx, opt_item in enumerate(options_data, start=1):
                    lbl = str(opt_item.get("label", "")).strip().upper() or chr(64 + idx)
                    opt_text = str(opt_item.get("text", "")).strip()
                    is_corr = (lbl == corr_lbl)
                    opt = Option(
                        question_id=question.id,
                        label=lbl,
                        position=idx,
                        text=opt_text,
                        is_correct=is_corr,
                    )
                    db.add(opt)

                db.commit()
                db.refresh(question)

                return json.dumps({
                    "success": True,
                    "question_id": question.id,
                    "question_number": question.question_number,
                    "message": "Question created successfully.",
                })
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
        """Fetches questions matching filters with pagination."""
        try:
            with SessionLocal() as db:
                query = select(Question).order_by(Question.year.desc(), Question.subject_id.asc(), Question.question_number.asc())

                if year_str and str(year_str).strip().isdigit():
                    query = query.where(Question.year == int(year_str))
                if subject_id_str and str(subject_id_str).strip().isdigit():
                    query = query.where(Question.subject_id == int(subject_id_str))
                if search_query and str(search_query).strip():
                    q_term = f"%{str(search_query).strip().lower()}%"
                    query = query.where(func.lower(Question.text).like(q_term))

                total = db.scalar(select(func.count()).select_from(query.subquery())) or 0

                offset_val = max(0, (int(page) - 1) * int(page_size))
                items = db.scalars(query.offset(offset_val).limit(int(page_size))).all()

                questions_list = []
                for q in items:
                    subj = db.get(Subject, q.subject_id)
                    opts = [
                        {"id": o.id, "label": o.label, "position": o.position, "text": o.text, "is_correct": o.is_correct}
                        for o in sorted(q.options, key=lambda x: x.position or 0)
                    ]
                    corr_lbl = next((o["label"] for o in opts if o["is_correct"]), "A")
                    questions_list.append({
                        "id": q.id,
                        "subject_id": q.subject_id,
                        "subject_name": subj.name if subj else "Unknown",
                        "year": q.year,
                        "question_number": q.question_number,
                        "text": q.text,
                        "explanation": q.explanation,
                        "correct_label": corr_lbl,
                        "options": opts,
                        "is_active": q.is_active,
                    })

                return json.dumps({
                    "success": True,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "questions": questions_list,
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
        """Updates an existing question and its options."""
        try:
            with SessionLocal() as db:
                question = db.get(Question, int(question_id))
                if not question:
                    return json.dumps({"success": False, "error": "Question not found."})

                q_text = str(text or "").strip()
                if not q_text:
                    return json.dumps({"success": False, "error": "Question text is required."})

                options_data = json.loads(options_json) if isinstance(options_json, str) else options_json
                if not options_data or len(options_data) < 2:
                    return json.dumps({"success": False, "error": "At least 2 options are required."})

                corr_lbl = str(correct_label or "").strip().upper()

                question.year = int(year)
                question.subject_id = int(subject_id)
                question.question_number = int(question_number)
                question.text = q_text
                question.explanation = str(explanation or "").strip()

                # Delete existing options and recreate
                for old_opt in list(question.options):
                    db.delete(old_opt)
                db.flush()

                for idx, opt_item in enumerate(options_data, start=1):
                    lbl = str(opt_item.get("label", "")).strip().upper() or chr(64 + idx)
                    opt_text = str(opt_item.get("text", "")).strip()
                    is_corr = (lbl == corr_lbl)
                    opt = Option(
                        question_id=question.id,
                        label=lbl,
                        position=idx,
                        text=opt_text,
                        is_correct=is_corr,
                    )
                    db.add(opt)

                db.commit()
                return json.dumps({"success": True, "message": "Question updated successfully."})
        except Exception as exc:
            return self._error(exc)

    @Slot(int, result=str)
    def delete_question_manual(self, question_id: int):
        """Deletes a question and its options."""
        try:
            with SessionLocal() as db:
                question = db.get(Question, int(question_id))
                if not question:
                    return json.dumps({"success": False, "error": "Question not found."})

                db.delete(question)
                db.commit()
                return json.dumps({"success": True, "message": "Question deleted successfully."})
        except Exception as exc:
            return self._error(exc)

    @Slot(int, result=str)
    def delete_subject(self, subject_id: int):
        """Deletes an examination subject."""
        try:
            with SessionLocal() as db:
                subj = db.get(Subject, int(subject_id))
                if not subj:
                    return json.dumps({"success": False, "error": "Subject not found."})

                db.delete(subj)
                db.commit()
                return json.dumps({"success": True, "message": "Subject deleted successfully."})
        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # CREATE EXAM
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
            candidate_identifier = str(student_name or "").strip()

            with SessionLocal() as db:
                user_id = None
                display_name = candidate_identifier or "Candidate"

                # Check if candidate_identifier matches a registered User
                if candidate_identifier:
                    user = db.scalar(
                        select(User).where(
                            func.lower(User.username) == candidate_identifier.lower()
                        )
                    )
                    if not user:
                        # Try matching by full name
                        user = db.scalar(
                            select(User).where(
                                func.lower(User.full_name) == candidate_identifier.lower()
                            )
                        )

                    if user:
                        if user.role == "admin":
                            return json.dumps({
                                "success": False,
                                "error": "Admin accounts cannot take exams. Please register or select a student account.",
                            })
                        user_id = user.id
                        display_name = user.full_name

                service = ExamService(db)
                exam = service.create_exam(
                    year=int(year),
                    subject_ids=subject_ids,
                    duration_minutes=int(duration_minutes),
                    student_name=display_name,
                    user_id=user_id,
                )

                return json.dumps({
                    "success": True,
                    "exam_id": exam.id,
                })
        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # START EXAM
    # ========================================================

    @Slot(int, result=str)
    def start_exam(self, exam_id: int):
        try:
            with SessionLocal() as db:
                service = ExamService(db)
                exam = service.start_exam(int(exam_id))
                remaining = service.get_remaining_seconds(exam.id)
                return json.dumps({
                    "success": True,
                    "exam_id": exam.id,
                    "remaining_seconds": remaining,
                })
        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # GET EXAM
    # ========================================================

    @Slot(int, result=str)
    def get_exam(self, exam_id: int):
        try:
            with SessionLocal() as db:
                service = ExamService(db)
                exam_dict = service.get_exam_payload(int(exam_id))
                return json.dumps({
                    "success": True,
                    "exam": exam_dict,
                })
        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # SAVE ANSWER
    # ========================================================

    @Slot(int, int, result=str)
    def save_answer(self, exam_question_id: int, option_id: int):
        try:
            with SessionLocal() as db:
                service = ExamService(db)
                service.save_answer(int(exam_question_id), int(option_id))
                return json.dumps({
                    "success": True,
                    "exam_question_id": exam_question_id,
                    "selected_option_id": option_id,
                })
        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # SAVE QUESTION POSITION
    # ========================================================

    @Slot(int, int, result=str)
    def save_question_position(self, exam_subject_id: int, position: int):
        try:
            with SessionLocal() as db:
                service = ExamService(db)
                service.save_question_position(int(exam_subject_id), int(position))
                return json.dumps({
                    "success": True,
                    "exam_subject_id": exam_subject_id,
                    "position": position,
                })
        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # REMAINING TIME
    # ========================================================

    @Slot(int, result=str)
    def get_remaining_time(self, exam_id: int):
        try:
            with SessionLocal() as db:
                service = ExamService(db)
                remaining = service.get_remaining_seconds(int(exam_id))
                expired = service.is_expired(int(exam_id))
                return json.dumps({
                    "success": True,
                    "remaining_seconds": remaining,
                    "expired": expired,
                })
        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # COMPLETE EXAM
    # ========================================================

    @Slot(int, result=str)
    def complete_exam(self, exam_id: int):
        try:
            with SessionLocal() as db:
                service = ExamService(db)
                service.complete_exam(int(exam_id))
                result = service.get_result(int(exam_id))
                return json.dumps({
                    "success": True,
                    "result": result,
                })
        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # GET RESULT
    # ========================================================

    @Slot(int, result=str)
    def get_result(self, exam_id: int):
        try:
            with SessionLocal() as db:
                service = ExamService(db)
                result = service.get_result(int(exam_id))
                return json.dumps({
                    "success": True,
                    "result": result,
                })
        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # REPORTLAB PDF GENERATION (SINGLE EXAM)
    # ========================================================

    @Slot(int, result=str)
    def generate_result_pdf_reportlab(self, exam_id: int):
        """Generates a professional PDF result transcript using ReportLab."""
        try:
            with SessionLocal() as db:
                service = ExamService(db)
                result = service.get_result(int(exam_id))

            from app.services.reportlab_report_service import ReportlabReportService

            report_service = ReportlabReportService()
            pdf_path = report_service.generate(result)

            try:
                if hasattr(os, "startfile"):
                    os.startfile(pdf_path)
            except Exception as open_err:
                print("Could not auto-open PDF:", open_err)

            return json.dumps({
                "success": True,
                "path": str(pdf_path),
                "message": f"Result PDF saved successfully to {pdf_path}",
            })
        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # AUTHENTICATION & IDENTITY (ADMIN LOGIN & USER CHECK)
    # ========================================================

    @Slot(str, str, result=str)
    def login_admin(self, username: str, password: str):
        """Authenticates an administrative user."""
        try:
            u_name = str(username or "").strip()
            p_word = str(password or "").strip()

            if not u_name or not p_word:
                return json.dumps({"success": False, "error": "Username and password are required."})

            with SessionLocal() as db:
                user = db.scalar(select(User).where(func.lower(User.username) == u_name.lower()))
                if not user or user.password != p_word:
                    return json.dumps({"success": False, "error": "Invalid admin username or password."})

                if user.role != "admin":
                    return json.dumps({"success": False, "error": "Access denied: Account is not an administrator."})

                if not user.is_active:
                    return json.dumps({"success": False, "error": "Account is deactivated. Contact system administrator."})

                return json.dumps({
                    "success": True,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "full_name": user.full_name,
                        "role": user.role,
                    }
                })
        except Exception as exc:
            return self._error(exc)

    @Slot(str, result=str)
    def check_username(self, username: str):
        """
        Looks up a username to check if the candidate already exists in the DB.
        Returns user full name and class for auto-fill/suggestion, or exists=False.
        """
        try:
            u_name = str(username or "").strip()
            if not u_name:
                return json.dumps({"success": True, "exists": False})

            with SessionLocal() as db:
                user = db.scalar(select(User).where(func.lower(User.username) == u_name.lower()))
                if user:
                    return json.dumps({
                        "success": True,
                        "exists": True,
                        "is_admin": (user.role == "admin"),
                        "user": {
                            "id": user.id,
                            "username": user.username,
                            "full_name": user.full_name,
                            "role": user.role,
                            "student_class": user.student_class or "",
                            "admission_year": user.admission_year,
                            "is_active": user.is_active,
                        }
                    })

                # Also try lookup by full name if entered
                user_by_fn = db.scalar(select(User).where(func.lower(User.full_name) == u_name.lower()))
                if user_by_fn:
                    return json.dumps({
                        "success": True,
                        "exists": True,
                        "is_admin": (user_by_fn.role == "admin"),
                        "user": {
                            "id": user_by_fn.id,
                            "username": user_by_fn.username,
                            "full_name": user_by_fn.full_name,
                            "role": user_by_fn.role,
                            "student_class": user_by_fn.student_class or "",
                            "admission_year": user_by_fn.admission_year,
                            "is_active": user_by_fn.is_active,
                        }
                    })

                return json.dumps({"success": True, "exists": False})
        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # USER MANAGEMENT CRUD (ADMIN & STUDENT REGISTRATION)
    # ========================================================

    @Slot(str, str, str, str, str, str, result=str)
    def register_user(
        self,
        username: str,
        password: str,
        full_name: str,
        role: str = "student",
        student_class: str = "",
        admission_year: str = "",
    ):
        """Creates a new User account (Admin or Student)."""
        try:
            u_name = str(username or "").strip()
            p_word = str(password or "").strip() or "cbt123"
            f_name = str(full_name or "").strip()
            u_role = str(role or "student").strip().lower()
            if u_role not in ["admin", "student"]:
                u_role = "student"

            s_class = str(student_class or "").strip() if u_role == "student" else None
            adm_year = int(admission_year) if (admission_year and str(admission_year).isdigit() and u_role == "student") else None

            if not u_name:
                return json.dumps({"success": False, "error": "Username is required."})
            if not f_name:
                return json.dumps({"success": False, "error": "Full name is required."})

            with SessionLocal() as db:
                existing = db.scalar(select(User).where(func.lower(User.username) == u_name.lower()))
                if existing:
                    return json.dumps({"success": False, "error": f"Username '{u_name}' is already registered."})

                user = User(
                    username=u_name,
                    password=p_word,
                    full_name=f_name,
                    role=u_role,
                    student_class=s_class,
                    admission_year=adm_year,
                    is_active=True,
                )
                db.add(user)
                db.commit()
                db.refresh(user)

                return json.dumps({
                    "success": True,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "full_name": user.full_name,
                        "role": user.role,
                        "student_class": user.student_class or "",
                        "admission_year": user.admission_year,
                        "is_active": user.is_active,
                    }
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
        """Convenience method for student self-registration before exam."""
        return self.register_user(
            username=username,
            password=password,
            full_name=full_name,
            role="student",
            student_class=student_class,
            admission_year=admission_year,
        )

    @Slot(result=str)
    def get_all_users(self):
        """Returns all registered user accounts with session counts."""
        try:
            with SessionLocal() as db:
                users = db.scalars(select(User).order_by(desc(User.created_at))).all()
                result_list = []
                for u in users:
                    session_count = db.scalar(
                        select(func.count(ExamSession.id)).where(ExamSession.user_id == u.id)
                    ) or 0
                    result_list.append({
                        "id": u.id,
                        "username": u.username,
                        "full_name": u.full_name,
                        "role": u.role,
                        "student_class": u.student_class or "",
                        "admission_year": u.admission_year,
                        "is_active": u.is_active,
                        "exam_count": session_count,
                        "created_at": u.created_at.strftime("%Y-%m-%d %H:%M") if u.created_at else "",
                    })

                return json.dumps({"success": True, "users": result_list})
        except Exception as exc:
            return self._error(exc)

    @Slot(int, str, str, str, str, str, str, str, result=str)
    def update_user(
        self,
        user_id: int,
        username: str,
        password: str,
        full_name: str,
        role: str,
        student_class: str,
        admission_year: str,
        is_active: str,
    ):
        """Updates user account details."""
        try:
            with SessionLocal() as db:
                user = db.get(User, int(user_id))
                if not user:
                    return json.dumps({"success": False, "error": "User not found."})

                f_name = str(full_name or "").strip()
                if f_name:
                    user.full_name = f_name

                p_word = str(password or "").strip()
                if p_word:
                    user.password = p_word

                u_role = str(role or user.role).strip().lower()
                if u_role in ["admin", "student"]:
                    user.role = u_role

                if user.role == "student":
                    user.student_class = str(student_class or "").strip() or None
                    user.admission_year = int(admission_year) if (admission_year and str(admission_year).isdigit()) else None
                else:
                    user.student_class = None
                    user.admission_year = None

                user.is_active = is_active.lower() == "true" if is_active else True
                db.commit()
                db.refresh(user)

                return json.dumps({
                    "success": True,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "full_name": user.full_name,
                        "role": user.role,
                        "student_class": user.student_class or "",
                        "admission_year": user.admission_year,
                        "is_active": user.is_active,
                    }
                })
        except Exception as exc:
            return self._error(exc)

    @Slot(int, result=str)
    def delete_user(self, user_id: int):
        """Deletes a user account."""
        try:
            with SessionLocal() as db:
                user = db.get(User, int(user_id))
                if not user:
                    return json.dumps({"success": False, "error": "User not found."})

                # Prevent deleting the last admin
                if user.role == "admin":
                    admin_count = db.scalar(select(func.count(User.id)).where(User.role == "admin"))
                    if admin_count <= 1:
                        return json.dumps({"success": False, "error": "Cannot delete the only remaining system administrator."})

                db.delete(user)
                db.commit()
                return json.dumps({"success": True, "message": "User deleted successfully."})
        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # STUDENT EXAMINATION RECORDS & TRANSCRIPT HISTORY
    # ========================================================

    @Slot(result=str)
    def get_all_student_records(self):
        """Returns aggregated examination records grouped by student."""
        try:
            with SessionLocal() as db:
                sessions = db.scalars(
                    select(ExamSession)
                    .where(ExamSession.student_name.is_not(None))
                    .order_by(desc(ExamSession.started_at))
                ).all()

                student_map: dict[str, dict] = {}
                service = ExamService(db)

                for sess in sessions:
                    name = (sess.student_name or "Unknown").strip()
                    if name not in student_map:
                        user = db.get(User, sess.user_id) if sess.user_id else None
                        student_map[name] = {
                            "name": name,
                            "session_count": 0,
                            "last_exam": sess.started_at.isoformat() if sess.started_at else None,
                            "student_class": user.student_class if user else "",
                            "admission_year": user.admission_year if user else None,
                            "scores": [],
                        }

                    student_map[name]["session_count"] += 1
                    try:
                        res = service.get_result(sess.id)
                        student_map[name]["scores"].append(float(res.get("percentage", 0)))
                    except Exception:
                        pass

                records = []
                for s in student_map.values():
                    avg_score = round(sum(s["scores"]) / len(s["scores"]), 1) if s["scores"] else 0.0
                    best_score = round(max(s["scores"]), 1) if s["scores"] else 0.0
                    records.append({
                        "name": s["name"],
                        "session_count": s["session_count"],
                        "last_exam": s["last_exam"],
                        "student_class": s["student_class"],
                        "admission_year": s["admission_year"],
                        "avg_score": avg_score,
                        "best_score": best_score,
                    })

                records.sort(key=lambda r: r["name"].lower())
                return json.dumps({"success": True, "students": records})
        except Exception as exc:
            return self._error(exc)

    @Slot(str, result=str)
    def get_student_history(self, student_name: str):
        """Returns detailed exam sessions and scores for a specific student."""
        try:
            s_name = str(student_name or "").strip()
            with SessionLocal() as db:
                user = db.scalar(
                    select(User).where(
                        (func.lower(User.username) == s_name.lower()) |
                        (func.lower(User.full_name) == s_name.lower())
                    )
                )

                query = select(ExamSession)
                if user:
                    query = query.where(
                        (ExamSession.user_id == user.id) |
                        (func.lower(ExamSession.student_name) == user.full_name.lower()) |
                        (func.lower(ExamSession.student_name) == user.username.lower())
                    )
                else:
                    query = query.where(func.lower(ExamSession.student_name) == s_name.lower())

                sessions = db.scalars(query.order_by(desc(ExamSession.started_at))).all()
                service = ExamService(db)

                history_list = []
                for sess in sessions:
                    try:
                        res = service.get_result(sess.id)
                        subject_names = [s["subject_name"] for s in res.get("subjects", [])]
                        date_fmt = sess.started_at.strftime("%b %d, %Y %I:%M %p") if sess.started_at else "N/A"
                        history_list.append({
                            "id": sess.id,
                            "year": sess.year,
                            "date_formatted": date_fmt,
                            "started_at": sess.started_at.isoformat() if sess.started_at else None,
                            "completed_at": sess.completed_at.isoformat() if sess.completed_at else None,
                            "subjects": subject_names,
                            "subjects_str": ", ".join(subject_names),
                            "total": res.get("total", 0),
                            "correct": res.get("correct", 0),
                            "wrong": res.get("wrong", 0),
                            "unanswered": res.get("unanswered", 0),
                            "percentage": res.get("percentage", 0.0),
                            "is_completed": sess.is_completed,
                        })
                    except Exception:
                        pass

                user_payload = {
                    "full_name": user.full_name if user else s_name,
                    "student_class": user.student_class if user else "",
                    "admission_year": user.admission_year if user else None,
                }

                return json.dumps({
                    "success": True,
                    "student_name": user_payload["full_name"],
                    "user_info": user_payload,
                    "history": history_list,
                })
        except Exception as exc:
            return self._error(exc)

    @Slot(str, result=str)
    def delete_student_records(self, student_name: str):
        """Deletes all examination sessions for a given student."""
        try:
            s_name = str(student_name or "").strip()
            with SessionLocal() as db:
                user = db.scalar(
                    select(User).where(
                        (func.lower(User.username) == s_name.lower()) |
                        (func.lower(User.full_name) == s_name.lower())
                    )
                )
                if user:
                    sessions = db.scalars(
                        select(ExamSession).where(
                            (ExamSession.user_id == user.id) |
                            (func.lower(ExamSession.student_name) == user.full_name.lower()) |
                            (func.lower(ExamSession.student_name) == user.username.lower())
                        )
                    ).all()
                else:
                    sessions = db.scalars(
                        select(ExamSession).where(func.lower(ExamSession.student_name) == s_name.lower())
                    ).all()

                count = len(sessions)
                for sess in sessions:
                    db.delete(sess)
                db.commit()

                return json.dumps({
                    "success": True,
                    "message": f"Successfully deleted {count} exam session(s) for '{s_name}'.",
                })
        except Exception as exc:
            return self._error(exc)

    @Slot(str, result=str)
    def generate_student_history_pdf(self, student_name: str):
        """Generates and opens a PDF transcript of all exam sessions taken by a student."""
        try:
            history_json = self.get_student_history(student_name)
            data = json.loads(history_json)
            if not data.get("success"):
                return history_json

            from app.services.reportlab_report_service import ReportlabReportService

            report_service = ReportlabReportService()
            pdf_path = report_service.generate_student_history(
                student_name=data.get("student_name", student_name),
                sessions=data.get("history", []),
                user_info=data.get("user_info"),
            )

            try:
                if hasattr(os, "startfile"):
                    os.startfile(pdf_path)
            except Exception as open_err:
                print("Could not auto-open PDF:", open_err)

            return json.dumps({
                "success": True,
                "path": str(pdf_path),
                "message": f"Student history transcript PDF saved to {pdf_path}",
            })
        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # RESTART APPLICATION
    # ========================================================

    @Slot(result=str)
    def restart_application(self):
        try:
            subprocess.Popen([sys.executable, *sys.argv], cwd=None)
            QTimer.singleShot(300, self._quit_current_application)
            return json.dumps({"success": True})
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
    # WINDOW REFERENCE & PRINTING
    # ========================================================

    def set_window(self, window):
        self._window = window

    @Slot(result=str)
    def print_current_page(self):
        """Opens native Qt Print Dialog to print the current examination document."""
        try:
            if hasattr(self, "_window") and self._window is not None:
                from PySide6.QtPrintSupport import QPrintDialog, QPrinter
                printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                dialog = QPrintDialog(printer, self._window)
                dialog.setWindowTitle("Print CBT Examination Document")
                if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                    self._window.page().print(printer, lambda ok: None)
                    return json.dumps({"success": True, "message": "Print job sent to printer."})
                else:
                    return json.dumps({"success": False, "cancelled": True, "message": "Print cancelled."})
            return json.dumps({"success": False, "error": "Window reference not set."})
        except Exception as exc:
            return self._error(exc)

    # ========================================================
    # ERROR
    # ========================================================

    @staticmethod
    def _error(exc: Exception):
        return json.dumps({
            "success": False,
            "error": str(exc),
        })
