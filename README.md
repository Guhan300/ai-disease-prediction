# MedAI — Conversational Disease Risk Prediction

Educational/research ChatGPT-style symptom assistant. A **trained local ML model**
produces disease/risk estimates. A **local LLM (Ollama)** handles conversation and
explanations only. Optional **local RAG** adds educational context.

> This application provides educational, model-based health information and is **not**
> a substitute for professional medical diagnosis or treatment.

No OpenAI / Gemini / Claude / Groq / OpenRouter APIs.

---

## Quick start

```powershell
cd C:\Users\guhan\Desktop\Projects\local-ai-disease-risk
copy .env.example .env

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Dataset (synthetic educational CSV; replace with Kaggle CSV if you prefer)
python scripts/generate_dataset.py

# Train LR / RF / XGBoost / SVM and save best model
python scripts/train_model.py

# Build local FAISS knowledge index
python scripts/ingest_knowledge_base.py

# Backend
uvicorn app.main:app --reload --app-dir backend --host 127.0.0.1 --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

---

## How it works

```
User chat → symptom extraction (Ollama or rules)
         → question engine follow-ups
         → safety red-flag check
         → feature mapping
         → trained ML model (top-3 scores)
         → SHAP / feature explanation
         → local RAG context
         → LLM explanation (fallback template if Ollama down)
         → chat UI prediction card
```

If Ollama is offline, MedAI still works using rule-based extraction and template explanations.

---

## Optional: Ollama

1. Install Ollama  
2. Pull a model, e.g. `ollama pull qwen2.5:7b`  
3. Set in `.env`:

```
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=qwen2.5:7b
```

---

## Dataset

Default path: `backend/data/raw/disease_dataset.csv`  
Target column: `prognosis` (configurable via `TARGET_COLUMN`)

You may replace the generated CSV with a Kaggle symptom/disease dataset. The
training pipeline inspects columns, imbalance, duplicates, and metrics automatically.

Primary model selection metric: `PRIMARY_METRIC=macro_f1`

---

## Main API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Component health |
| POST | `/api/chat/session` | Start assessment |
| POST | `/api/chat/message` | Conversational turn |
| GET | `/api/chat/session/{id}` | Session detail |
| POST | `/api/predict` | Direct ML prediction |
| GET | `/api/model/info` | Model metadata |
| POST | `/api/rag/search` | Knowledge search |
| GET | `/api/knowledge/sources` | Indexed sources |

---

## Tests

```powershell
.\.venv\Scripts\Activate.ps1
pytest tests -q
```

---

## Important limitations

- Educational demo, not clinical software
- Synthetic dataset is for local demos unless you supply a vetted Kaggle CSV
- Model scores are not calibrated medical probabilities
- Safety rules are limited and not an emergency triage system
