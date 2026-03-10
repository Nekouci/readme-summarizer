# Advanced Post-Processor Guide

## Overview

The **Advanced Post-Processor** is a powerful feature that transforms plain README summaries and content into beautifully styled, feature-rich documents. It provides multiple export formats, visual themes, syntax highlighting, and advanced formatting capabilities.

## Key Features

### 🎨 Visual Themes

Choose from multiple professionally designed themes:

- **GitHub** - Clean, familiar GitHub style
- **Material** - Google's Material Design aesthetic
- **Dracula** - Popular dark theme with vibrant colors
- **Nord** - Arctic, north-bluish color palette
- **Monokai** - Classic dark theme for code
- **Solarized Light/Dark** - Precision colors for readability
- **Minimalist** - Clean, distraction-free design

### ✨ Export Formats

Multiple output formats tailored for different use cases:

- **HTML Styled** - Styled HTML fragment (for embedding)
- **HTML Standalone** - Complete HTML document with CSS and JavaScript
- **Markdown Enhanced** - Markdown with metadata and enhancements
- **JSON Enriched** - JSON with content analysis and statistics
- **Social Snippet** - Optimized snippets for social media platforms
- **PDF Ready** - Print-optimized HTML for PDF conversion

### 🔥 Advanced Features

- **Syntax Highlighting** - Automatic code block highlighting for Python, JavaScript, Bash, and more
- **Copy Buttons** - One-click copy for code blocks
- **Dark Mode Toggle** - Press 'D' to toggle dark/light mode (HTML)
- **Table of Contents** - Auto-generated TOC from headings
- **Responsive Design** - Mobile-friendly layouts
- **Metadata Headers** - Rich document metadata
- **Analytics** - Content analysis and statistics
- **Social Media Optimization** - Platform-specific snippet generation

## Command-Line Usage

### Basic Usage

```bash
# Post-process a file with default settings
readme-summarizer postprocess input.md -o output.html

# Specify theme and format
readme-summarizer postprocess README.md --theme dracula --format html-standalone -o styled.html

# Enable verbose mode
readme-summarizer postprocess summary.txt -v -o result.html
```

### Theme Selection

```bash
# GitHub theme (default)
readme-summarizer postprocess input.md --theme github -o github.html

# Material Design theme
readme-summarizer postprocess input.md --theme material -o material.html

# Dracula dark theme
readme-summarizer postprocess input.md --theme dracula -o dracula.html

# Nord theme
readme-summarizer postprocess input.md --theme nord -o nord.html

# Minimalist theme
readme-summarizer postprocess input.md --theme minimalist -o minimal.html
```

### Export Formats

```bash
# Standalone HTML (default)
readme-summarizer postprocess input.md --format html-standalone -o doc.html

# Enhanced Markdown with metadata
readme-summarizer postprocess input.md --format markdown-enhanced -o enhanced.md

# Social media snippets
readme-summarizer postprocess README.md --format social-snippet -o social.json

# JSON with analytics
readme-summarizer postprocess README.md --format json-enriched -o analytics.json

# PDF-ready HTML
readme-summarizer postprocess docs.md --format pdf-ready -o printable.html
```

### Customization Options

```bash
# Disable table of contents
readme-summarizer postprocess input.md --no-toc -o output.html

# Disable copy buttons
readme-summarizer postprocess input.md --no-copy-buttons -o output.html

# Disable dark mode toggle
readme-summarizer postprocess input.md --no-dark-mode -o output.html

# Add metadata
readme-summarizer postprocess input.md --title "My Project" --author "John Doe" -o output.html

# Specify source information
readme-summarizer postprocess input.md --source "github.com/user/repo" -o output.html
```

### Syntax Highlighting Styles

```bash
# GitHub style (default)
readme-summarizer postprocess code.md --syntax github -o output.html

# Monokai style
readme-summarizer postprocess code.md --syntax monokai -o output.html

# Dracula style
readme-summarizer postprocess code.md --syntax dracula -o output.html

# VS Code style
readme-summarizer postprocess code.md --syntax vs -o output.html
```

## Python API

### Basic Usage

