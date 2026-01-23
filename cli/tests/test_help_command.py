"""Test the help command in the CLI application."""

from unittest.mock import patch
from click.testing import CliRunner
from src.main import cli, interactive_mode


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


def test_interactive_mode_help_command(capsys):
    """Test that typing 'help' in interactive mode shows general help."""
    # Mock session to skip user selection
    with patch("src.main.session.is_authenticated", return_value=True), \
         patch("src.main.session.get_active_user_data", return_value={"name": "Test User"}), \
         patch("click.prompt", side_effect=["help", "exit"]):
        interactive_mode()

    # Capture stdout
    captured = capsys.readouterr()
    help_output = captured.out

    # Verify that help was displayed
    assert "Maintenance Tracker CLI" in help_output
    assert "Commands:" in help_output


def test_interactive_mode_help_case_insensitive(capsys):
    """Test that 'help' is case insensitive in interactive mode."""
    # Mock session to skip user selection
    with patch("src.main.session.is_authenticated", return_value=True), \
         patch("src.main.session.get_active_user_data", return_value={"name": "Test User"}), \
         patch("click.prompt", side_effect=["HELP", "exit"]):
        interactive_mode()

    # Capture stdout
    captured = capsys.readouterr()
    help_output = captured.out

    # Verify that help was displayed
    assert "Maintenance Tracker CLI" in help_output


def test_interactive_mode_help_command_specific(capsys):
    """Test that 'help <command>' shows command-specific help in interactive mode."""
    # Mock session to skip user selection
    with patch("src.main.session.is_authenticated", return_value=True), \
         patch("src.main.session.get_active_user_data", return_value={"name": "Test User"}), \
         patch("click.prompt", side_effect=["help hello", "exit"]):
        interactive_mode()

    # Capture stdout
    captured = capsys.readouterr()
    help_output = captured.out

    # Verify that command-specific help was displayed
    assert "Test command to verify CLI is working" in help_output


def test_interactive_mode_help_nonexistent_command(capsys):
    """Test that 'help' with a non-existent command shows an error."""
    # Mock session to skip user selection
    with patch("src.main.session.is_authenticated", return_value=True), \
         patch("src.main.session.get_active_user_data", return_value={"name": "Test User"}), \
         patch("click.prompt", side_effect=["help nonexistent", "exit"]):
        interactive_mode()

    # Capture stderr (Click writes errors to stderr)
    captured = capsys.readouterr()
    output = captured.err + captured.out

    # Verify that an error message was displayed
    assert "Error" in output or "no such command" in output.lower()
