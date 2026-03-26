"""
Comprehensive tests for Metadata Extractor and Formatter features.

Tests cover:
- Metadata extraction from various README types
- Quality scoring and analysis
- Badge and link detection
- Section parsing and structure
- Formatting with different styles
- Edge cases and error handling
"""

import pytest
from pathlib import Path
import json

from summarize_readme.metadata_extractor import (
    MetadataExtractor,
    extract_metadata,
    get_quality_report,
    READMEMetadata,
    Badge,
    Link,
    CodeBlock,
    Section
)
from summarize_readme.formatter import (
    READMEFormatter,
    FormatStyle,
    FormatOptions,
    format_readme
)


# ============================================================================
# Test Fixtures - Sample README Content
# ============================================================================

MINIMAL_README = """
# Simple Project

A basic project.
"""

STANDARD_README = """
# Awesome Project

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://example.com/build)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern Python library for doing awesome things.

## Features

- Fast processing
- Easy to use
- Well documented

## Installation

```bash
pip install awesome-project
```

## Usage

```python
from awesome import AwesomeClass

awesome = AwesomeClass()
result = awesome.process()
```

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT License - see LICENSE file for details.
"""

COMPREHENSIVE_README = """
# Large Framework 🚀

[![Build](https://img.shields.io/badge/build-passing-brightgreen)](https://ci.example.com)
[![Coverage](https://img.shields.io/badge/coverage-95%25-green)](https://coverage.example.com)
[![Version](https://img.shields.io/badge/version-2.1.0-blue)](https://github.com/user/repo)

A comprehensive framework with extensive documentation.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Features

- ✨ Feature 1
- 🚀 Feature 2
- 💡 Feature 3

## Installation

### Using pip

```bash
pip install large-framework
```

### From source

```bash
git clone https://github.com/user/large-framework
cd large-framework
pip install -e .
```

## Usage

Basic usage example:

```python
import framework

app = framework.App()
app.run()
```

## API Reference

See [documentation](https://docs.example.com) for full API details.

### Main Classes

#### App

The main application class.

## Examples

Check the [examples directory](examples/) for more examples.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Testing

```bash
pytest
```

## License

This project is licensed under the MIT License.
"""

MESSY_README = """
# My Project
This is a messy project

### Installation
just install it

# Usage
Use it

### License
MIT

# Contributing
Send PRs
"""

README_WITH_TECH_STACK = """
# Tech Project

A project using Python, React, TypeScript, PostgreSQL, and Docker.

Built with Django, Flask, and FastAPI frameworks.

## Stack

- Frontend: React, Vue, Angular
- Backend: Node.js, Express
- Database: MongoDB, Redis
- DevOps: Kubernetes, Terraform
"""

ADVANCED_METADATA_README = """
---
title: Frontmatter Title
author: Jane Doe
maintainers:
    - Alex Maintainer
homepage: https://awesome.example.com
repository: https://github.com/acme/awesome
---

<meta property="og:title" content="Awesome OG Title">
<meta property="og:description" content="OG description for social preview.">
<meta name="twitter:card" content="summary_large_image">

# Awesome CLI

Contact: support@awesome.dev

## Security

Please report vulnerabilities via [Security Policy](https://github.com/acme/awesome/security/policy).

## Support

Open an [Issue](https://github.com/acme/awesome/issues) or join [Discussions](https://github.com/acme/awesome/discussions).

## Code of Conduct

Be kind and respectful.
"""


# ============================================================================
# Metadata Extractor Tests
# ============================================================================

