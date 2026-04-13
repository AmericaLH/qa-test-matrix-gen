import json
import os
import anthropic
from dotenv import load_dotenv

from .models import Checklist

load_dotenv()

MODEL = "claude-sonnet-4-6"

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
    """Call Claude to produce a flat checklist from a Jira ticket's text."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Generate a test checklist for this Jira ticket:\n\n{ticket_text}",
            }
        ],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.rsplit("```", 1)[0].strip()

    data = json.loads(raw)

    summary_line = ticket_text.splitlines()[0]
    summary = summary_line.replace("Summary: ", "").strip()

    return Checklist(
        ticket_key=ticket_key,
        ticket_summary=summary,
        items=data["items"],
    )
