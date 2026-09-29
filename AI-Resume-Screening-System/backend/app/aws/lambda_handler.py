"""
lambda_handler.py
--------------------
Backend-side helper for invoking the deployed AWS Lambda function
(see /aws/lambda/resume_processor/lambda_function.py) that performs
resume text extraction + NLP screening inside AWS.

This lets the FastAPI backend optionally offload the heavy
extraction/matching work to Lambda in a cloud deployment, instead of
running services/resume_parser.py + matching_engine.py in-process.

Architecture:
    React Frontend -> API Gateway -> AWS Lambda -> S3 -> NLP -> MySQL

Locally, the FastAPI app calls the same NLP services directly
in-process (see routes/candidates.py), so the app works fully
without AWS. In production this module can be used to trigger the
Lambda instead, keeping the request/response contract identical.
"""

import os
import json

try:
    import boto3
except ImportError:
    boto3 = None

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
LAMBDA_FUNCTION_NAME = os.getenv("LAMBDA_FUNCTION_NAME", "resume-processor")


def _get_lambda_client():
    if boto3 is None:
        raise RuntimeError("boto3 is not installed. Run: pip install boto3")
    return boto3.client("lambda", region_name=AWS_REGION)


def invoke_resume_processor(s3_bucket: str, s3_key: str, job_data: dict) -> dict:
    """
    Synchronously invoke the resume_processor Lambda function.

    payload matches what `aws/lambda/resume_processor/lambda_function.py`
    expects in its `event` argument.
    """
    lambda_client = _get_lambda_client()

    payload = {
        "s3_bucket": s3_bucket,
        "s3_key": s3_key,
        "job": job_data,
    }

    response = lambda_client.invoke(
        FunctionName=LAMBDA_FUNCTION_NAME,
        InvocationType="RequestResponse",  # synchronous
        Payload=json.dumps(payload).encode("utf-8"),
    )

    result_payload = json.loads(response["Payload"].read())
    return result_payload
