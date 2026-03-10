# README Summarizer CLI

A CLI tool for summarizing README files with parsing and formatting options.

## New Features

### Summarizer Wrapper

Advanced summarization orchestration with AI enhancement, caching, pipelines, and templating!

```bash
# Enhanced summarization with templates
readme-summarizer wrap README.md --template detailed

# AI-powered enhancement (requires Ollama)
readme-summarizer wrap README.md --ai --ai-provider ollama

# Compare different methods
readme-summarizer compare README.md

# Manage cache
readme-summarizer cache stats
```

See [WRAPPER_GUIDE.md](WRAPPER_GUIDE.md) for complete documentation!
Quick start: [QUICKSTART_WRAPPER.md](QUICKSTART_WRAPPER.md)

### Content Normalizer / Preprocessor

Advanced content cleaning and normalization for improved parsing accuracy!

```bash
# Normalize with standard settings
readme-summarizer normalize README.md

# Aggressive normalization with emoji removal
readme-summarizer normalize README.md --level aggressive --emoji remove

# Auto-normalize during summarization
readme-summarizer summarize README.md --normalize --norm-level standard -v
```

See [CONTENT_NORMALIZER.md](CONTENT_NORMALIZER.md) for complete documentation!

### File Detector / README Selector

Automatically discover and select multiple README files from repositories and directories!

```bash
# Detect all README files in a repository
readme-summarizer detect microsoft/vscode

# Interactive selection and processing
readme-summarizer select ./my-project

# Auto-process all READMEs
readme-summarizer select owner/repo --auto --strategy all
```

See [FILE_DETECTOR.md](FILE_DETECTOR.md) for complete documentation!

### Input Resolver & GitHub Fetcher

Fetch and summarize README files from anywhere with smart input detection!

```bash
# GitHub repos (shorthand notation)
readme-summarizer microsoft/vscode
readme-summarizer facebook/react@main

# GitHub URLs
readme-summarizer https://github.com/python/cpython

# Direct URLs
readme-summarizer https://example.com/readme.md

# Local files
readme-summarizer README.md
```

See [INPUT_RESOLVER.md](INPUT_RESOLVER.md) for complete documentation!

### Advanced Post-Processor

Transform README summaries into beautifully styled documents with multiple themes and export formats!

```bash
# Create styled HTML with theme
readme-summarizer postprocess README.md --theme dracula -o styled.html

# Export as social media snippet
readme-summarizer postprocess README.md --format social-snippet -o social.json

# PDF-ready output
readme-summarizer postprocess docs.md --format pdf-ready -o printable.html

# Enhanced Markdown with metadata
readme-summarizer postprocess input.md --format markdown-enhanced -o enhanced.md
```

**Themes Available:** GitHub, Material, Dracula, Nord, Monokai, Solarized, Minimalist

See [POST_PROCESSOR_GUIDE.md](POST_PROCESSOR_GUIDE.md) for complete documentation!

### Metadata Extractor & Formatter

Extract structured metadata and format README files with professional standards!

```bash
# Extract metadata from README
readme-summarizer extract README.md -o metadata.json

# Extract with quality analysis
readme-summarizer extract README.md --analyze-quality -v

# Format README with standard style
readme-summarizer format README.md --style standard -o formatted.md

# Apply comprehensive template
readme-summarizer format README.md --style comprehensive -o improved.md
```

See [METADATA_FORMATTER_GUIDE.md](METADATA_FORMATTER_GUIDE.md) for complete documentation!

## Features

- **Summarizer Wrapper**: Intelligent orchestration with AI enhancement, caching, pipelines, and custom templates
- **Content Normalizer**: Advanced preprocessing with unicode fixes, HTML removal, whitespace cleanup, and more
- **File Detector & Selector**: Discover all README files in directories/repos with smart prioritization and interactive selection
- **Smart Input Resolver**: Automatically detects and fetches from local files, URLs, or GitHub repos
- **GitHub Integration**: Fetch READMEs using simple `owner/repo` notation with automatic detection
- **Advanced Post-Processor**: Transform summaries into styled HTML, PDFs, or social snippets with professional themes
- **Metadata Extractor & Formatter**: Extract structured data and format READMEs with professional standards
- **Batch Processing**: Process multiple sources at once
- **Rich Terminal Output**: Beautiful, colored output with progress indicators
- **Flexible Output Formats**: Text, JSON, Markdown, and HTML
- **Advanced Parsing**: Extract sections, links, badges, and more
- **Customizable Summaries**: Control length, format, and included components

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/Nekouci/readme-summarizer
cd summarize-readme

