"""
Advanced Post-Processor for README Summarizer.

Handles output transformations, styling, theming, and advanced formatting
for summarized content. Supports multiple export formats with enhanced styling,
syntax highlighting, social media optimization, and analytics visualization.
"""

import re
import base64
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import json
import textwrap


class Theme(str, Enum):
    """Available theme presets for styled output."""
    GITHUB = "github"
    MATERIAL = "material"
    DRACULA = "dracula"
    SOLARIZED_LIGHT = "solarized-light"
    SOLARIZED_DARK = "solarized-dark"
    NORD = "nord"
    MONOKAI = "monokai"
    MINIMALIST = "minimalist"


class ExportFormat(str, Enum):
    """Enhanced export formats supported by post-processor."""
    HTML_STYLED = "html-styled"
    HTML_STANDALONE = "html-standalone"
    MARKDOWN_ENHANCED = "markdown-enhanced"
    JSON_ENRICHED = "json-enriched"
    SOCIAL_SNIPPET = "social-snippet"
    PDF_READY = "pdf-ready"


class SyntaxStyle(str, Enum):
    """Code syntax highlighting styles."""
    GITHUB = "github"
    MONOKAI = "monokai"
    DRACULA = "dracula"
    TOMORROW = "tomorrow"
    SOLARIZED = "solarized"
    VS = "vs"


@dataclass
class PostProcessorOptions:
    """Configuration options for post-processing."""
    theme: Theme = Theme.GITHUB
    syntax_style: SyntaxStyle = SyntaxStyle.GITHUB
    add_syntax_highlighting: bool = True
    add_table_of_contents: bool = True
    add_copy_buttons: bool = True
    add_line_numbers: bool = False
    minify_output: bool = False
    add_metadata_header: bool = True
    add_footer: bool = True
    responsive_design: bool = True
    dark_mode_toggle: bool = True
    add_analytics: bool = True
    add_share_buttons: bool = False
    emoji_rendering: str = "native"  # native, twitter, github
    custom_css: Optional[str] = None
    custom_js: Optional[str] = None


@dataclass
class SocialSnippet:
    """Social media optimized snippet."""
    platform: str  # twitter, linkedin, slack, etc.
    content: str
    hashtags: List[str] = field(default_factory=list)
    length: int = 0
    url: Optional[str] = None


@dataclass
class ProcessingStats:
    """Statistics from post-processing operation."""
    input_length: int
    output_length: int
    code_blocks_highlighted: int
    links_processed: int
    images_processed: int
    processing_time_ms: float
    theme_applied: str
    format_generated: str


