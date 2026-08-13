"""Prediction and model info schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    features: Dict[str, Any] = Field(default_factory=dict)
    answers: Optional[Dict[str, Any]] = None


class PredictResponse(BaseModel):
    top_predictions: List[Dict[str, Any]]
    explanation: Dict[str, Any] = Field(default_factory=dict)
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    disclaimer: str = (
        "Model-estimated risk scores for educational use only — not a diagnosis."
    )


class ModelInfoResponse(BaseModel):
    loaded: bool
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    features: List[str] = Field(default_factory=list)
    classes: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    message: Optional[str] = None
