# Summarizer Wrapper - Advanced Features Guide

## 🎁 Overview

The **Summarizer Wrapper** is an advanced feature suite that enhances the README Summarizer CLI with intelligent orchestration capabilities:

- **🎨 Template System** - Custom output formatting with built-in and custom templates
- **🔄 Processing Pipelines** - Chainable processing steps for different use cases
- **🤖 AI Enhancement** - Optional LLM-powered summary refinement
- **💾 Smart Caching** - Persistent caching to avoid reprocessing
- **📊 Comparison Mode** - Evaluate different summarization approaches
- **📈 Rich Metadata** - Detailed processing statistics and timing

## 🚀 Quick Start

### Basic Usage

```bash
# Use the wrapper with default settings
readme-summarizer wrap README.md

# Output with a detailed template
readme-summarizer wrap README.md --template detailed
```

### AI-Enhanced Summarization

```bash
# With Ollama (local LLM)
readme-summarizer wrap README.md --ai --ai-provider ollama

# With HuggingFace
readme-summarizer wrap README.md --ai --ai-provider huggingface

# Try both (chain)
readme-summarizer wrap README.md --ai --ai-provider chain
```

## 📋 Commands

### `wrap` - Advanced Summarization

Enhanced summarization with templates, pipelines, and AI.

```bash
readme-summarizer wrap <source> [OPTIONS]
```

**Options:**

- `--template, -t` - Output template (default, detailed, markdown, html, slack, compact)
- `--pipeline, -p` - Processing pipeline (standard, technical, user-friendly)
- `--ai/--no-ai` - Enable AI enhancement
- `--ai-provider` - AI provider (ollama, huggingface, chain)
- `--cache` - Cache backend (filesystem, memory)
- `--bypass-cache` - Force reprocessing
- `--output, -o` - Output file
- `--verbose, -v` - Verbose output

**Examples:**

```bash
# Detailed HTML output
readme-summarizer wrap owner/repo --template html -o report.html

# Technical pipeline with AI
readme-summarizer wrap README.md --pipeline technical --ai

# Slack-formatted for sharing
readme-summarizer wrap README.md --template slack

# Bypass cache for fresh processing
readme-summarizer wrap README.md --bypass-cache
```

### `compare` - Compare Summaries

Compare summaries using different pipelines/methods.

```bash
readme-summarizer compare <source> [OPTIONS]
```

**Options:**

- `--method, -m` - Pipeline to compare (repeatable)
- `--output, -o` - Save comparison to JSON
- `--diff/--no-diff` - Show differences

**Examples:**

```bash
# Compare all built-in pipelines
readme-summarizer compare README.md

# Compare specific methods
readme-summarizer compare owner/repo -m standard -m technical

# Save comparison results
readme-summarizer compare README.md -o comparison.json
```

### `cache` - Manage Cache

Manage the summary cache.

```bash
readme-summarizer cache <action>
```

**Actions:**

- `stats` - Show cache statistics
- `clear` - Clear all cached summaries
- `info` - Show cache configuration

**Examples:**

```bash
# View cache stats
readme-summarizer cache stats

# Clear cache
readme-summarizer cache clear
```

## 🎨 Templates

The wrapper includes several built-in output templates:

### Built-in Templates

1. **`default`** - Clean, simple format
2. **`detailed`** - Comprehensive with box formatting
3. **`markdown`** - Markdown-formatted output
4. **`html`** - Full HTML page with styling
5. **`slack`** - Slack-compatible formatting
6. **`compact`** - Single-line summary
7. **`json_pretty`** - Pretty-printed JSON
8. **`csv_row`** - CSV row format for spreadsheets

### Template Usage

```bash
# HTML report
readme-summarizer wrap README.md --template html -o report.html

# Slack message
readme-summarizer wrap README.md --template slack

# JSON export
readme-summarizer wrap README.md --template json_pretty -o data.json
```

### Custom Templates

You can create custom templates by creating `.tpl` files in `~/.config/readme-summarizer/templates/`:

```
{title}
{separator}

Summary: {summary}
Generated: {timestamp}
Words: {word_count} | Processing: {processing_time:.2f}s
AI Enhanced: {ai_enhanced}
```

## 🔄 Pipelines

Pipelines chain multiple processing steps together for specialized outputs.

### Built-in Pipelines

1. **`standard`** - Default processing
2. **`technical`** - Emphasizes technical content and code
3. **`user-friendly`** - Simplifies technical jargon

### Pipeline Usage

```bash
# Technical pipeline
readme-summarizer wrap README.md --pipeline technical

# User-friendly pipeline
readme-summarizer wrap README.md --pipeline user-friendly
```

## 🤖 AI Enhancement

The wrapper supports optional AI-powered summary enhancement using free/open-source LLM providers.

### Supported Providers

#### 1. **Ollama** (Recommended)

Local LLM runtime - no API keys required!

**Installation:**

1. Download from https://ollama.ai
2. Install and start Ollama
3. Pull a model: `ollama pull llama3.2`

**Usage:**

```bash
readme-summarizer wrap README.md --ai --ai-provider ollama
```

**Configuration:**

The wrapper uses these Ollama defaults:
- Model: `llama3.2`
- Host: `http://localhost:11434`
- Temperature: 0.7
- Max tokens: 250

#### 2. **HuggingFace Inference API**

Free tier available (no credit card required for public models).

**Setup:**

1. Sign up at https://huggingface.co
2. Get API token (optional for free tier)
3. Set environment variable: `export HF_API_TOKEN=your_token`

**Usage:**

```bash
readme-summarizer wrap README.md --ai --ai-provider huggingface
```

**Configuration:**

- Default model: `facebook/bart-large-cnn`
- Free tier has rate limits
- Some models may have loading time

#### 3. **Chain Provider**

Try multiple providers in sequence (Ollama → HuggingFace).

```bash
readme-summarizer wrap README.md --ai --ai-provider chain
```

### AI Enhancement Benefits

- **Improved Clarity** - More concise and readable
- **Better Structure** - Enhanced organization
- **Professional Tone** - Polished language
- **Key Information** - Preserves important details

## 💾 Caching

The wrapper includes smart caching to avoid reprocessing identical content.

### Cache Backends

1. **Filesystem** (default) - Persistent across sessions
2. **Memory** - Fast but temporary

### Cache Behavior

- Caches based on content + configuration hash
- Automatic cache hits for identical requests
- Optional TTL (time-to-live) support
- Cache statistics available

### Cache Management

```bash
# View cache statistics
readme-summarizer cache stats

# Clear cache
readme-summarizer cache clear

# Bypass cache for fresh processing
readme-summarizer wrap README.md --bypass-cache
```

## 📊 Metadata & Statistics

Every wrapper operation includes detailed metadata:

- **Processing time** - Millisecond precision
- **Word count** - Total words in summary
- **Character count** - Total characters
- **Cache hit** - Whether cached result was used
- **AI enhanced** - Whether AI was applied
- **Pipeline steps** - Processing steps executed
- **Content hash** - SHA-256 hash for caching
- **Timestamp** - When summary was generated

View metadata with `--verbose`:

```bash
readme-summarizer wrap README.md --verbose
```

## 🔧 Advanced Features

### Chaining with Other Commands

```bash
# Normalize then wrap
readme-summarizer normalize README.md -o clean.md
readme-summarizer wrap clean.md --template detailed

# Batch wrap with custom template
for file in $(readme-summarizer detect ./docs --format json | jq -r '.files[]'); do
  readme-summarizer wrap "$file" --template markdown -o "summaries/${file}.md"
done
```

### Integration Examples

#### Slack Notifications

```bash
# Generate Slack-formatted summary
summary=$(readme-summarizer wrap owner/repo --template slack)

# Send to Slack webhook
curl -X POST -H 'Content-type: application/json' \
  --data "{\"text\": \"$summary\"}" \
  "$SLACK_WEBHOOK_URL"
```

#### HTML Reports

