"""
Demo: Advanced Post-Processor for README Summarizer

This demo showcases the advanced post-processing features including:
- Multiple visual themes
- Syntax highlighting
- Social media snippet generation
- Enhanced HTML output with interactive features
"""

from pathlib import Path
from summarize_readme.post_processor import (
    AdvancedPostProcessor,
    PostProcessorOptions,
    Theme,
    ExportFormat,
    SyntaxStyle,
    create_post_processor,
    quick_process,
)


def demo_basic_html():
    """Demo 1: Basic HTML generation with GitHub theme."""
    print("=" * 60)
    print("Demo 1: Basic Styled HTML (GitHub Theme)")
    print("=" * 60)
    
    sample_content = """# My Awesome Project

A powerful tool for developers.

## Features

- Fast and efficient
- Easy to use
- Well documented

## Installation

```bash
pip install awesome-project
```

## Usage

```python
from awesome_project import AwesomeClass

# Create instance
app = AwesomeClass()
app.run()
```

## Links

Check out the [documentation](https://example.com/docs) for more info.
"""
    
    processor = create_post_processor(theme=Theme.GITHUB)
    result = processor.process(
        sample_content,
        ExportFormat.HTML_STANDALONE,
        metadata={"title": "My Awesome Project", "author": "Demo User"},
        source_info="demo_basic_html",
    )
    
    output_file = Path("demo_output_github.html")
    output_file.write_text(result, encoding='utf-8')
    print(f"✓ Generated: {output_file}")
    print(f"  Open in browser to view styled output with GitHub theme")
    print()


def demo_dracula_theme():
    """Demo 2: Dark theme with Dracula color scheme."""
    print("=" * 60)
    print("Demo 2: Dark Theme (Dracula)")
    print("=" * 60)
    
    sample_content = """# Dark Theme Demo

This showcases the Dracula color scheme.

## Code Example

```javascript
function greet(name) {
    console.log(`Hello, ${name}!`);
    return true;
}

// Call the function
greet("World");
```

Perfect for late-night coding sessions! 🌙
"""
    
    processor = create_post_processor(
        theme=Theme.DRACULA,
        syntax_style=SyntaxStyle.DRACULA,
        add_copy_buttons=True,
        dark_mode_toggle=True,
    )
    
    result = processor.process(
        sample_content,
        ExportFormat.HTML_STANDALONE,
        metadata={"title": "Dark Theme Demo"},
    )
    
    output_file = Path("demo_output_dracula.html")
    output_file.write_text(result, encoding='utf-8')
    print(f"✓ Generated: {output_file}")
    print(f"  Features: Copy buttons, Dark mode toggle (press 'D')")
    print()


def demo_material_theme():
    """Demo 3: Material Design theme."""
    print("=" * 60)
    print("Demo 3: Material Design Theme")
    print("=" * 60)
    
    sample_content = """# Material Design Example

Clean and modern aesthetic following Material Design principles.

## Table Support

| Feature | Status | Notes |
|---------|--------|-------|
| Themes | ✓ | Multiple options |
| Syntax | ✓ | Code highlighting |
| Export | ✓ | Various formats |

## Blockquote

> Material Design is a design language developed by Google.
> It's known for its clean, modern aesthetic.

## Lists

1. First item
2. Second item
3. Third item
"""
    
    processor = create_post_processor(theme=Theme.MATERIAL)
    result = processor.process(
        sample_content,
        ExportFormat.HTML_STANDALONE,
    )
    
    output_file = Path("demo_output_material.html")
    output_file.write_text(result, encoding='utf-8')
    print(f"✓ Generated: {output_file}")
    print(f"  Clean Material Design aesthetic")
    print()


def demo_social_snippets():
    """Demo 4: Social media snippet generation."""
    print("=" * 60)
    print("Demo 4: Social Media Snippets")
    print("=" * 60)
    
    sample_content = """# README Summarizer - Advanced Post-Processor

A powerful Python CLI tool for summarizing and transforming README files with advanced post-processing capabilities.

## Key Features

🎨 Multiple visual themes including GitHub, Material Design, Dracula, and more
✨ Syntax highlighting for code blocks
📱 Social media optimized snippets
🚀 Fast and efficient processing
📊 Analytics and metrics tracking

Perfect for developers who want beautiful, styled documentation! #Python #CLI #Documentation #OpenSource

Check it out at: https://github.com/yourusername/readme-summarizer
"""
    
    processor = create_post_processor()
    result = processor.process(sample_content, ExportFormat.SOCIAL_SNIPPET)
    
    import json
    snippets = json.loads(result)
    
    print("Generated social media snippets:")
    print()
    
    print("Twitter:")
    print(f"  {snippets['twitter']['content']}")
    print(f"  Length: {snippets['twitter']['length']} chars")
    print()
    
    print("LinkedIn:")
    print(f"  {snippets['linkedin']['content']}")
    print(f"  Length: {snippets['linkedin']['length']} chars")
    print()
    
    output_file = Path("demo_social_snippets.json")
    output_file.write_text(result, encoding='utf-8')
    print(f"✓ Full snippets saved to: {output_file}")
    print()


