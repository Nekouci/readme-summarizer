"""Comprehensive automated tests for the postprocess CLI command."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

import summarize_readme.cli as cli_module


runner = CliRunner()


SAMPLE_CONTENT = """# Sample Project

Simple content for post-processing validation.

## Features

- Feature A
- Feature B

## Code

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

Read [docs](https://example.com/docs).
"""


@pytest.mark.parametrize(
    ("export_format", "suffix", "markers"),
    [
        ("html-standalone", ".html", ["<!DOCTYPE html>", "<html", "<style>"]),
        ("html-styled", ".html", ["<h1>", "<p>"]),
        ("markdown-enhanced", ".md", ["## Table of Contents", "Sample Project"]),
        ("json-enriched", ".json", ['"content"', '"statistics"', '"processing"']),
        ("social-snippet", ".json", ['"twitter"', '"linkedin"', '"slack"']),
        ("pdf-ready", ".html", ["@page", '<style media="print">']),
    ],
)
def test_postprocess_all_formats_local_file(
    tmp_path: Path,
    export_format: str,
    suffix: str,
    markers: list[str],
):
    """Validate all postprocess export formats using a local markdown file."""
    input_file = tmp_path / "input.md"
    input_file.write_text(SAMPLE_CONTENT, encoding="utf-8")

    output_file = tmp_path / f"output{suffix}"

    result = runner.invoke(
        cli_module.app,
        [
            "postprocess",
            str(input_file),
            "--format",
            export_format,
            "--output",
            str(output_file),
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert output_file.exists()

    output = output_file.read_text(encoding="utf-8")
    for marker in markers:
        assert marker in output

    if export_format == "json-enriched":
        parsed = json.loads(output)
        assert "statistics" in parsed
        assert "extracted" in parsed

    if export_format == "social-snippet":
        parsed = json.loads(output)
        assert "twitter" in parsed
        assert "linkedin" in parsed
        assert "slack" in parsed


@pytest.mark.parametrize(
    ("source", "metadata"),
    [
        (
            "microsoft/vscode",
            {
                "type": "github_repo",
                "owner": "microsoft",
                "repo": "vscode",
                "url": "https://github.com/microsoft/vscode",
            },
        ),
        (
            "https://github.com/python/cpython",
            {
                "type": "github_repo",
                "owner": "python",
                "repo": "cpython",
                "url": "https://github.com/python/cpython",
            },
        ),
        (
            "https://example.com/readme.md",
            {
                "type": "url",
                "url": "https://example.com/readme.md",
            },
        ),
    ],
)
def test_postprocess_source_types_with_resolver_patch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    source: str,
    metadata: dict,
):
    """Validate resolver-driven source types without relying on external network."""

    def fake_resolve(self, given_source: str):
        assert given_source == source
        return SAMPLE_CONTENT, metadata

    monkeypatch.setattr(cli_module.InputResolver, "resolve", fake_resolve)

    output_file = tmp_path / "resolved_output.html"
    result = runner.invoke(
        cli_module.app,
        [
            "postprocess",
            source,
            "--format",
            "html-standalone",
            "--output",
            str(output_file),
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert output_file.exists()

    output = output_file.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in output
    if metadata.get("repo"):
        assert metadata["repo"] in output


def test_postprocess_missing_source_returns_error(monkeypatch: pytest.MonkeyPatch):
    """Validate error handling when resolver fails with FileNotFoundError."""

    def fake_resolve(self, given_source: str):
        raise FileNotFoundError(f"File not found: {given_source}")

    monkeypatch.setattr(cli_module.InputResolver, "resolve", fake_resolve)

    result = runner.invoke(
        cli_module.app,
        ["postprocess", "does-not-exist-xyz.md", "--format", "social-snippet"],
    )

    assert result.exit_code != 0
    assert "Source not found" in result.stdout
