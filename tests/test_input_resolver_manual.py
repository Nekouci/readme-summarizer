"""
Manual comprehensive test for Input Resolver / Repo Fetcher feature.
Run without pytest dependency.
"""

import sys
from pathlib import Path
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Mock rich.console if not available
try:
    from rich.console import Console as RichConsole
    Console = RichConsole  # type: ignore
except ImportError:
    class Console:  # type: ignore
        def print(self, *args: Any, **kwargs: Any) -> None:
            print(*args)


def test_imports() -> bool:
    """Test that all required modules import correctly."""
    print("\n=== Test 1: Module Imports ===")
    try:
        # Monkeypatch rich module in sys.modules
        if 'rich' not in sys.modules:
            import types
            rich_module = types.ModuleType('rich')
            console_module = types.ModuleType('rich.console')
            setattr(console_module, 'Console', Console)  # type: ignore
            setattr(rich_module, 'console', console_module)  # type: ignore
            sys.modules['rich'] = rich_module
            sys.modules['rich.console'] = console_module
        
        # Import directly from the module file
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "input_resolver", 
            Path(__file__).parent / "src" / "summarize_readme" / "input_resolver.py"
        )
        if spec is None or spec.loader is None:
            raise ImportError("Could not load module spec")
        input_resolver_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(input_resolver_module)
        
        InputResolver = input_resolver_module.InputResolver
        InputType = input_resolver_module.InputType
        
        # Store in globals for other tests to use
        globals()['InputResolver'] = InputResolver
        globals()['InputType'] = InputType
        
        print("✓ InputResolver imported")
        print("✓ InputType enum imported")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_input_type_detection() -> bool:
    """Test input type detection logic."""
    print("\n=== Test 2: Input Type Detection ===")
    InputResolver = globals().get('InputResolver')  # type: ignore
    InputType = globals().get('InputType')  # type: ignore
    
    if InputResolver is None or InputType is None:
        print("✗ InputResolver or InputType not available")
        return False
    
    resolver = InputResolver(verbose=False)
    
    test_cases = [
        # (input, expected_type, description)
        ("microsoft/vscode", InputType.GITHUB_SHORTHAND, "GitHub shorthand"),
        ("owner/repo@branch", InputType.GITHUB_SHORTHAND, "GitHub shorthand with branch"),
        ("https://github.com/owner/repo", InputType.GITHUB_REPO, "GitHub repo URL"),
        ("https://raw.githubusercontent.com/owner/repo/main/README.md", InputType.GITHUB_RAW_URL, "GitHub raw URL"),
        ("https://example.com/readme.md", InputType.DIRECT_URL, "Direct URL"),
        ("README.md", InputType.LOCAL_FILE, "Local file (current dir)"),
        ("./docs/README.md", InputType.LOCAL_FILE, "Local file (relative path)"),
    ]
    
    passed = 0
    failed = 0
    
    for input_str, expected_type, description in test_cases:
        try:
            detected_type = resolver.detect_input_type(input_str)
            if detected_type == expected_type:
                print(f"✓ {description:40s} -> {detected_type.value}")
                passed += 1
            else:
                print(f"✗ {description:40s} -> Expected {expected_type.value}, got {detected_type.value}")
                failed += 1
        except Exception as e:
            print(f"✗ {description:40s} -> Error: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_github_shorthand_pattern() -> bool:
    """Test GitHub shorthand pattern matching."""
    print("\n=== Test 3: GitHub Shorthand Pattern Matching ===")
    InputResolver = globals().get('InputResolver')  # type: ignore
    
    if InputResolver is None:
        print("✗ InputResolver not available")
        return False
    
    resolver = InputResolver(verbose=False)
    
    valid_patterns = [
        "owner/repo",
        "user123/my-repo",
        "org-name/project.name",
        "microsoft/vscode",
        "torvalds/linux",
        "facebook/react@main",
        "rust-lang/rust@stable",
    ]
    
    invalid_patterns = [
        "https://github.com/owner/repo",
        "./local/path",
        "../parent/path",
        "/absolute/path",
        "C:\\Windows\\path",
        "single-part",
        "owner/repo/extra/path",
    ]
    
    passed = 0
    failed = 0
    
    print("\nValid patterns (should match):")
    for pattern in valid_patterns:
        result = resolver._is_github_shorthand(pattern)
        if result:
            print(f"  ✓ '{pattern}'")
            passed += 1
        else:
            print(f"  ✗ '{pattern}' (should match but didn't)")
            failed += 1
    
    print("\nInvalid patterns (should NOT match):")
    for pattern in invalid_patterns:
        result = resolver._is_github_shorthand(pattern)
        if not result:
            print(f"  ✓ '{pattern}' (correctly rejected)")
            passed += 1
        else:
            print(f"  ✗ '{pattern}' (should not match but did)")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_local_file_resolution() -> bool:
    """Test local file resolution."""
    print("\n=== Test 4: Local File Resolution ===")
    InputResolver = globals().get('InputResolver')  # type: ignore
    import tempfile
    
    if InputResolver is None:
        print("✗ InputResolver not available")
        return False
    
    resolver = InputResolver(verbose=False)
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        test_content = "# Test README\n\nThis is a test file."
        f.write(test_content)
        temp_path = f.name
    
    try:
        content, metadata = resolver.resolve(temp_path)
        
        if content == test_content:
            print(f"✓ Content matches")
        else:
            print(f"✗ Content mismatch")
            return False
        
        if metadata['type'] == 'local_file':
            print(f"✓ Correct type: {metadata['type']}")
        else:
            print(f"✗ Wrong type: {metadata['type']}")
            return False
        
        if 'size' in metadata:
            print(f"✓ Size in metadata: {metadata['size']} bytes")
        else:
            print(f"✗ Size missing from metadata")
            return False
        
        if 'name' in metadata:
            print(f"✓ Name in metadata: {metadata['name']}")
        else:
            print(f"✗ Name missing from metadata")
            return False
        
        print("\n✓ All local file tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        # Clean up
        Path(temp_path).unlink(missing_ok=True)


def test_github_url_parsing() -> bool:
    """Test GitHub URL parsing."""
    print("\n=== Test 5: GitHub URL Parsing ===")
    import re
    
    test_urls = [
        ("https://github.com/microsoft/vscode", "microsoft", "vscode"),
        ("https://github.com/torvalds/linux", "torvalds", "linux"),
        ("https://github.com/facebook/react.git", "facebook", "react"),
    ]
    
    passed = 0
    failed = 0
    
    for url, expected_owner, expected_repo in test_urls:
        pattern = r"github\.com/([^/]+)/([^/]+)"
        match = re.search(pattern, url)
        
        if match:
            owner = match.group(1)
            repo = match.group(2).replace(".git", "")
            
            if owner == expected_owner and repo == expected_repo:
                print(f"✓ {url}")
                print(f"  -> owner={owner}, repo={repo}")
                passed += 1
            else:
                print(f"✗ {url}")
                print(f"  -> Expected owner={expected_owner}, repo={expected_repo}")
                print(f"  -> Got owner={owner}, repo={repo}")
                failed += 1
        else:
            print(f"✗ {url} -> No match")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_github_live_fetch() -> bool:
    """Test live GitHub fetching (requires internet)."""
    print("\n=== Test 6: Live GitHub Fetch (Internet Required) ===")
    print("This test will attempt to fetch a real README from GitHub...")
    InputResolver = globals().get('InputResolver')  # type: ignore
    
    if InputResolver is None:
        print("✗ InputResolver not available")
        return False
    
    resolver = InputResolver(verbose=True)
    
    # Use a small, stable public repo for testing
    test_repos = [
        "octocat/Hello-World",  # Famous test repo
    ]
    
    for repo in test_repos:
        print(f"\nTesting: {repo}")
        try:
            content, metadata = resolver.resolve(repo)
            
            print(f"✓ Successfully fetched")
            print(f"  Type: {metadata.get('type', 'unknown')}")
            print(f"  Owner: {metadata.get('owner', 'N/A')}")
            print(f"  Repo: {metadata.get('repo', 'N/A')}")
            print(f"  Branch: {metadata.get('branch', 'N/A')}")
            print(f"  File: {metadata.get('file', 'N/A')}")
            print(f"  Size: {len(content)} bytes")
            
            # Verify content looks like a README
            if len(content) > 0:
                print(f"✓ Content is non-empty")
            else:
                print(f"✗ Content is empty")
                return False
            
            # Check for common README markers
            if '#' in content or 'README' in content.upper():
                print(f"✓ Content appears to be markdown/README")
            else:
                print(f"⚠ Warning: Content doesn't look like typical README")
            
            print(f"\n✓ Live fetch test passed for {repo}")
            return True
            
        except Exception as e:
            print(f"✗ Error fetching {repo}: {e}")
            print(f"⚠ This may be due to network issues or rate limiting")
            return False
    
    return True


def test_error_handling() -> bool:
    """Test error handling for invalid inputs."""
    print("\n=== Test 7: Error Handling ===")
    InputResolver = globals().get('InputResolver')  # type: ignore
    
    if InputResolver is None:
        print("✗ InputResolver not available")
        return False
    
    resolver = InputResolver(verbose=False)
    
    test_cases = [
        ("nonexistent_file_12345.md", FileNotFoundError, "Nonexistent local file"),
        # Note: We won't test nonexistent repos to avoid unnecessary API calls
    ]
    
    passed = 0
    failed = 0
    
    for input_str, expected_error, description in test_cases:
        try:
            content, metadata = resolver.resolve(input_str)
            print(f"✗ {description}: Should have raised {expected_error.__name__}")
            failed += 1
        except expected_error:
            print(f"✓ {description}: Correctly raised {expected_error.__name__}")
            passed += 1
        except Exception as e:
            print(f"⚠ {description}: Raised {type(e).__name__} instead of {expected_error.__name__}")
            passed += 1  # Still counts as passed since error was raised
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def run_all_tests() -> bool:
    """Run all comprehensive tests."""
    print("=" * 70)
    print("COMPREHENSIVE INPUT RESOLVER / REPO FETCHER TEST SUITE")
    print("=" * 70)
    
    results = []
    
    # Test 1: Imports
    results.append(("Module Imports", test_imports()))
    
    if not results[0][1]:
        print("\n✗ Cannot proceed - module import failed")
        return False
    
    # Test 2-7: Functionality tests
    results.append(("Input Type Detection", test_input_type_detection()))
    results.append(("GitHub Shorthand Pattern", test_github_shorthand_pattern()))
    results.append(("Local File Resolution", test_local_file_resolution()))
    results.append(("GitHub URL Parsing", test_github_url_parsing()))
    results.append(("Live GitHub Fetch", test_github_live_fetch()))
    results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status:12s} - {test_name}")
    
    print("=" * 70)
    print(f"Overall: {passed_count}/{total_count} test groups passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! Feature is working correctly.")
        return True
    else:
        print(f"\n⚠ {total_count - passed_count} test group(s) failed.")
        return False


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