def demo_json_enriched():
    """Demo 5: Enriched JSON with analytics."""
    print("=" * 60)
    print("Demo 5: JSON with Analytics")
    print("=" * 60)
    
    sample_content = """# Analytics Demo

## Section 1

Content with [links](https://example.com) and more.

## Section 2

```python
def hello():
    print("Hello")
```

```javascript
console.log("World");
```

Multiple code blocks in different languages.
"""
    
    processor = create_post_processor()
    result = processor.process(sample_content, ExportFormat.JSON_ENRICHED)
    
    import json
    data = json.loads(result)
    
    print("Content Analysis:")
    print(f"  Word count: {data['statistics']['word_count']}")
    print(f"  Code blocks: {data['statistics']['code_blocks']}")
    print(f"  Headings: {data['statistics']['headings']}")
    print(f"  Links: {data['statistics']['links']}")
    print(f"  Languages detected: {', '.join(data['extracted']['code_languages'])}")
    
    output_file = Path("demo_analytics.json")
    output_file.write_text(result, encoding='utf-8')
    print(f"\n✓ Full analytics saved to: {output_file}")
    print()


def demo_enhanced_markdown():
    """Demo 6: Enhanced Markdown with metadata."""
    print("=" * 60)
    print("Demo 6: Enhanced Markdown")
    print("=" * 60)
    
    sample_content = """# Enhanced Markdown Demo

## Introduction

This demonstrates enhanced Markdown output.

## Features

- Metadata headers
- Table of contents
- Enhanced formatting
"""
    
    processor = create_post_processor()
    result = processor.process(
        sample_content,
        ExportFormat.MARKDOWN_ENHANCED,
        metadata={
            "title": "Enhanced Markdown Demo",
            "author": "Demo User",
            "date": "2024-03-10",
            "version": "1.0.0",
        }
    )
    
    output_file = Path("demo_enhanced.md")
    output_file.write_text(result, encoding='utf-8')
    print(f"✓ Generated: {output_file}")
    print(f"  Includes YAML frontmatter with metadata")
    print()


def demo_pdf_ready():
    """Demo 7: PDF-ready HTML."""
    print("=" * 60)
    print("Demo 7: PDF-Ready HTML")
    print("=" * 60)
    
    sample_content = """# PDF Export Demo

This HTML is optimized for PDF conversion with print-friendly styling.

## Professional Documentation

Perfect for creating polished, professional documentation that can be
easily converted to PDF format.

## Code Examples

```python
def generate_pdf():
    '''Generate PDF from README'''
    return "PDF ready!"
```

## Notes

- Print-optimized CSS
- No interactive elements in print
- Clean page breaks
"""
    
    processor = create_post_processor(theme=Theme.MINIMALIST)
    result = processor.process(
        sample_content,
        ExportFormat.PDF_READY,
        metadata={"title": "PDF Export Demo"},
    )
    
    output_file = Path("demo_pdf_ready.html")
    output_file.write_text(result, encoding='utf-8')
    print(f"✓ Generated: {output_file}")
    print(f"  Open in browser and use Print to PDF")
    print(f"  Optimized for professional documentation")
    print()


def demo_quick_process():
    """Demo 8: Quick processing with default settings."""
    print("=" * 60)
    print("Demo 8: Quick Process Function")
    print("=" * 60)
    
    sample_content = """# Quick Demo

Using the `quick_process()` convenience function for rapid styling.

## Easy API

```python
from summarize_readme.post_processor import quick_process

result = quick_process(content, format="html-standalone")
```

No configuration needed - just process!
"""
    
    result = quick_process(
        sample_content,
        ExportFormat.HTML_STANDALONE,
        Theme.NORD,
    )
    
    output_file = Path("demo_quick.html")
    output_file.write_text(result, encoding='utf-8')
    print(f"✓ Generated: {output_file}")
    print(f"  One-liner processing with Nord theme")
    print()


def demo_stats():
    """Demo 9: Processing statistics."""
    print("=" * 60)
    print("Demo 9: Processing Statistics")
    print("=" * 60)
    
    sample_content = """# Stats Demo

Content with multiple [links](https://a.com), [more links](https://b.com).

```python
print("Code block 1")
```

```javascript
console.log("Code block 2");
```

```bash
echo "Code block 3"
```
"""
    
    processor = create_post_processor()
    result = processor.process(sample_content, ExportFormat.HTML_STANDALONE)
    
    stats = processor.get_stats()
    
    print("Processing Statistics:")
    print(f"  Input length: {stats.input_length:,} characters")
    print(f"  Output length: {stats.output_length:,} characters")
    print(f"  Code blocks highlighted: {stats.code_blocks_highlighted}")
    print(f"  Links processed: {stats.links_processed}")
    print(f"  Processing time: {stats.processing_time_ms:.2f}ms")
    print(f"  Theme applied: {stats.theme_applied}")
    print(f"  Format: {stats.format_generated}")
    print()


def run_all_demos():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("README Summarizer - Advanced Post-Processor Demo")
    print("=" * 60)
    print()
    
    demos = [
        demo_basic_html,
        demo_dracula_theme,
        demo_material_theme,
        demo_social_snippets,
        demo_json_enriched,
        demo_enhanced_markdown,
        demo_pdf_ready,
        demo_quick_process,
        demo_stats,
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"Error in {demo.__name__}: {e}")
            print()
    
    print("=" * 60)
    print("All demos completed!")
    print("=" * 60)
    print()
    print("Generated files:")
    for file in Path(".").glob("demo_*"):
        print(f"  - {file}")
    print()
    print("Open the HTML files in your browser to see the results!")


if __name__ == "__main__":
    run_all_demos()