# Install in development mode
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

### From PyPI (when published)

```bash
pip install readme-summarizer
```

## Usage

### Basic Usage

```bash
# Summarize a local README
readme-summarizer README.md

# Summarize from GitHub (shorthand)
readme-summarizer microsoft/TypeScript
readme-summarizer torvalds/linux

# Summarize from specific branch
readme-summarizer facebook/react@main

# Summarize from GitHub URL
readme-summarizer https://github.com/python/cpython

# Summarize from any URL
readme-summarizer https://raw.githubusercontent.com/user/repo/main/README.md

# Short alias
rsm microsoft/vscode
```

### GitHub Integration Examples

The tool's **Input Resolver** makes it incredibly easy to fetch from GitHub:

```bash
# Quick summary of any public GitHub repo
readme-summarizer owner/repo

# Compare frameworks
readme-summarizer facebook/react vuejs/vue angular/angular

# Specific branch or tag
readme-summarizer microsoft/vscode@dev
readme-summarizer rust-lang/rust@stable

# Get detailed info first
readme-summarizer info torvalds/linux

# Save to file
readme-summarizer nodejs/node -o nodejs-summary.md
```

### Advanced Options

```bash
# Custom length and format
readme-summarizer README.md --length short --format markdown

# Bullet-point summary
readme-summarizer README.md --bullets

# Extract and list all links
readme-summarizer README.md --links

# Save to file
readme-summarizer README.md --output summary.txt

# JSON output with all features
readme-summarizer README.md --format json --links --output data.json
```

### Batch Processing

```bash
# Create a file with paths/URLs (one per line)
echo "README.md" > sources.txt
echo "docs/USAGE.md" >> sources.txt

# Process all files
readme-summarizer batch sources.txt --output-dir ./summaries
```

### File Analysis

```bash
# Get detailed info without summarizing
readme-summarizer info README.md
```

## CLI Options

### `summarize` command

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output file path | (console) |
| `--format` | `-f` | Output format (text/json/markdown/html) | text |
| `--length` | `-l` | Summary length (short/medium/long/full) | medium |
| `--bullets` | `-b` | Format as bullet points | false |
| `--badges/--no-badges` | | Include badge information | true |
| `--sections/--no-sections` | | Include section list | true |
| `--links` | | Extract and list links | false |
| `--verbose` | `-v` | Verbose output | false |
| `--quiet` | `-q` | Suppress non-error output | false |

### `batch` command

Process multiple files from a list.

### `info` command

Display detailed analysis of a README file.

### `version` command

Show version information.

## Examples

### Example 1: Quick Summary

```bash
$ readme-summarizer README.md

**README Summarizer CLI**

An advanced CLI tool for summarizing README files with powerful parsing and formatting options.

Sections: Features, Installation, Usage, CLI Options, Examples
```

### Example 2: Detailed JSON Output

```bash
$ readme-summarizer README.md --format json --links -o analysis.json
```

Output:
```json
{
  "title": "README Summarizer CLI",
  "description": "An advanced CLI tool...",
  "sections": ["Features", "Installation", "Usage"],
  "badges_count": 0,
  "links_count": 5,
  "summary": "..."
}
```

### Example 3: Batch Processing

```bash
$ readme-summarizer batch repos.txt --output-dir summaries/
Reading batch file: repos.txt
Found 10 sources to process

[1/10] Processing: https://github.com/user/repo1/README.md
  ✓ Saved to summaries/url_1_summary.text
[2/10] Processing: ../project/README.md
  ✓ Saved to summaries/README_summary.text
...
Results: 10 succeeded, 0 failed
```

## Development

### Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

### Project Structure

```
summarize-readme/
├── src/
│   └── summarize_readme/
│       ├── __init__.py
│       ├── cli.py         # CLI entrypoint with Typer
│       ├── core.py        # Core summarization logic
│       └── utils.py       # Helper utilities
├── tests/
├── samples/
├── pyproject.toml
└── README.md
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
