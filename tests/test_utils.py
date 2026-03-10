"""
Tests for utility functions.
"""

import pytest
from pathlib import Path
from summarize_readme.utils import (
    validate_url,
    sanitize_filename,
    format_file_size,
    extract_github_info,
)


def test_validate_url():
    """Test URL validation."""
    assert validate_url("https://example.com") is True
    assert validate_url("http://example.com") is True
    assert validate_url("ftp://example.com") is False
    assert validate_url("not-a-url") is False
    assert validate_url("/local/path") is False


def test_sanitize_filename():
    """Test filename sanitization."""
    assert sanitize_filename("file<>name.txt") == "file__name.txt"
    assert sanitize_filename("file:name") == "file_name"
    assert sanitize_filename("  file.txt  ") == "file.txt"
    assert sanitize_filename("") == "unnamed"


def test_format_file_size():
    """Test file size formatting."""
    assert "B" in format_file_size(500)
    assert "KB" in format_file_size(1024)
    assert "MB" in format_file_size(1024 * 1024)
    assert "GB" in format_file_size(1024 * 1024 * 1024)


def test_extract_github_info():
    """Test GitHub info extraction."""
    url = "https://github.com/user/repo"
    info = extract_github_info(url)
    
    assert info is not None
    assert info['owner'] == "user"
    assert info['repo'] == "repo"
    assert "github.com" in info['url']
    
    assert extract_github_info("https://example.com") is None
