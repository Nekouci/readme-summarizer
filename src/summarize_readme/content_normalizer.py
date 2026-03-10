"""
Advanced Content Normalizer / Preprocessor for README files.

This module provides comprehensive content cleaning, normalization, and preprocessing
capabilities to improve README parsing accuracy and consistency.
"""

import re
import unicodedata
from enum import Enum
from typing import Dict, List, Optional, Tuple
from html import unescape
from bs4 import BeautifulSoup


class NormalizationLevel(str, Enum):
    """Normalization intensity levels."""
    MINIMAL = "minimal"      # Basic whitespace and encoding fixes
    STANDARD = "standard"    # Recommended default preprocessing
    AGGRESSIVE = "aggressive"  # Maximum cleaning and standardization


class EmojiHandling(str, Enum):
    """How to handle emojis in content."""
    KEEP = "keep"           # Keep emojis as-is
    REMOVE = "remove"       # Remove all emojis
    CONVERT = "convert"     # Convert to text descriptions


class ContentNormalizer:
    """
    Advanced content normalizer with multiple preprocessing strategies.
    
    Features:
    - Unicode normalization and encoding fixes
    - HTML/XML tag removal
    - Whitespace normalization
    - Markdown syntax standardization
    - Emoji handling (keep/remove/convert)
    - Code block preservation
    - Link and badge cleanup
    - Comment removal
    - Special character handling
    """
    
    def __init__(
        self,
        level: NormalizationLevel = NormalizationLevel.STANDARD,
        emoji_handling: EmojiHandling = EmojiHandling.KEEP,
        remove_html: bool = True,
        remove_comments: bool = True,
        normalize_whitespace: bool = True,
        normalize_headers: bool = True,
        preserve_code_blocks: bool = True,
        fix_unicode: bool = True,
        remove_excessive_newlines: bool = True,
        standardize_links: bool = True,
    ):
        """
        Initialize the content normalizer.
        
        Args:
            level: Overall normalization intensity
            emoji_handling: How to handle emojis
            remove_html: Remove HTML tags
            remove_comments: Remove HTML/markdown comments
            normalize_whitespace: Normalize spaces, tabs, etc.
            normalize_headers: Standardize header formatting
            preserve_code_blocks: Protect code blocks during normalization
            fix_unicode: Fix unicode encoding issues
            remove_excessive_newlines: Remove more than 2 consecutive newlines
            standardize_links: Normalize link formatting
        """
        self.level = level
        self.emoji_handling = emoji_handling
        self.remove_html = remove_html
        self.remove_comments = remove_comments
        self.normalize_whitespace = normalize_whitespace
        self.normalize_headers = normalize_headers
        self.preserve_code_blocks = preserve_code_blocks
        self.fix_unicode = fix_unicode
        self.remove_excessive_newlines = remove_excessive_newlines
        self.standardize_links = standardize_links
        
        # Apply level-based defaults
        self._apply_level_defaults()
        
        # Stats tracking
        self.stats: Dict[str, int] = {}
    
    def _apply_level_defaults(self):
        """Apply default settings based on normalization level."""
        if self.level == NormalizationLevel.MINIMAL:
            self.remove_html = False
            self.normalize_headers = False
            self.standardize_links = False
        elif self.level == NormalizationLevel.AGGRESSIVE:
            self.remove_html = True
            self.remove_comments = True
            self.normalize_whitespace = True
            self.normalize_headers = True
            self.remove_excessive_newlines = True
            self.standardize_links = True
    
    def normalize(self, content: str) -> str:
        """
        Normalize README content with configured preprocessing steps.
        
        Args:
            content: Raw README content
        
        Returns:
            Normalized content
        """
        # Reset stats
        self.stats = {
            "original_size": len(content),
            "original_lines": content.count('\n') + 1,
            "html_tags_removed": 0,
            "comments_removed": 0,
            "emojis_processed": 0,
            "whitespace_normalized": 0,
            "headers_normalized": 0,
            "links_normalized": 0,
        }
        
        if not content or not content.strip():
            return content
        
        # Step 1: Preserve code blocks if needed
        code_blocks = []
        if self.preserve_code_blocks:
            content, code_blocks = self._extract_code_blocks(content)
        
        # Step 2: Fix unicode and encoding issues
        if self.fix_unicode:
            content = self._fix_unicode(content)
        
        # Step 3: Remove HTML comments and tags
        if self.remove_comments:
            content = self._remove_comments(content)
        
        if self.remove_html:
            content = self._remove_html_tags(content)
        
        # Step 4: Handle emojis
        if self.emoji_handling != EmojiHandling.KEEP:
            content = self._handle_emojis(content)
        
        # Step 5: Normalize markdown syntax
        if self.normalize_headers:
            content = self._normalize_headers(content)
        
        if self.standardize_links:
            content = self._standardize_links(content)
        
        # Step 6: Normalize whitespace
        if self.normalize_whitespace:
            content = self._normalize_whitespace(content)
        
        if self.remove_excessive_newlines:
            content = self._remove_excessive_newlines(content)
        
        # Step 7: Restore code blocks
        if self.preserve_code_blocks and code_blocks:
            content = self._restore_code_blocks(content, code_blocks)
        
        # Step 8: Final cleanup
        content = self._final_cleanup(content)
        
        # Update stats
        self.stats["final_size"] = len(content)
        self.stats["final_lines"] = content.count('\n') + 1
        self.stats["size_reduction"] = self.stats["original_size"] - self.stats["final_size"]
        
        return content
    
    def get_stats(self) -> Dict[str, int]:
        """Get normalization statistics from last run."""
        return self.stats.copy()
    
    def _extract_code_blocks(self, content: str) -> Tuple[str, List[str]]:
        """Extract code blocks for protection during normalization."""
        code_blocks = []
        placeholder_pattern = "__CODEBLOCK_PLACEHOLDER_{}__"
        
        # Match both ``` and indented code blocks
        def replacer(match):
            code_blocks.append(match.group(0))
            return placeholder_pattern.format(len(code_blocks) - 1)
        
        # Fenced code blocks
        content = re.sub(
            r'```[\s\S]*?```',
            replacer,
            content,
            flags=re.MULTILINE
        )
        
        # Inline code
        content = re.sub(
            r'`[^`\n]+`',
            replacer,
            content
        )
        
        return content, code_blocks
    
    def _restore_code_blocks(self, content: str, code_blocks: List[str]) -> str:
        """Restore protected code blocks."""
        for i, block in enumerate(code_blocks):
            placeholder = f"__CODEBLOCK_PLACEHOLDER_{i}__"
            content = content.replace(placeholder, block)
        return content
    
    def _fix_unicode(self, content: str) -> str:
        """Fix unicode normalization and encoding issues."""
        # Normalize unicode to NFC (canonical composition)
        content = unicodedata.normalize('NFC', content)
        
        # Fix common encoding issues
        replacements = {
            '\u00a0': ' ',  # Non-breaking space to regular space
            '\u2028': '\n',  # Line separator to newline
            '\u2029': '\n\n',  # Paragraph separator to double newline
            '\ufeff': '',  # Zero-width no-break space (BOM)
            '\u200b': '',  # Zero-width space
            '\u200c': '',  # Zero-width non-joiner
            '\u200d': '',  # Zero-width joiner
            '\xa0': ' ',  # Another non-breaking space
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Fix smart quotes and dashes
        content = content.replace('\u2018', "'").replace('\u2019', "'")  # Smart single quotes
        content = content.replace('\u201c', '"').replace('\u201d', '"')  # Smart double quotes
        content = content.replace('\u2013', '-').replace('\u2014', '--')  # En/em dashes
        content = content.replace('\u2026', '...')  # Ellipsis
        
        # HTML entity decoding
        content = unescape(content)
        
        return content
    
    def _remove_comments(self, content: str) -> str:
        """Remove HTML and markdown comments."""
        original_len = len(content)
        
        # Remove HTML comments
        content = re.sub(r'<!--[\s\S]*?-->', '', content)
        
        # Remove markdown link reference definitions that are essentially comments
        # (keep actual reference definitions that are used)
        
        self.stats["comments_removed"] = (original_len - len(content)) // 20  # Rough estimate
        return content
    
    def _remove_html_tags(self, content: str) -> str:
        """Remove HTML tags while preserving content."""
        original_len = len(content)
        
        # Use BeautifulSoup for robust HTML removal
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove script and style tags completely
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Fallback: regex for any remaining tags
        text = re.sub(r'<[^>]+>', '', text)
        
        self.stats["html_tags_removed"] = content.count('<') - text.count('<')
        return text
    
    def _handle_emojis(self, content: str) -> str:
        """Handle emojis based on configuration."""
        # Emoji regex pattern (simplified - covers most common emojis)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"
            "]+"
        )
        
        emojis_found = len(emoji_pattern.findall(content))
        self.stats["emojis_processed"] = emojis_found
        
        if self.emoji_handling == EmojiHandling.REMOVE:
            content = emoji_pattern.sub('', content)
        elif self.emoji_handling == EmojiHandling.CONVERT:
            # Convert to text descriptions (basic conversion)
            emoji_map = {
                '🚀': '[rocket]',
                '✨': '[sparkles]',
                '📦': '[package]',
                '🔧': '[wrench]',
                '🎨': '[art]',
                '🐛': '[bug]',
                '📝': '[memo]',
                '🔥': '[fire]',
                '✅': '[check]',
                '❌': '[x]',
                '⚠️': '[warning]',
                '💡': '[bulb]',
                '📖': '[book]',
                '🌟': '[star]',
                '🎯': '[target]',
                '🔍': '[search]',
            }
            for emoji, text in emoji_map.items():
                content = content.replace(emoji, text)
            # Remove remaining emojis
            content = emoji_pattern.sub('', content)
        
        return content
    
    def _normalize_headers(self, content: str) -> str:
        """Normalize markdown header formatting."""
        lines = content.split('\n')
        normalized_lines = []
        headers_count = 0
        
        for line in lines:
            # Normalize ATX-style headers (# Header)
            match = re.match(r'^(#{1,6})\s*(.+?)\s*#*\s*$', line)
            if match:
                level, text = match.groups()
                # Ensure single space after hashes
                normalized_lines.append(f"{level} {text.strip()}")
                headers_count += 1
            # Convert Setext-style headers (underlined with = or -)
            elif len(normalized_lines) > 0:
                if re.match(r'^=+\s*$', line):
                    # Previous line is h1
                    prev = normalized_lines.pop()
                    normalized_lines.append(f"# {prev.strip()}")
                    headers_count += 1
                    continue
                elif re.match(r'^-+\s*$', line):
                    # Previous line is h2
                    prev = normalized_lines.pop()
                    normalized_lines.append(f"## {prev.strip()}")
                    headers_count += 1
                    continue
                else:
                    normalized_lines.append(line)
            else:
                normalized_lines.append(line)
        
        self.stats["headers_normalized"] = headers_count
        return '\n'.join(normalized_lines)
    
    def _standardize_links(self, content: str) -> str:
        """Standardize link and image formatting."""
        links_count = 0
        
        # Fix malformed links with extra spaces - trim spaces from link text and URL
        def fix_link(match):
            text = match.group(1).strip()
            url = match.group(2).strip()
            return f'[{text}]({url})'
        
        content = re.sub(r'\[\s*([^\]]+?)\s*\]\(\s*([^)]+?)\s*\)', fix_link, content)
        links_count += len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content))
        
        # Fix malformed images
        def fix_image(match):
            alt = match.group(1).strip()
            url = match.group(2).strip()
            return f'![{alt}]({url})'
        
        content = re.sub(r'!\[\s*([^\]]*?)\s*\]\(\s*([^)]+?)\s*\)', fix_image, content)
        
        self.stats["links_normalized"] = links_count
        return content
    
    def _normalize_whitespace(self, content: str) -> str:
        """Normalize whitespace throughout content."""
        changes = 0
        
        # Convert tabs to spaces
        if '\t' in content:
            content = content.replace('\t', '    ')
            changes += 1
        
        # Remove trailing whitespace from lines
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.rstrip()
            if stripped != line:
                changes += 1
            cleaned_lines.append(stripped)
        content = '\n'.join(cleaned_lines)
        
        # Normalize multiple spaces (not in code context)
        content = re.sub(r'([^\n ]) {2,}([^\n])', r'\1 \2', content)
        
        self.stats["whitespace_normalized"] = changes
        return content
    
    def _remove_excessive_newlines(self, content: str) -> str:
        """Remove more than 2 consecutive newlines."""
        # Replace 3+ newlines with 2 newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        return content
    
    def _final_cleanup(self, content: str) -> str:
        """Final cleanup pass."""
        # Remove leading/trailing whitespace
        content = content.strip()
        
        # Ensure single newline at end of file
        if content and not content.endswith('\n'):
            content += '\n'
        
        return content


