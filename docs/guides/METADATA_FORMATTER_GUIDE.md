# Metadata Extractor & Formatter Guide

🔍 **Advanced feature for extracting structured data and formatting README files**

## Table of Contents

- [Overview](#overview)
- [Metadata Extractor](#metadata-extractor)
  - [What It Extracts](#what-it-extracts)
  - [CLI Usage](#cli-usage-extract)
  - [Programmatic Usage](#programmatic-usage-extractor)
  - [Quality Analysis](#quality-analysis)
- [README Formatter](#readme-formatter)
  - [Formatting Styles](#formatting-styles)
  - [CLI Usage](#cli-usage-format)
  - [Programmatic Usage](#programmatic-usage-formatter)
  - [Format Options](#format-options)
- [Advanced Examples](#advanced-examples)
- [Use Cases](#use-cases)

---

## Overview

The **Metadata Extractor & Formatter** is an advanced feature that provides:

1. **Metadata Extraction**: Extract structured information from README files
   - Badges, licenses, tech stack, dependencies
   - Section structure and code blocks
   - Links, authors, and project details
   - Quality metrics and completeness scoring

2. **README Formatting**: Standardize and improve README files
   - Multiple style presets (minimal, standard, comprehensive, library, application)
   - Automatic section ordering and TOC generation
   - Missing section detection and placeholder insertion
   - Quality improvements and best practices enforcement

---

## Metadata Extractor

### What It Extracts

The metadata extractor analyzes README files and extracts:

#### Basic Information
- **Title**: Main project title
- **Description**: Project description/tagline
- **Language**: Primary programming language
- **License**: License type (MIT, Apache, GPL, etc.)
- **Version**: Version number if specified

#### Technical Details
- **Tech Stack**: Detected technologies and frameworks
- **Dependencies**: Package/library dependencies
- **Code Blocks**: All code examples with language tags

#### Structure
- **Sections**: All sections with hierarchy
- **Table of Contents**: Whether TOC exists
- **Section Types**: Installation, Usage, Contributing, etc.

#### External Resources
- **Badges**: All badges with types (build, coverage, version, etc.)
- **Links**: Categorized links (documentation, repository, social, etc.)
- **Repository URL**: GitHub/GitLab repository
- **Documentation URL**: Documentation site

#### Quality Metrics
- **Word Count**: Total words
- **Line Count**: Total lines
- **Completeness Score**: 0-100 quality score
- **Missing Elements**: What's missing for completeness
- **Suggestions**: Improvement recommendations

### CLI Usage (Extract)

#### Basic Extraction

```bash
# Extract metadata as JSON
readme-summarizer extract README.md

# Extract from GitHub repo
readme-summarizer extract owner/repo

# Extract from URL
readme-summarizer extract https://github.com/owner/repo
```

#### With Output File

```bash
# Save to file
readme-summarizer extract README.md -o metadata.json

# Export as YAML (requires: pip install pyyaml)
readme-summarizer extract README.md --format yaml -o metadata.yaml

# Human-readable text format
readme-summarizer extract README.md --format text
```

#### Quality Analysis

```bash
# Include quality report
readme-summarizer extract README.md --quality

# Detailed extraction (includes code blocks, full sections)
readme-summarizer extract README.md --detailed --quality
```

#### Output Formats

**JSON** (default):
```json
{
  "title": "Awesome Project",
  "description": "A modern Python library...",
  "license": "MIT",
  "completeness_score": 85.0,
  "badges": [...],
  "sections": [...],
  ...
}
```

**YAML** (with `--format yaml`):
```yaml
title: Awesome Project
description: A modern Python library...
license: MIT
completeness_score: 85.0
badges:
  - alt_text: "Build Status"
    image_url: "https://..."
...
```

**Text** (with `--format text`):
```
=== README Metadata ===
Title: Awesome Project
License: MIT
Quality Score: 85/100
...
```

### Programmatic Usage (Extractor)

#### Quick Extraction

```python
from summarize_readme.metadata_extractor import extract_metadata, get_quality_report

# Extract metadata
content = "# My Project\n\n..."
metadata = extract_metadata(content)

print(f"Title: {metadata.title}")
print(f"Score: {metadata.completeness_score}/100")
print(f"Badges: {len(metadata.badges)}")

# Get quality report
quality = get_quality_report(content)
print(f"Grade: {quality['grade']}")
print(f"Missing: {quality['missing']}")
```

#### Advanced Usage

```python
from summarize_readme.metadata_extractor import MetadataExtractor

# Create extractor
extractor = MetadataExtractor()

# Extract full metadata
metadata = extractor.extract(content)

# Access specific data
for badge in metadata.badges:
    print(f"{badge.alt_text}: {badge.badge_type}")

for section in metadata.sections:
    print(f"Section: {section.title} (level {section.level})")

# Get quality report
quality_report = extractor.quality_report(metadata)

# Export as dict
data = metadata.to_dict()
```

### Quality Analysis

The quality analysis provides:

- **Completeness Score**: 0-100 scoring based on:
  - Title and description (20 points)
  - Installation instructions (15 points)
  - Usage examples (15 points)
  - Code examples (10 points)
  - License information (10 points)
  - Contributing guidelines (5 points)
  - Badges (5 points)
  - Documentation structure (15 points)
  - Content quality (10 points)

- **Letter Grade**: A (90+), B (80-89), C (70-79), D (60-69), F (<60)

- **Strengths**: What's done well
- **Missing Elements**: What's absent
- **Suggestions**: Actionable improvements

**Example Quality Report:**

```
Grade: B
Score: 82/100

Strengths:
  ✓ Has installation instructions
  ✓ Has usage examples
  ✓ Comprehensive documentation

Missing Elements:
  ✗ Contributing guidelines
  ✗ Status badges

Suggestions:
  → Consider adding status badges (build, coverage, version)
  → Add a table of contents for better navigation
```

---

## README Formatter

### Formatting Styles

The formatter supports multiple preset styles:

#### 1. **Minimal** (`--style minimal`)
Essential sections only:
- Title
- Description
- Installation
- Usage
- License

Best for: Small utilities, simple scripts

#### 2. **Standard** (`--style standard`) [Default]
Common open-source project structure:
- Title
- Badges
- Description
- Features
- Installation
- Usage
- Examples
- Configuration
- Contributing
- License

Best for: Most projects

#### 3. **Comprehensive** (`--style comprehensive`)
Full documentation with 20+ sections:
- Everything in Standard, plus:
- Table of Contents
- Demo/Screenshots
- API Reference
- Advanced Usage
- Testing
- Deployment
- Troubleshooting
- FAQ
- Roadmap
- Security
- Changelog

Best for: Major projects, frameworks, large libraries

#### 4. **Library** (`--style library`)
For libraries and packages:
- Title
- Badges
- Description
- Features
- Installation
- Quick Start
- API Reference
- Examples
- Configuration
- Testing
- Contributing

Best for: Node/Python/Ruby packages, SDKs

#### 5. **Application** (`--style application`)
For end-user applications:
- Title
- Badges
- Description
- Features
- Screenshots
- Installation
- Usage
- Configuration
- Examples
- Troubleshooting
- FAQ

Best for: CLI tools, desktop apps, web apps

### CLI Usage (Format)

#### Basic Formatting

```bash
# Format with standard style
readme-summarizer format README.md -o formatted.md

# Format in place (overwrites original)
readme-summarizer format README.md -o README.md

# Preview changes without saving
readme-summarizer format README.md --preview
```

#### Style Selection

```bash
# Minimal style
readme-summarizer format README.md --style minimal

# Comprehensive style
readme-summarizer format README.md --style comprehensive

# Library style with TOC
readme-summarizer format README.md --style library --toc
```

#### Adding Missing Sections

```bash
# Add placeholders for missing sections
readme-summarizer format README.md --add-missing

# Sort sections by convention
readme-summarizer format README.md --sort

# Both together
readme-summarizer format README.md --add-missing --sort -o README.md
```

#### Quality Improvements

```bash
# Apply automatic improvements
readme-summarizer format README.md --improve

# Full improvement with comprehensive style
readme-summarizer format README.md --style comprehensive --improve --add-missing --sort
```

#### Emoji Handling

```bash
# Keep emojis as-is (default)
readme-summarizer format README.md

# Remove all emojis
readme-summarizer format README.md --emoji remove

# Standardize emoji usage in headers
readme-summarizer format README.md --emoji standardize
```

#### Advanced Options

```bash
# Disable table of contents
readme-summarizer format README.md --no-toc

# Don't fix heading levels
readme-summarizer format README.md --no-fix-headings

# Don't sort sections
readme-summarizer format README.md --no-sort
```

### Programmatic Usage (Formatter)

#### Quick Formatting

```python
from summarize_readme.formatter import format_readme, FormatStyle

# Format with standard style
content = "# My Project\n\n..."
formatted = format_readme(content, style=FormatStyle.STANDARD)

# Format with custom options
formatted = format_readme(
    content,
    style=FormatStyle.LIBRARY,
    add_toc=True,
    add_missing=True
)
```

#### Advanced Usage

```python
from summarize_readme.formatter import READMEFormatter, FormatOptions, FormatStyle

# Create custom options
options = FormatOptions(
    style=FormatStyle.COMPREHENSIVE,
    add_toc=True,
    fix_headings=True,
    add_missing_sections=True,
    sort_sections=True,
    emoji_style="standardize"
)

# Create formatter
formatter = READMEFormatter(options)

# Format README
formatted = formatter.format(content)

# Format with quality improvements
formatted, improvements = formatter.format_quality_improvements(content)
print(f"Applied: {improvements}")
```

### Format Options

| Option | Description | Default |
|--------|-------------|---------|
| `style` | Formatting style preset | `standard` |
| `add_toc` | Add table of contents | `True` |
| `fix_headings` | Fix heading level inconsistencies | `True` |
| `add_missing_sections` | Add placeholders for missing sections | `False` |
| `sort_sections` | Sort sections by style convention | `False` |
| `preserve_custom_sections` | Keep custom sections at end | `True` |
| `emoji_style` | Emoji handling: keep/remove/standardize | `keep` |
| `max_line_length` | Wrap lines (None = no wrap) | `None` |

---

## Advanced Examples

### Example 1: CI/CD Quality Check

Check README quality in your CI pipeline:

```bash
#!/bin/bash
# quality-check.sh

# Extract metadata with quality report
readme-summarizer extract README.md --quality --format json -o metadata.json

# Parse score
SCORE=$(jq '.completeness_score' metadata.json)

if (( $(echo "$SCORE < 70" | bc -l) )); then
    echo "README quality score too low: $SCORE/100"
    exit 1
fi

echo "README quality: $SCORE/100 ✓"
```

### Example 2: Automated README Improvement

```python
from summarize_readme.metadata_extractor import MetadataExtractor
from summarize_readme.formatter import READMEFormatter, FormatOptions, FormatStyle
from pathlib import Path

def improve_readme(readme_path):
    """Automatically improve README quality."""
    
    # Read current README
    content = Path(readme_path).read_text(encoding='utf-8')
    
    # Analyze current state
    extractor = MetadataExtractor()
    metadata = extractor.extract(content)
    quality = extractor.quality_report(metadata)
    
    print(f"Current score: {metadata.completeness_score}/100")
    
    # Determine best style based on project type
    if 'library' in content.lower() or 'package' in content.lower():
        style = FormatStyle.LIBRARY
    elif 'api' in content.lower():
        style = FormatStyle.COMPREHENSIVE
    else:
        style = FormatStyle.STANDARD
    
    # Format with improvements
    options = FormatOptions(
        style=style,
        add_toc=True,
        add_missing_sections=True,
        sort_sections=True,
        fix_headings=True
    )
    
    formatter = READMEFormatter(options)
    improved, improvements = formatter.format_quality_improvements(content)
    
    # Re-analyze
    metadata_after = extractor.extract(improved)
    
    print(f"New score: {metadata_after.completeness_score}/100")
    print(f"Improvement: +{metadata_after.completeness_score - metadata.completeness_score}")
    
    # Save if improved
    if metadata_after.completeness_score > metadata.completeness_score:
        Path(readme_path).write_text(improved, encoding='utf-8')
        print("✓ README improved and saved")
    
    return improved, improvements

# Use it
improve_readme("README.md")
```

### Example 3: Batch Analysis

Analyze multiple READMEs and generate report:

```python
from pathlib import Path
from summarize_readme.metadata_extractor import extract_metadata
import json

def analyze_project_readmes(root_dir):
    """Analyze all READMEs in a directory tree."""
    
    results = []
    
    for readme in Path(root_dir).rglob("README.md"):
        try:
            content = readme.read_text(encoding='utf-8')
            metadata = extract_metadata(content)
            
            results.append({
                'path': str(readme.relative_to(root_dir)),
                'score': metadata.completeness_score,
                'has_installation': metadata.has_installation,
                'has_usage': metadata.has_usage,
                'has_examples': metadata.has_examples,
                'badge_count': len(metadata.badges),
                'section_count': len(metadata.sections),
            })
        except Exception as e:
            print(f"Error processing {readme}: {e}")
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Save report
    Path('readme-analysis.json').write_text(json.dumps(results, indent=2))
    
    # Print summary
    avg_score = sum(r['score'] for r in results) / len(results)
    print(f"Analyzed {len(results)} READMEs")
    print(f"Average score: {avg_score:.1f}/100")
    
    return results
```

### Example 4: Template Generation

Generate README from project metadata:

```python
from summarize_readme.formatter import READMEFormatter, FormatOptions, FormatStyle
from summarize_readme.metadata_extractor import READMEMetadata, Badge, Link

def generate_readme_template(project_name, language, license_type="MIT"):
    """Generate a README template for a new project."""
    
    # Create basic content
    initial_content = f"""# {project_name}

[Brief description of your project]

## Installation

```{language}
# Installation instructions here
```

## Usage

```{language}
# Usage examples here
```

## License

This project is licensed under the {license_type} License.
"""
    
    # Format with comprehensive style and missing sections
    options = FormatOptions(
        style=FormatStyle.COMPREHENSIVE,
        add_toc=True,
        add_missing_sections=True,
        sort_sections=True,
    )
    
    formatter = READMEFormatter(options)
    formatted = formatter.format(initial_content)
    
    return formatted

# Generate template
template = generate_readme_template("my-awesome-lib", "python")
Path("README.md").write_text(template, encoding='utf-8')
```

---

## Use Cases

### 1. **Documentation Quality Assurance**
- Enforce README standards across organization
- Track documentation completeness metrics
- CI/CD quality gates

### 2. **Project Analysis**
- Extract structured data from documentation
- Build project catalogs and indexes
- Analyze tech stack across repositories

### 3. **Automated Improvements**
- Fix formatting inconsistencies
- Add missing sections automatically
- Standardize documentation structure

### 4. **Migration & Modernization**
- Update old READMEs to modern standards
- Apply consistent styling across projects
- Add best practices (TOC, badges, etc.)

### 5. **Template Generation**
- Create project starter templates
- Generate boilerplate documentation
- Customize for different project types

### 6. **Compliance & Reporting**
- Extract license information
- Verify required sections exist
- Generate documentation reports

---

## Tips & Best Practices

### For Extraction

1. **Use `--quality` flag** to understand README completeness
2. **Export to JSON** for integration with other tools
3. **Use `--detailed`** when you need full section content and code blocks
4. **Combine with CI/CD** to enforce documentation standards

### For Formatting

1. **Always preview first** with `--preview` before committing changes
2. **Choose appropriate style** for your project type
3. **Use `--add-missing`** to discover what sections should be added
4. **Enable `--sort`** to organize sections logically
5. **Apply `--improve`** for automatic quality enhancements

### Combined Workflow

```bash
# 1. Analyze current state
readme-summarizer extract README.md --quality

# 2. Preview improvements
readme-summarizer format README.md --preview --style comprehensive

# 3. Apply formatting
readme-summarizer format README.md --improve --add-missing --sort -o README.md

# 4. Verify improvements
readme-summarizer extract README.md --quality
```

---

## Installation Note

For YAML export support, install the optional dependency:

```bash
pip install readme-summarizer[yaml]
```

---

## Related Commands

- `readme-summarizer summarize` - Generate text summaries
- `readme-summarizer normalize` - Clean and preprocess content
- `readme-summarizer detect` - Find README files in repositories
- `readme-summarizer wrap` - Advanced summarization with AI

---

## Feedback & Contributing

Found a bug or have a suggestion? Please open an issue on GitHub!

Happy documenting! 📚✨
