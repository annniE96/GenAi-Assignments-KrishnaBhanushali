# AgentCore deployment

This repo already exposes a Bedrock AgentCore runtime through `multiagent.py`.
The `app.py` wrapper is included so the runtime entrypoint is easy to reference
from build and deploy tooling.

## What this deploys

- A LangChain supervisor agent.
- Three specialist tool agents for retrieval, coverage, and defect triage.
- Retrieval grounded in the documents under `uat_documents/`.

## Runtime environment variables

Set these in AgentCore:

- `AWS_REGION` or `AWS_DEFAULT_REGION`
- `MODEL_ID`
- `UAT_DOCUMENT_DIRECTORY` if you want to override the bundled corpus path
- `LOG_LEVEL` if you want more or less logging

## Suggested deployment image

Build the container from the root of this repo. The image already includes:

- `multiagent.py`
- `app.py`
- `requirements.txt`
- `uat_documents/`

## Smoke test payload

Send a payload in this shape:

```json
{
  "prompt": "What are the UAT exit criteria and sign-off requirements?"
}
```

## Notes

- The app returns an error if no supported UAT documents are present in the
  configured document directory.
- The current corpus includes `uat_documents/UAT_RAG.txt`, so the knowledge base
  is available without converting it to PDF.