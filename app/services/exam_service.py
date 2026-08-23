from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from app.database.models import (
    ExamQuestion,
    ExamSession,
    ExamSubject,
    Option,
    Question,
    StudentAnswer,
    Subject,
)


class ExamServiceError(Exception):
    """Raised when an exam operation cannot be completed."""

    pass


class ExamService:
    """
    Main service for CBT examination sessions.

    Responsibilities:
        - Find available subjects for a year
        - Create an exam session
        - Load questions in source order
        - Start the master clock
        - Save answers
        - Save question position
        - Check expiration
        - Complete the exam
        - Calculate examination results
        - Build review data
    """

    def __init__(self, db: Session):
        self.db = db

    # ========================================================
    # CREATE EXAM
    # ========================================================

    def create_exam(
        self,
        year: int,
        subject_ids: list[int],
        duration_minutes: int,
        student_name: str | None = None,
        user_id: int | None = None,
    ) -> ExamSession:

        if not subject_ids:
            raise ExamServiceError("Select at least one subject.")

        if duration_minutes <= 0:
            raise ExamServiceError("Exam duration must be greater than zero.")

        subject_ids = list(dict.fromkeys(subject_ids))

        subjects = self._get_selected_subjects(
            year=year,
            subject_ids=subject_ids,
        )

        if len(subjects) != len(subject_ids):
            raise ExamServiceError(
                "One or more selected subjects have no questions for this year."
            )

        exam = ExamSession(
            year=year,
            student_name=student_name,
            user_id=user_id,
            duration_minutes=duration_minutes,
        )

        self.db.add(exam)
        self.db.flush()

        for position, subject in enumerate(
            subjects,
            start=1,
        ):
            questions = self._get_questions(
                year=year,
                subject_id=subject.id,
            )

            if not questions:
                raise ExamServiceError(f"No questions found for {subject.name}.")

            exam_subject = ExamSubject(
                exam_session_id=exam.id,
                subject_id=subject.id,
                position=position,
                current_question_position=0,
                is_completed=False,
            )

            self.db.add(exam_subject)
            self.db.flush()

            for question_position, question in enumerate(
                questions,
                start=1,
            ):
                exam_question = ExamQuestion(
                    exam_subject_id=exam_subject.id,
                    question_id=question.id,
                    position=question_position,
                )

                self.db.add(exam_question)
                self.db.flush()

                self.db.add(
                    StudentAnswer(
                        exam_question_id=exam_question.id,
                    )
                )

        self.db.commit()

        return self.get_exam(exam.id)

    # ========================================================
    # SELECTED SUBJECTS
    # ========================================================

    def _get_selected_subjects(
        self,
        year: int,
        subject_ids: list[int],
    ) -> list[Subject]:

        statement = (
            select(Subject)
            .join(
                Question,
                Question.subject_id == Subject.id,
            )
            .where(
                Subject.id.in_(subject_ids),
                Question.year == year,
                Question.is_active.is_(True),
                Subject.is_active.is_(True),
            )
            .distinct()
        )

        subjects = list(self.db.scalars(statement).all())

        subject_map = {subject.id: subject for subject in subjects}

        return [
            subject_map[subject_id]
            for subject_id in subject_ids
            if subject_id in subject_map
        ]

    # ========================================================
    # QUESTIONS
    # ========================================================

    def _get_questions(
        self,
        year: int,
        subject_id: int,
    ) -> list[Question]:

        statement = (
            select(Question)
            .where(
                Question.year == year,
                Question.subject_id == subject_id,
                Question.is_active.is_(True),
            )
            .options(joinedload(Question.options))
            .order_by(Question.question_number)
        )

        result = self.db.execute(statement)

        return list(result.unique().scalars().all())

    # ========================================================
    # GET EXAM
    # ========================================================

    def get_exam(
        self,
        exam_id: int,
    ) -> ExamSession:

        statement = (
            select(ExamSession)
            .where(ExamSession.id == exam_id)
            .options(
                joinedload(ExamSession.subjects).joinedload(ExamSubject.subject),
                joinedload(ExamSession.subjects)
                .joinedload(ExamSubject.questions)
                .joinedload(ExamQuestion.question)
                .joinedload(Question.options),
                joinedload(ExamSession.subjects)
                .joinedload(ExamSubject.questions)
                .joinedload(ExamQuestion.answer)
                .joinedload(StudentAnswer.selected_option),
            )
        )

        result = self.db.execute(statement)

        exam = result.unique().scalar_one_or_none()

        if exam is None:
            raise ExamServiceError("Exam session not found.")

        return exam

    # ========================================================
    # START EXAM
    # ========================================================

    def start_exam(
        self,
        exam_id: int,
    ) -> ExamSession:

        exam = self.get_exam(exam_id)

        if exam.is_completed:
            raise ExamServiceError("This exam has already been completed.")

        if exam.started_at is not None:
            return exam

        now = datetime.utcnow()

        exam.started_at = now

        exam.expires_at = now + timedelta(minutes=exam.duration_minutes)

        self.db.commit()

        return self.get_exam(exam_id)

    # ========================================================
    # MASTER CLOCK
    # ========================================================

    def get_remaining_seconds(
        self,
        exam_id: int,
    ) -> int:

        exam = self.get_exam(exam_id)

        if exam.is_completed:
            return 0

        if exam.expires_at is None:
            return exam.duration_minutes * 60

        remaining = (exam.expires_at - datetime.utcnow()).total_seconds()

        return max(
            int(remaining),
            0,
        )

    # ========================================================
    # SAVE ANSWER
    # ========================================================

    def save_answer(
        self,
        exam_question_id: int,
        option_id: int,
    ) -> StudentAnswer:

        answer = self.db.scalar(
            select(StudentAnswer).where(
                StudentAnswer.exam_question_id == exam_question_id
            )
        )

        if answer is None:
            raise ExamServiceError("Answer record not found.")

        valid_option = self.db.scalar(
            select(Option)
            .join(
                ExamQuestion,
                ExamQuestion.question_id == Option.question_id,
            )
            .where(
                ExamQuestion.id == exam_question_id,
                Option.id == option_id,
            )
        )

        if valid_option is None:
            raise ExamServiceError("Selected option does not belong to this question.")

        answer.selected_option_id = option_id
        answer.answered_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(answer)

        return answer

    # ========================================================
    # SAVE CURRENT QUESTION
    # ========================================================

    def save_question_position(
        self,
        exam_subject_id: int,
        position: int,
    ) -> ExamSubject:

        if position < 0:
            raise ExamServiceError("Invalid question position.")

        exam_subject = self.db.scalar(
            select(ExamSubject).where(ExamSubject.id == exam_subject_id)
        )

        if exam_subject is None:
            raise ExamServiceError("Exam subject not found.")

        exam_subject.current_question_position = position

        self.db.commit()
        self.db.refresh(exam_subject)

        return exam_subject

    # ========================================================
    # CHECK EXPIRATION
    # ========================================================

    def check_exam_expired(
        self,
        exam_id: int,
    ) -> bool:

        exam = self.get_exam(exam_id)

        if exam.is_completed:
            return True

        remaining = self.get_remaining_seconds(exam_id)

        if remaining <= 0:
            self.complete_exam(exam_id)

            return True

        return False

    # ========================================================
    # COMPLETE EXAM
    # ========================================================

    def complete_exam(
        self,
        exam_id: int,
    ) -> ExamSession:

        exam = self.get_exam(exam_id)

        if exam.is_completed:
            return exam

        exam.is_completed = True

        exam.completed_at = datetime.utcnow()

        self.db.commit()

        return self.get_exam(exam_id)

    # ========================================================
    # EXAM PAYLOAD
    # ========================================================

    def get_exam_payload(
        self,
        exam_id: int,
    ) -> dict:

        exam = self.get_exam(exam_id)

        remaining_seconds = self.get_remaining_seconds(exam_id)

        subjects = []

        for exam_subject in exam.subjects:
            questions = []

            for exam_question in exam_subject.questions:
                question = exam_question.question

                answer = exam_question.answer

                options = []

                for option in question.options:
                    options.append(
                        {
                            "id": option.id,
                            "label": option.label,
                            "text": option.text,
                        }
                    )

                questions.append(
                    {
                        "id": exam_question.id,
                        "question_id": question.id,
                        "number": (exam_question.position),
                        "text": question.text,
                        "year": question.year,
                        "options": options,
                        "selected_option_id": (
                            answer.selected_option_id if answer else None
                        ),
                        "answered": (
                            answer.selected_option_id is not None if answer else False
                        ),
                    }
                )

            subjects.append(
                {
                    "id": exam_subject.id,
                    "subject_id": (exam_subject.subject_id),
                    "name": (exam_subject.subject.name),
                    "position": (exam_subject.position),
                    "current_question_position": (
                        exam_subject.current_question_position
                    ),
                    "is_completed": (exam_subject.is_completed),
                    "question_count": len(questions),
                    "answered_count": sum(
                        1 for question in questions if question["answered"]
                    ),
                    "questions": questions,
                }
            )

        return {
            "exam_id": exam.id,
            "year": exam.year,
            "student_name": exam.student_name,
            "duration_minutes": (exam.duration_minutes),
            "started_at": (exam.started_at.isoformat() if exam.started_at else None),
            "expires_at": (exam.expires_at.isoformat() if exam.expires_at else None),
            "remaining_seconds": (remaining_seconds),
            "is_completed": (exam.is_completed),
            "subjects": subjects,
        }

    # ========================================================
    # RESULT
    # ========================================================

    def get_result(
        self,
        exam_id: int,
    ) -> dict:

        exam = self.get_exam(exam_id)

        total = 0
        correct = 0
        wrong = 0
        unanswered = 0

        subject_results = []
        review = []

        for exam_subject in exam.subjects:
            subject_total = 0
            subject_correct = 0
            subject_wrong = 0
            subject_unanswered = 0

            for exam_question in exam_subject.questions:
                question = exam_question.question

                answer = exam_question.answer

                selected_option = answer.selected_option if answer else None

                correct_option = next(
                    (option for option in question.options if option.is_correct),
                    None,
                )

                selected_option_id = selected_option.id if selected_option else None

                correct_option_id = correct_option.id if correct_option else None

                is_answered = selected_option is not None

                is_correct = (
                    is_answered
                    and correct_option is not None
                    and selected_option.id == correct_option.id
                )

                if is_correct:
                    correct += 1
                    subject_correct += 1

                elif is_answered:
                    wrong += 1
                    subject_wrong += 1

                else:
                    unanswered += 1
                    subject_unanswered += 1

                total += 1
                subject_total += 1

                review.append(
                    {
                        "exam_question_id": (exam_question.id),
                        "question_id": (question.id),
                        "subject_id": (exam_subject.subject_id),
                        "subject_name": (exam_subject.subject.name),
                        "number": (exam_question.position),
                        "text": question.text,
                        "year": question.year,
                        "options": [
                            {
                                "id": option.id,
                                "label": option.label,
                                "text": option.text,
                            }
                            for option in question.options
                        ],
                        "selected_option_id": (selected_option_id),
                        "correct_option_id": (correct_option_id),
                        "is_answered": (is_answered),
                        "is_correct": (is_correct),
                        "explanation": (question.explanation),
                    }
                )

            subject_percentage = (
                round(
                    (subject_correct / subject_total) * 100,
                    2,
                )
                if subject_total
                else 0
            )

            subject_results.append(
                {
                    "subject_id": (exam_subject.subject_id),
                    "subject_name": (exam_subject.subject.name),
                    "total": subject_total,
                    "correct": subject_correct,
                    "wrong": subject_wrong,
                    "unanswered": subject_unanswered,
                    "percentage": (subject_percentage),
                }
            )

        percentage = (
            round(
                (correct / total) * 100,
                2,
            )
            if total
            else 0
        )

        full_name = (
            exam.user.full_name
            if (exam.user and exam.user.full_name)
            else (exam.student_name or "Student")
        )

        return {
            "exam_id": exam.id,
            "student_name": full_name,
            "student_full_name": full_name,
            "username": exam.user.username if exam.user else None,
            "year": exam.year,
            "duration_minutes": (exam.duration_minutes),
            "started_at": (exam.started_at.isoformat() if exam.started_at else None),
            "completed_at": (
                exam.completed_at.isoformat() if exam.completed_at else None
            ),
            "total": total,
            "correct": correct,
            "wrong": wrong,
            "unanswered": unanswered,
            "percentage": percentage,
            "subjects": subject_results,
            "review": review,
        }

    # ========================================================
    # AVAILABLE YEARS
    # ========================================================

    def get_available_years(
        self,
    ) -> list[int]:

        rows = (
            self.db.query(Question.year).distinct().order_by(Question.year.asc()).all()
        )

        return [row[0] for row in rows]

    # ========================================================
    # SUBJECTS FOR YEAR
    # ========================================================

    def get_subjects_for_year(
        self,
        year: int,
    ) -> list[dict]:

        rows = (
            self.db.query(
                Subject.id,
                Subject.name,
                func.count(Question.id).label("question_count"),
            )
            .join(
                Question,
                Question.subject_id == Subject.id,
            )
            .filter(
                Question.year == year,
                Question.is_active.is_(True),
                Subject.is_active.is_(True),
            )
            .group_by(
                Subject.id,
                Subject.name,
            )
            .order_by(Subject.name.asc())
            .all()
        )

        return [
            {
                "id": subject_id,
                "name": subject_name,
                "question_count": int(question_count),
            }
            for (
                subject_id,
                subject_name,
                question_count,
            ) in rows
        ]

    def get_tutor_context(
        self,
        exam_question_id: int,
    ) -> dict:

        exam_question = self.db.scalar(
            select(ExamQuestion).where(
                ExamQuestion.id == exam_question_id,
            )
        )
        if not exam_question:
            raise ValueError("Exam question not found.")

        question = exam_question.question

        answer = exam_question.answer

        correct_option = None
        selected_option = None

        options = []

        for option in question.options:
            options.append(
                {
                    "id": option.id,
                    "label": option.label,
                    "text": option.text,
                }
            )

            if option.is_correct:
                correct_option = option

            if answer and answer.selected_option_id == option.id:
                selected_option = option

        if not correct_option:
            raise ValueError("This question has no correct answer configured.")

        return {
            "exam_question_id": exam_question.id,
            "question_id": question.id,
            "subject": question.subject.name,
            "question": question.text,
            "options": options,
            "correct_answer": (f"{correct_option.label}. {correct_option.text}"),
            "student_answer": (
                (f"{selected_option.label}. {selected_option.text}")
                if selected_option
                else ""
            ),
            "explanation": (question.explanation or ""),
        }
