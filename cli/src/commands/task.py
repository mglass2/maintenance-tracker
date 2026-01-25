"""Task management commands for the Maintenance Tracker CLI."""

import json
from datetime import datetime, date
from typing import Any, Optional

import click

from src.api_client import (
    APIClient,
    APIClientError4xx,
    APIConnectionError,
    APIServerError5xx,
    APITimeoutError,
)
from src.session import get_active_user_id


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


def _create_new_task_type() -> Optional[int]:
    """Create a new task type interactively.

    Returns:
        task_type_id or None on error
    """
    click.echo("\n--- Create New Task Type ---\n")

    # Collect name
    while True:
        name = click.prompt("Enter task type name", type=str, default="").strip()
        if not name:
            click.echo("Error: Name cannot be empty", err=True)
            continue
        if len(name) > 255:
            click.echo("Error: Name must be 255 characters or less", err=True)
            continue
        break

    # Collect description (optional)
    description = click.prompt(
        "Enter task type description (or press Enter to skip)",
        type=str,
        default=""
    ).strip()

    if not description:
        description = None

    # Submit to API
    payload = {"name": name}
    if description:
        payload["description"] = description

    try:
        with APIClient() as client:
            response = client._make_request("POST", "/task-types", data=payload)

            if response.status_code == 201:
                task_type_data = response.data.get("data", {})
                task_type_id = task_type_data.get("id")
                click.echo(f"\n✓ Task type '{name}' created successfully")
                return task_type_id
            else:
                click.echo(f"Error: Unexpected response status {response.status_code}", err=True)
                return None

    except APIClientError4xx as e:
        try:
            error_data = json.loads(e.response_body) if isinstance(e.response_body, str) else e.response_body
        except (json.JSONDecodeError, TypeError):
            error_data = {}

        if e.status_code == 409:
            click.echo("\n✗ Error: A task type with this name already exists", err=True)
        else:
            click.echo(f"\n✗ Error: {error_data.get('message', 'Request failed')}", err=True)
        return None

    except Exception as e:
        click.echo(f"\n✗ Error: {str(e)}", err=True)
        return None


