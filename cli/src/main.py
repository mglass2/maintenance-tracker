"""Main entry point for the CLI application."""

import click


@click.group()
def cli():
    """Maintenance Tracker CLI - manage and forecast maintenance tasks."""
    pass


@cli.command()
def hello():
    """Test command to verify CLI is working."""
    click.echo("Hello from Maintenance Tracker CLI!")


if __name__ == "__main__":
    cli()
