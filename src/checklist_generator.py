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

AUTOMATABLE_SYSTEM_PROMPT = """You are a senior QA engineer and automation specialist. Given a Jira ticket, generate a checklist containing ONLY test checks that are suitable for automated testing.

Include checks that are:
- Deterministic — same input always produces same output
- Repeatable — can run reliably in a CI pipeline without human intervention
- High or medium impact — cover critical paths, common errors, or boundary conditions

Omit checks that:
- Require human visual judgment (e.g. layout looks correct, colours match)
- Are exploratory or session-based
- Have low impact or are unlikely to catch real regressions
- Depend on external systems that cannot be mocked or controlled

Each item must be written as a concrete, automatable action. Mention the expected outcome.

Return ONLY valid JSON (no markdown fences):
{
  "items": ["check one", "check two", ...]
}"""


def generate_checklist(
    ticket_key: str,
    ticket_text: str,
    automatable_only: bool = False,
) -> Checklist:
    """Generate a flat checklist from a Jira ticket using the best available model.

    Args:
        ticket_key: Jira ticket key, e.g. PROJECT-123
        ticket_text: Plain text extracted from the Jira ticket
        automatable_only: When True, only include checks suitable for automation
    """
    system = AUTOMATABLE_SYSTEM_PROMPT if automatable_only else SYSTEM_PROMPT

    raw = call_model(
        system=system,
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