@click.command(name="create-task")
def create_task():
    """Create a new task record for an item.

    A task represents completed maintenance on an item. This command guides
    you through selecting the item, task type, and recording completion details.
    """
    # Phase 1: Check authentication
    user_id = get_active_user_id()
    if not user_id:
        click.echo("\n✗ Error: No user is currently selected", err=True)
        click.echo("Please run 'select-user' command first to choose your user identity.", err=True)
        return

    # Phase 2: Fetch and select item
    try:
        with APIClient() as client:
            response = client._make_request("GET", f"/items/users/{user_id}")
            if response.status_code != 200:
                click.echo("Error: Unable to fetch your items from API", err=True)
                return

            data = response.data.get("data", {})
            items = data.get("items", [])

            if not items:
                click.echo("\n⊘ You don't have any items yet", err=True)
                click.echo("Please create an item first using the 'create-item' command.", err=True)
                return

    except (APIConnectionError, APITimeoutError):
        click.echo("\n✗ Error: Unable to connect to API", err=True)
        return
    except Exception as e:
        click.echo(f"\n✗ Error: {str(e)}", err=True)
        return

    # Display items and prompt for selection
    click.echo("\nYour Items:")
    for idx, item in enumerate(items, 1):
        name = item.get("name", "Unknown")
        item_type_name = item.get("item_type_name", "")
        if item_type_name:
            click.echo(f"  {idx}. {name} ({item_type_name})")
        else:
            click.echo(f"  {idx}. {name}")

    # Validate selection
    selected_item = None
    while True:
        selection = click.prompt(f"Select an item (1-{len(items)})", type=str, default="").strip()
        if not selection:
            click.echo("Error: Please select an item", err=True)
            continue

        try:
            selection_num = int(selection)
            if 1 <= selection_num <= len(items):
                selected_item = items[selection_num - 1]
                break
            else:
                click.echo(f"Error: Please enter a number between 1 and {len(items)}", err=True)
        except ValueError:
            click.echo("Error: Please enter a valid number", err=True)

    selected_item_id = selected_item.get("id")
    selected_item_name = selected_item.get("name")

    # Phase 3: Fetch maintenance plans for the selected item
    try:
        with APIClient() as client:
            response = client._make_request(
                "GET",
                f"/item_maintenance_plans/items/{selected_item_id}"
            )

            if response.status_code == 200:
                plans = response.data.get("data", [])
            else:
                plans = []

    except Exception:
        plans = []

    click.echo(f"\n{'='*60}")

    # Phase 4: Select task type from plans or "Other"

    # Build list of task types from plans
    task_type_options = []
    if plans:
        # Fetch full task type details to show names/descriptions
        try:
            with APIClient() as client:
                response = client._make_request("GET", "/task-types")
                if response.status_code == 200:
                    all_task_types = response.data.get("data", {}).get("task_types", [])

                    # Filter to only task types in the plans
                    plan_task_type_ids = {plan.get("task_type_id") for plan in plans}
                    task_type_options = [
                        tt for tt in all_task_types
                        if tt.get("id") in plan_task_type_ids
                    ]
        except Exception:
            pass

    # Display task type options
    click.echo("\nAvailable Task Types:")
    for idx, task_type in enumerate(task_type_options, 1):
        name = task_type.get("name", "Unknown")
        description = task_type.get("description", "")
        if description:
            click.echo(f"  {idx}. {name} - {description}")
        else:
            click.echo(f"  {idx}. {name}")

    # Add "Other" option
    other_option_index = len(task_type_options) + 1
    click.echo(f"  {other_option_index}. Other (create new task type)")

    # Validate selection
    selected_task_type_id = None
    selected_task_type_name = None
    selected_plan = None

    while True:
        selection = click.prompt(
            f"Select a task type (1-{other_option_index})",
            type=str,
            default=""
        ).strip()

        if not selection:
            click.echo("Error: Please select a task type", err=True)
            continue

        try:
            selection_num = int(selection)
            if 1 <= selection_num < other_option_index:
                # Selected from existing task types
                selected_task_type = task_type_options[selection_num - 1]
                selected_task_type_id = selected_task_type.get("id")
                selected_task_type_name = selected_task_type.get("name")

                # Find the matching plan for custom_interval
                selected_plan = next(
                    (p for p in plans if p.get("task_type_id") == selected_task_type_id),
                    None
                )
                break

            elif selection_num == other_option_index:
                # "Other" option - create new task type
                selected_task_type_id = _create_new_task_type()
                if selected_task_type_id is None:
                    return  # Error occurred, exit
                selected_plan = None  # No plan for new task type
                break

            else:
                click.echo(f"Error: Please enter a number between 1 and {other_option_index}", err=True)
        except ValueError:
            click.echo("Error: Please enter a valid number", err=True)

    click.echo(f"\n{'='*60}")

    # Phase 5: Collect completion date, notes, and cost

    # Completion date (default: today)
    completed_at = None
    today_str = date.today().isoformat()

    while True:
        date_input = click.prompt(
            f"Enter completion date (yyyy-mm-dd) [today: {today_str}]",
            type=str,
            default=today_str
        ).strip()

        if not date_input:
            date_input = today_str

        try:
            date_obj = datetime.strptime(date_input, "%Y-%m-%d")
            completed_at = date_obj.date().isoformat()
            break
        except ValueError:
            click.echo("Error: Invalid date format. Please use yyyy-mm-dd (e.g., 2026-01-24)", err=True)

    # Notes (optional)
    notes = click.prompt(
        "Enter notes about this task (or press Enter to skip)",
        type=str,
        default=""
    ).strip()

    if not notes:
        notes = None

    # Cost (optional)
    cost = None
    while True:
        cost_input = click.prompt(
            "Enter cost (or press Enter to skip)",
            type=str,
            default=""
        ).strip()

        if not cost_input:
            break

        try:
            cost_value = float(cost_input)
            if cost_value < 0:
                click.echo("Error: Cost cannot be negative", err=True)
                continue
            cost = cost_value
            break
        except ValueError:
            click.echo("Error: Please enter a valid number", err=True)

    # Phase 6: Collect custom interval details (if plan has custom_interval)
    details = None

    if selected_plan and selected_plan.get("custom_interval"):
        custom_interval = selected_plan.get("custom_interval")

        click.echo(f"\n{'='*60}")
        click.echo("This task type has custom tracking fields.")
        click.echo("Please provide values for the following:\n")

        details = {}
        for key in custom_interval.keys():
            while True:
                value_input = click.prompt(f"Enter {key}", type=str, default="").strip()

                if not value_input:
                    click.echo(f"Error: {key} is required", err=True)
                    continue

                # Convert type
                converted_value = _convert_value_type(value_input)
                details[key] = converted_value
                click.echo(f"✓ {key} = {converted_value}")
                break

    # Phase 7: Submit to API
    payload = {
        "item_id": selected_item_id,
        "task_type_id": selected_task_type_id,
        "completed_at": completed_at,
    }

    if notes:
        payload["notes"] = notes

    if cost is not None:
        payload["cost"] = cost

    if details:
        payload["details"] = details

    try:
        with APIClient() as client:
            response = client._make_request("POST", "/tasks", data=payload)

            if response.status_code == 201:
                task_data = response.data.get("data", {})

                # Phase 8: Display confirmation
                click.echo("\n✓ Success: Task created successfully!\n")
                click.echo("Task Details:")
                click.echo(f"  ID:           {task_data.get('id')}")
                click.echo(f"  Item:         {selected_item_name}")
                click.echo(f"  Task Type:    {selected_task_type_name or task_data.get('task_type_id')}")
                click.echo(f"  Completed:    {task_data.get('completed_at')}")
                if task_data.get('notes'):
                    click.echo(f"  Notes:        {task_data.get('notes')}")
                if task_data.get('cost'):
                    click.echo(f"  Cost:         ${task_data.get('cost')}")
                if task_data.get('details'):
                    click.echo(f"  Details:      {json.dumps(task_data.get('details'))}")
                click.echo(f"  Created:      {task_data.get('created_at')}")
            else:
                click.echo(f"Error: Unexpected response status {response.status_code}", err=True)

    except APIClientError4xx as e:
        try:
            error_data = json.loads(e.response_body) if isinstance(e.response_body, str) else e.response_body
        except (json.JSONDecodeError, TypeError):
            error_data = {}

        if e.status_code == 404:
            click.echo(f"\n✗ Error: {error_data.get('message', 'Resource not found')}", err=True)
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

    except APIServerError5xx:
        click.echo("\n✗ Error: Server error occurred", err=True)

    except Exception as e:
        click.echo(f"\n✗ Error: An unexpected error occurred: {str(e)}", err=True)
