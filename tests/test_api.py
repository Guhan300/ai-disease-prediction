"""Core MedAI unit and API tests (LLM mocked)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.ml.feature_mapping import conversation_to_feature_frame
from app.ml.model_registry import model_registry
from app.services.question_engine import QuestionEngine
from app.services.safety_service import screen_safety
from app.services.symptom_extraction_service import extract_symptoms, merge_features

client = TestClient(app)


def test_health_ok():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_model_info_loaded():
    # Ensure registry loaded for tests
    if not model_registry.is_ready:
        model_registry.load()
    response = client.get("/api/model/info")
    assert response.status_code == 200
    payload = response.json()
    assert payload["loaded"] is True
    assert payload["classes"]


def test_rule_based_symptom_extraction():
    result = extract_symptoms("I have fever and severe body pain for 3 days.")
    assert result.symptoms.get("fever") is True
    assert result.symptoms.get("body_pain") is True
    assert result.duration_days == 3


def test_negated_symptom_extraction():
    result = extract_symptoms("I don't have any fever but I have a cough.")
    assert result.symptoms.get("fever") is False
    assert result.symptoms.get("cough") is True


def test_feature_mapping_uses_model_schema():
    if not model_registry.is_ready:
        model_registry.load()
    frame = conversation_to_feature_frame(
        {"fever": True, "cough": True},
        model_registry.feature_names,
    )
    assert int(frame.iloc[0]["fever"]) == 1
    assert int(frame.iloc[0]["cough"]) == 1
    assert frame.shape[1] == len(model_registry.feature_names)


def test_predict_endpoint_top3():
    if not model_registry.is_ready:
        model_registry.load()
    response = client.post(
        "/api/predict",
        json={"features": {"fever": True, "body_pain": True, "headache": True, "chills": True}},
    )
    assert response.status_code == 200
    preds = response.json()["top_predictions"]
    assert len(preds) == 3
    assert preds[0]["score"] >= preds[1]["score"]


def test_question_engine_followup():
    engine = QuestionEngine(min_known_features=3, max_questions=6)
    features = {"fever": True}
    nxt = engine.next_question(features, [])
    assert nxt
    question, feature = nxt
    assert "fever" in question.lower() or "days" in question.lower() or feature


def test_safety_red_flag():
    result = screen_safety("I can't breathe and feel like gasping")
    assert result["red_flag_detected"] is True


def test_chat_flow_reaches_prediction():
    if not model_registry.is_ready:
        model_registry.load()

    session = client.post("/api/chat/session").json()
    session_id = session["session_id"]

    turns = [
        "I have high fever, body pain, headache and chills for three days.",
        "Yes I also feel very fatigued and I have no sore throat.",
        "No breathing difficulty.",
        "No rash.",
        "No diarrhea.",
    ]

    final = None
    for message in turns:
        final = client.post(
            "/api/chat/message",
            json={"session_id": session_id, "message": message},
        ).json()
        if final.get("assessment_complete"):
            break

    assert final is not None
    assert final["assessment_complete"] is True
    assert final["type"] == "result"
    assert final["prediction"]["top_predictions"]
    assert "diagnosis" not in final["message"]["content"].lower() or "not" in final["message"]["content"].lower()


def test_merge_features():
    extraction = extract_symptoms("I have cough and nausea")
    merged = merge_features({"fever": True}, extraction)
    assert merged["fever"] is True
    assert merged.get("cough") is True
