import json
from dotenv import load_dotenv

from .ai_client import call_model
from .models import Checklist

load_dotenv()

SYSTEM_PROMPT = """You are a senior QA engineer. Given a Jira ticket, generate a concise test checklist.

Each item must be:
- A single, self-contained test check written as an action to verify
- Short enough to read at a glance (one line)
- Written in plain language a developer or QA can act on immediately

Cover all relevant angles:
- Core happy paths
- Key negative / error scenarios
- Boundary and edge cases
- UI / accessibility basics (if the ticket touches the UI)

Return ONLY valid JSON (no markdown fences):
{
  "items": ["check one", "check two", ...]
}"""


def generate_checklist(ticket_key: str, ticket_text: str) -> Checklist:
    """Generate a flat checklist from a Jira ticket using the best available model."""
    raw = call_model(
        system=SYSTEM_PROMPT,
        user_content=f"Generate a test checklist for this Jira ticket:\n\n{ticket_text}",
        max_tokens=1024,
    )

    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.rsplit("```", 1)[0].strip()

    data = json.loads(raw)
    summary = ticket_text.splitlines()[0].replace("Summary: ", "").strip()

    return Checklist(ticket_key=ticket_key, ticket_summary=summary, items=data["items"])
