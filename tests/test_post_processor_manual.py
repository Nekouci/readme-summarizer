"""
Quick manual test for the post-processor module.

Run this to verify the post-processor is working correctly.
"""

from pathlib import Path
from summarize_readme.post_processor import (
    create_post_processor,
    quick_process,
    Theme,
    ExportFormat,
)


def test_basic():
    """Test basic HTML generation."""
    print("Testing basic HTML generation...")
    
    content = """# Test Project

This is a test of the post-processor.

## Features

- Feature 1
- Feature 2

## Code Example

```python
def hello():
    print("Hello, World!")
```

Done!
"""
    
    result = quick_process(content, ExportFormat.HTML_STANDALONE, Theme.GITHUB)
    
    assert len(result) > 0
    assert "<!DOCTYPE html>" in result
    assert "Test Project" in result
    # The theme name appears in comments
    assert "README Summarizer" in result
    
    print("✓ Basic HTML generation works!")


def test_themes():
    """Test different themes."""
    print("\nTesting themes...")
    
    content = "# Theme Test\n\nTesting themes."
    
    themes = [Theme.GITHUB, Theme.MATERIAL, Theme.DRACULA, Theme.NORD]
    
    for theme in themes:
        result = quick_process(content, ExportFormat.HTML_STANDALONE, theme)
        assert len(result) > 0
        print(f"  ✓ {theme.value} theme works")
    
    print("✓ All themes work!")


def test_formats():
    """Test different export formats."""
    print("\nTesting export formats...")
    
    content = """# Format Test

Testing different formats.

## Code

```python
print("test")
```
"""
    
    processor = create_post_processor()
    
    # Test HTML standalone
    result = processor.process(content, ExportFormat.HTML_STANDALONE)
    assert "<!DOCTYPE html>" in result
    print("  ✓ HTML Standalone works")
    
    # Test JSON enriched
    result = processor.process(content, ExportFormat.JSON_ENRICHED)
    assert '"content"' in result
    assert '"statistics"' in result
    print("  ✓ JSON Enriched works")
    
    # Test Markdown enhanced
    result = processor.process(content, ExportFormat.MARKDOWN_ENHANCED)
    assert "#" in result
    print("  ✓ Markdown Enhanced works")
    
    # Test Social snippet
    result = processor.process(content, ExportFormat.SOCIAL_SNIPPET)
    assert "twitter" in result
    print("  ✓ Social Snippet works")
    
    print("✓ All formats work!")


def test_stats():
    """Test statistics collection."""
    print("\nTesting statistics...")
    
    content = """# Stats Test

Content with [link](https://example.com).

```python
code = "test"
```
"""
    
    processor = create_post_processor()
    result = processor.process(content, ExportFormat.HTML_STANDALONE)
    
    stats = processor.get_stats()
    
    assert stats.input_length > 0
    assert stats.output_length > 0
    assert stats.code_blocks_highlighted >= 0
    assert stats.links_processed >= 0
    
    print(f"  Input: {stats.input_length} chars")
    print(f"  Output: {stats.output_length} chars")
    print(f"  Code blocks: {stats.code_blocks_highlighted}")
    print(f"  Links: {stats.links_processed}")
    print("✓ Statistics collection works!")


def test_file_output():
    """Test writing to file."""
    print("\nTesting file output...")
    
    content = "# File Test\n\nTesting file output."
    result = quick_process(content)
    
    output_file = Path("test_postprocessor_output.html")
    output_file.write_text(result, encoding='utf-8')
    
    assert output_file.exists()
    assert output_file.stat().st_size > 0
    
    # Clean up
    output_file.unlink()
    
    print("✓ File output works!")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Post-Processor Manual Tests")
    print("=" * 60)
    
    tests = [
        test_basic,
        test_themes,
        test_formats,
        test_stats,
        test_file_output,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")


if __name__ == "__main__":
    run_all_tests()
