"""
candidates.py (routes)
--------------------------
Endpoints for:
  - Running the AI screening/matching process (resume <-> job)
  - Listing candidates and their screening results
  - Viewing full candidate detail (matched/missing skills, AI summary)
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.candidate import Candidate, ScreeningResult
from app.models.job import Job
from app.models.resume import Resume
from app.services.job_analyzer import analyze_job
from app.services.matching_engine import calculate_match

router = APIRouter(tags=["Candidates & Screening"])


class AnalyzeRequest(BaseModel):
    resume_id: int
    job_id: int


@router.post("/api/screening/analyze")
def analyze_resume_against_job(payload: AnalyzeRequest, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == payload.resume_id).first()
    job = db.query(Job).filter(Job.id == payload.job_id).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    candidate = db.query(Candidate).filter(Candidate.resume_id == resume.id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate record not found for this resume.")

    # Analyze job requirements
    job_data = analyze_job(
        job.title, job.description, job.required_skills,
        job.required_experience, job.required_qualification,
    )

    # Build resume_data for the matching engine
    resume_skills = [s.strip() for s in (resume.extracted_skills or "").split(",") if s.strip()]
    resume_education = [e.strip() for e in (resume.extracted_education or "").split(",") if e.strip()]
    try:
        experience_years = float(resume.extracted_experience or 0)
    except ValueError:
        experience_years = 0.0

    resume_data = {
        "name": resume.candidate_name,
        "skills": resume_skills,
        "education": resume_education,
        "experience_years": experience_years,
        "raw_text": resume.raw_text or "",
    }

    result = calculate_match(resume_data, job_data)

    # Persist screening result (update if one already exists for this pair)
    existing = (
        db.query(ScreeningResult)
        .filter(ScreeningResult.candidate_id == candidate.id, ScreeningResult.job_id == job.id)
        .first()
    )
    screening = existing or ScreeningResult(candidate_id=candidate.id, job_id=job.id)

    screening.match_score = result["match_score"]
    screening.skill_match_score = result["skill_match_score"]
    screening.experience_match_score = result["experience_match_score"]
    screening.education_match_score = result["education_match_score"]
    screening.keyword_match_score = result["keyword_match_score"]
    screening.matched_skills = ", ".join(result["matched_skills"])
    screening.missing_skills = ", ".join(result["missing_skills"])
    screening.ai_summary = result["ai_summary"]
    screening.status = result["status"]

    if not existing:
        db.add(screening)
    db.commit()
    db.refresh(screening)

    return {
        "message": "Screening completed.",
        "candidate_id": candidate.id,
        "job_id": job.id,
        **result,
    }


@router.get("/api/candidates")
def list_candidates(db: Session = Depends(get_db)):
    candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).all()
    response = []
    for c in candidates:
        latest_result = (
            db.query(ScreeningResult)
            .filter(ScreeningResult.candidate_id == c.id)
            .order_by(ScreeningResult.created_at.desc())
            .first()
        )
        response.append({
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "skills": c.skills,
            "experience": c.experience,
            "education": c.education,
            "match_score": latest_result.match_score if latest_result else None,
            "status": latest_result.status if latest_result else "Not Screened",
        })
    return response


@router.get("/api/candidates/{candidate_id}")
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    resume = db.query(Resume).filter(Resume.id == candidate.resume_id).first()
    results = (
        db.query(ScreeningResult)
        .filter(ScreeningResult.candidate_id == candidate.id)
        .order_by(ScreeningResult.created_at.desc())
        .all()
    )

    return {
        "candidate": {
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "skills": candidate.skills,
            "experience": candidate.experience,
            "education": candidate.education,
        },
        "resume": {
            "id": resume.id if resume else None,
            "file_name": resume.file_name if resume else None,
            "phone": resume.candidate_phone if resume else None,
        },
        "screening_results": [
            {
                "job_id": r.job_id,
                "match_score": r.match_score,
                "skill_match_score": r.skill_match_score,
                "experience_match_score": r.experience_match_score,
                "education_match_score": r.education_match_score,
                "keyword_match_score": r.keyword_match_score,
                "matched_skills": r.matched_skills,
                "missing_skills": r.missing_skills,
                "ai_summary": r.ai_summary,
                "status": r.status,
            }
            for r in results
        ],
    }
