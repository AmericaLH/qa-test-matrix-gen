import os
import httpx
from dotenv import load_dotenv

load_dotenv()


class JiraClient:
    """Thin wrapper around the Jira REST API v3."""

    def __init__(self) -> None:
        self.base_url = os.environ["JIRA_BASE_URL"].rstrip("/")
        self.auth = (os.environ["JIRA_EMAIL"], os.environ["JIRA_API_TOKEN"])
        self._client = httpx.Client(auth=self.auth, timeout=15)

    def get_ticket(self, ticket_key: str) -> dict:
        """Fetch a Jira issue and return the raw JSON."""
        url = f"{self.base_url}/rest/api/3/issue/{ticket_key}"
        response = self._client.get(url)
        response.raise_for_status()
        return response.json()

    def extract_text(self, ticket: dict) -> str:
        """Pull summary + description text from a Jira issue dict."""
        fields = ticket.get("fields", {})
        summary = fields.get("summary", "")
        description = _adf_to_text(fields.get("description") or {})
        acceptance = _adf_to_text(
            fields.get("customfield_acceptance_criteria") or {}
        )
        parts = [f"Summary: {summary}"]
        if description:
            parts.append(f"Description:\n{description}")
        if acceptance:
            parts.append(f"Acceptance Criteria:\n{acceptance}")
        return "\n\n".join(parts)


def _adf_to_text(node: dict) -> str:
    """Recursively extract plain text from Atlassian Document Format (ADF)."""
    if not node:
        return ""
    node_type = node.get("type", "")
    text = node.get("text", "")
    children = node.get("content", [])

    parts = [text] if text else []
    for child in children:
        parts.append(_adf_to_text(child))

    separator = "\n" if node_type in ("paragraph", "listItem", "heading") else ""
    return separator.join(filter(None, parts))