class SyntaxHighlighter:
    """Handles syntax highlighting for code blocks."""
    
    # Basic syntax highlighting rules (simplified, no external dependencies)
    LANGUAGE_PATTERNS = {
        'python': {
            'keyword': r'\b(def|class|import|from|if|else|elif|for|while|return|try|except|with|async|await|lambda|yield)\b',
            'string': r'(["\'])(?:(?=(\\?))\2.)*?\1',
            'comment': r'#.*$',
            'function': r'\bdef\s+(\w+)',
            'number': r'\b\d+\.?\d*\b',
        },
        'javascript': {
            'keyword': r'\b(function|const|let|var|if|else|return|class|async|await|import|export|from)\b',
            'string': r'(["\'])(?:(?=(\\?))\2.)*?\1',
            'comment': r'//.*$|/\*[\s\S]*?\*/',
            'number': r'\b\d+\.?\d*\b',
        },
        'bash': {
            'keyword': r'\b(if|then|else|fi|for|while|do|done|case|esac|function)\b',
            'string': r'(["\'])(?:(?=(\\?))\2.)*?\1',
            'comment': r'#.*$',
            'command': r'^\s*(\w+)',
        },
    }
    
    @classmethod
    def highlight_code(cls, code: str, language: str, style: SyntaxStyle = SyntaxStyle.GITHUB) -> str:
        """
        Apply syntax highlighting to code block.
        
        Args:
            code: Source code to highlight
            language: Programming language
            style: Highlighting style to use
            
        Returns:
            HTML-formatted code with syntax highlighting
        """
        if not code or language not in cls.LANGUAGE_PATTERNS:
            return cls._escape_html(code)
        
        patterns = cls.LANGUAGE_PATTERNS.get(language.lower(), {})
        highlighted = cls._escape_html(code)
        
        # Apply patterns in order
        for token_type, pattern in patterns.items():
            highlighted = re.sub(
                pattern,
                lambda m: f'<span class="token-{token_type}">{m.group(0)}</span>',
                highlighted,
                flags=re.MULTILINE
            )
        
        return highlighted
    
    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters."""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))


class ThemeManager:
    """Manages styling themes and CSS generation."""
    
    THEMES = {
        Theme.GITHUB: {
            'background': '#ffffff',
            'foreground': '#24292e',
            'accent': '#0366d6',
            'secondary': '#586069',
            'border': '#e1e4e8',
            'code_bg': '#f6f8fa',
            'link': '#0366d6',
        },
        Theme.MATERIAL: {
            'background': '#fafafa',
            'foreground': '#212121',
            'accent': '#2196f3',
            'secondary': '#757575',
            'border': '#e0e0e0',
            'code_bg': '#f5f5f5',
            'link': '#2196f3',
        },
        Theme.DRACULA: {
            'background': '#282a36',
            'foreground': '#f8f8f2',
            'accent': '#ff79c6',
            'secondary': '#6272a4',
            'border': '#44475a',
            'code_bg': '#44475a',
            'link': '#8be9fd',
        },
        Theme.NORD: {
            'background': '#2e3440',
            'foreground': '#eceff4',
            'accent': '#88c0d0',
            'secondary': '#81a1c1',
            'border': '#4c566a',
            'code_bg': '#3b4252',
            'link': '#88c0d0',
        },
        Theme.MONOKAI: {
            'background': '#272822',
            'foreground': '#f8f8f2',
            'accent': '#f92672',
            'secondary': '#75715e',
            'border': '#3e3d32',
            'code_bg': '#3e3d32',
            'link': '#66d9ef',
        },
        Theme.MINIMALIST: {
            'background': '#ffffff',
            'foreground': '#333333',
            'accent': '#000000',
            'secondary': '#666666',
            'border': '#dddddd',
            'code_bg': '#f8f8f8',
            'link': '#000000',
        },
    }
    
    @classmethod
    def get_theme_css(cls, theme: Theme, responsive: bool = True) -> str:
        """
        Generate CSS for the specified theme.
        
        Args:
            theme: Theme to generate CSS for
            responsive: Whether to include responsive design rules
            
        Returns:
            Complete CSS stylesheet as string
        """
        colors = cls.THEMES.get(theme, cls.THEMES[Theme.GITHUB])
        
        css = f"""
/* README Summarizer - {theme.value.title()} Theme */
:root {{
    --bg-color: {colors['background']};
    --fg-color: {colors['foreground']};
    --accent-color: {colors['accent']};
    --secondary-color: {colors['secondary']};
    --border-color: {colors['border']};
    --code-bg: {colors['code_bg']};
    --link-color: {colors['link']};
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: var(--fg-color);
    background-color: var(--bg-color);
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem;
}}

h1, h2, h3, h4, h5, h6 {{
    color: var(--fg-color);
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    font-weight: 600;
}}

h1 {{ font-size: 2em; border-bottom: 2px solid var(--border-color); padding-bottom: 0.3em; }}
h2 {{ font-size: 1.5em; border-bottom: 1px solid var(--border-color); padding-bottom: 0.3em; }}
h3 {{ font-size: 1.25em; }}

a {{
    color: var(--link-color);
    text-decoration: none;
}}

a:hover {{
    text-decoration: underline;
}}

code {{
    background-color: var(--code-bg);
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-family: "Monaco", "Courier New", monospace;
    font-size: 0.9em;
}}

