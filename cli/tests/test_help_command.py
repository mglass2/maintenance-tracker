"""Test the help command in the CLI application."""

from click.testing import CliRunner
from src.main import cli


def test_help_command_shows_available_commands():
    """Test that the help command displays available commands."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    # Verify the command executed successfully
    assert result.exit_code == 0

    # Verify the output contains the CLI description
    assert "Maintenance Tracker CLI" in result.output

    # Verify available commands are listed
    assert "hello" in result.output
    assert "Commands:" in result.output
