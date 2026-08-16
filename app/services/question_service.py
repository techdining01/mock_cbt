
from __future__ import annotations

from app.database.models import (
    Question,
    Option,
    QuestionImage,
)


class QuestionService:

    # ========================================================
    # GET QUESTION
    # ========================================================

    def get_question(
        self,
        session,
        question_id: int,
    ):

        question = session.get(
            Question,
            question_id,
        )

        if question is None:
            return None

        options = (
            session.query(Option)
            .filter(
                Option.question_id == question.id
            )
            .order_by(
                Option.position
            )
            .all()
        )

        return {
            "id": question.id,
            "subject_id": question.subject_id,
            "text": question.text,
            "year": question.year,
            "number": question.question_number,
            "explanation": question.explanation,

            "images": [
                {
                    "id": image.id,
                    "question_id": image.question_id,
                    "path": image.image_path,
                    "position": image.position,
                    "type": image.image_type,
                    "source_page": image.source_page,
                }
                for image in question.images
            ],

            "options": [
                {
                    "id": option.id,
                    "label": option.label,
                    "text": option.text,
                }
                for option in options
            ],
        }

    # ========================================================
    # ADD IMAGE
    # ========================================================

    def add_question_image(
        self,
        session,
        question_id: int,
        image_path: str,
        image_type: str = "diagram",
        source_page: int | None = None,
    ):

        question = session.get(
            Question,
            question_id,
        )

        if question is None:
            raise ValueError(
                f"Question {question_id} does not exist."
            )

        last_position = (
            session.query(QuestionImage)
            .filter(
                QuestionImage.question_id
                == question_id
            )
            .count()
        )

        image = QuestionImage(
            question_id=question_id,
            image_path=image_path,
            position=last_position + 1,
            image_type=image_type,
            source_page=source_page,
        )

        session.add(image)
        session.commit()
        session.refresh(image)

        return image