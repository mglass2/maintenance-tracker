"""Authentication and user selection commands."""

import sys

import click

from src.api_client import APIClient
from src import session


@click.command(name="select-user")
def select_user():
    """Select your user identity from the system."""
    try:
        # Fetch all users from API
        with APIClient() as client:
            response = client._make_request("GET", "/users")
            users = response.data.get("data", [])

        if not users:
            click.echo("Error: No users found in the system.", err=True)
            click.echo(
                "Please create a user first using the 'create-user' command.",
                err=True
            )
            return

        # Display users in a numbered list
        click.echo("\nAvailable users:")
        for idx, user in enumerate(users, 1):
            click.echo(f"  {idx}. {user['name']} ({user['email']})")

        # Prompt for selection with validation/retry
        while True:
            try:
                selection = click.prompt(
                    "\nSelect user number",
                    type=int,
                    default=""
                )

                if 1 <= selection <= len(users):
                    selected_user = users[selection - 1]
                    session.set_active_user(
                        selected_user['id'],
                        selected_user
                    )
                    click.echo(f"\n✓ Active user: {selected_user['name']}")
                    break
                else:
                    click.echo(
                        f"Error: Please enter a number between 1 and {len(users)}",
                        err=True
                    )
            except (ValueError, click.Abort):
                click.echo("Error: Invalid selection", err=True)

    except Exception as e:
        click.echo(f"\n✗ Error selecting user: {str(e)}", err=True)


@click.command(name="whoami")
def whoami():
    """Show the currently active user."""
    if not session.is_authenticated():
        click.echo("No active user. Use 'select-user' to choose a user.")
        return

    user_data = session.get_active_user_data()
    click.echo(f"\nActive User:")
    click.echo(f"  ID:    {user_data['id']}")
    click.echo(f"  Name:  {user_data['name']}")
    click.echo(f"  Email: {user_data['email']}")


@click.command(name="switch-user")
def switch_user():
    """Switch to a different user."""
    click.echo("Switching user...")
    # Invoke select_user command
    ctx = click.Context(select_user)
    ctx.invoke(select_user)


@click.command(name="logout")
def logout():
    """Log out and exit the CLI."""
    if session.is_authenticated():
        user_data = session.get_active_user_data()
        session.clear_session()
        click.echo(f"\n✓ Logged out: {user_data['name']}")
    else:
        click.echo("No active session.")

    click.echo("Exiting...")
    sys.exit(0)
