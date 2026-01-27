"""Item type management commands for the Maintenance Tracker CLI."""

import json
import click

from src.api_client import (
    APIClient,
    APIClientError4xx,
    APIConnectionError,
    APIServerError5xx,
    APITimeoutError,
)


@click.command(name="create-item-type")
def create_item_type():
    """Create a new item type in the system.

    An item type represents a category of items that can be maintained
    (e.g., Car, House, Snowblower). After creating an item type, you can
    optionally set up maintenance templates for it.
    """

    # Query for current item types
    try:
        with APIClient() as client:
            response = client._make_request("GET", "/item_types")
            if response.status_code != 200:
                click.echo("Error: Unable to fetch item types from API", err=True)
                return

            types_data = response.data.get("data", {})
            item_types = types_data.get("item_types", [])

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

    # Display item types if any exist
    if item_types:
        click.echo("\nExisting Item Types:")
        for idx, item_type in enumerate(item_types, 1):
            name = item_type.get("name", "Unknown")
            description = item_type.get("description", "")
            if description:
                click.echo(f"  {name} - {description}")
            else:
                click.echo(f"  {name}")
        click.echo()
    else:
        click.echo(f"\nNo item types exist.\n")

    # Phase 1: Collect name (required)
    while True:
        name = click.prompt("Enter item type name", type=str, default="").strip()
        if not name:
            click.echo("Error: Name cannot be empty", err=True)
            continue

        if len(name) > 255:
            click.echo("Error: Name must be 255 characters or less", err=True)
            continue

        break

    # Phase 2: Collect description (optional)
    description = click.prompt(
        "Enter item type description (or press Enter to skip)",
        type=str,
        default=""
    ).strip()

    # Convert empty string to None for API
    if not description:
        description = None

    # Phase 3: Build payload and submit to API
    payload = {
        "name": name,
    }

    if description:
        payload["description"] = description

    try:
        with APIClient() as client:
            response = client._make_request("POST", "/item_types", data=payload)

            if response.status_code == 201:
                item_type_data = response.data.get("data", {})
                click.echo("\n✓ Success: Item type created successfully!\n")
                click.echo("Item Type Details:")
                click.echo(f"  ID:          {item_type_data.get('id')}")
                click.echo(f"  Name:        {item_type_data.get('name')}")
                if item_type_data.get('description'):
                    click.echo(f"  Description: {item_type_data.get('description')}")
                click.echo(f"  Created:     {item_type_data.get('created_at')}")
            else:
                click.echo(f"Error: Unexpected response status {response.status_code}", err=True)
                return

    except APIClientError4xx as e:
        # Handle client errors (400, 409, 422)
        try:
            error_data = json.loads(e.response_body) if isinstance(e.response_body, str) else e.response_body
        except (json.JSONDecodeError, TypeError):
            error_data = {}

        if e.status_code == 409:
            click.echo("\n✗ Error: An item type with this name already exists", err=True)
            click.echo("Please use a different name.", err=True)
        elif e.status_code == 400:
            click.echo("\n✗ Error: Invalid input provided", err=True)
            details = error_data.get('details', {})
            errors = details.get('errors', [])
            if errors:
                for error in errors:
                    loc = error.get('loc', [])
                    msg = error.get('msg', '')
                    field = loc[-1] if loc else 'unknown'
                    click.echo(f"  - {field}: {msg}", err=True)
            else:
                click.echo(f"  - {error_data.get('message', 'Validation failed')}", err=True)
        else:
            click.echo(f"\n✗ Error: {error_data.get('message', 'Request failed')}", err=True)
        return

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

    # Phase 4: Ask if user wants to create maintenance templates
    click.echo("\n" + "="*60)
    while True:
        launch_template_cmd = click.prompt(
            "\nWould you like to create maintenance templates for this item type? (yes/no)",
            type=str,
            default="yes"
        ).strip().lower()

        if launch_template_cmd in ("yes", "y", ""):
            # Import the command
            from src.commands.maintenance_template import create_maintenance_template

            # Launch create-maintenance-template command
            click.echo("\nLaunching maintenance template setup...\n")
            ctx = click.Context(create_maintenance_template)
            ctx.invoke(create_maintenance_template, item_type_id=item_type_data.get('id'))
            break
        elif launch_template_cmd in ("no", "n"):
            click.echo("\nItem type created successfully. You can create maintenance templates later.")
            break
        else:
            click.echo("Please enter 'yes' or 'no'", err=True)
