# AI Resume Screening System

A full-stack, AI/NLP-powered resume screening platform built as a BCA
final-year project. Recruiters create job descriptions, upload
candidate resumes, and the system automatically extracts skills,
education and experience, calculates a weighted matching score
against the job, and ranks candidates — all backed by a cloud-ready
AWS architecture.

## Features

- Recruiter authentication (register/login, JWT-based)
- Job description creation with required skills/experience/qualification
- Drag-and-drop resume upload (PDF/DOC/DOCX)
- NLP-based resume parsing: name, email, phone, skills, education, experience
- Explainable weighted matching score (Skills 50% / Experience 20% / Education 15% / Keywords 15%)
- Matched vs. missing skill identification + AI-style summary
- Candidate ranking per job with visual score bars
- Professional, responsive dashboard UI
- AWS-ready: S3 storage, Lambda resume processing, API Gateway routing

## Technology Stack

| Layer     | Technology                                   |
|-----------|-----------------------------------------------|
| Frontend  | React.js, Vite, React Router, Axios            |
| Backend   | Python, FastAPI, SQLAlchemy                    |
| Database  | MySQL                                          |
| AI/NLP    | Keyword/rule-based extraction & matching (Python) |
| Cloud     | Amazon S3, AWS Lambda, API Gateway             |
| Auth      | JWT + bcrypt password hashing                  |

## Architecture

```
React Frontend
      ↓
API Gateway
      ↓
AWS Lambda  ──(resume-processor)──►  Amazon S3 (resume storage)
      ↓                                     │
NLP / AI Analysis  ◄─────────────────────────┘
      ↓
Job Description Matching
      ↓
Matching Score + Candidate Ranking
      ↓
MySQL Database
      ↓
API Response → React Dashboard
```

Locally, the FastAPI backend performs extraction/matching **in-process**
(no AWS required) so the whole app runs on a laptop for development
and demonstration. In production, uploads and screening can route
through API Gateway → Lambda → S3 as shown above — see
`backend/app/aws/api_gateway_config.md`.

## Folder Structure

```
AI-Resume-Screening-System/
├── frontend/         React + Vite app (pages, components, styles, services)
├── backend/          FastAPI app (models, routes, services, aws/, utils)
├── aws/              Deployable Lambda function + S3/API Gateway setup docs
├── database/         schema.sql (MySQL tables + sample data)
├── README.md
└── .gitignore
```

## AI/NLP Workflow

1. Extract raw text from the uploaded resume (`pdfplumber` / `python-docx`)
2. Extract name, email, phone via regex heuristics
3. Extract skills, education keywords and stated years of experience
   against a curated vocabulary (`services/skill_extractor.py`)
4. Parse the job description into required skills + keyword set
   (`services/job_analyzer.py`)
5. Compute 4 sub-scores and combine them into a final weighted score
   (`services/matching_engine.py`):

   ```
   Final Score = (Skill Match × 0.50)
               + (Experience Match × 0.20)
               + (Education Match × 0.15)
               + (Keyword/JD Match × 0.15)
   ```

   Weights live in `matching_engine.WEIGHTS` — change them in one
   place to re-tune scoring.
6. Status is derived from the score: ≥70 → Shortlisted, ≥40 → Pending,
   below → Rejected.
7. `services/ranking_engine.py` sorts candidates per job by score.

This logic is intentionally rule-based and explainable (suited for a
viva) but modular — swap `matching_engine.calculate_match()` for an
ML/embeddings model later without touching routes or the frontend.

## Local Setup

### 1. MySQL

```bash
mysql -u root -p < database/schema.sql
```

Or let the backend auto-create tables on first run (see below).

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # edit DB credentials
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

## Environment Variables

See `backend/.env.example`:

```
DATABASE_URL / MYSQL_HOST / MYSQL_PORT / MYSQL_USER / MYSQL_PASSWORD / MYSQL_DATABASE
AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_REGION / AWS_S3_BUCKET / LAMBDA_FUNCTION_NAME
JWT_SECRET
```

Never commit a real `.env` file — only `.env.example` is tracked. The backend requirements pin `bcrypt==4.3.0` for compatibility with the included Passlib setup.

## AWS Setup (optional — for cloud deployment)

- **S3**: `aws/s3/README.md` — bucket creation, IAM policy, presigned URLs
- **Lambda**: `aws/lambda/resume_processor/lambda_function.py` — deployable
  resume-processing function (S3 → text extraction → NLP → matching score)
- **API Gateway**: `aws/api-gateway/README.md` and
  `backend/app/aws/api_gateway_config.md` — full route-to-integration mapping

The app runs fully without AWS for local development and demos.

## API Endpoints

```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/resumes/upload
GET    /api/resumes
GET    /api/resumes/{id}
POST   /api/jobs
GET    /api/jobs
GET    /api/jobs/{id}
POST   /api/screening/analyze
GET    /api/candidates
GET    /api/candidates/{id}
GET    /api/ranking/{job_id}
```

## Future Enhancements

- Replace keyword-based NLP with a transformer/embeddings model
- Add resume file preview/download via S3 presigned URLs in the UI
- Bulk resume upload + batch screening
- Email notifications on shortlisting
- Role-based access control (admin vs. recruiter)