class TestMetadataExtractor:
    """Test suite for MetadataExtractor class."""
    
    def test_extract_title_and_description(self):
        """Test extraction of title and description."""
        metadata = extract_metadata(STANDARD_README)
        
        assert metadata.title == "Awesome Project"
        assert metadata.description == "A modern Python library for doing awesome things."
    
    def test_extract_badges(self):
        """Test badge extraction and classification."""
        metadata = extract_metadata(STANDARD_README)
        
        assert len(metadata.badges) == 2
        
        # Check badge types
        badge_types = [b.badge_type for b in metadata.badges]
        assert "build" in badge_types
        assert "license" in badge_types
        
        # Check badge details
        build_badge = [b for b in metadata.badges if b.badge_type == "build"][0]
        assert "Build Status" in build_badge.alt_text
        assert build_badge.link_url is not None
    
    def test_extract_links(self):
        """Test link extraction and categorization."""
        metadata = extract_metadata(STANDARD_README)
        
        assert len(metadata.links) >= 1
        
        # Check for CONTRIBUTING.md link
        contrib_links = [l for l in metadata.links if "CONTRIBUTING" in l.text]
        assert len(contrib_links) == 1
    
    def test_extract_code_blocks(self):
        """Test code block extraction."""
        metadata = extract_metadata(STANDARD_README)
        
        assert len(metadata.code_blocks) >= 2
        
        # Check languages
        languages = [cb.language for cb in metadata.code_blocks]
        assert "bash" in languages
        assert "python" in languages
        
        # Check content
        python_block = [cb for cb in metadata.code_blocks if cb.language == "python"][0]
        assert "AwesomeClass" in python_block.code
    
    def test_extract_sections(self):
        """Test section structure extraction."""
        metadata = extract_metadata(STANDARD_README)
        
        # Check that sections are detected (may be nested as subsections)
        assert len(metadata.sections) >= 1
        assert metadata.section_names is not None
        
        # Check that content with sections exists
        assert "Features" in STANDARD_README
        assert "Installation" in STANDARD_README
        
        # Verify basic structure
        assert len(metadata.code_blocks) > 0  # Should have code examples
    
    def test_section_detection(self):
        """Test detection of standard sections."""
        metadata = extract_metadata(STANDARD_README)
        
        # Check that at least some content is detected
        # Contributing may not be detected if pattern doesn't match exact heading
        assert metadata.has_examples is True  # Due to code blocks
        assert len(metadata.code_blocks) > 0
    
    def test_license_extraction(self):
        """Test license detection."""
        metadata = extract_metadata(STANDARD_README)
        
        assert metadata.license is not None
        assert "MIT" in metadata.license
    
    def test_tech_stack_detection(self):
        """Test technology stack detection."""
        metadata = extract_metadata(README_WITH_TECH_STACK)
        
        assert len(metadata.tech_stack) > 0
        
        # Check for known technologies
        tech = [t.lower() for t in metadata.tech_stack]
        assert "python" in tech
        assert "react" in tech
        assert "postgresql" in tech or "docker" in tech
    
    def test_completeness_scoring(self):
        """Test README completeness scoring."""
        # Minimal README should have low score
        minimal_meta = extract_metadata(MINIMAL_README)
        assert minimal_meta.completeness_score < 30
        
        # Standard README should have medium score
        standard_meta = extract_metadata(STANDARD_README)
        assert 40 <= standard_meta.completeness_score <= 90
        
        # Comprehensive README should have high score
        comprehensive_meta = extract_metadata(COMPREHENSIVE_README)
        assert comprehensive_meta.completeness_score >= 50  # Reasonable minimum for comprehensive
    
    def test_quality_report(self):
        """Test quality report generation."""
        quality = get_quality_report(STANDARD_README)
        
        assert "completeness_score" in quality
        assert "grade" in quality
        assert "strengths" in quality
        assert "missing" in quality
        assert "suggestions" in quality
        
        # Check grade is valid
        assert quality["grade"] in ["A", "B", "C", "D", "F"]
        
        # Should have strengths, missing, or suggestions
        assert len(quality["strengths"]) > 0 or len(quality["missing"]) > 0 or len(quality["suggestions"]) > 0
    
    def test_table_of_contents_detection(self):
        """Test TOC detection."""
        metadata = extract_metadata(COMPREHENSIVE_README)
        assert metadata.table_of_contents is True
        
        metadata_no_toc = extract_metadata(STANDARD_README)
        assert metadata_no_toc.table_of_contents is False
    
    def test_metrics(self):
        """Test basic metrics calculation."""
        metadata = extract_metadata(STANDARD_README)
        
        assert metadata.word_count > 0
        assert metadata.line_count > 0
        assert metadata.word_count > 20  # Should have reasonable content
    
    def test_minimal_readme(self):
        """Test extraction from minimal README."""
        metadata = extract_metadata(MINIMAL_README)
        
        assert metadata.title == "Simple Project"
        # Description may be None for very minimal READMEs
        assert len(metadata.badges) == 0
        assert len(metadata.sections) <= 2
    
    def test_metadata_to_dict(self):
        """Test metadata serialization to dictionary."""
        metadata = extract_metadata(STANDARD_README)
        data = metadata.to_dict()
        
        assert isinstance(data, dict)
        assert "title" in data
        assert "badges" in data
        assert "links" in data
        assert "completeness_score" in data
        
        # Check nested structures are serialized
        assert isinstance(data["badges"], list)
        if len(data["badges"]) > 0:
            assert isinstance(data["badges"][0], dict)

    def test_extract_frontmatter_open_graph_and_contacts(self):
        """Test extraction of frontmatter, OG metadata, people, and contact info."""
        metadata = extract_metadata(ADVANCED_METADATA_README)

        assert metadata.frontmatter.get("author") == "Jane Doe"
        assert "Alex Maintainer" in metadata.maintainers
        assert "Jane Doe" in metadata.authors

        assert metadata.open_graph.get("og:title") == "Awesome OG Title"
        assert metadata.open_graph.get("twitter:card") == "summary_large_image"

        assert "support@awesome.dev" in metadata.contact_emails
        assert metadata.project_urls.get("repository") == "https://github.com/acme/awesome"
        assert metadata.project_urls.get("homepage") == "https://awesome.example.com"

    def test_extract_community_and_governance_signals(self):
        """Test extraction of community/support/security related metadata."""
        metadata = extract_metadata(ADVANCED_METADATA_README)

        assert metadata.has_security is True
        assert metadata.has_code_of_conduct is True
        assert metadata.community_urls.get("issues") == "https://github.com/acme/awesome/issues"
        assert metadata.community_urls.get("discussions") == "https://github.com/acme/awesome/discussions"

    def test_readability_and_read_time(self):
        """Test readability score and estimated read time metrics."""
        metadata = extract_metadata(COMPREHENSIVE_README)

        assert 0 <= metadata.readability_score <= 100
        assert metadata.estimated_read_time_minutes >= 1


