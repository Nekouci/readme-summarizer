"""
Advanced README File Detector & Selector for README Summarizer.

This module provides intelligent discovery and selection of README files from:
- Local directories (recursive scan)
- GitHub repositories (via GitHub API)
- Multiple README detection (root, docs, language-specific, etc.)
- Interactive selection interface
"""

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.tree import Tree


console = Console()


class READMEPriority(int, Enum):
    """Priority levels for README files."""
    ROOT = 1           # Root-level README (highest priority)
    DOCS = 2          # Documentation directory README
    LANG_SPECIFIC = 3 # Language-specific README (README.fr.md, etc.)
    SUBDIR = 4        # Subdirectory README
    OTHER = 5         # Other README files


@dataclass
class READMEFile:
    """Represents a discovered README file with metadata."""
    path: str                    # Full path or URL
    name: str                    # File name
    relative_path: str           # Relative path from root
    priority: READMEPriority     # Priority level
    size: Optional[int] = None   # File size in bytes
    depth: int = 0               # Directory depth
    is_local: bool = True        # Local file vs remote
    language: Optional[str] = None  # Language code if language-specific
    
    def __repr__(self) -> str:
        return f"READMEFile(path={self.relative_path}, priority={self.priority.name})"
    
    @property
    def display_name(self) -> str:
        """Get a human-readable display name."""
        parts = []
        if self.relative_path == self.name:
            parts.append(f"📌 {self.name} (root)")
        else:
            parts.append(f"📄 {self.relative_path}")
        
        if self.language:
            parts.append(f"[{self.language}]")
        
        if self.size:
            size_kb = self.size / 1024
            parts.append(f"({size_kb:.1f} KB)")
        
        return " ".join(parts)


