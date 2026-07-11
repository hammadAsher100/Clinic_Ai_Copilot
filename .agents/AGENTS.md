# Clinical AI Co-Pilot — Project Memory

This file maintains context about what has been built, architectural decisions,
and remaining work for the Clinical AI Co-Pilot hackathon project.

---

## Project Overview

**Theme**: AI Co-Pilot for Industry — Healthcare Assistant track  
**Stack**: FastAPI + HTML/CSS/JS + PostgreSQL/SQLite + Docker + MLflow + GitHub Actions  
**Status**: Core implementation complete (Phases 1–4). Infrastructure, tests, and scripts in progress.

---

## What Has Been Built

### Phase 1 — Project Restructure ✅
- Deleted all legacy template stubs (`etl/`, `features/`, `evaluation/`, `monitoring/`, `models/`, `config/`, `scripts/`, `notebooks/`)
- Created new directory structure: `ml/`, `api/{core,db,schemas,services,routers}/`, `frontend/{css,js}/`, `data/{raw,processed,uploads,reports}/`
- Fixed `requirements.txt` (deduped httpx, added matplotlib, pydantic-settings, pytest-asyncio)
- `.env` already configured with Groq API key, DB config, model paths

### Phase 2 — ML Models ✅ (3 models, all with MLflow integration)

| Model | Location | Architecture | Explainability |
|-------|----------|-------------|----------------|
| ANN (Heart Disease) | `ml/ann/` | Dense(64)→Dropout→Dense(32)→Dense(1,sigmoid) | SHAP KernelExplainer + bar chart |
| CNN (Pneumonia) | `ml/cnn/` | MobileNetV2 (frozen) + classification head | Manual Grad-CAM on last conv layer |
| BiLSTM (Symptoms) | `ml/text_model/` | Embedding→SpatialDropout→BiLSTM(64)→Dense(24,softmax) | Top-3 confidence scores |

**Key design decisions:**
- TensorFlow/Keras (not PyTorch) — matches existing requirements.txt
- SHAP uses KernelExplainer (model-agnostic) to avoid DeepExplainer + Keras 3 compatibility issues
- Grad-CAM is a manual TF implementation, not relying on third-party libraries
- All models save to `ml/registry/` as `.h5` files + preprocessor pickles
- Class weighting applied for imbalanced X-ray dataset (~3:1)

### Phase 3 — API Backend ✅ (7 routers, 3 services, 5 DB tables)

**Routers**: `auth.py`, `image.py`, `tabular.py`, `text.py`, `llm_copilot.py`, `hitl.py`, `reports.py`

**Key endpoints:**
- `POST /api/v1/auth/login` — JWT auth
- `POST /api/v1/predict/{image,tabular,text}` — model inference
- `POST /api/v1/copilot/summarize` — LLM narrative (Groq API)
- `GET /api/v1/cases/{id}/review` — HITL dashboard data
- `POST /api/v1/cases/{id}/decision` — approve/reject/edit
- `POST /api/v1/cases/{id}/generate-report` — PDF generation
- `GET /api/v1/cases/{id}/report/download` — serve PDF

**Services:**
- `inference_service.py` — loads all 3 models at startup, exposes `predict_*()` functions
- `llm_service.py` — Groq API client, **reasoning/summarization only** (never diagnostic)
- `pdf_service.py` — pdfplumber for input extraction, reportlab for output report generation

**DB Models** (SQLAlchemy, supports SQLite dev + Postgres production):
- `Patient`, `Case`, `ModelPrediction`, `HITLDecision`, `Report`

**Configuration**: Pydantic `BaseSettings` in `api/core/config.py` loading from `.env`
**Auth**: JWT with bcrypt, demo users (clinician/demo2026, admin/admin2026)
**Logging**: Structured Python logging with separate prediction/hitl/api loggers

### Phase 4 — Frontend ✅ (4 HTML pages, dark-mode glassmorphism design)

- `index.html` — Login with JWT auth flow
- `upload.html` — 4-modality upload (X-ray drag-drop, vitals form, symptoms textarea, PDF)
- `review.html` — HITL dashboard with confidence gauges, SHAP charts, Grad-CAM, approve/reject/edit
- `report.html` — Report download with cases table

**Design system**: Inter font, navy/teal/amber/coral palette, glassmorphism cards, micro-animations
**Charts**: Vanilla JS Canvas — SHAP bar charts, confidence gauges, top-3 condition rankings (no external lib)

---

## What Remains

### Phase 5 — Infrastructure
- `Dockerfile` — add frontend + ml COPY, static file serving
- `docker-compose.yml` — add volumes, healthchecks, shared network
- `.github/workflows/ci-cd.yml` — conditional Docker push
- `.env.example` — sanitized template
- `.gitignore` — add new patterns

### Phase 6 — Tests
- `tests/conftest.py` — shared fixtures, mock models, test DB
- `tests/test_api.py` — router tests with mocked models
- `tests/test_ml_models.py` — model load + output shape validation
- Delete stale `tests/test_etl.py`, `tests/test_features.py`

### Phase 7 — Sample Data & Scripts
- `scripts/download_data.py` — dataset download helper
- `scripts/create_sample_pdfs.py` — synthetic clinical PDF generator
- `README.md` — full project documentation update

---

## Data Requirements (must be downloaded before training)

| Dataset | Source | Location | Notes |
|---------|--------|----------|-------|
| Chest X-Ray Pneumonia | `kaggle: paultimothymooney/chest-xray-pneumonia` | `data/raw/xray/` | Pre-split train/val/test |
| UCI Heart Disease | `archive.ics.uci.edu/dataset/45` | `data/raw/tabular/heart.csv` | 303 rows, 14 cols |
| Symptom2Disease | `kaggle: niyarrbarman/symptom2disease` | `data/raw/text/Symptom2Disease.csv` | 1200 rows, 24 classes |

---

## Critical Rules & Constraints

1. **LLM is NOT the diagnostic engine** — it only summarizes structured outputs from CNN/ANN/BiLSTM
2. **Models must be loaded at startup** (not per-request) for demo responsiveness
3. **No Streamlit or React** — vanilla HTML/CSS/JS only
4. **Pydantic models for every request/response** — no raw dicts across API boundary
5. **Business logic in services, not routers** — routers only handle HTTP concerns
6. **SHAP uses KernelExplainer** (not DeepExplainer) for Keras 3 compatibility
7. **Grad-CAM is manual TF implementation** — no third-party grad-cam libraries
8. **Class weighting** required for imbalanced X-ray data (~3:1 pneumonia:normal)

---

## File Map (key files only)

```
ml/
├── ann/        preprocess.py, model.py, train.py, shap_explain.py
├── cnn/        preprocess.py, model.py, train.py, gradcam.py
├── text_model/ preprocess.py, model.py, train.py
└── registry/   (model artifacts: .h5, .pkl — gitignored)

api/
├── main.py
├── core/       config.py, logging_config.py, security.py
├── db/         models.py, session.py
├── schemas/    prediction.py, case.py, hitl.py, report.py, auth.py, common.py
├── services/   inference_service.py, llm_service.py, pdf_service.py
└── routers/    image.py, tabular.py, text.py, llm_copilot.py, hitl.py, reports.py, auth.py

frontend/
├── index.html, upload.html, review.html, report.html
├── css/styles.css
└── js/api.js, charts.js
```
