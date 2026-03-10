#!/usr/bin/env python
"""
Comprehensive test script for Content Normalizer feature.
Tests various scenarios and edge cases.
"""

from summarize_readme.content_normalizer import (
    ContentNormalizer,
    NormalizationLevel,
    EmojiHandling,
    create_normalizer,
)
from pathlib import Path
import json

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def print_test(name, passed):
    """Print test result."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")

def test_basic_normalization():
    """Test basic normalization functionality."""
    print_section("TEST 1: Basic Normalization")
    
    normalizer = ContentNormalizer()
    content = "# Title\n\n\n\nContent with    spaces"
    result = normalizer.normalize(content)
    
    # Check excessive newlines removed
    test1 = '\n\n\n\n' not in result
    print_test("Excessive newlines removed", test1)
    
    # Check title preserved
    test2 = '# Title' in result
    print_test("Title preserved", test2)
    
    return test1 and test2

def test_unicode_normalization():
    """Test unicode character normalization."""
    print_section("TEST 2: Unicode Normalization")
    
    normalizer = ContentNormalizer(fix_unicode=True)
    content = "Smart \u201cquotes\u201d and fancy\u2014dashes\u2026 test"
    result = normalizer.normalize(content)
    
    # Check smart quotes converted
    test1 = '"' in result and '\u201c' not in result
    print_test("Smart quotes converted", test1)
    
    # Check em-dash converted
    test2 = '\u2014' not in result
    print_test("Em-dash converted", test2)
    
    # Check ellipsis converted
    test3 = '...' in result
    print_test("Ellipsis converted", test3)
    
    print(f"\nOriginal: {content}")
    print(f"Result:   {result}")
    
    return test1 and test2 and test3

def test_html_removal():
    """Test HTML tag removal."""
    print_section("TEST 3: HTML Removal")
    
    normalizer = ContentNormalizer(remove_html=True)
    content = "<div>Content</div>\n<script>alert('test');</script>"
    result = normalizer.normalize(content)
    
    # Check HTML tags removed
    test1 = '<div>' not in result
    print_test("HTML tags removed", test1)
    
    # Check content preserved
    test2 = 'Content' in result
    print_test("Content preserved", test2)
    
    # Check script removed
    test3 = 'alert' not in result
    print_test("Script content removed", test3)
    
    print(f"\nOriginal: {content[:50]}...")
    print(f"Result:   {result[:50]}...")
    
    return test1 and test2 and test3

def test_emoji_removal():
    """Test emoji removal."""
    print_section("TEST 4: Emoji Removal")
    
    normalizer = ContentNormalizer(emoji_handling=EmojiHandling.REMOVE)
    content = "# 🚀 Project Title ✨"
    result = normalizer.normalize(content)
    
    # Check emojis removed
    test1 = '🚀' not in result and '✨' not in result
    print_test("Emojis removed", test1)
    
    # Check text preserved
    test2 = 'Project Title' in result
    print_test("Text preserved", test2)
    
    print(f"\nOriginal: {content}")
    print(f"Result:   {result}")
    
    return test1 and test2

def test_emoji_conversion():
    """Test emoji to text conversion."""
    print_section("TEST 5: Emoji Conversion")
    
    normalizer = ContentNormalizer(emoji_handling=EmojiHandling.CONVERT)
    content = "🚀 Rocket ✨ Sparkles 🎨 Art"
    result = normalizer.normalize(content)
    
    # Check known emojis converted
    test1 = '[rocket]' in result
    print_test("Rocket emoji converted", test1)
    
    test2 = '[sparkles]' in result
    print_test("Sparkles emoji converted", test2)
    
    test3 = '[art]' in result
    print_test("Art emoji converted", test3)
    
    print(f"\nOriginal: {content}")
    print(f"Result:   {result}")
    
    return test1 and test2 and test3

def test_header_normalization():
    """Test markdown header normalization."""
    print_section("TEST 6: Header Normalization")
    
    normalizer = ContentNormalizer(normalize_headers=True)
    content = """
