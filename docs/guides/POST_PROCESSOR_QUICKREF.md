# Post-Processor Quick Reference

## Quick Start

```bash
# Basic usage
readme-summarizer postprocess input.md -o output.html

# With theme
readme-summarizer postprocess input.md --theme dracula -o output.html
```

## Themes

| Theme | Description | Best For |
|-------|-------------|----------|
| `github` | Classic GitHub style | General use, documentation |
| `material` | Material Design | Modern web apps |
| `dracula` | Dark theme with vibrant colors | Night coding, presentations |
| `nord` | Arctic bluish palette | Professional docs |
| `monokai` | Classic code theme | Code-heavy content |
| `minimalist` | Clean, simple design | Printing, PDFs |

## Export Formats

| Format | Description | Output |
|--------|-------------|--------|
| `html-standalone` | Full HTML document | `.html` |
| `html-styled` | HTML fragment | `.html` |
| `markdown-enhanced` | Markdown + metadata | `.md` |
| `json-enriched` | JSON + analytics | `.json` |
| `social-snippet` | Social media snippets | `.json` |
| `pdf-ready` | Print-optimized HTML | `.html` |

## Common Commands

### Generate Styled HTML
```bash
readme-summarizer postprocess README.md -o styled.html
```

### Dark Theme
```bash
readme-summarizer postprocess input.md --theme dracula -o dark.html
```

### Social Media Snippets
```bash
readme-summarizer postprocess README.md --format social-snippet -o social.json
```

### PDF Export
```bash
readme-summarizer postprocess docs.md --format pdf-ready --theme minimalist -o print.html
```

### With Metadata
```bash
readme-summarizer postprocess input.md --title "My Project" --author "Me" -o output.html
```

### Enhanced Markdown
```bash
readme-summarizer postprocess input.md --format markdown-enhanced -o enhanced.md
```

## Options Quick Reference

| Option | Default | Description |
|--------|---------|-------------|
| `--theme`, `-t` | `github` | Visual theme |
| `--format`, `-f` | `html-standalone` | Export format |
| `--syntax` | `github` | Code highlighting style |
| `--output`, `-o` | stdout | Output file |
| `--toc` / `--no-toc` | enabled | Table of contents |
| `--copy-buttons` | enabled | Copy buttons on code |
| `--dark-mode` | enabled | Dark mode toggle |
| `--title` | none | Document title |
| `--author` | none | Document author |
| `--source` | none | Source information |
| `--verbose`, `-v` | disabled | Verbose output |

## Python API Quick Reference

### Basic
```python
from summarize_readme.post_processor import quick_process, Theme, ExportFormat

result = quick_process(content, ExportFormat.HTML_STANDALONE, Theme.GITHUB)
```

### Advanced
```python
from summarize_readme.post_processor import create_post_processor, Theme

processor = create_post_processor(theme=Theme.DRACULA)
result = processor.process(content, ExportFormat.HTML_STANDALONE)
stats = processor.get_stats()
```

### Full Control
```python
from summarize_readme.post_processor import (
    AdvancedPostProcessor,
    PostProcessorOptions,
    Theme,
    ExportFormat,
)

options = PostProcessorOptions(
    theme=Theme.MATERIAL,
    add_table_of_contents=True,
    add_copy_buttons=True,
)

processor = AdvancedPostProcessor(options)
result = processor.process(content, ExportFormat.HTML_STANDALONE)
```

## Features At A Glance

- ✅ 6+ professional themes
- ✅ 6 export formats
- ✅ Syntax highlighting
- ✅ Copy buttons for code
- ✅ Dark mode toggle (press 'D')
- ✅ Responsive design
- ✅ Social media snippets
- ✅ Analytics & metrics
- ✅ Table of contents
- ✅ PDF-ready output
- ✅ Custom CSS/JS support
- ✅ Processing statistics

## Integration Pipeline

```bash
# Complete workflow
readme-summarizer summarize github/user/repo -o summary.md
readme-summarizer postprocess summary.md --theme dracula -o final.html
```

## Tips

1. **Dark Mode**: Press 'D' in HTML output to toggle
2. **Copy Code**: Hover over code blocks for copy button
3. **Mobile**: All outputs are responsive by default
4. **PDF**: Use `--format pdf-ready` for best results
5. **Social**: Generate snippets for Twitter, LinkedIn, etc.

## Demo

Run the demo to see all features:

```bash
python samples/post_processor_demo.py
```

## Help

```bash
readme-summarizer postprocess --help
```

---

For complete documentation, see [POST_PROCESSOR_GUIDE.md](POST_PROCESSOR_GUIDE.md)
