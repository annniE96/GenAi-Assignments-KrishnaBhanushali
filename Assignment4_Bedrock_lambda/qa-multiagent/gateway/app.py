"""
Public API Gateway for the UAT multi-agent system.
----------------------------------------------------
Runs on ECS Fargate. Its only job: accept public HTTP requests and forward
them to the multi-agent app deployed on Bedrock AgentCore Runtime.

Required environment variables (set in the ECS task definition):
- AGENT_RUNTIME_ARN : the agentRuntimeArn printed by `agentcore launch`
                       for multiagent_app/agent_example.py
- AWS_REGION : e.g. ap-south-1
"""

import json
import os
import uuid

import boto3
from fastapi import FastAPI
from pydantic import BaseModel

AGENT_RUNTIME_ARN = os.environ["AGENT_RUNTIME_ARN"]
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")

agentcore_client = boto3.client("bedrock-agentcore", region_name=AWS_REGION)

app = FastAPI(title="UAT Multi-Agent Gateway")


class QueryRequest(BaseModel):
    question: str


@app.post("/query")
def query(req: QueryRequest):
    # runtimeSessionId must be at least 33 characters
    session_id = f"{uuid.uuid4()}-{uuid.uuid4()}"
    payload = json.dumps({"prompt": req.question}).encode()

    response = agentcore_client.invoke_agent_runtime(
        agentRuntimeArn=AGENT_RUNTIME_ARN,
        runtimeSessionId=session_id,
        payload=payload,
    )
    body = response["response"].read()
    return json.loads(body)


@app.get("/health")
def health():
    return {"status": "ok"}

