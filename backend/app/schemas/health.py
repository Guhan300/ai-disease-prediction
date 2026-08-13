"""Health check response schemas."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response returned by GET /api/health."""

    status: str = Field(description="Service health status")
    app_name: str = Field(description="Application name")
    version: str = Field(description="Application version")
    environment: str = Field(description="Runtime environment")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of the health check",
    )
    components: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional component status map (expanded in later phases)",
    )
    message: Optional[str] = Field(
        default=None,
        description="Human-readable status message",
    )
