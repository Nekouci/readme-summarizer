"""
Wrapper Demo - Advanced Summarization Features

This script demonstrates the Summarizer Wrapper capabilities:
- Caching and performance
- AI enhancement
- Pipeline processing
- Template rendering
- Comparison mode

Run with: python samples/wrapper_demo.py
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from summarize_readme.core import ReadmeSummarizer
from summarize_readme.wrapper import (
    SummarizerWrapper,
    CacheBackend,
    AIProvider,
    SummaryPipeline,
)
from summarize_readme.templates import create_template_engine
from summarize_readme.ai_enhancers import create_enhancer


def demo_basic_wrapper():
    """Demo 1: Basic wrapper with caching."""
    print("=" * 70)
    print("DEMO 1: Basic Wrapper with Caching")
    print("=" * 70)
    
    # Sample README content
    readme_content = """
# My Awesome Project

A Python library for doing amazing things with minimal effort.

## Features

- Fast and efficient
- Easy to use API
- Comprehensive documentation
- Active community support

## Installation

```bash
pip install awesome-project
```

## Quick Start

```python
from awesome import Project

project = Project()
result = project.do_amazing_things()
print(result)
```

## Documentation

Full documentation available at https://docs.example.com
    """
    
    # Create wrapper
    wrapper = SummarizerWrapper(
        summarizer=ReadmeSummarizer(max_length=100),
        enable_cache=True,
        cache_backend=CacheBackend.MEMORY,
    )
    
    print("\n1️⃣  First run (no cache):")
    result1 = wrapper.summarize(readme_content, source="demo1.md")
    print(f"   Content: {result1.content[:100]}...")
    print(f"   Processing time: {result1.metadata.processing_time:.4f}s")
    print(f"   Cache hit: {result1.metadata.cache_hit}")
    
    print("\n2️⃣  Second run (cached):")
    result2 = wrapper.summarize(readme_content, source="demo1.md")
    print(f"   Content: {result2.content[:100]}...")
    print(f"   Processing time: {result2.metadata.processing_time:.4f}s")
    print(f"   Cache hit: {result2.metadata.cache_hit}")
    
    speedup = result1.metadata.processing_time / result2.metadata.processing_time
    print(f"\n   💨 Cache speedup: {speedup:.1f}x faster!")


def demo_templates():
    """Demo 2: Template rendering."""
    print("\n" + "=" * 70)
    print("DEMO 2: Template System")
    print("=" * 70)
    
    # Create wrapper
    wrapper = SummarizerWrapper()
    
    readme_content = """
# Data Analysis Tool

A powerful tool for analyzing large datasets with ease.

## Key Features
- Fast processing
- Multiple export formats
- Beautiful visualizations
    """
    
    result = wrapper.summarize(readme_content, source="analysis-tool.md")
    
    # Create template engine
    engine = create_template_engine()
    
    # Context for templates
    context = {
        "title": "Data Analysis Tool",
        "summary": result.content,
        "source": "analysis-tool.md",
        "processing_time": result.metadata.processing_time,
        "word_count": result.metadata.word_count,
        "char_count": result.metadata.char_count,
        "ai_enhanced": result.metadata.ai_enhanced,
        "cache_hit": result.metadata.cache_hit,
        "pipeline_steps": result.metadata.pipeline_steps,
    }
    
    # Render different templates
    print("\n📝 Default Template:")
    print("-" * 70)
    print(engine.render("default", context))
    
    print("\n📝 Compact Template:")
    print("-" * 70)
    print(engine.render("compact", context))
    
    print("\n📝 Markdown Template:")
    print("-" * 70)
    print(engine.render("markdown", context)[:200] + "...")


def demo_pipelines():
    """Demo 3: Processing pipelines."""
    print("\n" + "=" * 70)
    print("DEMO 3: Processing Pipelines")
    print("=" * 70)
    
    # Create custom pipeline
    custom_pipeline = SummaryPipeline("uppercase-demo")
    custom_pipeline.add_transform(
        "uppercase",
        lambda x: x.upper(),
        "Convert to uppercase"
    )
    custom_pipeline.add_transform(
        "add-prefix",
        lambda x: f"[SUMMARY] {x}",
        "Add prefix"
    )
    
    wrapper = SummarizerWrapper()
    wrapper.register_pipeline(custom_pipeline)
    
    readme_content = "# Test Project\n\nA simple test project."
    
    print("\n1️⃣  Without pipeline:")
    result1 = wrapper.summarize(readme_content, source="test.md")
    print(f"   {result1.content[:80]}")
    
    print("\n2️⃣  With custom pipeline:")
    result2 = wrapper.summarize(
        readme_content,
        source="test.md",
        pipeline=custom_pipeline,
        bypass_cache=True
    )
    print(f"   {result2.content[:80]}")
    print(f"   Pipeline steps: {' → '.join(result2.metadata.pipeline_steps or [])}")
    
    print("\n3️⃣  Available pipelines:")
    for pipeline_name in wrapper.list_pipelines():
        print(f"   • {pipeline_name}")


def demo_comparison():
    """Demo 4: Comparison mode."""
    print("\n" + "=" * 70)
    print("DEMO 4: Comparison Mode")
    print("=" * 70)
    
    readme_content = """
# Web Framework

A modern, fast web framework for Python developers.

## Features
- Asynchronous request handling
- Built-in ORM
- RESTful API support
- WebSocket support
- Comprehensive middleware
- Template engine
- Session management

## Performance
Benchmarks show 10x faster response times compared to traditional frameworks.