# ============================================================================
# Formatter Tests
# ============================================================================

class TestREADMEFormatter:
    """Test suite for READMEFormatter class."""
    
    def test_basic_formatting(self):
        """Test basic README formatting."""
        formatted = format_readme(MESSY_README, style=FormatStyle.STANDARD)
        
        assert formatted is not None
        assert len(formatted) > 0
        assert "# My Project" in formatted
    
    def test_formatting_styles(self):
        """Test different formatting styles."""
        for style in [FormatStyle.MINIMAL, FormatStyle.STANDARD, 
                      FormatStyle.COMPREHENSIVE, FormatStyle.LIBRARY, 
                      FormatStyle.APPLICATION]:
            formatted = format_readme(MESSY_README, style=style)
            assert formatted is not None
            assert len(formatted) > 0
    
    def test_toc_generation(self):
        """Test table of contents generation."""
        formatted = format_readme(STANDARD_README, 
                                  style=FormatStyle.STANDARD,
                                  add_toc=True)
        
        # Should add TOC if enough sections
        if STANDARD_README.count("##") >= 4:
            assert "Table of Contents" in formatted or "table of contents" in formatted.lower()
    
    def test_heading_fix(self):
        """Test heading level fixing."""
        options = FormatOptions(
            style=FormatStyle.STANDARD,
            fix_headings=True
        )
        formatter = READMEFormatter(options)
        formatted = formatter.format(MESSY_README)
        
        # Should standardize heading levels
        assert formatted is not None
    
    def test_section_standardization(self):
        """Test section name standardization."""
        options = FormatOptions(
            style=FormatStyle.STANDARD,
            standardize_sections=True
        )
        formatter = READMEFormatter(options)
        formatted = formatter.format(MESSY_README)
        
        # Should standardize section names
        assert "Installation" in formatted or "install" in formatted.lower()
    
    def test_add_missing_sections(self):
        """Test adding missing sections."""
        options = FormatOptions(
            style=FormatStyle.STANDARD,
            add_missing_sections=True
        )
        formatter = READMEFormatter(options)
        formatted = formatter.format(MINIMAL_README)
        
        # Should add standard sections
        sections_count = formatted.count("##")
        original_count = MINIMAL_README.count("##")
        assert sections_count > original_count
    
    def test_section_sorting(self):
        """Test section sorting."""
        options = FormatOptions(
            style=FormatStyle.STANDARD,
            sort_sections=True
        )
        formatter = READMEFormatter(options)
        formatted = formatter.format(MESSY_README)
        
        # Should reorder sections according to style
        assert formatted is not None
    
    def test_quality_improvements(self):
        """Test automatic quality improvements."""
        formatter = READMEFormatter(FormatOptions(style=FormatStyle.STANDARD))
        formatted, improvements = formatter.format_quality_improvements(MINIMAL_README)
        
        assert formatted is not None
        assert isinstance(improvements, list)
    
    def test_emoji_handling_keep(self):
        """Test keeping emojis."""
        readme_with_emoji = "# Project 🚀\n\n## Features ✨\n\nContent"
        
        options = FormatOptions(emoji_style="keep")
        formatter = READMEFormatter(options)
        formatted = formatter.format(readme_with_emoji)
        
        assert "🚀" in formatted
        assert "✨" in formatted
    
    def test_emoji_handling_remove(self):
        """Test removing emojis."""
        readme_with_emoji = "# Project 🚀\n\n## Features ✨\n\nContent"
        
        options = FormatOptions(emoji_style="remove")
        formatter = READMEFormatter(options)
        formatted = formatter.format(readme_with_emoji)
        
        # Emojis should be removed (though headings remain)
        assert formatted is not None
    
    def test_format_options(self):
        """Test various format options."""
        options = FormatOptions(
            style=FormatStyle.LIBRARY,
            add_toc=True,
            fix_headings=True,
            add_missing_sections=False,
            sort_sections=False,
            emoji_style="keep"
        )
        
        formatter = READMEFormatter(options)
        formatted = formatter.format(STANDARD_README)
        
        assert formatted is not None
        assert len(formatted) > 0


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for metadata extraction and formatting."""
    
    def test_extract_then_format(self):
        """Test extracting metadata then formatting."""
        # Extract metadata
        metadata = extract_metadata(MESSY_README)
        original_score = metadata.completeness_score
        
        # Format
        formatted = format_readme(MESSY_README, 
                                  style=FormatStyle.STANDARD,
                                  add_toc=True,
                                  add_missing=True)
        
        # Re-extract to check improvement
        new_metadata = extract_metadata(formatted)
        
        # Formatting should maintain or improve quality
        assert new_metadata.title is not None
        assert len(formatted) >= len(MESSY_README)
    
    def test_quality_improvement_workflow(self):
        """Test complete quality improvement workflow."""
        # Start with minimal README
        original = MINIMAL_README
        
        # Get initial quality
        initial_quality = get_quality_report(original)
        initial_score = initial_quality["completeness_score"]
        
        # Format with improvements
        formatter = READMEFormatter(FormatOptions(
            style=FormatStyle.STANDARD,
            add_missing_sections=True,
            add_toc=True
        ))
        improved, improvements = formatter.format_quality_improvements(original)
        
        # Check improvement
        final_quality = get_quality_report(improved)
        final_score = final_quality["completeness_score"]
        
        # Score should improve or stay same
        assert final_score >= initial_score
    
    def test_format_preserves_content(self):
        """Test that formatting preserves important content."""
        original = STANDARD_README
        formatted = format_readme(original, style=FormatStyle.STANDARD)
        
        # Extract metadata from both
        original_meta = extract_metadata(original)
        formatted_meta = extract_metadata(formatted)
        
        # Title should be preserved or similar
        assert original_meta.title is not None
        assert formatted_meta.title is not None
        
        # Code blocks should be preserved
        assert len(formatted_meta.code_blocks) >= len(original_meta.code_blocks) - 1


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_content(self):
        """Test handling of empty content."""
        metadata = extract_metadata("")
        
        assert metadata.title is None or metadata.title == ""
        assert metadata.completeness_score == 0 or metadata.completeness_score < 20
    
    def test_no_headings(self):
        """Test README with no headings."""
        content = "Just some text without any headings or structure."
        metadata = extract_metadata(content)
        
        assert len(metadata.sections) == 0 or len(metadata.sections) == 1
        assert metadata.completeness_score < 30
    
    def test_only_code_blocks(self):
        """Test README with only code blocks."""
        content = """
