"""
Utility functions for the README summarizer.
"""

import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid URL.
    
    Args:
        url: String to validate
    
    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except Exception:
        return False


def read_file_content(file_path: Path) -> str:
    """
    Read content from a file with error handling.
    
    Args:
        file_path: Path to the file
    
    Returns:
        File content as string
    
    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If file encoding is invalid
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        return file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            return file_path.read_text(encoding='latin-1')
        except Exception as e:
            raise UnicodeDecodeError(
                'utf-8', b'', 0, 1,
                f"Failed to decode file {file_path}: {e}"
            )


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    return filename or 'unnamed'


def format_file_size(size_bytes: int) -> str:
    """
    Format byte size to human-readable string.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 KB")
    """
    size: float = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def extract_github_info(url: str) -> Optional[dict]:
    """
    Extract GitHub repository information from a URL.
    
    Args:
        url: GitHub URL
    
    Returns:
        Dictionary with repo info or None
    """
    pattern = r'github\.com/([^/]+)/([^/]+)'
    match = re.search(pattern, url)
    
    if match:
        return {
            "owner": match.group(1),
            "repo": match.group(2).replace('.git', ''),
            "url": f"https://github.com/{match.group(1)}/{match.group(2).replace('.git', '')}",
        }
    return None
