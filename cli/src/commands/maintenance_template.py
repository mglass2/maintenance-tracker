"""Maintenance template management commands for the Maintenance Tracker CLI."""

import json
from typing import Any

import click

from src.api_client import (
    APIClient,
    APIClientError4xx,
    APIConnectionError,
    APIServerError5xx,
    APITimeoutError,
)


def _convert_value_type(value: str) -> Any:
    """Convert string to int/float if possible, else string.

    Args:
        value: The string value to convert

    Returns:
        Converted value (int, float, or str)
    """
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


@click.command(name="create-maintenance-template")
def create_maintenance_template(item_type_id=None):
    """Create a new maintenance template for an item type and task type combination.

    This command will:
    1. Let you select an item type (or use the provided one)
    2. Show existing templates for that item type
    3. Let you select a task type
    4. Collect the maintenance interval in days
    5. Optionally collect custom interval fields
    6. Create the maintenance template record

    Args:
        item_type_id: Optional item type ID. If provided, skips the item type selection.
    """
    # Phase 1: Fetch and select item type
    try:
        with APIClient() as client:
            response = client._make_request("GET", "/item_types")
            if response.status_code != 200:
                click.echo("Error: Unable to fetch item types from API", err=True)
                return

            types_data = response.data.get("data", {})
            item_types = types_data.get("item_types", [])

            if not item_types:
                click.echo("Error: No item types available in the system", err=True)
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

    # Handle item type selection (auto-select if provided, otherwise prompt)
    selected_item_type_id = None
    selected_item_type_name = None

    if item_type_id:
        # Auto-select the provided item type
        matching_type = None
        for item_type in item_types:
            if item_type.get("id") == item_type_id:
                matching_type = item_type
                break

        if matching_type:
            selected_item_type_id = matching_type.get("id")
            selected_item_type_name = matching_type.get("name")
            click.echo(f"\nUsing item type: {selected_item_type_name}")
        else:
            # Fallback to manual selection if item type not found
            click.echo(
                f"\nWarning: Item type {item_type_id} not found. Please select from available types.",
                err=True
            )
            click.echo("\nAvailable Item Types:")
            for idx, item_type in enumerate(item_types, 1):
                name = item_type.get("name", "Unknown")
                description = item_type.get("description", "")
                if description:
                    click.echo(f"  {idx}. {name} - {description}")
                else:
                    click.echo(f"  {idx}. {name}")

            while True:
                selection = click.prompt(
                    f"Select an item type (1-{len(item_types)})",
                    type=str,
                    default=""
                ).strip()
                if not selection:
                    click.echo("Error: Please select an item type", err=True)
                    continue

                try:
                    selection_num = int(selection)
                    if 1 <= selection_num <= len(item_types):
                        selected_item_type_id = item_types[selection_num - 1].get("id")
                        selected_item_type_name = item_types[selection_num - 1].get("name")
                        break
                    else:
                        click.echo(
                            f"Error: Please enter a number between 1 and {len(item_types)}",
                            err=True
                        )
                except ValueError:
                    click.echo(
                        f"Error: Please enter a valid number between 1 and {len(item_types)}",
                        err=True
                    )
    else:
        # Display item types and prompt for selection
        click.echo("\nAvailable Item Types:")
        for idx, item_type in enumerate(item_types, 1):
            name = item_type.get("name", "Unknown")
            description = item_type.get("description", "")
            if description:
                click.echo(f"  {idx}. {name} - {description}")
            else:
                click.echo(f"  {idx}. {name}")

        # Validate item type selection
        while True:
            selection = click.prompt(
                f"Select an item type (1-{len(item_types)})",
                type=str,
                default=""
            ).strip()
            if not selection:
                click.echo("Error: Please select an item type", err=True)
                continue

            try:
                selection_num = int(selection)
                if 1 <= selection_num <= len(item_types):
                    selected_item_type_id = item_types[selection_num - 1].get("id")
                    selected_item_type_name = item_types[selection_num - 1].get("name")
                    break
                else:
                    click.echo(
                        f"Error: Please enter a number between 1 and {len(item_types)}",
                        err=True
                    )
            except ValueError:
                click.echo(
                    f"Error: Please enter a valid number between 1 and {len(item_types)}",
                    err=True
                )

    # Phase 2: Fetch and display existing templates for this item type
    try:
        with APIClient() as client:
            response = client._make_request(
                "GET",
                f"/maintenance_templates/item_types/{selected_item_type_id}"
            )

            if response.status_code == 200:
                existing_templates = response.data.get("data", [])

                if existing_templates:
                    click.echo(f"\nCurrent maintenance templates for {selected_item_type_name}:")
                    for template in existing_templates:
                        task_name = template.get("task_type_name", "Unknown")
                        interval = template.get("time_interval_days")
                        click.echo(f"  • {task_name}: Every {interval} days")
                else:
                    click.echo(f"\nNo existing templates for {selected_item_type_name}")
            else:
                click.echo("\nWarning: Could not fetch existing templates", err=True)

    except Exception as e:
        click.echo(f"\nWarning: Could not fetch existing templates: {str(e)}", err=True)

    click.echo("\n" + "="*60)

    # Phase 3: Fetch and select task type
    try:
        with APIClient() as client:
            response = client._make_request("GET", f"/task_types?item_type_id={selected_item_type_id}")
            if response.status_code != 200:
                click.echo("Error: Unable to fetch task types from API", err=True)
                return

            types_data = response.data.get("data", {})
            task_types = types_data.get("task_types", [])

            if not task_types:
                click.echo(f"Error: No task types available for {selected_item_type_name} in the system", err=True)
                return
    except (APIConnectionError, APITimeoutError):
        click.echo("\n✗ Error: Unable to connect to API", err=True)
        click.echo("Please ensure the API service is running and try again.", err=True)
        return
    except APIServerError5xx:
        click.echo("\n✗ Error: Server error occurred", err=True)
        return
    except Exception as e:
        click.echo(f"\n✗ Error: An unexpected error occurred: {str(e)}", err=True)
        return

    # Display task types and prompt for selection
    click.echo("\nAvailable Task Types:")
    for idx, task_type in enumerate(task_types, 1):
        name = task_type.get("name", "Unknown")
        description = task_type.get("description", "")
        if description:
            click.echo(f"  {idx}. {name} - {description}")
        else:
            click.echo(f"  {idx}. {name}")

    # Validate task type selection
    selected_task_type_id = None
    selected_task_type_name = None
    while True:
        selection = click.prompt(
            f"Select a task type (1-{len(task_types)})",
            type=str,
            default=""
        ).strip()
        if not selection:
            click.echo("Error: Please select a task type", err=True)
            continue

        try:
            selection_num = int(selection)
            if 1 <= selection_num <= len(task_types):
                selected_task_type_id = task_types[selection_num - 1].get("id")
                selected_task_type_name = task_types[selection_num - 1].get("name")
                break
            else:
                click.echo(
                    f"Error: Please enter a number between 1 and {len(task_types)}",
                    err=True
                )
        except ValueError:
            click.echo(
                f"Error: Please enter a valid number between 1 and {len(task_types)}",
                err=True
            )

    # Phase 4: Collect time_interval_days
    time_interval_days = None
    while True:
        interval_input = click.prompt(
            "\nTime interval in days (how often should this maintenance be performed)",
            type=str,
            default=""
        ).strip()

        if not interval_input:
            click.echo("Error: Time interval is required", err=True)
            continue

        try:
            time_interval_days = int(interval_input)
            if time_interval_days <= 0:
                click.echo("Error: Interval must be greater than 0", err=True)
                continue
            break
        except ValueError:
            click.echo("Error: Please enter a valid number", err=True)

    # Phase 5: Collect custom_interval (optional)
    custom_interval = {}
    while True:
        add_field = click.prompt(
            "\nWould you like to save any other information about this maintenance template? (yes/no)",
            type=str,
            default="no"
        ).strip().lower()

        if add_field not in ("yes", "y", "no", "n", ""):
            click.echo("Please enter 'yes' or 'no'", err=True)
            continue

        if add_field in ("no", "n", ""):
            break

        # Get field name
        field_name = click.prompt(
            "Enter the name for the information (or press Enter to finish)",
            type=str,
            default=""
        ).strip()

        if not field_name:
            break

        # Normalize field name (lowercase, underscore)
        normalized_field = field_name.lower().replace(" ", "_")

        # Get field value
        field_value = click.prompt(
            f"What value would you like to submit for {normalized_field}?",
            type=str,
            default=""
        ).strip()

        if field_value:
            # Auto-convert type
            converted_value = _convert_value_type(field_value)
            custom_interval[normalized_field] = converted_value
            click.echo(f"✓ Added: {normalized_field} = {converted_value}")

    # Phase 6: Submit to API
    payload = {
        "item_type_id": selected_item_type_id,
        "task_type_id": selected_task_type_id,
        "time_interval_days": time_interval_days,
    }

    if custom_interval:
        payload["custom_interval"] = custom_interval

    try:
        with APIClient() as client:
            response = client._make_request(
                "POST",
                "/maintenance_templates",
                data=payload
            )

            if response.status_code == 201:
                template_data = response.data.get("data", {})
                click.echo("\n✓ Success: Maintenance template created successfully!\n")
                click.echo("Template Details:")
                click.echo(f"  ID:                {template_data.get('id')}")
                click.echo(f"  Item Type:         {selected_item_type_name}")
                click.echo(f"  Task Type:         {selected_task_type_name}")
                click.echo(f"  Interval (days):   {template_data.get('time_interval_days')}")
                if template_data.get('custom_interval'):
                    click.echo(f"  Custom Interval:   {json.dumps(template_data.get('custom_interval'))}")
                click.echo(f"  Created:           {template_data.get('created_at')}")
            else:
                click.echo(f"Error: Unexpected response status {response.status_code}", err=True)

    except APIClientError4xx as e:
        # Handle client errors
        try:
            error_data = json.loads(e.response_body) if isinstance(e.response_body, str) else e.response_body
        except (json.JSONDecodeError, TypeError):
            error_data = {}

        if e.status_code == 409:
            click.echo(
                "\n✗ Error: A template for this item type and task type combination already exists",
                err=True
            )
            click.echo("Please select a different combination or delete the existing template.", err=True)
        elif e.status_code == 404:
            click.echo(
                f"\n✗ Error: {error_data.get('message', 'Resource not found')}",
                err=True
            )
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
                click.echo(
                    f"  - {error_data.get('message', 'Validation failed')}",
                    err=True
                )
        else:
            click.echo(
                f"\n✗ Error: {error_data.get('message', 'Request failed')}",
                err=True
            )

    except (APIConnectionError, APITimeoutError):
        click.echo("\n✗ Error: Unable to connect to API", err=True)
        click.echo("Please ensure the API service is running and try again.", err=True)

    except APIServerError5xx:
        click.echo("\n✗ Error: Server error occurred", err=True)
        click.echo("Please try again later. If the problem persists, contact support.", err=True)

    except Exception as e:
        click.echo(f"\n✗ Error: An unexpected error occurred: {str(e)}", err=True)
