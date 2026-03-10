# 🔍 File Detector / README Selector

## Overview

The **File Detector / README Selector** is an advanced feature that automatically discovers, prioritizes, and allows selection of multiple README files from directories and GitHub repositories. Instead of working with just the main README, you can now detect and process ALL README files in a project!

## Key Features

### 🎯 Intelligent Detection
- **Recursive Scanning**: Finds README files at any depth in directory structure
- **GitHub Integration**: Scans entire GitHub repository tree using GitHub API
- **Multiple Formats**: Detects README.md, readme.md, README, README.rst, README.txt, and more
- **Language-Specific**: Recognizes language-specific READMEs (README.fr.md, README.es.md, etc.)

### 📊 Smart Prioritization
README files are automatically prioritized by importance:
1. **⭐ ROOT** - Root-level README (highest priority)
2. **📖 DOCS** - Documentation directory READMEs (docs/, documentation/)
3. **🌐 LANG_SPECIFIC** - Language-specific READMEs
4. **📁 SUBDIR** - Subdirectory READMEs
5. **📄 OTHER** - Other README files

### 🎨 Interactive Selection
- Beautiful table or tree display of discovered files
- Select single or multiple files
- Quick shortcuts (all, root, docs)
- Range and comma-separated selection (1,3,5 or 1-3)

### ⚡ Batch Processing
- Process multiple selected READMEs at once
- Consistent formatting across all summaries
- Save to individual files or view in console

## Usage

### 1. Detect Command - Discovery Only

Scan and display all README files without processing them.

```bash
# Scan local directory
readme-summarizer detect ./my-project

# Scan GitHub repository
readme-summarizer detect microsoft/vscode

# Scan specific branch
readme-summarizer detect facebook/react@main

# Display as tree structure
readme-summarizer detect owner/repo --display tree

# Non-recursive scan (current directory only)
readme-summarizer detect ./docs --no-recursive

# Verbose output
readme-summarizer detect owner/repo --verbose
```

**Output Example:**
```
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ #  ┃ File                      ┃ Priority     ┃     Size ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ 1  │ 📌 README.md (root)       │ ⭐ Root      │  12.3 KB │
│ 2  │ 📄 docs/README.md         │ 📖 Docs      │   5.7 KB │
│ 3  │ 📄 README.fr.md           │ 🌐 Lang...   │   8.2 KB │
│ 4  │ 📄 examples/README.md     │ Subdir       │   3.1 KB │
└────┴───────────────────────────┴──────────────┴──────────┘

✓ Found 4 README file(s)

By Priority:
  • Root: 1
  • Docs: 1
  • Lang_Specific: 1
  • Subdir: 1
```

### 2. Select Command - Interactive Processing

Scan, select, and summarize README files interactively or automatically.

#### Interactive Mode (Default)

```bash
# Interactive selection from local directory
readme-summarizer select ./my-project

# Interactive selection from GitHub repo
readme-summarizer select microsoft/TypeScript

# Save summaries to directory
readme-summarizer select owner/repo --output-dir ./summaries

# Custom format and length
readme-summarizer select owner/repo --format markdown --length short
```

**Interactive Selection:**
```
📚 Discovered README Files

┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ #  ┃ File                      ┃ Priority     ┃     Size ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ 1  │ 📌 README.md (root)       │ ⭐ Root      │  12.3 KB │
│ 2  │ 📄 docs/README.md         │ 📖 Docs      │   5.7 KB │
│ 3  │ 📄 examples/README.md     │ Subdir       │   3.1 KB │
└────┴───────────────────────────┴──────────────┴──────────┘

Selection Options:
  • Enter numbers (e.g., 1,3,5 or 1-3)
  • Enter 'all' to select all files
  • Enter 'root' for root README only
  • Press Enter for default (root + docs)

Select README file(s) [root]: 1,2
```

#### Automatic Mode

```bash
# Auto-select root README only (fastest)
readme-summarizer select owner/repo --auto --strategy root

# Auto-select all READMEs
readme-summarizer select owner/repo --auto --strategy all

# Auto-select root + documentation READMEs
readme-summarizer select owner/repo --auto --strategy docs

# Auto-select by priority (highest priority only)
readme-summarizer select owner/repo --auto --strategy priority
```

