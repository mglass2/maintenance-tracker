"""Item management commands for the Maintenance Tracker CLI."""

import json
from datetime import datetime
from typing import Optional, Dict, Any

import click

from src.api_client import (
    APIClient,
    APIClientError4xx,
    APIConnectionError,
    APIServerError5xx,
    APITimeoutError,
)


# Field translation dictionary for normalization
FIELD_TRANSLATIONS = {
    'mileage': ['miles', 'mile', 'milage', 'milleage', 'odometer'],
    'vin': ['vehicle_id', 'vehicle_identification'],
    'serial_number': ['serial', 'serial_no', 'sn'],
    'purchase_price': ['price', 'cost', 'purchase_cost'],
}


def _translate_field_name(field_name: str) -> str:
    """Normalize and translate field names to standard forms.

    Args:
        field_name: The field name to normalize

    Returns:
        The normalized field name
    """
    normalized = field_name.lower().replace(" ", "_")
    for standard_name, variations in FIELD_TRANSLATIONS.items():
        if normalized in variations or normalized == standard_name:
            return standard_name
    return normalized


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


@click.command(name="create-item-maintenance-plan")
@click.argument("item_id", type=int)
def create_item_maintenance_plan(item_id: int):
    """Create maintenance plans for an item based on its maintenance templates.

    ITEM_ID: The ID of the item to create maintenance plans for

    This command will:
    1. Fetch maintenance templates for the item's type
    2. Guide you through selecting which templates to implement
    3. Allow customization of maintenance intervals
    4. Create item_maintenance_plan records
    """
    try:
        with APIClient() as client:
            # Step 1: Fetch item details
            response = client._make_request("GET", f"/items/{item_id}")

            if response.status_code != 200:
                click.echo(f"✗ Error: Item with ID {item_id} not found", err=True)
                return

            item = response.data.get("data", {})
            item_type_id = item.get("item_type_id")

            click.echo(f"\nItem: {item.get('name')}")
            click.echo(f"Setting up maintenance plan...\n")

            # Step 2: Fetch maintenance templates
            response = client._make_request(
                "GET",
                f"/maintenance_templates/item_types/{item_type_id}"
            )

            templates = response.data.get("data", [])

            if not templates:
                click.echo("✗ No maintenance templates available for this item type", err=True)
                return

            # Step 3: Fetch existing plans
            response = client._make_request(
                "GET",
                f"/item_maintenance_plans/items/{item_id}"
            )

            existing_plans = response.data.get("data", [])
            existing_task_type_ids = {plan.get("task_type_id") for plan in existing_plans}

            # Step 4-6: Loop through templates, collect customizations, create plans
            created_plans = []
            skipped_plans = []

            for template in templates:
                task_type_id = template.get("task_type_id")
                task_type_name = template.get("task_type_name")
                default_time_interval = template.get("time_interval_days")
                default_custom_interval = template.get("custom_interval")

                # Skip if already exists
                if task_type_id in existing_task_type_ids:
                    click.echo(f"\n⊘ {task_type_name}: Already exists (skipping)")
                    continue

                # Ask user if they want to implement
                click.echo(f"\n{'='*60}")
                click.echo(f"Task Type: {task_type_name}")
                click.echo(f"Default Interval: Every {default_time_interval} days")

                if default_custom_interval:
                    click.echo(f"Default Custom Interval: {json.dumps(default_custom_interval)}")

                implement = None
                while True:
                    implement = click.prompt(
                        "Implement this maintenance task? (yes/skip)",
                        type=str,
                        default="yes"
                    ).strip().lower()

                    if implement in ("yes", "y", ""):
                        implement = "yes"
                        break
                    elif implement in ("skip", "s", "no", "n"):
                        implement = "skip"
                        break
                    else:
                        click.echo("Please enter 'yes' or 'skip'", err=True)

                if implement == "skip":
                    skipped_plans.append(task_type_name)
                    click.echo(f"⊘ Skipped: {task_type_name}")
                    continue

                # Prompt for time_interval_days
                time_interval_days = None
                while True:
                    time_input = click.prompt(
                        f"Time interval in days (default: {default_time_interval})",
                        type=str,
                        default=str(default_time_interval)
                    ).strip()

                    try:
                        time_interval_days = int(time_input)
                        if time_interval_days <= 0:
                            click.echo("Error: Interval must be greater than 0", err=True)
                            continue
                        break
                    except ValueError:
                        click.echo("Error: Please enter a valid number", err=True)

                # Handle custom_interval if template has it
                custom_interval = None
                if default_custom_interval:
                    click.echo(f"\nCustom Interval Configuration:")
                    click.echo("The template defines these custom intervals:")

                    custom_interval = {}
                    for key, default_value in default_custom_interval.items():
                        while True:
                            value_input = click.prompt(
                                f"  {key} (default: {default_value})",
                                type=str,
                                default=str(default_value)
                            ).strip()

                            # Try to preserve type from template
                            if isinstance(default_value, int):
                                try:
                                    custom_interval[key] = int(value_input)
                                    break
                                except ValueError:
                                    click.echo(f"Error: Please enter a valid number", err=True)
                            else:
                                custom_interval[key] = value_input
                                break

                # Create the plan
                payload = {
                    "item_id": item_id,
                    "task_type_id": task_type_id,
                    "time_interval_days": time_interval_days,
                }

                if custom_interval:
                    payload["custom_interval"] = custom_interval

                try:
                    response = client._make_request(
                        "POST",
                        "/item_maintenance_plans",
                        data=payload
                    )

                    if response.status_code == 201:
                        created_plans.append(task_type_name)
                        click.echo(f"✓ Created: {task_type_name}")
                    elif response.status_code == 409:
                        click.echo(f"⊘ Already exists: {task_type_name}")
                    else:
                        click.echo(f"✗ Failed to create: {task_type_name}", err=True)

                except APIClientError4xx as e:
                    click.echo(f"✗ Error creating plan for {task_type_name}: {e}", err=True)

            # Step 7: Display summary
            click.echo(f"\n{'='*60}")
            click.echo("Maintenance Plan Setup Complete\n")

            if created_plans:
                click.echo(f"✓ Created {len(created_plans)} plan(s):")
                for plan in created_plans:
                    click.echo(f"  • {plan}")

            if skipped_plans:
                click.echo(f"\n⊘ Skipped {len(skipped_plans)} plan(s):")
                for plan in skipped_plans:
                    click.echo(f"  • {plan}")

            if not created_plans and not skipped_plans:
                click.echo("No new plans created (all already exist)")

    except (APIConnectionError, APITimeoutError):
        click.echo("\n✗ Error: Unable to connect to API", err=True)
    except Exception as e:
        click.echo(f"\n✗ Error: {str(e)}", err=True)


