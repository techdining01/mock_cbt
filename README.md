# Mock CBT

A desktop Computer-Based Testing (CBT) application built with PySide6 and Alpine.js. Students take timed mock exams using past questions; admins manage users, subjects, questions, and view results.

---

## Features

- **Exam Engine** — timed multi-subject exams with answer persistence and auto-submit on expiry
- **Admin Panel** — user management, subject management, manual question editor, student history
- **Question Import** — import questions from PDF via OCR (Tesseract) or JSON bulk import
- **AI Tutor** — per-question explanations powered by Google Gemini (FastAPI sidecar on port 8000)
- **PDF Reports** — generate and print exam result transcripts via ReportLab
- **Role-based access** — `admin` and `student` roles with bcrypt-hashed passwords

---

## Tech Stack

| Layer | Technology |
|---|---|
| Desktop shell | PySide6 (Qt WebEngine) |
| Frontend | HTML + Tailwind CSS + Alpine.js |
| Backend bridge | PySide6 QWebChannel (Python ↔ JS) |
| AI Tutor API | FastAPI + Uvicorn (localhost:8000) |
| Database | SQLite via SQLAlchemy 2.0 |
| OCR | Tesseract + OpenCV + PyMuPDF |
| PDF generation | ReportLab |

---

## Requirements

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed and on PATH
- A `.env` file with your Google Gemini API key (see below)

---

## Setup

```bash
# 1. Clone the repo
git clone <repo-url>
cd mock_cbt

# 2. Install dependencies
uv sync
# or: pip install -e .

# 3. Create .env
echo GEMINI_API_KEY=your_key_here > .env

# 4. Initialise the database and create an admin account
uv run python create_tables.py
uv run python create_admin.py

# 5. (Optional) Import sample questions
uv run python import_questions.py

# 6. Run the app
uv run python main.py
```

---

## Project Structure

```
mock_cbt/
├── main.py                        # Entry point — Qt app + AI Tutor thread
├── app/
│   ├── bridge/
│   │   ├── exam_bridge.py         # QWebChannel bridge (exam, auth, admin, AI)
│   │   └── question_import_bridge.py
│   ├── database/
│   │   ├── database.py
│   │   └── models.py              # SQLAlchemy models
│   ├── services/
│   │   ├── exam_service.py
│   │   ├── auth_service.py
│   │   ├── question_service.py
│   │   ├── reportlab_report_service.py
│   │   └── ocr_ingestion/
│   ├── ai_tutor/                  # FastAPI AI Tutor sidecar
│   │   ├── main.py
│   │   ├── router.py
│   │   └── services/
│   └── web/
│       ├── index.html             # Main SPA
│       ├── question_import.html
│       └── js/app.js
├── data/
│   ├── cbt.sqlite3
│   └── reports/
└── question_data/                 # JSON question bank files
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key for the AI Tutor |

---

## Creating an Admin

```bash
uv run python create_admin.py
```

Follow the prompts to set a username and password.

---

## Importing Questions

Place a JSON file in `question_data/` following this structure:

```json
[
  {
    "subject": "Mathematics",
    "year": 2002,
    "question_number": 1,
    "text": "Question text here",
    "options": [
      {"label": "A", "text": "Option A"},
      {"label": "B", "text": "Option B"},
      {"label": "C", "text": "Option C"},
      {"label": "D", "text": "Option D"}
    ],
    "correct_label": "B",
    "explanation": "Optional explanation"
  }
]
```

Then run:

```bash
uv run python import_questions.py
```
# LLS-CBT-Activator
