# Input Resolver & Repo Fetcher

The README Summarizer CLI includes an advanced **Input Resolver** feature that intelligently detects and fetches README files from multiple sources.

## Overview

The Input Resolver automatically detects the type of input you provide and handles it appropriately. No need to specify different flags for different input types - just provide the source and the tool figures it out!

## Supported Input Formats

### 1. Local Files
Standard file paths on your system.

```bash
# Current directory
readme-summarizer README.md

# Relative path
readme-summarizer ./docs/README.md

# Absolute path (Windows)
readme-summarizer C:\Projects\myapp\README.md

# Absolute path (Unix/Mac)
readme-summarizer /home/user/projects/myapp/README.md
```

### 2. Direct URLs
Any direct URL to a README file.

```bash
# Any web server
readme-summarizer https://example.com/documentation/readme.md

# Documentation sites
readme-summarizer https://docs.myproject.org/README.md
```

### 3. GitHub Repository URLs
Full GitHub repository URLs - automatically finds and fetches the README.

```bash
# Main repository page
readme-summarizer https://github.com/owner/repository

# With .git extension
readme-summarizer https://github.com/owner/repository.git

# Specific branch (via tree URL)
readme-summarizer https://github.com/owner/repository/tree/develop
```

### 4. GitHub Shorthand Notation ⭐ NEW!
The easiest way to fetch from GitHub - just use `owner/repo` format!

```bash
# Basic format
readme-summarizer owner/repo

# Examples
readme-summarizer torvalds/linux
readme-summarizer microsoft/vscode
readme-summarizer facebook/react

# With specific branch
readme-summarizer owner/repo@branch-name
readme-summarizer microsoft/vscode@dev
readme-summarizer facebook/react@main
```

### 5. GitHub Raw URLs
Direct links to raw file content on GitHub.

```bash
readme-summarizer https://raw.githubusercontent.com/owner/repo/main/README.md
readme-summarizer https://raw.githubusercontent.com/owner/repo/develop/docs/README.md
```

## How It Works

### Automatic Detection
The Input Resolver uses intelligent pattern matching to detect the input type:

1. **Local File Check**: First checks if the path exists on your filesystem
2. **GitHub Shorthand Pattern**: Checks for `owner/repo` or `owner/repo@branch` format
3. **URL Parsing**: Analyzes URLs to distinguish between:
   - GitHub repository URLs
   - GitHub raw URLs
   - Other direct URLs

### GitHub README Fetching

When fetching from GitHub, the resolver uses the **GitHub API** (no authentication required for public repos) which provides several advantages:

✅ **Automatic README Detection**: Finds README files regardless of case (README.md, readme.md, README, etc.)

✅ **Default Branch Detection**: Automatically uses the repository's default branch (main/master)

✅ **Multiple Format Support**: Handles README.md, README.rst, README.txt, and more

✅ **Fallback Mechanism**: If API fails, falls back to trying common README filenames directly

### Branch Specification

You can specify a branch in multiple ways:

```bash
# Using shorthand notation
readme-summarizer owner/repo@develop
readme-summarizer owner/repo@feature-x

# Using GitHub tree URL
readme-summarizer https://github.com/owner/repo/tree/develop
```

If no branch is specified, the repository's default branch is used automatically.

## Usage Examples

### Single Source
```bash
# Fetch and summarize from GitHub
readme-summarizer microsoft/TypeScript

# With options
readme-summarizer facebook/react --length short --bullets
```

### Multiple Sources
Process multiple sources in one command:

```bash
# Mix different source types
readme-summarizer README.md owner/repo https://example.com/readme.md

# Multiple GitHub repos
readme-summarizer torvalds/linux microsoft/vscode python/cpython
```

### Output to File
```bash
# Save summary to file
readme-summarizer microsoft/vscode -o vscode-summary.txt

# JSON output with metadata
readme-summarizer owner/repo --format json -o output.json
```

### Verbose Mode
See detailed information about what's being fetched:

```bash
readme-summarizer owner/repo --verbose
```

Output will show:
- Detected input type
- GitHub repository details
- README file found (name, branch, size)
- Fetch progress

### Batch Processing
Create a file with multiple sources (one per line):

**sources.txt:**
```
torvalds/linux
microsoft/vscode
https://github.com/python/cpython
./local/README.md
https://example.com/readme.md
facebook/react@main
```

Then process all at once:
```bash
readme-summarizer batch sources.txt --output-dir ./summaries
```

