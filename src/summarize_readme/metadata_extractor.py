"""
Advanced metadata extraction from README files.

Extracts structured information including badges, licenses, tech stacks, 
dependencies, links, code samples, and more.
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict, field
from urllib.parse import urlparse
import json

from bs4 import BeautifulSoup
import markdown


@dataclass
class Badge:
    """Represents a badge found in the README."""
    alt_text: str
    image_url: str
    link_url: Optional[str] = None
    badge_type: Optional[str] = None  # e.g., 'build', 'coverage', 'version', 'license'


@dataclass
class Link:
    """Represents a link found in the README."""
    text: str
    url: str
    link_type: str  # 'documentation', 'repository', 'social', 'website', 'other'


@dataclass
class CodeBlock:
    """Represents a code block in the README."""
    language: str
    code: str
    line_number: Optional[int] = None


@dataclass
class Section:
    """Represents a section in the README."""
    title: str
    level: int  # Heading level (1-6)
    content: str
    subsections: List['Section'] = field(default_factory=list)


@dataclass
class READMEMetadata:
    """Complete metadata extracted from a README file."""
    # Basic info
    title: Optional[str] = None
    description: Optional[str] = None
    
    # Technical details
    language: Optional[str] = None
    tech_stack: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    # Project info
    license: Optional[str] = None
    version: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    
    # Badges and links
    badges: List[Badge] = field(default_factory=list)
    links: List[Link] = field(default_factory=list)
    
    # Structure
    sections: List[Section] = field(default_factory=list)
    section_names: List[str] = field(default_factory=list)
    table_of_contents: bool = False
    
    # Code samples
    code_blocks: List[CodeBlock] = field(default_factory=list)
    
    # Quality metrics
    word_count: int = 0
    line_count: int = 0
    has_installation: bool = False
    has_usage: bool = False
    has_contributing: bool = False
    has_license_section: bool = False
    has_examples: bool = False
    completeness_score: float = 0.0
    
    # Social/Community
    repository_url: Optional[str] = None
    documentation_url: Optional[str] = None
    homepage_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary with proper serialization."""
        result = asdict(self)
        # Convert Badge, Link, CodeBlock, Section objects to dicts
        result['badges'] = [asdict(b) for b in self.badges]
        result['links'] = [asdict(link) for link in self.links]
        result['code_blocks'] = [asdict(cb) for cb in self.code_blocks]
        result['sections'] = [self._section_to_dict(s) for s in self.sections]
        return result
    
    def _section_to_dict(self, section: Section) -> Dict[str, Any]:
        """Recursively convert section to dict."""
        return {
            'title': section.title,
            'level': section.level,
            'content': section.content[:200] + '...' if len(section.content) > 200 else section.content,
            'subsections': [self._section_to_dict(s) for s in section.subsections]
        }


