"""Health check API routes."""

from fastapi import APIRouter, Request

from app.core.config import get_settings
from app.core.logging import get_logger
from app.ml.model_registry import model_registry
from app.rag.retriever import retriever
from app.schemas.health import HealthResponse
from app.services.llm_service import llm_client

router = APIRouter(tags=["health"])
logger = get_logger("api.health")


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    settings = get_settings()
    request_id = getattr(request.state, "request_id", "n/a")
    logger.info("Health check | request_id=%s", request_id)

    llm_status = "ok" if llm_client.is_available() else "unavailable"
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        components={
            "api": "ok",
            "model": "ok" if model_registry.is_ready else "not_loaded",
            "rag": "ok" if retriever.loaded else "not_loaded",
            "llm": llm_status,
        },
        message=(
            "MedAI backend is running. Predictions require a trained local ML model; "
            "Ollama/RAG enhance conversation when available."
        ),
    )
