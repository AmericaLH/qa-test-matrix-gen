import anthropic
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from src.cli import cli, _retry_message


# --- _retry_message unit tests ---

def _rate_limit_error(headers: dict) -> anthropic.RateLimitError:
    response = MagicMock()
    response.headers = headers
    return anthropic.RateLimitError(
        message="rate limit exceeded", response=response, body={}
    )


def test_retry_message_with_seconds():
    exc = _rate_limit_error({"retry-after": "45"})
    msg = _retry_message(exc)
    assert "45 seconds" in msg


def test_retry_message_with_minutes():
    exc = _rate_limit_error({"retry-after": "120"})
    msg = _retry_message(exc)
    assert "2 minute" in msg


def test_retry_message_with_hours():
    exc = _rate_limit_error({"retry-after": "7200"})
    msg = _retry_message(exc)
    assert "2 hour" in msg


def test_retry_message_falls_back_to_reset_headers():
    exc = _rate_limit_error({"x-ratelimit-reset-requests": "2026-04-13T10:00:00Z"})
    msg = _retry_message(exc)
    assert "2026-04-13" in msg


def test_retry_message_falls_back_to_console_link():
    exc = _rate_limit_error({})
    msg = _retry_message(exc)
    assert "console.anthropic.com" in msg


# --- CLI integration tests ---

def test_generate_shows_rate_limit_message(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    response = MagicMock()
    response.headers = {"retry-after": "60"}

    with patch("src.matrix_generator.anthropic.Anthropic") as mock_cls:
        mock_cls.return_value.messages.create.side_effect = anthropic.RateLimitError(
            message="rate limit", response=response, body={}
        )
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "--from-file", "tests/fixtures/sample_ticket.json"])

    assert result.exit_code != 0
    assert "rate limit" in result.output.lower()
    assert "1 minute" in result.output


def test_generate_shows_auth_error_message(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "bad-key")

    with patch("src.matrix_generator.anthropic.Anthropic") as mock_cls:
        mock_cls.return_value.messages.create.side_effect = anthropic.AuthenticationError(
            message="invalid key", response=MagicMock(headers={}), body={}
        )
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "--from-file", "tests/fixtures/sample_ticket.json"])

    assert result.exit_code != 0
    assert "ANTHROPIC_API_KEY" in result.output
