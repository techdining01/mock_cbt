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
    Create all database tables if they do not already exist.
    """

    # Import models here so SQLAlchemy knows about them before
    # create_all() is called.
    from app.database import models  # noqa: F401

    Base.metadata.create_all(
        bind=engine,
    )
