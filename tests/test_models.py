from src.models import TestCase, TestMatrix, TestType


def test_testcase_fields():
    tc = TestCase(
        id="TC-001",
        title="Login with valid credentials",
        type=TestType.HAPPY_PATH,
        preconditions=["User account exists"],
        steps=["Open login page", "Enter valid email and password", "Click Login"],
        expected_result="User is redirected to dashboard",
        sql_fixture="INSERT INTO users (email, password_hash) VALUES ('test@example.com', 'hashed');",
    )
    assert tc.type == TestType.HAPPY_PATH
    assert tc.sql_fixture is not None


def test_testmatrix_by_type():
    cases = [
        TestCase(
            id="TC-001",
            title="Happy path",
            type=TestType.HAPPY_PATH,
            preconditions=[],
            steps=["step"],
            expected_result="ok",
        ),
        TestCase(
            id="TC-002",
            title="Negative path",
            type=TestType.NEGATIVE,
            preconditions=[],
            steps=["step"],
            expected_result="error shown",
        ),
    ]
    matrix = TestMatrix(ticket_key="DEMO-1", ticket_summary="Test feature", test_cases=cases)
    grouped = matrix.by_type
    assert len(grouped[TestType.HAPPY_PATH]) == 1
    assert len(grouped[TestType.NEGATIVE]) == 1


def test_testcase_sql_fixture_optional():
    tc = TestCase(
        id="TC-003",
        title="Accessibility check",
        type=TestType.ACCESSIBILITY,
        preconditions=[],
        steps=["Tab through form"],
        expected_result="All elements are focusable",
    )
    assert tc.sql_fixture is None
