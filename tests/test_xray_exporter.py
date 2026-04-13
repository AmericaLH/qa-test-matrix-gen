from pytest_httpx import HTTPXMock

from src.models import TestCase, TestMatrix, TestType
from src.xray_exporter import export_to_xray

XRAY_TOKEN_URL = "https://xray.cloud.getxray.app/api/v2/authenticate"
XRAY_IMPORT_URL = "https://xray.cloud.getxray.app/api/v2/import/test/bulk"


def _sample_matrix() -> TestMatrix:
    return TestMatrix(
        ticket_key="DEMO-10",
        ticket_summary="Sample feature",
        test_cases=[
            TestCase(
                id="TC-001",
                title="Happy path login",
                type=TestType.HAPPY_PATH,
                preconditions=["User exists"],
                steps=["Go to login", "Enter credentials"],
                expected_result="Logged in",
                glean_prompt="users table schema and seed data for login",
            ),
            TestCase(
                id="TC-002",
                title="Missing password",
                type=TestType.NEGATIVE,
                preconditions=[],
                steps=["Go to login", "Leave password empty", "Submit"],
                expected_result="Validation error shown",
            ),
        ],
    )


def test_export_calls_xray_import_endpoint(monkeypatch, httpx_mock: HTTPXMock):
    monkeypatch.setenv("XRAY_CLIENT_ID", "client123")
    monkeypatch.setenv("XRAY_CLIENT_SECRET", "secret456")

    httpx_mock.add_response(url=XRAY_TOKEN_URL, text='"fake-token"')
    httpx_mock.add_response(url=XRAY_IMPORT_URL, json={"issueCount": 2})

    result = export_to_xray(_sample_matrix(), "DEMO")

    assert result["issueCount"] == 2


def test_export_includes_glean_prompt_in_description(monkeypatch, httpx_mock: HTTPXMock):
    monkeypatch.setenv("XRAY_CLIENT_ID", "client123")
    monkeypatch.setenv("XRAY_CLIENT_SECRET", "secret456")

    httpx_mock.add_response(url=XRAY_TOKEN_URL, text='"fake-token"')

    captured = {}

    def capture_request(request):
        import json as _json
        captured["body"] = _json.loads(request.content)
        from httpx import Response
        return Response(200, json={"issueCount": 2})

    httpx_mock.add_callback(capture_request, url=XRAY_IMPORT_URL)

    export_to_xray(_sample_matrix(), "DEMO")

    happy_path_test = captured["body"][0]
    assert "Glean prompt" in happy_path_test["description"]


def test_export_summary_includes_type(monkeypatch, httpx_mock: HTTPXMock):
    monkeypatch.setenv("XRAY_CLIENT_ID", "client123")
    monkeypatch.setenv("XRAY_CLIENT_SECRET", "secret456")

    httpx_mock.add_response(url=XRAY_TOKEN_URL, text='"fake-token"')

    captured = {}

    def capture_request(request):
        import json as _json
        captured["body"] = _json.loads(request.content)
        from httpx import Response
        return Response(200, json={"issueCount": 2})

    httpx_mock.add_callback(capture_request, url=XRAY_IMPORT_URL)

    export_to_xray(_sample_matrix(), "DEMO")

    summaries = [t["summary"] for t in captured["body"]]
    assert any("HAPPY_PATH" in s for s in summaries)
    assert any("NEGATIVE" in s for s in summaries)
