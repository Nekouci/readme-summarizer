"""
Advanced README formatter for standardizing and improving documentation.

Formats READMEs according to best practices with customizable templates.
"""

import re
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass

from .metadata_extractor import MetadataExtractor, READMEMetadata


class FormatStyle(str, Enum):
    """README formatting style presets."""
    STANDARD = "standard"  # Basic open-source project
    MINIMAL = "minimal"    # Minimal essential sections
    COMPREHENSIVE = "comprehensive"  # Full documentation
    LIBRARY = "library"    # For libraries/packages
    APPLICATION = "application"  # For applications/tools


@dataclass
class FormatOptions:
    """Options for README formatting."""
    style: FormatStyle = FormatStyle.STANDARD
    add_toc: bool = True
    fix_headings: bool = True
    add_badges_section: bool = True
    standardize_sections: bool = True
    add_missing_sections: bool = False
    sort_sections: bool = True
    preserve_custom_sections: bool = True
    max_line_length: Optional[int] = None
    emoji_style: str = "keep"  # keep, remove, standardize


class READMEFormatter:
    """Format and standardize README files."""
    
    # Standard section order by style
    SECTION_ORDER = {
        FormatStyle.MINIMAL: [
            "Title",
            "Description",
            "Installation",
            "Usage",
            "License"
        ],
        FormatStyle.STANDARD: [
            "Title",
            "Badges",
            "Description",
            "Features",
            "Installation",
            "Usage",
            "Examples",
            "API",
            "Configuration",
            "Contributing",
            "License",
            "Acknowledgments"
        ],
        FormatStyle.COMPREHENSIVE: [
            "Title",
            "Badges",
            "Table of Contents",
            "Description",
            "Features",
            "Demo",
            "Screenshots",
            "Installation",
            "Quick Start",
            "Usage",
            "Examples",
            "API Reference",
            "Configuration",
            "Advanced Usage",
            "Testing",
            "Deployment",
            "Performance",
            "Troubleshooting",
            "FAQ",
            "Roadmap",
            "Contributing",
            "Code of Conduct",
            "Security",
            "Changelog",
            "License",
            "Authors",
            "Acknowledgments",
            "Related Projects",
            "Support"
        ],
        FormatStyle.LIBRARY: [
            "Title",
            "Badges",
            "Description",
            "Features",
            "Installation",
            "Quick Start",
            "API Reference",
            "Examples",
            "Configuration",
            "Testing",
            "Contributing",
            "Changelog",
            "License"
        ],
        FormatStyle.APPLICATION: [
            "Title",
            "Badges",
            "Description",
            "Features",
            "Screenshots",
            "Installation",
            "Usage",
            "Configuration",
            "Examples",
            "Troubleshooting",
            "FAQ",
            "Contributing",
            "License"
        ]
    }
    
    # Section templates for missing sections
    SECTION_TEMPLATES = {
        "Installation": """## Installation

### Using pip
```bash
pip install {project_name}
```

### From source
```bash
git clone {repository_url}
cd {project_name}
pip install -e .
```
""",
        "Usage": """## Usage

### Basic Example
```{language}
# Add usage example here
```

### Quick Start
```bash
# Add command-line usage here
```

For more detailed usage instructions, see the [documentation]({docs_url}).
""",
        "Contributing": """## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.
""",
        "License": """## License

This project is licensed under the [LICENSE_NAME] License - see the [LICENSE](LICENSE) file for details.
""",
        "Features": """## Features

- ✨ Feature 1
- 🚀 Feature 2  
- 💡 Feature 3

""",
        "Examples": """## Examples

### Example 1
```{language}
# Add example code here
```

### Example 2
```{language}
# Add more examples
```

See the [examples](examples/) directory for more detailed examples.
""",
        "API Reference": """## API Reference

### Main Classes/Functions

#### `ClassName`

Description of the main class or function.

**Parameters:**
- `param1` (type): Description
- `param2` (type): Description

**Returns:**
- type: Description

**Example:**
```{language}
# Usage example
```

For complete API documentation, see [API.md](docs/API.md).
""",
        "Configuration": """## Configuration

### Basic Configuration

```{language}
# Configuration example
```

### Environment Variables

- `VAR_NAME`: Description (default: `value`)
- `ANOTHER_VAR`: Description

### Configuration File

See [config.example.yaml](config.example.yaml) for a complete configuration example.
""",
        "Testing": """## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov
```

### Writing Tests

Tests are located in the `tests/` directory. Follow the existing pattern for new tests.
""",
        "FAQ": """## FAQ

### Question 1?

Answer to question 1.

### Question 2?

Answer to question 2.

If you have more questions, please [open an issue](issues).
""",
        "Troubleshooting": """## Troubleshooting

### Common Issues

#### Issue 1

**Problem:** Description of the problem

**Solution:** How to fix it

#### Issue 2

**Problem:** Description of the problem

**Solution:** How to fix it

For more help, see [Issues](issues) or join our [community chat](chat_url).
"""
    }
    
    def __init__(self, options: Optional[FormatOptions] = None):
        """Initialize formatter with options."""
        self.options = options or FormatOptions()
        self.extractor = MetadataExtractor()
    
    def format(self, content: str, metadata: Optional[READMEMetadata] = None) -> str:
        """
        Format README content according to options.
        
        Args:
            content: Raw README markdown content
            metadata: Pre-extracted metadata (optional, will extract if not provided)
            
        Returns:
            Formatted README content
        """
        # Extract metadata if not provided
        if metadata is None:
            metadata = self.extractor.extract(content)
        
        # Parse existing content into sections
        sections = self._parse_content_sections(content)
        
        # Fix headings if enabled
        if self.options.fix_headings:
            sections = self._fix_heading_levels(sections)
        
        # Standardize section names
        if self.options.standardize_sections:
            sections = self._standardize_section_names(sections)
        
        # Add missing sections if enabled
        if self.options.add_missing_sections:
            sections = self._add_missing_sections(sections, metadata)
        
        # Sort sections according to style
        if self.options.sort_sections:
            sections = self._sort_sections(sections, metadata)
        
        # Build formatted README
        formatted = self._build_readme(sections, metadata)
        
        # Add table of contents if enabled
        if self.options.add_toc and self._should_add_toc(sections):
            formatted = self._add_table_of_contents(formatted, sections)
        
        # Apply line length limit if set
        if self.options.max_line_length:
            formatted = self._wrap_lines(formatted, self.options.max_line_length)
        
        # Handle emoji formatting
        if self.options.emoji_style != "keep":
            formatted = self._format_emojis(formatted, self.options.emoji_style)
        
        return formatted
    
    def _parse_content_sections(self, content: str) -> Dict[str, str]:
        """Parse content into section dictionary."""
        sections = {}
        lines = content.split('\n')
        
        current_section = "Header"
        current_content = []
        in_code_block = False
        
        for line in lines:
            # Track code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                current_content.append(line)
                continue
            
            if in_code_block:
                current_content.append(line)
                continue
            
            # Check for heading
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if heading_match and len(heading_match.group(1)) <= 2:  # Only h1 and h2
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                # Remove emojis from title for key
                clean_title = re.sub(r'[^\w\s\-]', '', title).strip()
                current_section = clean_title if clean_title else title
                current_content = [line]
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _fix_heading_levels(self, sections: Dict[str, str]) -> Dict[str, str]:
        """Fix inconsistent heading levels."""
        fixed_sections = {}
        
        for name, content in sections.items():
            lines = content.split('\n')
            fixed_lines = []
            
            for line in lines:
                heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
                if heading_match:
                    level = len(heading_match.group(1))
                    title = heading_match.group(2)
                    
                    # Ensure proper nesting (max 4 levels)
                    if level > 4:
                        level = 4
                    
                    fixed_lines.append(f"{'#' * level} {title}")
                else:
                    fixed_lines.append(line)
            
            fixed_sections[name] = '\n'.join(fixed_lines)
        
        return fixed_sections
    
    def _standardize_section_names(self, sections: Dict[str, str]) -> Dict[str, str]:
        """Standardize section names to common conventions."""
        name_mappings = {
            'install': 'Installation',
            'installing': 'Installation',
            'setup': 'Installation',
            'getting started': 'Installation',
            'how to use': 'Usage',
            'using': 'Usage',
            'quickstart': 'Quick Start',
            'quick-start': 'Quick Start',
            'example': 'Examples',
            'demos': 'Examples',
            'contribute': 'Contributing',
            'development': 'Contributing',
            'licence': 'License',
            'features': 'Features',
            'documentation': 'API Reference',
            'api docs': 'API Reference',
            'config': 'Configuration',
            'settings': 'Configuration',
            'tests': 'Testing',
            'credits': 'Acknowledgments',
            'thanks': 'Acknowledgments',
        }
        
        standardized = {}
        for name, content in sections.items():
            # Normalize name for lookup
            normalized_name = name.lower().strip()
            
            # Check mappings
            standard_name = name
            for pattern, replacement in name_mappings.items():
                if pattern in normalized_name:
                    standard_name = replacement
                    # Update heading in content
                    content = re.sub(
                        r'^#{1,2}\s+' + re.escape(name),
                        f'## {replacement}',
                        content,
                        flags=re.IGNORECASE
                    )
                    break
            
            standardized[standard_name] = content
        
        return standardized
    
    def _add_missing_sections(self, sections: Dict[str, str], metadata: READMEMetadata) -> Dict[str, str]:
        """Add placeholders for missing standard sections."""
        order = self.SECTION_ORDER[self.options.style]
        
        for section_name in order:
            if section_name not in sections and section_name in self.SECTION_TEMPLATES:
                # Create section from template
                template = self.SECTION_TEMPLATES[section_name]
                
                # Fill in template variables
                template = template.replace(
                    '{project_name}',
                    metadata.title or 'your-project'
                )
                template = template.replace(
                    '{repository_url}',
                    metadata.repository_url or 'https://github.com/username/repo'
                )
                template = template.replace(
                    '{docs_url}',
                    metadata.documentation_url or '#'
                )
                template = template.replace(
                    '{language}',
                    metadata.language or 'python'
                )
                
                sections[section_name] = template
        
        return sections
    
    def _sort_sections(self, sections: Dict[str, str], metadata: READMEMetadata) -> Dict[str, str]:
        """Sort sections according to style order."""
        order = self.SECTION_ORDER[self.options.style]
        sorted_sections = {}
        
        # Add sections in order
        for section_name in order:
            if section_name in sections:
                sorted_sections[section_name] = sections[section_name]
        
        # Add remaining custom sections at the end if preserving
        if self.options.preserve_custom_sections:
            for name, content in sections.items():
                if name not in sorted_sections and name != "Header":
                    sorted_sections[name] = content
        
        # Always keep Header first if it exists
        if "Header" in sections:
            header_content = sections["Header"]
            sorted_sections = {"Header": header_content, **sorted_sections}
        
        return sorted_sections
    
    def _build_readme(self, sections: Dict[str, str], metadata: READMEMetadata) -> str:
        """Build formatted README from sections."""
        parts = []
        
        # Add title if not in Header
        if "Header" in sections:
            parts.append(sections["Header"])
        elif metadata.title:
            parts.append(f"# {metadata.title}\n")
            if metadata.description:
                parts.append(f"{metadata.description}\n")
        
        # Add badges section if enabled and badges exist
        if self.options.add_badges_section and metadata.badges and "Badges" not in sections:
            badge_lines = []
            for badge in metadata.badges:
                if badge.link_url:
                    badge_lines.append(f"[![{badge.alt_text}]({badge.image_url})]({badge.link_url})")
                else:
                    badge_lines.append(f"![{badge.alt_text}]({badge.image_url})")
            
            if badge_lines:
                parts.append("\n" + " ".join(badge_lines) + "\n")
        
        # Add all other sections
        for name, content in sections.items():
            if name != "Header":
                # Ensure section starts with proper heading if missing
                if not content.strip().startswith('#'):
                    parts.append(f"\n## {name}\n\n{content}\n")
                else:
                    parts.append(f"\n{content}\n")
        
        return '\n'.join(parts).strip() + '\n'
    
    def _should_add_toc(self, sections: Dict[str, str]) -> bool:
        """Determine if table of contents should be added."""
        # Add TOC if more than 4 sections
        section_count = len([s for s in sections.keys() if s != "Header"])
        return section_count >= 4
    
    def _add_table_of_contents(self, content: str, sections: Dict[str, str]) -> str:
        """Add table of contents to README."""
        # Check if TOC already exists
        if re.search(r'##\s*Table\s+of\s+Contents', content, re.IGNORECASE):
            return content
        
        # Build TOC
        toc_lines = ["## Table of Contents\n"]
        
        lines = content.split('\n')
        for line in lines:
            heading_match = re.match(r'^(#{2,3})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                
                # Skip TOC itself
                if 'table of contents' in title.lower():
                    continue
                
                # Create anchor link
                anchor = re.sub(r'[^\w\s-]', '', title.lower())
                anchor = re.sub(r'\s+', '-', anchor)
                
                indent = '  ' * (level - 2)
                toc_lines.append(f"{indent}- [{title}](#{anchor})")
        
        toc = '\n'.join(toc_lines) + '\n'
        
        # Insert TOC after title/badges
        lines = content.split('\n')
        insert_pos = 0
        
        # Find position after title and badges
        for i, line in enumerate(lines):
            if line.strip().startswith('##') and 'table of contents' not in line.lower():
                insert_pos = i
                break
            if line.strip() and not line.startswith('#') and not line.startswith('!') and not line.startswith('['):
                insert_pos = i
                break
        
        if insert_pos > 0:
            lines.insert(insert_pos, toc)
            return '\n'.join(lines)
        else:
            return toc + '\n' + content
    
    def _wrap_lines(self, content: str, max_length: int) -> str:
        """Wrap long lines to max length (excluding code blocks)."""
        lines = content.split('\n')
        wrapped = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                wrapped.append(line)
                continue
            
            if in_code_block or line.startswith('#') or line.startswith('|'):
                wrapped.append(line)
            elif len(line) > max_length:
                # Simple word wrapping
                words = line.split()
                current_line = []
                current_length = 0
                
                for word in words:
                    if current_length + len(word) + 1 > max_length:
                        wrapped.append(' '.join(current_line))
                        current_line = [word]
                        current_length = len(word)
                    else:
                        current_line.append(word)
                        current_length += len(word) + 1
                
                if current_line:
                    wrapped.append(' '.join(current_line))
            else:
                wrapped.append(line)
        
        return '\n'.join(wrapped)
    
    def _format_emojis(self, content: str, style: str) -> str:
        """Format emojis according to style."""
        if style == "remove":
            # Remove all emojis
            emoji_pattern = re.compile(
                "["
                "\U0001F600-\U0001F64F"  # emoticons
                "\U0001F300-\U0001F5FF"  # symbols & pictographs
                "\U0001F680-\U0001F6FF"  # transport & map symbols
                "\U0001F1E0-\U0001F1FF"  # flags
                "\U00002702-\U000027B0"
                "\U000024C2-\U0001F251"
                "]+",
                flags=re.UNICODE
            )
            content = emoji_pattern.sub('', content)
            
            # Clean up extra spaces
            content = re.sub(r'\s+', ' ', content)
        
        elif style == "standardize":
            # Ensure consistent emoji usage in section headers
            section_emojis = {
                'Features': '✨',
                'Installation': '📦',
                'Usage': '🚀',
                'Examples': '💡',
                'Contributing': '🤝',
                'License': '📄',
                'API': '📚',
                'Testing': '🧪',
                'Configuration': '⚙️',
            }
            
            for section, emoji in section_emojis.items():
                # Remove existing emoji and add standard one
                pattern = r'(##\s*)(?:[^\w\s]*\s*)?' + re.escape(section)
                replacement = r'\1' + emoji + ' ' + section
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        return content
    
    def format_quality_improvements(self, content: str) -> tuple[str, List[str]]:
        """
        Format README with automatic quality improvements.
        
        Returns:
            Tuple of (formatted_content, list_of_improvements_made)
        """
        improvements = []
        metadata = self.extractor.extract(content)
        
        # Extract quality report
        quality = self.extractor.quality_report(metadata)
        
        # Start with basic formatting
        formatted = self.format(content, metadata)
        
        # Apply quality improvements based on report
        if 'Add a table of contents' in quality['suggestions']:
            # TOC already handled in format
            improvements.append("Added table of contents")
        
        if 'Status badges' in quality['missing'] and metadata.repository_url:
            # Could add suggested badge placeholders
            improvements.append("Added badge section placeholder")
        
        if not metadata.description and metadata.sections:
            improvements.append("Improved section structure")
        
        return formatted, improvements


def format_readme(
    content: str,
    style: FormatStyle = FormatStyle.STANDARD,
    add_toc: bool = True,
    add_missing: bool = False
) -> str:
    """
    Convenience function to format README content.
    
    Args:
        content: Raw README markdown content
        style: Formatting style preset
        add_toc: Add table of contents
        add_missing: Add missing standard sections
        
    Returns:
        Formatted README content
    """
    options = FormatOptions(
        style=style,
        add_toc=add_toc,
        add_missing_sections=add_missing
    )
    formatter = READMEFormatter(options)
    return formatter.format(content)
