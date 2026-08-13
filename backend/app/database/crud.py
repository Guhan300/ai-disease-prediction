"""CRUD helpers for assessment sessions."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.database.models import AssessmentSession


def upsert_session(
    db: Session,
    session_id: str,
    *,
    answers: Optional[Dict[str, Any]] = None,
    predictions: Optional[Dict[str, Any]] = None,
    model_version: str = "unknown",
    stage: str = "greeting",
) -> AssessmentSession:
    row = db.get(AssessmentSession, session_id)
    if row is None:
        row = AssessmentSession(id=session_id)
        db.add(row)
    if answers is not None:
        row.answers = json.dumps(answers)
    if predictions is not None:
        row.predictions = json.dumps(predictions)
    row.model_version = model_version
    row.stage = stage
    db.commit()
    db.refresh(row)
    return row


def get_session_row(db: Session, session_id: str) -> Optional[AssessmentSession]:
    return db.get(AssessmentSession, session_id)
