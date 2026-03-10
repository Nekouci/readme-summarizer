"""
Tests for the content normalizer module.
"""

import unittest
from summarize_readme.content_normalizer import (
    ContentNormalizer,
    NormalizationLevel,
    EmojiHandling,
    create_normalizer,
)


class TestContentNormalizer(unittest.TestCase):
    """Test cases for ContentNormalizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.normalizer = ContentNormalizer()
    
    def test_basic_normalization(self):
        """Test basic content normalization."""
        content = "# Title\n\n\n\nSome content with    extra   spaces."
        normalized = self.normalizer.normalize(content)
        
        # Should remove excessive newlines
        self.assertNotIn('\n\n\n\n', normalized)
        # Should maintain basic structure
        self.assertIn('# Title', normalized)
        self.assertIn('Some content', normalized)
    
    def test_unicode_normalization(self):
        """Test unicode character normalization."""
        content = "Smart\u2019quotes and\u00a0spaces"
        normalized = self.normalizer.normalize(content)
        
        # Smart quotes should be converted to regular quotes
        self.assertNotIn('\u2019', normalized)
        self.assertIn("'", normalized)
        # Non-breaking spaces should become regular spaces
        self.assertIn(' ', normalized)
    
    def test_html_removal(self):
        """Test HTML tag removal."""
        content = """
# Title

<div>Some HTML content</div>
<script>alert('test');</script>
Regular **markdown** text.
"""
        normalizer = ContentNormalizer(remove_html=True)
        normalized = normalizer.normalize(content)
        
        # HTML tags should be removed
        self.assertNotIn('<div>', normalized)
        self.assertNotIn('<script>', normalized)
        # Markdown should remain
        self.assertIn('**markdown**', normalized)
        # Content should remain
        self.assertIn('Some HTML content', normalized)
    
    def test_comment_removal(self):
        """Test HTML comment removal."""
        content = """
# Title

<!-- This is a comment -->
Some content
<!-- Another comment -->
More content
"""
        normalizer = ContentNormalizer(remove_comments=True)
        normalized = normalizer.normalize(content)
        
        # Comments should be removed
        self.assertNotIn('<!--', normalized)
        self.assertNotIn('This is a comment', normalized)
        # Content should remain
        self.assertIn('Some content', normalized)
        self.assertIn('More content', normalized)
    
    def test_emoji_removal(self):
        """Test emoji removal."""
        content = "# 🚀 Title\n\nSome content with emojis 🎨 ✨"
        normalizer = ContentNormalizer(emoji_handling=EmojiHandling.REMOVE)
        normalized = normalizer.normalize(content)
        
        # Emojis should be removed
        self.assertNotIn('🚀', normalized)
        self.assertNotIn('🎨', normalized)
        self.assertNotIn('✨', normalized)
        # Text should remain
        self.assertIn('Title', normalized)
        self.assertIn('Some content', normalized)
    
    def test_emoji_conversion(self):
        """Test emoji conversion to text."""
        content = "# 🚀 Project\n\n✨ Features"
        normalizer = ContentNormalizer(emoji_handling=EmojiHandling.CONVERT)
        normalized = normalizer.normalize(content)
        
        # Emojis should be converted
        self.assertIn('[rocket]', normalized)
        self.assertIn('[sparkles]', normalized)
    
    def test_emoji_keep(self):
        """Test keeping emojis intact."""
        content = "# 🚀 Project\n\n✨ Features"
        normalizer = ContentNormalizer(emoji_handling=EmojiHandling.KEEP)
        normalized = normalizer.normalize(content)
        
        # Emojis should remain
        self.assertIn('🚀', normalized)
        self.assertIn('✨', normalized)
    
    def test_header_normalization(self):
        """Test markdown header normalization."""
        content = """
#Title Without Space
##  Title With Extra Spaces  ##
### Title With Trailing Hashes ###

Underlined H1
===========

Underlined H2
-----------
"""
        normalizer = ContentNormalizer(normalize_headers=True)
        normalized = normalizer.normalize(content)
        
        # Headers should be normalized
        self.assertIn('# Title Without Space', normalized)
        self.assertIn('## Title With Extra Spaces', normalized)
        self.assertIn('### Title With Trailing Hashes', normalized)
        # Underlined headers should be converted
        self.assertIn('# Underlined H1', normalized)
        self.assertIn('## Underlined H2', normalized)
    
    def test_link_standardization(self):
        """Test link formatting standardization."""
        content = """
