"""
Advanced input resolver and repository fetcher for README Summarizer.

Supports multiple input formats:
- Local file paths: README.md, ./docs/README.md
- Direct URLs: https://example.com/readme.md
- GitHub repo URLs: https://github.com/owner/repo
- GitHub shorthand: owner/repo, owner/repo@branch
- Raw GitHub URLs: https://raw.githubusercontent.com/owner/repo/main/README.md
"""

import re
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse
import base64

import requests
from rich.console import Console


console = Console()


class InputType(str, Enum):
    """Types of input sources."""
    LOCAL_FILE = "local_file"
    DIRECT_URL = "direct_url"
    GITHUB_REPO = "github_repo"
    GITHUB_SHORTHAND = "github_shorthand"
    GITHUB_RAW_URL = "github_raw_url"


class InputResolver:
    """
    Resolves various input formats to README content.
    
    Supports:
    - Local files
    - Direct URLs
    - GitHub repositories (with automatic README detection)
    - GitHub shorthand notation (owner/repo)
    """
    
    # GitHub API base URL (no auth required for public repos)
    GITHUB_API_BASE = "https://api.github.com"
    
    # Common README filenames to try
    README_VARIANTS = [
        "README.md",
        "readme.md",
        "README",
        "readme",
        "README.markdown",
        "readme.markdown",
        "README.rst",
        "readme.rst",
        "README.txt",
        "readme.txt",
    ]
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.session = requests.Session()
        # Set User-Agent for GitHub API
        self.session.headers.update({
            "User-Agent": "README-Summarizer-CLI/0.1.0",
            "Accept": "application/vnd.github.v3+json",
        })
    
    def _convert_blob_to_raw_url(self, url: str) -> str:
        """
        Convert GitHub blob URL to raw content URL.
        
        Example:
            Input:  https://github.com/owner/repo/blob/main/README.md
            Output: https://raw.githubusercontent.com/owner/repo/main/README.md
        """
        # Pattern to match GitHub blob URLs
        blob_pattern = r"github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)"
        match = re.match(r"https?://" + blob_pattern, url)
        
        if match:
            owner, repo, branch, file_path = match.groups()
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
            if self.verbose:
                console.print(f"[yellow]ℹ[/yellow] Converted blob URL to raw URL")
            return raw_url
        
        return url
    
    def detect_input_type(self, source: str) -> InputType:
        """
        Detect the type of input source.
        
        Args:
            source: Input string (file path, URL, repo, etc.)
        
        Returns:
            InputType enum value
        """
        # Check if it's a local file
        if Path(source).exists():
            return InputType.LOCAL_FILE
        
        # Check for GitHub shorthand (owner/repo or owner/repo@branch)
        if self._is_github_shorthand(source):
            return InputType.GITHUB_SHORTHAND
        
        # Check if it's a URL
        if source.startswith(("http://", "https://")):
            # Check for GitHub raw URL
            if "raw.githubusercontent.com" in source:
                return InputType.GITHUB_RAW_URL
            # Check for GitHub repo URL
            elif "github.com" in source and "/blob/" not in source:
                return InputType.GITHUB_REPO
            else:
                return InputType.DIRECT_URL
        
        # Default to treating as file path
        return InputType.LOCAL_FILE
    
    def resolve(self, source: str) -> Tuple[str, Dict[str, Any]]:
        """
        Resolve input source to README content.
        
        Args:
            source: Input string (file path, URL, repo, etc.)
        
        Returns:
            Tuple of (content, metadata dict)
        
        Raises:
            Exception: If content cannot be fetched
        """
        # Convert GitHub blob URLs to raw URLs to avoid rate limiting
        if "github.com" in source and "/blob/" in source:
            source = self._convert_blob_to_raw_url(source)
        
        input_type = self.detect_input_type(source)
        
        if self.verbose:
            console.print(f"[cyan]Detected input type:[/cyan] {input_type.value}")
        
        if input_type == InputType.LOCAL_FILE:
            return self._resolve_local_file(source)
        
        elif input_type == InputType.DIRECT_URL:
            return self._resolve_direct_url(source)
        
        elif input_type == InputType.GITHUB_RAW_URL:
            return self._resolve_github_raw_url(source)
        
        elif input_type == InputType.GITHUB_REPO:
            return self._resolve_github_repo_url(source)
        
        elif input_type == InputType.GITHUB_SHORTHAND:
            return self._resolve_github_shorthand(source)
        
        else:
            raise ValueError(f"Unsupported input type: {input_type}")
    
    def _resolve_local_file(self, file_path: str) -> Tuple[str, Dict]:
        """Read content from a local file."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Try with different encoding
            content = path.read_text(encoding="latin-1")
        
        metadata = {
            "source": str(path.absolute()),
            "type": "local_file",
            "size": path.stat().st_size,
            "name": path.name,
        }
        
        if self.verbose:
            console.print(f"[green]✓[/green] Read {len(content)} bytes from {path.name}")
        
        return content, metadata
    
    def _resolve_direct_url(self, url: str) -> Tuple[str, Dict]:
        """Fetch content from a direct URL."""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            content = response.text
            
            metadata = {
                "source": url,
                "type": "direct_url",
                "size": len(content),
                "status_code": response.status_code,
            }
            
            if self.verbose:
                console.print(f"[green]✓[/green] Fetched {len(content)} bytes from URL")
            
            return content, metadata
        
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch URL {url}: {e}")
    
    def _resolve_github_raw_url(self, url: str) -> Tuple[str, Dict]:
        """Fetch content from a GitHub raw URL."""
        # Extract repo info for metadata
        pattern = r"raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.+)"
        match = re.search(pattern, url)
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            content = response.text
            
            metadata = {
                "source": url,
                "type": "github_raw",
                "size": len(content),
            }
            
            if match:
                metadata.update({
                    "owner": match.group(1),
                    "repo": match.group(2),
                    "branch": match.group(3),
                    "file": match.group(4),
                })
            
            if self.verbose:
                console.print(f"[green]✓[/green] Fetched {len(content)} bytes from GitHub raw URL")
            
            return content, metadata
        
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch from GitHub raw URL: {e}")
    
    def _resolve_github_repo_url(self, url: str) -> Tuple[str, Dict]:
        """Fetch README from a GitHub repository URL using GitHub API."""
        # Extract owner and repo from URL
        pattern = r"github\.com/([^/]+)/([^/]+)"
        match = re.search(pattern, url)
        
        if not match:
            raise ValueError(f"Invalid GitHub URL: {url}")
        
        owner = match.group(1)
        repo = match.group(2).replace(".git", "")
        
        # Extract branch if specified in URL
        branch = None
        branch_pattern = r"/tree/([^/]+)"
        branch_match = re.search(branch_pattern, url)
        if branch_match:
            branch = branch_match.group(1)
        
        return self._fetch_github_readme(owner, repo, branch)
    
    def _resolve_github_shorthand(self, shorthand: str) -> Tuple[str, Dict]:
        """
        Fetch README from GitHub shorthand notation.
        
        Supports:
        - owner/repo
        - owner/repo@branch
        """
        # Parse shorthand
        if "@" in shorthand:
            repo_part, branch = shorthand.split("@", 1)
        else:
            repo_part, branch = shorthand, None
        
        parts = repo_part.split("/")
        if len(parts) != 2:
            raise ValueError(
                f"Invalid GitHub shorthand: {shorthand}. "
                "Expected format: owner/repo or owner/repo@branch"
            )
        
        owner, repo = parts
        
        return self._fetch_github_readme(owner, repo, branch)
    
    def _fetch_github_readme(
        self,
        owner: str,
        repo: str,
        branch: Optional[str] = None,
    ) -> Tuple[str, Dict]:
        """
        Fetch README from GitHub repository using GitHub API.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Optional branch name (uses default branch if not specified)
        
        Returns:
            Tuple of (content, metadata)
        
        Raises:
            Exception: If README cannot be fetched
        """
        if self.verbose:
            console.print(f"[cyan]Fetching README from GitHub:[/cyan] {owner}/{repo}")
        
        # Try using GitHub API first (automatically finds README)
        try:
            api_url = f"{self.GITHUB_API_BASE}/repos/{owner}/{repo}/readme"
            
            # Add branch parameter if specified
            params = {}
            if branch:
                params["ref"] = branch
            
            response = self.session.get(api_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # Decode base64 content
            content = base64.b64decode(data["content"]).decode("utf-8")
            
            metadata = {
                "source": f"https://github.com/{owner}/{repo}",
                "type": "github_repo",
                "owner": owner,
                "repo": repo,
                "branch": branch or data.get("ref", "default"),
                "file": data.get("name", "README.md"),
                "size": len(content),
                "download_url": data.get("download_url"),
                "html_url": data.get("html_url"),
            }
            
            if self.verbose:
                console.print(
                    f"[green]✓[/green] Fetched README.md ({len(content)} bytes) "
                    f"from {owner}/{repo}"
                )
            
            return content, metadata
        
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                # README not found via API, try manual detection
                if self.verbose:
                    console.print("[yellow]README not found via API, trying manual detection...[/yellow]")
                return self._fetch_github_readme_fallback(owner, repo, branch)
            else:
                raise Exception(f"GitHub API error: {e}")
        
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch from GitHub API: {e}")
    
    def _fetch_github_readme_fallback(
        self,
        owner: str,
        repo: str,
        branch: Optional[str] = None,
    ) -> Tuple[str, Dict]:
        """
        Fallback method to fetch README by trying multiple filenames.
        
        Uses raw.githubusercontent.com URLs to try different README variants.
        """
        # If no branch specified, try common default branches
        branches_to_try = [branch] if branch else ["main", "master"]
        
        for branch_name in branches_to_try:
            for readme_variant in self.README_VARIANTS:
                raw_url = (
                    f"https://raw.githubusercontent.com/{owner}/{repo}/"
                    f"{branch_name}/{readme_variant}"
                )
                
                try:
                    response = self.session.get(raw_url, timeout=10)
                    if response.status_code == 200:
                        content = response.text
                        
                        metadata = {
                            "source": f"https://github.com/{owner}/{repo}",
                            "type": "github_repo",
                            "owner": owner,
                            "repo": repo,
                            "branch": branch_name,
                            "file": readme_variant,
                            "size": len(content),
                            "download_url": raw_url,
                        }
                        
                        if self.verbose:
                            console.print(
                                f"[green]✓[/green] Found {readme_variant} "
                                f"on branch {branch_name}"
                            )
                        
                        return content, metadata
                
                except requests.RequestException:
                    continue
        
        # If we get here, no README was found
        raise FileNotFoundError(
            f"No README file found in repository {owner}/{repo}. "
            f"Tried branches: {', '.join(branches_to_try)}"
        )
    
    def _is_github_shorthand(self, source: str) -> bool:
        """
        Check if source matches GitHub shorthand pattern.
        
        Pattern: owner/repo or owner/repo@branch
        """
        # Should not contain :// (would be a URL)
        if "://" in source:
            return False
        
        # Should not be a file path
        if source.startswith(("./", "../", "/", "\\")) or ":" in source[:2]:
            return False
        
        # Check pattern
        pattern = r"^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+(@[a-zA-Z0-9_.-]+)?$"
        return bool(re.match(pattern, source))
    
    def resolve_with_detection(
        self,
        source: str,
        auto_select_strategy: str = "root",
        interactive: bool = False,
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Resolve input source with multi-file detection support.
        
        This method uses the READMEDetector to find all README files in a directory
        or repository, then resolves each one.
        
        Args:
            source: Input string (directory path, GitHub repo, etc.)
            auto_select_strategy: Strategy for auto-selection ('root', 'all', 'docs', 'priority')
            interactive: Whether to use interactive selection
        
        Returns:
            List of tuples (content, metadata) for each resolved README
        
        Raises:
            Exception: If content cannot be fetched
        """
        from .readme_detector import READMEDetector
        
        detector = READMEDetector(verbose=self.verbose)
        readme_files = []
        
        # Check if it's a local directory
        if Path(source).exists() and Path(source).is_dir():
            readme_files = detector.scan_local_directory(Path(source))
        
        # Check for GitHub shorthand
        elif self._is_github_shorthand(source):
            parts = source.split("@")
            repo_part = parts[0]
            branch = parts[1] if len(parts) > 1 else None
            owner, repo = repo_part.split("/")
            
            readme_files = detector.scan_github_repo(owner, repo, branch)
        
        else:
            # Fall back to single file resolution
            content, metadata = self.resolve(source)
            return [(content, metadata)]
        
        if not readme_files:
            raise FileNotFoundError(f"No README files found in {source}")
        
        # Select files
        if interactive:
            selected_files = detector.interactive_select(readme_files)
        else:
            selected_files = detector.auto_select(readme_files, strategy=auto_select_strategy)
        
        if not selected_files:
            raise ValueError("No README files selected")
        
        # Resolve each selected file
        results = []
        for readme_file in selected_files:
            if readme_file.is_local:
                content, metadata = self._resolve_local_file(readme_file.path)
            else:
                # For remote files (GitHub), fetch from URL
                content, metadata = self._resolve_direct_url(readme_file.path)
            
            # Add detector metadata
            metadata["detector"] = {
                "relative_path": readme_file.relative_path,
                "priority": readme_file.priority.name,
                "depth": readme_file.depth,
                "language": readme_file.language,
            }
            
            results.append((content, metadata))
        
        return results