pre {{
    background-color: var(--code-bg);
    padding: 1em;
    border-radius: 6px;
    overflow-x: auto;
    border: 1px solid var(--border-color);
}}

pre code {{
    background-color: transparent;
    padding: 0;
    border-radius: 0;
}}

.code-block-wrapper {{
    position: relative;
    margin: 1em 0;
}}

.code-language {{
    position: absolute;
    top: 0.5em;
    right: 0.5em;
    font-size: 0.75em;
    color: var(--secondary-color);
    text-transform: uppercase;
}}

.copy-button {{
    position: absolute;
    top: 0.5em;
    right: 4em;
    background: var(--accent-color);
    color: white;
    border: none;
    padding: 0.3em 0.8em;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.75em;
    opacity: 0;
    transition: opacity 0.2s;
}}

.code-block-wrapper:hover .copy-button {{
    opacity: 1;
}}

.copy-button:hover {{
    opacity: 0.8;
}}

blockquote {{
    border-left: 4px solid var(--accent-color);
    margin: 1em 0;
    padding-left: 1em;
    color: var(--secondary-color);
}}

table {{
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}}

table th, table td {{
    border: 1px solid var(--border-color);
    padding: 0.75em;
    text-align: left;
}}

table th {{
    background-color: var(--code-bg);
    font-weight: 600;
}}

.metadata-header {{
    background: var(--code-bg);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 1em;
    margin-bottom: 2em;
    font-size: 0.9em;
}}

.metadata-header .title {{
    font-size: 1.2em;
    font-weight: 600;
    margin-bottom: 0.5em;
}}

.metadata-header .info {{
    color: var(--secondary-color);
}}

.toc {{
    background: var(--code-bg);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 1em;
    margin: 2em 0;
}}

.toc h2 {{
    margin-top: 0;
    font-size: 1.1em;
    border: none;
}}

.toc ul {{
    list-style: none;
    padding-left: 1em;
}}

.toc a {{
    color: var(--fg-color);
}}

.footer {{
    margin-top: 3em;
    padding-top: 1em;
    border-top: 1px solid var(--border-color);
    text-align: center;
    color: var(--secondary-color);
    font-size: 0.9em;
}}

