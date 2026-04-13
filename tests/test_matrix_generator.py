import json
from unittest.mock import patch

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
            "glean_prompt": "users table schema and seed data for valid account",
        },
        {
            "id": "TC-002",
            "title": "Login with wrong password",
            "type": "negative",
            "preconditions": ["User account exists"],
            "steps": ["Open login page", "Enter wrong password", "Click Login"],
            "expected_result": "Error message is shown",
            "glean_prompt": None,
        },
        {
            "id": "TC-003",
            "title": "Tab through login form",
            "type": "accessibility",
            "preconditions": [],
            "steps": ["Open login page", "Press Tab repeatedly"],
            "expected_result": "All fields are reachable via keyboard",
            "glean_prompt": None,
        },
    ]
}

TICKET_TEXT = "Summary: Login feature\n\nDescription:\nAllow users to log in."


def _fake_call_model(wrap_in_fences=False):
    text = json.dumps(FAKE_RESPONSE)
    if wrap_in_fences:
        text = f"```json\n{text}\n```"
    return text


def test_generate_matrix_returns_correct_ticket_key():
    with patch("src.matrix_generator.call_model", return_value=_fake_call_model()):
        matrix = generate_matrix("PROJ-1", TICKET_TEXT)
    assert matrix.ticket_key == "PROJ-1"


def test_generate_matrix_test_case_count():
    with patch("src.matrix_generator.call_model", return_value=_fake_call_model()):
        matrix = generate_matrix("PROJ-1", TICKET_TEXT)
    assert len(matrix.test_cases) == 3


def test_generate_matrix_types_are_parsed():
    with patch("src.matrix_generator.call_model", return_value=_fake_call_model()):
        matrix = generate_matrix("PROJ-1", TICKET_TEXT)
    types = {tc.type for tc in matrix.test_cases}
    assert TestType.HAPPY_PATH in types
    assert TestType.NEGATIVE in types
    assert TestType.ACCESSIBILITY in types


def test_generate_matrix_glean_prompt_present_when_provided():
    with patch("src.matrix_generator.call_model", return_value=_fake_call_model()):
        matrix = generate_matrix("PROJ-1", TICKET_TEXT)
    happy = next(tc for tc in matrix.test_cases if tc.type == TestType.HAPPY_PATH)
    assert happy.glean_prompt is not None
    assert "users" in happy.glean_prompt


def test_generate_matrix_passes_ticket_text_to_model():
    with patch("src.matrix_generator.call_model", return_value=_fake_call_model()) as mock_call:
        generate_matrix("PROJ-99", "Summary: Checkout flow\n\nDescription:\nUser can complete purchase.")
    user_content = mock_call.call_args.kwargs["user_content"]
    assert "Checkout flow" in user_content


def test_generate_matrix_handles_markdown_fences():
    with patch("src.matrix_generator.call_model", return_value=_fake_call_model(wrap_in_fences=True)):
        matrix = generate_matrix("PROJ-1", TICKET_TEXT)
    assert len(matrix.test_cases) == 3
