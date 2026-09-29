"""
jobs.py (routes)
-------------------
CRUD-style endpoints for Job Descriptions.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.job import Job

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


class JobCreateRequest(BaseModel):
    title: str
    description: str
    required_skills: str          # comma-separated, e.g. "Python, SQL, React"
    required_experience: str | None = None   # e.g. "2 Years"
    required_qualification: str | None = None  # e.g. "BCA"


@router.post("")
def create_job(payload: JobCreateRequest, db: Session = Depends(get_db)):
    job = Job(
        title=payload.title,
        description=payload.description,
        required_skills=payload.required_skills,
        required_experience=payload.required_experience,
        required_qualification=payload.required_qualification,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("")
def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).order_by(Job.created_at.desc()).all()


@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job
