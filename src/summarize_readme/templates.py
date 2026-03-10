"""
Template system for customizable summary output formatting.

Supports Jinja2-based templates with predefined and custom templates.
"""

from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime
import json


class TemplateEngine:
    """
    Simple template engine for formatting summary output.
    
    Uses Python string formatting with dictionaries for simplicity.
    Can be extended to use Jinja2 for more complex templates.
    """
    
    BUILTIN_TEMPLATES = {
        "default": """
{title}
{separator}

{summary}

Generated: {timestamp}
Source: {source}
""",
        
        "detailed": """
╔═══════════════════════════════════════════════════╗
║           README SUMMARY REPORT                   ║
╚═══════════════════════════════════════════════════╝

Title: {title}
Source: {source}
Generated: {timestamp}

─────────────────────────────────────────────────────
SUMMARY
─────────────────────────────────────────────────────
{summary}

─────────────────────────────────────────────────────
METADATA
─────────────────────────────────────────────────────
Processing Time: {processing_time:.3f}s
Word Count: {word_count}
Character Count: {char_count}
AI Enhanced: {ai_enhanced}
Cache Hit: {cache_hit}
{pipeline_info}
""",
        
        "markdown": """# {title}

## Summary

{summary}

---

**Metadata:**
- Source: `{source}`
- Generated: {timestamp}
- Processing Time: {processing_time:.3f}s
- Word Count: {word_count}
- AI Enhanced: {ai_enhanced}
{pipeline_info}
""",
        
        "json_pretty": """{json_data}""",
        
        "slack": """*{title}*

{summary}

_Generated: {timestamp} | Source: {source}_
""",
        
        "html": """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        .header {{
            border-bottom: 3px solid #0066cc;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .summary {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .metadata {{
            font-size: 0.9em;
            color: #666;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            margin-right: 5px;
        }}
        .badge.ai {{
            background: #4CAF50;
            color: white;
        }}
        .badge.cached {{
            background: #2196F3;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
    </div>
    
    <div class="summary">
        {summary_html}
    </div>
    
    <div class="metadata">
        <strong>Source:</strong> <code>{source}</code><br>
        <strong>Generated:</strong> {timestamp}<br>
        <strong>Processing Time:</strong> {processing_time:.3f}s<br>
        <strong>Word Count:</strong> {word_count}<br>
        
        <div style="margin-top: 10px;">
            {ai_badge}
            {cache_badge}
        </div>
        
        {pipeline_info}
    </div>
</body>
</html>
""",
        
        "compact": "{title} - {summary} ({word_count} words, {processing_time:.2f}s)",
        
        "csv_row": '"{title}","{source}","{summary_escaped}",{word_count},{processing_time:.3f},{ai_enhanced},{timestamp}',
    }
    
    def __init__(self, custom_templates: Optional[Dict[str, str]] = None):
        """
        Initialize template engine.
        
        Args:
            custom_templates: Dictionary of custom template names to template strings
        """
        self.templates = dict(self.BUILTIN_TEMPLATES)
        if custom_templates:
            self.templates.update(custom_templates)
    
    def render(
        self,
        template_name: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Render a template with the given context.
        
        Args:
            template_name: Name of the template to use
            context: Dictionary of values to substitute in template
        
        Returns:
            Rendered template string
        """
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}. Available: {self.list_templates()}")
        
        template = self.templates[template_name]
        
        # Prepare context with default values
        prepared_context = self._prepare_context(context, template_name)
        
        try:
            return template.format(**prepared_context)
        except KeyError as e:
            raise ValueError(f"Missing required context key: {e}")
    
    def _prepare_context(self, context: Dict[str, Any], template_name: str) -> Dict[str, Any]:
        """Prepare context with default values and transformations."""
        prepared = dict(context)
        
        # Ensure required fields exist with defaults
        prepared.setdefault("title", "README Summary")
        prepared.setdefault("summary", "")
        prepared.setdefault("source", "unknown")
        prepared.setdefault("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        prepared.setdefault("processing_time", 0.0)
        prepared.setdefault("word_count", 0)
        prepared.setdefault("char_count", 0)
        prepared.setdefault("ai_enhanced", False)
        prepared.setdefault("cache_hit", False)
        prepared.setdefault("pipeline_steps", None)
        
        # Add computed fields
        prepared["separator"] = "=" * len(prepared["title"])
        
        # Format pipeline info
        if prepared["pipeline_steps"]:
            steps_str = " → ".join(prepared["pipeline_steps"])
            prepared["pipeline_info"] = f"Pipeline: {steps_str}"
        else:
            prepared["pipeline_info"] = ""
        
        # Template-specific transformations
        if template_name == "html":
            prepared["summary_html"] = prepared["summary"].replace("\n", "<br>\n")
            prepared["ai_badge"] = '<span class="badge ai">AI Enhanced</span>' if prepared["ai_enhanced"] else ""
            prepared["cache_badge"] = '<span class="badge cached">Cached</span>' if prepared["cache_hit"] else ""
        
        elif template_name == "json_pretty":
            prepared["json_data"] = json.dumps(
                {k: v for k, v in prepared.items() if k != "json_data"},
                indent=2,
                default=str
            )
        
        elif template_name == "csv_row":
            # Escape quotes in summary for CSV
            prepared["summary_escaped"] = prepared["summary"].replace('"', '""')
        
        return prepared
    
    def render_from_result(self, result, template_name: str = "default") -> str:
        """
        Render a template from a SummaryResult object.
        
        Args:
            result: SummaryResult instance
            template_name: Template to use
        
        Returns:
            Rendered output
        """
        from .wrapper import SummaryResult
        
        if not isinstance(result, SummaryResult):
            raise TypeError("Expected SummaryResult instance")
        
        context = {
            "title": "README Summary",
            "summary": result.content,
            "source": result.metadata.source,
            "timestamp": datetime.fromtimestamp(result.metadata.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "processing_time": result.metadata.processing_time,
            "word_count": result.metadata.word_count,
            "char_count": result.metadata.char_count,
            "ai_enhanced": result.metadata.ai_enhanced,
            "cache_hit": result.metadata.cache_hit,
            "pipeline_steps": result.metadata.pipeline_steps,
        }
        
        return self.render(template_name, context)
    
    def add_template(self, name: str, template: str) -> None:
        """Add or update a template."""
        self.templates[name] = template
    
    def remove_template(self, name: str) -> None:
        """Remove a template."""
        if name in self.BUILTIN_TEMPLATES:
            raise ValueError(f"Cannot remove built-in template: {name}")
        if name in self.templates:
            del self.templates[name]
    
    def list_templates(self) -> list[str]:
        """Get list of available template names."""
        return list(self.templates.keys())
    
    def get_template(self, name: str) -> str:
        """Get the template string for a given name."""
        if name not in self.templates:
            raise ValueError(f"Unknown template: {name}")
        return self.templates[name]
    
    def save_template(self, name: str, filepath: Path) -> None:
        """Save a template to a file."""
        if name not in self.templates:
            raise ValueError(f"Unknown template: {name}")
        
        filepath.write_text(self.templates[name], encoding="utf-8")
    
    def load_template(self, name: str, filepath: Path) -> None:
        """Load a template from a file."""
        template = filepath.read_text(encoding="utf-8")
        self.add_template(name, template)


def create_template_engine(
    custom_templates_dir: Optional[Path] = None
) -> TemplateEngine:
    """
    Create a template engine with optional custom templates from directory.
    
    Args:
        custom_templates_dir: Directory containing .tpl or .txt template files
    
    Returns:
        TemplateEngine instance
    """
    custom_templates = {}
    
    if custom_templates_dir and custom_templates_dir.exists():
        for template_file in custom_templates_dir.glob("*.tpl"):
            name = template_file.stem
            template = template_file.read_text(encoding="utf-8")
            custom_templates[name] = template
    
    return TemplateEngine(custom_templates=custom_templates)
