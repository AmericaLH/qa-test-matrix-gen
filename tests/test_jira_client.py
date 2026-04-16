import json
from pathlib import Path
from pytest_httpx import HTTPXMock

from src.jira_client import JiraClient, _adf_to_text


SAMPLE_TICKET = json.loads(
    (Path(__file__).parent / "fixtures" / "sample_ticket.json").read_text()
)


def test_adf_to_text_simple():
    adf = {
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": "Hello world"}],
            }
        ],
    }
    assert "Hello world" in _adf_to_text(adf)


def test_adf_to_text_empty():
    assert _adf_to_text({}) == ""
    assert _adf_to_text(None) == ""


def test_extract_text_includes_summary(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token123")

    client = JiraClient()
    text = client.extract_text(SAMPLE_TICKET)
    assert "Remember me" in text


def test_extract_text_includes_acceptance_criteria(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token123")

    client = JiraClient()
    text = client.extract_text(SAMPLE_TICKET)
    assert "Acceptance Criteria" in text
    assert "session cookie expires in 30 days" in text


def test_parse_ticket_acceptance_criteria_list(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token123")

    client = JiraClient()
    parsed = client.parse_ticket(SAMPLE_TICKET)
    assert len(parsed.acceptance_criteria) == 6
    assert parsed.acceptance_criteria[0] == "Checkbox is visible and labeled 'Remember me' on the login page"


def test_parse_ticket_missing_acceptance_criteria(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token123")

    ticket_without_ac = {"key": "DEMO-1", "fields": {"summary": "Simple task"}}
    client = JiraClient()
    parsed = client.parse_ticket(ticket_without_ac)
    assert parsed.acceptance_criteria == []


def test_get_ticket_returns_json(monkeypatch, httpx_mock: HTTPXMock):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token123")

    httpx_mock.add_response(
        url="https://example.atlassian.net/rest/api/3/issue/DEMO-42",
        json=SAMPLE_TICKET,
    )

    client = JiraClient()
    result = client.get_ticket("DEMO-42")
    assert result["key"] == "DEMO-42"
