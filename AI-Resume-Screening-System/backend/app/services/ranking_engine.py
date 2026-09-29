"""
ranking_engine.py
--------------------
Ranks candidates for a given job based on their stored screening
results (match_score), highest first.
"""

from sqlalchemy.orm import Session
from app.models.candidate import ScreeningResult


def rank_candidates_for_job(db: Session, job_id: int) -> list[ScreeningResult]:
    """
    Return all ScreeningResult rows for a job, ordered by match_score
    descending (best candidates first).
    """
    return (
        db.query(ScreeningResult)
        .filter(ScreeningResult.job_id == job_id)
        .order_by(ScreeningResult.match_score.desc())
        .all()
    )
