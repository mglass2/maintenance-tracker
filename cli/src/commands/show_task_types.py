"""Command to display all item types and their associated task types."""

import click

from src.api_client import (
    APIClient,
    APIConnectionError,
    APIServerError5xx,
    APITimeoutError,
)


@click.command(name="show-default-maintenance")
def show_task_types():
    """Display all default maintenance for all types of items.

    This command shows the complete list of item types in the system,
    along with the maintenance tasks that should be performed on each type.
    The information comes from the maintenance templates configured for each item type.
    """

    try:
        with APIClient() as client:
            response = client._make_request("GET", "/maintenance_templates")

            if response.status_code != 200:
                click.echo("Error: Unable to fetch maintenance templates from API", err=True)
                return

            response_data = response.data.get("data", {})
            item_types = response_data.get("item_types", [])

    except (APIConnectionError, APITimeoutError):
        click.echo("\n✗ Error: Unable to connect to API", err=True)
        click.echo("Please ensure the API service is running and try again.", err=True)
        return
    except APIServerError5xx:
        click.echo("\n✗ Error: Server error occurred", err=True)
        click.echo("Please try again later. If the problem persists, contact support.", err=True)
        return
    except Exception as e:
        click.echo(f"\n✗ Error: An unexpected error occurred: {str(e)}", err=True)
        return

    # Display the information
    if not item_types:
        click.echo("\nNo maintenance templates configured yet.")
        click.echo("Create item types and maintenance templates to see them listed here.\n")
        return

    click.echo("\nDefault Maintenance Tasks:\n")
    click.echo("=" * 60)

    for item_type in item_types:
        item_name = item_type.get("item_type_name", "Unknown")
        templates = item_type.get("templates", [])

        click.echo(f"\n{item_name}:")

        if not templates:
            click.echo("  No maintenance tasks configured")
            continue

        for template in templates:
            task_name = template.get("task_type_name", "Unknown")
            interval_days = template.get("time_interval_days", "?")
            custom_interval = template.get("custom_interval")

            # Format the display
            interval_str = f"{interval_days} days"

            if custom_interval:
                click.echo(f"  • {task_name} - {interval_str} - {custom_interval}")
            else:
                click.echo(f"  • {task_name} - {interval_str}")

    click.echo("\n" + "=" * 60 + "\n")
