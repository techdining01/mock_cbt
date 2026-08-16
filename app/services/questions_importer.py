from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Option, Question, Subject, QuestionImage


class QuestionImportError(Exception):
    """
    Raised when question-bank data is invalid.
    """

    pass


class QuestionImporter:
    """
    Imports prepared question-bank JSON data into SQLite.

    The importer is intentionally independent of OCR.

    OCR creates the source data.
    This class imports validated data into the database.
    """

    REQUIRED_OPTION_LABELS = {"A", "B", "C", "D"}

    def __init__(self, session: Session):
        self.session = session

    # ========================================================
    # PUBLIC API
    # ========================================================

    def import_file(self, file_path: str | Path) -> dict[str, int]:
        """
        Import one JSON question-bank file.

        Returns statistics about the import.
        """

        path = Path(file_path)

        if not path.exists():
            raise QuestionImportError(f"Question file does not exist: {path}")

        if path.suffix.lower() != ".json":
            raise QuestionImportError("Question-bank files must be JSON.")

        try:
            with path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

        except json.JSONDecodeError as exc:
            raise QuestionImportError(f"Invalid JSON file: {path}") from exc

        return self.import_data(data)

    # ========================================================

    def import_data(
        self,
        data: dict[str, Any],
    ) -> dict[str, int]:
        """
        Import already-loaded question-bank data.
        """

        self._validate_document(data)

        year = data["year"]

        imported = 0
        skipped = 0

        try:
            for subject_data in data["subjects"]:
                subject = self._get_or_create_subject(
                    name=subject_data["name"],
                    code=subject_data.get("code"),
                )

                for question_data in subject_data["questions"]:
                    created = self._import_question(
                        subject=subject,
                        year=year,
                        question_data=question_data,
                    )

                    if created:
                        imported += 1
                    else:
                        skipped += 1

            self.session.commit()

        except Exception:
            self.session.rollback()
            raise

        return {
            "imported": imported,
            "skipped": skipped,
        }

    # ========================================================
    # VALIDATION
    # ========================================================

    def _validate_document(
        self,
        data: dict[str, Any],
    ) -> None:

        if not isinstance(data, dict):
            raise QuestionImportError("Root JSON value must be an object.")

        if "year" not in data:
            raise QuestionImportError("Missing required field: year")

        if "subjects" not in data:
            raise QuestionImportError("Missing required field: subjects")

        year = data["year"]

        if not isinstance(year, int):
            raise QuestionImportError("year must be an integer.")

        if year < 1900 or year > 2100:
            raise QuestionImportError(f"Invalid examination year: {year}")

        if not isinstance(data["subjects"], list):
            raise QuestionImportError("subjects must be a list.")

    # ========================================================
    # SUBJECT
    # ========================================================

    def _get_or_create_subject(
        self,
        name: str,
        code: str | None = None,
    ) -> Subject:

        name = name.strip()

        if not name:
            raise QuestionImportError("Subject name cannot be empty.")

        statement = select(Subject).where(Subject.name == name)

        subject = self.session.scalar(statement)

        if subject:
            return subject

        subject = Subject(
            name=name,
            code=code,
        )

        self.session.add(subject)

        self.session.flush()

        return subject

    # ========================================================
    # QUESTION
    # ========================================================

    def _import_question(
        self,
        subject: Subject,
        year: int,
        question_data: dict[str, Any],
    ) -> bool:
        """
        Import one question.

        Returns:

            True  → newly created
            False → already exists
        """

        self._validate_question(question_data)

        normalized_question = (
            self._normalize_question_data(
                question_data
            )
        )

        question_number = normalized_question["question_number"]

        # ----------------------------------------------------
        # Check for an existing question.
        # ----------------------------------------------------

        statement = select(Question).where(
            Question.subject_id == subject.id,
            Question.year == year,
            Question.question_number == question_number,
        )

        existing_question = self.session.scalar(statement)

        if existing_question:
            return False

        # ----------------------------------------------------
        # Create question.
        # ----------------------------------------------------

        question = Question(
            subject=subject,
            year=year,
            question_number=question_number,
            text=normalized_question["text"].strip(),
            explanation=self._clean_optional_text(
                normalized_question.get("explanation")
            ),
            source_reference=self._clean_optional_text(
                normalized_question.get("source_reference")
            ),
            source_page=normalized_question.get("source_page"),
        )

        for position, image_path in enumerate(
            normalized_question.get("images", []),
            start=1,
        ):
            image = QuestionImage(
                image_path=image_path,
                position=position,
                image_type="diagram",
                source_page=normalized_question.get("source_page"),
            )
            question.images.append(image)
        self.session.add(question)

        self.session.flush()

        # ----------------------------------------------------
        # Create options.
        # ----------------------------------------------------

        for position, option_data in enumerate(
            normalized_question["options"],
            start=1,
        ):
            option = Option(
                question=question,
                label=option_data["label"],
                position=position,
                text=option_data["text"].strip(),
                is_correct=option_data["is_correct"],
            )

            self.session.add(option)

        self.session.flush()

        return True

    # ========================================================
    # QUESTION VALIDATION
    # ========================================================

    def _validate_question(
        self,
        question_data: dict[str, Any],
    ) -> None:

        question_data = self._normalize_question_data(
            question_data
        )

        if not isinstance(question_data, dict):
            raise QuestionImportError("Each question must be an object.")

        required_fields = {
            "question_number",
            "text",
            "options",
        }

        missing = required_fields - question_data.keys()

        if missing:
            raise QuestionImportError(
                f"Question is missing fields: {', '.join(sorted(missing))}"
            )

        if not isinstance(
            question_data["question_number"],
            int,
        ):
            raise QuestionImportError("Question number must be an integer.")

        if question_data["question_number"] <= 0:
            raise QuestionImportError("Question number must be greater than zero.")

        if not isinstance(
            question_data["text"],
            str,
        ):
            raise QuestionImportError("Question text must be a string.")

        if not question_data["text"].strip():
            raise QuestionImportError("Question text cannot be empty.")

        options = question_data["options"]

        if not isinstance(options, list):
            raise QuestionImportError("Question options must be a list.")

        if len(options) < 2:
            raise QuestionImportError("A question must have at least two options.")

        labels = set()
        correct_count = 0

        for option in options:
            if not isinstance(option, dict):
                raise QuestionImportError("Each option must be an object.")

            required_option_fields = {
                "label",
                "text",
                "is_correct",
            }

            missing = required_option_fields - option.keys()

            if missing:
                raise QuestionImportError(
                    f"Option is missing fields: {', '.join(sorted(missing))}"
                )

            label = str(option["label"]).strip().upper()

            if label in labels:
                raise QuestionImportError(f"Duplicate option label: {label}")

            labels.add(label)

            if not option["text"].strip():
                raise QuestionImportError(f"Option {label} has empty text.")

            if option["is_correct"]:
                correct_count += 1

        # ----------------------------------------------------
        # Standard four-option CBT questions should have
        # exactly one correct answer.
        # ----------------------------------------------------

        if correct_count != 1:
            raise QuestionImportError(
                "Each question must have exactly one correct option."
            )

    # ========================================================
    # HELPERS
    # ========================================================

    @staticmethod
    def _clean_optional_text(
        value: Any,
    ) -> str | None:

        if value is None:
            return None

        if not isinstance(value, str):
            return str(value)

        value = value.strip()

        return value or None

    def _normalize_question_data(
        self,
        question_data: dict[str, Any],
    ) -> dict[str, Any]:

        normalized = dict(question_data)

        if (
            "question_number" not in normalized
            and "number" in normalized
        ):
            normalized["question_number"] = normalized["number"]

        try:
            normalized["question_number"] = int(
                normalized["question_number"]
            )
        except Exception:
            pass

        source_page = normalized.get(
            "source_page"
        )

        if source_page not in (
            None,
            "",
        ):
            try:
                normalized["source_page"] = int(
                    source_page
                )
            except Exception:
                normalized["source_page"] = None

        normalized["images"] = [
            self._normalize_image_path(
                image
            )
            for image in normalized.get(
                "images",
                [],
            )
            if self._normalize_image_path(
                image
            )
        ]

        normalized["options"] = [
            self._normalize_option_data(
                option
            )
            for option in normalized.get(
                "options",
                [],
            )
        ]

        return normalized

    @staticmethod
    def _normalize_option_data(
        option: dict[str, Any],
    ) -> dict[str, Any]:

        normalized = dict(option)

        normalized["label"] = str(
            normalized.get("label", "")
        ).strip().upper()

        normalized["text"] = str(
            normalized.get("text", "")
        )

        normalized["is_correct"] = bool(
            normalized.get("is_correct", False)
        )

        return normalized

    @staticmethod
    def _normalize_image_path(
        image: Any,
    ) -> str | None:

        if isinstance(image, str):
            return image.strip() or None

        if isinstance(image, dict):
            path = image.get("path")
            if path is None:
                return None
            return str(path).strip() or None

        return None