```python
from summarize_readme.post_processor import (
    create_post_processor,
    Theme,
    ExportFormat,
    SyntaxStyle,
)

# Create processor with options
processor = create_post_processor(
    theme=Theme.GITHUB,
    syntax_style=SyntaxStyle.GITHUB,
)

# Process content
result = processor.process(
    content="# My README\n\nContent here...",
    export_format=ExportFormat.HTML_STANDALONE,
    metadata={"title": "My Project", "author": "John Doe"},
    source_info="github.com/user/repo",
)

# Save to file
with open("output.html", "w", encoding="utf-8") as f:
    f.write(result)
```

### Quick Processing

For simple use cases, use the convenience function:

```python
from summarize_readme.post_processor import quick_process, Theme, ExportFormat

# One-liner processing
result = quick_process(
    content="# Hello World",
    format=ExportFormat.HTML_STANDALONE,
    theme=Theme.DRACULA,
)
```

### Advanced Configuration

```python
from summarize_readme.post_processor import (
    AdvancedPostProcessor,
    PostProcessorOptions,
    Theme,
    SyntaxStyle,
)

# Configure all options
options = PostProcessorOptions(
    theme=Theme.MATERIAL,
    syntax_style=SyntaxStyle.MONOKAI,
    add_syntax_highlighting=True,
    add_table_of_contents=True,
    add_copy_buttons=True,
    add_line_numbers=False,
    minify_output=False,
    add_metadata_header=True,
    add_footer=True,
    responsive_design=True,
    dark_mode_toggle=True,
    add_analytics=True,
    emoji_rendering="native",
    custom_css="body { font-size: 16px; }",
    custom_js="console.log('Custom script');",
)

processor = AdvancedPostProcessor(options)
result = processor.process(content, ExportFormat.HTML_STANDALONE)
```

### Getting Statistics

```python
processor = create_post_processor()
result = processor.process(content, ExportFormat.HTML_STANDALONE)

# Get processing statistics
stats = processor.get_stats()
print(f"Input: {stats.input_length} chars")
print(f"Output: {stats.output_length} chars")
print(f"Code blocks: {stats.code_blocks_highlighted}")
print(f"Links: {stats.links_processed}")
print(f"Time: {stats.processing_time_ms:.2f}ms")
```

## Use Cases

### 1. Documentation Generation

Generate beautiful, styled documentation from README files:

```bash
readme-summarizer postprocess README.md \
  --theme material \
  --title "Project Documentation" \
  --author "Your Name" \
  -o docs/index.html
```

### 2. Social Media Promotion

Create optimized snippets for promoting your project:

```bash
readme-summarizer postprocess README.md \
  --format social-snippet \
  -o social.json

# Then use the generated snippets in your social media posts
```

### 3. PDF Documentation

Generate print-ready HTML for PDF conversion:

```bash
readme-summarizer postprocess docs.md \
  --format pdf-ready \
  --theme minimalist \
  -o printable.html

# Open in browser and use "Print to PDF"
```

### 4. Blog Post Conversion

Convert README to enhanced Markdown for blog platforms:

```bash
readme-summarizer postprocess README.md \
  --format markdown-enhanced \
  --title "Introducing My Project" \
  -o blog-post.md
```

### 5. Analytics and Insights

Extract detailed statistics and analysis:

```bash
readme-summarizer postprocess README.md \
  --format json-enriched \
  -o analytics.json

# Use the JSON for insights dashboards
```

## Theme Gallery

### GitHub Theme
Classic GitHub style with familiar colors and layout. Perfect for developers.

### Material Design
Clean, modern aesthetic following Google's Material Design principles.

### Dracula
Popular dark theme with vibrant purple, pink, and cyan accents.

### Nord
Arctic, north-bluish color palette. Calm and professional.

### Monokai
Classic dark theme for code, used in many editors.

### Minimalist
Distraction-free design focusing on content. Great for printing.

## Supported Languages

Syntax highlighting supports:

- **Python**
- **JavaScript**
- **TypeScript**
- **Bash/Shell**
- **HTML**
- **CSS**
- **JSON**
- **YAML**
- **Markdown**
- And more...

