# Import the database engine.
from app.database.database import engine

# Import our database models.
from app.database.models import Question, Option

# Import SQLAlchemy's Session.
from sqlalchemy.orm import Session


class QuestionService:
    # Get one complete question.
    def get_question(self, question_id: int):

        # Open a database session.
        with Session(engine) as session:
            # Find the question by its ID.
            question = session.get(
                Question,
                question_id,
            )

            # Return None if the question doesn't exist.
            if question is None:
                return None

            # Get all options belonging to this question.
            options = (
                session.query(Option)
                .filter(Option.question_id == question.id)
                .order_by(Option.label)
                .all()
            )

            # Build a clean dictionary for the frontend.
            return {
                "id": question.id,
                "subject_id": question.subject_id,
                "text": question.text,
                "year": question.year,
                "number": question.question_number,
                "explanation": question.explanation,
                "options": [
                    {
                        "id": option.id,
                        "label": option.label,
                        "text": option.text,
                    }
                    for option in options
                ],
            }
