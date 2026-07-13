"""
FastAPI application entrypoint for the Clinical AI Co-Pilot.

Wires up all routers, CORS, static file serving, database initialisation,
and ML model loading at startup.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.core.logging_config import setup_logging
from api.db.session import init_db

# ── Routers ──────────────────────────────────────────────────────────────
from api.routers import image, tabular, text, llm_copilot, hitl, reports, auth, documents

setup_logging()
logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    # ── Startup ──────────────────────────────────────────────────────────
    logger.info("Initialising database tables...")
    init_db()

    logger.info("Loading ML models into memory...")
    try:
        # Load models in background to avoid startup timeout
        import os
        if os.getenv("SKIP_MODEL_LOAD_ON_STARTUP", "false").lower() == "true":
            logger.warning("Skipping model load on startup (SKIP_MODEL_LOAD_ON_STARTUP=true)")
            logger.info("Models will be loaded on first prediction request")
        else:
            from api.services.inference_service import load_all_models
            load_all_models()
    except Exception as e:
        logger.error("Model loading failed: %s — prediction endpoints will be unavailable", e)

    # Ensure upload & report directories exist
    Path("data/uploads").mkdir(parents=True, exist_ok=True)
    Path("data/reports").mkdir(parents=True, exist_ok=True)

    logger.info("Clinical AI Co-Pilot API is ready")
    yield

    # ── Shutdown ─────────────────────────────────────────────────────────
    logger.info("Shutting down Clinical AI Co-Pilot API")


# ── App ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Clinical AI Co-Pilot",
    description=(
        "Multi-modal clinical decision-support system combining CNN (chest X-ray), "
        "ANN (heart disease risk), and BiLSTM (symptom classification) with "
        "LLM-powered narrative summarization and HITL review workflow."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files (frontend + uploaded artifacts) ─────────────────────────
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static/frontend", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

uploads_dir = Path("data/uploads")
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# ── Register routers ────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(image.router)
app.include_router(tabular.router)
app.include_router(text.router)
app.include_router(llm_copilot.router)
app.include_router(hitl.router)
app.include_router(reports.router)
app.include_router(documents.router)


# ── Health check ─────────────────────────────────────────────────────────
@app.get("/health", tags=["system"])
def health():
    """Health check endpoint for load balancers and monitoring."""
    from api.services.inference_service import models_are_loaded
    return {
        "status": "ok",
        "models_loaded": models_are_loaded(),
    }


# ── Root redirect to frontend ───────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to dashboard."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/frontend/dashboard.html")
