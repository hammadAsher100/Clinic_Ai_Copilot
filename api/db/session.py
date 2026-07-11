"""
Database session management.

Creates the SQLAlchemy engine and session factory from DATABASE_URL.
Supports both SQLite (dev) and PostgreSQL (production/Docker).
"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from api.core.config import settings


def _get_engine_args() -> dict:
    """Return engine kwargs appropriate for the database backend."""
    if settings.database_url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {"pool_pre_ping": True, "pool_size": 5}


engine = create_engine(settings.database_url, **_get_engine_args())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables defined in models.py.

    Uses simple create_all — no Alembic migration complexity given
    the hackathon time budget.
    """
    from api.db.models import Base  # noqa: F401 — import triggers table registration
    Base.metadata.create_all(bind=engine)
