# Summarizer Wrapper - Quick Start

## Installation

No additional installation needed! The wrapper is included with the README Summarizer CLI.

## 5-Minute Tutorial

### 1. Basic Wrap

```bash
# Simple wrap with default template
readme-summarizer wrap README.md

# Output to file
readme-summarizer wrap README.md -o summary.txt
```

### 2. Use Templates

```bash
# Detailed template with box formatting
readme-summarizer wrap README.md --template detailed

# HTML report
readme-summarizer wrap README.md --template html -o report.html

# Slack format
readme-summarizer wrap README.md --template slack
```

### 3. AI Enhancement (Optional)

First, install Ollama (recommended for local AI):

```bash
# Download from https://ollama.ai and install
# Then pull a model
ollama pull llama3.2

# Use AI enhancement
readme-summarizer wrap README.md --ai --ai-provider ollama
```

### 4. Compare Summaries

```bash
# Compare all methods
readme-summarizer compare README.md

# Compare specific methods
readme-summarizer compare README.md -m standard -m technical
```

### 5. Manage Cache

```bash
# View cache statistics
readme-summarizer cache stats

# Clear cache
readme-summarizer cache clear
```

## Common Use Cases

### For Documentation

```bash
readme-summarizer wrap owner/repo \
  --template markdown \
  --pipeline technical \
  -o docs/summary.md
```

### For Team Sharing

```bash
readme-summarizer wrap README.md --template slack
```

### For Quick Overview

```bash
readme-summarizer wrap README.md --template compact
```

### For Analysis

```bash
readme-summarizer wrap README.md --template detailed --verbose
```

## Template Gallery

### Default Template

```bash
readme-summarizer wrap README.md
```

**Output:**
```
README Summary
==============

This is a summary of the README content...

Generated: 2024-03-07 10:30:00
Source: README.md
```

### Detailed Template

```bash
readme-summarizer wrap README.md --template detailed
```

**Output:**
```
╔═══════════════════════════════════════════════════╗
║           README SUMMARY REPORT                   ║
╚═══════════════════════════════════════════════════╝

Title: README Summary
Source: README.md
Generated: 2024-03-07 10:30:00

─────────────────────────────────────────────────────
SUMMARY
─────────────────────────────────────────────────────
This is a summary of the README content...

─────────────────────────────────────────────────────
METADATA
─────────────────────────────────────────────────────
Processing Time: 0.234s
Word Count: 45
Character Count: 289
AI Enhanced: No
Cache Hit: No
```

### Compact Template

```bash
readme-summarizer wrap README.md --template compact
```

**Output:**
```
README Summary - This is a summary... (45 words, 0.23s)
```

### Slack Template

```bash
readme-summarizer wrap README.md --template slack
```

**Output:**
```
*README Summary*

This is a summary of the README content...

_Generated: 2024-03-07 10:30:00 | Source: README.md_
```

## Pipeline Examples

### Technical Pipeline

Emphasizes code, APIs, and technical details:

```bash
readme-summarizer wrap README.md --pipeline technical
```

### User-Friendly Pipeline

Simplifies technical jargon for broader audience:

```bash
readme-summarizer wrap README.md --pipeline user-friendly
```

## AI Enhancement Examples

### With Ollama (Local)

```bash
# Basic AI enhancement
readme-summarizer wrap README.md --ai

# With specific provider
readme-summarizer wrap README.md --ai --ai-provider ollama

# Combine with pipeline
readme-summarizer wrap README.md --ai --pipeline technical
```

### With HuggingFace (Cloud)

```bash
# Set API token (optional for free tier)
export HF_API_TOKEN=your_token

# Use HuggingFace
readme-summarizer wrap README.md --ai --ai-provider huggingface
```

### Chain Provider (Try Both)

```bash
# Tries Ollama first, falls back to HuggingFace
readme-summarizer wrap README.md --ai --ai-provider chain
```

## Advanced Tips

### 1. Combine Multiple Features

```bash
readme-summarizer wrap owner/repo \
  --template html \
  --pipeline technical \
  --ai \
  --ai-provider ollama \
  --verbose \
  -o report.html
```

### 2. Process Multiple READMEs

```bash
# Use with detect/select
readme-summarizer select ./project --auto --strategy all \
  | xargs -I {} readme-summarizer wrap {} --template markdown
```

### 3. Integration with Other Tools

```bash
# Generate summary and copy to clipboard
readme-summarizer wrap README.md --template slack | pbcopy  # macOS
readme-summarizer wrap README.md --template slack | clip    # Windows

# Generate and email
readme-summarizer wrap README.md --template html -o report.html
# Then attach report.html to email
```

### 4. Refresh Cached Summary

```bash
# Force fresh processing
readme-summarizer wrap README.md --bypass-cache
```

### 5. Debug Processing

```bash
# Verbose output shows all details
readme-summarizer wrap README.md --verbose
```

## Comparison Mode

### Compare All Methods

```bash
readme-summarizer compare README.md
```

Shows side-by-side comparison of:
- Standard pipeline
- Technical pipeline
- User-friendly pipeline

### Compare Specific Methods

```bash
readme-summarizer compare README.md \
  -m standard \
  -m technical \
  -o comparison.json
```

### Save Comparison Results

```bash
readme-summarizer compare README.md -o results.json
```

**Output (results.json):**
```json
{
  "standard": {
    "content": "Summary text...",
    "metadata": {
      "word_count": 45,
      "processing_time": 0.234
    }
  },
  "technical": {
    "content": "Technical summary...",
    "metadata": {
      "word_count": 52,
      "processing_time": 0.256
    }
  }
}
```

## Cache Management

### View Cache Stats

```bash
readme-summarizer cache stats
```

**Output:**
```
Cache Statistics:

Backend         filesystem
Entries         42
Total Size      2.34 MB
Cache Directory /home/user/.cache/readme-summarizer
```

### Clear Cache

```bash
readme-summarizer cache clear
```

**Output:**
```
✓ Cleared 42 cached summaries
```

### Cache Info

```bash
readme-summarizer cache info
```

Shows cache configuration details.

## Troubleshooting

### "Ollama not available"

```bash
# Check if Ollama is running
ollama list

# Start Ollama and pull a model
ollama pull llama3.2

# Try again
readme-summarizer wrap README.md --ai
```

### "Unknown template"

```bash
# List available templates in help
readme-summarizer wrap --help

# Use a valid template
readme-summarizer wrap README.md --template detailed
```

### Slow Processing

```bash
# Check if it's a cache miss
readme-summarizer cache stats

# Disable AI if not needed
readme-summarizer wrap README.md --no-ai

# Use lighter pipeline
readme-summarizer wrap README.md --pipeline standard
```

## Next Steps

- Read full guide: [WRAPPER_GUIDE.md](WRAPPER_GUIDE.md)
- Try AI enhancement with Ollama
- Create custom templates
- Build custom pipelines
- Integrate with your workflow

## Cheat Sheet

```bash
# Basic
readme-summarizer wrap <source>

# With template
readme-summarizer wrap <source> --template <name>

# With AI
readme-summarizer wrap <source> --ai

# With pipeline
readme-summarizer wrap <source> --pipeline <name>

# Compare
readme-summarizer compare <source>

# Cache management
readme-summarizer cache <action>

# Full power
readme-summarizer wrap <source> \
  --template html \
  --pipeline technical \
  --ai \
  --verbose \
  -o output.html
```

---

**Ready to explore more?** Check out [WRAPPER_GUIDE.md](WRAPPER_GUIDE.md) for comprehensive documentation!