### Info Command
Get detailed information about a README before summarizing:

```bash
readme-summarizer info owner/repo
```

Shows:
- Source type and metadata
- Repository and branch information
- File size, line count, word count
- Number of sections, links, badges, images
- List of all section headings

## Advanced Features

### Repository Metadata
When fetching from GitHub, the tool collects rich metadata:

- Repository owner and name
- Branch name
- README file name and path
- Download and web URLs
- File size

This metadata is included in JSON output and shown in verbose mode.

### Error Handling
The resolver includes comprehensive error handling:

- **File Not Found**: Clear error message if local file doesn't exist
- **GitHub 404**: Helpful message if repository or README not found
- **Network Errors**: Timeout handling and retry logic
- **API Rate Limits**: Graceful degradation to fallback methods

### README Variant Detection
When the GitHub API doesn't find a README, the resolver tries multiple common filenames:

- README.md
- readme.md
- README
- readme
- README.markdown
- readme.markdown
- README.rst
- readme.rst
- README.txt
- readme.txt

### Branch Fallback
If a specific branch is not specified, the resolver tries:

1. Repository's default branch (via API)
2. `main` branch
3. `master` branch

## Technical Details

### GitHub API
- Endpoint: `https://api.github.com/repos/{owner}/{repo}/readme`
- No authentication required for public repositories
- Rate limit: 60 requests/hour (unauthenticated)
- Content returned in base64 encoding (automatically decoded)

### Performance
- Requests include proper User-Agent headers
- Connection pooling via `requests.Session`
- 15-second timeout for GitHub requests
- 10-second timeout for fallback attempts

### Security
- No credentials stored or required
- HTTPS only for GitHub communication
- Input validation to prevent injection attacks
- Safe file path handling

## Troubleshooting

### Repository Not Found
```bash
Error: No README file found in repository owner/repo
```
**Solutions:**
- Verify the repository exists and is public
- Check if the repository has a README file
- Try specifying a branch: `owner/repo@main`

### Rate Limiting
If you hit GitHub API rate limits (rare for normal use):
- Wait an hour for rate limit to reset
- The tool will automatically fall back to raw URL fetching

### Network Issues
```bash
Error: Failed to fetch from GitHub API: timeout
```
**Solutions:**
- Check your internet connection
- Try again (temporary network issues)
- Verify GitHub is accessible from your network

## Examples Gallery

### Quick GitHub Summaries
```bash
# Popular projects
readme-summarizer tensorflow/tensorflow
readme-summarizer nodejs/node
readme-summarizer rust-lang/rust

# Your own projects
readme-summarizer yourusername/your-repo
```

### Comparing Projects
```bash
# Generate summaries for comparison
readme-summarizer \
  facebook/react \
  vuejs/vue \
  angular/angular \
  --format markdown \
  -o frameworks-comparison.md
```

### Documentation Workflows
```bash
# Generate short summaries for a documentation index
readme-summarizer project/repo --length short --bullets > index.md
```

### Mixed Source Analysis
```bash
# Analyze multiple documentation sources
readme-summarizer \
  ./local-docs/README.md \
  github-org/repo \
  https://docs.example.com/README.md \
  --format json \
  -o analysis.json
```

## Best Practices

1. **Use Shorthand When Possible**: `owner/repo` is the fastest and easiest way to fetch from GitHub

2. **Specify Branches for Accuracy**: If you need a specific version, use `owner/repo@branch`

3. **Enable Verbose Mode for Debugging**: Use `--verbose` to see exactly what's being fetched

4. **Batch Process Large Sets**: Use the `batch` command for processing many repositories

5. **Check Info First**: Use `readme-summarizer info owner/repo` to verify before summarizing

## Future Enhancements

Potential future features:
- GitLab support with similar shorthand notation
- Bitbucket repository support
- Private repository access with authentication
- Caching for frequently accessed repositories
- Support for other files besides README (CONTRIBUTING.md, etc.)

## API Reference

For developers integrating the input resolver:

```python
from summarize_readme.input_resolver import InputResolver

# Create resolver
resolver = InputResolver(verbose=True)

# Detect input type
input_type = resolver.detect_input_type("owner/repo")

# Resolve content
content, metadata = resolver.resolve("owner/repo")

# Access metadata
print(f"Owner: {metadata['owner']}")
print(f"Repo: {metadata['repo']}")
print(f"Branch: {metadata['branch']}")
print(f"File: {metadata['file']}")
```

See the [API Documentation](API.md) for complete details.
