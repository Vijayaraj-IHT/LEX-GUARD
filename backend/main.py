"""
LexGuard FastAPI application (FR-01 through FR-05, 3.1, 3.2).

Serves the prototype front-end (static HTML/CSS/JS) at "/" and the JSON API
under "/api/".
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.config import get_settings
from backend.database import init_db, get_db, engine

settings = get_settings()

STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: initialise database schema (FR-02)."""
    init_db()
    yield


app = FastAPI(
    title="LexGuard",
    description="Legal Learning and Case-Reference Platform for India",
    version=settings.lexguard_version,
    lifespan=lifespan,
)


# --- JSON API endpoints (prefixed with /api) ---

@app.get("/api")
def api_root():
    """Identify the LexGuard JSON API."""
    return {
        "application": "LexGuard",
        "version": settings.lexguard_version,
        "description": "Legal Learning and Case-Reference Platform for India",
        "status": "running",
    }


@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    """
    Report application and database health (FR-03, FR-04, 3.2 Health).

    Distinguishes reviewed records from drafts (FR-48).
    """
    db_status = "unhealthy"
    counts = {}

    try:
        # Test connectivity
        db.execute(text("SELECT 1"))
        db_status = "healthy"

        # Count reviewed vs draft cases (FR-48)
        from backend.models.case import CaseReference
        total_cases = db.query(CaseReference).count()
        draft_cases = (
            db.query(CaseReference)
            .filter(CaseReference.review_status == "draft")
            .count()
        )
        reviewed_cases = total_cases - draft_cases

        counts = {
            "total_cases": total_cases,
            "reviewed_cases": reviewed_cases,
            "draft_cases": draft_cases,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "unhealthy",
            "error": str(e),
        }

    return {
        "status": "healthy",
        "database": db_status,
        "version": settings.lexguard_version,
        "counts": counts,
    }


# --- Static front-end ---

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def serve_frontend():
    """Serve the single-page front-end prototype."""
    return FileResponse(str(STATIC_DIR / "index.html"))