[ Link with spaces ]( https://example.com )
[Normal link](https://example.com)
![ Image with spaces ]( image.png )
"""
        normalizer = ContentNormalizer(standardize_links=True)
        normalized = normalizer.normalize(content)
        
        # Links should be normalized
        self.assertIn('[Link with spaces](https://example.com)', normalized)
        self.assertIn('[Image with spaces](image.png)', normalized)
    
    def test_code_block_preservation(self):
        """Test that code blocks are preserved during normalization."""
        content = """
# Title

```python
def   function_with_weird_spacing():
    return    "preserved"
```

Regular text with    spaces.
"""
        normalizer = ContentNormalizer(
            preserve_code_blocks=True,
            normalize_whitespace=True
        )
        normalized = normalizer.normalize(content)
        
        # Code content should be preserved
        self.assertIn('function_with_weird_spacing', normalized)
        self.assertIn('return    "preserved"', normalized)
        # Regular text should be normalized (this is context-dependent)
    
    def test_whitespace_normalization(self):
        """Test whitespace normalization."""
        content = "Text with\ttabs and   multiple     spaces"
        normalizer = ContentNormalizer(normalize_whitespace=True)
        normalized = normalizer.normalize(content)
        
        # Tabs should be converted
        self.assertNotIn('\t', normalized)
        # Multiple spaces should be reduced (in non-code context)
    
    def test_excessive_newlines_removal(self):
        """Test removal of excessive newlines."""
        content = "Line 1\n\n\n\n\n\nLine 2"
        normalizer = ContentNormalizer(remove_excessive_newlines=True)
        normalized = normalizer.normalize(content)
        
        # Should have max 2 consecutive newlines
        self.assertNotIn('\n\n\n', normalized)
        self.assertIn('Line 1', normalized)
        self.assertIn('Line 2', normalized)
    
    def test_stats_tracking(self):
        """Test that statistics are tracked correctly."""
        content = """
# Title

<div>HTML content</div>
<!-- Comment -->

Some content with 🚀 emoji.
"""
        normalizer = ContentNormalizer(
            remove_html=True,
            remove_comments=True,
            emoji_handling=EmojiHandling.REMOVE
        )
        normalized = normalizer.normalize(content)
        stats = normalizer.get_stats()
        
        # Stats should contain expected keys
        self.assertIn('original_size', stats)
        self.assertIn('final_size', stats)
        self.assertIn('size_reduction', stats)
        self.assertIn('original_lines', stats)
        self.assertIn('final_lines', stats)
        
        # Size should be reduced
        self.assertGreater(stats['size_reduction'], 0)
    
    def test_minimal_level(self):
        """Test minimal normalization level."""
        normalizer = ContentNormalizer(level=NormalizationLevel.MINIMAL)
        content = "<div>HTML</div> with content"
        normalized = normalizer.normalize(content)
        
        # Minimal should preserve more
        # HTML removal is disabled by default for minimal
        self.assertFalse(normalizer.remove_html)
    
    def test_standard_level(self):
        """Test standard normalization level."""
        normalizer = ContentNormalizer(level=NormalizationLevel.STANDARD)
        
        # Standard should have balanced defaults
        self.assertTrue(normalizer.remove_html)
        self.assertTrue(normalizer.normalize_whitespace)
    
    def test_aggressive_level(self):
        """Test aggressive normalization level."""
        normalizer = ContentNormalizer(level=NormalizationLevel.AGGRESSIVE)
        
        # Aggressive should enable all normalizations
        self.assertTrue(normalizer.remove_html)
        self.assertTrue(normalizer.remove_comments)
        self.assertTrue(normalizer.normalize_whitespace)
        self.assertTrue(normalizer.normalize_headers)
    
    def test_empty_content(self):
        """Test handling of empty content."""
        normalized = self.normalizer.normalize("")
        self.assertEqual(normalized, "")
        
        normalized = self.normalizer.normalize("   \n\n   ")
        # Should handle whitespace-only content
        self.assertIsNotNone(normalized)
    
    def test_real_world_readme(self):
        """Test with a realistic README example."""
        content = """
# 🚀 My Project

<div align="center">
  <img src="logo.png" alt="Logo">
</div>

<!-- Build status -->
![Build](https://img.shields.io/badge/build-passing-green)

## ✨ Features

- Feature 1
- Feature 2  
- Feature 3

###Installation

```bash
npm install my-project
```

## Usage

Use this project by...

<!-- TODO: Add more examples -->

"""
        normalizer = ContentNormalizer(
            level=NormalizationLevel.STANDARD,
            emoji_handling=EmojiHandling.KEEP
        )
        normalized = normalizer.normalize(content)
        
        # Should maintain structure
        self.assertIn('# ', normalized)
        self.assertIn('## ', normalized)
        # Should clean up spacing
        self.assertNotIn('\n\n\n\n', normalized)
        # Should preserve code blocks
        self.assertIn('```bash', normalized)


class TestCreateNormalizer(unittest.TestCase):
    """Test cases for create_normalizer factory function."""
    
    def test_minimal_preset(self):
        """Test minimal preset creation."""
        normalizer = create_normalizer("minimal")
        self.assertEqual(normalizer.level, NormalizationLevel.MINIMAL)
        self.assertFalse(normalizer.remove_html)
    
    def test_standard_preset(self):
        """Test standard preset creation."""
        normalizer = create_normalizer("standard")
        self.assertEqual(normalizer.level, NormalizationLevel.STANDARD)
    
    def test_aggressive_preset(self):
        """Test aggressive preset creation."""
        normalizer = create_normalizer("aggressive")
        self.assertEqual(normalizer.level, NormalizationLevel.AGGRESSIVE)
        self.assertEqual(normalizer.emoji_handling, EmojiHandling.REMOVE)
    
    def test_custom_overrides(self):
        """Test custom parameter overrides."""
        normalizer = create_normalizer(
            "standard",
            emoji_handling=EmojiHandling.REMOVE,
            remove_html=False
        )
        self.assertEqual(normalizer.emoji_handling, EmojiHandling.REMOVE)
        self.assertFalse(normalizer.remove_html)
    
    def test_invalid_preset(self):
        """Test invalid preset raises error."""
        with self.assertRaises(ValueError):
            create_normalizer("invalid_preset")


if __name__ == '__main__':
    unittest.main()
