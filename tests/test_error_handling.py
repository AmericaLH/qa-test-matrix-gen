import anthropic
from unittest.mock import patch
from click.testing import CliRunner

from src.cli import cli


def test_generate_shows_auth_error_message(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "bad-key")

    with patch("src.ai_client._call_anthropic") as mock:
        mock.side_effect = anthropic.AuthenticationError(
            message="invalid key", response=__mock_response(), body={}
        )
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "--from-file", "tests/fixtures/sample_ticket.json"])

    assert result.exit_code != 0
    assert "ANTHROPIC_API_KEY" in result.output


def test_generate_shows_ollama_not_running_message(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    with patch("src.ai_client._call_anthropic") as mock_ant:
        mock_ant.side_effect = anthropic.RateLimitError(
            message="rate limit", response=__mock_response(), body={}
        )
        with patch("src.ai_client._call_ollama") as mock_oll:
            mock_oll.side_effect = RuntimeError(
                "Ollama is not running at http://localhost:11434/v1.\n"
                "Start it with:  ollama serve\n"
                "Pull a model:   ollama pull llama3.2"
            )
            runner = CliRunner()
            result = runner.invoke(cli, ["generate", "--from-file", "tests/fixtures/sample_ticket.json"])

    assert result.exit_code != 0
    assert "ollama serve" in result.output


def test_checklist_shows_auth_error_message(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "bad-key")

    with patch("src.ai_client._call_anthropic") as mock:
        mock.side_effect = anthropic.AuthenticationError(
            message="invalid key", response=__mock_response(), body={}
        )
        runner = CliRunner()
        result = runner.invoke(cli, ["checklist", "--from-file", "tests/fixtures/sample_ticket.json"])

    assert result.exit_code != 0
    assert "ANTHROPIC_API_KEY" in result.output


def __mock_response():
    from unittest.mock import MagicMock
    r = MagicMock()
    r.headers = {}
    return r
