"""
helpers.py
-----------
Small shared utility functions: password hashing/verification, JWT
token creation/decoding, and local file storage helpers.

AWS S3 note: `save_upload_file()` currently saves resumes to a local
`uploads/` folder so the project works fully offline. To move to AWS
S3, replace the body of that function with a `boto3` upload call
using the AWS_* environment variables from .env.example — the rest
of the app only depends on getting back a `file_path`/key string, so
no other code needs to change.
"""

import os
import shutil
import uuid
from datetime import datetime, timedelta

from fastapi import UploadFile
from jose import jwt, JWTError
from passlib.context import CryptContext

# Fix for passlib 1.7.4 incompatibility with bcrypt >= 4.0.0
import bcrypt
if not hasattr(bcrypt, "__about__"):
    class _BcryptAbout:
        __version__ = getattr(bcrypt, "__version__", "3.2.2")
    bcrypt.__about__ = _BcryptAbout()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24  # 1 day

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None


def save_upload_file(upload_file: UploadFile) -> str:
    """
    Save an uploaded resume file to the local uploads/ directory with
    a unique filename, and return the saved file path.
    """
    ext = os.path.splitext(upload_file.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    destination = os.path.join(UPLOAD_DIR, unique_name)

    with open(destination, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return destination
