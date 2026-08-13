"""Chat API routes backed by ConversationService."""

from fastapi import APIRouter, HTTPException, Request

from app.core.logging import get_logger
from app.database.crud import upsert_session
from app.database.database import SessionLocal
from app.ml.model_registry import model_registry
from app.schemas.chat import (
    ChatMessage,
    ChatMessageRequest,
    ChatMessageResponse,
    CreateSessionResponse,
    SessionDetailResponse,
)
from app.services.conversation_service import DISCLAIMER, conversation_service

router = APIRouter(prefix="/chat", tags=["chat"])
logger = get_logger("api.chat")


@router.post("/session", response_model=CreateSessionResponse)
async def create_session(request: Request) -> CreateSessionResponse:
    request_id = getattr(request.state, "request_id", "n/a")
    payload = conversation_service.create_session()
    try:
        with SessionLocal() as db:
            upsert_session(
                db,
                payload["session_id"],
                answers={},
                predictions={},
                model_version=str(model_registry.metadata.get("model_version", "unknown")),
                stage="greeting",
            )
    except Exception as exc:
        logger.warning("DB persist skipped: %s", exc)

    logger.info("session created | request_id=%s | session_id=%s", request_id, payload["session_id"])
    return CreateSessionResponse(**payload)


@router.get("/session/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: str) -> SessionDetailResponse:
    session = conversation_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return SessionDetailResponse(
        session_id=session["session_id"],
        stage=session.get("stage", "unknown"),
        messages=session.get("messages") or [],
        assessment_complete=bool(session.get("assessment_complete")),
        extracted_features=session.get("extracted_features") or {},
        prediction=session.get("prediction"),
    )


@router.post("/message", response_model=ChatMessageResponse)
async def post_message(payload: ChatMessageRequest, request: Request) -> ChatMessageResponse:
    request_id = getattr(request.state, "request_id", "n/a")
    try:
        result = conversation_service.handle_message(payload.session_id, payload.message)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found.") from None
    except Exception:
        logger.exception("chat message failed | request_id=%s", request_id)
        raise HTTPException(
            status_code=500,
            detail="Unable to process chat message.",
        ) from None

    # Normalize message object
    message = result["message"]
    if isinstance(message, dict):
        message = ChatMessage(**message)

    try:
        with SessionLocal() as db:
            upsert_session(
                db,
                payload.session_id,
                answers=result.get("extracted_features") or {},
                predictions=result.get("prediction") or {},
                model_version=str(model_registry.metadata.get("model_version", "unknown")),
                stage="complete" if result.get("assessment_complete") else "questioning",
            )
    except Exception as exc:
        logger.warning("DB persist skipped: %s", exc)

    logger.info(
        "chat message | request_id=%s | session_id=%s | type=%s",
        request_id,
        payload.session_id,
        result.get("type"),
    )

    return ChatMessageResponse(
        session_id=result["session_id"],
        type=result.get("type", "question"),
        message=message,
        assessment_complete=bool(result.get("assessment_complete")),
        prediction=result.get("prediction"),
        explanation=result.get("explanation"),
        safety=result.get("safety"),
        sources=result.get("sources") or [],
        extracted_features=result.get("extracted_features"),
        disclaimer=result.get("disclaimer") or DISCLAIMER,
        note=result.get("note"),
    )