class READMEDetector:
    """
    Detects and manages README files from various sources.
    
    Features:
    - Recursive directory scanning
    - GitHub repository tree scanning
    - Intelligent prioritization
    - Interactive selection interface
    - Multiple file format support
    """
    
    # README filename patterns (case-insensitive)
    README_PATTERNS = [
        r"^readme\.md$",
        r"^readme\.markdown$",
        r"^readme\.rst$",
        r"^readme\.txt$",
        r"^readme$",
        r"^readme\.[a-z]{2}\.md$",      # Language-specific (readme.fr.md)
        r"^readme\.[a-z]{2}-[a-z]{2}\.md$",  # Locale-specific (readme.en-us.md)
    ]
    
    # Priority patterns for directory paths
    DOCS_DIRS = ["docs", "doc", "documentation", ".github"]
    EXCLUDE_DIRS = [
        "__pycache__", "node_modules", ".git", ".venv", "venv",
        "build", "dist", ".egg-info", "htmlcov", ".pytest_cache",
        ".mypy_cache", ".tox", "site-packages"
    ]
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "README-Summarizer-CLI/0.2.0",
            "Accept": "application/vnd.github.v3+json",
        })
    
    def is_readme_file(self, filename: str) -> bool:
        """Check if filename matches README patterns."""
        filename_lower = filename.lower()
        return any(re.match(pattern, filename_lower) for pattern in self.README_PATTERNS)
    
    def detect_priority(self, relative_path: str, depth: int) -> READMEPriority:
        """Determine the priority of a README file based on its location."""
        path_lower = relative_path.lower()
        filename = Path(relative_path).name.lower()
        
        # Root-level README
        if depth == 0 or "/" not in relative_path and "\\" not in relative_path:
            return READMEPriority.ROOT
        
        # Documentation directory README
        path_parts = relative_path.replace("\\", "/").split("/")
        if any(part.lower() in self.DOCS_DIRS for part in path_parts):
            return READMEPriority.DOCS
        
        # Language-specific README
        if re.match(r"readme\.[a-z]{2}(-[a-z]{2})?\.md$", filename):
            return READMEPriority.LANG_SPECIFIC
        
        # Subdirectory README
        if depth > 0:
            return READMEPriority.SUBDIR
        
        return READMEPriority.OTHER
    
    def extract_language_code(self, filename: str) -> Optional[str]:
        """Extract language code from filename (e.g., README.fr.md -> 'fr')."""
        match = re.match(r"readme\.([a-z]{2}(-[a-z]{2})?)\.md$", filename.lower())
        if match:
            return match.group(1)
        return None
    
    def scan_local_directory(
        self,
        directory: Path,
        max_depth: int = 10,
        recursive: bool = True
    ) -> List[READMEFile]:
        """
        Scan a local directory for README files.
        
        Args:
            directory: Directory path to scan
            max_depth: Maximum recursion depth
            recursive: Whether to scan recursively
        
        Returns:
            List of discovered README files with metadata
        """
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        if not directory.is_dir():
            raise ValueError(f"Not a directory: {directory}")
        
        readme_files: List[READMEFile] = []
        directory = directory.resolve()
        
        if self.verbose:
            console.print(f"[cyan]Scanning directory:[/cyan] {directory}")
        
        def scan_dir(path: Path, depth: int = 0):
            """Recursive directory scanner."""
            if depth > max_depth:
                return
            
            try:
                for item in path.iterdir():
                    # Skip excluded directories
                    if item.is_dir():
                        if item.name in self.EXCLUDE_DIRS:
                            continue
                        if recursive:
                            scan_dir(item, depth + 1)
                    
                    # Check if it's a README file
                    elif item.is_file() and self.is_readme_file(item.name):
                        relative_path = str(item.relative_to(directory))
                        priority = self.detect_priority(relative_path, depth)
                        language = self.extract_language_code(item.name)
                        
                        readme_files.append(READMEFile(
                            path=str(item),
                            name=item.name,
                            relative_path=relative_path,
                            priority=priority,
                            size=item.stat().st_size,
                            depth=depth,
                            is_local=True,
                            language=language,
                        ))
            except PermissionError:
                if self.verbose:
                    console.print(f"[yellow]⚠ Permission denied:[/yellow] {path}")
        
        scan_dir(directory)
        
        # Sort by priority, then by depth, then by name
        readme_files.sort(key=lambda x: (x.priority.value, x.depth, x.relative_path))
        
        if self.verbose:
            console.print(f"[green]✓[/green] Found {len(readme_files)} README file(s)")
        
        return readme_files
    
    def scan_github_repo(
        self,
        owner: str,
        repo: str,
        branch: Optional[str] = None
    ) -> List[READMEFile]:
        """
        Scan a GitHub repository for README files using GitHub API.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name (optional, uses default branch if not specified)
        
        Returns:
            List of discovered README files with metadata
        """
        if self.verbose:
            console.print(f"[cyan]Scanning GitHub repo:[/cyan] {owner}/{repo}")
        
        # Get repository info to determine default branch
        repo_url = f"https://api.github.com/repos/{owner}/{repo}"
        try:
            repo_response = self.session.get(repo_url, timeout=15)
            repo_response.raise_for_status()
            repo_data = repo_response.json()
            
            if branch is None:
                branch = repo_data.get("default_branch", "main")
            
            if self.verbose:
                console.print(f"[cyan]Using branch:[/cyan] {branch}")
        
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch repository info: {e}")
        
        # Get repository tree (recursive)
        tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        
        try:
            tree_response = self.session.get(tree_url, timeout=20)
            tree_response.raise_for_status()
            tree_data = tree_response.json()
        
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch repository tree: {e}")
        
        readme_files: List[READMEFile] = []
        
        # Parse tree and find README files
        for item in tree_data.get("tree", []):
            if item["type"] != "blob":  # Only files, not directories
                continue
            
            file_path = item["path"]
            filename = Path(file_path).name
            
            if self.is_readme_file(filename):
                depth = file_path.count("/")
                priority = self.detect_priority(file_path, depth)
                language = self.extract_language_code(filename)
                
                # Construct raw URL for direct access
                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
                
                readme_files.append(READMEFile(
                    path=raw_url,
                    name=filename,
                    relative_path=file_path,
                    priority=priority,
                    size=item.get("size"),
                    depth=depth,
                    is_local=False,
                    language=language,
                ))
        
        # Sort by priority, then by depth, then by name
        readme_files.sort(key=lambda x: (x.priority.value, x.depth, x.relative_path))
        
        if self.verbose:
            console.print(f"[green]✓[/green] Found {len(readme_files)} README file(s) in repository")
        
        return readme_files
    
    def display_readme_list(
        self,
        readme_files: List[READMEFile],
        show_indices: bool = True
    ) -> None:
        """
        Display a formatted list of README files.
        
        Args:
            readme_files: List of README files to display
            show_indices: Whether to show selection indices
        """
        if not readme_files:
            console.print("[yellow]No README files found.[/yellow]")
            return
        
        table = Table(
            title="📚 Discovered README Files",
            show_header=True,
            header_style="bold cyan",
            border_style="blue",
        )
        
        if show_indices:
            table.add_column("#", style="dim", width=4)
        
        table.add_column("File", style="white", no_wrap=False)
        table.add_column ("Priority", style="magenta", width=12)
        table.add_column("Size", style="green", width=10, justify="right")
        
        for idx, readme in enumerate(readme_files, start=1):
            size_str = f"{readme.size / 1024:.1f} KB" if readme.size else "N/A"
            priority_str = readme.priority.name.title()
            
            # Add visual indicators
            if readme.priority == READMEPriority.ROOT:
                priority_str = f"⭐ {priority_str}"
            elif readme.priority == READMEPriority.DOCS:
                priority_str = f"📖 {priority_str}"
            elif readme.language:
                priority_str = f"🌐 {priority_str}"
            
            row = [readme.display_name, priority_str, size_str]
            if show_indices:
                row.insert(0, str(idx))
            
            table.add_row(*row)
        
        console.print(table)
    
    def display_readme_tree(self, readme_files: List[READMEFile]) -> None:
        """Display README files as a tree structure."""
        tree = Tree("📂 Repository Structure")
        
        # Group by directory
        dir_trees: Dict[str, Tree] = {"": tree}
        
        for readme in readme_files:
            parts = readme.relative_path.replace("\\", "/").split("/")
            
            # Build directory tree
            current_path = ""
            for i, part in enumerate(parts[:-1]):
                parent_path = current_path
                current_path = f"{current_path}/{part}" if current_path else part
                
                if current_path not in dir_trees:
                    parent_tree = dir_trees.get(parent_path, tree)
                    dir_trees[current_path] = parent_tree.add(f"📁 {part}")
            
            # Add file to tree
            dir_path = "/".join(parts[:-1]) if len(parts) > 1 else ""
            parent_tree = dir_trees.get(dir_path, tree)
            
            icon = "⭐" if readme.priority == READMEPriority.ROOT else "📄"
            parent_tree.add(f"{icon} {readme.name}")
        
        console.print(tree)
    
    def interactive_select(
        self,
        readme_files: List[READMEFile],
        allow_multiple: bool = True
    ) -> List[READMEFile]:
        """
        Interactive selection interface for README files.
        
        Args:
            readme_files: List of README files to choose from
            allow_multiple: Allow selecting multiple files
        
        Returns:
            List of selected README files
        """
        if not readme_files:
            console.print("[yellow]No README files to select.[/yellow]")
            return []
        
        # Display files
        console.print()
        self.display_readme_list(readme_files, show_indices=True)
        console.print()
        
        # Single file - auto-select with confirmation
        if len(readme_files) == 1:
            if Confirm.ask(f"Process this README file?", default=True):
                return [readme_files[0]]
            return []
        
        # Multiple files - interactive selection
        console.print("[bold]Selection Options:[/bold]")
        console.print("  • Enter [cyan]numbers[/cyan] (e.g., 1,3,5 or 1-3)")
        console.print("  • Enter [cyan]'all'[/cyan] to select all files")
        console.print("  • Enter [cyan]'root'[/cyan] for root README only")
        console.print("  • Press [cyan]Enter[/cyan] for default (root + docs)")
        console.print()
        
        while True:
            selection = Prompt.ask(
                "Select README file(s)",
                default="root"
            ).strip().lower()
            
            try:
                if selection == "all":
                    return readme_files
                
                elif selection == "root":
                    return [f for f in readme_files if f.priority == READMEPriority.ROOT]
                
                elif selection == "":
                    # Default: root + docs
                    return [
                        f for f in readme_files
                        if f.priority in [READMEPriority.ROOT, READMEPriority.DOCS]
                    ]
                
                else:
                    # Parse number selection
                    selected_indices = self._parse_selection(selection, len(readme_files))
                    return [readme_files[i] for i in selected_indices]
            
            except ValueError as e:
                console.print(f"[red]Invalid selection:[/red] {e}")
                console.print("Please try again.")
    
    def _parse_selection(self, selection: str, max_index: int) -> List[int]:
        """
        Parse selection string into list of indices.
        
        Supports:
        - Individual numbers: "1,3,5"
        - Ranges: "1-3"
        - Mixed: "1,3-5,7"
        """
        indices = set()
        
        parts = selection.split(",")
        for part in parts:
            part = part.strip()
            
            if "-" in part:
                # Range
                start, end = part.split("-", 1)
                start_idx = int(start.strip()) - 1
                end_idx = int(end.strip()) - 1
                
                if start_idx < 0 or end_idx >= max_index or start_idx > end_idx:
                    raise ValueError(f"Invalid range: {part}")
                
                indices.update(range(start_idx, end_idx + 1))
            
            else:
                # Single number
                idx = int(part) - 1
                if idx < 0 or idx >= max_index:
                    raise ValueError(f"Index out of range: {part}")
                indices.add(idx)
        
        return sorted(list(indices))
    
    def auto_select(
        self,
        readme_files: List[READMEFile],
        strategy: str = "root"
    ) -> List[READMEFile]:
        """
        Automatic selection of README files without interaction.
        
        Args:
            readme_files: List of README files
            strategy: Selection strategy:
                - "root": Root README only (default)
                - "all": All README files
                - "docs": Root + documentation READMEs
                - "priority": By priority (root > docs > others)
        
        Returns:
            List of selected README files
        """
        if not readme_files:
            return []
        
        if strategy == "all":
            return readme_files
        
        elif strategy == "root":
            return [f for f in readme_files if f.priority == READMEPriority.ROOT]
        
        elif strategy == "docs":
            return [
                f for f in readme_files
                if f.priority in [READMEPriority.ROOT, READMEPriority.DOCS]
            ]
        
        elif strategy == "priority":
            # Return highest priority READMEs
            if not readme_files:
                return []
            highest_priority = min(f.priority.value for f in readme_files)
            return [f for f in readme_files if f.priority.value == highest_priority]
        
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
