"""
database.py
------------
Handles the MySQL database connection using SQLAlchemy.

For local development, this reads connection details from environment
variables (see .env.example). If MySQL is not available, you can still
explore the API structure, but actual data operations will fail until
a database is configured.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "ai_resume_screening")

# Full database URL. Example:
# mysql+pymysql://root:password@localhost:3306/ai_resume_screening
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"mysql+pymysql://{MYSQL_USER}:{quote_plus(MYSQL_PASSWORD)}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}",
)

# `pool_pre_ping` and `pool_recycle` keep long-lived AWS RDS connections healthy.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
     connect_args={"charset": "utf8mb4", "connect_timeout": 5} if "mysql" in DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session per request
    and guarantees it is closed afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
