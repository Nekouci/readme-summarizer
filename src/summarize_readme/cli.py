"""
Advanced CLI entrypoint with comprehensive argument parsing for README Summarizer.
"""

from pathlib import Path
from typing import List, Optional
from enum import Enum
from datetime import datetime
import sys
import json

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

from .core import ReadmeSummarizer, SummaryFormat
from .utils import validate_url, read_file_content
from .input_resolver import InputResolver
from .readme_detector import READMEDetector, READMEFile
from .metadata_extractor import MetadataExtractor, extract_metadata, get_quality_report
from .formatter import READMEFormatter, FormatStyle, FormatOptions, format_readme
from .post_processor import (
    AdvancedPostProcessor,
    PostProcessorOptions,
    Theme,
    ExportFormat,
    SyntaxStyle,
    create_post_processor,
    quick_process,
)
from . import __version__


# Initialize Typer app with rich markup support
app = typer.Typer(
    name="readme-summarizer",
    help="🚀 Advanced CLI tool for summarizing README files with AI-powered insights",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=False,  # Allow running without explicit subcommand
)

console = Console()


class OutputFormat(str, Enum):
    """Output format options."""
    TEXT = "text"
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"


class SummaryLength(str, Enum):
    """Summary length presets."""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    FULL = "full"


@app.command(name="summarize", help="Summarize README file(s) (default command)")
def summarize(
    source: List[str] = typer.Argument(
        ...,
        help="README source(s): local files, URLs, GitHub repos (owner/repo), or GitHub URLs. Supports multiple inputs.",
        show_default=False,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path. If not specified, prints to console.",
        exists=False,
    ),
    format: OutputFormat = typer.Option(
        OutputFormat.TEXT,
        "--format",
        "-f",
        help="Output format for the summary.",
        case_sensitive=False,
    ),
    length: SummaryLength = typer.Option(
        SummaryLength.MEDIUM,
        "--length",
        "-l",
        help="Summary length: short (~50 words), medium (~150 words), long (~300 words), full (complete).",
        case_sensitive=False,
    ),
    bullet_points: bool = typer.Option(
        False,
        "--bullets",
        "-b",
        help="Format summary as bullet points.",
    ),
    include_badges: bool = typer.Option(
        True,
        "--badges/--no-badges",
        help="Include badge information in summary.",
    ),
    include_sections: bool = typer.Option(
        True,
        "--sections/--no-sections",
        help="Include detected sections in summary.",
    ),
    extract_links: bool = typer.Option(
        False,
        "--links",
        help="Extract and list all links from README.",
    ),
    normalize: bool = typer.Option(
        True,
        "--normalize/--no-normalize",
        help="Enable/disable content normalization and preprocessing.",
    ),
    normalization_level: str = typer.Option(
        "standard",
        "--norm-level",
        help="Normalization level: minimal, standard, or aggressive.",
    ),
    emoji_handling: str = typer.Option(
        "keep",
        "--emoji",
        help="How to handle emojis: keep, remove, or convert to text.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output with processing details.",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress all non-error output.",
    ),
) -> None:
    """
    Summarize README file(s) with advanced parsing and formatting options.
    
    [bold green]Examples:[/bold green]
    
      # Summarize a local README file
      $ readme-summarizer README.md
      
      # Summarize from GitHub repo (shorthand)
      $ readme-summarizer owner/repo
      
      # Summarize from specific branch
      $ readme-summarizer owner/repo@dev
      
      # Summarize from GitHub URL
      $ readme-summarizer https://github.com/owner/repo
      
      # Multiple sources with output to file
      $ readme-summarizer README.md owner/repo -o summary.txt
      
      # Short bullet-point summary
      $ readme-summarizer owner/repo --length short --bullets
      
      # JSON output with extracted links
      $ readme-summarizer owner/repo --format json --links -o output.json
    """
    
    if quiet and verbose:
        console.print("[yellow]Warning: --quiet and --verbose are mutually exclusive. Using --quiet.[/yellow]")
        verbose = False
    
    try:
        # Initialize summarizer and input resolver
        summarizer = ReadmeSummarizer(
            max_length=_get_max_length(length),
            include_badges=include_badges,
            include_sections=include_sections,
            bullet_points=bullet_points,
            enable_normalization=normalize,
            normalization_level=normalization_level,
            emoji_handling=emoji_handling,
        )
        
        resolver = InputResolver(verbose=verbose and not quiet)
        
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=quiet,
        ) as progress:
            
            for src in source:
                task = progress.add_task(f"Processing {src}...", total=None)
                
                if verbose and not quiet:
                    console.print(f"\n[cyan]Processing:[/cyan] {src}")
                
                # Use input resolver to fetch content
                content, metadata = resolver.resolve(src)
                
                # Generate summary
                summary = summarizer.summarize(
                    content,
                    output_format=SummaryFormat(format.value),
                    extract_links=extract_links,
                )
                
                # Collect normalization stats if enabled and verbose
                norm_stats = None
                if normalize and verbose:
                    norm_stats = summarizer.get_normalization_stats()
                
                results.append({
                    "source": src,
                    "type": metadata.get("type", "unknown"),
                    "summary": summary,
                    "metadata": metadata,
                    "normalization_stats": norm_stats,
                })
                
                progress.update(task, completed=True)
        
        # Output results
        if output:
            _write_output(results, output, format, quiet)
        else:
            _display_results(results, format, verbose, quiet)
        
        if not quiet:
            console.print("\n[bold green]✓[/bold green] Summary completed successfully!")
    
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] File not found: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1)


