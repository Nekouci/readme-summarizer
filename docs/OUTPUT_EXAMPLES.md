# CLI Output Examples

This document shows what the CLI output looks like when running various commands.

## 1. Help Output

```bash
$ readme-summarizer --help
```

```
                  README Summarizer                  

🚀 Advanced CLI tool for summarizing README files with
AI-powered insights

Usage: readme-summarizer [OPTIONS] COMMAND [ARGS]...

Commands:
  summarize  Summarize README file(s) with advanced parsing
  batch      Process multiple README files from a batch input
  info       Display detailed information about a README file
  version    Display version information

Options:
  --help                Show this message and exit.
  --install-completion  Install completion for the current shell
  --show-completion     Show completion for the current shell
```

## 2. Summarize Command Help

```bash
$ readme-summarizer summarize --help
```

```
Usage: readme-summarizer summarize [OPTIONS] SOURCE...

Summarize README file(s) with advanced parsing and formatting options.

Examples:

  # Summarize a local README file
  $ readme-summarizer README.md
  
  # Summarize from GitHub URL
  $ readme-summarizer https://raw.githubusercontent.com/user/repo/main/README.md
  
  # Multiple files with output to file
  $ readme-summarizer README.md docs/USAGE.md -o summary.txt
  
  # Short bullet-point summary
  $ readme-summarizer README.md --length short --bullets
  
  # JSON output with extracted links
  $ readme-summarizer README.md --format json --links -o output.json

Arguments:
  SOURCE...  README file path(s) or URL(s) to summarize [required]

Options:
  -o, --output PATH                  Output file path
  -f, --format [text|json|markdown|html]
                                     Output format [default: text]
  -l, --length [short|medium|long|full]
                                     Summary length [default: medium]
  -b, --bullets                      Format as bullet points
  --badges / --no-badges             Include badge information [default: badges]
  --sections / --no-sections         Include sections [default: sections]
  --links                            Extract and list all links
  -v, --verbose                      Enable verbose output
  -q, --quiet                        Suppress all non-error output
  --help                             Show this message and exit.
```

## 3. Basic Summarize Output

```bash
$ readme-summarizer README.md
```

```
⠋ Processing README.md...

**README Summarizer CLI**

An advanced CLI tool for summarizing README files with powerful parsing and
formatting options. Support for local files and remote URLs, flexible output
formats, batch processing, rich terminal output with progress indicators, and
advanced parsing to extract sections, links, badges, and more.

Sections: Features, Installation, Usage, CLI Options, Examples, Development,
License, Contributing

✓ Summary completed successfully!
```

## 4. Short Bullet-Point Summary

```bash
$ readme-summarizer README.md --length short --bullets
```

```
⠋ Processing README.md...

**README Summarizer CLI**

• An advanced CLI tool for summarizing README files with powerful parsing
  and formatting options.

• Badges: 0 found

• Sections: Features, Installation, Usage, CLI Options, Examples

✓ Summary completed successfully!
```

## 5. JSON Output

```bash
$ readme-summarizer README.md --format json
```

```json
{
  "title": "README Summarizer CLI",
  "description": "An advanced CLI tool for summarizing README files with powerful parsing and formatting options.",
  "sections": [
    "Features",
    "Installation",
    "Usage",
    "CLI Options",
    "Examples",
    "Development",
    "License",
    "Contributing"
  ],
  "badges_count": 0,
  "links_count": 12,
  "summary": "**README Summarizer CLI**\n\nAn advanced CLI tool for summarizing README files..."
}
```

## 6. Verbose Mode

```bash
$ readme-summarizer README.md --verbose
```

```
Processing: README.md

File Type: Local File
File Path: c:\Users\dj-emina\summarize-readme\README.md
File Size: 15,234 bytes
Reading content...
Parsing markdown structure...
  - Found title: README Summarizer CLI
  - Found 342 lines
  - Found 8 sections
  - Extracting description...
Generating summary...
  - Max length: 150 words
  - Include badges: Yes
  - Include sections: Yes
  - Format: text

**README Summarizer CLI**

An advanced CLI tool for summarizing README files with powerful parsing and
formatting options. [content continues...]

Sections: Features, Installation, Usage, CLI Options, Examples, Development,
License, Contributing

✓ Summary completed successfully!
```

## 7. Info Command

```bash
$ readme-summarizer info README.md
```

```
Analyzing: README.md

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Metric                         ┃ Value        ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ File Size                      │ 15234 bytes  │
│ Lines                          │ 342          │
│ Word Count                     │ 2145         │
│ Sections                       │ 8            │
│ Code Blocks                    │ 12           │
│ Links                          │ 23           │
│ Badges                         │ 0            │
│ Images                         │ 0            │
└────────────────────────────────┴──────────────┘

Sections Found:
  • Features
  • Installation
  • Usage
  • CLI Options
  • Examples
  • Development
  • License
  • Contributing
```

