# QA Test Matrix Generator

An AI-powered assistant that ingests a Jira ticket and auto-derives:
- A **test matrix** — structured test cases covering happy paths, negative paths, boundary conditions, data permutations, accessibility, and performance
- A **checklist** — a flat list of test checks ready to paste directly into Jira's Checklist feature

Built as a capstone for the [Enroute Coding Assistants Course](../Enroute-Coding-Assistants-Course/).

---

## Why This Exists

Manual test design from requirements is time-consuming and inconsistent. This tool uses Claude (Anthropic SDK) to:
1. Parse acceptance criteria and user stories from a Jira ticket
2. Generate a structured test matrix or a quick checklist
3. Export test cases directly to Xray (Jira test management)
4. Suggest Glean search prompts to find the test data setup you need internally

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

## Checklist command

Generates a flat list of test checks — one per line — ready to paste into Jira's Checklist feature.

### From a live Jira ticket

```bash
python -m src.cli checklist --ticket PROJECT-123
```

### From a local file (no VPN needed)

```bash
python -m src.cli checklist --from-file tests/fixtures/sample_ticket.json
```

Files are saved in `checklists/PROJECT-123.txt`. Open it, select all, and paste directly into the Jira Checklist field.

Example output file:
```
User can log in with valid email and password
Error message appears when password is incorrect
Form shows validation error when email is empty
Remember me checkbox is visible and clickable
Session persists for 30 days when remember me is checked
All form fields are reachable via keyboard
```

---

## Architecture

```
qa-test-matrix-gen/
├── src/
│   ├── cli.py               # Entry point (Click CLI)
│   ├── jira_client.py       # Jira REST API wrapper
│   ├── matrix_generator.py    # AI logic for full test matrix
│   ├── checklist_generator.py # AI logic for flat Jira checklist
│   ├── xray_exporter.py       # Xray REST API export
│   └── models.py              # Data models (TestCase, TestMatrix, Checklist)
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
