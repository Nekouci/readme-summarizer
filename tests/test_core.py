"""
Tests for core summarization functionality.
"""

import pytest
from summarize_readme.core import ReadmeSummarizer, SummaryFormat


def test_summarizer_initialization():
    """Test ReadmeSummarizer initialization."""
    summarizer = ReadmeSummarizer(max_length=100)
    assert summarizer.max_length == 100
    assert summarizer.include_badges is True


def test_parse_markdown():
    """Test markdown parsing."""
    summarizer = ReadmeSummarizer()
    content = """
# Test Project

This is a test description.

## Features

- Feature 1
- Feature 2

[Link](https://example.com)
"""
    
    parsed = summarizer._parse_markdown(content)
    
    assert parsed['title'] == "Test Project"
    assert "test description" in parsed['description'].lower()
    assert "Features" in parsed['sections']
    assert len(parsed['links']) >= 1


def test_analyze():
    """Test content analysis."""
    summarizer = ReadmeSummarizer()
    content = """
# Project

Description here.

## Section 1
## Section 2

[Link](https://example.com)
"""
    
    analysis = summarizer.analyze(content)
    
    assert analysis['lines'] > 0
    assert analysis['words'] > 0
    assert analysis['sections'] >= 2
    assert analysis['links'] >= 1


def test_summarize_text_format():
    """Test text format summarization."""
    summarizer = ReadmeSummarizer()
    content = """
# My Project

A simple project description.

## Installation
## Usage
"""
    
    summary = summarizer.summarize(content, output_format=SummaryFormat.TEXT)
    
    assert "My Project" in summary
    assert len(summary) > 0


def test_summarize_json_format():
    """Test JSON format summarization."""
    import json
    
    summarizer = ReadmeSummarizer()
    content = """
# Test Project

Description of the project.
"""
    
    summary = summarizer.summarize(content, output_format=SummaryFormat.JSON)
    data = json.loads(summary)
    
    assert "title" in data
    assert data['title'] == "Test Project"
    assert "summary" in data


def test_truncate_text():
    """Test text truncation."""
    summarizer = ReadmeSummarizer()
    
    text = " ".join(["word"] * 100)
    truncated = summarizer._truncate_text(text, 10)
    
    assert len(truncated.split()) <= 11  # 10 words + "..."
    assert truncated.endswith("...")
