# ADR-002: Use Jira REST API v3 with Basic Auth

## Status: Accepted

## Context

Jira tickets need to be fetched programmatically. Options: REST API v2, REST API v3, Jira Python library (`jira` package).

## Decision

Use Jira REST API v3 directly via `httpx` with Basic Auth (email + API token). No third-party Jira wrapper library.

## AI Tool Input

Claude Code noted that the `jira` PyPI package wraps v2 and adds a large dependency. Direct `httpx` calls against v3 are simpler, easier to test with `pytest-httpx`, and avoid version mismatch issues.

## Consequences

- ADF (Atlassian Document Format) must be parsed manually — implemented as `_adf_to_text()` in `jira_client.py`
- Custom fields (like Acceptance Criteria) may vary by Jira instance — fieldname is configurable
- Tests mock the HTTP layer cleanly with `pytest-httpx`
