"""
Demo script for the Metadata Extractor and Formatter features.

This demonstrates how to use the new advanced features for
extracting structured data and formatting README files.
"""

from pathlib import Path
from summarize_readme.metadata_extractor import (
    MetadataExtractor,
    extract_metadata,
    get_quality_report
)
from summarize_readme.formatter import (
    READMEFormatter,
    FormatStyle,
    FormatOptions,
    format_readme
)


def demo_metadata_extraction():
    """Demonstrate metadata extraction from a README."""
    print("=" * 60)
    print("DEMO 1: Metadata Extraction")
    print("=" * 60)
    
    # Sample README content
    sample_readme = """
# Awesome Project 🚀

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://example.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern Python library for doing awesome things with data.

## Features

- ✨ Fast processing
- 🔒 Secure by default
- 📦 Easy to install

## Installation

```bash
pip install awesome-project
```

## Usage

```python
from awesome_project import AwesomeClass

# Create instance
awesome = AwesomeClass()
result = awesome.process()
```

## API Reference

See [documentation](https://docs.example.com) for full API details.

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## License

This project is licensed under the MIT License.
"""
    
    # Extract metadata
    print("\n1. Extracting metadata...")
    metadata = extract_metadata(sample_readme)
    
    print(f"\nTitle: {metadata.title}")
    print(f"Description: {metadata.description}")
    print(f"License: {metadata.license}")
    print(f"Word count: {metadata.word_count}")
    print(f"Badges: {len(metadata.badges)}")
    print(f"Sections: {len(metadata.sections)}")
    print(f"Code blocks: {len(metadata.code_blocks)}")
    print(f"Completeness score: {metadata.completeness_score}/100")
    
    # Get quality report
    print("\n2. Quality analysis...")
    quality = get_quality_report(sample_readme)
    print(f"Grade: {quality['grade']}")
    print(f"\nStrengths:")
    for strength in quality['strengths']:
        print(f"  ✓ {strength}")
    
    if quality['missing']:
        print(f"\nMissing elements:")
        for missing in quality['missing']:
            print(f"  ✗ {missing}")
    
    if quality['suggestions']:
        print(f"\nSuggestions:")
        for suggestion in quality['suggestions']:
            print(f"  → {suggestion}")
    
    # Export metadata
    print("\n3. Exporting metadata...")
    metadata_dict = metadata.to_dict()
    print(f"Exported {len(metadata_dict)} metadata fields")
    
    print("\n" + "=" * 60 + "\n")


def demo_formatting():
    """Demonstrate README formatting."""
    print("=" * 60)
    print("DEMO 2: README Formatting")
    print("=" * 60)
    
    # Sample messy README
    messy_readme = """
# My Project
This is a project.

### Installation
Run pip install

# Usage
Use it like this

### Contributing
Send PRs

# License
MIT
"""
    
    print("\nOriginal README (messy):")
    print("-" * 40)
    print(messy_readme[:200] + "...")
    
    # Format with standard style
    print("\n1. Formatting with standard style...")
    formatted = format_readme(messy_readme, style=FormatStyle.STANDARD)
    
    print("\nFormatted README preview:")
    print("-" * 40)
    print(formatted[:400] + "...")
    
    # Format with comprehensive style and missing sections
    print("\n2. Formatting with comprehensive style + missing sections...")
    options = FormatOptions(
        style=FormatStyle.COMPREHENSIVE,
        add_toc=True,
        add_missing_sections=True,
        fix_headings=True,
        sort_sections=True
    )
    formatter = READMEFormatter(options)
    formatted_comprehensive = formatter.format(messy_readme)
    
    print(f"\nOriginal sections: {messy_readme.count('#')}")
    print(f"Formatted sections: {formatted_comprehensive.count('##')}")
    print(f"Size: {len(messy_readme)} → {len(formatted_comprehensive)} bytes")
    
    # Format for library
    print("\n3. Formatting for library style...")
    library_formatted = format_readme(
        messy_readme,
        style=FormatStyle.LIBRARY,
        add_toc=True,
        add_missing=True
    )
    
    print(f"Library format size: {len(library_formatted)} bytes")
    print("Added library-specific sections (API Reference, etc.)")
    
    print("\n" + "=" * 60 + "\n")