## Integration Examples

### With Summarization Pipeline

```bash
# Summarize then post-process
readme-summarizer summarize github/user/repo -o summary.md
readme-summarizer postprocess summary.md --theme dracula -o styled.html
```

### With Wrapper

```bash
# Use wrapper for enhanced summarization
readme-summarizer wrap README.md --template detailed -o summary.md

# Then apply post-processing
readme-summarizer postprocess summary.md --format html-standalone -o result.html
```

### With Normalization

```bash
# Normalize, summarize, and post-process
readme-summarizer normalize README.md -o clean.md
readme-summarizer summarize clean.md -o summary.md
readme-summarizer postprocess summary.md -o final.html
```

## Tips and Tricks

### 1. Dark Mode

HTML outputs support a dark mode toggle. Press the 'D' key to switch!

### 2. Copy Code Blocks

Hover over code blocks to reveal the copy button for easy copying.

### 3. Custom Styling

Add custom CSS for personalization:

```python
options = PostProcessorOptions(
    custom_css="""
    body { 
        font-family: 'Georgia', serif;
        max-width: 800px;
    }
    """
)
```

### 4. Responsive Design

All HTML outputs are mobile-friendly by default. Test on different screen sizes!

### 5. Print Optimization

For best PDF results:
1. Use `--format pdf-ready`
2. Use `--theme minimalist`
3. Print from browser with "Print to PDF"

## Troubleshooting

### Issue: Output file is too large

**Solution:** Use the `minify_output` option:

```python
options = PostProcessorOptions(minify_output=True)
```

### Issue: Code highlighting looks wrong

**Solution:** Specify the correct syntax style:

```bash
readme-summarizer postprocess input.md --syntax github
```

### Issue: Theme doesn't apply

**Solution:** Make sure you're using `html-standalone` format for full theme support:

```bash
readme-summarizer postprocess input.md --format html-standalone
```

## Performance

The post-processor is designed for speed:

- Average processing time: **< 50ms** for typical READMEs
- Handles large documents (100KB+) efficiently
- No external API calls required
- All processing done locally

## Future Enhancements

Planned features:

- 🎨 More themes (Atom, Tomorrow Night, etc.)
- 🔍 Search functionality in HTML output
- 📊 Interactive charts and graphs
- 🌐 Multi-language support
- 🎬 Animation effects
- 📱 Progressive Web App (PWA) export
- 🔐 Password-protected documents

## Examples

See `samples/post_processor_demo.py` for comprehensive examples of all features.

Run the demo:

```bash
cd samples
python post_processor_demo.py
```

This will generate multiple example outputs demonstrating different themes and formats.

## API Reference

### Classes

#### `AdvancedPostProcessor`
Main processor class.

**Methods:**
- `process(content, export_format, metadata, source_info)` - Process content
- `get_stats()` - Get processing statistics

#### `PostProcessorOptions`
Configuration options dataclass.

**Attributes:**
- `theme: Theme` - Visual theme
- `syntax_style: SyntaxStyle` - Code highlighting style
- `add_table_of_contents: bool` - Include TOC
- `add_copy_buttons: bool` - Add copy buttons
- `dark_mode_toggle: bool` - Enable dark mode
- And more...

### Enums

#### `Theme`
- `GITHUB`, `MATERIAL`, `DRACULA`, `NORD`, `MONOKAI`, `MINIMALIST`

#### `ExportFormat`
- `HTML_STYLED`, `HTML_STANDALONE`, `MARKDOWN_ENHANCED`, `JSON_ENRICHED`, `SOCIAL_SNIPPET`, `PDF_READY`

#### `SyntaxStyle`
- `GITHUB`, `MONOKAI`, `DRACULA`, `TOMORROW`, `SOLARIZED`, `VS`

### Functions

#### `create_post_processor(theme, syntax_style, **kwargs)`
Convenience function to create a configured processor.

#### `quick_process(content, format, theme)`
One-liner processing with default options.

## Contributing

Have ideas for new themes or features? Contributions are welcome!

## License

MIT License - feel free to use in your projects!

---

**Generated by README Summarizer - Advanced Post-Processor**