def create_normalizer(
    preset: str = "standard",
    **kwargs
) -> ContentNormalizer:
    """
    Factory function to create a normalizer with preset configuration.
    
    Args:
        preset: Preset name ("minimal", "standard", "aggressive", "custom")
        **kwargs: Override specific settings
    
    Returns:
        Configured ContentNormalizer instance
    
    Examples:
        >>> normalizer = create_normalizer("standard")
        >>> normalizer = create_normalizer("aggressive", emoji_handling=EmojiHandling.REMOVE)
        >>> normalizer = create_normalizer("custom", remove_html=True, normalize_headers=False)
    """
    # Convert string emoji_handling to enum if needed
    if "emoji_handling" in kwargs:
        if isinstance(kwargs["emoji_handling"], str):
            kwargs["emoji_handling"] = EmojiHandling(kwargs["emoji_handling"])
    
    # Build base configuration based on preset
    level: NormalizationLevel
    emoji_handling: EmojiHandling = EmojiHandling.KEEP
    remove_html: bool = True
    remove_comments: bool = True
    normalize_headers: bool = True
    
    if preset == "minimal":
        level = NormalizationLevel.MINIMAL
        remove_html = False
        normalize_headers = False
    elif preset == "aggressive":
        level = NormalizationLevel.AGGRESSIVE
        emoji_handling = EmojiHandling.REMOVE
        remove_html = True
        remove_comments = True
    elif preset in ("standard", "custom"):
        level = NormalizationLevel.STANDARD
    else:
        raise ValueError(f"Unknown preset: {preset}. Use 'minimal', 'standard', or 'aggressive'")
    
    # Build config dictionary with proper types
    config = {
        "level": level,
        "emoji_handling": emoji_handling,
        "remove_html": remove_html,
        "remove_comments": remove_comments,
        "normalize_headers": normalize_headers,
    }
    
    # Override with kwargs
    config.update(kwargs)
    
    return ContentNormalizer(**config)
