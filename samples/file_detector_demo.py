"""
Demo script for the File Detector / README Selector feature.

This script demonstrates the various capabilities of the advanced
file detection and selection system.
"""

from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from summarize_readme.readme_detector import READMEDetector, READMEPriority
from summarize_readme.input_resolver import InputResolver
from summarize_readme.core import ReadmeSummarizer, SummaryFormat


console = Console()


def demo_local_detection():
    """Demo: Detect README files in a local directory."""
    console.print(Panel.fit(
        "[bold cyan]Demo 1: Local Directory Detection[/bold cyan]",
        border_style="blue"
    ))
    
    # Initialize detector
    detector = READMEDetector(verbose=True)
    
    # Scan current directory
    current_dir = Path.cwd()
    console.print(f"\n[yellow]Scanning:[/yellow] {current_dir}\n")
    
    try:
        readme_files = detector.scan_local_directory(
            current_dir,
            recursive=True,
            max_depth=3
        )
        
        if readme_files:
            console.print("\n[bold green]Found README files:[/bold green]")
            detector.display_readme_list(readme_files, show_indices=True)
            
            # Show tree view
            console.print("\n[bold green]Tree view:[/bold green]")
            detector.display_readme_tree(readme_files)
        else:
            console.print("[yellow]No README files found.[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


def demo_github_detection():
    """Demo: Detect README files in a GitHub repository."""
    console.print(Panel.fit(
        "[bold cyan]Demo 2: GitHub Repository Detection[/bold cyan]",
        border_style="blue"
    ))
    
    # Initialize detector
    detector = READMEDetector(verbose=True)
    
    # Example repositories with multiple READMEs
    repos = [
        ("microsoft", "TypeScript"),
        ("facebook", "react"),
    ]
    
    for owner, repo in repos:
        console.print(f"\n[yellow]Scanning:[/yellow] {owner}/{repo}\n")
        
        try:
            readme_files = detector.scan_github_repo(owner, repo)
            
            if readme_files:
                console.print(f"\n[bold green]Found {len(readme_files)} README files:[/bold green]")
                detector.display_readme_list(readme_files, show_indices=False)
            else:
                console.print("[yellow]No README files found.[/yellow]")
            
            console.print("\n" + "─" * 60)
        
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
        
        break  # Only demo first repo to avoid rate limiting


def demo_auto_selection():
    """Demo: Automatic selection strategies."""
    console.print(Panel.fit(
        "[bold cyan]Demo 3: Auto-Selection Strategies[/bold cyan]",
        border_style="blue"
    ))
    
    detector = READMEDetector(verbose=False)
    
    # Scan current directory
    current_dir = Path.cwd()
    try:
        readme_files = detector.scan_local_directory(current_dir, max_depth=3)
        
        if not readme_files:
            console.print("[yellow]No README files found in current directory.[/yellow]")
            return
        
        console.print(f"\n[bold]Discovered {len(readme_files)} README files[/bold]\n")
        
        # Try different strategies
        strategies = ["root", "docs", "all", "priority"]
        
        for strategy in strategies:
            console.print(f"\n[cyan]Strategy:[/cyan] [bold]{strategy}[/bold]")
            selected = detector.auto_select(readme_files, strategy=strategy)
            console.print(f"[green]Selected {len(selected)} file(s):[/green]")
            for f in selected:
                console.print(f"  • {f.relative_path} ({f.priority.name})")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


def demo_priority_system():
    """Demo: Priority-based organization."""
    console.print(Panel.fit(
        "[bold cyan]Demo 4: Priority System[/bold cyan]",
        border_style="blue"
    ))
    
    detector = READMEDetector(verbose=False)
    
    current_dir = Path.cwd()
    try:
        readme_files = detector.scan_local_directory(current_dir, max_depth=3)
        
        if not readme_files:
            console.print("[yellow]No README files found.[/yellow]")
            return
        
        # Group by priority
        from collections import defaultdict
        priority_groups = defaultdict(list)
        
        for readme in readme_files:
            priority_groups[readme.priority].append(readme)
        
        console.print("\n[bold]READMEs grouped by priority:[/bold]\n")
        
        for priority in READMEPriority:
            files = priority_groups.get(priority, [])
            if files:
                icon = "⭐" if priority == READMEPriority.ROOT else "📄"
                console.print(f"\n{icon} [cyan]{priority.name}[/cyan] ({len(files)} file(s)):")
                for f in files:
                    console.print(f"  • {f.relative_path}")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


def demo_integrated_workflow():
    """Demo: Complete workflow with detection and summarization."""
    console.print(Panel.fit(
        "[bold cyan]Demo 5: Integrated Workflow[/bold cyan]",
        border_style="blue"
    ))
    
    detector = READMEDetector(verbose=False)
    resolver = InputResolver(verbose=False)
    summarizer = ReadmeSummarizer(max_length=100)
    
    current_dir = Path.cwd()
    
    try:
        # Step 1: Detect
        console.print("\n[bold]Step 1: Detecting README files...[/bold]")
        readme_files = detector.scan_local_directory(current_dir, max_depth=2)
        console.print(f"[green]✓[/green] Found {len(readme_files)} files")
        
        if not readme_files:
            return
        
        # Step 2: Select (auto-select root only for demo)
        console.print("\n[bold]Step 2: Auto-selecting root README...[/bold]")
        selected = detector.auto_select(readme_files, strategy="root")
        console.print(f"[green]✓[/green] Selected {len(selected)} file(s)")
        
        if not selected:
            return
        
        # Step 3: Process
        console.print("\n[bold]Step 3: Processing and summarizing...[/bold]")
        for readme in selected:
            console.print(f"\n[cyan]Processing:[/cyan] {readme.relative_path}")
            
            try:
                # Read content
                content = Path(readme.path).read_text(encoding='utf-8')
                
                # Generate summary
                summary = summarizer.summarize(
                    content,
                    output_format=SummaryFormat.TEXT
                )
                
                # Display
                console.print(Panel(
                    summary,
                    title=f"📄 {readme.name}",
                    border_style="green"
                ))
            
            except Exception as e:
                console.print(f"[red]Error processing file:[/red] {e}")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


def demo_programmatic_usage():
    """Demo: Using the detector programmatically."""
    console.print(Panel.fit(
        "[bold cyan]Demo 6: Programmatic API Usage[/bold cyan]",
        border_style="blue"
    ))
    
    console.print("\n[bold]Example: Using InputResolver with detection[/bold]\n")
    
    # Show code example
    code = '''
from summarize_readme.input_resolver import InputResolver

resolver = InputResolver(verbose=True)

# Multi-file resolution with detection
results = resolver.resolve_with_detection(
    source="./my-project",
    auto_select_strategy="docs",
    interactive=False
)

for content, metadata in results:
    detector_info = metadata.get("detector", {})
    print(f"File: {detector_info['relative_path']}")
    print(f"Priority: {detector_info['priority']}")
    print(f"Size: {len(content)} bytes")
    '''
    
    from rich.syntax import Syntax
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    
    console.print("\n[dim]This API allows seamless integration into your own projects![/dim]")


def main():
    """Run all demos."""
    console.print("\n[bold magenta]╔═══════════════════════════════════════════════════════════╗[/bold magenta]")
    console.print("[bold magenta]║    File Detector / README Selector - Feature Demo       ║[/bold magenta]")
    console.print("[bold magenta]╚═══════════════════════════════════════════════════════════╝[/bold magenta]\n")
    
    demos = [
        ("Local Detection", demo_local_detection),
        ("GitHub Detection", demo_github_detection),
        ("Auto-Selection", demo_auto_selection),
        ("Priority System", demo_priority_system),
        ("Integrated Workflow", demo_integrated_workflow),
        ("Programmatic Usage", demo_programmatic_usage),
    ]
    
    for idx, (name, demo_func) in enumerate(demos, 1):
        console.print(f"\n{'='*60}")
        console.print(f"[bold yellow]Demo {idx}/{len(demos)}: {name}[/bold yellow]")
        console.print(f"{'='*60}\n")
        
        try:
            demo_func()
        except KeyboardInterrupt:
            console.print("\n[yellow]Demo interrupted by user.[/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]Demo failed:[/red] {e}")
        
        console.print()
    
    console.print("\n[bold green]✓ Demo completed![/bold green]")
    console.print("\n[dim]For more information, see FILE_DETECTOR.md[/dim]")


if __name__ == "__main__":
    main()
