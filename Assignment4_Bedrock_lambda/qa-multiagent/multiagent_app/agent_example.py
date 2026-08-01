"""AgentCore Runtime hosting a LangChain multi-agent UAT assistant.

Architecture (all deployed together as ONE AgentCore Runtime agent):
  Main supervisor agent
    -> UAT retrieval agent tool -> your existing RAG bot (API Gateway + Lambda + Bedrock KB)
    -> Test coverage agent tool -> same RAG bot
    -> Defect triage agent tool -> same RAG bot

All three specialist agents share one tool that calls your existing RAG bot
API. Each agent asks it different kinds of questions depending on its role.
"""

import json
import logging
import os

import requests
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_aws import ChatBedrockConverse

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()

AWS_REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "ap-south-1"))
MODEL_ID = os.getenv("MODEL_ID", "amazon.nova-lite-v1:0")
RAG_API_URL = os.getenv("RAG_API_URL", "https://mlj4rlxl58.execute-api.ap-south-1.amazonaws.com/newstage")

model = ChatBedrockConverse(
    model_id=MODEL_ID,
    region_name=AWS_REGION,
    temperature=0.1,
    max_tokens=900,
)


@tool
def search_uat_documents(query: str) -> str:
    """Search the UAT knowledge base (your existing RAG bot) for test cases,
    requirements, results, defects, and sign-off criteria."""
    try:
        resp = requests.post(RAG_API_URL, json={"question": query}, timeout=30)
        resp.raise_for_status()
        body = resp.json()
        # Your Lambda returns {"answer": "...", ...} sometimes double-encoded as a string body
        if isinstance(body, str):
            body = json.loads(body)
        answer = body.get("answer", "")
        return answer if answer else "No matching evidence was found in the UAT knowledge base."
    except Exception as exc:
        logger.exception("RAG bot call failed")
        return f"UAT knowledge base lookup failed: {exc}"


def _last_content(result) -> str:
    content = result["messages"][-1].content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )
    return str(content)


retrieval_agent = create_agent(
    model=model,
    tools=[search_uat_documents],
    name="uat_retrieval_agent",
    system_prompt=(
        "You are a UAT document retrieval specialist. Always search the UAT "
        "knowledge base before answering. Return only claims supported by the "
        "retrieved text. If evidence is missing, say so explicitly."
    ),
)

coverage_agent = create_agent(
    model=model,
    tools=[search_uat_documents],
    name="uat_coverage_agent",
    system_prompt=(
        "You are a senior UAT test analyst. Search the UAT knowledge base, then "
        "evaluate scenario coverage, acceptance criteria, dependencies, evidence, "
        "and missing tests."
    ),
)

defect_agent = create_agent(
    model=model,
    tools=[search_uat_documents],
    name="uat_defect_agent",
    system_prompt=(
        "You are a UAT defect triage specialist. Search the UAT knowledge base, "
        "then assess severity, business impact, reproducibility, workarounds, "
        "retest status, and release risk. Do not invent defect records."
    ),
)


@tool("ask_uat_retrieval_agent")
def ask_uat_retrieval_agent(question: str) -> str:
    """Delegate evidence-based questions about UAT requirements, cases, outcomes, and sign-off."""
    result = retrieval_agent.invoke({"messages": [{"role": "user", "content": question}]})
    return _last_content(result)


@tool("ask_uat_coverage_agent")
def ask_uat_coverage_agent(question: str) -> str:
    """Delegate test-coverage, acceptance-criteria, gap-analysis, and readiness assessments."""
    result = coverage_agent.invoke({"messages": [{"role": "user", "content": question}]})
    return _last_content(result)


@tool("ask_uat_defect_agent")
def ask_uat_defect_agent(question: str) -> str:
    """Delegate defect triage, severity, business impact, retest, and release-risk questions."""
    result = defect_agent.invoke({"messages": [{"role": "user", "content": question}]})
    return _last_content(result)


supervisor_agent = create_agent(
    model=model,
    tools=[ask_uat_retrieval_agent, ask_uat_coverage_agent, ask_uat_defect_agent],
    name="uat_supervisor_agent",
    system_prompt=(
        "You are the main UAT supervisor. Answer only using the UAT knowledge "
        "base. Delegate factual retrieval to ask_uat_retrieval_agent, "
        "coverage/readiness analysis to ask_uat_coverage_agent, and "
        "defect/release-risk analysis to ask_uat_defect_agent. You may call "
        "multiple specialists. If the knowledge base does not contain enough "
        "evidence, state that clearly rather than relying on general knowledge."
    ),
)


@app.entrypoint
def invoke(payload, context=None):
    """AgentCore entry point. Expected payload: {"prompt": "..."}."""
    prompt = str(payload.get("prompt", "")).strip() if isinstance(payload, dict) else ""
    if not prompt:
        return {"error": "Payload must contain a non-empty 'prompt'."}

    try:
        result = supervisor_agent.invoke({"messages": [{"role": "user", "content": prompt}]})
        return {"result": _last_content(result), "model_id": MODEL_ID, "region": AWS_REGION}
    except Exception:
        logger.exception("UAT multi-agent workflow failed")
        return {"error": "The UAT multi-agent workflow failed."}


if __name__ == "__main__":
    app.run()



