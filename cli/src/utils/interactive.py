"""Interactive mode utility for the Maintenance Tracker CLI."""

import click
import sys

from src import session
from src.commands.auth import select_user


def run_interactive_mode(cli_group):
    """Run the CLI in interactive mode, accepting commands until exit.

    Args:
        cli_group: The click CLI group to run commands against
    """
    click.echo("Maintenance Tracker CLI - type 'help' for available commands or 'exit' to quit")

    # Check if user is selected, prompt if not
    if not session.is_authenticated():
        click.echo("\n" + "="*60)
        click.echo("User Identity Required")
        click.echo("="*60)

        # Retry user selection up to 3 times
        max_retries = 3
        for attempt in range(max_retries):
            ctx = click.Context(select_user)
            ctx.invoke(select_user)

            if session.is_authenticated():
                break

            if attempt < max_retries - 1:
                click.echo(
                    f"\nRetrying user selection ({attempt + 2}/{max_retries})...\n"
                )
            else:
                click.echo(
                    "\nError: Could not select user after multiple attempts.\n"
                    "Please ensure the API service is running and try again."
                )
                sys.exit(1)

    # Welcome message with active user
    user_data = session.get_active_user_data()
    click.echo(f"\nWelcome, {user_data['name']}!")
    click.echo("="*60 + "\n")

    while True:
        try:
            user_input = click.prompt("tracker").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                click.echo("Goodbye!")
                break

            # Handle 'help' command - show general help
            if user_input.lower() == "help":
                try:
                    cli_group(["--help"], standalone_mode=False)
                except click.exceptions.Exit:
                    pass
                except Exception as e:
                    click.echo(f"Error: {e}", err=True)
                continue

            # Handle 'help <command>' - show command-specific help
            if user_input.lower().startswith("help "):
                command_name = user_input[5:].strip()
                if command_name:
                    try:
                        cli_group([command_name, "--help"], standalone_mode=False)
                    except click.exceptions.Exit:
                        pass
                    except Exception as e:
                        click.echo(f"Error: {e}", err=True)
                else:
                    try:
                        cli_group(["--help"], standalone_mode=False)
                    except click.exceptions.Exit:
                        pass
                    except Exception as e:
                        click.echo(f"Error: {e}", err=True)
                continue

            # Parse and execute the command
            args = user_input.split()
            try:
                cli_group(args, standalone_mode=False)
            except click.exceptions.Exit:
                pass
            except Exception as e:
                click.echo(f"Error: {e}", err=True)
        except (KeyboardInterrupt, EOFError):
            click.echo("\nGoodbye!")
            break
