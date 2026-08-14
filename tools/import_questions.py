from pathlib import Path

from app.database.database import SessionLocal
from app.services.questions_importer import QuestionImporter


def main() -> None:
    """
    Import a question-bank JSON file into SQLite.
    """

    project_root = Path(__file__).resolve().parents[0]

    question_file = project_root / "question_data" / "waec_2002.json"

    session = SessionLocal()

    try:
        importer = QuestionImporter(session)

        result = importer.import_file(question_file)

        print()
        print("Question import completed.")
        print(f"Imported: {result['imported']}")
        print(f"Skipped:  {result['skipped']}")
        print()

    finally:
        session.close()


if __name__ == "__main__":
    main()
