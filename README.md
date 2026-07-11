# Clinical AI Co-Pilot

A multi-modal clinical decision support platform built with FastAPI, deep learning models, MLflow experiment tracking, and a lightweight browser-based frontend.

## Project Overview

This repository demonstrates a clinical AI assistant that combines:
- Chest X-ray classification via CNN
- Heart disease risk prediction via ANN
- Symptom classification via text model (BiLSTM/GRU style workflow)
- LLM-powered case summarization and report generation
- Human-in-the-loop review workflow for clinical validation

The backend exposes REST endpoints for image, tabular, and text prediction, plus report generation and user authentication. It also serves the static frontend from the `frontend/` folder.

## Key Features

- FastAPI backend with async startup lifecycle and model loading
- PostgreSQL support via Docker Compose, with fallback configuration for SQLite
- MLflow tracking server for experiment and model metadata
- JWT authentication for protected API routes
- Static frontend pages for upload, review, and report workflow
- PDF report generation and upload management
- Automated linting and test configuration via GitHub Actions

## Repository Structure

- `api/` - FastAPI application, routers, services, database and security layers
- `api/core/` - configuration, logging, and security utilities
- `api/db/` - SQLAlchemy session and database setup
- `api/routers/` - API route definitions for auth, image, tabular, text, HITL, reports, and LLM copilot
- `api/services/` - inference, LLM, and PDF services
- `frontend/` - static HTML, CSS, and JavaScript UI assets
- `ml/` - model training, preprocessing, and registry utilities
- `data/` - raw and processed data, uploads, generated reports, and ML run artifacts
- `mlruns/` - MLflow artifact store for experiments
- `tests/` - unit and integration tests

## Requirements

- Python 3.10+ (project uses `requirements.txt`)
- Docker and Docker Compose for containerized deployment
- PostgreSQL is included in Docker Compose configuration
- Optional: Groq API key for LLM summarization

## Quick Start

### 1. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Copy environment variables

```powershell
copy .env.example .env
```

Edit `.env` and update values as needed.

### 3. Run locally with Docker Compose

```powershell
docker compose up --build
```

The backend will be available at `http://localhost:8000` and MLflow UI at `http://localhost:5000`.

### 4. Access the frontend

Open `http://localhost:8000/static/frontend/index.html` in your browser.

## Environment Configuration

The application uses `.env` variables loaded by `api/core/config.py`. Important variables include:

- `DATABASE_URL` - database connection string
- `MLFLOW_TRACKING_URI` - MLflow server URL
- `MODEL_REGISTRY_PATH`, `CNN_MODEL_PATH`, `ANN_MODEL_PATH`, `TEXT_MODEL_PATH`, `TEXT_TOKENIZER_PATH`
- `GROQ_API_KEY`, `GROQ_API_BASE_URL`, `GROQ_MODEL`
- `JWT_SECRET_KEY`, `JWT_ALGORITHM`
- `API_HOST`, `API_PORT`
- `UPLOAD_DIR`, `REPORTS_DIR`

## Running the API Directly

```powershell
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Testing

Run tests with:

```powershell
pytest tests/ -v --tb=short
```

The CI workflow also runs `flake8` linting and tests on pushes and pull requests.

## Docker Compose

The `docker-compose.yml` file defines:

- `api` - FastAPI service
- `db` - PostgreSQL database
- `mlflow` - MLflow tracking server

It also mounts model registry and data directories so uploaded files and traced artifacts persist locally.

## Notes

- Uploaded files are stored in `data/uploads`
- Generated reports are stored in `data/reports`
- The frontend is served from `frontend/` through FastAPI static file mounting

## Contribution

1. Fork the repo
2. Create a feature branch
3. Add tests for new functionality
4. Open a pull request

## License

This project is covered by the repository `LICENSE` file.
