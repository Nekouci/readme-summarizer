# Metadata Extractor & Formatter - Quick Reference

⚡ **Quick guide for the new advanced features**

## Quick Start

### Extract Metadata

```bash
# Basic extraction (JSON output)
readme-summarizer extract README.md

# With quality report
readme-summarizer extract README.md --quality

# Save to file
readme-summarizer extract README.md -o metadata.json

# Human-readable text format
readme-summarizer extract README.md --format text --quality
```

### Format README

```bash
# Preview changes
readme-summarizer format README.md --preview

# Format with standard style
readme-summarizer format README.md -o formatted.md

# Add missing sections
readme-summarizer format README.md --add-missing -o README.md

# Comprehensive style with all improvements
readme-summarizer format README.md --style comprehensive --improve --add-missing --sort -o README.md
```

## Common Patterns

### Check Documentation Quality

```bash
# Get quality score and suggestions
readme-summarizer extract README.md --quality --format text
```

### Standardize Project Documentation

```bash
# Format for library/package
readme-summarizer format README.md --style library --sort --add-missing -o README.md

# Format for application
readme-summarizer format README.md --style application --sort --add-missing -o README.md
```

### Export Structured Data

```bash
# Export as JSON
readme-summarizer extract README.md -o metadata.json

# Export as YAML (requires: pip install pyyaml)
readme-summarizer extract README.md --format yaml -o metadata.yaml
```

### Batch Process READMEs

```bash
# Create a script to process multiple READMEs
for file in */README.md; do
  echo "Processing $file"
  readme-summarizer extract "$file" --quality -o "${file%.md}_metadata.json"
  readme-summarizer format "$file" --style standard --improve -o "$file"
done
```

## Formatting Styles

| Style | Use For |
|-------|---------|
| `minimal` | Small utilities, simple scripts |
| `standard` | Most open-source projects (default) |
| `comprehensive` | Major projects, frameworks, large libraries |
| `library` | Node/Python/Ruby packages, SDKs, APIs |
| `application` | CLI tools, desktop apps, web apps |

## Format Options Quick Reference

| Option | Description | Default |
|--------|-------------|---------|
| `--style` | Formatting style preset | `standard` |
| `--toc` / `--no-toc` | Add table of contents | `yes` |
| `--add-missing` | Add missing sections | `no` |
| `--fix-headings` | Fix heading levels | `yes` |
| `--sort` | Sort sections by convention | `no` |
| `--emoji keep/remove/standardize` | Emoji handling | `keep` |
| `--improve` | Apply quality improvements | `no` |
| `--preview` | Show preview without saving | `no` |

## Extract Options Quick Reference

| Option | Description | Default |
|--------|-------------|---------|
| `--format json/yaml/text` | Output format | `json` |
| `--quality` | Include quality analysis | `no` |
| `--detailed` | Include full content | `no` |
| `--output` | Save to file | console |

## Programmatic Usage

### Python API

```python
from summarize_readme.metadata_extractor import extract_metadata
from summarize_readme.formatter import format_readme, FormatStyle

# Read README
content = open("README.md").read()

# Extract metadata
metadata = extract_metadata(content)
print(f"Score: {metadata.completeness_score}/100")

# Format README
formatted = format_readme(
    content,
    style=FormatStyle.LIBRARY,
    add_toc=True,
    add_missing=True
)

# Save
open("README_formatted.md", "w").write(formatted)
```

## What Gets Extracted?

✅ **Basic Info**: Title, description, language, license, version  
✅ **Technical**: Tech stack, dependencies, code blocks  
✅ **Structure**: Sections, TOC, hierarchy  
✅ **Resources**: Badges (typed), links (categorized), URLs  
✅ **Quality**: Completeness score, missing elements, suggestions

## Typical Workflow

```bash
# 1. Analyze current state
readme-summarizer extract README.md --quality --format text

# 2. Preview improvements  
readme-summarizer format README.md --preview --style comprehensive

# 3. Apply formatting
readme-summarizer format README.md --improve --add-missing --sort -o README.md

# 4. Verify improvements
readme-summarizer extract README.md --quality --format text
```

## Quality Score Breakdown

- **90-100 (A)**: Excellent documentation
- **80-89 (B)**: Good documentation, minor improvements needed
- **70-79 (C)**: Adequate documentation, several improvements suggested
- **60-69 (D)**: Below average, significant improvements needed
- **0-59 (F)**: Poor documentation, major overhaul recommended

## Tips

💡 **Always preview first**: Use `--preview` before overwriting files  
💡 **Start simple**: Use standard style, then customize if needed  
💡 **Check quality**: Run `extract --quality` to understand completeness  
💡 **Combine features**: Use `normalize`, `extract`, and `format` together  
💡 **CI integration**: Add quality checks to your CI/CD pipeline

## Examples

### Complete Documentation Workflow

```bash
# Step 1: Check current quality
readme-summarizer extract README.md --quality

# Step 2: Normalize content (clean up)
readme-summarizer normalize README.md -o README_clean.md

# Step 3: Format with improvements
readme-summarizer format README_clean.md --style comprehensive --improve --add-missing --sort -o README.md

# Step 4: Verify final quality
readme-summarizer extract README.md --quality
```

### Generate Reports

```bash
# Generate metadata report
readme-summarizer extract README.md --quality --format text > README_report.txt

# Export structured data for analysis
readme-summarizer extract README.md --detailed -o metadata.json
```

---

📚 **Full Documentation**: See [METADATA_FORMATTER_GUIDE.md](METADATA_FORMATTER_GUIDE.md)  
🎮 **Demo**: Run `python samples/metadata_formatter_demo.py`  
🐛 **Issues**: Report on GitHub

**Happy documenting!** ✨
