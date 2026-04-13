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
4. Suggest Glean search prompts to find the internal test data setup you need

If the Anthropic API rate limit is hit, the tool **automatically falls back to a local Ollama model** so your work is never blocked.

---

## Prerequisites

- Python >= 3.11
- An Anthropic API key
- A Jira account with API token (only needed for live ticket fetching)
- Ollama installed locally (automatic fallback — see [Ollama Setup](#ollama-setup))
- (Optional) Xray API token for direct export to Jira

---

## Installation

```bash
git clone <your-repo-url>
cd qa-test-matrix-gen
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Copy and fill in your credentials:
```bash
cp .env.example .env
```

---

## Configuration

Edit `.env` with your values:

| Variable | Description | Required |
|---|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Yes |
| `JIRA_BASE_URL` | e.g. `https://yourcompany.atlassian.net` | For live tickets |
| `JIRA_EMAIL` | Your Jira account email | For live tickets |
| `JIRA_API_TOKEN` | Jira API token (from id.atlassian.com) | For live tickets |
| `OLLAMA_BASE_URL` | Ollama server URL (default: `http://localhost:11434/v1`) | No |
| `OLLAMA_MODEL` | Model to use as fallback (default: `llama3.2`) | No |
| `XRAY_CLIENT_ID` | Xray API client ID | For Xray export |
| `XRAY_CLIENT_SECRET` | Xray API client secret | For Xray export |

---

## Ollama Setup

Ollama is used as an automatic fallback when the Anthropic API rate limit is reached. It runs entirely on your machine — no data leaves your network.

### Install Ollama (Mac)

```bash
# Download from https://ollama.com and install, then:
ollama pull llama3.2
```

### Start Ollama

```bash
ollama serve
```

Keep this running in a separate terminal. The tool will use it automatically whenever Anthropic is unavailable.

### Change the fallback model (optional)

Add this to your `.env`:
```
OLLAMA_MODEL=mistral
```

Any model listed at [ollama.com/library](https://ollama.com/library) works. `llama3.2` is the recommended default.

### What you will see when the fallback activates

```
Anthropic rate limit reached (retry in ~2 min).
Falling back to Ollama (llama3.2)...
```

The tool then continues normally using the local model.

---

## Usage

### Generate a test matrix

**From a live Jira ticket** (requires VPN + Jira credentials in `.env`):
```bash
python -m src.cli generate --ticket PROJECT-123
```

**From a local file** (no VPN or Jira credentials needed):
```bash
python -m src.cli generate --from-file tests/fixtures/sample_ticket.json
```

Output is saved to `test_cases/PROJECT-123.json`.

### Generate a checklist

Produces a flat `.txt` file — one check per line — ready to paste into Jira's Checklist field.

**From a live Jira ticket:**
```bash
python -m src.cli checklist --ticket PROJECT-123
```

**From a local file:**
```bash
python -m src.cli checklist --from-file tests/fixtures/sample_ticket.json
```

Output is saved to `checklists/PROJECT-123.txt`. Open the file, select all, and paste directly into the Jira Checklist field.

Example output:
```
User can log in with valid email and password
Error message appears when password is incorrect
Form shows validation error when email is empty
Remember me checkbox is visible and clickable
Session persists for 30 days when remember me is checked
All form fields are reachable via keyboard
```

### Export a test matrix to Xray

```bash
python -m src.cli export --ticket PROJECT-123 --project MYPROJECT
```

Reads from `test_cases/PROJECT-123.json` and pushes each test case to Xray as a new test issue.

---

## Architecture

```
qa-test-matrix-gen/
├── src/
│   ├── cli.py                 # Entry point — Click CLI commands
│   ├── ai_client.py           # Model routing: Anthropic → Ollama fallback
│   ├── matrix_generator.py    # Builds full test matrix via AI
│   ├── checklist_generator.py # Builds flat Jira checklist via AI
│   ├── jira_client.py         # Jira REST API v3 wrapper
│   ├── xray_exporter.py       # Xray Cloud API export
│   └── models.py              # Pydantic models: TestCase, TestMatrix, Checklist
├── tests/
│   ├── fixtures/              # Sample Jira ticket JSON for offline testing
│   ├── test_ai_client.py      # Anthropic/Ollama fallback logic
│   ├── test_matrix_generator.py
│   ├── test_checklist_generator.py
│   ├── test_jira_client.py
│   ├── test_models.py
│   ├── test_xray_exporter.py
│   └── test_error_handling.py
├── docs/
│   └── adr/                   # Architecture Decision Records
├── .github/
│   └── workflows/
│       └── ci.yml             # CI pipeline with AI-assisted step
├── test_cases/                # Generated test matrices (gitignored)
├── checklists/                # Generated checklists (gitignored)
├── DEVLOG.md                  # AI tool usage log (course requirement)
├── CLAUDE.md                  # Instructions for Claude Code in this repo
└── .env.example
```

---

## How the AI routing works

```
generate / checklist command
        │
        ▼
  ai_client.py
        │
        ├─── Try Anthropic (Claude)
        │         │
        │         ├── Success → return result
        │         │
        │         └── RateLimitError
        │                   │
        │                   ▼
        │           warn to terminal
        │                   │
        └─── Try Ollama (local model)
                    │
                    ├── Success → return result
                    │
                    └── Not running → clear error with setup instructions
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
| Claude Code (CLI) | Scaffolding, debugging, refactoring throughout development |
| Anthropic SDK (programmatic) | Primary model for test matrix and checklist generation |
| Ollama (local model) | Automatic fallback when Anthropic rate limit is hit; comparison tasks |

---

## Known Limitations

- Jira ticket parsing quality depends on how well-written the acceptance criteria are
- Xray export uses Xray Cloud API v2; Xray Server/DC requires different endpoints
- Ollama output quality is lower than Claude for complex tickets — review carefully
- `glean_prompt` suggestions are generic and may need adjusting for your team's Glean structure

---

## Development Log

See [DEVLOG.md](DEVLOG.md) for a timestamped record of AI tool interactions throughout development.
