import json
from dotenv import load_dotenv

from .ai_client import call_model
from .models import TestCase, TestMatrix

load_dotenv()

SYSTEM_PROMPT = """You are a senior QA engineer. Given a Jira ticket, you generate a comprehensive test matrix.

When "Acceptance Criteria" are provided, each criterion MUST be covered by at least one test case. Use them to anchor the happy-path and negative scenarios.

For each test case, produce:
- id: sequential string like "TC-001"
- title: short, descriptive
- type: one of happy_path | negative | boundary | data_permutation | accessibility | performance
- preconditions: list of setup steps
- steps: list of test steps
- expected_result: what success looks like
- glean_prompt: a short natural-language search prompt the QA engineer can paste into
  Glean to find the internal documentation, schema, or existing test data needed to
  set up this test case. Focus on what data needs to exist. Example:
  "users table schema and seed data for inactive account"
  Set to null if no specific data setup is needed.
- automation: assess whether this test case is a good candidate for automation:
    - suitable: true if the test is deterministic, repeatable, and does not require
      human judgment. false for exploratory, visual, or subjective checks.
    - reason: one sentence explaining the assessment
    - suggested_tool: the most appropriate tool (e.g. Playwright, pytest, Postman,
      RestAssured) or null if not suitable

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


def generate_matrix(
    ticket_key: str,
    ticket_text: str,
    automatable_only: bool = False,
) -> TestMatrix:
    """Generate a test matrix from a Jira ticket using the best available model.

    Args:
        ticket_key: Jira ticket key, e.g. PROJECT-123
        ticket_text: Plain text extracted from the Jira ticket
        automatable_only: When True, omit test cases that are not suitable for automation
    """
    raw = call_model(
        system=SYSTEM_PROMPT,
        user_content=f"Generate a test matrix for this Jira ticket:\n\n{ticket_text}",
        max_tokens=8192,
    )

    raw = _strip_fences(raw)
    data = json.loads(raw)
    test_cases = [TestCase(**tc) for tc in data["test_cases"]]

    if automatable_only:
        test_cases = [
            tc for tc in test_cases
            if tc.automation and tc.automation.suitable
        ]

    summary = ticket_text.splitlines()[0].replace("Summary: ", "").strip()
    return TestMatrix(ticket_key=ticket_key, ticket_summary=summary, test_cases=test_cases)


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0].strip()
    return text
