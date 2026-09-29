"""
job.py
-------
SQLAlchemy model representing a Job Description (JD) created by a
recruiter. Resumes are screened/matched against these jobs.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(Text, nullable=False)  # comma-separated skills
    required_experience = Column(String(50), nullable=True)  # e.g. "2 Years"
    required_qualification = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
