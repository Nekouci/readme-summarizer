# CLI Demo & Command Reference

## Command Overview

```
readme-summarizer [COMMAND] [OPTIONS]

Commands:
  summarize  - Summarize README file(s) (default command)
  batch      - Process multiple files from a list
  info       - Display detailed README analysis
  version    - Show version information
```

## 📖 Detailed Command Reference

### 1. `summarize` Command

**Basic Syntax:**
```bash
readme-summarizer summarize SOURCE [SOURCE...] [OPTIONS]
```

**Arguments:**
- `SOURCE` - File path(s) or URL(s) to summarize (required, supports multiple)

**Options:**

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--output` | `-o` | Path | console | Output file path |
| `--format` | `-f` | Choice | text | Output format: text, json, markdown, html |
| `--length` | `-l` | Choice | medium | Summary length: short, medium, long, full |
| `--bullets` | `-b` | Flag | false | Format summary as bullet points |
| `--badges` | | Flag | true | Include badge information |
| `--no-badges` | | Flag | | Exclude badge information |
| `--sections` | | Flag | true | Include sections list |
| `--no-sections` | | Flag | | Exclude sections list |
| `--links` | | Flag | false | Extract and list all links |
| `--verbose` | `-v` | Flag | false | Enable verbose output |
| `--quiet` | `-q` | Flag | false | Suppress all non-error output |

**Examples:**

```bash
# Basic summarization
readme-summarizer README.md

# Can also use 'summarize' explicitly
readme-summarizer summarize README.md

# Multiple files
readme-summarizer README.md CHANGELOG.md LICENSE

# From URL
readme-summarizer https://raw.githubusercontent.com/python/cpython/main/README.rst

# Mixed sources
readme-summarizer README.md https://example.com/README.md

# Short bullet-point summary
readme-summarizer README.md -l short -b

# JSON output with links
readme-summarizer README.md -f json --links

# Save to file
readme-summarizer README.md -o summary.txt

# Full analysis in markdown
readme-summarizer README.md -l full -f markdown -o full.md

# Quiet mode (no console output)
readme-summarizer README.md -o out.txt -q

# Verbose processing details
readme-summarizer README.md -v

# No badges or sections, just description
readme-summarizer README.md --no-badges --no-sections
```

**Output Examples:**

TEXT format:
```
**My Awesome Project**

A revolutionary tool that simplifies README management with advanced
parsing capabilities and multiple output formats...

Sections: Installation, Usage, Features, Contributing, License
```

JSON format:
```json
{
  "title": "My Awesome Project",
  "description": "A revolutionary tool...",
  "sections": ["Installation", "Usage", "Features", "Contributing", "License"],
  "badges_count": 5,
  "links_count": 12,
  "summary": "**My Awesome Project**\n\nA revolutionary tool..."
}
```

---

### 2. `batch` Command

**Syntax:**
```bash
readme-summarizer batch INPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE` - File containing list of README paths/URLs (one per line)

**Options:**

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--output-dir` | `-d` | Path | console | Directory for output files |
| `--format` | `-f` | Choice | text | Output format |
| `--continue` | `-c` | Flag | false | Continue processing on errors |

**Input File Format:**

sources.txt:
```
README.md
docs/USAGE.md
https://raw.githubusercontent.com/user/repo/main/README.md
../other-project/README.md
# Comments are ignored
```

**Examples:**

```bash
# Process all sources (output to console)
readme-summarizer batch sources.txt

# Save to individual files
readme-summarizer batch sources.txt -d ./summaries

# JSON format with output directory
readme-summarizer batch sources.txt -d output -f json

# Continue even if some fail
readme-summarizer batch sources.txt -d out --continue
```

**Output:**
```
Reading batch file: sources.txt
Found 4 sources to process

[1/4] Processing: README.md
  ✓ Saved to summaries/README_summary.text
[2/4] Processing: docs/USAGE.md
  ✓ Saved to summaries/USAGE_summary.text
[3/4] Processing: https://raw.githubusercontent.com/user/repo/main/README.md
  ✓ Saved to summaries/url_3_summary.text
[4/4] Processing: ../other-project/README.md
  ✓ Saved to summaries/README_summary.text

Results: 4 succeeded, 0 failed
```

