# CLI Features Overview

## 🎯 Core Features

### 1. **Advanced Argument Parsing**
- Built with **Typer** - Modern Python CLI framework
- Type-safe arguments with validation
- Automatic help generation with rich formatting
- Tab completion support (bash, zsh, fish, PowerShell)

### 2. **Multiple Commands**

#### `summarize` - Main summarization command
```bash
readme-summarizer README.md [OPTIONS]
```

**Options:**
- `--output, -o` - Save to file instead of console
- `--format, -f` - Output format (text/json/markdown/html)
- `--length, -l` - Summary length (short/medium/long/full)
- `--bullets, -b` - Format as bullet points
- `--badges/--no-badges` - Include/exclude badge info
- `--sections/--no-sections` - Include/exclude sections
- `--links` - Extract and list all links
- `--verbose, -v` - Detailed processing output
- `--quiet, -q` - Suppress non-error output

#### `batch` - Process multiple files
```bash
readme-summarizer batch sources.txt --output-dir ./summaries
```

**Features:**
- Process multiple READMEs from a list
- Continue on error option
- Individual output files per source
- Progress tracking

#### `info` - Detailed analysis
```bash
readme-summarizer info README.md
```

**Displays:**
- File size and line count
- Word count
- Number of sections, links, badges, images, code blocks
- Section names list

#### `version` - Show version
```bash
readme-summarizer version
```

### 3. **Input Sources**

✓ Local files
✓ Remote URLs (HTTP/HTTPS)
✓ GitHub raw URLs
✓ Batch file lists
✓ Multiple inputs in single command

### 4. **Output Formats**

- **TEXT** - Clean plain text
- **JSON** - Structured data with metadata
- **MARKDOWN** - Formatted markdown
- **HTML** - Rendered HTML

### 5. **Rich Terminal UI**

- Colored output with **Rich** library
- Progress spinners
- Tables for analysis
- Panels and formatting
- Markdown rendering in terminal
- Error highlighting

### 6. **Summary Options**

**Length Presets:**
- short (50 words)
- medium (150 words)
- long (300 words)
- full (complete analysis)

**Formatting:**
- Paragraph style
- Bullet points
- Include/exclude badges
- Include/exclude sections
- Extract links

### 7. **Error Handling**

- File not found detection
- URL validation
- Network error handling
- Encoding detection (UTF-8, Latin-1 fallback)
- Continue-on-error for batch processing
- Detailed error messages with verbose mode

### 8. **Developer Features**

- Library API (use as Python package)
- Comprehensive test suite
- Type hints throughout
- Docstrings for all functions
- Configuration via pyproject.toml
- Extensible architecture

## 🏗️ Architecture

```
src/summarize_readme/
├── __init__.py      # Package initialization
├── cli.py           # CLI entrypoint (Typer app)
├── core.py          # Core summarization logic
└── utils.py         # Helper utilities
```

### Key Components:

**cli.py** (450+ lines)
- Typer application setup
- Command definitions
- Argument parsing
- Rich console output
- Progress tracking

**core.py** (200+ lines)
- `ReadmeSummarizer` class
- Markdown parsing
- Content analysis
- Format conversion
- URL fetching

**utils.py** (100+ lines)
- URL validation
- File operations
- Filename sanitization
- GitHub info extraction
- File size formatting

## 📦 Dependencies

### Core:
- **typer[all]** - CLI framework with completion
- **rich** - Terminal formatting
- **requests** - HTTP requests
- **markdown** - Markdown processing
- **beautifulsoup4** - HTML parsing

### Development:
- **pytest** - Testing framework
- **pytest-cov** - Coverage reports
- **black** - Code formatting
- **ruff** - Fast linting
- **mypy** - Type checking

## 🎨 Usage Examples

### Basic Usage
```bash
# Simple summary
readme-summarizer README.md

# Short version with bullets
readme-summarizer README.md --length short --bullets

# Save to file
readme-summarizer README.md -o summary.txt
```

### Advanced Usage
```bash
# JSON with links
readme-summarizer README.md --format json --links -o data.json

# Markdown output, long summary
readme-summarizer README.md --format markdown --length long

# Quiet mode (only errors)
readme-summarizer README.md -o out.txt --quiet

# Verbose processing
readme-summarizer README.md --verbose
```

### Batch Processing
```bash
# Create sources file
echo README.md > sources.txt
echo docs/USAGE.md >> sources.txt

# Process all
readme-summarizer batch sources.txt --output-dir summaries/

# Continue on error
readme-summarizer batch sources.txt -d out/ --continue
```

### From URLs
```bash
# GitHub README
readme-summarizer https://raw.githubusercontent.com/user/repo/main/README.md

# Multiple sources (mixed)
readme-summarizer README.md https://example.com/README.md -o combined.txt
```

### Analysis
```bash
# Detailed metrics
readme-summarizer info README.md

# Shows:
# - File size, lines, words
# - Sections count and names
# - Links, badges, images, code blocks
```

## 🔧 Configuration

The project uses **pyproject.toml** for all configuration:

- Project metadata
- Dependencies
- Build system
- Console scripts (entry points)
- Tool configurations (black, ruff, mypy, pytest)

## 🚀 Entry Points

Two command aliases are registered:

1. `readme-summarizer` - Full name
2. `rsm` - Short alias

Both execute: `summarize_readme.cli:app`

## 📝 Notes

- All paths are absolute (cross-platform)
- Unicode support (UTF-8 encoding)
- Windows PowerShell compatible
- Testable via CliRunner (Typer)
- Extensible for future features
