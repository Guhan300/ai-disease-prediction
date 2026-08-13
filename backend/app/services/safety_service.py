"""Configurable red-flag safety screening."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping

from app.core.logging import get_logger

logger = get_logger("services.safety")

DEFAULT_RULES = [
    {
        "id": "severe_breathing",
        "keywords": [
            "can't breathe",
            "cannot breathe",
            "severe breathing",
            "gasping",
            "blue lips",
        ],
        "features": ["breathing_difficulty"],
        "require_severe": True,
        "message": (
            "Severe breathing difficulty can be urgent. "
            "Seek emergency medical care immediately if breathing is severely impaired."
        ),
    },
    {
        "id": "severe_chest_pain",
        "keywords": [
            "crushing chest pain",
            "severe chest pain",
            "chest pain radiating",
            "heart attack",
        ],
        "features": ["chest_pain"],
        "require_severe": True,
        "message": (
            "Severe chest pain may require prompt medical attention. "
            "If pain is severe, sudden, or accompanied by shortness of breath, seek emergency care."
        ),
    },
    {
        "id": "loss_of_consciousness",
        "keywords": [
            "passed out",
            "unconscious",
            "lost consciousness",
            "fainted and did not wake",
        ],
        "features": [],
        "require_severe": False,
        "message": (
            "Loss of consciousness can be serious. Seek urgent medical evaluation."
        ),
    },
    {
        "id": "severe_confusion",
        "keywords": [
            "severe confusion",
            "can't stay awake",
            "disoriented suddenly",
            "altered mental status",
        ],
        "features": [],
        "require_severe": False,
        "message": (
            "Sudden severe confusion may require urgent medical assessment."
        ),
    },
    {
        "id": "severe_allergic",
        "keywords": [
            "throat swelling",
            "tongue swelling",
            "anaphylaxis",
            "severe allergic reaction",
        ],
        "features": [],
        "require_severe": False,
        "message": (
            "Signs of a severe allergic reaction can be life-threatening. "
            "Seek emergency care immediately."
        ),
    },
]


def _rules_path() -> Path:
    return Path(__file__).resolve().parents[2] / "config" / "safety_rules.json"


def load_rules() -> List[Dict[str, Any]]:
    path = _rules_path()
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("Failed to load safety rules file: %s", exc)
    return DEFAULT_RULES


def screen_safety(
    message: str,
    extracted_features: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Run configurable red-flag checks.

    This is not an exhaustive emergency detector.
    """
    text = (message or "").lower()
    features = extracted_features or {}
    severity = str(features.get("severity") or features.get("symptom_severity") or "").lower()
    rules = load_rules()
    hits: List[Dict[str, Any]] = []

    for rule in rules:
        matched = False
        for kw in rule.get("keywords") or []:
            if kw.lower() in text:
                matched = True
                break
        if not matched:
            for feat in rule.get("features") or []:
                if features.get(feat) in (True, 1, "yes", "true"):
                    if rule.get("require_severe"):
                        if "severe" in severity or "severe" in text or features.get("breathing_difficulty") in (True, 1):
                            # For breathing_difficulty alone, warn only if message implies severity
                            if feat == "breathing_difficulty" and (
                                "severe" in text
                                or "can't" in text
                                or "cannot" in text
                                or features.get("severity") == "severe"
                            ):
                                matched = True
                            elif feat == "chest_pain" and ("severe" in text or features.get("severity") == "severe"):
                                matched = True
                        else:
                            matched = False
                    else:
                        matched = True
        if matched:
            hits.append(rule)

    if not hits:
        return {
            "red_flag_detected": False,
            "message": None,
            "matched_rules": [],
        }

    messages = [h["message"] for h in hits]
    return {
        "red_flag_detected": True,
        "message": " ".join(messages),
        "reason": "Potentially urgent symptom reported",
        "matched_rules": [h["id"] for h in hits],
    }
