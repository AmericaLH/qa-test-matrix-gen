import json
import os
import anthropic
from dotenv import load_dotenv

from .models import TestCase, TestMatrix

load_dotenv()

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are a senior QA engineer. Given a Jira ticket, you generate a comprehensive test matrix.

For each test case, produce:
- id: sequential string like "TC-001"
- title: short, descriptive
- type: one of happy_path | negative | boundary | data_permutation | accessibility | performance
- preconditions: list of setup steps
- steps: list of test steps
- expected_result: what success looks like
- sql_fixture: a suggested PostgreSQL INSERT or seed query to set up test data (or null if not applicable)

Cover ALL of these dimensions:
1. Happy paths — standard successful flows
2. Negative paths — invalid inputs, unauthorized access, missing data
3. Boundary conditions — min/max values, empty strings, length limits
4. Data permutations — combinations of valid inputs that might interact
5. Accessibility — keyboard navigation, screen reader labels, color contrast
6. (Optional) Performance — large data sets or slow network if relevant

Return ONLY valid JSON matching this schema (no markdown fences):
{
  "test_cases": [ <TestCase objects> ]
}"""


def generate_matrix(ticket_key: str, ticket_text: str) -> TestMatrix:
    """Call Claude to produce a test matrix from a Jira ticket's text."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Generate a test matrix for this Jira ticket:\n\n{ticket_text}",
            }
        ],
    )

    raw = message.content[0].text
    data = json.loads(raw)

    test_cases = [TestCase(**tc) for tc in data["test_cases"]]

    # Parse ticket summary from the first line ("Summary: ...")
    summary_line = ticket_text.splitlines()[0]
    summary = summary_line.replace("Summary: ", "").strip()

    return TestMatrix(
        ticket_key=ticket_key,
        ticket_summary=summary,
        test_cases=test_cases,
    )
