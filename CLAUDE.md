# Claude Code Instructions

## Project Context

This is a QA test matrix generator. It takes a Jira ticket and produces a structured test matrix using the Anthropic SDK. The target users are QA Engineers who work with Jira + Xray + PostgreSQL.

## Stack

- Python 3.11+, no framework (just Click for CLI)
- Anthropic SDK for AI calls (use `claude-sonnet-4-6` as default model)
- Pydantic for data models
- pytest for tests
- ruff for linting

## Key Conventions

- All AI calls live in `src/matrix_generator.py` — keep them separate from business logic
- Use `python-dotenv` to load `.env` — never hardcode credentials
- Pydantic models are in `src/models.py` — validate all Jira API responses there
- Tests use `pytest-httpx` to mock HTTP calls; do not make real API calls in tests

## Running

```bash
python -m src.cli generate --ticket PROJECT-123
pytest --cov=src
ruff check src tests
```

## What NOT to do

- Do not commit `.env` (it is in .gitignore)
- Do not add async unless needed — keep it sync for simplicity
- Do not add new dependencies without updating `requirements.txt`
