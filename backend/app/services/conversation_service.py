"""End-to-end conversational assessment orchestration."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.core.logging import get_logger
from app.ml.feature_mapping import humanize_feature
from app.ml.model_registry import model_registry
from app.rag.retriever import retriever
from app.services.llm_service import LocalLLM, llm_client
from app.services.prediction_service import prediction_service
from app.services.question_engine import QuestionEngine
from app.services.safety_service import screen_safety
from app.services.session_store import session_store
from app.services.symptom_extraction_service import (
    extract_symptoms,
    merge_features,
)

logger = get_logger("services.conversation")

DISCLAIMER = (
    "This application provides educational, model-based health information "
    "and is not a substitute for professional medical diagnosis or treatment."
)

WELCOME = (
    "Hi! I'm MedAI. Tell me what symptoms you're experiencing in your own words.\n\n"
    "I'll ask a few follow-up questions, then a trained machine-learning model "
    "will estimate possible conditions. This is not a medical diagnosis."
)

YES_RE = re.compile(r"^\s*(y|yes|yeah|yep|yup|true|correct|i do|i have|present)\b", re.I)
NO_RE = re.compile(r"^\s*(n|no|nope|nah|false|not really|i don't|i do not|none)\b", re.I)


class ConversationService:
    def __init__(
        self,
        llm: Optional[LocalLLM] = None,
        question_engine: Optional[QuestionEngine] = None,
    ) -> None:
        self.llm = llm or llm_client
        self.questions = question_engine or QuestionEngine()

    def create_session(self) -> Dict[str, Any]:
        from app.schemas.chat import ChatMessage

        welcome = ChatMessage(role="assistant", content=WELCOME)
        session_id = session_store.create(welcome)
        session_store.update_state(
            session_id,
            stage="questioning",
            extracted_features={},
            questions_asked=[],
            pending_feature=None,
            prediction_ready=False,
        )
        return {
            "session_id": session_id,
            "type": "question",
            "message": welcome,
            "assessment_complete": False,
            "disclaimer": DISCLAIMER,
        }

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return session_store.get(session_id)

    def _apply_pending_answer(
        self,
        features: Dict[str, Any],
        pending_feature: Optional[str],
        message: str,
    ) -> Dict[str, Any]:
        """Map short yes/no (or duration) answers onto the last asked feature."""
        if not pending_feature:
            return features
        updated = dict(features)
        text = message.strip()

        # Conditional follow-up flags
        if pending_feature in {
            "fever_duration_asked",
            "cough_detail_asked",
            "symptom_duration",
        }:
            match = re.search(r"(\d+)\s*(day|days|week|weeks)?", text.lower())
            if match:
                value = float(match.group(1))
                unit = match.group(2) or "days"
                updated["symptom_duration"] = value * (7 if "week" in unit else 1)
            return updated

        if pending_feature in {"breathing_severity_asked", "breathing_severity"}:
            lowered = text.lower()
            if "severe" in lowered:
                updated["severity"] = "severe"
                updated["breathing_difficulty"] = True
            elif "mild" in lowered:
                updated["severity"] = "mild"
                updated["breathing_difficulty"] = True
            elif YES_RE.search(text):
                updated["breathing_difficulty"] = True
            elif NO_RE.search(text):
                updated["breathing_difficulty"] = False
            return updated

        if YES_RE.search(text):
            updated[pending_feature] = True
        elif NO_RE.search(text):
            updated[pending_feature] = False
        return updated

    def handle_message(self, session_id: str, message: str) -> Dict[str, Any]:
        from app.schemas.chat import ChatMessage

        session = session_store.get(session_id)
        if not session:
            raise KeyError("Session not found.")

        user_msg = ChatMessage(role="user", content=message.strip())
        pending_feature = session.get("pending_feature")
        extraction = extract_symptoms(message, llm=self.llm)
        features = merge_features(session.get("extracted_features") or {}, extraction)
        features = self._apply_pending_answer(features, pending_feature, message)
        questions_asked: List[str] = list(session.get("questions_asked") or [])

        safety = screen_safety(message, features)

        session_store.append_messages(session_id, [user_msg])
        session_store.update_state(
            session_id,
            extracted_features=features,
            pending_feature=None,
            stage="questioning",
        )

        if safety.get("red_flag_detected"):
            if (
                self.questions.is_ready_for_prediction(features, questions_asked)
                and model_registry.is_ready
            ):
                result = self._build_result(
                    session_id, features, safety, prioritize_safety=True
                )
                assistant = ChatMessage(
                    role="assistant", content=result["message"]["content"]
                )
                session_store.append_messages(session_id, [assistant], stage="complete")
                session_store.update_state(
                    session_id,
                    assessment_complete=True,
                    prediction=result.get("prediction"),
                    prediction_ready=True,
                    pending_feature=None,
                )
                return result

            content = (
                f"I'm concerned about something you mentioned.\n\n"
                f"{safety['message']}\n\n"
                "I can still share an educational model-based estimate if you want to "
                "continue, but please prioritize appropriate medical care.\n\n"
                f"{DISCLAIMER}"
            )
            assistant = ChatMessage(role="assistant", content=content)
            session_store.append_messages(session_id, [assistant], stage="safety")
            return {
                "session_id": session_id,
                "type": "safety",
                "message": assistant,
                "assessment_complete": False,
                "safety": safety,
                "disclaimer": DISCLAIMER,
            }

        if self.questions.is_ready_for_prediction(features, questions_asked):
            if not model_registry.is_ready:
                assistant = ChatMessage(
                    role="assistant",
                    content=(
                        "I have enough symptom details, but the ML model is not loaded yet. "
                        "Please run `python scripts/train_model.py` and restart the backend.\n\n"
                        f"{DISCLAIMER}"
                    ),
                )
                session_store.append_messages(session_id, [assistant])
                return {
                    "session_id": session_id,
                    "type": "info",
                    "message": assistant,
                    "assessment_complete": False,
                    "disclaimer": DISCLAIMER,
                }

            result = self._build_result(session_id, features, safety)
            assistant = ChatMessage(
                role="assistant", content=result["message"]["content"]
            )
            session_store.append_messages(session_id, [assistant], stage="complete")
            session_store.update_state(
                session_id,
                assessment_complete=True,
                prediction=result.get("prediction"),
                explanation=result.get("explanation"),
                prediction_ready=True,
                extracted_features=features,
                pending_feature=None,
            )
            return result

        nxt = self.questions.next_question(features, questions_asked)
        if not nxt:
            if model_registry.is_ready:
                result = self._build_result(session_id, features, safety)
                assistant = ChatMessage(
                    role="assistant", content=result["message"]["content"]
                )
                session_store.append_messages(session_id, [assistant], stage="complete")
                session_store.update_state(
                    session_id,
                    assessment_complete=True,
                    prediction=result.get("prediction"),
                    prediction_ready=True,
                    pending_feature=None,
                )
                return result
            next_q, target_feature = (
                "Could you share any other symptoms you're noticing?",
                None,
            )
        else:
            next_q, target_feature = nxt

        questions_asked.append(next_q)
        # Also store tracking flag/feature so conditional questions are not repeated
        if target_feature and target_feature not in questions_asked:
            questions_asked.append(target_feature)
        assistant = ChatMessage(role="assistant", content=next_q)
        session_store.append_messages(session_id, [assistant], stage="questioning")
        session_store.update_state(
            session_id,
            questions_asked=questions_asked,
            extracted_features=features,
            pending_feature=target_feature,
        )
        return {
            "session_id": session_id,
            "type": "question",
            "message": assistant,
            "assessment_complete": False,
            "extracted_features": features,
            "safety": safety,
            "disclaimer": DISCLAIMER,
        }

    def _build_result(
        self,
        session_id: str,
        features: Dict[str, Any],
        safety: Dict[str, Any],
        prioritize_safety: bool = False,
    ) -> Dict[str, Any]:
        prediction = prediction_service.predict(features)
        top = prediction["top_predictions"]
        explanation = prediction.get("explanation") or {}
        important = explanation.get("important_features") or []

        query_bits = [k for k, v in features.items() if v is True]
        rag_hits = retriever.search(
            " ".join(query_bits + [t["condition"] for t in top[:2]]),
            top_k=3,
        )
        sources = []
        context_blobs = []
        for hit in rag_hits:
            sources.append(
                {
                    "source": hit.get("source"),
                    "document": hit.get("document"),
                    "section": hit.get("section"),
                    "chunk_id": hit.get("chunk_id"),
                }
            )
            context_blobs.append(hit.get("text") or "")

        narrative = self._compose_explanation(
            features=features,
            top=top,
            important=important,
            context="\n\n".join(context_blobs),
            safety=safety,
            prioritize_safety=prioritize_safety,
        )

        return {
            "session_id": session_id,
            "type": "result",
            "message": {"role": "assistant", "content": narrative, "id": str(uuid4())},
            "prediction": {"top_predictions": top},
            "explanation": {"important_features": important},
            "safety": safety,
            "sources": sources,
            "extracted_features": features,
            "assessment_complete": True,
            "disclaimer": DISCLAIMER,
        }

    def _compose_explanation(
        self,
        features: Dict[str, Any],
        top: List[Dict[str, Any]],
        important: List[Dict[str, Any]],
        context: str,
        safety: Dict[str, Any],
        prioritize_safety: bool,
    ) -> str:
        lines = []
        if prioritize_safety and safety.get("red_flag_detected"):
            lines.append(safety.get("message") or "Please seek prompt medical attention.")
            lines.append("")

        if top:
            best = top[0]
            lines.append(
                f"Based on the symptoms you shared, the ML model estimated "
                f"**{best['condition']}** as the highest-scoring possible condition "
                f"(model score: {best['score'] * 100:.0f}%)."
            )
            if len(top) > 1:
                others = ", ".join(
                    f"{item['condition']} ({item['score'] * 100:.0f}%)" for item in top[1:]
                )
                lines.append(f"Other model-ranked possibilities: {others}.")

        if important:
            feats = ", ".join(item["feature"] for item in important[:5])
            lines.append(f"Features that most influenced this model result: {feats}.")

        active = [humanize_feature(k) for k, v in features.items() if v is True]
        if active:
            lines.append(f"Symptoms considered: {', '.join(active)}.")

        if context:
            lines.append("")
            lines.append(
                "Educational reference notes from the local knowledge base were used "
                "to phrase this explanation. They are not a diagnosis."
            )

        lines.append("")
        lines.append(
            "This is not a confirmed medical diagnosis. Several conditions can cause "
            "similar symptoms. Please consult a qualified healthcare professional."
        )
        lines.append(DISCLAIMER)
        fallback = "\n".join(lines)

        # Prefer deterministic template so chat stays fast.
        # Ollama can optionally polish later; never block prediction on LLM latency.
        return fallback


conversation_service = ConversationService()
