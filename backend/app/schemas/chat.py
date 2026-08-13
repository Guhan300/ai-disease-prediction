"""Chat schemas for MedAI conversational API."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    role: Literal["assistant", "user", "system"] = "assistant"
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CreateSessionResponse(BaseModel):
    session_id: str
    type: Literal["question", "info"] = "question"
    message: ChatMessage
    assessment_complete: bool = False
    phase: str = "full"
    disclaimer: str


class ChatMessageRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=80)
    message: str = Field(min_length=1, max_length=4000)


class PredictionItem(BaseModel):
    condition: str
    score: float


class ImportantFeature(BaseModel):
    feature: str
    impact: str
    direction: Optional[str] = None


class SafetyInfo(BaseModel):
    red_flag_detected: bool = False
    message: Optional[str] = None
    reason: Optional[str] = None
    matched_rules: List[str] = Field(default_factory=list)


class SourceInfo(BaseModel):
    source: Optional[str] = None
    document: Optional[str] = None
    section: Optional[str] = None
    chunk_id: Optional[str] = None


class ChatMessageResponse(BaseModel):
    session_id: str
    type: Literal["question", "info", "result", "safety"] = "question"
    message: ChatMessage
    assessment_complete: bool = False
    prediction: Optional[Dict[str, Any]] = None
    explanation: Optional[Dict[str, Any]] = None
    safety: Optional[SafetyInfo] = None
    sources: List[SourceInfo] = Field(default_factory=list)
    extracted_features: Optional[Dict[str, Any]] = None
    disclaimer: Optional[str] = None
    note: Optional[str] = None


class SessionDetailResponse(BaseModel):
    session_id: str
    stage: str
    messages: List[ChatMessage]
    assessment_complete: bool = False
    extracted_features: Dict[str, Any] = Field(default_factory=dict)
    prediction: Optional[Dict[str, Any]] = None
