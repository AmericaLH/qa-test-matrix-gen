from enum import Enum
from pydantic import BaseModel


class TestType(str, Enum):
    HAPPY_PATH = "happy_path"
    NEGATIVE = "negative"
    BOUNDARY = "boundary"
    DATA_PERMUTATION = "data_permutation"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"


class TestCase(BaseModel):
    id: str                        # e.g. TC-001
    title: str
    type: TestType
    preconditions: list[str]
    steps: list[str]
    expected_result: str
    glean_prompt: str | None = None  # prompt to search in Glean for test data setup


class Checklist(BaseModel):
    ticket_key: str
    ticket_summary: str
    items: list[str]   # one entry per Jira checklist row

    def to_text(self) -> str:
        """Plain text ready to paste into Jira's Checklist field."""
        return "\n".join(self.items)


class TestMatrix(BaseModel):
    ticket_key: str
    ticket_summary: str
    test_cases: list[TestCase]

    @property
    def by_type(self) -> dict[TestType, list[TestCase]]:
        result: dict[TestType, list[TestCase]] = {}
        for tc in self.test_cases:
            result.setdefault(tc.type, []).append(tc)
        return result
