"""SQLAlchemy database setup (SQLite now, PostgreSQL-ready URL)."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


def _make_engine():
    settings = get_settings()
    url = settings.database_url
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, future=True, connect_args=connect_args)


engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    from app.database import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
