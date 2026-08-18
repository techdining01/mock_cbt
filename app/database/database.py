from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# ============================================================
# DATABASE LOCATION
# ============================================================

# Project root:
#
# app/
# main.py
#
# We keep the database inside a data directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

DATABASE_PATH = DATA_DIR / "cbt.sqlite3"


# ============================================================
# DATABASE URL
# ============================================================

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


# ============================================================
# SQLALCHEMY ENGINE
# ============================================================

engine = create_engine(
    DATABASE_URL,
    # SQLite desktop application.
    connect_args={
        "check_same_thread": False,
    },
    # Useful during development.
    echo=False,
)


# ============================================================
# SQLITE FOREIGN KEY SUPPORT
# ============================================================


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    """
    SQLite does not enable foreign-key enforcement by default.

    This turns it on for every connection.
    """

    cursor = dbapi_connection.cursor()

    cursor.execute("PRAGMA foreign_keys=ON")

    cursor.close()


# ============================================================
# BASE MODEL
# ============================================================


class Base(DeclarativeBase):
    """
    Base class inherited by every SQLAlchemy model.
    """

    pass


# ============================================================
# SESSION FACTORY
# ============================================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================


def init_database() -> None:
    """
    Create all database tables if they do not already exist,
    run safe lightweight column migrations for SQLite,
    and ensure default admin exists.
    """

    # Import models here so SQLAlchemy knows about them before create_all()
    from app.database import models  # noqa: F401
    from app.database.models import User
    from sqlalchemy import text

    Base.metadata.create_all(
        bind=engine,
    )

    # Lightweight SQLite schema migration
    try:
        with engine.connect() as conn:
            # Check exam_sessions columns
            res = conn.execute(text("PRAGMA table_info(exam_sessions)")).fetchall()
            col_names = [row[1] for row in res]
            if "user_id" not in col_names:
                conn.execute(text("ALTER TABLE exam_sessions ADD COLUMN user_id INTEGER REFERENCES users(id)"))
                conn.commit()

            # Check questions columns
            res_q = conn.execute(text("PRAGMA table_info(questions)")).fetchall()
            q_cols = [row[1] for row in res_q]
            if "image_path" not in q_cols:
                conn.execute(text("ALTER TABLE questions ADD COLUMN image_path VARCHAR(500)"))
                conn.commit()
            if "source_reference" not in q_cols:
                conn.execute(text("ALTER TABLE questions ADD COLUMN source_reference VARCHAR(255)"))
                conn.commit()
            if "source_page" not in q_cols:
                conn.execute(text("ALTER TABLE questions ADD COLUMN source_page INTEGER"))
                conn.commit()
            if "explanation" not in q_cols:
                conn.execute(text("ALTER TABLE questions ADD COLUMN explanation TEXT"))
                conn.commit()

            # Check users columns
            res_u = conn.execute(text("PRAGMA table_info(users)")).fetchall()
            u_cols = [row[1] for row in res_u]
            if "student_class" not in u_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN student_class VARCHAR(50)"))
                conn.commit()
            if "admission_year" not in u_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN admission_year INTEGER"))
                conn.commit()
    except Exception as mig_err:
        print("Schema migration check:", mig_err)

    try:
        with SessionLocal() as db:
            admin_user = db.query(User).filter(User.role == "admin").first()
            if not admin_user:
                default_admin = User(
                    username="admin",
                    password="adminpassword123",
                    full_name="System Administrator",
                    role="admin",
                    is_active=True,
                )
                db.add(default_admin)
                db.commit()
                print("Default admin created: username=admin, password=adminpassword123")
    except Exception as exc:
        print("Admin seed check:", exc)