## 8. Multiple Files

```bash
$ readme-summarizer README.md CHANGELOG.md
```

```
⠋ Processing README.md...
⠋ Processing CHANGELOG.md...

============================================================
Source: README.md (File)
============================================================

**README Summarizer CLI**

An advanced CLI tool for summarizing README files...

Sections: Features, Installation, Usage, CLI Options, Examples

============================================================
Source: CHANGELOG.md (File)
============================================================

**Changelog**

All notable changes to this project will be documented in this file...

Sections: 0.1.0, 0.0.1, Unreleased

✓ Summary completed successfully!
```

## 9. Batch Processing

```bash
$ readme-summarizer batch sources.txt --output-dir summaries
```

```
Reading batch file: sources.txt
Found 5 sources to process

[1/5] Processing: README.md
  ✓ Saved to summaries/README_summary.text
[2/5] Processing: docs/USAGE.md
  ✓ Saved to summaries/USAGE_summary.text
[3/5] Processing: CHANGELOG.md
  ✓ Saved to summaries/CHANGELOG_summary.text
[4/5] Processing: https://raw.githubusercontent.com/python/cpython/main/README.rst
  ✓ Saved to summaries/url_4_summary.text
[5/5] Processing: ../other-project/README.md
  ✓ Saved to summaries/README_summary.text

Results: 5 succeeded, 0 failed
```

## 10. Error Handling

```bash
$ readme-summarizer nonexistent.md
```

```
Error: File not found: nonexistent.md
```

```bash
$ readme-summarizer https://invalid-url/README.md -v
```

```
Processing: https://invalid-url/README.md

Error: Failed to fetch URL: HTTPConnectionPool(host='invalid-url', port=443):
Max retries exceeded with url: /README.md (Caused by
NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x...>:
Failed to establish a new connection: [Errno 11001] getaddrinfo failed'))

[Full stack trace shown in verbose mode]
```

## 11. Quiet Mode

```bash
$ readme-summarizer README.md -o summary.txt --quiet
```

```
[No output - only errors would be shown]
```

## 12. Save to File

```bash
$ readme-summarizer README.md --output summary.txt
```

```
⠋ Processing README.md...

Output saved to: summary.txt

✓ Summary completed successfully!
```

## 13. With Links Extracted

```bash
$ readme-summarizer README.md --links
```

```
⠋ Processing README.md...

**README Summarizer CLI**

An advanced CLI tool for summarizing README files with powerful parsing and
formatting options.

Sections: Features, Installation, Usage, CLI Options, Examples

Links:
  - https://pypi.org/project/typer/
  - https://github.com/Textualize/rich
  - https://github.com/yourusername/summarize-readme
  - https://docs.python.org/3/
  - https://github.com/yourusername/summarize-readme/issues
  - https://www.python.org/
  - https://pip.pypa.io/en/stable/
  - https://black.readthedocs.io/
  - https://github.com/astral-sh/ruff
  - https://mypy.readthedocs.io/

✓ Summary completed successfully!
```

## 14. Version Command

```bash
$ readme-summarizer version
```

```
README Summarizer version 0.1.0
```

## 15. Using Short Alias

```bash
$ rsm README.md
```

```
⠋ Processing README.md...

**README Summarizer CLI**

An advanced CLI tool for summarizing README files...

✓ Summary completed successfully!
```

## 16. Markdown Output Format

```bash
$ readme-summarizer README.md --format markdown
```

```
⠋ Processing README.md...

**README Summarizer CLI**

An advanced CLI tool for summarizing README files with powerful parsing and
formatting options. Multiple input sources, flexible output formats, batch
processing, rich terminal output, and advanced parsing capabilities.

Sections: Features, Installation, Usage, CLI Options, Examples, Development,
License, Contributing

✓ Summary completed successfully!
```

## Color Coding

The actual CLI uses rich colors:
- **Cyan** - File paths and processing info
- **Green** - Success messages, checkmarks
- **Yellow** - Warnings
- **Red** - Errors
- **Magenta** - Headers and titles
- **Blue** - Links and URLs
- **Bold** - Important text

## Progress Indicators

The CLI shows animated spinners during:
- File processing
- URL fetching
- Content analysis
- Summary generation
- Batch operations

## Tables

Analysis output uses formatted tables with:
- Unicode box drawing characters
- Aligned columns
- Color-coded headers
- Proper spacing

All outputs are:
- ✅ Human-readable
- ✅ Machine-parsable (JSON)
- ✅ Copy-paste friendly
- ✅ Visually appealing
- ✅ Informative
