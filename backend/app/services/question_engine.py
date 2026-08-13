"""Deterministic follow-up question engine."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

PRIORITY_QUESTIONS: List[Tuple[str, str]] = [
    ("fever", "Do you currently have a fever?"),
    ("cough", "Are you coughing?"),
    ("headache", "Do you have a headache?"),
    ("body_pain", "Are you experiencing body pain or muscle aches?"),
    ("fatigue", "Have you been feeling unusually fatigued or tired?"),
    ("sore_throat", "Do you have a sore throat?"),
    ("breathing_difficulty", "Do you have any difficulty breathing?"),
    ("chest_pain", "Are you having any chest pain?"),
    ("nausea", "Do you feel nauseous?"),
    ("vomiting", "Have you been vomiting?"),
    ("diarrhea", "Do you have diarrhea?"),
    ("abdominal_pain", "Do you have abdominal or stomach pain?"),
    ("rash", "Do you notice any rash on your skin?"),
    ("runny_nose", "Do you have a runny or stuffy nose?"),
    ("chills", "Are you experiencing chills?"),
    ("dizziness", "Do you feel dizzy?"),
    ("joint_pain", "Do you have joint pain?"),
    ("itching", "Are you experiencing itching?"),
    ("loss_of_appetite", "Have you lost your appetite?"),
    ("sweating", "Have you been sweating more than usual?"),
]

CONDITIONAL_FOLLOWUPS = {
    "fever": ("fever_duration_asked", "How many days have you had the fever?"),
    "cough": ("cough_detail_asked", "How long have you been coughing?"),
    "breathing_difficulty": (
        "breathing_severity_asked",
        "Is your breathing difficulty mild or severe?",
    ),
}

# Map question text / flags → feature or meta keys for yes/no answers
QUESTION_FEATURE_MAP: Dict[str, str] = {
    **{question: feature for feature, question in PRIORITY_QUESTIONS},
    "How many days have you had the fever?": "symptom_duration",
    "How long have you been coughing?": "symptom_duration",
    "Is your breathing difficulty mild or severe?": "breathing_severity",
}


class QuestionEngine:
    """Choose the next question from missing features / conditional rules."""

    def __init__(self, min_known_features: int = 3, max_questions: int = 6) -> None:
        self.min_known_features = min_known_features
        self.max_questions = max_questions

    def known_symptom_count(self, features: Dict[str, Any]) -> int:
        return sum(
            1
            for key, _ in PRIORITY_QUESTIONS
            if key in features and features[key] is not None
        )

    def is_ready_for_prediction(
        self,
        features: Dict[str, Any],
        questions_asked: List[str],
    ) -> bool:
        positives = sum(1 for key, _ in PRIORITY_QUESTIONS if features.get(key) is True)
        known = self.known_symptom_count(features)
        # Two clear positive symptoms is enough for an educational estimate
        if positives >= 2:
            return True
        # Enough answered questions (yes or no)
        if known >= self.min_known_features:
            return True
        # Hard cap so chat does not loop forever
        if len(questions_asked) >= self.max_questions and known >= 1:
            return True
        return False

    def feature_for_question(self, question: str) -> Optional[str]:
        if question in QUESTION_FEATURE_MAP:
            return QUESTION_FEATURE_MAP[question]
        # Fuzzy: rewritten questions may still contain feature words
        lowered = question.lower()
        for feature, canonical in PRIORITY_QUESTIONS:
            label = feature.replace("_", " ")
            if label in lowered or feature in lowered:
                return feature
        if "day" in lowered or "how long" in lowered:
            return "symptom_duration"
        if "mild or severe" in lowered or "severity" in lowered:
            return "breathing_severity"
        return None

    def next_question(
        self,
        features: Dict[str, Any],
        questions_asked: List[str],
    ) -> Optional[Tuple[str, Optional[str]]]:
        """
        Return (question_text, target_feature_or_none).
        """
        asked = set(questions_asked)

        for feature, (flag, question) in CONDITIONAL_FOLLOWUPS.items():
            if features.get(feature) is True and flag not in asked and question not in asked:
                # Return flag as tracking id so it cannot be asked twice
                return question, flag

        for feature, question in PRIORITY_QUESTIONS:
            if feature in features:
                continue
            if question in asked:
                continue
            return question, feature
        return None
