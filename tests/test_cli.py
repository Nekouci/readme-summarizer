"""
Tests for CLI functionality.
"""

import pytest
from typer.testing import CliRunner
from summarize_readme.cli import app

runner = CliRunner()


def test_version_command():
    """Test version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "README Summarizer" in result.stdout
    assert "version" in result.stdout


def test_help_command():
    """Test help output."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "README" in result.stdout or "summarize" in result.stdout


def test_summarize_help():
    """Test summarize command help."""
    result = runner.invoke(app, ["summarize", "--help"])
    assert result.exit_code == 0
    assert "source" in result.stdout.lower() or "output" in result.stdout.lower()
