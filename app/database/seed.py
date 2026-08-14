# Import the database engine.
from app.database.database import engine

# Import our models.
from app.database.models import Subject, Question, Option

# Import SQLAlchemy Session.
from sqlalchemy.orm import Session


# Open a database session.
with Session(engine) as session:
    # ---------------------------------------------------------
    # SUBJECT
    # ---------------------------------------------------------

    mathematics = Subject(name="Mathematics")

    session.add(mathematics)

    session.flush()

    # ---------------------------------------------------------
    # QUESTION 1
    # ---------------------------------------------------------

    question1 = Question(
        subject_id=mathematics.id,
        question_text="If 2x + 4 = 10, what is the value of x?",
        year=2022,
        question_number=1,
        explanation="Subtract 4 from both sides. This gives 2x = 6, therefore x = 3.",
    )

    session.add(question1)

    session.flush()

    session.add_all(
        [
            Option(
                question_id=question1.id,
                label="A",
                text="2",
                is_correct=False,
            ),
            Option(
                question_id=question1.id,
                label="B",
                text="3",
                is_correct=True,
            ),
            Option(
                question_id=question1.id,
                label="C",
                text="4",
                is_correct=False,
            ),
            Option(
                question_id=question1.id,
                label="D",
                text="5",
                is_correct=False,
            ),
        ]
    )

    # ---------------------------------------------------------
    # QUESTION 2
    # ---------------------------------------------------------

    question2 = Question(
        subject_id=mathematics.id,
        question_text="What is 15 × 4?",
        year=2022,
        question_number=2,
        explanation="15 multiplied by 4 equals 60.",
    )

    session.add(question2)

    session.flush()

    session.add_all(
        [
            Option(
                question_id=question2.id,
                label="A",
                text="45",
                is_correct=False,
            ),
            Option(
                question_id=question2.id,
                label="B",
                text="50",
                is_correct=False,
            ),
            Option(
                question_id=question2.id,
                label="C",
                text="60",
                is_correct=True,
            ),
            Option(
                question_id=question2.id,
                label="D",
                text="75",
                is_correct=False,
            ),
        ]
    )

    # ---------------------------------------------------------
    # QUESTION 3
    # ---------------------------------------------------------

    question3 = Question(
        subject_id=mathematics.id,
        question_text="What is the square of 9?",
        year=2021,
        question_number=3,
        explanation="9 × 9 = 81.",
    )

    session.add(question3)

    session.flush()

    session.add_all(
        [
            Option(
                question_id=question3.id,
                label="A",
                text="18",
                is_correct=False,
            ),
            Option(
                question_id=question3.id,
                label="B",
                text="72",
                is_correct=False,
            ),
            Option(
                question_id=question3.id,
                label="C",
                text="81",
                is_correct=True,
            ),
            Option(
                question_id=question3.id,
                label="D",
                text="90",
                is_correct=False,
            ),
        ]
    )

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    session.commit()


print("Sample CBT questions inserted successfully.")
