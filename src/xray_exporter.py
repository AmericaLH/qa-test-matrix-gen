import os
import httpx
from dotenv import load_dotenv

from .models import TestMatrix

load_dotenv()

XRAY_TOKEN_URL = "https://xray.cloud.getxray.app/api/v2/authenticate"
XRAY_IMPORT_URL = "https://xray.cloud.getxray.app/api/v2/import/test/bulk"


def _get_xray_token() -> str:
    response = httpx.post(
        XRAY_TOKEN_URL,
        json={
            "client_id": os.environ["XRAY_CLIENT_ID"],
            "client_secret": os.environ["XRAY_CLIENT_SECRET"],
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.text.strip('"')


def export_to_xray(matrix: TestMatrix, project_key: str) -> dict:
    """Push all test cases in a matrix to Xray as new test issues."""
    token = _get_xray_token()

    tests = []
    for tc in matrix.test_cases:
        tests.append(
            {
                "summary": f"[{tc.type.value.upper()}] {tc.title}",
                "description": (
                    "**Preconditions:**\n"
                    + "\n".join(f"- {p}" for p in tc.preconditions)
                    + "\n\n**Steps:**\n"
                    + "\n".join(f"{i+1}. {s}" for i, s in enumerate(tc.steps))
                    + f"\n\n**Expected Result:** {tc.expected_result}"
                    + (f"\n\n**Glean prompt:** `{tc.glean_prompt}`" if tc.glean_prompt else "")
                ),
                "labels": [tc.type.value, matrix.ticket_key],
                "project": {"key": project_key},
            }
        )

    response = httpx.post(
        XRAY_IMPORT_URL,
        json=tests,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