**Selection Strategies:**
- `root` - Root-level README only (default, fastest)
- `all` - All discovered README files
- `docs` - Root + documentation READMEs
- `priority` - Highest priority README files only

### 3. Combined with Existing Features

The detector integrates seamlessly with existing features:

```bash
# Select and output as JSON
readme-summarizer select owner/repo --format json --output-dir ./output

# Short bullet-point summaries
readme-summarizer select ./project --length short --bullets

# Verbose mode for debugging
readme-summarizer select owner/repo --verbose

# Non-recursive scan (shallow)
readme-summarizer select ./docs --no-recursive
```

## Use Cases

### 1. Multilingual Projects
Automatically find and process language-specific READMEs:
```bash
readme-summarizer detect internationalized-app/
# Finds: README.md, README.fr.md, README.es.md, README.de.md
```

### 2. Monorepos
Process READMEs from multiple packages:
```bash
readme-summarizer select ./monorepo --auto --strategy all --output-dir ./summaries
# Processes: README.md, packages/pkg1/README.md, packages/pkg2/README.md, etc.
```

### 3. Documentation Projects
Extract documentation from multiple README files:
```bash
readme-summarizer select ./docs --auto --strategy docs
# Processes: README.md, docs/README.md, docs/api/README.md
```

### 4. GitHub Repository Analysis
Quickly understand a large project structure:
```bash
readme-summarizer detect microsoft/vscode --display tree
# Shows all READMEs in tree structure
```

### 5. Content Aggregation
Gather all READMEs for analysis or archival:
```bash
readme-summarizer select owner/repo --auto --strategy all --output-dir ./archive --format markdown
# Saves all READMEs as separate markdown summaries
```

## Technical Details

### Supported README Formats
The detector recognizes these patterns (case-insensitive):
- `README.md`
- `README.markdown`
- `README.rst`
- `README.txt`
- `README` (no extension)
- `README.{lang}.md` (e.g., README.fr.md, README.es.md)
- `README.{locale}.md` (e.g., README.en-us.md)

### Excluded Directories
These directories are automatically excluded from scanning:
- `__pycache__`, `node_modules`
- `.git`, `.venv`, `venv`
- `build`, `dist`, `.egg-info`
- `htmlcov`, `.pytest_cache`, `.mypy_cache`, `.tox`
- `site-packages`

### Priority Algorithm
Files are prioritized based on:
1. **Location** - Root > docs > subdirectories
2. **Depth** - Shallower files have higher priority
3. **Type** - Standard READMEs > language-specific > others

### GitHub API Integration
- Uses GitHub API v3 for repository tree scanning
- No authentication required for public repositories
- Supports all branches and tags
- Respects rate limits (60 requests/hour without auth)

### Local Directory Scanning
- Recursive up to configurable max depth (default: 10)
- Follows symlinks (with loop detection)
- Handles permission errors gracefully
- Fast parallel processing

## API Usage

You can also use the detector programmatically:

```python
from summarize_readme.readme_detector import READMEDetector
from pathlib import Path

# Initialize detector
detector = READMEDetector(verbose=True)

# Scan local directory
readme_files = detector.scan_local_directory(
    Path("./my-project"),
    recursive=True,
    max_depth=10
)

# Scan GitHub repository
readme_files = detector.scan_github_repo(
    owner="microsoft",
    repo="vscode",
    branch="main"  # Optional
)

# Display results
detector.display_readme_list(readme_files)
detector.display_readme_tree(readme_files)

# Interactive selection
selected = detector.interactive_select(readme_files)

# Automatic selection
selected = detector.auto_select(readme_files, strategy="root")

# Access file metadata
for readme in selected:
    print(f"Path: {readme.relative_path}")
    print(f"Priority: {readme.priority.name}")
    print(f"Size: {readme.size} bytes")
    print(f"Language: {readme.language}")
```

## Configuration

### Options for `detect` Command

