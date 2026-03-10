"""
Manual comprehensive test script for Metadata Extractor & Formatter.

Run this script to test all features interactively.
"""

import sys
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


# Test samples
TEST_SAMPLES = {
    "minimal": """# Simple Project

A basic project with minimal content.
""",
    
    "standard": """# Awesome Library 🚀

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://ci.example.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/user/repo)

A modern Python library for awesome things.

## Features

- ✨ Fast and efficient
- 🔒 Secure by default
- 📦 Easy installation
- 🎯 Simple API

## Installation

```bash
pip install awesome-library
```

Or install from source:

```bash
git clone https://github.com/user/awesome-library
cd awesome-library
pip install -e .
```

## Usage

Basic example:

```python
from awesome import AwesomeClass

# Create instance
awesome = AwesomeClass()

# Use it
result = awesome.process(data)
print(result)
```

## API Reference

See [documentation](https://awesome-lib.readthedocs.io) for full API details.

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the MIT License.
""",
    
    "messy": """# My Project
Some description here

### install
just run pip install

# usage
Use it like this

### Contributing
send PRs

# License
MIT
""",
    
    "comprehensive": """# Enterprise Framework 🏢

[![Build](https://img.shields.io/badge/build-passing-brightgreen)](https://ci.example.com)
[![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen)](https://coverage.example.com)
[![Version](https://img.shields.io/badge/version-3.2.1-blue)](https://github.com/enterprise/framework)
[![Downloads](https://img.shields.io/badge/downloads-50k%2Fmonth-blue)](https://pypi.org/project/framework)

An enterprise-grade framework built with Python for scalable applications.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Configuration](#configuration)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Overview

Enterprise Framework is a production-ready solution for building scalable applications.

## Features

- 🚀 High performance
- 📊 Built-in analytics
- 🔐 Enterprise security
- 🌐 Multi-language support
- 📱 Responsive design
- ⚡ Real-time updates

## Installation

### Via pip

```bash
pip install enterprise-framework
```

### Via conda

```bash
conda install -c conda-forge enterprise-framework
```

### From source

```bash
git clone https://github.com/enterprise/framework
cd framework
python setup.py install
```

## Quick Start

```python
import framework

app = framework.App(config='production')
app.run()
```

## Usage

Detailed usage instructions with examples.

## API Reference

Complete API documentation available at [docs.framework.io](https://docs.framework.io).

## Examples

Check the [examples directory](examples/) for more.

## Configuration

See [CONFIG.md](CONFIG.md) for configuration options.

## Testing

```bash
pytest tests/
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment guides.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

Licensed under the Apache License 2.0 - see [LICENSE](LICENSE) file.
"""
}


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subsection(title):
    """Print a subsection header."""
    print(f"\n--- {title} ---")


def test_metadata_extraction():
    """Test metadata extraction features."""
    print_section("TEST 1: METADATA EXTRACTION")
    
    for name, content in TEST_SAMPLES.items():
        print_subsection(f"Testing {name.upper()} README")
        
        try:
            # Extract metadata
            metadata = extract_metadata(content)
            
            # Print results
            print(f"✓ Title: {metadata.title}")
            print(f"✓ Description: {metadata.description[:60] if metadata.description else 'None'}...")
            print(f"✓ Language: {metadata.language or 'Not detected'}")
            print(f"✓ License: {metadata.license or 'Not specified'}")
            print(f"✓ Word count: {metadata.word_count}")
            print(f"✓ Badges: {len(metadata.badges)}")
            print(f"✓ Links: {len(metadata.links)}")
            print(f"✓ Sections: {len(metadata.sections)}")
            print(f"✓ Code blocks: {len(metadata.code_blocks)}")
            print(f"✓ Completeness score: {metadata.completeness_score}/100")
            print(f"✓ Has installation: {metadata.has_installation}")
            print(f"✓ Has usage: {metadata.has_usage}")
            print(f"✓ Has examples: {metadata.has_examples}")
            
            # Badge details
            if metadata.badges:
                badge_types = set(b.badge_type for b in metadata.badges if b.badge_type)
                if badge_types:
                    print(f"\n  Badge types: {', '.join(badge_types)}")
            
            # Tech stack
            if metadata.tech_stack:
                print(f"  Tech stack: {', '.join(metadata.tech_stack[:5])}")
            
            print("✅ PASS")
        except Exception as e:
            print(f"❌ FAIL - Error: {e}")
            import traceback
            traceback.print_exc()


