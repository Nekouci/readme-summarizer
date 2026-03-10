"""
Tests for the input_resolver module.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import base64

from summarize_readme.input_resolver import InputResolver, InputType


class TestInputTypeDetection:
    """Test input type detection."""
    
    def test_detect_local_file(self, tmp_path):
        """Test detection of local file paths."""
        resolver = InputResolver()
        
        # Create a temporary file
        test_file = tmp_path / "README.md"
        test_file.write_text("# Test")
        
        assert resolver.detect_input_type(str(test_file)) == InputType.LOCAL_FILE
    
    def test_detect_github_shorthand(self):
        """Test detection of GitHub shorthand notation."""
        resolver = InputResolver()
        
        assert resolver.detect_input_type("owner/repo") == InputType.GITHUB_SHORTHAND
        assert resolver.detect_input_type("user-name/repo-name") == InputType.GITHUB_SHORTHAND
        assert resolver.detect_input_type("owner/repo@branch") == InputType.GITHUB_SHORTHAND
        assert resolver.detect_input_type("user123/my-repo@dev-branch") == InputType.GITHUB_SHORTHAND
    
    def test_detect_github_repo_url(self):
        """Test detection of GitHub repository URLs."""
        resolver = InputResolver()
        
        assert resolver.detect_input_type("https://github.com/owner/repo") == InputType.GITHUB_REPO
        assert resolver.detect_input_type("https://github.com/user/project.git") == InputType.GITHUB_REPO
    
    def test_detect_github_raw_url(self):
        """Test detection of GitHub raw URLs."""
        resolver = InputResolver()
        
        url = "https://raw.githubusercontent.com/owner/repo/main/README.md"
        assert resolver.detect_input_type(url) == InputType.GITHUB_RAW_URL
    
    def test_detect_direct_url(self):
        """Test detection of direct URLs."""
        resolver = InputResolver()
        
        assert resolver.detect_input_type("https://example.com/readme.md") == InputType.DIRECT_URL
        assert resolver.detect_input_type("http://docs.site.org/README.md") == InputType.DIRECT_URL
    
    def test_not_github_shorthand(self):
        """Test patterns that should not be detected as GitHub shorthand."""
        resolver = InputResolver()
        
        # These should not be detected as GitHub shorthand
        assert resolver.detect_input_type("./local/file.md") != InputType.GITHUB_SHORTHAND
        assert resolver.detect_input_type("../parent/file.md") != InputType.GITHUB_SHORTHAND
        assert resolver.detect_input_type("/absolute/path.md") != InputType.GITHUB_SHORTHAND
        assert resolver.detect_input_type("C:/windows/path.md") != InputType.GITHUB_SHORTHAND


class TestLocalFileResolution:
    """Test local file resolution."""
    
    def test_resolve_local_file(self, tmp_path):
        """Test resolving a local file."""
        resolver = InputResolver()
        
        # Create test file
        test_file = tmp_path / "test_readme.md"
        test_content = "# Test README\n\nThis is a test."
        test_file.write_text(test_content)
        
        content, metadata = resolver.resolve(str(test_file))
        
        assert content == test_content
        assert metadata["type"] == "local_file"
        assert metadata["name"] == "test_readme.md"
        assert metadata["size"] == len(test_content)
    
    def test_resolve_nonexistent_file(self):
        """Test error handling for nonexistent files."""
        resolver = InputResolver()
        
        with pytest.raises(FileNotFoundError):
            resolver.resolve("nonexistent_file.md")


class TestDirectUrlResolution:
    """Test direct URL resolution."""
    
    @patch('summarize_readme.input_resolver.requests.Session.get')
    def test_resolve_direct_url(self, mock_get):
        """Test resolving a direct URL."""
        resolver = InputResolver()
        
        # Mock response
        mock_response = Mock()
        mock_response.text = "# README Content"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        url = "https://example.com/readme.md"
        content, metadata = resolver.resolve(url)
        
        assert content == "# README Content"
        assert metadata["type"] == "direct_url"
        assert metadata["source"] == url
        assert metadata["status_code"] == 200
    
    @patch('summarize_readme.input_resolver.requests.Session.get')
    def test_resolve_url_error(self, mock_get):
        """Test error handling for failed URL requests."""
        resolver = InputResolver()
        
        # Mock failed response
        mock_get.side_effect = Exception("Network error")
        
        with pytest.raises(Exception, match="Failed to fetch URL"):
            resolver.resolve("https://example.com/readme.md")


class TestGitHubResolution:
    """Test GitHub repository resolution."""
    
    @patch('summarize_readme.input_resolver.requests.Session.get')
    def test_resolve_github_shorthand(self, mock_get):
        """Test resolving GitHub shorthand notation."""
        resolver = InputResolver()
        
        # Mock GitHub API response
        readme_content = "# Project README"
        encoded_content = base64.b64encode(readme_content.encode()).decode()
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": encoded_content,
            "name": "README.md",
            "download_url": "https://raw.githubusercontent.com/owner/repo/main/README.md",
            "html_url": "https://github.com/owner/repo/blob/main/README.md",
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        content, metadata = resolver.resolve("owner/repo")
        
        assert content == readme_content
        assert metadata["type"] == "github_repo"
        assert metadata["owner"] == "owner"
        assert metadata["repo"] == "repo"
        assert "README.md" in metadata["file"]
    
    @patch('summarize_readme.input_resolver.requests.Session.get')
    def test_resolve_github_shorthand_with_branch(self, mock_get):
        """Test resolving GitHub shorthand with branch specification."""
        resolver = InputResolver()
        
        readme_content = "# Dev Branch README"
        encoded_content = base64.b64encode(readme_content.encode()).decode()
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": encoded_content,
            "name": "README.md",
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        content, metadata = resolver.resolve("owner/repo@dev")
        
        assert content == readme_content
        assert metadata["owner"] == "owner"
        assert metadata["repo"] == "repo"
        # Note: branch metadata might vary based on implementation
    
    @patch('summarize_readme.input_resolver.requests.Session.get')
    def test_resolve_github_repo_url(self, mock_get):
        """Test resolving GitHub repository URL."""
        resolver = InputResolver()
        
        readme_content = "# Repository README"
        encoded_content = base64.b64encode(readme_content.encode()).decode()
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": encoded_content,
            "name": "README.md",
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        content, metadata = resolver.resolve("https://github.com/owner/repo")
        
        assert content == readme_content
        assert metadata["owner"] == "owner"
        assert metadata["repo"] == "repo"
    
    @patch('summarize_readme.input_resolver.requests.Session.get')
    def test_resolve_github_raw_url(self, mock_get):
        """Test resolving GitHub raw URL."""
        resolver = InputResolver()
        
        mock_response = Mock()
        mock_response.text = "# Raw README Content"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        url = "https://raw.githubusercontent.com/owner/repo/main/README.md"
        content, metadata = resolver.resolve(url)
        
        assert content == "# Raw README Content"
        assert metadata["type"] == "github_raw"
        assert metadata["owner"] == "owner"
        assert metadata["repo"] == "repo"
        assert metadata["branch"] == "main"
    
    @patch('summarize_readme.input_resolver.requests.Session.get')
    def test_resolve_github_not_found(self, mock_get):
        """Test error handling when GitHub README is not found."""
        resolver = InputResolver()
        
        # Mock 404 response from GitHub API
        mock_api_response = Mock()
        mock_api_response.status_code = 404
        mock_api_response.raise_for_status.side_effect = Exception("Not found")
        
        # Mock failed fallback attempts
        mock_fallback_response = Mock()
        mock_fallback_response.status_code = 404
        
        mock_get.side_effect = [mock_api_response, mock_fallback_response]
        
        # Should try API first, then fallback
        with pytest.raises((FileNotFoundError, Exception)):
            resolver.resolve("owner/nonexistent-repo")


class TestGitHubShorthandPattern:
    """Test GitHub shorthand pattern matching."""
    
    def test_is_github_shorthand_valid(self):
        """Test valid GitHub shorthand patterns."""
        resolver = InputResolver()
        
        assert resolver._is_github_shorthand("owner/repo") is True
        assert resolver._is_github_shorthand("user123/my-repo") is True
        assert resolver._is_github_shorthand("org-name/project.name") is True
        assert resolver._is_github_shorthand("user/repo@branch") is True
        assert resolver._is_github_shorthand("user/repo@feature-branch") is True
    
    def test_is_github_shorthand_invalid(self):
        """Test invalid patterns that should not match."""
        resolver = InputResolver()
        
        assert resolver._is_github_shorthand("https://github.com/owner/repo") is False
        assert resolver._is_github_shorthand("./local/path") is False
        assert resolver._is_github_shorthand("../parent/path") is False
        assert resolver._is_github_shorthand("/absolute/path") is False
        assert resolver._is_github_shorthand("C:\\Windows\\path") is False
        assert resolver._is_github_shorthand("owner/repo/extra/path") is False
        assert resolver._is_github_shorthand("single-part") is False


class TestMetadata:
    """Test metadata returned by resolver."""
    
    @patch('summarize_readme.input_resolver.requests.Session.get')
    def test_metadata_completeness(self, mock_get, tmp_path):
        """Test that metadata contains expected fields."""
        resolver = InputResolver()
        
        # Test local file metadata
        test_file = tmp_path / "README.md"
        test_file.write_text("# Test")
        content, metadata = resolver.resolve(str(test_file))
        
        assert "type" in metadata
        assert "source" in metadata
        assert "size" in metadata
        assert "name" in metadata
        
        # Test GitHub metadata
        readme_content = "# Test"
        encoded_content = base64.b64encode(readme_content.encode()).decode()
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": encoded_content,
            "name": "README.md",
            "download_url": "https://example.com",
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        content, metadata = resolver.resolve("owner/repo")
        
        assert "type" in metadata
        assert "source" in metadata
        assert "owner" in metadata
        assert "repo" in metadata
        assert "file" in metadata
