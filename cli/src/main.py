"""Main entry point for the CLI application."""

import click
import sys

from src.commands.user import create_user
from src.commands.item import create_item, create_item_maintenance_plan
from src.commands.auth import select_user, whoami, switch_user, logout
from src.utils.interactive import run_interactive_mode


@click.group()
def cli():
    """Maintenance Tracker CLI - manage and forecast maintenance tasks."""
    pass


@cli.command()
def hello():
    """Test command to verify CLI is working."""
    click.echo("Hello from Maintenance Tracker CLI!")


cli.add_command(create_user)
cli.add_command(create_item)
cli.add_command(create_item_maintenance_plan)
cli.add_command(select_user)
cli.add_command(whoami)
cli.add_command(switch_user)
cli.add_command(logout)


if __name__ == "__main__":
    # Check if running in a container (non-interactive environment)
    if not sys.stdin.isatty():
        # Non-interactive mode, just run the CLI normally (shows help and exits)
        cli()
    else:
        # Interactive mode (when tty is available)
        run_interactive_mode(cli)
