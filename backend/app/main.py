"""FastAPI application entrypoint for MedAI."""

import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.database.database import init_db
from app.ml.model_registry import model_registry
from app.rag.retriever import retriever

setup_logging()
logger = get_logger("main")
settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    logger.info(
        "Starting %s v%s [%s]",
        settings.app_name,
        settings.app_version,
        settings.environment,
    )
    try:
        init_db()
    except Exception:
        logger.exception("Database init failed")
    model_registry.load()
    retriever.load()
    yield
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "MedAI — conversational educational disease-risk assistant. "
        "A trained local ML model produces risk estimates; the local LLM "
        "handles conversation only. Not a medical diagnosis."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.exception(
            "Unhandled error | request_id=%s | path=%s | elapsed_ms=%.2f",
            request_id,
            request.url.path,
            elapsed_ms,
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected server error occurred.",
                "request_id": request_id,
            },
            headers={"X-Request-ID": request_id},
        )

    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "Request completed | request_id=%s | method=%s | path=%s | "
        "status=%s | elapsed_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/")
async def root() -> dict:
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": f"{settings.api_prefix}/health",
        "model_loaded": model_registry.is_ready,
        "disclaimer": (
            "This system provides informational risk estimates and is not "
            "a medical diagnosis."
        ),
    }
