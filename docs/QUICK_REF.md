# Quick Reference Card

## 🚀 Installation

```bash
pip install typer[all] rich requests markdown beautifulsoup4
pip install -e .
```

## 📖 Basic Commands

```bash
# View help
readme-summarizer --help

# Summarize a README
readme-summarizer README.md

# Short alias
rsm README.md

# Version info
readme-summarizer version
```

## 🎯 Common Options

```bash
# Save to file
readme-summarizer README.md -o summary.txt

# JSON format
readme-summarizer README.md -f json

# Short bullet points
readme-summarizer README.md -l short -b

# With links extracted
readme-summarizer README.md --links

# Quiet mode
readme-summarizer README.md -q

# Verbose mode
readme-summarizer README.md -v
```

## 📊 Analysis

```bash
# Detailed info
readme-summarizer info README.md

# Shows: size, lines, words, sections, links, badges, etc.
```

## 📦 Batch Processing

```bash
# Create sources file
echo README.md > sources.txt
echo docs/USAGE.md >> sources.txt

# Process all
readme-summarizer batch sources.txt -d ./summaries
```

## 🌐 From URLs

```bash
# GitHub raw URL
readme-summarizer https://raw.githubusercontent.com/user/repo/main/README.md

# Multiple sources
readme-summarizer README.md https://example.com/README.md
```

## ⚙️ All Options

| Option | Short | Values | Default |
|--------|-------|--------|---------|
| --output | -o | path | console |
| --format | -f | text/json/markdown/html | text |
| --length | -l | short/medium/long/full | medium |
| --bullets | -b | flag | false |
| --badges/--no-badges | | flag | true |
| --sections/--no-sections | | flag | true |
| --links | | flag | false |
| --verbose | -v | flag | false |
| --quiet | -q | flag | false |

## 🎨 Output Formats

- **text** - Plain text (default)
- **json** - JSON with metadata
- **markdown** - Markdown formatted
- **html** - HTML rendered

## 📏 Length Options

- **short** - ~50 words
- **medium** - ~150 words (default)
- **long** - ~300 words
- **full** - Complete analysis

## 💡 Pro Tips

```bash
# Tab completion (run once)
readme-summarizer --install-completion

# Pipeline usage
Get-ChildItem -Filter "README.md" -Recurse | 
  ForEach-Object { $_.FullName } > all-readmes.txt

# Create JSON index
readme-summarizer batch all-readmes.txt -f json -d index/
```

## 📚 Documentation Files

- **README.md** - Main documentation
- **INSTALL.md** - Installation guide
- **FEATURES.md** - Feature details
- **CLI_GUIDE.md** - Command reference
- **PROJECT_SUMMARY.md** - Overview

## 🔧 Development

```bash
# Run tests
pytest

# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## 🎯 Example Workflows

### Quick Summary
```bash
rsm README.md
```

### Save Analysis
```bash
rsm README.md -l long -o analysis.txt
```

### JSON Export
```bash
rsm README.md -f json --links -o data.json
```

### Batch Convert
```bash
rsm batch sources.txt -d summaries -f markdown
```

### Project Overview
```bash
rsm info README.md
```

---

**Project:** README Summarizer CLI  
**Version:** 0.1.0  
**Tech:** Typer + Rich + Python 3.8+
