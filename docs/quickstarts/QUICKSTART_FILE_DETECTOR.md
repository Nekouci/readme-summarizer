# Quick Start: File Detector Feature

## Installation

Make sure you have the latest code:
```bash
cd c:\Users\dj-emina\summarize-readme
pip install -e .
```

## Test 1: Detect Command (Local)

Scan the current project for README files:
```bash
readme-summarizer detect .
```

Expected output: Should show README.md and any other README files in the project.

## Test 2: Detect Command (GitHub)

Scan a popular GitHub repository:
```bash
readme-summarizer detect microsoft/vscode
```

Expected output: Should show all README files in the VS Code repository.

## Test 3: Select Command (Interactive)

Try interactive selection:
```bash
readme-summarizer select .
```

Then:
- Type `1` to select the first README
- Or type `all` to select all
- Or press Enter for default (root + docs)

## Test 4: Select Command (Auto)

Auto-process with different strategies:

```bash
# Root only (fastest)
readme-summarizer select . --auto --strategy root

# All READMEs
readme-summarizer select . --auto --strategy all

# Root + docs
readme-summarizer select . --auto --strategy docs
```

## Test 5: Save to Files

Process and save summaries:
```bash
mkdir summaries
readme-summarizer select . --auto --strategy all --output-dir ./summaries --format markdown
```

Check the `summaries/` directory for the output files.

## Test 6: GitHub Repository

Process a GitHub repo:
```bash
readme-summarizer select facebook/react --auto --strategy docs
```

## Test 7: Display Modes

Try different display modes:
```bash
# Table view (default)
readme-summarizer detect microsoft/TypeScript --display table

# Tree view
readme-summarizer detect microsoft/TypeScript --display tree
```

## Test 8: Run Demo Script

Run the comprehensive demo:
```bash
python samples/file_detector_demo.py
```

This will show all features in action.

## Troubleshooting

### Error: Module not found
```bash
# Reinstall in development mode
pip install -e .
```

### Error: No README files found
- Make sure you're in a directory with README files
- Try with verbose flag: `--verbose`
- Check if the path is correct

### Error: GitHub rate limit
- Wait for a while (rate limit resets hourly)
- Or use direct URLs instead of shorthand notation
- Consider adding GitHub authentication

## Quick Command Reference

```bash
# Detection
readme-summarizer detect <source> [options]

# Selection & Processing
readme-summarizer select <source> [options]

# Options
--auto / --interactive    # Selection mode
--strategy <name>         # Auto-selection strategy
--output-dir <dir>        # Save summaries
--format <type>           # Output format
--display <mode>          # Display mode (table/tree)
--recursive / --no-recursive  # Recursive scan
--verbose                 # Verbose output
```

## Next Steps

1. Read the full documentation: [FILE_DETECTOR.md](FILE_DETECTOR.md)
2. Explore API usage: Check `samples/file_detector_demo.py`
3. Try with your own projects!

Happy README detecting! 🔍✨
