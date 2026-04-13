# QA Test Matrix Generator

An AI-powered assistant that ingests a Jira ticket and auto-derives a complete test matrix: happy paths, negative paths, boundary conditions, data permutations, non-functional checks (accessibility, performance), and concrete SQL setups for reproducible test data.

Built as a capstone for the [Enroute Coding Assistants Course](../Enroute-Coding-Assistants-Course/).

---

## Why This Exists

Manual test design from requirements is time-consuming and inconsistent. This tool uses Claude (Anthropic SDK) to:
1. Parse acceptance criteria and user stories from a Jira ticket
2. Generate a structured test matrix covering all test dimensions
3. Export test cases directly to Xray (Jira test management)
4. Suggest PostgreSQL fixtures for reproducible test data

---

## Prerequisites

- Python >= 3.11
- A Jira account with API token
- An Anthropic API key
- (Optional) Xray API token for direct export

---

## Installation

```bash
git clone <your-repo-url>
cd qa-test-matrix-gen
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt --index-url https://pypi.org/simple/
```

Copy and fill in your credentials:
```bash
cp .env.example .env
```

---

## Configuration

Edit `.env` with your values:

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `JIRA_BASE_URL` | e.g. `https://yourcompany.atlassian.net` |
| `JIRA_EMAIL` | Your Jira account email |
| `JIRA_API_TOKEN` | Jira API token (from id.atlassian.com) |
| `XRAY_CLIENT_ID` | Xray API client ID (optional) |
| `XRAY_CLIENT_SECRET` | Xray API client secret (optional) |

---

## Usage

### Option A — Generate from a live Jira ticket (requires VPN + Jira credentials in `.env`)

```bash
python -m src.cli generate --ticket PROJECT-123
```

### Option B — Generate from a local file (no VPN or Jira credentials needed)

Use this to try the tool quickly, or when you are not connected to your corporate VPN:

```bash
python -m src.cli generate --from-file tests/fixtures/sample_ticket.json
```

You can also save your own ticket locally and use it as input:

```bash
python -m src.cli generate --from-file path/to/my_ticket.json --output my_matrix.json
```

### Export the matrix to Xray

```bash
python -m src.cli export --ticket PROJECT-123 --project MYPROJECT
```

---

## Architecture

```
qa-test-matrix-gen/
├── src/
│   ├── cli.py               # Entry point (Click CLI)
│   ├── jira_client.py       # Jira REST API wrapper
│   ├── matrix_generator.py  # Core AI logic (Anthropic SDK)
│   ├── xray_exporter.py     # Xray REST API export
│   ├── sql_fixtures.py      # PostgreSQL fixture generator
│   └── models.py            # Data models (TestCase, TestMatrix)
├── tests/
│   ├── fixtures/            # Sample Jira ticket JSON for tests
│   ├── test_matrix_generator.py
│   ├── test_jira_client.py
│   └── test_models.py
├── docs/
│   └── adr/                 # Architecture Decision Records
├── .github/
│   └── workflows/
│       └── ci.yml           # CI with AI-assisted test generation step
├── .claude/
│   └── agents/              # Claude Code agent configs
├── DEVLOG.md                # AI tool usage log (course requirement)
├── CLAUDE.md                # Instructions for Claude Code in this repo
└── .env.example
```

---

## Running Tests

```bash
pytest --cov=src --cov-report=term-missing
```

---

## AI Tools Used

| Tool | Used For |
|---|---|
| Claude Code (CLI) | Scaffolding, debugging, refactoring |
| Anthropic SDK (programmatic) | Core test matrix generation |
| Codex CLI | Comparison tasks (documented in DEVLOG) |

---

## Known Limitations

- Jira ticket parsing quality depends on how well-written the acceptance criteria are
- Xray export uses Xray Cloud API v2; Xray Server/DC requires different endpoints
- SQL fixture suggestions are schema-agnostic — you may need to adapt column names

---

## Development Log

See [DEVLOG.md](DEVLOG.md) for a timestamped record of AI tool interactions throughout development.