@app.command()
def batch(
    input_file: Path = typer.Argument(
        ...,
        help="File containing list of README paths/URLs (one per line).",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        "-d",
        help="Directory to save individual summaries. Creates one file per input.",
    ),
    format: OutputFormat = typer.Option(
        OutputFormat.TEXT,
        "--format",
        "-f",
        help="Output format for summaries.",
    ),
    continue_on_error: bool = typer.Option(
        False,
        "--continue",
        "-c",
        help="Continue processing even if some files fail.",
    ),
) -> None:
    """
    Process multiple README files from a batch input file.
    
    [bold green]Example:[/bold green]
    
      $ readme-summarizer batch sources.txt --output-dir ./summaries
    """
    
    console.print(f"[cyan]Reading batch file:[/cyan] {input_file}")
    
    # Read sources from input file
    sources = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                sources.append(line)
    
    if not sources:
        console.print("[yellow]Warning: No sources found in input file.[/yellow]")
        raise typer.Exit(code=0)
    
    console.print(f"[green]Found {len(sources)} sources to process[/green]\n")
    
    # Create output directory if specified
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each source
    success_count = 0
    error_count = 0
    
    resolver = InputResolver(verbose=False)
    
    for idx, source in enumerate(sources, 1):
        try:
            console.print(f"[{idx}/{len(sources)}] Processing: {source}")
            
            # Use input resolver to fetch content
            content, metadata = resolver.resolve(source)
            
            # Use the main summarize logic
            summarizer = ReadmeSummarizer()
            summary = summarizer.summarize(content, output_format=SummaryFormat(format.value))
            
            if output_dir:
                # Generate output filename based on metadata
                if metadata.get("type") == "github_repo":
                    source_name = f"{metadata['owner']}_{metadata['repo']}"
                elif metadata.get("type") == "local_file":
                    source_name = Path(metadata["name"]).stem
                else:
                    source_name = f"url_{idx}"
                
                output_file = output_dir / f"{source_name}_summary.{format.value}"
                output_file.write_text(summary, encoding='utf-8')
                console.print(f"  [green]✓[/green] Saved to {output_file}")
            else:
                console.print(Panel(summary, title=f"Summary: {source}", border_style="green"))
            
            success_count += 1
        
        except Exception as e:
            error_count += 1
            console.print(f"  [red]✗[/red] Error: {e}")
            if not continue_on_error:
                raise typer.Exit(code=1)
    
    # Summary
    console.print(f"\n[bold]Results:[/bold] {success_count} succeeded, {error_count} failed")


@app.command()
def normalize(
    source: str = typer.Argument(
        ...,
        help="README source: local file, URL, or GitHub repo (owner/repo).",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file for normalized content. If not specified, prints to console.",
    ),
    level: str = typer.Option(
        "standard",
        "--level",
        "-l",
        help="Normalization level: minimal, standard, or aggressive.",
    ),
    emoji_handling: str = typer.Option(
        "keep",
        "--emoji",
        help="How to handle emojis: keep, remove, or convert.",
    ),
    show_stats: bool = typer.Option(
        True,
        "--stats/--no-stats",
        help="Show normalization statistics.",
    ),
) -> None:
    """
    Normalize and preprocess README content without summarization.
    
    This command applies content normalization (whitespace cleanup, unicode fixes,
    HTML removal, etc.) and outputs the cleaned content. Useful for preprocessing
    or cleaning README files for other purposes.
    
    [bold green]Examples:[/bold green]
    
      # Normalize a README with standard settings
      $ readme-summarizer normalize README.md
      
      # Aggressive normalization with emoji removal
      $ readme-summarizer normalize owner/repo --level aggressive --emoji remove
      
      # Save normalized content to file
      $ readme-summarizer normalize README.md -o clean-readme.md
    """
    try:
        from .content_normalizer import create_normalizer
        
        # Create normalizer
        normalizer = create_normalizer(
            preset=level,
            emoji_handling=emoji_handling
        )
        
        # Fetch content
        resolver = InputResolver(verbose=False)
        content, metadata = resolver.resolve(source)
        
        console.print(f"[cyan]Normalizing:[/cyan] {source}")
        
        # Normalize content
        normalized = normalizer.normalize(content)
        stats = normalizer.get_stats()
        
        # Output
        if output:
            output.write_text(normalized, encoding='utf-8')
            console.print(f"[green]✓[/green] Saved normalized content to {output}")
        else:
            console.print("\n[bold]Normalized Content:[/bold]\n")
            console.print(normalized, markup=False, highlight=False)
        
        # Show statistics
        if show_stats:
            console.print("\n[bold yellow]Normalization Statistics:[/bold yellow]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", justify="right", style="green")
            
            table.add_row("Original Size", f"{stats.get('original_size', 0):,} bytes")
            table.add_row("Final Size", f"{stats.get('final_size', 0):,} bytes")
            table.add_row("Size Reduction", f"{stats.get('size_reduction', 0):,} bytes")
            table.add_row("Original Lines", str(stats.get('original_lines', 0)))
            table.add_row("Final Lines", str(stats.get('final_lines', 0)))
            
            if stats.get('html_tags_removed', 0) > 0:
                table.add_row("HTML Tags Removed", str(stats['html_tags_removed']))
            if stats.get('comments_removed', 0) > 0:
                table.add_row("Comments Removed", str(stats['comments_removed']))
            if stats.get('emojis_processed', 0) > 0:
                table.add_row("Emojis Processed", str(stats['emojis_processed']))
            if stats.get('headers_normalized', 0) > 0:
                table.add_row("Headers Normalized", str(stats['headers_normalized']))
            if stats.get('links_normalized', 0) > 0:
                table.add_row("Links Normalized", str(stats['links_normalized']))
            if stats.get('whitespace_normalized', 0) > 0:
                table.add_row("Whitespace Changes", str(stats['whitespace_normalized']))
            
            console.print(table)
            
            # Show percentage reduction
            if stats.get('original_size', 0) > 0:
                reduction_pct = (stats.get('size_reduction', 0) / stats['original_size']) * 100
                console.print(f"\n[bold]Total reduction:[/bold] {reduction_pct:.1f}%")
    
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def info(
    source: str = typer.Argument(
        ...,
        help="README source: local file, URL, or GitHub repo (owner/repo).",
    ),
) -> None:
    """
    Display detailed information about a README file without summarizing.
    
    Shows: file size, sections, links, badges, code blocks, etc.
    """
    
    console.print(f"[cyan]Analyzing:[/cyan] {source}\n")
    
    try:
        resolver = InputResolver(verbose=True)
        summarizer = ReadmeSummarizer()
        
        # Use input resolver to fetch content
        content, metadata = resolver.resolve(source)
        
        # Analyze content
        info_data = summarizer.analyze(content)
        
        # Create info table
        table = Table(title="README Analysis", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", width=30)
        table.add_column("Value", style="green")
        
        # Add source metadata
        table.add_row("Source Type", metadata.get("type", "unknown"))
        if metadata.get("owner") and metadata.get("repo"):
            table.add_row("Repository", f"{metadata['owner']}/{metadata['repo']}")
        if metadata.get("branch"):
            table.add_row("Branch", metadata["branch"])
        
        table.add_row("File Size", f"{info_data['size']} bytes")
        table.add_row("Lines", str(info_data['lines']))
        table.add_row("Word Count", str(info_data['words']))
        table.add_row("Sections", str(info_data['sections']))
        table.add_row("Code Blocks", str(info_data['code_blocks']))
        table.add_row("Links", str(info_data['links']))
        table.add_row("Badges", str(info_data['badges']))
        table.add_row("Images", str(info_data['images']))
        
        console.print(table)
        
        # Display section names
        if info_data.get('section_names'):
            console.print("\n[bold]Sections Found:[/bold]")
            for section in info_data['section_names']:
                console.print(f"  • {section}")
    
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def detect(
    source: str = typer.Argument(
        ...,
        help="Source to scan: local directory path or GitHub repo (owner/repo).",
    ),
    recursive: bool = typer.Option(
        True,
        "--recursive/--no-recursive",
        "-r",
        help="Scan directories recursively.",
    ),
    max_depth: int = typer.Option(
        10,
        "--max-depth",
        help="Maximum directory depth for recursive scan.",
    ),
    display: str = typer.Option(
        "table",
        "--display",
        "-d",
        help="Display mode: 'table' or 'tree'.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output.",
    ),
) -> None:
    """
    🔍 Detect and list all README files in a directory or GitHub repository.
    
    This advanced feature scans the entire directory structure or repository
    to find ALL README files, including:
    - Root README files
    - Documentation READMEs
    - Language-specific READMEs (README.fr.md, etc.)
    - Subdirectory READMEs
    
    [bold green]Examples:[/bold green]
    
      # Scan local directory
      $ readme-summarizer detect ./my-project
      
      # Scan GitHub repository
      $ readme-summarizer detect microsoft/vscode
      
      # Show as tree structure
      $ readme-summarizer detect owner/repo --display tree
      
      # Scan without recursion
      $ readme-summarizer detect ./docs --no-recursive
    """
    
    try:
        detector = READMEDetector(verbose=verbose)
        
        # Determine if source is local or GitHub
        from pathlib import Path
        import re
        
        readme_files = []
        
        # Check if it's a local directory
        if Path(source).exists() and Path(source).is_dir():
            console.print(f"[cyan]📁 Scanning local directory:[/cyan] {source}")
            readme_files = detector.scan_local_directory(
                Path(source),
                max_depth=max_depth,
                recursive=recursive
            )
        
        # Check for GitHub shorthand (owner/repo)
        elif re.match(r"^[\w-]+/[\w-]+(@[\w-]+)?$", source):
            parts = source.split("@")
            repo_part = parts[0]
            branch = parts[1] if len(parts) > 1 else None
            
            owner, repo = repo_part.split("/")
            console.print(f"[cyan]📦 Scanning GitHub repository:[/cyan] {owner}/{repo}")
            if branch:
                console.print(f"[cyan]🌿 Branch:[/cyan] {branch}")
            
            readme_files = detector.scan_github_repo(owner, repo, branch)
        
        else:
            console.print("[red]Error:[/red] Source must be a local directory or GitHub repo (owner/repo)")
            raise typer.Exit(code=1)
        
        # Display results
        console.print()
        if not readme_files:
            console.print("[yellow]⚠ No README files found.[/yellow]")
            return
        
        if display == "tree":
            detector.display_readme_tree(readme_files)
        else:
            detector.display_readme_list(readme_files, show_indices=False)
        
        # Summary
        console.print()
        console.print(f"[bold green]✓[/bold green] Found [bold]{len(readme_files)}[/bold] README file(s)")
        
        # Priority breakdown
        from collections import Counter
        priority_counts = Counter(f.priority.name for f in readme_files)
        console.print("\n[bold]By Priority:[/bold]")
        for priority, count in priority_counts.items():
            console.print(f"  • {priority.title()}: {count}")
    
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1)


