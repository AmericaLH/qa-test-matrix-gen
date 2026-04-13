import anthropic
import pytest
from unittest.mock import MagicMock, patch

from src.ai_client import call_model, _warn_rate_limit


def _rate_limit_error(headers: dict = {}) -> anthropic.RateLimitError:
    response = MagicMock()
    response.headers = headers
    return anthropic.RateLimitError(message="rate limit", response=response, body={})


# --- Anthropic happy path ---

def test_call_model_returns_anthropic_response(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("src.ai_client._call_anthropic", return_value='{"items":[]}') as mock:
        result = call_model("sys", "user msg")
    assert result == '{"items":[]}'
    mock.assert_called_once()


# --- Ollama fallback ---

def test_call_model_falls_back_to_ollama_on_rate_limit(monkeypatch, capsys):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("src.ai_client._call_anthropic", side_effect=_rate_limit_error({"retry-after": "60"})):
        with patch("src.ai_client._call_ollama", return_value='{"items":[]}') as ollama_mock:
            result = call_model("sys", "user msg")

    assert result == '{"items":[]}'
    ollama_mock.assert_called_once()
    captured = capsys.readouterr()
    assert "rate limit" in captured.err.lower()
    assert "Ollama" in captured.err


def test_call_model_shows_retry_time_in_fallback_warning(monkeypatch, capsys):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("src.ai_client._call_anthropic", side_effect=_rate_limit_error({"retry-after": "120"})):
        with patch("src.ai_client._call_ollama", return_value="ok"):
            call_model("sys", "user msg")

    captured = capsys.readouterr()
    assert "2 min" in captured.err


# --- Ollama not running ---

def test_call_model_raises_if_ollama_not_running(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("src.ai_client._call_anthropic", side_effect=_rate_limit_error()):
        with patch("src.ai_client._call_ollama", side_effect=RuntimeError("Ollama is not running")):
            with pytest.raises(RuntimeError, match="Ollama is not running"):
                call_model("sys", "user msg")


# --- _warn_rate_limit formatting ---

def test_warn_rate_limit_seconds(capsys):
    _warn_rate_limit(_rate_limit_error({"retry-after": "45"}))
    assert "45s" in capsys.readouterr().err


def test_warn_rate_limit_minutes(capsys):
    _warn_rate_limit(_rate_limit_error({"retry-after": "180"}))
    assert "3 min" in capsys.readouterr().err


def test_warn_rate_limit_no_header(capsys):
    _warn_rate_limit(_rate_limit_error({}))
    assert "Ollama" in capsys.readouterr().err
