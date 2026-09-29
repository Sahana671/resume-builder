# API Gateway Setup

Full route-to-integration mapping lives in
`backend/app/aws/api_gateway_config.md`. Summary steps to deploy:

## 1. Create the HTTP API

```
aws apigatewayv2 create-api \
  --name ai-resume-screening-api \
  --protocol-type HTTP
```

## 2. Add routes

For every endpoint listed in `api_gateway_config.md`, create a route
and an integration:

- **Lambda-backed routes** (`/api/resumes/upload`,
  `/api/screening/analyze`): integration type `AWS_PROXY`, pointing
  at the `resume-processor` Lambda ARN.
- **FastAPI-backed routes** (everything else): integration type
  `HTTP_PROXY`, pointing at your FastAPI deployment's base URL.

## 3. Enable CORS

```
aws apigatewayv2 update-api \
  --api-id <API_ID> \
  --cors-configuration AllowOrigins="*",AllowMethods="GET,POST,PUT,DELETE,OPTIONS",AllowHeaders="*"
```

Restrict `AllowOrigins` to your deployed frontend's domain in production.

## 4. Deploy a stage

```
aws apigatewayv2 create-stage --api-id <API_ID> --stage-name prod --auto-deploy
```

This gives an invoke URL like:
`https://xxxxxx.execute-api.ap-south-1.amazonaws.com/prod`

## 5. Point the frontend at it

In `frontend/.env`:

```
VITE_API_BASE_URL=https://xxxxxx.execute-api.ap-south-1.amazonaws.com/prod
```

## Local development

None of this is required to run the project locally — the React
frontend simply talks to `http://localhost:8000` (FastAPI) directly.
