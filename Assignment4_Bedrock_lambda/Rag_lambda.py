"""
AWS Lambda RAG Handler
----------------------

Flow:
1. Retrieve relevant chunks from Bedrock Knowledge Base
2. Build grounded context
3. Generate answer using Llama 3 via Converse API
4. Return answer with source information

Environment Variables:
----------------------
KNOWLEDGE_BASE_ID
MODEL_ID
NUMBER_OF_RESULTS
MAX_CONTEXT_CHARS
"""

import base64
import json
import os

import boto3
from botocore.exceptions import ClientError, BotoCoreError

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

KNOWLEDGE_BASE_ID = os.getenv("KNOWLEDGE_BASE_ID", "BD4V95U7UE")

MODEL_ID = os.getenv(
    "MODEL_ID",
    "meta.llama3-8b-instruct-v1:0"
)

NUMBER_OF_RESULTS = int(
    os.getenv("NUMBER_OF_RESULTS", "5")
)

MAX_CONTEXT_CHARS = int(
    os.getenv("MAX_CONTEXT_CHARS", "15000")
)

# -----------------------------------------------------------------------------
# AWS Clients
# -----------------------------------------------------------------------------

agent_runtime = boto3.client("bedrock-agent-runtime")
bedrock_runtime = boto3.client("bedrock-runtime")

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def create_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body, default=str)
    }


def parse_request(event):
    """
    Supports:
    - API Gateway
    - Lambda direct invocation
    """

    if not isinstance(event, dict):
        return {}

    body = event.get("body")

    if body is None:
        return event

    if event.get("isBase64Encoded") and isinstance(body, str):
        body = base64.b64decode(body).decode("utf-8")

    if isinstance(body, str):
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {"question": body}

    return body if isinstance(body, dict) else {}


def extract_location(location):
    """
    Extract human-readable source location.
    """

    if not location:
        return None

    location_type = location.get("type")

    mapping = {
        "S3": "s3Location",
        "WEB": "webLocation",
        "CONFLUENCE": "confluenceLocation",
        "SALESFORCE": "salesforceLocation",
        "SHAREPOINT": "sharePointLocation",
        "CUSTOM": "customDocumentLocation",
        "KENDRA": "kendraDocumentLocation",
        "SQL": "sqlLocation",
    }

    details = location.get(
        mapping.get(location_type, ""),
        {}
    )

    return (
        details.get("url")
        or details.get("uri")
        or details.get("key")
        or details.get("id")
        or location_type
    )


def retrieve_documents(question):
    """
    Retrieve chunks from Knowledge Base.
    """

    response = agent_runtime.retrieve(
        knowledgeBaseId=KNOWLEDGE_BASE_ID,
        retrievalQuery={
            "text": question
        },
        retrievalConfiguration={
            "vectorSearchConfiguration": {
                "numberOfResults": NUMBER_OF_RESULTS
            }
        }
    )

    return response.get("retrievalResults", [])


def build_context(results):
    """
    Build context string and source metadata.
    """

    context_parts = []
    sources = []

    for idx, result in enumerate(results, start=1):

        text = (
            result.get("content", {})
            .get("text", "")
            .strip()
        )

        if not text:
            continue

        context_parts.append(
            f"[Source {idx}]\n{text}"
        )

        sources.append({
            "source": idx,
            "location": extract_location(
                result.get("location", {})
            ),
            "score": result.get("score")
        })

    context = "\n\n".join(context_parts)

    if len(context) > MAX_CONTEXT_CHARS:
        context = context[:MAX_CONTEXT_CHARS]

    return context, sources


def build_prompt(question, context):
    return f"""
You are a UAT and QA Testing Knowledge Assistant.

Rules:
1. Answer ONLY from the provided context.
2. Do NOT use outside knowledge.
3. If the answer is not available, respond:
   "The knowledge base does not contain enough information."
4. Cite sources as [Source N].
5. Keep responses concise and factual.
6. If multiple sources support the answer, cite all relevant sources.

QUESTION:
{question}

CONTEXT:
{context}
"""


def generate_answer(question, context):

    prompt = build_prompt(question, context)

    response = bedrock_runtime.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        inferenceConfig={
            "temperature": 0.1,
            "maxTokens": 700
        }
    )

    answer = "".join(
        part.get("text", "")
        for part in response["output"]["message"]["content"]
        if "text" in part
    )

    return answer, response.get("usage", {})


# -----------------------------------------------------------------------------
# Lambda Entry Point
# -----------------------------------------------------------------------------

def lambda_handler(event, context):

    try:
        request = parse_request(event)

        question = str(
            request.get("question")
            or request.get("prompt")
            or ""
        ).strip()

        if not question:
            return create_response(
                400,
                {
                    "error": "Provide a non-empty 'question'."
                }
            )

        # ---------------------------------------------------------------------
        # Retrieval
        # ---------------------------------------------------------------------

        results = retrieve_documents(question)

        if not results:
            return create_response(
                200,
                {
                    "answer": "No relevant information was found in the knowledge base.",
                    "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                    "sources": []
                }
            )

        # ---------------------------------------------------------------------
        # Build Context
        # ---------------------------------------------------------------------

        kb_context, sources = build_context(results)

        if not kb_context:
            return create_response(
                200,
                {
                    "answer": "No usable content was retrieved from the knowledge base.",
                    "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                    "sources": []
                }
            )

        # ---------------------------------------------------------------------
        # Generation
        # ---------------------------------------------------------------------

        answer, usage = generate_answer(
            question,
            kb_context
        )

        return create_response(
            200,
            {
                "answer": answer,
                "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                "modelId": MODEL_ID,
                "sources": sources,
                "usage": usage
            }
        )

    except (ClientError, BotoCoreError) as error:

        if isinstance(error, ClientError):
            details = error.response.get("Error", {})
            code = details.get("Code", "ClientError")
            message = details.get("Message", str(error))
        else:
            code = type(error).__name__
            message = str(error)

        return create_response(
            500,
            {
                "error": code,
                "message": message
            }
        )

    except Exception as error:

        return create_response(
            500,
            {
                "error": "UnexpectedError",
                "message": str(error)
            }
        )