def test_quality_analysis():
    """Test quality analysis features."""
    print_section("TEST 2: QUALITY ANALYSIS")
    
    for name, content in TEST_SAMPLES.items():
        print_subsection(f"Analyzing {name.upper()} README")
        
        try:
            quality = get_quality_report(content)
            
            print(f"✓ Completeness: {quality['completeness_score']}/100")
            print(f"✓ Grade: {quality['grade']}")
            
            if quality['strengths']:
                print(f"✓ Strengths ({len(quality['strengths'])}):")
                for strength in quality['strengths'][:3]:
                    print(f"    • {strength}")
            
            if quality['missing']:
                print(f"✓ Missing ({len(quality['missing'])}):")
                for missing in quality['missing'][:3]:
                    print(f"    • {missing}")
            
            if quality['suggestions']:
                print(f"✓ Suggestions ({len(quality['suggestions'])}):")
                for suggestion in quality['suggestions'][:2]:
                    print(f"    → {suggestion}")
            
            print("✅ PASS")
        except Exception as e:
            print(f"❌ FAIL - Error: {e}")


def test_formatting():
    """Test README formatting features."""
    print_section("TEST 3: README FORMATTING")
    
    test_content = TEST_SAMPLES["messy"]
    
    styles = [
        FormatStyle.MINIMAL,
        FormatStyle.STANDARD,
        FormatStyle.COMPREHENSIVE,
        FormatStyle.LIBRARY,
        FormatStyle.APPLICATION
    ]
    
    for style in styles:
        print_subsection(f"Testing {style.value.upper()} style")
        
        try:
            formatted = format_readme(test_content, style=style)
            
            print(f"✓ Original size: {len(test_content)} bytes")
            print(f"✓ Formatted size: {len(formatted)} bytes")
            print(f"✓ Size change: {len(formatted) - len(test_content):+d} bytes")
            
            # Check structure
            h1_count = formatted.count("\n# ")
            h2_count = formatted.count("\n## ")
            print(f"✓ Top-level headings: {h1_count}")
            print(f"✓ Second-level headings: {h2_count}")
            
            print("✅ PASS")
        except Exception as e:
            print(f"❌ FAIL - Error: {e}")


def test_format_options():
    """Test various formatting options."""
    print_section("TEST 4: FORMAT OPTIONS")
    
    test_content = TEST_SAMPLES["standard"]
    
    test_cases = [
        ("Add TOC", {"add_toc": True}),
        ("Fix headings", {"fix_headings": True}),
        ("Add missing sections", {"add_missing_sections": True}),
        ("Sort sections", {"sort_sections": True}),
        ("Remove emojis", {"emoji_style": "remove"}),
        ("All options combined", {
            "add_toc": True,
            "fix_headings": True,
            "add_missing_sections": True,
            "sort_sections": True
        })
    ]
    
    for name, options in test_cases:
        print_subsection(name)
        
        try:
            format_options = FormatOptions(style=FormatStyle.STANDARD, **options)
            formatter = READMEFormatter(format_options)
            formatted = formatter.format(test_content)
            
            print(f"✓ Formatted successfully")
            print(f"✓ Size: {len(formatted)} bytes")
            
            # Check for TOC if requested
            if options.get("add_toc"):
                has_toc = "table of contents" in formatted.lower()
                print(f"✓ TOC present: {has_toc}")
            
            print("✅ PASS")
        except Exception as e:
            print(f"❌ FAIL - Error: {e}")


def test_quality_improvements():
    """Test quality improvement features."""
    print_section("TEST 5: QUALITY IMPROVEMENTS")
    
    test_content = TEST_SAMPLES["minimal"]
    
    print_subsection("Before improvement")
    
    try:
        # Get initial quality
        initial_quality = get_quality_report(test_content)
        print(f"✓ Initial score: {initial_quality['completeness_score']}/100")
        print(f"✓ Initial grade: {initial_quality['grade']}")
        
        # Apply improvements
        print_subsection("Applying improvements")
        
        formatter = READMEFormatter(FormatOptions(
            style=FormatStyle.STANDARD,
            add_missing_sections=True,
            add_toc=True,
            fix_headings=True,
            sort_sections=True
        ))
        
        improved, improvements = formatter.format_quality_improvements(test_content)
        
        print(f"✓ Improvements applied: {len(improvements)}")
        for improvement in improvements:
            print(f"    • {improvement}")
        
        # Get final quality
        print_subsection("After improvement")
        
        final_quality = get_quality_report(improved)
        print(f"✓ Final score: {final_quality['completeness_score']}/100")
        print(f"✓ Final grade: {final_quality['grade']}")
        print(f"✓ Score change: {final_quality['completeness_score'] - initial_quality['completeness_score']:+.1f}")
        
        print("✅ PASS")
    except Exception as e:
        print(f"❌ FAIL - Error: {e}")
        import traceback
        traceback.print_exc()