@app.command()
def select(
    source: str = typer.Argument(
        ...,
        help="Source to scan: local directory path or GitHub repo (owner/repo).",
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--auto",
        "-i",
        help="Enable interactive selection mode.",
    ),
    strategy: str = typer.Option(
        "root",
        "--strategy",
        "-s",
        help="Auto-selection strategy: 'root', 'all', 'docs', 'priority'.",
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Directory to save summaries (one file per README).",
    ),
    format: OutputFormat = typer.Option(
        OutputFormat.TEXT,
        "--format",
        "-f",
        help="Output format for summaries.",
    ),
    length: SummaryLength = typer.Option(
        SummaryLength.MEDIUM,
        "--length",
        "-l",
        help="Summary length preset.",
    ),
    recursive: bool = typer.Option(
        True,
        "--recursive/--no-recursive",
        help="Scan directories recursively.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output.",
    ),
) -> None:
    """
    📚 Scan, select, and summarize multiple README files interactively.
    
    This powerful feature combines detection with interactive selection,
    allowing you to:
    - Discover all README files in a repository or directory
    - Choose which ones to summarize (single or multiple)
    - Process them in batch with consistent formatting
    
    [bold green]Examples:[/bold green]
    
      # Interactive selection from local directory
      $ readme-summarizer select ./my-project
      
      # Interactive selection from GitHub repo
      $ readme-summarizer select microsoft/TypeScript
      
      # Auto-select root README only
      $ readme-summarizer select owner/repo --auto --strategy root
      
      # Auto-select all READMEs and save to directory
      $ readme-summarizer select owner/repo --auto --strategy all --output-dir ./summaries
      
      # Select documentation READMEs
      $ readme-summarizer select ./project --auto --strategy docs
    """
    
    try:
        detector = READMEDetector(verbose=verbose)
        
        # Detect README files
        from pathlib import Path
        import re
        
        readme_files = []
        
        # Check if it's a local directory
        if Path(source).exists() and Path(source).is_dir():
            if verbose:
                console.print(f"[cyan]📁 Scanning local directory:[/cyan] {source}")
            readme_files = detector.scan_local_directory(
                Path(source),
                recursive=recursive
            )
        
        # Check for GitHub shorthand
        elif re.match(r"^[\w-]+/[\w-]+(@[\w-]+)?$", source):
            parts = source.split("@")
            repo_part = parts[0]
            branch = parts[1] if len(parts) > 1 else None
            
            owner, repo = repo_part.split("/")
            if verbose:
                console.print(f"[cyan]📦 Scanning GitHub repository:[/cyan] {owner}/{repo}")
            
            readme_files = detector.scan_github_repo(owner, repo, branch)
        
        else:
            console.print("[red]Error:[/red] Source must be a local directory or GitHub repo (owner/repo)")
            raise typer.Exit(code=1)
        
        if not readme_files:
            console.print("[yellow]⚠ No README files found.[/yellow]")
            return
        
        # Select files
        if interactive:
            selected_files = detector.interactive_select(readme_files, allow_multiple=True)
        else:
            selected_files = detector.auto_select(readme_files, strategy=strategy)
        
        if not selected_files:
            console.print("[yellow]No files selected.[/yellow]")
            return
        
        console.print(f"\n[bold green]Processing {len(selected_files)} README file(s)...[/bold green]\n")
        
        # Initialize summarizer and resolver
        summarizer = ReadmeSummarizer(
            max_length=_get_max_length(length),
            bullet_points=False,
        )
        resolver = InputResolver(verbose=False)
        
        # Create output directory if specified
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process each selected README
        results = []
        for idx, readme_file in enumerate(selected_files, 1):
            try:
                console.print(f"[{idx}/{len(selected_files)}] [cyan]Processing:[/cyan] {readme_file.relative_path}")
                
                # Fetch content
                if readme_file.is_local:
                    content = Path(readme_file.path).read_text(encoding='utf-8')
                else:
                    # Fetch from URL (GitHub raw URL)
                    content, _ = resolver.resolve(readme_file.path)
                
                # Generate summary
                summary = summarizer.summarize(
                    content,
                    output_format=SummaryFormat(format.value)
                )
                
                result = {
                    "file": readme_file.relative_path,
                    "priority": readme_file.priority.name,
                    "summary": summary,
                }
                results.append(result)
                
                # Save to file if output directory specified
                if output_dir:
                    # Generate safe filename
                    safe_name = readme_file.relative_path.replace("/", "_").replace("\\", "_")
                    output_file = output_dir / f"{Path(safe_name).stem}_summary.{format.value}"
                    output_file.write_text(summary, encoding='utf-8')
                    console.print(f"  [green]✓[/green] Saved to {output_file}")
                else:
                    # Display summary
                    console.print(Panel(
                        summary,
                        title=f"📄 {readme_file.relative_path}",
                        border_style="green",
                        subtitle=f"Priority: {readme_file.priority.name.title()}"
                    ))
                    console.print()
            
            except Exception as e:
                console.print(f"  [red]✗[/red] Error: {e}")
                if verbose:
                    console.print_exception()
        
        # Final summary
        console.print(f"\n[bold green]✓[/bold green] Successfully processed {len(results)}/{len(selected_files)} file(s)")
    
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1)


