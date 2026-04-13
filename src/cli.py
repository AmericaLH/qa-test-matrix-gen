import json
from pathlib import Path
import click
from dotenv import load_dotenv

from .jira_client import JiraClient
from .matrix_generator import generate_matrix
from .checklist_generator import generate_checklist
from .xray_exporter import export_to_xray

load_dotenv()


@click.group()
def cli():
    """QA Test Matrix Generator — derive test cases from Jira tickets using AI."""


@cli.command()
@click.option("--ticket", default=None, help="Jira ticket key, e.g. PROJECT-123")
@click.option("--from-file", "from_file", default=None, help="Path to a saved Jira ticket JSON (skips Jira API call)")
@click.option("--output-dir", "output_dir", default="test_cases", show_default=True, help="Folder where the matrix JSON will be saved")
def generate(ticket: str | None, from_file: str | None, output_dir: str):
    """Generate a test matrix from a Jira ticket and save it as JSON.

    Either --ticket (live Jira fetch) or --from-file (local JSON) is required.
    """
    if not ticket and not from_file:
        raise click.UsageError("Provide either --ticket or --from-file.")

    if from_file:
        click.echo(f"Reading ticket from {from_file}...")
        with open(from_file) as f:
            raw = json.load(f)
        ticket = ticket or raw.get("key", "LOCAL")
        text = JiraClient.__new__(JiraClient).extract_text(raw)
    else:
        click.echo(f"Fetching {ticket} from Jira...")
        jira = JiraClient()
        raw = jira.get_ticket(ticket)
        text = jira.extract_text(raw)

    click.echo("Generating test matrix with Claude...")
    matrix = generate_matrix(ticket, text)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{ticket}.json"

    out_file.write_text(matrix.model_dump_json(indent=2))

    click.echo(f"Generated {len(matrix.test_cases)} test cases -> {out_file}")
    for type_name, cases in matrix.by_type.items():
        click.echo(f"  {type_name.value}: {len(cases)}")


@cli.command()
@click.option("--ticket", default=None, help="Jira ticket key, e.g. PROJECT-123")
@click.option("--from-file", "from_file", default=None, help="Path to a saved Jira ticket JSON (skips Jira API call)")
@click.option("--output-dir", "output_dir", default="checklists", show_default=True, help="Folder where the checklist will be saved")
def checklist(ticket: str | None, from_file: str | None, output_dir: str):
    """Generate a flat checklist from a Jira ticket, ready to paste into Jira.

    Either --ticket (live Jira fetch) or --from-file (local JSON) is required.

    The output is a plain .txt file — one check per line — that you can copy
    directly into Jira's Checklist field.
    """
    if not ticket and not from_file:
        raise click.UsageError("Provide either --ticket or --from-file.")

    if from_file:
        click.echo(f"Reading ticket from {from_file}...")
        with open(from_file) as f:
            raw = json.load(f)
        ticket = ticket or raw.get("key", "LOCAL")
        text = JiraClient.__new__(JiraClient).extract_text(raw)
    else:
        click.echo(f"Fetching {ticket} from Jira...")
        jira = JiraClient()
        raw = jira.get_ticket(ticket)
        text = jira.extract_text(raw)

    click.echo("Generating checklist with Claude...")
    result = generate_checklist(ticket, text)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{ticket}.txt"

    out_file.write_text(result.to_text())

    click.echo(f"Generated {len(result.items)} checks -> {out_file}")
    for item in result.items:
        click.echo(f"  - {item}")


@cli.command()
@click.option("--ticket", required=True, help="Jira ticket key")
@click.option("--project", required=True, help="Jira project key for Xray import")
@click.option("--input", "input_file", default=None, help="Path to matrix JSON. Defaults to test_cases/{ticket}.json")
def export(ticket: str, project: str, input_file: str | None):
    """Export a saved test matrix JSON to Xray."""
    from .models import TestMatrix

    path = Path(input_file) if input_file else Path("test_cases") / f"{ticket}.json"
    with open(path) as f:
        matrix = TestMatrix.model_validate_json(f.read())

    click.echo(f"Exporting {len(matrix.test_cases)} test cases to Xray project {project}...")
    result = export_to_xray(matrix, project)
    click.echo(f"Done: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    cli()
