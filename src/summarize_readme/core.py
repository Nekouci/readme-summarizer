"""
Core functionality for README summarization.
"""

import re
from enum import Enum
from typing import Any, Dict, List, Optional
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import markdown

from .content_normalizer import ContentNormalizer, NormalizationLevel, EmojiHandling, create_normalizer


class SummaryFormat(str, Enum):
    """Supported output formats."""
    TEXT = "text"
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"


class ReadmeSummarizer:
    """Main summarizer class with README parsing and analysis capabilities."""
    
    def __init__(
        self,
        max_length: int = 150,
        include_badges: bool = True,
        include_sections: bool = True,
        bullet_points: bool = False,
        enable_normalization: bool = True,
        normalization_level: str = "standard",
        emoji_handling: str = "keep",
    ):
        self.max_length = max_length
        self.include_badges = include_badges
        self.include_sections = include_sections
        self.bullet_points = bullet_points
        self.enable_normalization = enable_normalization
        
        # Initialize content normalizer
        if self.enable_normalization:
            emoji_mode = EmojiHandling(emoji_handling) if emoji_handling in ["keep", "remove", "convert"] else EmojiHandling.KEEP
            self.normalizer = create_normalizer(
                preset=normalization_level,
                emoji_handling=emoji_mode
            )
        else:
            self.normalizer = None
        
        # Stats tracking
        self.last_normalization_stats: Optional[Dict[str, int]] = None
    
    def fetch_from_url(self, url: str) -> str:
        """Fetch README content from a URL."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch URL: {e}")
    
    def summarize(
        self,
        content: str,
        output_format: SummaryFormat = SummaryFormat.TEXT,
        extract_links: bool = False,
    ) -> str:
        """
        Generate a summary of the README content.
        
        Args:
            content: Raw README content
            output_format: Desired output format
            extract_links: Whether to extract and include links
        
        Returns:
            Formatted summary string
        """
        # Normalize content if enabled
        if self.enable_normalization and self.normalizer:
            content = self.normalizer.normalize(content)
            self.last_normalization_stats = self.normalizer.get_stats()
        
        # Parse the markdown content
        parsed = self._parse_markdown(content)
        
        # Extract key components
        summary_parts = []
        
        # Add title
        if parsed['title']:
            summary_parts.append(f"**{parsed['title']}**")
        
        # Add description
        if parsed['description']:
            desc = self._truncate_text(parsed['description'], self.max_length)
            if self.bullet_points:
                summary_parts.append(f"• {desc}")
            else:
                summary_parts.append(desc)
        
        # Add badges info
        if self.include_badges and parsed['badges']:
            badge_text = f"Badges: {len(parsed['badges'])} found"
            if self.bullet_points:
                summary_parts.append(f"• {badge_text}")
            else:
                summary_parts.append(badge_text)
        
        # Add sections
        if self.include_sections and parsed['sections']:
            sections_text = "Sections: " + ", ".join(parsed['sections'][:5])
            if len(parsed['sections']) > 5:
                sections_text += f" (+{len(parsed['sections']) - 5} more)"
            if self.bullet_points:
                summary_parts.append(f"• {sections_text}")
            else:
                summary_parts.append(sections_text)
        
        # Add links
        if extract_links and parsed['links']:
            links_section = "\n\nLinks:\n" + "\n".join([f"  - {link}" for link in parsed['links'][:10]])
            summary_parts.append(links_section)
        
        # Format based on output type
        summary = "\n\n".join(summary_parts)
        
        if output_format == SummaryFormat.JSON:
            import json
            return json.dumps({
                "title": parsed['title'],
                "description": parsed['description'],
                "sections": parsed['sections'],
                "badges_count": len(parsed['badges']),
                "links_count": len(parsed['links']),
                "summary": summary,
            }, indent=2)
        elif output_format == SummaryFormat.HTML:
            return markdown.markdown(summary)
        elif output_format == SummaryFormat.MARKDOWN:
            return summary
        else:  # TEXT
            # Convert markdown to plain text
            return self._markdown_to_text(summary)
    
    def analyze(self, content: str, normalize: bool = True) -> Dict[str, Any]:
        """
        Analyze README and return detailed metrics.
        
        Args:
            content: Raw README content
            normalize: Whether to normalize before analysis (default: True)
        
        Returns:
            Dictionary with analysis results
        """
        # Optionally normalize content
        if normalize and self.enable_normalization and self.normalizer:
            content = self.normalizer.normalize(content)
            self.last_normalization_stats = self.normalizer.get_stats()
        
        parsed = self._parse_markdown(content)
        
        return {
            "size": len(content.encode('utf-8')),
            "lines": content.count('\n') + 1,
            "words": len(content.split()),
            "sections": len(parsed['sections']),
            "section_names": parsed['sections'],
            "code_blocks": content.count('```'),
            "links": len(parsed['links']),
            "badges": len(parsed['badges']),
            "images": len(re.findall(r'!\[.*?\]\(.*?\)', content)),
        }
    
    def get_normalization_stats(self) -> Optional[Dict[str, int]]:
        """
        Get statistics from the last normalization operation.
        
        Returns:
            Dictionary with normalization stats or None if normalization is disabled
        """
        return self.last_normalization_stats
    
    def _parse_markdown(self, content: str) -> Dict[str, Any]:
        """Parse markdown content and extract components."""
        # Extract title (first h1)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else ""
        
        # Extract description (first paragraph after title)
        description = ""
        lines = content.split('\n')
        found_title = False
        for line in lines:
            if line.startswith('# '):
                found_title = True
                continue
            if found_title and line.strip() and not line.startswith('#') and not line.startswith('!'):
                # Skip badges
                if not re.match(r'\[!\[.*?\]\(.*?\)\]', line):
                    description = line.strip()
                    break
        
        # Extract sections (all headers)
        sections = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
        sections = [s for s in sections if s != title]  # Remove title from sections
        
        # Extract badges
        badges = re.findall(r'\[!\[.*?\]\(.*?\)\]\(.*?\)', content)
        
        # Extract links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        links = [url for _, url in links if not url.startswith('#')]
        
        return {
            "title": title,
            "description": description,
            "sections": sections,
            "badges": badges,
            "links": links,
        }
    
    def _truncate_text(self, text: str, max_words: int) -> str:
        """Truncate text to max words."""
        words = text.split()
        if len(words) <= max_words:
            return text
        return ' '.join(words[:max_words]) + '...'
    
    def _markdown_to_text(self, md_text: str) -> str:
        """Convert markdown to plain text."""
        # Remove bold/italic markers
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', md_text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        
        # Remove links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        
        return text
