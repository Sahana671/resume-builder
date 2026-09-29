"""
Models package.

Importing every model here ensures that SQLAlchemy's Base.metadata
knows about all tables when `Base.metadata.create_all(engine)` is
called from main.py.
"""

from app.models.user import User
from app.models.job import Job
from app.models.resume import Resume
from app.models.candidate import Candidate, ScreeningResult

__all__ = ["User", "Job", "Resume", "Candidate", "ScreeningResult"]
