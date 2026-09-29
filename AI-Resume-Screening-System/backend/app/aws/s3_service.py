"""
s3_service.py
---------------
Amazon S3 service for resume storage.

Credentials are NEVER hard-coded — boto3 reads them from environment
variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION) as
set in .env / .env.example, or from the Lambda execution role when
running inside AWS.

This module mirrors `save_upload_file()` in utils/helpers.py, which
is what the local-dev backend uses instead. To switch the running
app from local disk storage to S3, replace the call to
`save_upload_file()` in routes/resume.py with `upload_resume_to_s3()`
below — the rest of the pipeline (parsing, NLP, matching) is
unaffected because it only depends on getting back a file
reference/text, not on *where* the file lives.
"""

import os
import uuid
from dotenv import load_dotenv

load_dotenv()

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None
    ClientError = Exception


def get_s3_bucket() -> str:
    return os.getenv("AWS_S3_BUCKET") or "ai-resume-screening-bucket"


def get_aws_region() -> str:
    return os.getenv("AWS_REGION") or "ap-south-1"


def _get_s3_client():
    """Create a boto3 S3 client using environment-provided credentials or IAM role."""
    if boto3 is None:
        raise RuntimeError("boto3 is not installed. Run: pip install boto3")
    return boto3.client("s3", region_name=get_aws_region())


def generate_unique_key(original_filename: str) -> str:
    """Generate a unique S3 object key for a resume, preserving its extension."""
    ext = os.path.splitext(original_filename)[1]
    return f"resumes/{uuid.uuid4().hex}{ext}"


def upload_resume_to_s3(file_bytes: bytes, original_filename: str) -> dict:
    """
    Upload resume bytes to the configured S3 bucket.

    Returns a dict with the S3 key, bucket name and a constructed
    object URL, so the caller can store this reference in MySQL
    (resumes.file_path).
    """
    s3_client = _get_s3_client()
    bucket = get_s3_bucket()
    region = get_aws_region()
    key = generate_unique_key(original_filename)

    ext = os.path.splitext(original_filename)[1].lower()
    content_type_map = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".doc": "application/msword",
    }
    content_type = content_type_map.get(ext, "application/octet-stream")

    try:
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
        )
    except ClientError as exc:
        raise RuntimeError(f"Failed to upload resume to S3: {exc}")

    return {
        "bucket": bucket,
        "key": key,
        "url": f"https://{bucket}.s3.{region}.amazonaws.com/{key}",
    }


def download_resume_from_s3(key: str) -> bytes:
    """Download a resume's bytes from S3 given its object key."""
    s3_client = _get_s3_client()
    bucket = get_s3_bucket()
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        return response["Body"].read()
    except ClientError as exc:
        raise RuntimeError(f"Failed to download resume from S3: {exc}")


def generate_presigned_url(key: str, expires_in: int = 3600) -> str:
    """
    Generate a temporary, secure URL so the frontend can let a
    recruiter view/download the original resume without making the
    bucket public.
    """
    s3_client = _get_s3_client()
    bucket = get_s3_bucket()
    try:
        return s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )
    except ClientError as exc:
        raise RuntimeError(f"Failed to generate presigned URL: {exc}")


def delete_resume_from_s3(key: str) -> bool:
    """Delete a resume object from S3. Returns True on success."""
    s3_client = _get_s3_client()
    bucket = get_s3_bucket()
    try:
        s3_client.delete_object(Bucket=bucket, Key=key)
        return True
    except ClientError:
        return False
