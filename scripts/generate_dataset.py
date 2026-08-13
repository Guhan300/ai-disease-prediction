"""Generate an educational symptom/disease dataset (Kaggle-style schema).

Replace this CSV with a real Kaggle export at DATASET_PATH if preferred.
This synthetic dataset is for local demos when Kaggle credentials are unavailable.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SYMPTOMS = [
    "fever",
    "cough",
    "headache",
    "fatigue",
    "body_pain",
    "sore_throat",
    "breathing_difficulty",
    "nausea",
    "vomiting",
    "diarrhea",
    "abdominal_pain",
    "chest_pain",
    "rash",
    "dizziness",
    "joint_pain",
    "runny_nose",
    "chills",
    "loss_of_appetite",
    "sweating",
    "itching",
]

# Approximate symptom probabilities per disease (educational patterns only).
DISEASE_PROFILES = {
    "Common Cold": {
        "runny_nose": 0.9,
        "cough": 0.75,
        "sore_throat": 0.7,
        "headache": 0.45,
        "fatigue": 0.5,
        "fever": 0.25,
    },
    "Influenza": {
        "fever": 0.9,
        "body_pain": 0.85,
        "fatigue": 0.85,
        "headache": 0.7,
        "cough": 0.65,
        "chills": 0.7,
        "sore_throat": 0.4,
        "loss_of_appetite": 0.45,
    },
    "Malaria": {
        "fever": 0.95,
        "chills": 0.9,
        "sweating": 0.85,
        "headache": 0.7,
        "nausea": 0.55,
        "fatigue": 0.7,
        "vomiting": 0.4,
        "body_pain": 0.5,
    },
    "Typhoid": {
        "fever": 0.9,
        "abdominal_pain": 0.75,
        "fatigue": 0.8,
        "headache": 0.65,
        "loss_of_appetite": 0.7,
        "diarrhea": 0.45,
        "nausea": 0.5,
        "chills": 0.4,
    },
    "Pneumonia": {
        "fever": 0.85,
        "cough": 0.9,
        "breathing_difficulty": 0.8,
        "chest_pain": 0.7,
        "fatigue": 0.7,
        "chills": 0.55,
        "sweating": 0.4,
    },
    "Migraine": {
        "headache": 0.98,
        "nausea": 0.7,
        "dizziness": 0.55,
        "vomiting": 0.35,
        "fatigue": 0.4,
    },
    "Gastroenteritis": {
        "diarrhea": 0.9,
        "vomiting": 0.8,
        "nausea": 0.85,
        "abdominal_pain": 0.8,
        "fever": 0.35,
        "loss_of_appetite": 0.6,
        "fatigue": 0.5,
    },
    "Allergy": {
        "itching": 0.85,
        "rash": 0.75,
        "runny_nose": 0.6,
        "cough": 0.35,
        "dizziness": 0.2,
        "sore_throat": 0.15,
    },
    "Dengue": {
        "fever": 0.95,
        "body_pain": 0.9,
        "joint_pain": 0.8,
        "headache": 0.75,
        "rash": 0.55,
        "nausea": 0.5,
        "fatigue": 0.7,
        "loss_of_appetite": 0.55,
    },
    "Urinary tract infection": {
        "abdominal_pain": 0.7,
        "fever": 0.4,
        "nausea": 0.35,
        "fatigue": 0.4,
        "chills": 0.3,
    },
    "Bronchial Asthma": {
        "breathing_difficulty": 0.95,
        "cough": 0.85,
        "chest_pain": 0.45,
        "fatigue": 0.4,
    },
    "Hypertension": {
        "headache": 0.7,
        "dizziness": 0.65,
        "chest_pain": 0.35,
        "fatigue": 0.4,
    },
    "Chicken pox": {
        "rash": 0.95,
        "itching": 0.9,
        "fever": 0.75,
        "fatigue": 0.55,
        "headache": 0.45,
        "loss_of_appetite": 0.4,
    },
    "Jaundice": {
        "fatigue": 0.8,
        "nausea": 0.65,
        "abdominal_pain": 0.55,
        "loss_of_appetite": 0.7,
        "vomiting": 0.4,
        "itching": 0.35,
    },
    "Tuberculosis": {
        "cough": 0.9,
        "fever": 0.75,
        "fatigue": 0.8,
        "sweating": 0.7,
        "loss_of_appetite": 0.65,
        "chest_pain": 0.5,
        "breathing_difficulty": 0.4,
    },
}


def generate_dataset(
    output_path: str | Path,
    samples_per_class: int = 120,
    seed: int = 42,
) -> Path:
    """Write a synthetic CSV with binary symptom features and prognosis labels."""
    rng = np.random.default_rng(seed)
    rows = []

    for disease, profile in DISEASE_PROFILES.items():
        for _ in range(samples_per_class):
            row = {symptom: 0 for symptom in SYMPTOMS}
            for symptom in SYMPTOMS:
                p = float(profile.get(symptom, 0.08))
                # Add small noise so rows are less often identical
                p = float(np.clip(p + rng.normal(0, 0.05), 0.01, 0.99))
                row[symptom] = int(rng.random() < p)
            if sum(row.values()) == 0:
                forced = rng.choice(SYMPTOMS)
                row[forced] = 1
            row["prognosis"] = disease
            rows.append(row)

    df = pd.DataFrame(rows)
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    out = (
        Path(__file__).resolve().parents[1]
        / "backend"
        / "data"
        / "raw"
        / "disease_dataset.csv"
    )
    path = generate_dataset(out)
    print(f"Wrote {path} shape={pd.read_csv(path).shape}")

