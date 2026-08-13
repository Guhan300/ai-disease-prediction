"""Map conversational symptom dicts onto the trained model feature schema."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping

import pandas as pd

# Canonical conversational symptoms → possible dataset column aliases
CANONICAL_ALIASES: Dict[str, List[str]] = {
    "fever": ["fever", "high_fever", "mild_fever"],
    "cough": ["cough"],
    "headache": ["headache"],
    "fatigue": ["fatigue", "lethargy", "malaise"],
    "body_pain": ["body_pain", "muscle_pain", "muscle_weakness"],
    "sore_throat": ["sore_throat", "throat_irritation", "patches_in_throat"],
    "breathing_difficulty": ["breathing_difficulty", "breathlessness"],
    "nausea": ["nausea"],
    "vomiting": ["vomiting"],
    "diarrhea": ["diarrhea", "diarrhoea"],
    "abdominal_pain": ["abdominal_pain", "stomach_pain", "belly_pain"],
    "chest_pain": ["chest_pain"],
    "rash": ["rash", "skin_rash", "red_spots_over_body"],
    "dizziness": ["dizziness", "vertigo", "spinning_movements"],
    "joint_pain": ["joint_pain", "knee_pain", "hip_joint_pain", "swelling_joints"],
    "runny_nose": ["runny_nose", "continuous_sneezing", "congestion", "sinus_pressure"],
    "chills": ["chills", "shivering"],
    "loss_of_appetite": ["loss_of_appetite"],
    "sweating": ["sweating"],
    "itching": ["itching", "internal_itching"],
}


def canonical_symptom_names() -> List[str]:
    return list(CANONICAL_ALIASES.keys())


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "present", "severe"}
    return False


def conversation_to_feature_frame(
    extracted: Mapping[str, Any],
    model_features: Iterable[str],
) -> pd.DataFrame:
    """
    Convert extracted conversational symptoms into a single-row DataFrame
    matching the trained model feature columns.
    """
    features = list(model_features)
    row = {name: 0 for name in features}

    # Direct keys that already match dataset columns
    for key, value in extracted.items():
        if key in row and _truthy(value):
            row[key] = 1

    # Canonical mapping
    for canonical, aliases in CANONICAL_ALIASES.items():
        present = _truthy(extracted.get(canonical))
        if not present:
            # also accept nested symptoms dict
            symptoms = extracted.get("symptoms")
            if isinstance(symptoms, Mapping):
                present = _truthy(symptoms.get(canonical))
        if not present:
            continue
        for alias in aliases:
            if alias in row:
                row[alias] = 1

    return pd.DataFrame([row], columns=features)


def humanize_feature(name: str) -> str:
    """Convert snake_case feature names into readable labels."""
    return name.replace("_", " ").strip().capitalize()