@app.command()
def wrap(
    source: str = typer.Argument(
        ...,
        help="README source: local file, URL, or GitHub repo (owner/repo).",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path.",
    ),
    template: str = typer.Option(
        "default",
        "--template",
        "-t",
        help="Output template: default, detailed, markdown, html, slack, compact, json_pretty.",
    ),
    pipeline: Optional[str] = typer.Option(
        None,
        "--pipeline",
        "-p",
        help="Processing pipeline: standard, technical, user-friendly, or custom name.",
    ),
    ai_enhance: bool = typer.Option(
        False,
        "--ai/--no-ai",
        help="Enable AI-powered enhancement (requires Ollama or HuggingFace config).",
    ),
    ai_provider: str = typer.Option(
        "ollama",
        "--ai-provider",
        help="AI provider: ollama, huggingface, or chain (tries both).",
    ),
    cache_backend: str = typer.Option(
        "filesystem",
        "--cache",
        help="Cache backend: filesystem or memory.",
    ),
    bypass_cache: bool = typer.Option(
        False,
        "--bypass-cache",
        help="Skip cache lookup and force reprocessing.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output.",
    ),
) -> None:
    """
    🎁 Advanced summarization with wrapper features.
    
    The wrapper provides intelligent orchestration with:
    - 🎨 Custom templates for output formatting
    - 🔄 Processing pipelines for different use cases
    - 🤖 AI-enhanced summaries (Ollama or HuggingFace)
    - 💾 Smart caching to avoid reprocessing
    - 📊 Detailed metadata and statistics
    
    [bold green]Examples:[/bold green]
    
      # Standard wrap with detailed template
      $ readme-summarizer wrap README.md --template detailed
      
      # AI-enhanced wrap with Ollama
      $ readme-summarizer wrap owner/repo --ai --ai-provider ollama
      
      # Technical pipeline with HTML output
      $ readme-summarizer wrap owner/repo --pipeline technical --template html -o summary.html
      
      # Slack-formatted wrap for sharing
      $ readme-summarizer wrap README.md --template slack
      
      # With custom pipeline
      $ readme-summarizer wrap README.md --pipeline custom-pipeline
    """
    
    try:
        from .wrapper import SummarizerWrapper, CacheBackend, AIProvider
        from .templates import create_template_engine
        
        if verbose:
            console.print(f"[cyan]Processing:[/cyan] {source}")
            console.print(f"[cyan]Template:[/cyan] {template}")
            if pipeline:
                console.print(f"[cyan]Pipeline:[/cyan] {pipeline}")
            if ai_enhance:
                console.print(f"[cyan]AI Provider:[/cyan] {ai_provider}")
        
        # Fetch content
        resolver = InputResolver(verbose=verbose)
        content, metadata = resolver.resolve(source)
        
        # Create wrapper
        base_summarizer = ReadmeSummarizer()
        
        ai_prov = AIProvider.NONE
        if ai_enhance:
            if ai_provider == "ollama":
                ai_prov = AIProvider.OLLAMA
            elif ai_provider == "huggingface":
                ai_prov = AIProvider.HUGGINGFACE
            elif ai_provider == "chain":
                # Use chain of both providers
                ai_prov = AIProvider.OLLAMA  # Will be handled in wrapper
        
        wrapper = SummarizerWrapper(
            summarizer=base_summarizer,
            enable_cache=True,
            cache_backend=CacheBackend(cache_backend),
            ai_provider=ai_prov,
        )
        
        if verbose:
            console.print("[yellow]Generating summary...[/yellow]")
        
        # Generate summary with wrapper
        result = wrapper.summarize(
            content=content,
            source=source,
            pipeline=pipeline,
            bypass_cache=bypass_cache,
        )
        
        # Create template engine and render
        template_engine = create_template_engine()
        
        # Extract title from metadata or content
        title = metadata.get("name", "README Summary")
        
        # Prepare context for template
        template_context = {
            "title": title,
            "summary": result.content,
            "source": source,
            "timestamp": datetime.fromtimestamp(result.metadata.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "processing_time": result.metadata.processing_time,
            "word_count": result.metadata.word_count,
            "char_count": result.metadata.char_count,
            "ai_enhanced": result.metadata.ai_enhanced,
            "cache_hit": result.metadata.cache_hit,
            "pipeline_steps": result.metadata.pipeline_steps,
        }
        
        rendered = template_engine.render(template, template_context)
        
        # Output
        if output:
            output.write_text(rendered, encoding='utf-8')
            console.print(f"[green]✓[/green] Saved to {output}")
        else:
            console.print("\n")
            console.print(rendered)
        
        # Show metadata if verbose
        if verbose:
            console.print("\n[bold yellow]Processing Details:[/bold yellow]")
            table = Table(show_header=False)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Processing Time", f"{result.metadata.processing_time:.3f}s")
            table.add_row("Word Count", str(result.metadata.word_count))
            table.add_row("Cache Hit", "Yes" if result.metadata.cache_hit else "No")
            table.add_row("AI Enhanced", "Yes" if result.metadata.ai_enhanced else "No")
            if result.metadata.pipeline_steps:
                table.add_row("Pipeline Steps", " → ".join(result.metadata.pipeline_steps))
            
            console.print(table)
    
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1)


