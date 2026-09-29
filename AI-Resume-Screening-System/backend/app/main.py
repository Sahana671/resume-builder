"""
main.py
--------
FastAPI application entry point.

Run locally with:
    uvicorn app.main:app --reload

This wires together the database, all models (so tables get created)
and all route modules.
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()

from app.database import Base, engine
from app import models  # noqa: F401  (ensures all models are registered)
from app.routes import auth, resume, jobs, candidates, ranking
from app.utils.helpers import UPLOAD_DIR

# Create all tables if they don't already exist.
# (If schema.sql was already imported in Phase 4 of AWS deployment, this is a safe no-op.)
try:
    Base.metadata.create_all(bind=engine)
except Exception as exc:
    print(f"Notice: Automatic table creation deferred or failed (schema.sql can be used instead): {exc}")

app = FastAPI(
    title="AI Resume Screening System API",
    description="Backend API for uploading resumes, analyzing job descriptions, "
                "and generating AI-based candidate matching scores.",
    version="1.0.0",
)

# Configurable CORS for production (AWS Amplify domain) and local development.
cors_origins_raw = os.getenv("CORS_ORIGINS", "*")
origins = [o.strip() for o in cors_origins_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve local uploads for file downloads when running with local storage fallback
if os.path.exists(UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(jobs.router)
app.include_router(candidates.router)
app.include_router(ranking.router)


@app.get("/")
def root():
    return {
        "message": "AI Resume Screening System API is running.",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