| Option | Default | Description |
|--------|---------|-------------|
| `--recursive/-r` | `True` | Scan directories recursively |
| `--no-recursive` | - | Disable recursive scanning |
| `--max-depth` | `10` | Maximum directory depth |
| `--display` | `table` | Display mode: `table` or `tree` |
| `--verbose/-v` | `False` | Enable verbose output |

### Options for `select` Command

| Option | Default | Description |
|--------|---------|-------------|
| `--interactive/-i` | `True` | Interactive selection mode |
| `--auto` | - | Automatic selection mode |
| `--strategy/-s` | `root` | Auto-selection strategy |
| `--output-dir/-o` | None | Save summaries to directory |
| `--format/-f` | `text` | Output format (text, json, markdown, html) |
| `--length/-l` | `medium` | Summary length (short, medium, long, full) |
| `--recursive` | `True` | Scan recursively |
| `--verbose/-v` | `False` | Enable verbose output |

## Performance

### Local Scanning
- **Small repos** (<100 files): Instant
- **Medium repos** (<1000 files): < 1 second
- **Large repos** (<10000 files): 1-3 seconds

### GitHub Scanning
- **Small repos** (<100 files): 1-2 seconds
- **Large repos** (>10000 files): 3-5 seconds
- Limited by GitHub API response time

## Troubleshooting

### No README Files Found
- Check directory path is correct
- Verify README files exist and have recognized names
- Use `--verbose` flag to see what's being scanned
- Try `--no-recursive` to scan only the root directory

### GitHub Rate Limiting
- Public repos: 60 requests/hour without authentication
- Solution: Add GitHub token for 5000 requests/hour
- Or: Use direct URL instead of shorthand notation

### Permission Errors
- Some directories may be inaccessible
- Use `--verbose` to see which directories are skipped
- Run with appropriate permissions if needed

## Examples Collection

### Example 1: Quick Scan
```bash
# Just see what READMEs exist
readme-summarizer detect ./my-app
```

### Example 2: Process Root Only
```bash
# Fast processing of main README
readme-summarizer select owner/repo --auto
```

### Example 3: Full Analysis
```bash
# Process all READMEs and save
readme-summarizer select ./large-project \
  --auto --strategy all \
  --output-dir ./analysis \
  --format markdown \
  --length long
```

### Example 4: Documentation Extraction
```bash
# Get all documentation READMEs
readme-summarizer select owner/repo \
  --auto --strategy docs \
  --format json \
  --output-dir ./docs-export
```

### Example 5: Interactive Exploration
```bash
# Explore and select interactively
readme-summarizer select microsoft/TypeScript
# Then choose which ones to process
```

## Integration with Input Resolver

The detector integrates with the existing Input Resolver:

```python
from summarize_readme.input_resolver import InputResolver

resolver = InputResolver(verbose=True)

# Single README (existing behavior)
content, metadata = resolver.resolve("owner/repo")

# Multiple READMEs (new feature)
results = resolver.resolve_with_detection(
    "owner/repo",
    auto_select_strategy="all",
    interactive=False
)

for content, metadata in results:
    print(f"Processing: {metadata['detector']['relative_path']}")
    # ... process each README
```

## Future Enhancements

Potential future additions:
- 🔍 Content-based filtering (e.g., only READMEs with installation sections)
- 🏷️ Custom tagging and categorization
- 📊 Comparative analysis between multiple READMEs
- 🌐 Automatic language detection and translation
- 💾 Caching for faster repeat scans
- 🔗 Cross-reference detection between READMEs

## Conclusion

The **File Detector / README Selector** feature transforms the README Summarizer from a single-file tool into a comprehensive project documentation analyzer. Whether you're working with multilingual projects, monorepos, or just want to explore all documentation in a repository, this feature makes it simple and efficient.

**Get started:**
```bash
# Explore the feature
readme-summarizer detect microsoft/vscode

# Try interactive selection
readme-summarizer select ./your-project

# Go automatic
readme-summarizer select owner/repo --auto --strategy all -o ./summaries
```

Enjoy the enhanced README analysis capabilities! 🚀