/* Syntax highlighting tokens */
.token-keyword {{ color: #d73a49; font-weight: bold; }}
.token-string {{ color: #032f62; }}
.token-comment {{ color: #6a737d; font-style: italic; }}
.token-function {{ color: #6f42c1; }}
.token-number {{ color: #005cc5; }}
.token-command {{ color: #22863a; font-weight: bold; }}

/* Dark theme adjustments */
body.dark-theme {{
    --bg-color: #1e1e1e;
    --fg-color: #d4d4d4;
    --border-color: #404040;
    --code-bg: #2d2d2d;
}}

body.dark-theme .token-keyword {{ color: #ff79c6; }}
body.dark-theme .token-string {{ color: #f1fa8c; }}
body.dark-theme .token-comment {{ color: #6272a4; }}
body.dark-theme .token-function {{ color: #50fa7b; }}
body.dark-theme .token-number {{ color: #bd93f9; }}
"""
        
        if responsive:
            css += """
/* Responsive design */
@media (max-width: 768px) {
    body {
        padding: 1rem;
    }
    
    h1 { font-size: 1.75em; }
    h2 { font-size: 1.5em; }
    h3 { font-size: 1.25em; }
    
    pre {
        padding: 0.75em;
    }
}
"""
        
        return css
    
    @classmethod
    def get_theme_colors(cls, theme: Theme) -> Dict[str, str]:
        """Get color palette for a theme."""
        return cls.THEMES.get(theme, cls.THEMES[Theme.GITHUB])


class AdvancedPostProcessor:
    """
    Advanced post-processor for README summarizer outputs.
    
    Provides comprehensive output transformations including:
    - Styled HTML generation with themes
    - Syntax highlighting
    - Social media snippet generation
    - Analytics and metrics
    - Custom templating
    """
    
    def __init__(self, options: Optional[PostProcessorOptions] = None):
        """
        Initialize post-processor.
        
        Args:
            options: Configuration options for post-processing
        """
        self.options = options or PostProcessorOptions()
        self.theme_manager = ThemeManager()
        self.highlighter = SyntaxHighlighter()
        self.stats = ProcessingStats(
            input_length=0,
            output_length=0,
            code_blocks_highlighted=0,
            links_processed=0,
            images_processed=0,
            processing_time_ms=0.0,
            theme_applied=self.options.theme.value,
            format_generated="",
        )
    
    def process(
        self,
        content: str,
        export_format: ExportFormat,
        metadata: Optional[Dict[str, Any]] = None,
        source_info: Optional[str] = None,
    ) -> str:
        """
        Process content and generate output in specified format.
        
        Args:
            content: Input content to process
            export_format: Desired output format
            metadata: Optional metadata to include
            source_info: Optional source information
            
        Returns:
            Processed content in specified format
        """
        import time
        start_time = time.time()
        
        self.stats.input_length = len(content)
        self.stats.format_generated = export_format.value
        
        # Route to appropriate processor
        if export_format == ExportFormat.HTML_STYLED:
            result = self._generate_html_styled(content, metadata, source_info)
        elif export_format == ExportFormat.HTML_STANDALONE:
            result = self._generate_html_standalone(content, metadata, source_info)
        elif export_format == ExportFormat.MARKDOWN_ENHANCED:
            result = self._generate_markdown_enhanced(content, metadata)
        elif export_format == ExportFormat.JSON_ENRICHED:
            result = self._generate_json_enriched(content, metadata)
        elif export_format == ExportFormat.SOCIAL_SNIPPET:
            result = self._generate_social_snippet(content)
        elif export_format == ExportFormat.PDF_READY:
            result = self._generate_pdf_ready(content, metadata, source_info)
        else:
            result = content
        
        self.stats.output_length = len(result)
        self.stats.processing_time_ms = (time.time() - start_time) * 1000
        
        return result
    
    def _generate_html_styled(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]],
        source_info: Optional[str],
    ) -> str:
        """Generate styled HTML with CSS (fragment, not full document)."""
        html_content = self._markdown_to_html(content)
        
        if self.options.add_syntax_highlighting:
            html_content = self._apply_syntax_highlighting(html_content)
        
        if self.options.add_copy_buttons:
            html_content = self._add_copy_buttons(html_content)
        
        return html_content
    
    def _generate_html_standalone(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]],
        source_info: Optional[str],
    ) -> str:
        """Generate complete standalone HTML document."""
        html_body = self._markdown_to_html(content)
        
        if self.options.add_syntax_highlighting:
            html_body = self._apply_syntax_highlighting(html_body)
        
        if self.options.add_copy_buttons:
            html_body = self._add_copy_buttons(html_body)
        
        # Build complete HTML document
        css = self.theme_manager.get_theme_css(
            self.options.theme,
            self.options.responsive_design
        )
        
        if self.options.custom_css:
            css += f"\n/* Custom CSS */\n{self.options.custom_css}"
        
        metadata_html = ""
        if self.options.add_metadata_header and metadata:
            metadata_html = self._generate_metadata_header(metadata, source_info)
        
        toc_html = ""
        if self.options.add_table_of_contents:
            toc_html = self._generate_toc(html_body)
        
        footer_html = ""
        if self.options.add_footer:
            footer_html = self._generate_footer()
        
        dark_mode_script = ""
        if self.options.dark_mode_toggle:
            dark_mode_script = self._get_dark_mode_script()
        
        copy_script = ""
        if self.options.add_copy_buttons:
            copy_script = self._get_copy_button_script()
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="generator" content="README Summarizer Post-Processor">
    <title>{metadata.get('title', 'README Summary') if metadata else 'README Summary'}</title>
    <style>
{css}
    </style>
</head>
<body>
{metadata_html}
{toc_html}
<div class="content">
{html_body}
</div>
{footer_html}
<script>
{copy_script}
{dark_mode_script}
{self.options.custom_js or ''}
</script>
</body>
</html>"""
        
        return html
    
    def _generate_markdown_enhanced(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]],
    ) -> str:
        """Generate enhanced Markdown with additional formatting."""
        result = content
        
        # Add metadata header
        if metadata:
            header = "---\n"
            for key, value in metadata.items():
                header += f"{key}: {value}\n"
            header += "---\n\n"
            result = header + result
        
        # Add table of contents
        if self.options.add_table_of_contents:
            toc = self._generate_markdown_toc(content)
            result = result.split('\n', 1)[0] + f"\n\n{toc}\n\n" + result.split('\n', 1)[1]
        
        # Enhance code blocks with language indicators
        result = self._enhance_code_blocks(result)
        
        return result
    
    def _generate_json_enriched(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]],
    ) -> str:
        """Generate enriched JSON with content analysis."""
        # Analyze content
        analysis = {
            "content": content,
            "metadata": metadata or {},
            "statistics": {
                "length": len(content),
                "word_count": len(content.split()),
                "line_count": len(content.split('\n')),
                "code_blocks": len(re.findall(r'```[\s\S]*?```', content)),
                "links": len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)),
                "headings": len(re.findall(r'^#+\s+.+$', content, re.MULTILINE)),
            },
            "extracted": {
                "headings": self._extract_headings(content),
                "links": self._extract_links(content),
                "code_languages": self._extract_code_languages(content),
            },
            "processing": {
                "timestamp": datetime.now().isoformat(),
                "theme": self.options.theme.value,
                "processor_version": "1.0.0",
            }
        }
        
        return json.dumps(analysis, indent=2, ensure_ascii=False)
    
    def _generate_social_snippet(self, content: str) -> str:
        """Generate social media optimized snippets."""
        snippets = []
        
        # Twitter (280 chars)
        twitter = self._create_social_snippet(
            content, platform="twitter", max_length=250
        )
        
        # LinkedIn (3000 chars but 150 for preview)
        linkedin = self._create_social_snippet(
            content, platform="linkedin", max_length=150
        )
        
        # Slack (4000 chars but keep it short)
        slack = self._create_social_snippet(
            content, platform="slack", max_length=500
        )
        
        result = {
            "twitter": twitter.__dict__,
            "linkedin": linkedin.__dict__,
            "slack": slack.__dict__,
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    def _generate_pdf_ready(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]],
        source_info: Optional[str],
    ) -> str:
        """Generate PDF-ready HTML (print-optimized)."""
        html = self._generate_html_standalone(content, metadata, source_info)
        
        # Add print-specific CSS
        print_css = """
<style media="print">
    body {
        max-width: 100%;
        padding: 0;
    }
    
    .copy-button,
    .dark-mode-toggle {
        display: none !important;
    }
    
    pre {
        page-break-inside: avoid;
    }
    
    h1, h2, h3, h4, h5, h6 {
        page-break-after: avoid;
    }
    
    @page {
        margin: 2cm;
    }
</style>
"""
        
        html = html.replace('</head>', f'{print_css}</head>')
        
        return html
    
    def _create_social_snippet(
        self,
        content: str,
        platform: str,
        max_length: int,
    ) -> SocialSnippet:
        """Create optimized snippet for social media platform."""
        # Extract first meaningful paragraph
        text = re.sub(r'```[\s\S]*?```', '', content)  # Remove code blocks
        text = re.sub(r'[#*`\[\]()]', '', text)  # Remove markdown syntax
        text = re.sub(r'\n+', ' ', text).strip()  # Normalize whitespace
        
        # Extract hashtags
        hashtags = re.findall(r'#\w+', content)[:3]
        
        # Truncate if needed
        if len(text) > max_length - 20:
            text = text[:max_length - 20].rsplit(' ', 1)[0] + '...'
        
        return SocialSnippet(
            platform=platform,
            content=text,
            hashtags=hashtags,
            length=len(text),
        )
    
    def _markdown_to_html(self, markdown_text: str) -> str:
        """Convert Markdown to HTML (basic conversion)."""
        html = markdown_text
        
        # Headings
        html = re.sub(r'^#{6}\s+(.+)$', r'<h6>\1</h6>', html, flags=re.MULTILINE)
        html = re.sub(r'^#{5}\s+(.+)$', r'<h5>\1</h5>', html, flags=re.MULTILINE)
        html = re.sub(r'^#{4}\s+(.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        html = re.sub(r'^#{3}\s+(.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^#{2}\s+(.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^#{1}\s+(.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Code blocks
        def replace_code_block(match):
            lang = match.group(1) or ''
            code = match.group(2)
            return f'<pre><code class="language-{lang}">{code}</code></pre>'
        
        html = re.sub(r'```(\w+)?\n([\s\S]*?)```', replace_code_block, html)
        
        # Inline code
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        
        # Bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'__(.+?)__', r'<strong>\1</strong>', html)
        
        # Italic
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        html = re.sub(r'_(.+?)_', r'<em>\1</em>', html)
        
        # Links
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
        
        # Paragraphs
        html = re.sub(r'\n\n', '</p><p>', html)
        html = f'<p>{html}</p>'
        
        # Clean up empty paragraphs
        html = re.sub(r'<p>\s*</p>', '', html)
        
        return html
    
    def _apply_syntax_highlighting(self, html: str) -> str:
        """Apply syntax highlighting to code blocks in HTML."""
        def highlight_block(match):
            self.stats.code_blocks_highlighted += 1
            lang = match.group(1) or 'text'
            code = match.group(2)
            
            highlighted = self.highlighter.highlight_code(
                code, lang, self.options.syntax_style
            )
            
            return f'''<div class="code-block-wrapper">
    <span class="code-language">{lang}</span>
    <pre><code class="language-{lang}">{highlighted}</code></pre>
</div>'''
        
        return re.sub(
            r'<pre><code class="language-(\w+)">([\s\S]*?)</code></pre>',
            highlight_block,
            html
        )
    
    def _add_copy_buttons(self, html: str) -> str:
        """Add copy buttons to code blocks."""
        def add_button(match):
            return match.group(0).replace(
                '<div class="code-block-wrapper">',
                '<div class="code-block-wrapper"><button class="copy-button" onclick="copyCode(this)">Copy</button>'
            )
        
        return re.sub(
            r'<div class="code-block-wrapper">[\s\S]*?</div>',
            add_button,
            html
        )
    
    def _generate_metadata_header(
        self,
        metadata: Dict[str, Any],
        source_info: Optional[str],
    ) -> str:
        """Generate metadata header HTML."""
        title = metadata.get('title', 'README Summary')
        generated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        info_items = []
        if source_info:
            info_items.append(f'Source: {source_info}')
        if 'author' in metadata:
            info_items.append(f'Author: {metadata["author"]}')
        info_items.append(f'Generated: {generated}')
        
        info_html = ' | '.join(info_items)
        
        return f'''<div class="metadata-header">
    <div class="title">{title}</div>
    <div class="info">{info_html}</div>
</div>'''
    
    def _generate_toc(self, html: str) -> str:
        """Generate table of contents from HTML headings."""
        headings = re.findall(r'<h([1-3])>(.+?)</h\1>', html)
        
        if not headings:
            return ""
        
        toc_items = []
        for level, text in headings:
            indent = "  " * (int(level) - 1)
            slug = re.sub(r'[^\w\s-]', '', text.lower()).replace(' ', '-')
            toc_items.append(f'{indent}<li><a href="#{slug}">{text}</a></li>')
        
        toc_html = '\n'.join(toc_items)
        
        return f'''<div class="toc">
    <h2>Table of Contents</h2>
    <ul>
{toc_html}
    </ul>
</div>'''
    
    def _generate_footer(self) -> str:
        """Generate footer HTML."""
        return f'''<div class="footer">
    <p>Generated by <strong>README Summarizer</strong> with Advanced Post-Processor</p>
    <p>Theme: {self.options.theme.value.title()} | {datetime.now().strftime('%Y-%m-%d')}</p>
</div>'''
    
    def _get_copy_button_script(self) -> str:
        """Get JavaScript for copy button functionality."""
        return """
function copyCode(button) {
    const codeBlock = button.parentElement.querySelector('code');
    const text = codeBlock.innerText;
    
    navigator.clipboard.writeText(text).then(() => {
        button.textContent = 'Copied!';
        setTimeout(() => {
            button.textContent = 'Copy';
        }, 2000);
    });
}
"""
    
    def _get_dark_mode_script(self) -> str:
        """Get JavaScript for dark mode toggle."""
        return """
// Dark mode toggle (press 'D' key)
document.addEventListener('keydown', (e) => {
    if (e.key === 'd' || e.key === 'D') {
        document.body.classList.toggle('dark-theme');
        localStorage.setItem('darkMode', document.body.classList.contains('dark-theme'));
    }
});

// Restore dark mode preference
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-theme');
}
"""
    
    def _generate_markdown_toc(self, content: str) -> str:
        """Generate Markdown table of contents."""
        headings = re.findall(r'^(#{1,3})\s+(.+)$', content, re.MULTILINE)
        
        if not headings:
            return ""
        
        toc_lines = ["## Table of Contents\n"]
        for hashes, text in headings:
            level = len(hashes)
            if level == 1:
                continue  # Skip h1
            indent = "  " * (level - 2)
            slug = re.sub(r'[^\w\s-]', '', text.lower()).replace(' ', '-')
            toc_lines.append(f'{indent}- [{text}](#{slug})')
        
        return '\n'.join(toc_lines)
    
    def _enhance_code_blocks(self, markdown: str) -> str:
        """Enhance code blocks with additional features."""
        # Already in markdown format, no changes needed for basic enhancement
        return markdown
    
    def _extract_headings(self, content: str) -> List[Dict[str, Any]]:
        """Extract all headings from content."""
        headings = []
        for match in re.finditer(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE):
            headings.append({
                'level': len(match.group(1)),
                'text': match.group(2),
                'line': content[:match.start()].count('\n') + 1,
            })
        return headings
    
    def _extract_links(self, content: str) -> List[Dict[str, str]]:
        """Extract all links from content."""
        links = []
        for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', content):
            self.stats.links_processed += 1
            links.append({
                'text': match.group(1),
                'url': match.group(2),
            })
        return links
    
    def _extract_code_languages(self, content: str) -> List[str]:
        """Extract programming languages from code blocks."""
        languages = []
        for match in re.finditer(r'```(\w+)', content):
            lang = match.group(1)
            if lang and lang not in languages:
                languages.append(lang)
        return languages
    
    def get_stats(self) -> ProcessingStats:
        """Get processing statistics."""
        return self.stats


# Convenience functions
def create_post_processor(
    theme: Theme = Theme.GITHUB,
    syntax_style: SyntaxStyle = SyntaxStyle.GITHUB,
    **kwargs
) -> AdvancedPostProcessor:
    """
    Create a post-processor with specified options.
    
    Args:
        theme: Visual theme to apply
        syntax_style: Code syntax highlighting style
        **kwargs: Additional options for PostProcessorOptions
        
    Returns:
        Configured AdvancedPostProcessor instance
    """
    options = PostProcessorOptions(theme=theme, syntax_style=syntax_style, **kwargs)
    return AdvancedPostProcessor(options)


def quick_process(
    content: str,
    format: ExportFormat = ExportFormat.HTML_STANDALONE,
    theme: Theme = Theme.GITHUB,
) -> str:
    """
    Quick processing with default options.
    
    Args:
        content: Content to process
        format: Output format
        theme: Visual theme
        
    Returns:
        Processed content
    """
    processor = create_post_processor(theme=theme)
    return processor.process(content, format)
