import json
from unittest.mock import MagicMock, patch

from src.matrix_generator import generate_matrix
from src.models import TestType

FAKE_RESPONSE = {
    "test_cases": [
        {
            "id": "TC-001",
            "title": "Login with valid credentials",
            "type": "happy_path",
            "preconditions": ["User account exists"],
            "steps": ["Open login page", "Enter valid credentials", "Click Login"],
            "expected_result": "User is redirected to dashboard",
            "sql_fixture": "INSERT INTO users (email) VALUES ('test@example.com');",
        },
        {
            "id": "TC-002",
            "title": "Login with wrong password",
            "type": "negative",
            "preconditions": ["User account exists"],
            "steps": ["Open login page", "Enter wrong password", "Click Login"],
            "expected_result": "Error message is shown",
            "sql_fixture": None,
        },
        {
            "id": "TC-003",
            "title": "Tab through login form",
            "type": "accessibility",
            "preconditions": [],
            "steps": ["Open login page", "Press Tab repeatedly"],
            "expected_result": "All fields are reachable via keyboard",
            "sql_fixture": None,
        },
    ]
}


def _make_mock_client(wrap_in_fences=False):
    text = json.dumps(FAKE_RESPONSE)
    if wrap_in_fences:
        text = f"```json\n{text}\n```"
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=text)]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message
    return mock_client


TICKET_TEXT = "Summary: Login feature\n\nDescription:\nAllow users to log in."


def test_generate_matrix_returns_correct_ticket_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("src.matrix_generator.anthropic.Anthropic", return_value=_make_mock_client()):
        matrix = generate_matrix("PROJ-1", TICKET_TEXT)

    assert matrix.ticket_key == "PROJ-1"


def test_generate_matrix_test_case_count(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("src.matrix_generator.anthropic.Anthropic", return_value=_make_mock_client()):
        matrix = generate_matrix("PROJ-1", TICKET_TEXT)

    assert len(matrix.test_cases) == 3


def test_generate_matrix_types_are_parsed(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("src.matrix_generator.anthropic.Anthropic", return_value=_make_mock_client()):
        matrix = generate_matrix("PROJ-1", TICKET_TEXT)

    types = {tc.type for tc in matrix.test_cases}
    assert TestType.HAPPY_PATH in types
    assert TestType.NEGATIVE in types
    assert TestType.ACCESSIBILITY in types


def test_generate_matrix_sql_fixture_present_when_provided(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("src.matrix_generator.anthropic.Anthropic", return_value=_make_mock_client()):
        matrix = generate_matrix("PROJ-1", TICKET_TEXT)

    happy = next(tc for tc in matrix.test_cases if tc.type == TestType.HAPPY_PATH)
    assert happy.sql_fixture is not None
    assert "INSERT" in happy.sql_fixture


def test_generate_matrix_passes_ticket_text_to_claude(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_client = _make_mock_client()
    with patch("src.matrix_generator.anthropic.Anthropic", return_value=mock_client):
        generate_matrix("PROJ-99", "Summary: Checkout flow\n\nDescription:\nUser can complete purchase.")

    call_args = mock_client.messages.create.call_args
    user_message = call_args.kwargs["messages"][0]["content"]
    assert "Checkout flow" in user_message


def test_generate_matrix_handles_markdown_fences(monkeypatch):
    """Claude sometimes wraps JSON in ```json fences — must be stripped before parsing."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("src.matrix_generator.anthropic.Anthropic", return_value=_make_mock_client(wrap_in_fences=True)):
        matrix = generate_matrix("PROJ-1", TICKET_TEXT)

    assert len(matrix.test_cases) == 3
