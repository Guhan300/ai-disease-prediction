"""Natural-language symptom extraction with LLM + rule-based fallback."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.ml.feature_mapping import canonical_symptom_names
from app.services.llm_service import LocalLLM, extract_json_object, llm_client


class SymptomExtraction(BaseModel):
    """Validated structured extraction payload."""

    symptoms: Dict[str, bool] = Field(default_factory=dict)
    duration_days: Optional[float] = None
    severity: Optional[str] = None
    confidence: Dict[str, float] = Field(default_factory=dict)
    notes: Optional[str] = None


NEGATION = re.compile(
    r"\b(no|not|don't|dont|never|without|denied)\b.{0,20}\b({symptom})\b|"
    r"\b({symptom})\b.{0,12}\b(no|not)\b",
    re.IGNORECASE,
)

KEYWORD_MAP = {
    "fever": [r"\bfever\b", r"\bhigh temperature\b", r"\bpyrexia\b"],
    "cough": [r"\bcough(?:ing)?\b"],
    "headache": [r"\bheadache\b", r"\bhead pain\b", r"\bmigraine\b"],
    "fatigue": [r"\bfatigue\b", r"\btired\b", r"\bexhausted\b", r"\bweak\b"],
    "body_pain": [r"\bbody pain\b", r"\bbody ache\b", r"\bmuscle pain\b", r"\baches?\b"],
    "sore_throat": [r"\bsore throat\b", r"\bthroat pain\b"],
    "breathing_difficulty": [
        r"\bshortness of breath\b",
        r"\bdifficulty breathing\b",
        r"\bcan't breathe\b",
        r"\bbreathless\b",
        r"\bdyspnea\b",
    ],
    "nausea": [r"\bnausea\b", r"\bnauseous\b", r"\bqueasy\b"],
    "vomiting": [r"\bvomit(?:ing)?\b", r"\bthrowing up\b"],
    "diarrhea": [r"\bdiarrhea\b", r"\bdiarrhoea\b", r"\bloose stool\b"],
    "abdominal_pain": [r"\bstomach pain\b", r"\babdominal pain\b", r"\bbelly pain\b"],
    "chest_pain": [r"\bchest pain\b"],
    "rash": [r"\brash\b", r"\bskin spots\b"],
    "dizziness": [r"\bdizzy\b", r"\bdizziness\b", r"\bvertigo\b", r"\blightheaded\b"],
    "joint_pain": [r"\bjoint pain\b", r"\bknee pain\b", r"\barthritis pain\b"],
    "runny_nose": [r"\brunny nose\b", r"\bstuffy nose\b", r"\bsneezing\b", r"\bcongested\b"],
    "chills": [r"\bchills\b", r"\bshivering\b"],
    "loss_of_appetite": [r"\bloss of appetite\b", r"\bno appetite\b", r"\bnot eating\b"],
    "sweating": [r"\bsweating\b", r"\bnight sweats\b"],
    "itching": [r"\bitch(?:ing)?\b"],
}


def _rule_based_extract(text: str) -> SymptomExtraction:
    lowered = text.lower()
    symptoms: Dict[str, bool] = {}
    confidence: Dict[str, float] = {}

    for name, patterns in KEYWORD_MAP.items():
        hit = any(re.search(p, lowered) for p in patterns)
        if not hit:
            continue
        negated = False
        for p in patterns:
            # simple negation window
            for match in re.finditer(p, lowered):
                start = max(0, match.start() - 25)
                window = lowered[start:match.end() + 5]
                if re.search(r"\b(no|not|don't|dont|never|without)\b", window):
                    negated = True
                    break
            if negated:
                break
        symptoms[name] = not negated
        confidence[name] = 0.7 if not negated else 0.75

    duration = None
    duration_match = re.search(
        r"(\d+)\s*(day|days|week|weeks)",
        lowered,
    )
    if duration_match:
        value = float(duration_match.group(1))
        unit = duration_match.group(2)
        duration = value * (7 if "week" in unit else 1)

    severity = None
    if re.search(r"\b(severe|worst|unbearable)\b", lowered):
        severity = "severe"
    elif re.search(r"\b(mild|slight|little)\b", lowered):
        severity = "mild"
    elif re.search(r"\b(moderate|quite)\b", lowered):
        severity = "moderate"

    return SymptomExtraction(
        symptoms=symptoms,
        duration_days=duration,
        severity=severity,
        confidence=confidence,
        notes="rule_based",
    )


def _llm_extract(text: str, llm: LocalLLM) -> Optional[SymptomExtraction]:
    symptom_list = ", ".join(canonical_symptom_names())
    system = (
        "You extract medical symptoms for an educational ML pipeline. "
        "Return STRICT JSON only. Do not diagnose. Do not invent unstated symptoms."
    )
    prompt = f"""
Extract symptoms from the user message into JSON with this schema:
{{
  "symptoms": {{"<symptom>": true/false}},
  "duration_days": number or null,
  "severity": "mild"|"moderate"|"severe"|null,
  "confidence": {{"<symptom>": 0.0-1.0}}
}}

Allowed symptom keys: {symptom_list}
Only include keys you can support from the text.
User message: {text}
"""
    raw = llm.generate(prompt, system=system, format_json=True, temperature=0.0)
    data = extract_json_object(raw or "")
    if not data:
        return None
    try:
        symptoms = data.get("symptoms") or {}
        cleaned = {
            k: bool(v)
            for k, v in symptoms.items()
            if k in canonical_symptom_names()
        }
        return SymptomExtraction(
            symptoms=cleaned,
            duration_days=data.get("duration_days"),
            severity=data.get("severity"),
            confidence=data.get("confidence") or {},
            notes="llm",
        )
    except Exception:
        return None


def extract_symptoms(
    text: str,
    llm: Optional[LocalLLM] = None,
) -> SymptomExtraction:
    """
    Extract structured symptoms.

    Prefer fast local rules first so chat stays responsive.
    Use Ollama only when rules find nothing and the message is not a short yes/no.
    """
    rule_result = _rule_based_extract(text)
    if rule_result.symptoms or rule_result.duration_days is not None:
        return rule_result

    stripped = text.strip()
    if len(stripped) <= 12 and re.match(
        r"^(y|yes|yeah|yep|yup|n|no|nope|nah|true|false)\.?$",
        stripped,
        flags=re.I,
    ):
        return rule_result

    client = llm or llm_client
    if client.is_available():
        result = _llm_extract(text, client)
        if result is not None and result.symptoms:
            return result
    return rule_result


def merge_features(
    existing: Dict[str, Any],
    extraction: SymptomExtraction,
) -> Dict[str, Any]:
    """Merge new extraction into cumulative feature state."""
    merged = dict(existing)
    for key, value in extraction.symptoms.items():
        merged[key] = bool(value)
    if extraction.duration_days is not None:
        merged["symptom_duration"] = extraction.duration_days
    if extraction.severity:
        merged["severity"] = extraction.severity
    return merged
