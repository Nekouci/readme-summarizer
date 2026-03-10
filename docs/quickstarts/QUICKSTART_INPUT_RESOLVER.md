# Quick Start: Input Resolver & Repo Fetcher

Get started with the advanced input resolver feature in 5 minutes!

## Installation

Make sure you have the package installed:

```bash
pip install -e .
```

## Quick Examples

### 1. Fetch from GitHub (Easiest!)

```bash
# Just use owner/repo notation
readme-summarizer microsoft/vscode

# That's it! The tool automatically:
# - Detects it's a GitHub repo
# - Finds the README file
# - Fetches the content
# - Summarizes it
```

### 2. Specify a Branch

```bash
# Use @ to specify a branch
readme-summarizer facebook/react@main
readme-summarizer rust-lang/rust@stable
```

### 3. Multiple Repos at Once

```bash
# Process several repos
readme-summarizer torvalds/linux microsoft/vscode python/cpython
```

### 4. Mix Different Sources

```bash
# Combine local files, URLs, and GitHub repos
readme-summarizer \
  README.md \
  microsoft/TypeScript \
  https://example.com/readme.md
```

### 5. Save Output

```bash
# Save to file
readme-summarizer nodejs/node -o nodejs-summary.txt

# JSON format with metadata
readme-summarizer facebook/react --format json -o react.json
```

### 6. Customize Summary

```bash
# Short bullet-point summary
readme-summarizer microsoft/vscode --length short --bullets

# Long detailed summary
readme-summarizer python/cpython --length long

# Extract links
readme-summarizer torvalds/linux --links
```

### 7. Get Detailed Info

```bash
# See detailed analysis before summarizing
readme-summarizer info microsoft/TypeScript

# Shows:
# - Repository info (owner, repo, branch)
# - File size and line count
# - Sections, links, badges, images
# - List of all section headings
```

### 8. Verbose Mode

```bash
# See what's happening behind the scenes
readme-summarizer owner/repo --verbose

# Shows:
# - Detected input type
# - Fetching progress
# - File found (name, branch, size)
# - GitHub API interactions
```

## All Supported Input Formats

| Format | Example | Description |
|--------|---------|-------------|
| **GitHub Shorthand** | `owner/repo` | Easiest way to fetch from GitHub |
| **GitHub w/ Branch** | `owner/repo@branch` | Fetch from specific branch |
| **GitHub URL** | `https://github.com/owner/repo` | Full GitHub repository URL |
| **Raw GitHub URL** | `https://raw.githubusercontent.com/...` | Direct raw file URL |
| **Any URL** | `https://example.com/readme.md` | Any web URL |
| **Local File** | `README.md` or `./docs/README.md` | Files on your system |

## Common Use Cases

### Compare Multiple Projects

```bash
# Compare web frameworks
readme-summarizer \
  facebook/react \
  vuejs/vue \
  angular/angular \
  --length short \
  --bullets \
  -o framework-comparison.md
```

### Daily Repo Check

```bash
# Quick check on projects you follow
readme-summarizer microsoft/vscode --length short
readme-summarizer python/cpython --length short
```

### Documentation Generation

```bash
# Generate documentation summaries
readme-summarizer your-org/project-1 -o docs/project-1.md
readme-summarizer your-org/project-2 -o docs/project-2.md
```

### Research Mode

```bash
# Get detailed info on interesting projects
readme-summarizer info tensorflow/tensorflow
readme-summarizer info pytorch/pytorch
```

### Batch Processing

Create `repos.txt`:
```
microsoft/vscode
python/cpython
torvalds/linux
facebook/react
rust-lang/rust
```

Process all:
```bash
readme-summarizer batch repos.txt --output-dir ./summaries
```

## Tips & Tricks

### 1. Use the Short Alias

```bash
# Instead of 'readme-summarizer', use 'rsm'
rsm microsoft/vscode
rsm owner/repo --length short
```

### 2. Chain with Other Tools

```bash
# Count words in summary
rsm microsoft/vscode | wc -w

# Search for keywords
rsm python/cpython | grep -i "performance"

# Save and view
rsm torvalds/linux -o linux.md && cat linux.md
```

### 3. JSON for Automation

```bash
# Get machine-readable output
rsm microsoft/TypeScript --format json > typescript.json

# Use with jq
rsm owner/repo --format json | jq '.summary'
```

### 4. Quiet Mode for Scripts

```bash
# Suppress progress output
rsm owner/repo --quiet -o summary.txt

# Perfect for automation
for repo in microsoft/vscode python/cpython; do
  rsm "$repo" --quiet -o "${repo//\//_}.txt"
done
```

## Troubleshooting

### Repository Not Found

```bash
Error: No README file found in repository owner/repo
```

**Fix:** Verify the repository exists and is public, or try specifying a branch:
```bash
rsm owner/repo@main
```

### Rate Limiting

GitHub API allows 60 requests/hour without authentication. If you hit the limit:

- Wait an hour for the reset
- The tool will automatically fall back to alternative methods
- Consider spacing out your requests

### Network Issues

If you see timeout errors:
```bash
Error: Failed to fetch from GitHub API: timeout
```

**Fix:** 
- Check your internet connection
- Try again (temporary issues)
- Use `--verbose` to see what's happening

## Next Steps

- Read the full documentation: [`INPUT_RESOLVER.md`](INPUT_RESOLVER.md)
- Check out examples: [`samples/input_resolver_demo.py`](samples/input_resolver_demo.py)
- Explore CLI options: `readme-summarizer --help`

## Need Help?

- Check the [main README](README.md)
- Look at [example usage](samples/)
- Run `readme-summarizer --help` for all options
- Run `readme-summarizer info --help` for info command options

Happy summarizing! 🚀
