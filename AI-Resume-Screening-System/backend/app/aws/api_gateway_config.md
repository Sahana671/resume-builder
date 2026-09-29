# API Gateway ↔ Backend Mapping

This backend is designed so every FastAPI route can be exposed
through Amazon API Gateway, either as:

- **HTTP passthrough** to this FastAPI app running on EC2/ECS/App Runner, or
- **Lambda proxy integration**, where API Gateway invokes AWS Lambda
  functions directly (e.g. the `resume-processor` function in
  `/aws/lambda/resume_processor/lambda_function.py` for the upload +
  screening flow).

## Route Map

| Method | Path                        | Integration                          |
|--------|-----------------------------|---------------------------------------|
| POST   | /api/auth/register          | FastAPI (`routes/auth.py`)            |
| POST   | /api/auth/login             | FastAPI (`routes/auth.py`)            |
| POST   | /api/resumes/upload         | Lambda proxy → `resume-processor`     |
| GET    | /api/resumes                | FastAPI (`routes/resume.py`)          |
| GET    | /api/resumes/{id}           | FastAPI (`routes/resume.py`)          |
| POST   | /api/jobs                   | FastAPI (`routes/jobs.py`)            |
| GET    | /api/jobs                   | FastAPI (`routes/jobs.py`)            |
| GET    | /api/jobs/{id}               | FastAPI (`routes/jobs.py`)            |
| POST   | /api/screening/analyze      | Lambda proxy → `resume-processor`     |
| GET    | /api/candidates             | FastAPI (`routes/candidates.py`)      |
| GET    | /api/candidates/{id}        | FastAPI (`routes/candidates.py`)      |
| GET    | /api/ranking/{job_id}       | FastAPI (`routes/ranking.py`)         |

## Recommended Setup (HTTP API, cheaper than REST API)

1. Create an **HTTP API** in API Gateway named `ai-resume-screening-api`.
2. Add a route for each path above.
3. For the two AI-heavy routes (`/api/resumes/upload`,
   `/api/screening/analyze`), use a **Lambda proxy integration**
   pointing at the `resume-processor` function.
4. For all other routes, use an **HTTP proxy integration** pointing
   at your FastAPI deployment's base URL (e.g. an ALB or App Runner
   endpoint), or run everything through FastAPI locally/on EC2 and
   skip Lambda entirely — the app works either way.
5. Enable **CORS** on the API for your frontend's origin.
6. (Optional) Add a **JWT authorizer** using the same `JWT_SECRET`
   used by the backend, so API Gateway can reject unauthenticated
   requests before they reach Lambda/FastAPI.
7. Deploy a stage, e.g. `prod`, giving an invoke URL such as:
   `https://xxxxxx.execute-api.ap-south-1.amazonaws.com/prod`
8. Set `VITE_API_BASE_URL` in the frontend's `.env` to that invoke URL.

## Local Development

None of this is required locally. `uvicorn app.main:app --reload`
runs the full API on `http://localhost:8000` and the NLP/matching
logic executes in-process — API Gateway and Lambda are only used
when deploying to AWS.
