"""
resume.py
----------
SQLAlchemy model representing an uploaded resume file and the raw/
extracted text pulled from it during NLP processing.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import func
from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # local path or S3 key
    candidate_name = Column(String(150), nullable=True)
    candidate_email = Column(String(150), nullable=True)
    candidate_phone = Column(String(50), nullable=True)
    raw_text = Column(Text().with_variant(LONGTEXT, "mysql"), nullable=True)
    extracted_skills = Column(Text, nullable=True)      # comma-separated
    extracted_education = Column(Text, nullable=True)
    extracted_experience = Column(Text, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
