import json
import click
from dotenv import load_dotenv

from .jira_client import JiraClient
from .matrix_generator import generate_matrix
from .xray_exporter import export_to_xray

load_dotenv()


@click.group()
def cli():
    """QA Test Matrix Generator — derive test cases from Jira tickets using AI."""


@cli.command()
@click.option("--ticket", required=True, help="Jira ticket key, e.g. PROJECT-123")
@click.option("--output", default="matrix.json", show_default=True, help="Output file path")
def generate(ticket: str, output: str):
    """Generate a test matrix from a Jira ticket and save it as JSON."""
    click.echo(f"Fetching {ticket} from Jira...")
    jira = JiraClient()
    raw = jira.get_ticket(ticket)
    text = jira.extract_text(raw)

    click.echo("Generating test matrix with Claude...")
    matrix = generate_matrix(ticket, text)

    with open(output, "w") as f:
        f.write(matrix.model_dump_json(indent=2))

    click.echo(f"Generated {len(matrix.test_cases)} test cases -> {output}")
    for type_name, cases in matrix.by_type.items():
        click.echo(f"  {type_name.value}: {len(cases)}")


@cli.command()
@click.option("--ticket", required=True, help="Jira ticket key")
@click.option("--project", required=True, help="Jira project key for Xray import")
@click.option("--input", "input_file", default="matrix.json", show_default=True)
def export(ticket: str, project: str, input_file: str):
    """Export a saved test matrix JSON to Xray."""
    from .models import TestMatrix

    with open(input_file) as f:
        matrix = TestMatrix.model_validate_json(f.read())

    click.echo(f"Exporting {len(matrix.test_cases)} test cases to Xray project {project}...")
    result = export_to_xray(matrix, project)
    click.echo(f"Done: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    cli()
