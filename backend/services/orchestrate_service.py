"""
IBM watsonx Orchestrate Service
Trigger workflows and retrieve run status via REST API
"""
import os
import time
import logging
from typing import Any, Dict, Optional
from pathlib import Path
import httpx
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

IAM_URL = "https://iam.cloud.ibm.com/identity/token"

ORCHESTRATE_BASE_URL = os.getenv("ORCHESTRATE_BASE_URL", "").rstrip("/")
ORCHESTRATE_PROJECT_ID = os.getenv("ORCHESTRATE_PROJECT_ID", "")
ORCHESTRATE_WORKFLOW_ID = os.getenv("ORCHESTRATE_WORKFLOW_ID", "")
IBM_IAM_API_KEY = os.getenv("IBM_IAM_API_KEY", os.getenv("ORCHESTRATE_IAM_API_KEY", ""))

_TOKEN: Optional[str] = None
_TOKEN_EXPIRY: Optional[float] = None


async def _get_iam_token() -> Optional[str]:
    global _TOKEN, _TOKEN_EXPIRY

    if _TOKEN and _TOKEN_EXPIRY and time.time() < _TOKEN_EXPIRY - 60:
        return _TOKEN

    if not IBM_IAM_API_KEY:
        logger.warning("IBM IAM API key not configured for Orchestrate")
        return None

    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": IBM_IAM_API_KEY,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(IAM_URL, data=data, headers=headers)
        response.raise_for_status()
        payload = response.json()

    _TOKEN = payload.get("access_token")
    expires_in = int(payload.get("expires_in", 3600))
    _TOKEN_EXPIRY = time.time() + expires_in

    return _TOKEN


def _resolve_project_workflow(
    project_id: Optional[str], workflow_id: Optional[str]
) -> tuple[str, str]:
    resolved_project = project_id or ORCHESTRATE_PROJECT_ID
    resolved_workflow = workflow_id or ORCHESTRATE_WORKFLOW_ID

    if not ORCHESTRATE_BASE_URL:
        raise ValueError("ORCHESTRATE_BASE_URL is not configured")
    if not resolved_project:
        raise ValueError("ORCHESTRATE_PROJECT_ID is not configured")
    if not resolved_workflow:
        raise ValueError("ORCHESTRATE_WORKFLOW_ID is not configured")

    return resolved_project, resolved_workflow


async def run_workflow(
    variables: Optional[Dict[str, Any]] = None,
    project_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
) -> Dict[str, Any]:
    token = await _get_iam_token()
    if not token:
        raise ValueError("IBM IAM token could not be obtained")

    resolved_project, resolved_workflow = _resolve_project_workflow(project_id, workflow_id)

    url = f"{ORCHESTRATE_BASE_URL}/v1/projects/{resolved_project}/workflows/{resolved_workflow}/runs"
    payload = {"variables": variables or {}}

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    return data


async def get_run_status(
    run_id: str,
    project_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
) -> Dict[str, Any]:
    token = await _get_iam_token()
    if not token:
        raise ValueError("IBM IAM token could not be obtained")

    resolved_project, resolved_workflow = _resolve_project_workflow(project_id, workflow_id)

    url = f"{ORCHESTRATE_BASE_URL}/v1/projects/{resolved_project}/workflows/{resolved_workflow}/runs/{run_id}"
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

    return data
