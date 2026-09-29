"""
lambda_function.py
---------------------
AWS Lambda entry point for the "resume-processor" function.

Workflow:
    API Gateway -> Lambda (this file) -> S3 -> NLP -> matching score -> response

This function is self-contained (no imports from the FastAPI app
package) so it can be zipped and deployed independently to AWS
Lambda. It duplicates the lightweight extraction/matching logic from
backend/app/services/* by design, since Lambda deployment packages
should not depend on the full FastAPI backend.

Deployment (summary — see /aws/README.md for full steps):
    1. pip install -r requirements.txt -t ./package
    2. Copy this file into ./package
    3. Zip the package folder
    4. Create/update the Lambda function "resume-processor" with that zip
    5. Set environment variables: AWS_S3_BUCKET, AWS_REGION
    6. Give the function's execution role s3:GetObject on the bucket

Event shape (from API Gateway / lambda_handler.py):
{
  "s3_bucket": "ai-resume-screening-bucket",
  "s3_key": "resumes/abc123.pdf",
  "job": {
      "required_skills": ["python", "sql", "react"],
      "required_years": 2,
      "required_qualification": "bca",
      "keywords": ["python", "backend", "api"]
  }
}
"""

import json
import re
import io
import os

import boto3

s3_client = boto3.client("s3", region_name=os.getenv("AWS_REGION", "ap-south-1"))

SKILL_VOCABULARY = [
    "python", "java", "javascript", "react", "node", "django", "flask",
    "fastapi", "sql", "mysql", "mongodb", "aws", "docker", "kubernetes",
    "git", "machine learning", "nlp", "pandas", "numpy", "html", "css",
]

WEIGHTS = {"skill": 0.50, "experience": 0.20, "education": 0.15, "keyword": 0.15}


def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    """Extract text from PDF bytes using pdfplumber (bundled in the Lambda layer/package)."""
    import pdfplumber
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_skills(text: str) -> list:
    text_lower = text.lower()
    return sorted({s for s in SKILL_VOCABULARY if s in text_lower})


def extract_experience_years(text: str) -> float:
    match = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*years?", text.lower())
    return float(match.group(1)) if match else 0.0


def calculate_match(resume_skills, resume_years, job: dict) -> dict:
    required_skills = set(job.get("required_skills", []))
    matched = sorted(set(resume_skills) & required_skills)
    missing = sorted(required_skills - set(resume_skills))
    skill_score = (len(matched) / len(required_skills) * 100) if required_skills else 100.0

    required_years = job.get("required_years", 0)
    experience_score = 100.0 if resume_years >= required_years or required_years <= 0 else round(
        (resume_years / required_years) * 100, 2
    )

    education_score = 80.0  # simplified for the Lambda path
    keyword_score = 80.0    # simplified for the Lambda path

    final_score = round(
        skill_score * WEIGHTS["skill"]
        + experience_score * WEIGHTS["experience"]
        + education_score * WEIGHTS["education"]
        + keyword_score * WEIGHTS["keyword"],
        2,
    )
    status = "Shortlisted" if final_score >= 70 else ("Pending" if final_score >= 40 else "Rejected")

    return {
        "match_score": final_score,
        "skill_match_score": round(skill_score, 2),
        "experience_match_score": experience_score,
        "education_match_score": education_score,
        "keyword_match_score": keyword_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "status": status,
    }


def lambda_handler(event, context):
    """Main Lambda entry point."""
    try:
        body = event.get("body")
        payload = json.loads(body) if isinstance(body, str) else event

        s3_bucket = payload["s3_bucket"]
        s3_key = payload["s3_key"]
        job = payload.get("job", {})

        # 1. Read resume from S3
        s3_object = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
        file_bytes = s3_object["Body"].read()

        # 2. Extract text (PDF assumed; extend for DOCX as needed)
        raw_text = extract_text_from_pdf_bytes(file_bytes)

        # 3. NLP extraction
        skills = extract_skills(raw_text)
        experience_years = extract_experience_years(raw_text)

        # 4. Matching score against the provided job
        result = calculate_match(skills, experience_years, job)

        response_body = {
            "s3_key": s3_key,
            "extracted_skills": skills,
            "experience_years": experience_years,
            **result,
        }

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response_body),
        }

    except Exception as exc:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(exc)}),
        }