@app.command()
def compare(
    source: str = typer.Argument(
        ...,
        help="README source: local file, URL, or GitHub repo (owner/repo).",
    ),
    methods: Optional[List[str]] = typer.Option(
        None,
        "--method",
        "-m",
        help="Pipeline to include in comparison. Can be specified multiple times.",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file for comparison results (JSON format).",
    ),
    show_diff: bool = typer.Option(
        True,
        "--diff/--no-diff",
        help="Show differences between summaries.",
    ),
) -> None:
    """
    📊 Compare summaries generated using different methods/pipelines.
    
    This feature helps you evaluate different summarization approaches:
    - Compare standard vs technical pipelines
    - See impact of different processing steps
    - Choose the best summary for your needs
    
    [bold green]Examples:[/bold green]
    
      # Compare all built-in pipelines
      $ readme-summarizer compare README.md
      
      # Compare specific methods
      $ readme-summarizer compare owner/repo -m standard -m technical
      
      # Save comparison to file
      $ readme-summarizer compare README.md -o comparison.json
    """
    
    try:
        from .wrapper import SummarizerWrapper
        
        console.print(f"[cyan]Comparing summaries for:[/cyan] {source}\n")
        
        # Fetch content
        resolver = InputResolver(verbose=False)
        content, metadata = resolver.resolve(source)
        
        # Create wrapper
        wrapper = SummarizerWrapper(
            summarizer=ReadmeSummarizer(),
            enable_cache=True,
        )
        
        # Get comparison results
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating summaries...", total=None)
            results = wrapper.compare(content, methods=methods)
            progress.update(task, completed=True)
        
        # Display results
        console.print("\n[bold]Comparison Results:[/bold]\n")
        
        for method, result in results.items():
            if isinstance(result, str):
                console.print(f"[red]✗ {method}:[/red] {result}")
            else:
                console.print(Panel(
                    result.content,
                    title=f"📋 {method.title()}",
                    border_style="blue",
                    subtitle=f"Words: {result.metadata.word_count} | Time: {result.metadata.processing_time:.3f}s"
                ))
                console.print()
        
        # Show statistics
        console.print("[bold yellow]Statistics:[/bold yellow]")
        stats_table = Table(show_header=True, header_style="bold magenta")
        stats_table.add_column("Method", style="cyan")
        stats_table.add_column("Words", justify="right")
        stats_table.add_column("Chars", justify="right")
        stats_table.add_column("Time (s)", justify="right")
        
        for method, result in results.items():
            if not isinstance(result, str):
                stats_table.add_row(
                    method.title(),
                    str(result.metadata.word_count),
                    str(result.metadata.char_count),
                    f"{result.metadata.processing_time:.3f}"
                )
        
        console.print(stats_table)
        
        # Save to JSON if requested
        if output:
            comparison_data = {}
            for method, result in results.items():
                if not isinstance(result, str):
                    comparison_data[method] = result.to_dict()
                else:
                    comparison_data[method] = {"error": result}
            
            output.write_text(json.dumps(comparison_data, indent=2), encoding='utf-8')
            console.print(f"\n[green]✓[/green] Saved comparison to {output}")
    
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def cache(
    action: str = typer.Argument(
        ...,
        help="Cache action: stats, clear, or info.",
    ),
) -> None:
    """
    💾 Manage summary cache.
    
    The cache stores processed summaries to avoid reprocessing identical content.
    
    [bold green]Actions:[/bold green]
    
      stats - Show cache statistics
      clear - Clear all cached summaries
      info  - Show cache configuration
    
    [bold green]Examples:[/bold green]
    
      # View cache statistics
      $ readme-summarizer cache stats
      
      # Clear cache
      $ readme-summarizer cache clear
    """
    
    try:
        from .wrapper import SummaryCache, CacheBackend
        
        cache = SummaryCache(backend=CacheBackend.FILESYSTEM)
        
        if action == "stats":
            stats = cache.stats()
            
            console.print("[bold]Cache Statistics:[/bold]\n")
            table = Table(show_header=False)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Backend", stats.get("backend", "unknown"))
            table.add_row("Entries", str(stats.get("entries", 0)))
            
            if "total_size_bytes" in stats:
                size_mb = stats["total_size_bytes"] / (1024 * 1024)
                table.add_row("Total Size", f"{size_mb:.2f} MB")
            
            if "cache_dir" in stats:
                table.add_row("Cache Directory", stats["cache_dir"])
            
            console.print(table)
        
        elif action == "clear":
            count = cache.clear()
            console.print(f"[green]✓[/green] Cleared {count} cached summaries")
        
        elif action == "info":
            console.print("[bold]Cache Configuration:[/bold]\n")
            console.print(f"Backend: filesystem")
            console.print(f"Location: {Path.home() / '.cache' / 'readme-summarizer'}")
            console.print(f"TTL: No expiration")
        
        else:
            console.print(f"[red]Unknown action:[/red] {action}")
            console.print("Available actions: stats, clear, info")
            raise typer.Exit(code=1)
    
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def extract(
    source: str = typer.Argument(
        ...,
        help="README source: local file, URL, or GitHub repo (owner/repo).",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path. If not specified, prints to console.",
    ),
    format: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Output format: json, yaml, or text.",
    ),
    quality: bool = typer.Option(
        False,
        "--quality",
        "-q",
        help="Include quality analysis and suggestions.",
    ),
    detailed: bool = typer.Option(
        False,
        "--detailed",
        "-d",
        help="Include detailed information (code blocks, full section content, etc.).",
    ),
) -> None:
    """
    Extract structured metadata from README files.
    
    Extracts badges, licenses, tech stack, dependencies, links, sections,
    code blocks, and more. Provides completeness scoring and quality analysis.
    
    [bold green]Examples:[/bold green]
    
      # Extract metadata as JSON
      $ readme-summarizer extract README.md
      
      # Extract with quality report
      $ readme-summarizer extract README.md --quality
      
      # Extract from GitHub repo
      $ readme-summarizer extract owner/repo -o metadata.json
      
      # Get YAML formatted metadata
      $ readme-summarizer extract README.md --format yaml
    """
    
    try:
        console.print(f"[cyan]Extracting metadata from:[/cyan] {source}")
        
        # Resolve input
        resolver = InputResolver(verbose=False)
        content, metadata = resolver.resolve(source)
        
        # Extract metadata
        extractor = MetadataExtractor()
        readme_metadata = extractor.extract(content)
        
        # Prepare output data
        output_data = readme_metadata.to_dict()
        
        # Remove detailed fields if not requested
        if not detailed:
            # Simplify sections
            output_data['section_names'] = [s.title for s in readme_metadata.sections]
            output_data.pop('sections', None)
            
            # Limit code blocks to count
            output_data['code_blocks_count'] = len(readme_metadata.code_blocks)
            output_data['code_languages'] = list(set(cb.language for cb in readme_metadata.code_blocks))
            output_data.pop('code_blocks', None)
        
        # Add quality report if requested
        if quality:
            quality_report = extractor.quality_report(readme_metadata)
            output_data['quality'] = quality_report
        
        # Format and output
        if format.lower() == "yaml":
            try:
                import yaml  # type: ignore[import-not-found]
                output_text = yaml.dump(output_data, default_flow_style=False, sort_keys=False)
            except ImportError:
                console.print("[yellow]Warning: PyYAML not installed. Falling back to JSON.[/yellow]")
                console.print("[dim]Install with: pip install pyyaml[/dim]\n")
                output_text = json.dumps(output_data, indent=2)
        elif format.lower() == "text":
            # Human-readable text format
            output_lines = []
            output_lines.append(f"=== README Metadata for {source} ===\n")
            output_lines.append(f"Title: {readme_metadata.title or 'N/A'}")
            output_lines.append(f"Description: {readme_metadata.description or 'N/A'}")
            output_lines.append(f"\nBasic Info:")
            output_lines.append(f"  Language: {readme_metadata.language or 'Not detected'}")
            output_lines.append(f"  License: {readme_metadata.license or 'Not specified'}")
            output_lines.append(f"  Version: {readme_metadata.version or 'Not specified'}")
            output_lines.append(f"\nMetrics:")
            output_lines.append(f"  Word count: {readme_metadata.word_count:,}")
            output_lines.append(f"  Line count: {readme_metadata.line_count:,}")
            output_lines.append(f"  Badges: {len(readme_metadata.badges)}")
            output_lines.append(f"  Links: {len(readme_metadata.links)}")
            output_lines.append(f"  Sections: {len(readme_metadata.sections)}")
            output_lines.append(f"  Code blocks: {len(readme_metadata.code_blocks)}")
            output_lines.append(f"\nQuality Score: {readme_metadata.completeness_score}/100")
            
            if readme_metadata.tech_stack:
                output_lines.append(f"\nTech Stack: {', '.join(readme_metadata.tech_stack[:10])}")
            
            if readme_metadata.section_names:
                output_lines.append(f"\nSections:")
                for section in readme_metadata.section_names[:15]:
                    output_lines.append(f"  • {section}")
                if len(readme_metadata.section_names) > 15:
                    output_lines.append(f"  ... and {len(readme_metadata.section_names) - 15} more")
            
            if quality:
                quality_report = extractor.quality_report(readme_metadata)
                output_lines.append(f"\n=== Quality Report ===")
                output_lines.append(f"Grade: {quality_report['grade']}")
                output_lines.append(f"Score: {quality_report['completeness_score']}/100")
                
                if quality_report['strengths']:
                    output_lines.append(f"\nStrengths:")
                    for strength in quality_report['strengths']:
                        output_lines.append(f"  ✓ {strength}")
                
                if quality_report['missing']:
                    output_lines.append(f"\nMissing Elements:")
                    for missing in quality_report['missing']:
                        output_lines.append(f"  ✗ {missing}")
                
                if quality_report['suggestions']:
                    output_lines.append(f"\nSuggestions:")
                    for suggestion in quality_report['suggestions']:
                        output_lines.append(f"  → {suggestion}")
            
            output_text = "\n".join(output_lines)
        else:
            # JSON format
            output_text = json.dumps(output_data, indent=2)
        
        # Write to file or console
        if output:
            output.write_text(output_text, encoding='utf-8')
            console.print(f"[green]✓ Metadata saved to:[/green] {output}")
        else:
            console.print()
            if format.lower() == "json":
                console.print_json(output_text)
            else:
                console.print(output_text)
            console.print()
        
        # Display summary table
        table = Table(title="Metadata Summary", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Title", readme_metadata.title or "N/A")
        table.add_row("Language", readme_metadata.language or "Not detected")
        table.add_row("License", readme_metadata.license or "Not specified")
        table.add_row("Completeness", f"{readme_metadata.completeness_score}/100")
        table.add_row("Badges", str(len(readme_metadata.badges)))
        table.add_row("Links", str(len(readme_metadata.links)))
        table.add_row("Sections", str(len(readme_metadata.sections)))
        table.add_row("Code Blocks", str(len(readme_metadata.code_blocks)))
        
        console.print()
        console.print(table)
        
        console.print("\n[bold green]✓[/bold green] Metadata extraction completed!")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def format(
    source: str = typer.Argument(
        ...,
        help="README source: local file, URL, or GitHub repo (owner/repo).",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path. If not specified, prints to console.",
    ),
    style: str = typer.Option(
        "standard",
        "--style",
        "-s",
        help="Formatting style: minimal, standard, comprehensive, library, or application.",
    ),
    add_toc: bool = typer.Option(
        True,
        "--toc/--no-toc",
        help="Add table of contents if 4+ sections exist.",
    ),
    add_missing: bool = typer.Option(
        False,
        "--add-missing",
        "-m",
        help="Add placeholders for missing standard sections.",
    ),
    fix_headings: bool = typer.Option(
        True,
        "--fix-headings/--no-fix-headings",
        help="Fix inconsistent heading levels.",
    ),
    sort_sections: bool = typer.Option(
        False,
        "--sort/--no-sort",
        help="Sort sections according to style convention.",
    ),
    emoji_style: str = typer.Option(
        "keep",
        "--emoji",
        help="Emoji handling: keep, remove, or standardize.",
    ),
    quality_improvements: bool = typer.Option(
        False,
        "--improve",
        "-i",
        help="Apply automatic quality improvements.",
    ),
    preview: bool = typer.Option(
        False,
        "--preview",
        "-p",
        help="Preview changes without saving (shows diff summary).",
    ),
) -> None:
    """
    Format and standardize README files according to best practices.
    
    Reorganizes sections, fixes formatting issues, adds missing elements,
    and ensures consistent structure according to documentation standards.
    
    [bold green]Examples:[/bold green]
    
      # Format with standard style
      $ readme-summarizer format README.md -o README_formatted.md
      
      # Format and add missing sections
      $ readme-summarizer format README.md --add-missing --style comprehensive
      
      # Format with quality improvements
      $ readme-summarizer format README.md --improve -o README.md
      
      # Preview formatting changes
      $ readme-summarizer format README.md --preview
      
      # Format for library documentation
      $ readme-summarizer format README.md --style library --sort
    """
    
    try:
        console.print(f"[cyan]Formatting README from:[/cyan] {source}")
        
        # Resolve input
        resolver = InputResolver(verbose=False)
        original_content, metadata = resolver.resolve(source)
        
        # Validate style
        try:
            format_style = FormatStyle(style.lower())
        except ValueError:
            console.print(f"[red]Error: Invalid style '{style}'. Choose from: minimal, standard, comprehensive, library, application[/red]")
            raise typer.Exit(code=1)
        
        # Create format options
        options = FormatOptions(
            style=format_style,
            add_toc=add_toc,
            fix_headings=fix_headings,
            add_missing_sections=add_missing,
            sort_sections=sort_sections,
            emoji_style=emoji_style,
        )
        
        # Format README
        formatter = READMEFormatter(options)
        
        if quality_improvements:
            formatted_content, improvements = formatter.format_quality_improvements(original_content)
            
            if improvements:
                console.print("\n[bold green]Applied improvements:[/bold green]")
                for improvement in improvements:
                    console.print(f"  ✓ {improvement}")
        else:
            formatted_content = formatter.format(original_content)
        
        # Show preview or save
        if preview:
            console.print("\n[bold yellow]=== FORMAT PREVIEW ===[/bold yellow]")
            console.print(f"Original size: {len(original_content):,} bytes")
            console.print(f"Formatted size: {len(formatted_content):,} bytes")
            console.print(f"Size change: {len(formatted_content) - len(original_content):+,} bytes")
            
            # Extract metadata from both
            extractor = MetadataExtractor()
            original_meta = extractor.extract(original_content)
            formatted_meta = extractor.extract(formatted_content)
            
            console.print(f"\n[cyan]Sections:[/cyan] {len(original_meta.sections)} → {len(formatted_meta.sections)}")
            console.print(f"[cyan]Completeness score:[/cyan] {original_meta.completeness_score} → {formatted_meta.completeness_score}")
            console.print(f"[cyan]TOC:[/cyan] {'Yes' if formatted_meta.table_of_contents else 'No'}")
            
            # Show first few lines
            console.print("\n[bold]First 15 lines:[/bold]")
            preview_lines = formatted_content.split('\n')[:15]
            console.print(Panel('\n'.join(preview_lines), border_style="cyan"))
            
            console.print("\n[dim]Use --output to save formatted README[/dim]")
        else:
            # Write to file or console
            if output:
                output.write_text(formatted_content, encoding='utf-8')
                console.print(f"\n[green]✓ Formatted README saved to:[/green] {output}")
            else:
                console.print("\n[bold cyan]=== FORMATTED README ===[/bold cyan]\n")
                console.print(formatted_content)
        
        console.print("\n[bold green]✓[/bold green] Formatting completed!")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def version() -> None:
    """Display version information."""
    console.print(f"[bold cyan]README Summarizer[/bold cyan] version [green]{__version__}[/green]")


def _get_max_length(length: SummaryLength) -> int:
    """Convert length enum to max word count."""
    length_map = {
        SummaryLength.SHORT: 50,
        SummaryLength.MEDIUM: 150,
        SummaryLength.LONG: 300,
        SummaryLength.FULL: 10000,
    }
    return length_map[length]


def _write_output(
    results: List[dict],
    output_path: Path,
    format: OutputFormat,
    quiet: bool,
) -> None:
    """Write results to output file."""
    import json
    
    if format == OutputFormat.JSON:
        output_path.write_text(json.dumps(results, indent=2), encoding='utf-8')
    else:
        # Combine all summaries
        combined = "\n\n".join([
            f"# Summary: {r['source']}\n{r['summary']}"
            for r in results
        ])
        output_path.write_text(combined, encoding='utf-8')
    
    if not quiet:
        console.print(f"[green]Output saved to:[/green] {output_path}")


def _display_results(
    results: List[dict],
    format: OutputFormat,
    verbose: bool,
    quiet: bool,
) -> None:
    """Display results to console."""
    if quiet:
        return
    
    for result in results:
        # Display normalization stats if available (in verbose mode)
        if verbose and result.get('normalization_stats'):
            stats = result['normalization_stats']
            console.print(f"\n[bold yellow]Normalization Stats:[/bold yellow]")
            console.print(f"  [dim]Original size: {stats.get('original_size', 0):,} bytes → Final size: {stats.get('final_size', 0):,} bytes[/dim]")
            console.print(f"  [dim]Size reduction: {stats.get('size_reduction', 0):,} bytes ({stats.get('size_reduction', 0) / max(stats.get('original_size', 1), 1) * 100:.1f}%)[/dim]")
            if stats.get('html_tags_removed', 0) > 0:
                console.print(f"  [dim]HTML tags removed: {stats['html_tags_removed']}[/dim]")
            if stats.get('emojis_processed', 0) > 0:
                console.print(f"  [dim]Emojis processed: {stats['emojis_processed']}[/dim]")
            if stats.get('headers_normalized', 0) > 0:
                console.print(f"  [dim]Headers normalized: {stats['headers_normalized']}[/dim]")
            console.print()
        
        if len(results) > 1:
            console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
            console.print(f"[bold]Source:[/bold] {result['source']} ({result['type']})")
            if verbose and result.get('metadata'):
                metadata = result['metadata']
                if metadata.get('owner') and metadata.get('repo'):
                    console.print(f"[dim]Repository: {metadata['owner']}/{metadata['repo']}[/dim]")
                if metadata.get('branch'):
                    console.print(f"[dim]Branch: {metadata['branch']}[/dim]")
            console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")
        
        if format == OutputFormat.MARKDOWN:
            console.print(Markdown(result['summary']))
        elif format == OutputFormat.JSON:
            import json
            console.print_json(json.dumps(result, indent=2))
        else:
            console.print(result['summary'])


@app.command(name="postprocess")
def postprocess_command(
    source: str = typer.Argument(
        ...,
        help="Content source: local file, GitHub repo (owner/repo), GitHub URL, or direct URL.",
        show_default=False,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path. If not specified, prints to console.",
    ),
    format: ExportFormat = typer.Option(
        ExportFormat.HTML_STANDALONE,
        "--format",
        "-f",
        help="Export format: html-styled, html-standalone, markdown-enhanced, json-enriched, social-snippet, pdf-ready.",
        case_sensitive=False,
    ),
    theme: Theme = typer.Option(
        Theme.GITHUB,
        "--theme",
        "-t",
        help="Visual theme: github, material, dracula, nord, monokai, minimalist, etc.",
        case_sensitive=False,
    ),
    syntax_style: SyntaxStyle = typer.Option(
        SyntaxStyle.GITHUB,
        "--syntax",
        help="Code syntax highlighting style: github, monokai, dracula, solarized, vs, tomorrow.",
        case_sensitive=False,
    ),
    add_toc: bool = typer.Option(
        True,
        "--toc/--no-toc",
        help="Add table of contents.",
    ),
    add_copy_buttons: bool = typer.Option(
        True,
        "--copy-buttons/--no-copy-buttons",
        help="Add copy buttons to code blocks (HTML only).",
    ),
    dark_mode_toggle: bool = typer.Option(
        True,
        "--dark-mode/--no-dark-mode",
        help="Enable dark mode toggle (press 'D' key in HTML).",
    ),
    metadata_title: Optional[str] = typer.Option(
        None,
        "--title",
        help="Metadata title for the document.",
    ),
    metadata_author: Optional[str] = typer.Option(
        None,
        "--author",
        help="Metadata author for the document.",
    ),
    source_info: Optional[str] = typer.Option(
        None,
        "--source",
        help="Source information to include in metadata header.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output with processing details.",
    ),
) -> None:
    """
    Apply advanced post-processing to README summaries or content.
    
    Transform plain summaries into beautifully styled, feature-rich documents with:
    - Multiple visual themes (GitHub, Material, Dracula, etc.)
    - Syntax highlighting for code blocks
    - Interactive HTML with copy buttons and dark mode
    - Social media optimized snippets
    - Enhanced Markdown with metadata
    - Analytics-enriched JSON output
    
    Supports multiple input sources:
    - Local files: README.md, summary.txt
    - GitHub repos: owner/repo, owner/repo@branch
    - GitHub URLs: https://github.com/owner/repo
    - Direct URLs: https://example.com/readme.md
    
    [bold green]Examples:[/bold green]
    
      # Local file with GitHub theme
      $ readme-summarizer postprocess summary.txt -o output.html
      
      # Fetch from GitHub repo with Material theme
      $ readme-summarizer postprocess microsoft/vscode --theme material -o styled.html
      
      # GitHub URL with social snippets
      $ readme-summarizer postprocess https://github.com/user/repo --format social-snippet -o social.json
      
      # Specific branch
      $ readme-summarizer postprocess owner/repo@dev --format html-standalone
      
      # Direct URL with dark theme
      $ readme-summarizer postprocess https://example.com/docs.md --theme dracula
      
      # Enhanced Markdown with metadata
      $ readme-summarizer postprocess input.md --format markdown-enhanced --title "My Project"
      
      # PDF-ready from GitHub
      $ readme-summarizer postprocess owner/repo --format pdf-ready --theme minimalist
    """
    
    try:
        # Initialize input resolver to fetch content from various sources
        resolver = InputResolver(verbose=verbose)
        
        if verbose:
            console.print(f"[cyan]Resolving source:[/cyan] {source}")
        
        # Fetch content using input resolver
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=verbose,  # Hide progress if verbose (to show resolver details)
        ) as progress:
            fetch_task = progress.add_task(f"Fetching content from {source}...", total=None)
            content, fetch_metadata = resolver.resolve(source)
            progress.update(fetch_task, completed=True)
        
        if verbose:
            console.print(f"[cyan]Content fetched:[/cyan] {len(content)} characters")
            console.print(f"[cyan]Source type:[/cyan] {fetch_metadata.get('type', 'unknown')}")
            if fetch_metadata.get('owner') and fetch_metadata.get('repo'):
                console.print(f"[cyan]Repository:[/cyan] {fetch_metadata['owner']}/{fetch_metadata['repo']}")
            console.print(f"[cyan]Export format:[/cyan] {format.value}")
            console.print(f"[cyan]Theme:[/cyan] {theme.value}")
        
        # Create post-processor with options
        options = PostProcessorOptions(
            theme=theme,
            syntax_style=syntax_style,
            add_table_of_contents=add_toc,
            add_copy_buttons=add_copy_buttons,
            dark_mode_toggle=dark_mode_toggle,
        )
        
        processor = AdvancedPostProcessor(options)
        
        # Build metadata from fetch metadata and user-provided values
        metadata = {}
        if metadata_title:
            metadata['title'] = metadata_title
        elif fetch_metadata.get('repo'):
            # Auto-generate title from repo name
            metadata['title'] = fetch_metadata['repo']
        
        if metadata_author:
            metadata['author'] = metadata_author
        elif fetch_metadata.get('owner'):
            # Auto-populate author from repo owner
            metadata['author'] = fetch_metadata['owner']
        
        # Use source info from fetch metadata if not provided
        if not source_info and fetch_metadata.get('url'):
            source_info = fetch_metadata['url']
        
        # Process content
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Post-processing...", total=None)
            
            result = processor.process(
                content,
                format,
                metadata if metadata else None,
                source_info,
            )
            
            progress.update(task, completed=True)
        
        # Get stats
        stats = processor.get_stats()
        
        # Output result
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(result)
            console.print(f"\n[bold green]✓[/bold green] Output saved to: {output}")
        else:
            console.print("\n" + result)
        
        # Display stats if verbose
        if verbose:
            console.print(f"\n[bold yellow]Processing Statistics:[/bold yellow]")
            console.print(f"  Input length: {stats.input_length:,} chars")
            console.print(f"  Output length:{stats.output_length:,} chars")
            console.print(f"  Code blocks highlighted: {stats.code_blocks_highlighted}")
            console.print(f"  Links processed: {stats.links_processed}")
            console.print(f"  Processing time: {stats.processing_time_ms:.2f}ms")
            console.print(f"  Theme applied: {stats.theme_applied}")
        
        console.print("\n[bold green]✓[/bold green] Post-processing completed successfully!")
    
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] Source not found: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1)


def main() -> None:
    """Main entry point."""
    import sys
    
    # If first argument doesn't look like a command and doesn't start with '-',
    # insert 'summarize' as the default command
    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        # Check if it's not a known command and not an option
        known_commands = ['summarize', 'batch', 'info', 'version', 'detect', 'select', 'normalize', 'wrap', 'compare', 'cache', 'extract', 'format', 'postprocess', '--help', '-h', '--version', '--install-completion', '--show-completion']
        if first_arg not in known_commands and not first_arg.startswith('-'):
            # Insert 'summarize' as the default command
            sys.argv.insert(1, 'summarize')
    
    app()


if __name__ == "__main__":
    main()
