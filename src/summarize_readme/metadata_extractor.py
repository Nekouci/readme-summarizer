"""
Advanced metadata extraction from README files.

Extracts structured information including badges, licenses, tech stacks, 
dependencies, links, code samples, and more.
"""

import math
import re
from collections import Counter
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict, field

from bs4 import BeautifulSoup


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
    maintainers: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    project_status: Optional[str] = None
    
    # Badges and links
    badges: List[Badge] = field(default_factory=list)
    links: List[Link] = field(default_factory=list)
    project_urls: Dict[str, str] = field(default_factory=dict)
    community_urls: Dict[str, str] = field(default_factory=dict)
    contact_emails: List[str] = field(default_factory=list)
    frontmatter: Dict[str, Any] = field(default_factory=dict)
    open_graph: Dict[str, str] = field(default_factory=dict)
    
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
    has_code_of_conduct: bool = False
    has_changelog: bool = False
    has_security: bool = False
    completeness_score: float = 0.0
    readability_score: float = 0.0
    estimated_read_time_minutes: int = 0
    
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

    PROJECT_URL_HINTS = {
        'issues': r'(?i)issues?|bug\s*report',
        'changelog': r'(?i)changelog|release\s*notes?',
        'contributing': r'(?i)contribut(?:ing|ion)',
        'security': r'(?i)security|vulnerab',
        'discussions': r'(?i)discussion|forum',
        'support': r'(?i)support|help|contact',
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

    STOPWORDS = {
        'the', 'and', 'for', 'with', 'this', 'that', 'from', 'into', 'your', 'you',
        'about', 'project', 'readme', 'using', 'used', 'use', 'are', 'was', 'were',
        'our', 'their', 'have', 'has', 'will', 'can', 'all', 'any', 'not', 'but',
    }
    
    def __init__(self):
        """Initialize the metadata extractor."""
        self.yaml_loader = self._get_yaml_loader()
    
    def extract(self, content: str) -> READMEMetadata:
        """
        Extract comprehensive metadata from README content.
        
        Args:
            content: Raw README markdown content
            
        Returns:
            READMEMetadata object with extracted information
        """
        metadata = READMEMetadata()

        # Extract frontmatter and HTML meta tags first
        metadata.frontmatter = self._extract_frontmatter(content)
        metadata.open_graph = self._extract_open_graph(content)
        
        # Basic metrics
        metadata.line_count = len(content.split('\n'))
        metadata.word_count = len(content.split())
        metadata.estimated_read_time_minutes = max(1, math.ceil(metadata.word_count / 220)) if metadata.word_count else 0
        
        # Extract title and description
        metadata.title, metadata.description = self._extract_title_and_description(content)
        
        # Extract badges
        metadata.badges = self._extract_badges(content)
        
        # Extract links
        metadata.links = self._extract_links(content)
        
        # Extract sections
        metadata.sections = self._extract_sections(content)
        metadata.section_names = self._flatten_section_titles(metadata.sections)
        
        # Extract code blocks
        metadata.code_blocks = self._extract_code_blocks(content)
        
        # Detect technical details
        metadata.license = self._extract_license(content)
        metadata.version = self._extract_version(content)
        metadata.tech_stack = self._extract_tech_stack(content)
        metadata.dependencies = self._extract_dependencies(content)
        metadata.language = self._detect_primary_language(content, metadata.code_blocks)
        metadata.keywords = self._extract_keywords(content, metadata)
        metadata.authors, metadata.maintainers = self._extract_people(metadata.frontmatter, content)
        metadata.project_status = self._extract_project_status(content, metadata.badges)
        metadata.contact_emails = self._extract_contact_emails(content)
        
        # Extract important URLs
        metadata.repository_url = self._extract_url(metadata.links, 'repository')
        metadata.documentation_url = self._extract_url(metadata.links, 'documentation')
        metadata.homepage_url = self._extract_url(metadata.links, 'website')
        metadata.project_urls, metadata.community_urls = self._extract_url_maps(metadata.links, metadata.frontmatter)
        
        # Check for table of contents
        metadata.table_of_contents = self._has_table_of_contents(content)
        
        # Analyze sections
        metadata.has_installation = self._has_section('installation', metadata.section_names)
        metadata.has_usage = self._has_section('usage', metadata.section_names)
        metadata.has_contributing = self._has_section('contributing', metadata.section_names)
        metadata.has_license_section = self._has_section('license', metadata.section_names)
        metadata.has_examples = self._has_section('examples', metadata.section_names) or len(metadata.code_blocks) > 0
        metadata.has_code_of_conduct = self._has_pattern(content, r'(?i)code\s+of\s+conduct')
        metadata.has_changelog = self._has_section('changelog', metadata.section_names) or self._has_pattern(content, r'(?i)changelog|release\s*notes?')
        metadata.has_security = self._has_pattern(content, r'(?i)security|vulnerab(?:ility|ilities)|responsible\s+disclosure')
        metadata.readability_score = self._calculate_readability(content)
        
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

        # Prefer Open Graph title/description if markdown title is missing
        if not title:
            og_title = self._extract_open_graph(content).get('og:title')
            if og_title:
                title = og_title
        
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

        if not description:
            og_description = self._extract_open_graph(content).get('og:description')
            if og_description:
                description = og_description
        
        return title, description
    
    def _extract_badges(self, content: str) -> List[Badge]:
        """Extract all badges from README."""
        badges = []
        seen_images = set()

        linked_badge_pattern = r'\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)'
        for match in re.finditer(linked_badge_pattern, content):
            alt_text = match.group(1)
            image_url = match.group(2)
            link_url = match.group(3)

            if image_url in seen_images:
                continue
            seen_images.add(image_url)

            badge_type = self._classify_badge(alt_text, image_url)
            badges.append(Badge(
                alt_text=alt_text,
                image_url=image_url,
                link_url=link_url,
                badge_type=badge_type
            ))

        standalone_badge_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        for match in re.finditer(standalone_badge_pattern, content):
            alt_text = match.group(1)
            image_url = match.group(2)
            if image_url in seen_images:
                continue
            if 'badge' not in image_url.lower() and 'shields.io' not in image_url.lower():
                continue
            seen_images.add(image_url)

            badge_type = self._classify_badge(alt_text, image_url)
            badges.append(Badge(
                alt_text=alt_text,
                image_url=image_url,
                link_url=None,
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

        # Also detect bare URLs that are not markdown links
        bare_url_pattern = r'(?<!\()https?://[^\s)>]+'
        for match in re.finditer(bare_url_pattern, content):
            url = match.group(0).rstrip('.,;')
            if url in seen_urls:
                continue
            seen_urls.add(url)

            links.append(Link(
                text=self._url_to_label(url),
                url=url,
                link_type=self._classify_link(url, url)
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
        in_code_block = False

        heading_matches: List[Tuple[int, int, str]] = []

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

                heading_matches.append((i, level, title))

        if not heading_matches:
            return sections

        flat_sections: List[Section] = []
        for idx, (line_no, level, title) in enumerate(heading_matches):
            next_line_no = heading_matches[idx + 1][0] if idx + 1 < len(heading_matches) else len(lines)
            section_content = '\n'.join(lines[line_no + 1:next_line_no]).strip()
            flat_sections.append(Section(
                title=title,
                level=level,
                content=section_content
            ))

        # Build hierarchy by heading levels
        stack: List[Tuple[int, Section]] = []
        for section in flat_sections:
            while stack and stack[-1][0] >= section.level:
                stack.pop()

            if stack:
                stack[-1][1].subsections.append(section)
            else:
                sections.append(section)

            stack.append((section.level, section))
        
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

        install_patterns = [
            r'pip install\s+([^\n]+)',
            r'poetry add\s+([^\n]+)',
            r'npm install\s+([^\n]+)',
            r'yarn add\s+([^\n]+)',
            r'pnpm add\s+([^\n]+)',
            r'cargo add\s+([^\n]+)',
            r'go get\s+([^\n]+)',
        ]

        for pattern in install_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                deps = re.split(r'\s+', match.group(1).strip())
                for dep in deps:
                    clean = dep.strip().strip('"\' ,')
                    if not clean or clean.startswith('-'):
                        continue
                    dependencies.add(clean)

        package_pattern = r'([a-z][a-z0-9\-_\.]+)\s*[><=~^]+\s*[\d\.]+'
        for match in re.finditer(package_pattern, content, re.IGNORECASE):
            dependencies.add(match.group(1))
        
        return sorted(list(dependencies))[:20]  # Limit to 20 most relevant
    
    def _detect_primary_language(self, content: str, code_blocks: List[CodeBlock]) -> Optional[str]:
        """Detect the primary programming language."""
        if not code_blocks:
            return None

        aliases = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'shell': 'bash',
            'sh': 'bash',
            'yml': 'yaml',
        }

        # Count language occurrences
        lang_counts = {}
        for block in code_blocks:
            lang = block.language.lower()
            lang = aliases.get(lang, lang)
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

        # Community health (10 points)
        if metadata.has_code_of_conduct:
            score += 3
        if metadata.has_security:
            score += 4
        if metadata.has_changelog:
            score += 3
        
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

        return round(min(100.0, score), 2)
    
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
        if metadata.has_security:
            report['strengths'].append('Includes security guidance')
        if metadata.has_code_of_conduct:
            report['strengths'].append('Includes code of conduct information')
        
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
        if not metadata.has_security:
            report['missing'].append('Security policy or disclosure process')
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
        if not metadata.project_urls.get('issues'):
            report['suggestions'].append('Add an issues/bug reporting link')
        if metadata.readability_score and metadata.readability_score < 45:
            report['suggestions'].append('Simplify long sentences to improve readability')
        
        return report

    def _flatten_section_titles(self, sections: List[Section]) -> List[str]:
        """Flatten nested section titles into a single list."""
        titles = []
        for section in sections:
            titles.append(section.title)
            if section.subsections:
                titles.extend(self._flatten_section_titles(section.subsections))
        return titles

    def _extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter when present at top of README."""
        match = re.match(r'^\s*---\s*\n(.*?)\n---\s*(?:\n|$)', content, re.DOTALL)
        if not match:
            return {}

        raw_frontmatter = match.group(1).strip()
        if not raw_frontmatter:
            return {}

        if self.yaml_loader:
            try:
                parsed = self.yaml_loader(raw_frontmatter)
                return parsed if isinstance(parsed, dict) else {}
            except Exception:
                pass

        # Lightweight fallback parser for simple key/value YAML
        data: Dict[str, Any] = {}
        current_key: Optional[str] = None
        for line in raw_frontmatter.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue

            if stripped.startswith('- ') and current_key:
                existing = data.get(current_key)
                if not isinstance(existing, list):
                    existing = []
                existing.append(stripped[2:].strip().strip('"\''))
                data[current_key] = existing
                continue

            if ':' in stripped:
                key, value = stripped.split(':', 1)
                key = key.strip()
                value = value.strip()
                current_key = key

                if not value:
                    data[key] = []
                elif value.lower() in {'true', 'false'}:
                    data[key] = value.lower() == 'true'
                else:
                    data[key] = value.strip('"\'')

        return data

    def _extract_open_graph(self, content: str) -> Dict[str, str]:
        """Extract Open Graph / Twitter card metadata from embedded HTML."""
        metadata: Dict[str, str] = {}
        soup = BeautifulSoup(content, 'html.parser')

        for tag in soup.find_all('meta'):
            key = tag.get('property') or tag.get('name')
            value = tag.get('content')
            if not key or not value:
                continue

            if isinstance(key, list):
                key = key[0] if key else ''
            if isinstance(value, list):
                value = value[0] if value else ''
            if not isinstance(key, str) or not isinstance(value, str):
                continue

            key_lower = key.lower().strip()
            if key_lower.startswith('og:') or key_lower.startswith('twitter:'):
                metadata[key_lower] = value.strip()

        return metadata

    def _extract_url_maps(self, links: List[Link], frontmatter: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Extract project and community URL maps from links and frontmatter."""
        project_urls: Dict[str, str] = {}
        community_urls: Dict[str, str] = {}

        for link in links:
            combined = f"{link.text} {link.url}"

            if link.link_type == 'repository':
                existing_repo = project_urls.get('repository')
                if not existing_repo:
                    project_urls['repository'] = link.url
                elif self._is_repository_root_url(link.url) and not self._is_repository_root_url(existing_repo):
                    project_urls['repository'] = link.url
            elif link.link_type == 'documentation' and 'documentation' not in project_urls:
                project_urls['documentation'] = link.url
            elif link.link_type == 'website' and 'homepage' not in project_urls:
                project_urls['homepage'] = link.url

            for label, pattern in self.PROJECT_URL_HINTS.items():
                if re.search(pattern, combined):
                    target = community_urls if label in {'issues', 'discussions', 'support'} else project_urls
                    if label not in target:
                        target[label] = link.url

        # Frontmatter convention support
        if isinstance(frontmatter.get('homepage'), str):
            project_urls['homepage'] = frontmatter['homepage']
        if isinstance(frontmatter.get('repository'), str):
            project_urls['repository'] = frontmatter['repository']
        if isinstance(frontmatter.get('documentation'), str):
            project_urls['documentation'] = frontmatter['documentation']

        return project_urls, community_urls

    def _is_repository_root_url(self, url: str) -> bool:
        """Return True when URL appears to be a repo root and not a subpage."""
        return not re.search(r'/(issues|pulls|security|wiki|releases|actions|tree|blob|discussions)(/|$)', url, re.IGNORECASE)

    def _extract_contact_emails(self, content: str) -> List[str]:
        """Extract contact emails mentioned in README."""
        emails = set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', content))
        return sorted(emails)

    def _extract_people(self, frontmatter: Dict[str, Any], content: str) -> Tuple[List[str], List[str]]:
        """Extract authors and maintainers from frontmatter and markdown sections."""
        authors: Set[str] = set()
        maintainers: Set[str] = set()

        for key in ('author', 'authors'):
            value = frontmatter.get(key)
            if isinstance(value, str):
                authors.add(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        authors.add(item)

        for key in ('maintainer', 'maintainers'):
            value = frontmatter.get(key)
            if isinstance(value, str):
                maintainers.add(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        maintainers.add(item)

        heading_based = re.findall(
            r'(?ims)^#{2,3}\s*(authors?|maintainers?|team)\s*\n(.*?)(?=^#{1,6}\s|\Z)',
            content
        )
        for heading, body in heading_based:
            names = re.findall(r'(?:^|\n)\s*[-*]\s+([^\n]+)', body)
            if not names:
                names = re.findall(r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b', body)

            if re.search(r'(?i)author', heading):
                authors.update(n.strip() for n in names)
            else:
                maintainers.update(n.strip() for n in names)

        return sorted(authors), sorted(maintainers)

    def _extract_keywords(self, content: str, metadata: READMEMetadata) -> List[str]:
        """Extract lightweight keyword signals from title, sections, and tech stack."""
        tokens = []
        if metadata.title:
            tokens.extend(re.findall(r'\b[a-zA-Z][a-zA-Z0-9\-]{2,}\b', metadata.title.lower()))

        for section_name in metadata.section_names:
            tokens.extend(re.findall(r'\b[a-zA-Z][a-zA-Z0-9\-]{2,}\b', section_name.lower()))

        for tech in metadata.tech_stack:
            tokens.append(tech.lower())

        words = [w for w in tokens if w not in self.STOPWORDS]
        counts = Counter(words)
        return [word for word, _ in counts.most_common(15)]

    def _extract_project_status(self, content: str, badges: List[Badge]) -> Optional[str]:
        """Infer rough project status from badges and textual signals."""
        combined = content.lower() + ' ' + ' '.join((b.alt_text + ' ' + b.image_url).lower() for b in badges)

        if re.search(r'\b(deprecated|unmaintained|archived)\b', combined):
            return 'deprecated'
        if re.search(r'\b(alpha|experimental)\b', combined):
            return 'alpha'
        if re.search(r'\b(beta|preview|release\s*candidate|rc\b)\b', combined):
            return 'beta'
        if re.search(r'\b(stable|production\s*ready|maintained)\b', combined):
            return 'stable'

        return None

    def _calculate_readability(self, content: str) -> float:
        """Compute an approximate Flesch Reading Ease score (0-100)."""
        cleaned = re.sub(r'```.*?```', ' ', content, flags=re.DOTALL)
        cleaned = re.sub(r'`[^`]+`', ' ', cleaned)
        cleaned = re.sub(r'\[[^\]]+\]\([^)]+\)', ' ', cleaned)

        sentences = max(1, len(re.findall(r'[.!?]+', cleaned)))
        words = re.findall(r"\b[a-zA-Z']+\b", cleaned)
        word_count = max(1, len(words))

        syllables = sum(self._count_syllables(word) for word in words) or 1
        score = 206.835 - 1.015 * (word_count / sentences) - 84.6 * (syllables / word_count)
        return round(max(0.0, min(100.0, score)), 2)

    def _count_syllables(self, word: str) -> int:
        """Rough syllable estimator for readability scoring."""
        word = word.lower().strip()
        if not word:
            return 1

        vowels = re.findall(r'[aeiouy]+', word)
        count = len(vowels)
        if word.endswith('e') and count > 1:
            count -= 1
        return max(1, count)

    def _get_yaml_loader(self):
        """Load PyYAML parser lazily when available."""
        try:
            import yaml  # type: ignore[import-not-found]
            return yaml.safe_load
        except Exception:
            return None

    def _url_to_label(self, url: str) -> str:
        """Create a compact label from URL for bare-link extraction."""
        compact = re.sub(r'^https?://', '', url)
        return compact[:50] + ('...' if len(compact) > 50 else '')

    def _has_pattern(self, content: str, pattern: str) -> bool:
        """Case-insensitive helper for feature checks."""
        return bool(re.search(pattern, content, re.IGNORECASE))
    
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
