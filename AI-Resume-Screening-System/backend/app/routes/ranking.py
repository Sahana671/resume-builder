"""
ranking.py (routes)
-----------------------
Returns candidates ranked by matching score for a specific job.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.job import Job
from app.models.candidate import Candidate
from app.services.ranking_engine import rank_candidates_for_job

router = APIRouter(prefix="/api/ranking", tags=["Ranking"])


@router.get("/{job_id}")
def get_ranking(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    ranked_results = rank_candidates_for_job(db, job_id)

    ranking = []
    for position, result in enumerate(ranked_results, start=1):
        candidate = db.query(Candidate).filter(Candidate.id == result.candidate_id).first()
        ranking.append({
            "rank": position,
            "candidate_id": candidate.id if candidate else None,
            "name": candidate.name if candidate else "Unknown",
            "match_score": result.match_score,
            "status": result.status,
        })

    return {
        "job_id": job.id,
        "job_title": job.title,
        "ranking": ranking,
    }