class MetadataExtractor:
    """Extract structured metadata from README files."""
    
    # Common section patterns
    SECTION_PATTERNS = {
        'installation': r'(?i)install(?:ation)?|setup|getting\s+started',
        'usage': r'(?i)usage|how\s+to\s+use|quick\s*start',
        'examples': r'(?i)examples?|demos?',
        'contributing': r'(?i)contribut(?:ing|ion)|development',
        'license': r'(?i)licen[cs]e',
        'testing': r'(?i)test(?:ing|s)?',
        'documentation': r'(?i)documentation|docs',
        'api': r'(?i)api\s*(?:reference|documentation)?',
        'features': r'(?i)features?',
        'changelog': r'(?i)changelog|release\s*notes?|version\s*history',
        'faq': r'(?i)faq|frequently\s+asked',
        'roadmap': r'(?i)roadmap|future|upcoming',
        'acknowledgments': r'(?i)acknowledge?ments?|credits?|thanks',
    }
    
    # Badge type patterns
    BADGE_PATTERNS = {
        'build': r'(?i)build|ci|travis|circleci|github\s*actions?|azure',
        'coverage': r'(?i)coverage|codecov|coveralls',
        'version': r'(?i)version|npm|pypi|release',
        'license': r'(?i)licen[cs]e',
        'downloads': r'(?i)downloads?',
        'dependencies': r'(?i)dependencies|deps|david-dm',
        'quality': r'(?i)quality|code\s*climate|codacy|sonar',
        'status': r'(?i)status|maintained|activity',
    }
    
    # Link type patterns
    LINK_TYPE_PATTERNS = {
        'documentation': r'(?i)docs?|documentation|wiki|guide|manual',
        'repository': r'github\.com|gitlab\.com|bitbucket\.org|git\.',
        'social': r'twitter\.com|linkedin\.com|facebook\.com|discord|slack|gitter',
        'website': r'(?i)homepage|website|site',
    }
    
    # Tech stack keywords
    TECH_KEYWORDS = [
        # Languages
        'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'ruby', 'go', 
        'rust', 'php', 'swift', 'kotlin', 'scala', 'r', 'perl', 'lua', 'dart',
        # Frameworks
        'react', 'vue', 'angular', 'django', 'flask', 'fastapi', 'express', 'nest',
        'spring', 'rails', 'laravel', 'asp.net', 'nextjs', 'nuxt', 'svelte',
        # Databases
        'postgresql', 'mysql', 'mongodb', 'redis', 'sqlite', 'cassandra', 'elasticsearch',
        # Tools
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'terraform', 'ansible',
        'webpack', 'vite', 'babel', 'jest', 'pytest', 'selenium',
    ]
    
    def __init__(self):
        """Initialize the metadata extractor."""
        self.html_parser = markdown.Markdown(extensions=['extra', 'codehilite', 'toc'])
    
    def extract(self, content: str) -> READMEMetadata:
        """
        Extract comprehensive metadata from README content.
        
        Args:
            content: Raw README markdown content
            
        Returns:
            READMEMetadata object with extracted information
        """
        metadata = READMEMetadata()
        
        # Basic metrics
        metadata.line_count = len(content.split('\n'))
        metadata.word_count = len(content.split())
        
        # Extract title and description
        metadata.title, metadata.description = self._extract_title_and_description(content)
        
        # Extract badges
        metadata.badges = self._extract_badges(content)
        
        # Extract links
        metadata.links = self._extract_links(content)
        
        # Extract sections
        metadata.sections = self._extract_sections(content)
        metadata.section_names = [s.title for s in metadata.sections]
        
        # Extract code blocks
        metadata.code_blocks = self._extract_code_blocks(content)
        
        # Detect technical details
        metadata.license = self._extract_license(content)
        metadata.version = self._extract_version(content)
        metadata.tech_stack = self._extract_tech_stack(content)
        metadata.dependencies = self._extract_dependencies(content)
        metadata.language = self._detect_primary_language(content, metadata.code_blocks)
        
        # Extract important URLs
        metadata.repository_url = self._extract_url(metadata.links, 'repository')
        metadata.documentation_url = self._extract_url(metadata.links, 'documentation')
        metadata.homepage_url = self._extract_url(metadata.links, 'website')
        
        # Check for table of contents
        metadata.table_of_contents = self._has_table_of_contents(content)
        
        # Analyze sections
        metadata.has_installation = self._has_section('installation', metadata.section_names)
        metadata.has_usage = self._has_section('usage', metadata.section_names)
        metadata.has_contributing = self._has_section('contributing', metadata.section_names)
        metadata.has_license_section = self._has_section('license', metadata.section_names)
        metadata.has_examples = self._has_section('examples', metadata.section_names) or len(metadata.code_blocks) > 0
        
        # Calculate completeness score
        metadata.completeness_score = self._calculate_completeness(metadata)
        
        return metadata
    
    def _extract_title_and_description(self, content: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract the main title and description from README."""
        lines = content.split('\n')
        title = None
        description = None
        
        # Find first heading
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                # Remove heading markers and clean
                title = re.sub(r'^#+\s*', '', line).strip()
                # Remove emojis and badges
                title = re.sub(r'!\[.*?\]\(.*?\)', '', title).strip()
                break
        
        # Find first substantial paragraph as description
        in_code_block = False
        for line in lines:
            line = line.strip()
            
            # Track code blocks
            if line.startswith('```'):
                in_code_block = not in_code_block
                continue
            
            if in_code_block or not line or line.startswith('#') or line.startswith('![') or line.startswith('[!'):
                continue
            
            # Skip badges and similar
            if re.match(r'^\[.*?\]\(.*?\)$', line):
                continue
                
            # Found a good description candidate
            if len(line) > 20 and not line.startswith('|'):
                description = line
                break
        
        return title, description
    
    def _extract_badges(self, content: str) -> List[Badge]:
        """Extract all badges from README."""
        badges = []
        
        # Pattern for markdown badges: [![alt](img)](link) or ![alt](img)
        badge_pattern = r'\[?!\[([^\]]*)\]\(([^)]+)\)\]?(?:\(([^)]+)\))?'
        
        for match in re.finditer(badge_pattern, content):
            alt_text = match.group(1)
            image_url = match.group(2)
            link_url = match.group(3) if len(match.groups()) >= 3 else None
            
            # Detect badge type
            badge_type = self._classify_badge(alt_text, image_url)
            
            badges.append(Badge(
                alt_text=alt_text,
                image_url=image_url,
                link_url=link_url,
                badge_type=badge_type
            ))
        
        return badges
    
    def _classify_badge(self, alt_text: str, image_url: str) -> str:
        """Classify badge type based on content."""
        combined = f"{alt_text} {image_url}".lower()
        
        for badge_type, pattern in self.BADGE_PATTERNS.items():
            if re.search(pattern, combined):
                return badge_type
        
        return 'other'
    
    def _extract_links(self, content: str) -> List[Link]:
        """Extract all links from README."""
        links = []
        seen_urls = set()
        
        # Pattern for markdown links: [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        for match in re.finditer(link_pattern, content):
            text = match.group(1)
            url = match.group(2)
            
            # Skip image links and anchors
            if url.startswith('#') or text.startswith('!'):
                continue
            
            # Skip duplicates
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            # Classify link type
            link_type = self._classify_link(text, url)
            
            links.append(Link(
                text=text,
                url=url,
                link_type=link_type
            ))
        
        return links
    
    def _classify_link(self, text: str, url: str) -> str:
        """Classify link type based on URL and text."""
        combined = f"{text} {url}".lower()
        
        for link_type, pattern in self.LINK_TYPE_PATTERNS.items():
            if re.search(pattern, combined):
                return link_type
        
        return 'other'
    
    def _extract_sections(self, content: str) -> List[Section]:
        """Extract section structure from README."""
        sections = []
        lines = content.split('\n')
        
        current_sections = {}  # Track sections by level
        in_code_block = False
        
        for i, line in enumerate(lines):
            # Track code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            if in_code_block:
                continue
            
            # Check for heading
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if heading_match:
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                
                # Remove emojis and badges from title
                title = re.sub(r'!\[.*?\]\(.*?\)', '', title).strip()
                
                section = Section(
                    title=title,
                    level=level,
                    content=""
                )
                
                # Add to appropriate parent
                if level == 1:
                    sections.append(section)
                    current_sections = {1: section}
                else:
                    # Find parent section
                    parent_level = level - 1
                    while parent_level > 0 and parent_level not in current_sections:
                        parent_level -= 1
                    
                    if parent_level > 0:
                        current_sections[parent_level].subsections.append(section)
                    else:
                        sections.append(section)
                    
                    current_sections[level] = section
        
        return sections
    
    def _extract_code_blocks(self, content: str) -> List[CodeBlock]:
        """Extract all code blocks with their languages."""
        code_blocks = []
        
        # Pattern for fenced code blocks
        code_pattern = r'```(\w+)?\n(.*?)```'
        
        line_number = 1
        for match in re.finditer(code_pattern, content, re.DOTALL):
            language = match.group(1) or 'plaintext'
            code = match.group(2).strip()
            
            # Calculate line number
            line_number = content[:match.start()].count('\n') + 1
            
            code_blocks.append(CodeBlock(
                language=language,
                code=code,
                line_number=line_number
            ))
        
        return code_blocks
    
    def _extract_license(self, content: str) -> Optional[str]:
        """Extract license information."""
        # Common license patterns
        license_patterns = [
            r'licen[cs]e[:\s]+([A-Z][\w\s\-\.]+(?:License)?)',
            r'(MIT|Apache|GPL|BSD|ISC|MPL|LGPL|AGPL|CC[\w\-]+)\s*[Ll]icen[cs]e',
            r'!\[License\]\([^)]*\)\]\((https?://[^)]+)\)',
        ]
        
        for pattern in license_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                license_text = match.group(1).strip()
                # Clean up common suffixes
                license_text = re.sub(r'\s*[Ll]icen[cs]e\s*$', '', license_text)
                return license_text
        
        return None
    
    def _extract_version(self, content: str) -> Optional[str]:
        """Extract version information."""
        version_patterns = [
            r'version[:\s]+v?(\d+\.\d+\.\d+[\w\-\.]*)',
            r'v(\d+\.\d+\.\d+[\w\-\.]*)',
            r'!\[Version\]\([^)]*badge/v[^)]*-(\d+\.\d+\.\d+)',
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_tech_stack(self, content: str) -> List[str]:
        """Extract technology stack from README."""
        content_lower = content.lower()
        found_techs = set()
        
        for tech in self.TECH_KEYWORDS:
            # Look for whole word matches
            if re.search(r'\b' + re.escape(tech.lower()) + r'\b', content_lower):
                found_techs.add(tech)
        
        return sorted(list(found_techs))
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependency names from code blocks and text."""
        dependencies = set()
        
        # Look for requirements.txt style
        requirements_pattern = r'```(?:bash|sh|shell)?\n(?:pip install |npm install |yarn add )([^\n]+)'
        for match in re.finditer(requirements_pattern, content):
            deps = match.group(1).strip().split()
            dependencies.update([d for d in deps if not d.startswith('-')])
        
        # Look for package.json, requirements.txt mentions
        package_pattern = r'([a-z][a-z0-9\-_]+)\s*[><=~^]+\s*[\d\.]+'
        for match in re.finditer(package_pattern, content, re.IGNORECASE):
            dependencies.add(match.group(1))
        
        return sorted(list(dependencies))[:20]  # Limit to 20 most relevant
    
    def _detect_primary_language(self, content: str, code_blocks: List[CodeBlock]) -> Optional[str]:
        """Detect the primary programming language."""
        if not code_blocks:
            return None
        
        # Count language occurrences
        lang_counts = {}
        for block in code_blocks:
            lang = block.language.lower()
            if lang not in ['bash', 'shell', 'sh', 'plaintext', 'text']:
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
        
        if not lang_counts:
            return None
        
        # Return most common
        return max(lang_counts.items(), key=lambda x: x[1])[0]
    
    def _extract_url(self, links: List[Link], link_type: str) -> Optional[str]:
        """Extract first URL of a specific type."""
        for link in links:
            if link.link_type == link_type:
                return link.url
        return None
    
    def _has_table_of_contents(self, content: str) -> bool:
        """Check if README has a table of contents."""
        toc_patterns = [
            r'##?\s*table\s+of\s+contents',
            r'##?\s*contents',
            r'##?\s*toc\b',
        ]
        
        for pattern in toc_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _has_section(self, section_type: str, section_names: List[str]) -> bool:
        """Check if a specific section type exists."""
        if section_type not in self.SECTION_PATTERNS:
            return False
        
        pattern = self.SECTION_PATTERNS[section_type]
        
        for name in section_names:
            if re.search(pattern, name):
                return True
        
        return False
    
    def _calculate_completeness(self, metadata: READMEMetadata) -> float:
        """Calculate README completeness score (0-100)."""
        score = 0.0
        max_score = 100.0
        
        # Title (10 points)
        if metadata.title:
            score += 10
        
        # Description (10 points)
        if metadata.description and len(metadata.description) > 20:
            score += 10
        
        # Installation (15 points)
        if metadata.has_installation:
            score += 15
        
        # Usage (15 points)
        if metadata.has_usage:
            score += 15
        
        # Examples/Code (10 points)
        if metadata.has_examples:
            score += 10
        
        # License (10 points)
        if metadata.license or metadata.has_license_section:
            score += 10
        
        # Badges (5 points)
        if len(metadata.badges) > 0:
            score += 5
        
        # Contributing (5 points)
        if metadata.has_contributing:
            score += 5
        
        # Links (5 points)
        if len(metadata.links) >= 3:
            score += 5
        
        # Documentation structure (10 points)
        if len(metadata.sections) >= 4:
            score += 5
        if metadata.table_of_contents:
            score += 5
        
        # Content quality (5 points)
        if metadata.word_count >= 200:
            score += 5
        
        return round(score, 2)
    
    def quality_report(self, metadata: READMEMetadata) -> Dict[str, Any]:
        """Generate a quality report with suggestions."""
        report = {
            'completeness_score': metadata.completeness_score,
            'grade': self._score_to_grade(metadata.completeness_score),
            'strengths': [],
            'missing': [],
            'suggestions': []
        }
        
        # Identify strengths
        if metadata.has_installation:
            report['strengths'].append('Has installation instructions')
        if metadata.has_usage:
            report['strengths'].append('Has usage examples')
        if len(metadata.badges) >= 3:
            report['strengths'].append(f'Good badge coverage ({len(metadata.badges)} badges)')
        if metadata.word_count >= 300:
            report['strengths'].append('Comprehensive documentation')
        if metadata.table_of_contents:
            report['strengths'].append('Includes table of contents')
        
        # Identify missing elements
        if not metadata.title:
            report['missing'].append('Main title')
        if not metadata.description:
            report['missing'].append('Project description')
        if not metadata.has_installation:
            report['missing'].append('Installation section')
        if not metadata.has_usage:
            report['missing'].append('Usage section')
        if not (metadata.license or metadata.has_license_section):
            report['missing'].append('License information')
        if not metadata.has_contributing:
            report['missing'].append('Contributing guidelines')
        if len(metadata.badges) == 0:
            report['missing'].append('Status badges')
        
        # Generate suggestions
        if not metadata.table_of_contents and len(metadata.sections) >= 5:
            report['suggestions'].append('Add a table of contents for better navigation')
        if len(metadata.code_blocks) == 0:
            report['suggestions'].append('Add code examples to illustrate usage')
        if not metadata.repository_url:
            report['suggestions'].append('Add link to source repository')
        if metadata.word_count < 200:
            report['suggestions'].append('Expand documentation with more details')
        if len(metadata.badges) < 3:
            report['suggestions'].append('Consider adding status badges (build, coverage, version)')
        
        return report
    
    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'


def extract_metadata(content: str) -> READMEMetadata:
    """
    Convenience function to extract metadata from README content.
    
    Args:
        content: Raw README markdown content
        
    Returns:
        READMEMetadata object with extracted information
    """
    extractor = MetadataExtractor()
    return extractor.extract(content)


def get_quality_report(content: str) -> Dict[str, Any]:
    """
    Convenience function to get quality report for README.
    
    Args:
        content: Raw README markdown content
        
    Returns:
        Quality report dictionary
    """
    extractor = MetadataExtractor()
    metadata = extractor.extract(content)
    return extractor.quality_report(metadata)
