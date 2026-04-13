import json
from unittest.mock import MagicMock, patch

from src.checklist_generator import generate_checklist

FAKE_RESPONSE = {
    "items": [
        "User can log in with valid email and password",
        "Error message appears when password is incorrect",
        "Form shows validation error when email is empty",
        "Remember me checkbox is visible and clickable",
        "Session persists for 30 days when remember me is checked",
        "Session does not persist when remember me is unchecked",
        "All form fields are reachable via keyboard",
    ]
}

TICKET_TEXT = "Summary: Login form — add Remember me checkbox\n\nDescription:\nAllow users to stay logged in."


def _make_mock_client(wrap_in_fences=False):
    text = json.dumps(FAKE_RESPONSE)
    if wrap_in_fences:
        text = f"```json\n{text}\n```"
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=text)]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message
    return mock_client


def test_generate_checklist_returns_correct_ticket_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("src.checklist_generator.anthropic.Anthropic", return_value=_make_mock_client()):
        result = generate_checklist("PROJ-1", TICKET_TEXT)

    assert result.ticket_key == "PROJ-1"


def test_generate_checklist_item_count(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("src.checklist_generator.anthropic.Anthropic", return_value=_make_mock_client()):
        result = generate_checklist("PROJ-1", TICKET_TEXT)

    assert len(result.items) == 7


def test_generate_checklist_to_text_is_one_item_per_line(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("src.checklist_generator.anthropic.Anthropic", return_value=_make_mock_client()):
        result = generate_checklist("PROJ-1", TICKET_TEXT)

    lines = result.to_text().splitlines()
    assert len(lines) == 7
    assert lines[0] == "User can log in with valid email and password"


def test_generate_checklist_handles_markdown_fences(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("src.checklist_generator.anthropic.Anthropic", return_value=_make_mock_client(wrap_in_fences=True)):
        result = generate_checklist("PROJ-1", TICKET_TEXT)

    assert len(result.items) == 7


def test_generate_checklist_extracts_summary(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("src.checklist_generator.anthropic.Anthropic", return_value=_make_mock_client()):
        result = generate_checklist("PROJ-1", TICKET_TEXT)

    assert "Remember me" in result.ticket_summary