```bash
# Generate HTML report for repository
readme-summarizer wrap microsoft/vscode \
  --template html \
  --pipeline technical \
  --ai \
  -o vscode-summary.html

# Open in browser
open vscode-summary.html  # macOS
# or
start vscode-summary.html  # Windows
```

#### CI/CD Integration

```bash
# In GitHub Actions workflow
- name: Generate README summary
  run: |
    readme-summarizer wrap README.md \
      --template json_pretty \
      -o summary.json
    
    # Upload as artifact
    gh api repos/${{ github.repository }}/releases/${{ github.event.release.id }}/assets \
      --method POST \
      --file summary.json
```

## 🎯 Use Cases

### 1. Documentation Generation

```bash
readme-summarizer wrap owner/repo \
  --template detailed \
  --pipeline technical \
  -o docs/project-summary.md
```

### 2. Quick Project Overview

```bash
readme-summarizer wrap README.md --template compact
```

### 3. Code Review Preparation

```bash
readme-summarizer compare README.md \
  -m standard \
  -m technical \
  -o review-notes.json
```

### 4. Team Sharing

```bash
readme-summarizer wrap owner/repo --template slack | pbcopy
# Paste into Slack
```

### 5. AI-Enhanced Summaries

```bash
readme-summarizer wrap complex-project/README.md \
  --ai \
  --ai-provider ollama \
  --template markdown \
  -o ai-summary.md
```

## 🔍 Troubleshooting

### Ollama Not Available

**Error:** "Ollama not available"

**Solution:**
1. Check Ollama is running: `ollama list`
2. Start Ollama service
3. Pull a model: `ollama pull llama3.2`

### HuggingFace API Errors

**Error:** "Model loading" or 503 errors

**Solution:**
- Wait a few seconds and retry
- Free tier models may take time to load
- Use `--ai-provider chain` to fallback

### Cache Issues

**Problem:** Old summaries being returned

**Solution:**
```bash
# Clear cache
readme-summarizer cache clear

# Or bypass cache
readme-summarizer wrap README.md --bypass-cache
```

### Template Not Found

**Error:** "Unknown template: custom"

**Solution:**
- Check template name: `readme-summarizer wrap --help`
- Ensure custom template file exists in config directory

## 📚 API Reference

### SummarizerWrapper Class

```python
from summarize_readme.wrapper import SummarizerWrapper, CacheBackend, AIProvider

wrapper = SummarizerWrapper(
    summarizer=ReadmeSummarizer(),
    enable_cache=True,
    cache_backend=CacheBackend.FILESYSTEM,
    ai_provider=AIProvider.OLLAMA,
)

result = wrapper.summarize(
    content="README content...",
    source="README.md",
    pipeline="technical",
)

print(result.content)
print(result.metadata)
```

### Template Engine

```python
from summarize_readme.templates import create_template_engine

engine = create_template_engine()

output = engine.render("detailed", {
    "title": "My Project",
    "summary": "A great project...",
    "source": "README.md",
})

print(output)
```

## 🌟 Best Practices

1. **Use Templates** - Choose appropriate template for your use case
2. **Enable Caching** - Speeds up repeated operations significantly
3. **Try Pipelines** - Different pipelines for different audiences
4. **AI Enhancement** - Use for complex READMEs, but test quality
5. **Compare Methods** - Evaluate different approaches before deciding
6. **Verbose Mode** - Use `--verbose` to understand processing

## 📝 Notes

- AI enhancement requires external services (Ollama or HuggingFace)
- Cache is stored in `~/.cache/readme-summarizer/`
- Templates can be customized in `~/.config/readme-summarizer/templates/`
- Processing time includes AI enhancement if enabled
- Cache keys are based on content + configuration hash

## 🔗 Related Features

- [Content Normalizer](CONTENT_NORMALIZER.md) - Content preprocessing
- [File Detector](FILE_DETECTOR.md) - Multi-README discovery
- [Input Resolver](INPUT_RESOLVER.md) - Flexible input handling

## 🎓 Examples Repository

More examples available at: https://github.com/yourusername/summarize-readme/tree/main/examples/wrapper

---

**Need help?** Open an issue at https://github.com/yourusername/summarize-readme/issues
