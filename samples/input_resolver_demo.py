"""
Example usage of the Input Resolver / Repo Fetcher feature.

This demonstrates various ways to use the advanced input resolver.
"""

from summarize_readme.input_resolver import InputResolver, InputType
from summarize_readme.core import ReadmeSummarizer, SummaryFormat


def example_basic_usage():
    """Basic usage examples."""
    print("=== Basic Input Resolver Usage ===\n")
    
    resolver = InputResolver(verbose=True)
    
    # Example 1: GitHub shorthand
    print("Example 1: GitHub shorthand notation")
    print("Input: 'microsoft/vscode'")
    try:
        content, metadata = resolver.resolve("microsoft/vscode")
        print(f"✓ Successfully fetched {len(content)} bytes")
        print(f"  Owner: {metadata['owner']}")
        print(f"  Repo: {metadata['repo']}")
        print(f"  Branch: {metadata.get('branch', 'default')}")
        print(f"  File: {metadata.get('file', 'README.md')}\n")
    except Exception as e:
        print(f"✗ Error: {e}\n")
    
    # Example 2: Detect input types
    print("Example 2: Input type detection")
    sources = [
        "README.md",
        "python/cpython",
        "https://github.com/torvalds/linux",
        "https://raw.githubusercontent.com/facebook/react/main/README.md",
        "https://example.com/readme.md",
    ]
    
    for source in sources:
        input_type = resolver.detect_input_type(source)
        print(f"  '{source}' -> {input_type.value}")
    print()


def example_with_summarization():
    """Example combining input resolver with summarization."""
    print("=== Complete Workflow Example ===\n")
    
    # Initialize resolver and summarizer
    resolver = InputResolver(verbose=False)
    summarizer = ReadmeSummarizer(
        max_length=100,
        include_badges=True,
        include_sections=True,
        bullet_points=True,
    )
    
    # Fetch from GitHub and summarize
    print("Fetching and summarizing: facebook/react")
    try:
        content, metadata = resolver.resolve("facebook/react")
        summary = summarizer.summarize(content, output_format=SummaryFormat.TEXT)
        
        print(f"\n✓ Fetched from: {metadata['owner']}/{metadata['repo']}")
        print(f"  Branch: {metadata.get('branch', 'default')}")
        print(f"  Size: {metadata['size']} bytes")
        print(f"\n--- Summary ---")
        print(summary)
        print()
    except Exception as e:
        print(f"✗ Error: {e}\n")


def example_multiple_sources():
    """Example processing multiple sources."""
    print("=== Multiple Sources Example ===\n")
    
    resolver = InputResolver(verbose=False)
    summarizer = ReadmeSummarizer(max_length=50)
    
    sources = [
        "torvalds/linux",
        "microsoft/TypeScript",
        "python/cpython",
    ]
    
    results = []
    
    for source in sources:
        try:
            print(f"Processing: {source}...", end=" ")
            content, metadata = resolver.resolve(source)
            summary = summarizer.summarize(content)
            results.append({
                "source": source,
                "metadata": metadata,
                "summary": summary[:100] + "..." if len(summary) > 100 else summary,
            })
            print("✓")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print(f"\n✓ Successfully processed {len(results)}/{len(sources)} repositories\n")
    
    for result in results:
        print(f"--- {result['source']} ---")
        print(result['summary'])
        print()


def example_branch_specific():
    """Example fetching from specific branches."""
    print("=== Branch-Specific Fetching ===\n")
    
    resolver = InputResolver(verbose=True)
    
    # Test with branch notation
    examples = [
        ("microsoft/vscode", "default branch"),
        ("microsoft/vscode@main", "main branch"),
        ("facebook/react@main", "main branch"),
    ]
    
    for source, description in examples:
        print(f"Fetching: {source} ({description})")
        try:
            content, metadata = resolver.resolve(source)
            print(f"✓ Success: {len(content)} bytes from {metadata.get('file', 'README')}")
            print(f"  Branch: {metadata.get('branch', 'unknown')}\n")
        except Exception as e:
            print(f"✗ Error: {e}\n")


def example_error_handling():
    """Example demonstrating error handling."""
    print("=== Error Handling Examples ===\n")
    
    resolver = InputResolver(verbose=False)
    
    invalid_sources = [
        ("nonexistent/repository123abc", "Invalid repository"),
        ("invalid format", "Invalid format"),
        ("https://example.com/404-not-found.md", "404 URL"),
    ]
    
    for source, description in invalid_sources:
        print(f"Testing: {source} ({description})")
        try:
            content, metadata = resolver.resolve(source)
            print(f"  Unexpected success!")
        except FileNotFoundError as e:
            print(f"  ✓ Caught FileNotFoundError: {str(e)[:60]}...")
        except Exception as e:
            print(f"  ✓ Caught Exception: {str(e)[:60]}...")
        print()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║   README Summarizer - Input Resolver Demo                   ║
║   Advanced Input Resolution & Repository Fetcher            ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Run examples (comment out if rate-limited)
    example_basic_usage()
    
    # Uncomment to run other examples:
    # example_with_summarization()
    # example_multiple_sources()
    # example_branch_specific()
    # example_error_handling()
    
    print("\n✓ Demo completed!")
    print("\nNote: Some examples are commented out to avoid GitHub API rate limits.")
    print("Uncomment them in the code to test all features.")