def demo_combined_workflow():
    """Demonstrate combined metadata extraction and formatting."""
    print("=" * 60)
    print("DEMO 3: Combined Workflow")
    print("=" * 60)
    
    readme = """
# Data Processing Tool

A lightweight tool for processing data files.

## Install

pip install data-tool

## How to use

Just run it.
"""
    
    # Step 1: Analyze current state
    print("\n1. Analyzing current README...")
    extractor = MetadataExtractor()
    metadata = extractor.extract(readme)
    quality = extractor.quality_report(metadata)
    
    print(f"Current completeness: {metadata.completeness_score}/100 (Grade: {quality['grade']})")
    print(f"Missing: {', '.join(quality['missing'][:3])}...")
    
    # Step 2: Format and improve
    print("\n2. Formatting and improving...")
    formatter = READMEFormatter(FormatOptions(
        style=FormatStyle.STANDARD,
        add_missing_sections=True,
        add_toc=True,
        fix_headings=True,
        sort_sections=True
    ))
    
    improved, improvements = formatter.format_quality_improvements(readme)
    
    print(f"Applied improvements:")
    for improvement in improvements:
        print(f"  ✓ {improvement}")
    
    # Step 3: Re-analyze
    print("\n3. Re-analyzing improved README...")
    metadata_after = extractor.extract(improved)
    quality_after = extractor.quality_report(metadata_after)
    
    print(f"New completeness: {metadata_after.completeness_score}/100 (Grade: {quality_after['grade']})")
    print(f"Improvement: +{metadata_after.completeness_score - metadata.completeness_score} points")
    
    print("\n" + "=" * 60 + "\n")


def demo_programmatic_usage():
    """Demonstrate programmatic API usage."""
    print("=" * 60)
    print("DEMO 4: Programmatic API Usage")
    print("=" * 60)
    
    readme_content = Path("README.md").read_text(encoding='utf-8')
    
    # Extract metadata
    print("\n1. Using MetadataExtractor class...")
    extractor = MetadataExtractor()
    metadata = extractor.extract(readme_content)
    
    print(f"Project: {metadata.title}")
    print(f"Tech stack detected: {', '.join(metadata.tech_stack[:5])}")
    print(f"Primary language: {metadata.language or 'Not detected'}")
    
    # Badge analysis
    print(f"\n2. Badge analysis...")
    print(f"Total badges: {len(metadata.badges)}")
    badge_types = {}
    for badge in metadata.badges:
        badge_types[badge.badge_type] = badge_types.get(badge.badge_type, 0) + 1
    for badge_type, count in badge_types.items():
        print(f"  {badge_type}: {count}")
    
    # Link analysis
    print(f"\n3. Link analysis...")
    print(f"Total links: {len(metadata.links)}")
    link_types = {}
    for link in metadata.links:
        link_types[link.link_type] = link_types.get(link.link_type, 0) + 1
    for link_type, count in link_types.items():
        print(f"  {link_type}: {count}")
    
    # Section structure
    print(f"\n4. Document structure...")
    print(f"Sections: {len(metadata.sections)}")
    print(f"Has TOC: {metadata.table_of_contents}")
    print(f"Key sections present:")
    print(f"  Installation: {metadata.has_installation}")
    print(f"  Usage: {metadata.has_usage}")
    print(f"  Contributing: {metadata.has_contributing}")
    print(f"  Examples: {metadata.has_examples}")
    
    print("\n" + "=" * 60 + "\n")


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 5 + "README Metadata Extractor & Formatter Demo" + " " * 10 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    try:
        demo_metadata_extraction()
        demo_formatting()
        demo_combined_workflow()
        
        # Only run if README.md exists
        if Path("README.md").exists():
            demo_programmatic_usage()
        else:
            print("\nSkipping programmatic demo (README.md not found)")
        
        print("\n" + "=" * 60)
        print("All demos completed successfully! ✓")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
