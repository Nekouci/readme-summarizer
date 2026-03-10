# Installation & Setup Guide

## Prerequisites

You need Python 3.8+ with pip installed.

## Installation Steps

### Option 1: Using pip (Recommended)

```powershell
# Install dependencies
pip install typer[all] rich requests markdown beautifulsoup4

# Install the package in editable mode
pip install -e .
```

### Option 2: Install from PyPI (when published)

```powershell
pip install readme-summarizer
```

### Option 3: Direct execution (Development)

If pip is not working properly, you can run directly:

```powershell
# Set PYTHONPATH
$env:PYTHONPATH = "c:\Users\dj-emina\summarize-readme\src"

# Run the CLI
python -m summarize_readme.cli --help
```

## Verify Installation

After installation, test with:

```powershell
# Using installed command (Option 1)
readme-summarizer --help
rsm --help

# Or using Python module
python -m summarize_readme.cli --help
```

## Troubleshooting

### pip not found

If you get "No module named pip":

```powershell
# Download get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

# Install pip
python get-pip.py
```

### Import errors

Make sure all dependencies are installed:

```powershell
pip list | Select-String -Pattern "typer|rich|requests|markdown|beautifulsoup"
```

Expected output should show:
- typer (0.9.0+)
- rich (13.0.0+)
- requests (2.31.0+)
- markdown (3.5.0+)
- beautifulsoup4 (4.12.0+)

## Testing

Run the test suite:

```powershell
pip install pytest pytest-cov
pytest
```

## Quick Start Examples

Once installed, try these commands:

```powershell
# See all commands
readme-summarizer --help

# Summarize your README
readme-summarizer README.md

# Get detailed information
readme-summarizer info README.md

# Batch processing
readme-summarizer batch sources.txt --output-dir summaries

# JSON output
readme-summarizer README.md --format json --output summary.json
```
