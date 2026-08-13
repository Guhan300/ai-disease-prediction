"""In-memory chat session store (SQLite persistence layered in database module)."""

from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.schemas.chat import ChatMessage


class SessionStore:
    """Thread-safe session store used by the conversation service."""

    def __init__(self) -> None:
        self._sessions: Dict[str, dict] = {}
        self._lock = Lock()

    def create(self, welcome: ChatMessage) -> str:
        session_id = str(uuid4())
        with self._lock:
            self._sessions[session_id] = {
                "session_id": session_id,
                "stage": "greeting",
                "messages": [welcome],
                "assessment_complete": False,
                "extracted_features": {},
                "questions_asked": [],
                "prediction_ready": False,
                "prediction": None,
                "explanation": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        return session_id

    def get(self, session_id: str) -> Optional[dict]:
        with self._lock:
            session = self._sessions.get(session_id)
            return dict(session) if session else None

    def list_sessions(self) -> List[dict]:
        with self._lock:
            items = []
            for session in self._sessions.values():
                items.append(
                    {
                        "session_id": session["session_id"],
                        "created_at": session.get("created_at"),
                        "stage": session.get("stage"),
                        "assessment_complete": session.get("assessment_complete", False),
                    }
                )
            return sorted(items, key=lambda x: x.get("created_at") or "", reverse=True)

    def append_messages(
        self,
        session_id: str,
        messages: List[ChatMessage],
        *,
        stage: Optional[str] = None,
    ) -> Optional[dict]:
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return None
            session["messages"].extend(messages)
            if stage:
                session["stage"] = stage
            return dict(session)

    def update_state(self, session_id: str, **kwargs: Any) -> Optional[dict]:
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return None
            session.update(kwargs)
            return dict(session)


session_store = SessionStore()
