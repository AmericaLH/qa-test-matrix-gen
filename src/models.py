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
    sql_fixture: str | None = None  # suggested INSERT / seed SQL


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