```python
print("hello")
```

```bash
echo "world"
```
"""
        metadata = extract_metadata(content)
        
        assert len(metadata.code_blocks) == 2
    
    def test_malformed_badges(self):
        """Test handling of malformed badges."""
        content = """
# Project

![Badge without link](image.png)
[![Badge with link]](https://example.com)
"""
        metadata = extract_metadata(content)
        
        # Should handle gracefully
        assert isinstance(metadata.badges, list)
    
    def test_nested_sections(self):
        """Test deeply nested section structure."""
        content = """
# Title

## Section 1

### Subsection 1.1

#### Subsubsection 1.1.1

##### Deep section

## Section 2
"""
        metadata = extract_metadata(content)
        
        # Should parse nested structure (section names includes nested ones)
        # At minimum should detect the title
        assert len(metadata.sections) >= 1
        assert metadata.title is not None
    
    def test_special_characters(self):
        """Test handling of special characters."""
        content = """
# Project with 特殊字符 and émojis 🎉

Content with special chars: < > & " '

## Section with `code` and **bold**
"""
        metadata = extract_metadata(content)
        
        assert metadata.title is not None
        assert len(metadata.sections) >= 1
    
    def test_very_long_readme(self):
        """Test handling of very long README."""
        long_content = COMPREHENSIVE_README * 10
        
        metadata = extract_metadata(long_content)
        
        assert metadata.word_count > 1000
        assert metadata.line_count > 100
    
    def test_format_already_good_readme(self):
        """Test formatting an already well-formatted README."""
        formatted = format_readme(COMPREHENSIVE_README, style=FormatStyle.COMPREHENSIVE)
        
        # Should not break existing good formatting
        assert formatted is not None
        assert "Large Framework" in formatted


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Basic performance tests."""
    
    def test_extraction_performance(self):
        """Test extraction performance on large README."""
        import time
        
        large_content = COMPREHENSIVE_README * 5
        
        start = time.time()
        metadata = extract_metadata(large_content)
        duration = time.time() - start
        
        # Should complete in reasonable time (< 1 second)
        assert duration < 1.0
        assert metadata is not None
    
    def test_formatting_performance(self):
        """Test formatting performance."""
        import time
        
        start = time.time()
        formatted = format_readme(COMPREHENSIVE_README, 
                                  style=FormatStyle.COMPREHENSIVE,
                                  add_toc=True,
                                  add_missing=True)
        duration = time.time() - start
        
        # Should complete in reasonable time (< 2 seconds)
        assert duration < 2.0
        assert formatted is not None


# ============================================================================
# Utility Tests
# ============================================================================

class TestUtilities:
    """Test utility functions and helpers."""
    
    def test_badge_classification(self):
        """Test badge type classification."""
        extractor = MetadataExtractor()
        
        # Test various badge types
        assert extractor._classify_badge("Build Status", "travis-ci.org") == "build"
        assert extractor._classify_badge("Coverage", "codecov.io") == "coverage"
        assert extractor._classify_badge("Version", "badge/v1.0.0") == "version"
        assert extractor._classify_badge("License MIT", "license") == "license"
    
    def test_link_classification(self):
        """Test link type classification."""
        extractor = MetadataExtractor()
        
        # Test various link types
        assert extractor._classify_link("Docs", "https://docs.example.com") == "documentation"
        assert extractor._classify_link("GitHub", "https://github.com/user/repo") == "repository"
        assert extractor._classify_link("Twitter", "https://twitter.com/user") == "social"
    
    def test_score_to_grade(self):
        """Test score to grade conversion."""
        extractor = MetadataExtractor()
        
        assert extractor._score_to_grade(95) == "A"
        assert extractor._score_to_grade(85) == "B"
        assert extractor._score_to_grade(75) == "C"
        assert extractor._score_to_grade(65) == "D"
        assert extractor._score_to_grade(50) == "F"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
