# Amazon S3 Setup

The S3 bucket stores all uploaded resume files.

## 1. Create the bucket

```
aws s3api create-bucket \
  --bucket ai-resume-screening-bucket \
  --region ap-south-1 \
  --create-bucket-configuration LocationConstraint=ap-south-1
```

Use a globally-unique bucket name; update `AWS_S3_BUCKET` in `.env` to match.

## 2. Block public access (recommended)

Keep "Block all public access" ON. Resumes are private; the backend
generates **presigned URLs** (see `backend/app/aws/s3_service.py ->
generate_presigned_url()`) for temporary, secure viewing/downloading
from the Candidate Details page.

## 3. Folder convention

Resumes are stored under the `resumes/` prefix with a UUID filename,
e.g. `resumes/8f14e45f-ceea-4b.pdf`, to avoid collisions and to keep
original filenames out of the object key (they're stored separately
in MySQL as `resumes.file_name`).

## 4. IAM permissions

The backend (or the Lambda execution role) needs at minimum:

```json
{
  "Effect": "Allow",
  "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
  "Resource": "arn:aws:s3:::ai-resume-screening-bucket/*"
}
```

## 5. Local development

S3 is **not required** to run the project locally — the FastAPI
backend saves resumes to a local `backend/uploads/` folder by
default (see `utils/helpers.py -> save_upload_file()`). Switch to S3
in production by calling `upload_resume_to_s3()` from
`app/aws/s3_service.py` instead.
