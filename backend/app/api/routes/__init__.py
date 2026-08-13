"""API router aggregation."""

from fastapi import APIRouter

from app.api.routes import chat, health, prediction, rag

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(chat.router)
api_router.include_router(prediction.router)
api_router.include_router(rag.router)
