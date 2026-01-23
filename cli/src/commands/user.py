"""User management commands for the Maintenance Tracker CLI."""

import json
import re
from typing import Optional

import click

from src.api_client import (
    APIClient,
    APIClientError4xx,
    APIConnectionError,
    APIServerError5xx,
    APITimeoutError,
)


@click.command(name="create-user")
def create_user():
    """Create a new user in the system."""

    # Prompt for name with validation (re-prompt on error)
    while True:
        name = click.prompt("Enter user name", type=str, default="").strip()
        if not name:
            click.echo("Error: Name cannot be empty", err=True)
            continue

        if len(name) > 255:
            click.echo("Error: Name must be 255 characters or less", err=True)
            continue

        break

    # Prompt for email with basic format validation (re-prompt on error)
    while True:
        email = click.prompt("Enter user email", type=str, default="").strip()
        if not email:
            click.echo("Error: Email cannot be empty", err=True)
            continue

        # Basic email format check (simple regex)
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            click.echo("Error: Invalid email format", err=True)
            continue

        break

    # Call API with error handling
    try:
        with APIClient() as client:
            data = {
                "name": name,
                "email": email
            }
            response = client._make_request("POST", "/users", data=data)

            # Display success message
            if response.status_code == 201:
                user_data = response.data.get("data", {})
                click.echo("\n✓ Success: User created successfully!\n")
                click.echo("User Details:")
                click.echo(f"  ID:      {user_data.get('id')}")
                click.echo(f"  Name:    {user_data.get('name')}")
                click.echo(f"  Email:   {user_data.get('email')}")
                click.echo(f"  Created: {user_data.get('created_at')}")
            else:
                click.echo(f"Error: Unexpected response status {response.status_code}", err=True)

    except APIClientError4xx as e:
        # Handle client errors (400, 409, 422)
        try:
            error_data = json.loads(e.response_body) if isinstance(e.response_body, str) else e.response_body
        except (json.JSONDecodeError, TypeError):
            error_data = {}

        if e.status_code == 409:
            # Duplicate email
            click.echo(f"\n✗ Error: {error_data.get('message', 'Email already exists')}", err=True)
            click.echo("Please use a different email address.", err=True)
        elif e.status_code == 400:
            # Validation error
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
