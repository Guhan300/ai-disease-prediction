"""Direct prediction and model info routes."""

from fastapi import APIRouter, HTTPException

from app.ml.model_registry import model_registry
from app.schemas.prediction import ModelInfoResponse, PredictRequest, PredictResponse
from app.services.prediction_service import prediction_service

router = APIRouter(tags=["prediction"])


@router.post("/predict", response_model=PredictResponse)
async def predict(payload: PredictRequest) -> PredictResponse:
    features = payload.features or payload.answers or {}
    if not features:
        raise HTTPException(status_code=400, detail="No features provided.")
    if not model_registry.is_ready:
        raise HTTPException(
            status_code=503,
            detail=model_registry.load_error
            or "ML model has not been trained yet. Please run the training script.",
        )
    try:
        result = prediction_service.predict(features)
    except Exception:
        raise HTTPException(status_code=500, detail="Prediction failed.") from None

    return PredictResponse(
        top_predictions=result["top_predictions"],
        explanation=result.get("explanation") or {},
        model_name=result.get("model_name"),
        model_version=result.get("model_version"),
    )


@router.get("/model/info", response_model=ModelInfoResponse)
async def model_info() -> ModelInfoResponse:
    if not model_registry.is_ready:
        return ModelInfoResponse(
            loaded=False,
            message=model_registry.load_error
            or "ML model has not been trained yet. Please run the training script.",
        )
    metrics = model_registry.metadata.get("metrics") or {}
    return ModelInfoResponse(
        loaded=True,
        model_name=model_registry.metadata.get("model_name"),
        model_version=model_registry.metadata.get("model_version"),
        features=model_registry.feature_names,
        classes=model_registry.class_names,
        metrics={
            "test": metrics.get("test"),
            "primary_metric": model_registry.metadata.get("primary_metric"),
        },
        message="Model loaded.",
    )
