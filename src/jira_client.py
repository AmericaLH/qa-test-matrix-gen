import os
import httpx
from dotenv import load_dotenv

from .models import JiraTicket

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

    def parse_ticket(self, raw: dict) -> JiraTicket:
        """Normalize a raw Jira API response into a JiraTicket model."""
        fields = raw.get("fields", {})
        summary = fields.get("summary", "")
        description = _adf_to_text(fields.get("description") or {})

        raw_ac = fields.get("customfield_acceptance_criteria") or []
        if isinstance(raw_ac, list):
            acceptance_criteria = [str(item) for item in raw_ac if item]
        else:
            ac_text = _adf_to_text(raw_ac)
            acceptance_criteria = [line.lstrip("- ").strip() for line in ac_text.splitlines() if line.strip()]

        return JiraTicket(
            key=raw.get("key", ""),
            summary=summary,
            description=description,
            acceptance_criteria=acceptance_criteria,
        )

    def extract_text(self, ticket: dict) -> str:
        """Pull summary + description + acceptance criteria from a Jira issue dict."""
        parsed = self.parse_ticket(ticket)
        parts = [f"Summary: {parsed.summary}"]
        if parsed.description:
            parts.append(f"Description:\n{parsed.description}")
        if parsed.acceptance_criteria:
            ac_lines = "\n".join(f"- {item}" for item in parsed.acceptance_criteria)
            parts.append(f"Acceptance Criteria:\n{ac_lines}")
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
