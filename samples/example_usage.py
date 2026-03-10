"""
Example usage of README Summarizer as a Python library.
"""

from pathlib import Path
from summarize_readme import ReadmeSummarizer
from summarize_readme.core import SummaryFormat


def example_basic_usage():
    """Basic summarization example."""
    print("=== Basic Usage ===\n")
    
    # Initialize summarizer
    summarizer = ReadmeSummarizer()
    
    # Read content
    content = Path("README.md").read_text(encoding='utf-8')
    
    # Generate summary
    summary = summarizer.summarize(content)
    print(summary)


def example_advanced_usage():
    """Advanced summarization with options."""
    print("\n=== Advanced Usage ===\n")
    
    # Custom configuration
    summarizer = ReadmeSummarizer(
        max_length=50,
        bullet_points=True,
        include_badges=True,
    )
    
    content = Path("README.md").read_text(encoding='utf-8')
    
    # JSON format with links
    summary = summarizer.summarize(
        content,
        output_format=SummaryFormat.JSON,
        extract_links=True,
    )
    
    print(summary)


def example_analysis():
    """Analyze README metrics."""
    print("\n=== Content Analysis ===\n")
    
    summarizer = ReadmeSummarizer()
    content = Path("README.md").read_text(encoding='utf-8')
    
    # Get detailed analysis
    analysis = summarizer.analyze(content)
    
    print(f"File size: {analysis['size']} bytes")
    print(f"Lines: {analysis['lines']}")
    print(f"Words: {analysis['words']}")
    print(f"Sections: {analysis['sections']}")
    print(f"Links: {analysis['links']}")
    print(f"Code blocks: {analysis['code_blocks']}")
    
    if analysis['section_names']:
        print("\nSection names:")
        for section in analysis['section_names']:
            print(f"  - {section}")


def example_url_fetching():
    """Fetch and summarize from URL."""
    print("\n=== URL Fetching ===\n")
    
    summarizer = ReadmeSummarizer()
    
    # Fetch from GitHub
    url = "https://raw.githubusercontent.com/python/cpython/main/README.rst"
    
    try:
        content = summarizer.fetch_from_url(url)
        summary = summarizer.summarize(content, output_format=SummaryFormat.TEXT)
        print(summary)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    example_basic_usage()
    example_advanced_usage()
    example_analysis()
    # example_url_fetching()  # Uncomment to test URL fetching
