"""
main.py
-------
FastAPI application entry point for the Poker Training backend.

Run with:
    uvicorn main:app --reload

API Base: http://localhost:8000/api

Canonical endpoints:
    GET  /api/scenario/new              — Request a new training scenario
    GET  /api/scenario/fixture/{name}   — Get a named fixture scenario
    GET  /api/scenario/example          — Get the static example scenario
    POST /api/decision/analyze          — Submit a user's action + get coaching
    POST /api/analyze                   — Stateless analysis (no logging)
    POST /api/hand/review               — Full hand review
    POST /api/session/save              — Save a session summary
    GET  /api/session/{id}/summary      — Retrieve session report
    GET  /api/health                    — Health check
    GET  /api/docs                      — Interactive API documentation
"""

import sys
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — allow importing agent execution scripts
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent.parent
AGENT_EXEC_PATH = REPO_ROOT / "agent" / "execution"
APP_SHARED_PATH = REPO_ROOT / "app" / "shared"

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(AGENT_EXEC_PATH))
sys.path.insert(0, str(APP_SHARED_PATH))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import scenarios, decisions, sessions

# ---------------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Poker Training API",
    description=(
        "Backend for the Poker Training Application. "
        "Educational use only — no real money, no multiplayer."
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ---------------------------------------------------------------------------
# CORS — allow frontend dev server
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",    # Vite default
        "http://localhost:3000",    # CRA fallback
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(scenarios.router, prefix="/api", tags=["scenarios"])
app.include_router(decisions.router, prefix="/api", tags=["decisions"])
app.include_router(sessions.router,  prefix="/api", tags=["sessions"])

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/api/health", tags=["health"])
async def health_check():
    return {"status": "ok", "service": "poker-training-api", "version": "1.0.0"}


# ---------------------------------------------------------------------------
# Root redirect
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Poker Training API. See /api/docs for documentation."}
