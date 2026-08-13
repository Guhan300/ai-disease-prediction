"""ORM models for assessment sessions (no unnecessary PII)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class AssessmentSession(Base):
    __tablename__ = "assessment_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    answers: Mapped[str] = mapped_column(Text, default="{}")
    predictions: Mapped[str] = mapped_column(Text, default="{}")
    model_version: Mapped[str] = mapped_column(String(64), default="unknown")
    stage: Mapped[str] = mapped_column(String(64), default="greeting")
