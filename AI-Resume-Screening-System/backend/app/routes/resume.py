"""
resume.py (routes)
---------------------
Endpoints for uploading resumes and retrieving extracted resume data.

Upload flow:
  1. Save file locally (or to S3 in production, see helpers.py)
  2. Extract raw text (resume_parser.py)
  3. Extract skills/education/experience (skill_extractor.py)
  4. Persist a Resume row and a linked Candidate row
"""

import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.resume import Resume
from app.models.candidate import Candidate
from app.services.resume_parser import parse_resume
from app.services.skill_extractor import analyze_resume_skills
from app.utils.helpers import save_upload_file
from app.aws.s3_service import upload_resume_to_s3, generate_presigned_url

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}


@router.post("/upload")
def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF, DOC and DOCX files are supported.")

    # 1. Save file locally for text extraction
    saved_path = save_upload_file(file)

    # 2. Upload to S3 if AWS bucket is configured (supports both IAM role on EC2 and explicit IAM keys)
    s3_key = None
    s3_bucket = os.getenv("AWS_S3_BUCKET")
    if s3_bucket:
        try:
            with open(saved_path, "rb") as f:
                file_bytes = f.read()
            s3_res = upload_resume_to_s3(file_bytes, file.filename)
            s3_key = s3_res.get("key")
        except Exception as s3_err:
            print(f"Warning: S3 upload failed, falling back to local path: {s3_err}")

    # 3. Extract text + contact info
    try:
        parsed = parse_resume(saved_path)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse resume: {exc}")

    # 4. Extract skills/education/experience
    analysis = analyze_resume_skills(parsed["raw_text"])

    # 5. Persist Resume (store S3 key if uploaded, else local path)
    resume = Resume(
        file_name=file.filename,
        file_path=s3_key if s3_key else saved_path,
        candidate_name=parsed["name"],
        candidate_email=parsed["email"],
        candidate_phone=parsed["phone"],
        raw_text=parsed["raw_text"],
        extracted_skills=", ".join(analysis["skills"]),
        extracted_education=", ".join(analysis["education"]),
        extracted_experience=str(analysis["experience_years"]),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    # Also create a linked Candidate record for easy listing/ranking
    candidate = Candidate(
        resume_id=resume.id,
        name=parsed["name"],
        email=parsed["email"],
        skills=", ".join(analysis["skills"]),
        experience=f"{analysis['experience_years']} Years",
        education=", ".join(analysis["education"]) or "Not specified",
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return {
        "message": "Resume uploaded and processed successfully.",
        "resume_id": resume.id,
        "candidate_id": candidate.id,
        "storage": "s3" if s3_key else "local",
        "s3_key": s3_key,
        "extracted": {
            "name": parsed["name"],
            "email": parsed["email"],
            "phone": parsed["phone"],
            "skills": analysis["skills"],
            "education": analysis["education"],
            "experience_years": analysis["experience_years"],
        },
    }


@router.get("")
def list_resumes(db: Session = Depends(get_db)):
    resumes = db.query(Resume).order_by(Resume.uploaded_at.desc()).all()
    return [
        {
            "id": r.id,
            "file_name": r.file_name,
            "candidate_name": r.candidate_name,
            "candidate_email": r.candidate_email,
            "extracted_skills": r.extracted_skills,
            "uploaded_at": r.uploaded_at,
        }
        for r in resumes
    ]


@router.get("/{resume_id}")
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    download_url = None
    if resume.file_path:
        if resume.file_path.startswith("resumes/"):
            try:
                download_url = generate_presigned_url(resume.file_path)
            except Exception as e:
                print(f"Warning: Failed to generate presigned URL: {e}")
                download_url = None
        elif os.path.exists(resume.file_path):
            filename = os.path.basename(resume.file_path)
            download_url = f"/uploads/{filename}"

    return {
        "id": resume.id,
        "file_name": resume.file_name,
        "file_path": resume.file_path,
        "candidate_name": resume.candidate_name,
        "candidate_email": resume.candidate_email,
        "candidate_phone": resume.candidate_phone,
        "raw_text": resume.raw_text,
        "extracted_skills": resume.extracted_skills,
        "extracted_education": resume.extracted_education,
        "extracted_experience": resume.extracted_experience,
        "uploaded_at": resume.uploaded_at,
        "download_url": download_url,
    }