## Community
Active community with 1000+ contributors and regular updates.
    """
    
    wrapper = SummarizerWrapper(
        summarizer=ReadmeSummarizer(max_length=80)
    )
    
    print("\n🔍 Comparing different processing methods...")
    results = wrapper.compare(readme_content, methods=["standard", "technical", "user-friendly"])
    
    print("\n📊 Comparison Results:")
    print("-" * 70)
    
    for method, result in results.items():
        if isinstance(result, str):
            print(f"\n❌ {method}: {result}")
        else:
            print(f"\n✅ {method.upper()}:")
            print(f"   Content: {result.content[:100]}...")
            print(f"   Words: {result.metadata.word_count}")
            print(f"   Processing: {result.metadata.processing_time:.4f}s")


def demo_ai_enhancement():
    """Demo 5: AI enhancement (if available)."""
    print("\n" + "=" * 70)
    print("DEMO 5: AI Enhancement")
    print("=" * 70)
    
    readme_content = """
# Machine Learning Toolkit

Advanced machine learning library with state-of-the-art algorithms.

## Features
- Neural networks
- Decision trees
- Random forests
- Support vector machines
- Gradient boosting
    """
    
    # Check if Ollama is available
    ollama_enhancer = create_enhancer("ollama")
    
    if ollama_enhancer and ollama_enhancer.is_available():
        print("\n🤖 Ollama is available! Testing AI enhancement...")
        
        # Without AI
        wrapper_no_ai = SummarizerWrapper(
            summarizer=ReadmeSummarizer(max_length=50),
            ai_provider=AIProvider.NONE,
        )
        result_no_ai = wrapper_no_ai.summarize(readme_content, source="ml.md")
        
        print("\n1️⃣  Without AI:")
        print(f"   {result_no_ai.content}")
        
        # With AI
        wrapper_ai = SummarizerWrapper(
            summarizer=ReadmeSummarizer(max_length=50),
            ai_provider=AIProvider.OLLAMA,
        )
        result_ai = wrapper_ai.summarize(
            readme_content,
            source="ml-ai.md",
            bypass_cache=True
        )
        
        print("\n2️⃣  With AI Enhancement:")
        print(f"   {result_ai.content}")
        print(f"\n   AI Enhanced: {result_ai.metadata.ai_enhanced}")
    else:
        print("\n⚠️  Ollama not available. Skipping AI demo.")
        print("   Install Ollama from https://ollama.ai to enable AI features.")
        print("   Then run: ollama pull llama3.2")


def demo_metadata():
    """Demo 6: Rich metadata."""
    print("\n" + "=" * 70)
    print("DEMO 6: Rich Metadata")
    print("=" * 70)
    
    readme_content = """
# API Client Library

Simple and powerful API client for Python.

## Features
- Async/sync support
- Automatic retries
- Rate limiting
- Response caching
    """
    
    wrapper = SummarizerWrapper(
        summarizer=ReadmeSummarizer(max_length=60)
    )
    
    result = wrapper.summarize(readme_content, source="api-client.md")
    
    print("\n📈 Processing Metadata:")
    print("-" * 70)
    print(f"Source: {result.metadata.source}")
    print(f"Content Hash: {result.metadata.content_hash[:16]}...")
    print(f"Processing Time: {result.metadata.processing_time:.4f}s")
    print(f"Word Count: {result.metadata.word_count}")
    print(f"Character Count: {result.metadata.char_count}")
    print(f"Cache Hit: {result.metadata.cache_hit}")
    print(f"AI Enhanced: {result.metadata.ai_enhanced}")
    print(f"Normalizer Used: {result.metadata.normalizer_used}")
    
    # Show as JSON
    print("\n📄 As JSON:")
    print("-" * 70)
    print(result.to_json())


def demo_cache_management():
    """Demo 7: Cache management."""
    print("\n" + "=" * 70)
    print("DEMO 7: Cache Management")
    print("=" * 70)
    
    from summarize_readme.wrapper import SummaryCache
    
    cache = SummaryCache(backend=CacheBackend.MEMORY)
    
    wrapper = SummarizerWrapper(
        summarizer=ReadmeSummarizer(),
        enable_cache=True,
        cache_backend=CacheBackend.MEMORY,
    )
    wrapper.cache = cache  # Use same cache instance
    
    print("\n💾 Cache Operations:")
    
    # Generate some summaries
    for i in range(3):
        content = f"# Project {i}\n\nDescription for project {i}."
        wrapper.summarize(content, source=f"project-{i}.md")
        print(f"   ✓ Cached project-{i}.md")
    
    # Show stats
    stats = cache.stats()
    print(f"\n📊 Cache Stats:")
    print(f"   Backend: {stats['backend']}")
    print(f"   Entries: {stats['entries']}")
    
    # Clear cache
    cleared = cache.clear()
    print(f"\n🗑️  Cleared {cleared} cached entries")
    
    # Show stats again
    stats = cache.stats()
    print(f"   Entries after clear: {stats['entries']}")


def main():
    """Run all demos."""
    print("\n" + "🎁" * 35)
    print("  SUMMARIZER WRAPPER - FEATURE DEMONSTRATION")
    print("🎁" * 35 + "\n")
    
    try:
        # Run demos
        demo_basic_wrapper()
        demo_templates()
        demo_pipelines()
        demo_comparison()
        demo_ai_enhancement()
        demo_metadata()
        demo_cache_management()
        
        print("\n" + "=" * 70)
        print("✅ All demos completed successfully!")
        print("=" * 70)
        print("\n💡 Try these features in the CLI:")
        print("   readme-summarizer wrap README.md --template detailed")
        print("   readme-summarizer compare README.md")
        print("   readme-summarizer cache stats")
        print("   readme-summarizer wrap README.md --ai --ai-provider ollama")
        print("\n📚 Read more: WRAPPER_GUIDE.md")
        print("=" * 70 + "\n")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
