"""
Industry-Grade Healthcare Interoperability Application
Phase 1: Semantic Discovery and Evidence-Based FHIR R4 Mapping

Main FastAPI Application Entrypoint.
"""

import os
import sys
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.database import engine, Base, SessionLocal, get_db
from app.services.seed_service import seed_existing_phase1_data

# Import API Routers
from app.api.projects import router as projects_router
from app.api.databases import router as databases_router
from app.api.analysis import router as analysis_router
from app.api.mappings import router as mappings_router
from app.api.reviews import router as reviews_router
from app.api.reports import router as reports_router
from app.api.resources import router as resources_router
from app.api.health import router as health_router
from app.api.audit import router as audit_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and seed initial Phase 1 data
    logger.info("Initializing Healthcare Interoperability Platform database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        logger.info("Checking and seeding initial Phase 1 hospital evaluations...")
        seed_existing_phase1_data(db)
        logger.info("Phase 1 initialization complete.")
    except Exception as e:
        logger.error(f"Error during data seeding: {e}", exc_info=True)
    finally:
        db.close()
        
    yield
    # Shutdown
    logger.info("Shutting down Healthcare Interoperability Platform.")


app = FastAPI(
    title="Legacy EHR → FHIR R4 Interoperability Platform",
    description=(
        "Phase 1: Semantic Discovery and Evidence-Based FHIR R4 Mapping. "
        "Autonomous clinical schema profiling, hybrid evidence retrieval, "
        "semantic candidate proposal, and deterministic confidence scoring."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health_router)
app.include_router(projects_router)
app.include_router(databases_router)
app.include_router(analysis_router)
app.include_router(mappings_router)
app.include_router(reviews_router)
app.include_router(reports_router)
app.include_router(resources_router)
app.include_router(audit_router)

# Static files mounts
STATIC_DIR = os.path.join(BASE_DIR, "static")
CHARTS_DIR = os.path.join(BASE_DIR, "outputs", "reports", "charts")

os.makedirs(STATIC_DIR, exist_ok=True)
if os.path.exists(CHARTS_DIR):
    app.mount("/static/charts", StaticFiles(directory=CHARTS_DIR), name="charts")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=FileResponse)
def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Phase 1 Interoperability Platform - Frontend loading...</h1>")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