#NoSpace
##  Extra Spaces  ##
### Trailing Hashes ###

Underlined H1
===========

Underlined H2
-----------
"""
    result = normalizer.normalize(content)
    
    # Check headers normalized
    test1 = '# NoSpace' in result
    print_test("Header without space fixed", test1)
    
    test2 = '## Extra Spaces' in result
    print_test("Header with extra spaces normalized", test2)
    
    test3 = '### Trailing Hashes' in result
    print_test("Trailing hashes removed", test3)
    
    test4 = '# Underlined H1' in result
    print_test("Underlined H1 converted", test4)
    
    test5 = '## Underlined H2' in result
    print_test("Underlined H2 converted", test5)
    
    print(f"\nResult preview:\n{result[:200]}")
    
    return test1 and test2 and test3 and test4 and test5

def test_code_block_preservation():
    """Test that code blocks are preserved."""
    print_section("TEST 7: Code Block Preservation")
    
    normalizer = ContentNormalizer(
        preserve_code_blocks=True,
        normalize_whitespace=True
    )
    content = """
# Title

```python
def   function_with_spaces():
    return    "preserved"
```

Regular text with    spaces.
"""
    result = normalizer.normalize(content)
    
    # Check code block preserved
    test1 = 'function_with_spaces' in result
    print_test("Code block function name preserved", test1)
    
    test2 = 'return    "preserved"' in result
    print_test("Code block spacing preserved", test2)
    
    print(f"\nResult preview:\n{result[:200]}")
    
    return test1 and test2

def test_link_standardization():
    """Test link formatting standardization."""
    print_section("TEST 8: Link Standardization")
    
    normalizer = ContentNormalizer(standardize_links=True)
    content = "[ Link with spaces ]( https://example.com )"
    result = normalizer.normalize(content)
    
    # Check link normalized
    test1 = '[Link with spaces](https://example.com)' in result
    print_test("Link spacing normalized", test1)
    
    print(f"\nOriginal: {content}")
    print(f"Result:   {result}")
    
    return test1

def test_statistics_tracking():
    """Test that statistics are tracked correctly."""
    print_section("TEST 9: Statistics Tracking")
    
    normalizer = ContentNormalizer(
        remove_html=True,
        normalize_headers=True
    )
    content = "<div>Test</div>\n#NoSpace\n\n\n\nContent"
    result = normalizer.normalize(content)
    stats = normalizer.get_stats()
    
    # Check stats exist
    test1 = 'original_size' in stats
    print_test("Stats contain original_size", test1)
    
    test2 = 'final_size' in stats
    print_test("Stats contain final_size", test2)
    
    test3 = stats['size_reduction'] >= 0
    print_test("Size reduction calculated", test3)
    
    print(f"\nStatistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    return test1 and test2 and test3

def test_normalization_levels():
    """Test different normalization levels."""
    print_section("TEST 10: Normalization Levels")
    
    content = "<div>HTML</div> #NoSpace"
    
    # Test minimal
    minimal = create_normalizer("minimal")
    result_min = minimal.normalize(content)
    test1 = not minimal.remove_html  # Minimal doesn't remove HTML
    print_test("Minimal level disables HTML removal", test1)
    
    # Test standard
    standard = create_normalizer("standard")
    result_std = standard.normalize(content)
    test2 = standard.remove_html  # Standard removes HTML
    print_test("Standard level enables HTML removal", test2)
    
    # Test aggressive
    aggressive = create_normalizer("aggressive")
    result_agg = aggressive.normalize(content)
    test3 = aggressive.emoji_handling == EmojiHandling.REMOVE
    print_test("Aggressive level removes emojis", test3)
    
    print(f"\nMinimal result:    {result_min[:50]}")
    print(f"Standard result:   {result_std[:50]}")
    print(f"Aggressive result: {result_agg[:50]}")
    
    return test1 and test2 and test3

def test_factory_function():
    """Test the create_normalizer factory function."""
    print_section("TEST 11: Factory Function")
    
    # Test with preset
    normalizer = create_normalizer("standard")
    test1 = normalizer.level == NormalizationLevel.STANDARD
    print_test("Standard preset creates correct level", test1)
    
    # Test with overrides
    normalizer = create_normalizer(
        "standard",
        emoji_handling="remove",
        remove_html=False
    )
    test2 = normalizer.emoji_handling == EmojiHandling.REMOVE
    print_test("Emoji handling override works", test2)
    
    test3 = not normalizer.remove_html
    print_test("Remove HTML override works", test3)
    
    return test1 and test2 and test3

def test_real_world_file():
    """Test with a real-world messy README file."""
    print_section("TEST 12: Real-World File")
    
    file_path = Path("test_samples/messy_readme.md")
    if not file_path.exists():
        print("⚠️  Test file not found, skipping")
        return True
    
    content = file_path.read_text(encoding='utf-8')
    print(f"Original file size: {len(content)} bytes")
    
    normalizer = create_normalizer("aggressive", emoji_handling="remove")
    result = normalizer.normalize(content)
    stats = normalizer.get_stats()
    
    print(f"Final file size: {len(result)} bytes")
    print(f"Size reduction: {stats['size_reduction']} bytes ({stats['size_reduction']/stats['original_size']*100:.1f}%)")
    
    # Check various normalizations occurred
    test1 = '<div>' not in result
    print_test("HTML tags removed", test1)
    
    test2 = '🚀' not in result and '✨' not in result
    print_test("Emojis removed", test2)
    
    test3 = '# Badly Formatted Title' in result  # Should be normalized
    print_test("Header normalized", test3)
    
    test4 = 'function_with_spaces' in result  # Code should be preserved
    print_test("Code block preserved", test4)
    
    print(f"\nFirst 300 chars of result:\n{result[:300]}...")
    
    return test1 and test2 and test3 and test4

def test_edge_cases():
    """Test edge cases."""
    print_section("TEST 13: Edge Cases")
    
    normalizer = ContentNormalizer()
    
    # Empty string
    result1 = normalizer.normalize("")
    test1 = result1 == ""
    print_test("Empty string handled", test1)
    
    # Whitespace only
    result2 = normalizer.normalize("   \n\n   ")
    test2 = result2 is not None
    print_test("Whitespace-only string handled", test2)
    
    # Very long content
    long_content = "# Title\n\n" + ("Content paragraph. " * 1000)
    result3 = normalizer.normalize(long_content)
    test3 = len(result3) > 0
    print_test("Long content handled", test3)
    
    return test1 and test2 and test3

def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "="*70)
    print("  CONTENT NORMALIZER - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    tests = [
        ("Basic Normalization", test_basic_normalization),
        ("Unicode Normalization", test_unicode_normalization),
        ("HTML Removal", test_html_removal),
        ("Emoji Removal", test_emoji_removal),
        ("Emoji Conversion", test_emoji_conversion),
        ("Header Normalization", test_header_normalization),
        ("Code Block Preservation", test_code_block_preservation),
        ("Link Standardization", test_link_standardization),
        ("Statistics Tracking", test_statistics_tracking),
        ("Normalization Levels", test_normalization_levels),
        ("Factory Function", test_factory_function),
        ("Real-World File", test_real_world_file),
        ("Edge Cases", test_edge_cases),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"❌ EXCEPTION: {e}")
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed\n")
    
    for name, result, error in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if error:
            print(f"         Error: {error}")
    
    print(f"\n{'='*70}")
    if passed == total:
        print("  🎉 ALL TESTS PASSED!")
    else:
        print(f"  ⚠️  {total - passed} test(s) failed")
    print(f"{'='*70}\n")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
