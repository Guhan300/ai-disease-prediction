"""RAG search and knowledge source routes."""

from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.rag.retriever import retriever

router = APIRouter(tags=["rag"])


class RagSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=4, ge=1, le=10)


class RagSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    available: bool


@router.post("/rag/search", response_model=RagSearchResponse)
async def rag_search(payload: RagSearchRequest) -> RagSearchResponse:
    results = retriever.search(payload.query, top_k=payload.top_k)
    return RagSearchResponse(results=results, available=retriever.loaded)


@router.get("/knowledge/sources")
async def knowledge_sources() -> Dict[str, Any]:
    return {
        "available": retriever.loaded,
        "sources": retriever.list_sources(),
        "error": retriever.error,
    }