---

### 3. `info` Command

**Syntax:**
```bash
readme-summarizer info SOURCE
```

**Arguments:**
- `SOURCE` - README file path or URL to analyze

**Examples:**

```bash
# Analyze local file
readme-summarizer info README.md

# Analyze from URL
readme-summarizer info https://raw.githubusercontent.com/user/repo/main/README.md
```

**Output:**
```
Analyzing: README.md

┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Metric                   ┃ Value      ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ File Size                │ 15234 bytes│
│ Lines                    │ 342        │
│ Word Count               │ 2145       │
│ Sections                 │ 8          │
│ Code Blocks              │ 12         │
│ Links                    │ 23         │
│ Badges                   │ 5          │
│ Images                   │ 3          │
└──────────────────────────┴────────────┘

Sections Found:
  • Installation
  • Usage
  • Features
  • API Reference
  • Contributing
  • License
  • Changelog
  • Credits
```

---

### 4. `version` Command

**Syntax:**
```bash
readme-summarizer version
```

**Output:**
```
README Summarizer version 0.1.0
```

---

## 🎯 Common Use Cases

### Use Case 1: Quick Documentation Review
```bash
# Get a quick overview of a project's README
readme-summarizer README.md -l short -b
```

### Use Case 2: Create Documentation Index
```bash
# Generate JSON index of all READMEs
readme-summarizer batch all-readmes.txt -f json -d index/
```

### Use Case 3: README Quality Check
```bash
# Analyze README structure and content
readme-summarizer info README.md
```

### Use Case 4: Multi-Project Summary Report
```bash
# Create markdown summary of multiple projects
readme-summarizer proj1/README.md proj2/README.md proj3/README.md \
  -f markdown -o projects-summary.md
```

### Use Case 5: GitHub README Preview
```bash
# Quick preview of a GitHub project
readme-summarizer https://raw.githubusercontent.com/user/repo/main/README.md -v
```

---

## 💡 Pro Tips

1. **Use the short alias for quick access:**
   ```bash
   rsm README.md
   ```

2. **Chain with other commands:**
   ```bash
   # Find all READMEs and create index
   Get-ChildItem -Recurse -Filter "README.md" | 
     ForEach-Object { $_.FullName } > readmes.txt
   readme-summarizer batch readmes.txt -d summaries
   ```

3. **Pipe to other tools:**
   ```bash
   readme-summarizer README.md -f json | ConvertFrom-Json
   ```

4. **Quick stats:**
   ```bash
   readme-summarizer info README.md | Select-String "Word Count"
   ```

5. **Silent processing:**
   ```bash
   readme-summarizer batch sources.txt -d out -q
   # Only errors will be shown
   ```

---

## 🔍 Tab Completion

Enable shell completion for faster typing:

**Bash:**
```bash
readme-summarizer --install-completion bash
```

**PowerShell:**
```powershell
readme-summarizer --install-completion powershell
```

**Zsh:**
```zsh
readme-summarizer --install-completion zsh
```

After installation, you can use TAB to complete:
- Commands: `readme-summarizer [TAB]`
- Options: `readme-summarizer --[TAB]`
- Formats: `readme-summarizer --format [TAB]`
- Lengths: `readme-summarizer --length [TAB]`

---

## 🐛 Error Handling

The CLI provides clear error messages:

```bash
# File not found
$ readme-summarizer nonexistent.md
Error: File not found: nonexistent.md

# Invalid URL
$ readme-summarizer https://invalid-url
Error: Failed to fetch URL: HTTPConnectionPool(host='invalid-url'...)

# With verbose mode for debugging
$ readme-summarizer problem.md -v
Error: [full stack trace shown]
```

---

## 📚 Help System

Every command has built-in help:

```bash
# Main help
readme-summarizer --help

# Command-specific help
readme-summarizer summarize --help
readme-summarizer batch --help
readme-summarizer info --help
```

The help output uses rich formatting with:
- Color-coded options
- Usage examples
- Detailed descriptions
- Default values clearly marked