def test_edge_cases():
    """Test edge cases."""
    print_section("TEST 6: EDGE CASES")
    
    edge_cases = {
        "empty": "",
        "no_headings": "Just some text without any structure.",
        "only_code": "```python\nprint('hello')\n```",
        "special_chars": "# Project with 特殊字符 🎉\n\nContent",
        "nested_sections": "# Title\n## Section\n### Subsection\n#### Deep\n##### Very deep",
    }
    
    for name, content in edge_cases.items():
        print_subsection(f"Testing {name}")
        
        try:
            # Try extraction
            metadata = extract_metadata(content)
            print(f"✓ Extract successful - Score: {metadata.completeness_score}/100")
            
            # Try formatting
            formatted = format_readme(content, style=FormatStyle.STANDARD)
            print(f"✓ Format successful - Size: {len(formatted)} bytes")
            
            print("✅ PASS")
        except Exception as e:
            print(f"❌ FAIL - Error: {e}")


def test_real_readme():
    """Test on actual project README if available."""
    print_section("TEST 7: REAL README")
    
    readme_path = Path("README.md")
    
    if not readme_path.exists():
        print("ℹ️  README.md not found, skipping real README test")
        return
    
    print_subsection("Testing project README.md")
    
    try:
        content = readme_path.read_text(encoding='utf-8')
        
        # Extract metadata
        print("\nExtracting metadata...")
        metadata = extract_metadata(content)
        
        print(f"✓ Title: {metadata.title}")
        print(f"✓ Completeness: {metadata.completeness_score}/100")
        print(f"✓ Sections: {len(metadata.sections)}")
        print(f"✓ Code blocks: {len(metadata.code_blocks)}")
        print(f"✓ Word count: {metadata.word_count:,}")
        
        # Get quality report
        print("\nQuality analysis...")
        quality = get_quality_report(content)
        
        print(f"✓ Grade: {quality['grade']}")
        if quality['missing']:
            print(f"✓ Missing elements: {', '.join(quality['missing'][:3])}")
        if quality['suggestions']:
            print(f"✓ Top suggestion: {quality['suggestions'][0]}")
        
        # Test formatting (preview only)
        print("\nTesting format preview...")
        formatted = format_readme(content, style=FormatStyle.STANDARD)
        print(f"✓ Format successful - Size: {len(content)} → {len(formatted)} bytes")
        
        print("✅ PASS")
    except Exception as e:
        print(f"❌ FAIL - Error: {e}")
        import traceback
        traceback.print_exc()


def test_performance():
    """Test performance."""
    print_section("TEST 8: PERFORMANCE")
    
    import time
    
    # Create large content
    large_content = TEST_SAMPLES["comprehensive"] * 5
    
    print_subsection("Extraction performance")
    try:
        start = time.time()
        metadata = extract_metadata(large_content)
        duration = time.time() - start
        
        print(f"✓ Content size: {len(large_content):,} bytes")
        print(f"✓ Extracted in: {duration:.3f}s")
        print(f"✓ Performance: {'✅ Good' if duration < 1.0 else '⚠️  Slow'}")
        
        if duration < 1.0:
            print("✅ PASS")
        else:
            print("⚠️  SLOW but functional")
    except Exception as e:
        print(f"❌ FAIL - Error: {e}")
    
    print_subsection("Formatting performance")
    try:
        start = time.time()
        formatted = format_readme(large_content, 
                                  style=FormatStyle.COMPREHENSIVE,
                                  add_toc=True)
        duration = time.time() - start
        
        print(f"✓ Formatted in: {duration:.3f}s")
        print(f"✓ Performance: {'✅ Good' if duration < 2.0 else '⚠️  Slow'}")
        
        if duration < 2.0:
            print("✅ PASS")
        else:
            print("⚠️  SLOW but functional")
    except Exception as e:
        print(f"❌ FAIL - Error: {e}")


def run_all_tests():
    """Run all tests."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "COMPREHENSIVE TEST SUITE" + " " * 34 + "║")
    print("║" + " " * 10 + "Metadata Extractor & Formatter" + " " * 28 + "║")
    print("╚" + "═" * 68 + "╝")
    
    tests = [
        ("Metadata Extraction", test_metadata_extraction),
        ("Quality Analysis", test_quality_analysis),
        ("README Formatting", test_formatting),
        ("Format Options", test_format_options),
        ("Quality Improvements", test_quality_improvements),
        ("Edge Cases", test_edge_cases),
        ("Real README", test_real_readme),
        ("Performance", test_performance),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ TEST SUITE '{name}' FAILED")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
    else:
        print(f"\n⚠️  {failed} test suite(s) failed")
    
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_all_tests()