@click.command(name="create-item")
def create_item():
    """Create a new item in the system."""

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
    selected_type_id = None
    while True:
        selection = click.prompt(f"Select an item type (1-{len(item_types)})", type=str, default="").strip()
        if not selection:
            click.echo("Error: Please select an item type", err=True)
            continue

        try:
            selection_num = int(selection)
            if 1 <= selection_num <= len(item_types):
                selected_type_id = item_types[selection_num - 1].get("id")
                break
            else:
                click.echo(f"Error: Please enter a number between 1 and {len(item_types)}", err=True)
        except ValueError:
            click.echo(f"Error: Please enter a valid number between 1 and {len(item_types)}", err=True)

    # Phase 2: Collect item name (required)
    while True:
        name = click.prompt("Enter item name", type=str, default="").strip()
        if not name:
            click.echo("Error: Name cannot be empty", err=True)
            continue

        if len(name) > 255:
            click.echo("Error: Name must be 255 characters or less", err=True)
            continue

        break

    # Phase 3: Collect acquired date (optional)
    acquired_at = None
    while True:
        date_input = click.prompt(
            "Enter acquisition date (yyyy-mm-dd, or press Enter to skip)",
            type=str,
            default=""
        ).strip()

        if not date_input:
            # User skipped
            break

        # Validate date format
        try:
            date_obj = datetime.strptime(date_input, "%Y-%m-%d")
            acquired_at = date_obj.date().isoformat()
            break
        except ValueError:
            click.echo("Error: Invalid date format. Please use yyyy-mm-dd (e.g., 2015-06-15)", err=True)

    # Phase 4: Collect custom details (loop)
    details = {}
    while True:
        add_detail = click.prompt(
            "Would you like to save any other information about this item? (yes/no, or press Enter to skip)",
            type=str,
            default="no"
        ).strip().lower()

        if add_detail not in ("yes", "y", ""):
            if add_detail == "no" or add_detail == "n":
                break
            click.echo("Please enter 'yes' or 'no'", err=True)
            continue

        if add_detail in ("yes", "y"):
            field_name = click.prompt(
                "Enter the name for the information (or press Enter to finish)",
                type=str,
                default=""
            ).strip()

            if not field_name:
                break

            # Normalize field name
            normalized_field = _translate_field_name(field_name)

            # Prompt for value
            field_value = click.prompt(
                f"What value would you like to submit for {normalized_field}?",
                type=str,
                default=""
            ).strip()

            if field_value:
                # Convert value type
                converted_value = _convert_value_type(field_value)
                details[normalized_field] = converted_value
                click.echo(f"✓ Added: {normalized_field} = {converted_value}")
        else:
            # Empty input means skip
            break

    # Phase 5: Submit to API
    try:
        with APIClient() as client:
            # Build request payload
            payload = {
                "item_type_id": selected_type_id,
                "name": name,
            }

            if acquired_at:
                payload["acquired_at"] = acquired_at

            if details:
                payload["details"] = details

            # POST to /items endpoint (x-user-id header automatically included by APIClient)
            response = client._make_request("POST", "/items", data=payload)

            # Phase 6: Display result
            if response.status_code == 201:
                item_data = response.data.get("data", {})
                click.echo("\n✓ Success: Item created successfully!\n")
                click.echo("Item Details:")
                click.echo(f"  ID:          {item_data.get('id')}")
                click.echo(f"  Name:        {item_data.get('name')}")
                click.echo(f"  Item Type:   {item_data.get('item_type_id')}")
                if item_data.get('acquired_at'):
                    click.echo(f"  Acquired:    {item_data.get('acquired_at')}")
                if item_data.get('details'):
                    click.echo(f"  Details:     {json.dumps(item_data.get('details'))}")
                click.echo(f"  Created:     {item_data.get('created_at')}")
            else:
                click.echo(f"Error: Unexpected response status {response.status_code}", err=True)

    except APIClientError4xx as e:
        # Handle client errors (400, 404, 422)
        try:
            error_data = json.loads(e.response_body) if isinstance(e.response_body, str) else e.response_body
        except (json.JSONDecodeError, TypeError):
            error_data = {}

        if e.status_code == 404:
            click.echo(f"\n✗ Error: {error_data.get('message', 'Resource not found')}", err=True)
            click.echo("Please verify the item type exists and try again.", err=True)
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

    except (APIConnectionError, APITimeoutError):
        click.echo("\n✗ Error: Unable to connect to API", err=True)
        click.echo("Please ensure the API service is running and try again.", err=True)

    except APIServerError5xx:
        click.echo("\n✗ Error: Server error occurred", err=True)
        click.echo("Please try again later. If the problem persists, contact support.", err=True)

    except Exception as e:
        click.echo(f"\n✗ Error: An unexpected error occurred: {str(e)}", err=True)
