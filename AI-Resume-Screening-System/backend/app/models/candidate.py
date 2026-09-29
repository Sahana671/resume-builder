"""
candidate.py
-------------
Models for candidates (derived from a Resume) and the ScreeningResult
which stores the outcome of matching a candidate's resume against a
specific job (matching score, matched/missing skills, status).
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    name = Column(String(150), nullable=True)
    email = Column(String(150), nullable=True)
    skills = Column(Text, nullable=True)
    experience = Column(String(100), nullable=True)
    education = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume")
    screening_results = relationship("ScreeningResult", back_populates="candidate")


class ScreeningResult(Base):
    __tablename__ = "screening_results"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)

    match_score = Column(Float, default=0.0)
    skill_match_score = Column(Float, default=0.0)
    experience_match_score = Column(Float, default=0.0)
    education_match_score = Column(Float, default=0.0)
    keyword_match_score = Column(Float, default=0.0)

    matched_skills = Column(Text, nullable=True)   # comma-separated
    missing_skills = Column(Text, nullable=True)   # comma-separated
    ai_summary = Column(Text, nullable=True)

    status = Column(String(50), default="Pending")  # Pending / Shortlisted / Rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    candidate = relationship("Candidate", back_populates="screening_results")
    job = relationship("Job")
