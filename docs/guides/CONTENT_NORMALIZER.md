# Content Normalizer / Preprocessor

## 🎯 Overview

The **Content Normalizer / Preprocessor** is an advanced feature that cleans, standardizes, and normalizes README content before summarization. It handles various edge cases, encoding issues, and formatting inconsistencies to improve parsing accuracy and output quality.

## ✨ Key Features

### 🧹 Comprehensive Cleaning
- **Unicode Normalization**: Fixes encoding issues and normalizes unicode characters
- **HTML Removal**: Strips HTML tags while preserving content
- **Comment Removal**: Removes HTML and markdown comments
- **Whitespace Normalization**: Cleans up excessive spaces, tabs, and newlines

### 🎨 Format Standardization
- **Header Normalization**: Standardizes markdown header formatting (ATX and Setext styles)
- **Link Standardization**: Fixes malformed links and image references
- **Code Block Preservation**: Protects code blocks from normalization
- **Emoji Handling**: Keep, remove, or convert emojis to text

### 📊 Statistics Tracking
- Original and final file sizes
- Count of removed elements (HTML tags, comments, emojis)
- Number of normalized headers and links
- Whitespace changes and file size reduction

## 🚀 Quick Start

### Using with Summarize Command

By default, normalization is **enabled** for all summarization operations:

```bash
# Standard normalization (default)
readme-summarizer summarize README.md

# Disable normalization
readme-summarizer summarize README.md --no-normalize

# Aggressive normalization with emoji removal
readme-summarizer summarize README.md --norm-level aggressive --emoji remove

# Show normalization statistics
readme-summarizer summarize README.md -v
```

### Standalone Normalize Command

Use the `normalize` command to preprocess README files without summarization:

```bash
# Normalize a README file
readme-summarizer normalize README.md

# Save normalized content to file
readme-summarizer normalize README.md -o clean-readme.md

# Aggressive normalization
readme-summarizer normalize owner/repo --level aggressive

# Remove emojis during normalization
readme-summarizer normalize README.md --emoji remove
```

## 📖 Normalization Levels

### Minimal
Light preprocessing with essential fixes only:
- Basic whitespace cleanup
- Unicode encoding fixes
- Minimal HTML handling

**Use case**: When you want to preserve most original formatting

```bash
readme-summarizer summarize README.md --norm-level minimal
```

### Standard (Default)
Balanced preprocessing for most use cases:
- Unicode normalization
- HTML and comment removal
- Whitespace normalization
- Header standardization
- Link formatting fixes

**Use case**: Default choice for most README files

```bash
readme-summarizer summarize README.md --norm-level standard
```

### Aggressive
Maximum cleaning and standardization:
- All standard normalizations
- Aggressive HTML removal
- Extensive whitespace cleanup
- Complete header and link normalization
- Optional emoji removal

**Use case**: Heavily formatted or messy README files

```bash
readme-summarizer summarize README.md --norm-level aggressive
```

## 🎭 Emoji Handling

Control how emojis are processed during normalization:

### Keep (Default)
Preserves all emojis in the content:
```bash
readme-summarizer normalize README.md --emoji keep
```

**Input**: `# 🚀 My Project`  
**Output**: `# 🚀 My Project`

### Remove
Strips all emojis from the content:
```bash
readme-summarizer normalize README.md --emoji remove
```

**Input**: `# 🚀 My Project`  
**Output**: `# My Project`

### Convert
Converts common emojis to text descriptions:
```bash
readme-summarizer normalize README.md --emoji convert
```

**Input**: `# 🚀 My Project`  
**Output**: `# [rocket] My Project`

**Supported emoji conversions**:
- 🚀 → `[rocket]`
- ✨ → `[sparkles]`
- 📦 → `[package]`
- 🔧 → `[wrench]`
- 🎨 → `[art]`
- 🐛 → `[bug]`
- 📝 → `[memo]`
- 🔥 → `[fire]`
- ✅ → `[check]`
- ❌ → `[x]`
- ⚠️ → `[warning]`
- 💡 → `[bulb]`
- 📖 → `[book]`
- 🌟 → `[star]`
- 🎯 → `[target]`
- 🔍 → `[search]`

## 💻 Programmatic Usage

### Basic Usage

```python
from summarize_readme.content_normalizer import ContentNormalizer, NormalizationLevel, EmojiHandling

# Create normalizer with default settings
normalizer = ContentNormalizer()

# Normalize content
content = """
# 🚀 My Project

<div align="center">Some HTML</div>

Regular content here.
"""

normalized = normalizer.normalize(content)
print(normalized)

# Get statistics
stats = normalizer.get_stats()
print(f"Size reduction: {stats['size_reduction']} bytes")
```

### Advanced Configuration

```python
from summarize_readme.content_normalizer import ContentNormalizer, NormalizationLevel, EmojiHandling

# Custom normalizer
normalizer = ContentNormalizer(
    level=NormalizationLevel.AGGRESSIVE,
    emoji_handling=EmojiHandling.REMOVE,
    remove_html=True,
    remove_comments=True,
    normalize_whitespace=True,
    normalize_headers=True,
    preserve_code_blocks=True,
    fix_unicode=True,
    remove_excessive_newlines=True,
    standardize_links=True,
)

normalized = normalizer.normalize(content)
```

### Using Factory Function

```python
from summarize_readme.content_normalizer import create_normalizer

# Create with preset
normalizer = create_normalizer("standard")

# Create with custom overrides
normalizer = create_normalizer(
    preset="aggressive",
    emoji_handling="remove",
    normalize_headers=False  # Override specific setting
)
```

### Integration with ReadmeSummarizer

```python
from summarize_readme.core import ReadmeSummarizer

# Summarizer with normalization enabled
summarizer = ReadmeSummarizer(
    enable_normalization=True,
    normalization_level="standard",
    emoji_handling="keep"
)

summary = summarizer.summarize(content)

# Get normalization stats from last operation
stats = summarizer.get_normalization_stats()
if stats:
    print(f"Normalized {stats['original_size']} → {stats['final_size']} bytes")
```

## 📋 Configuration Options

### ContentNormalizer Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `NormalizationLevel` | `STANDARD` | Overall normalization intensity |
| `emoji_handling` | `EmojiHandling` | `KEEP` | How to handle emojis |
| `remove_html` | `bool` | `True` | Remove HTML tags |
| `remove_comments` | `bool` | `True` | Remove HTML/markdown comments |
| `normalize_whitespace` | `bool` | `True` | Normalize spaces and tabs |
| `normalize_headers` | `bool` | `True` | Standardize header formatting |
| `preserve_code_blocks` | `bool` | `True` | Protect code blocks during normalization |
| `fix_unicode` | `bool` | `True` | Fix unicode encoding issues |
| `remove_excessive_newlines` | `bool` | `True` | Remove 3+ consecutive newlines |
| `standardize_links` | `bool` | `True` | Normalize link formatting |

## 📊 Normalization Statistics

When verbose mode is enabled (`-v`), detailed statistics are displayed:

```bash
readme-summarizer summarize README.md -v
```

**Example output**:
```
Normalization Stats:
  Original size: 5432 bytes
  Final size: 4891 bytes
  Size reduction: 541 bytes
  HTML tags removed: 12
  Emojis processed: 5
  Headers normalized: 8
```

Use the standalone `normalize` command to see detailed statistics:

```bash
readme-summarizer normalize README.md --stats
```

**Example table output**:
```
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Metric              ┃        Value ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ Original Size       │    5,432 bytes │
│ Final Size          │    4,891 bytes │
│ Size Reduction      │      541 bytes │
│ Original Lines      │          187 │
│ Final Lines         │          165 │
│ HTML Tags Removed   │           12 │
│ Emojis Processed    │            5 │
│ Headers Normalized  │            8 │
└─────────────────────┴──────────────┘

Total reduction: 9.9%
```

## 🔧 What Gets Normalized

### Unicode & Encoding
- ✅ Non-breaking spaces (U+00A0) → regular spaces
- ✅ Smart quotes (" " ' ') → regular quotes
- ✅ Em/en dashes (— –) → hyphens
- ✅ Ellipsis (…) → three periods
- ✅ Zero-width characters removed
- ✅ HTML entities decoded

### HTML & Comments
- ✅ All HTML tags removed (content preserved)
- ✅ Script and style tags completely removed
- ✅ HTML comments removed
- ✅ Inline styles removed

### Whitespace
- ✅ Tabs → 4 spaces
- ✅ Trailing whitespace removed
- ✅ Multiple consecutive spaces reduced
- ✅ More than 2 newlines → 2 newlines
- ✅ File ends with single newline

### Markdown Headers
- ✅ ATX headers standardized: `#Title` → `# Title`
- ✅ Trailing hashes removed: `## Title ##` → `## Title`
- ✅ Setext headers converted: Underlined → ATX style
- ✅ Consistent spacing after hash marks

### Links & Images
- ✅ Extra spaces removed: `[ link ]( url )` → `[link](url)`
- ✅ Consistent formatting applied
- ✅ Malformed links fixed

### Code Blocks
- ✅ **Preserved exactly as-is**
- ✅ Protected from all normalizations
- ✅ Includes both fenced (```) and inline code

## 🎯 Use Cases

### 1. Improving Summarization Accuracy
Normalization removes noise and standardizes formatting, leading to better summaries:
```bash
readme-summarizer summarize messy-readme.md --norm-level aggressive -v
```

### 2. Cleaning READMEs for Publishing
Prepare a clean README for distribution:
```bash
readme-summarizer normalize draft-readme.md -o README.md --level standard
```

### 3. Batch Processing Multiple READMEs
Normalize all READMEs in a project:
```bash
readme-summarizer batch readmes.txt --normalize --norm-level standard
```

### 4. Converting Emoji-Heavy READMEs
Convert decorative emojis to text for better accessibility:
```bash
readme-summarizer normalize README.md --emoji convert -o clean-readme.md
```

### 5. Preprocessing for Other Tools
Clean README content for use with other markdown processors:
```bash
readme-summarizer normalize owner/repo --level aggressive -o preprocessed.md
```

## 🧪 Testing

Run the test suite to verify normalizer functionality:

```bash
# Run all tests
python -m pytest tests/test_content_normalizer.py

# Run specific test
python -m pytest tests/test_content_normalizer.py::TestContentNormalizer::test_emoji_removal

# Run with verbose output
python -m pytest tests/test_content_normalizer.py -v
```

## 🔍 Technical Details

### Processing Pipeline

1. **Code Block Extraction**: Protected from normalization
2. **Unicode Normalization**: NFC normalization + encoding fixes
3. **Comment Removal**: HTML and markdown comments
4. **HTML Removal**: Tags stripped, content preserved
5. **Emoji Processing**: Based on configuration
6. **Header Normalization**: Standardize markdown headers
7. **Link Standardization**: Fix formatting issues
8. **Whitespace Normalization**: Clean up spaces and tabs
9. **Newline Reduction**: Remove excessive line breaks
10. **Code Block Restoration**: Return protected content
11. **Final Cleanup**: Trim and ensure proper ending

### Performance

- Fast regex-based processing
- Efficient string operations
- Minimal memory overhead
- Suitable for large README files (tested up to 1MB)

### Error Handling

- Gracefully handles malformed markdown
- Preserves content even if normalization fails partially
- Detailed error messages for debugging
- Safe fallbacks for edge cases

## 📚 Examples

### Example 1: Basic Cleanup

**Input**:
```markdown
#My Project

<center>Welcome!</center>

This   has     extra    spaces.


Too many newlines above.
```

**Command**:
```bash
readme-summarizer normalize input.md
```

**Output**:
```markdown
# My Project

Welcome!

This has extra spaces.

Too many newlines above.
```

### Example 2: Aggressive Normalization

**Input**:
```markdown
# 🚀 Cool Project 🎨

<!-- TODO: Update this -->

<div align="center">
  <img src="logo.png">
</div>

###Installation

Smart "quotes" and—dashes.
```

**Command**:
```bash
readme-summarizer normalize input.md --level aggressive --emoji remove
```

**Output**:
```markdown
# Cool Project

### Installation

Smart "quotes" and--dashes.
```

### Example 3: Emoji Conversion

**Input**:
```markdown
# ✨ Features

- 🚀 Fast
- 🎨 Beautiful
- 🔧 Configurable
```

**Command**:
```bash
readme-summarizer normalize input.md --emoji convert
```

**Output**:
```markdown
# [sparkles] Features

- [rocket] Fast
- [art] Beautiful
- [wrench] Configurable
```

## 🤝 Integration with Other Features

### File Detector
Works seamlessly with the file detector:
```bash
readme-summarizer select ./project --auto --normalize --norm-level standard
```

### Batch Processing
Apply normalization to multiple files:
```bash
readme-summarizer batch files.txt --normalize --norm-level aggressive
```

### Input Resolver
Normalize content from any source:
```bash
# From GitHub
readme-summarizer normalize owner/repo --emoji remove

# From URL
readme-summarizer normalize https://example.com/readme.md

# From local file
readme-summarizer normalize ./README.md
```

## ⚙️ Advanced Tips

1. **For web-scraped content**: Use aggressive level
   ```bash
   readme-summarizer normalize scraped.md --level aggressive --emoji remove
   ```

2. **For accessibility**: Convert emojis to text
   ```bash
   readme-summarizer normalize README.md --emoji convert
   ```

3. **For minimal changes**: Use minimal level
   ```bash
   readme-summarizer normalize README.md --level minimal
   ```

4. **View before saving**: Check output first
   ```bash
   readme-summarizer normalize README.md | less
   ```

5. **Compare before/after**: Use diff
   ```bash
   readme-summarizer normalize README.md -o clean.md
   diff README.md clean.md
   ```

## 🐛 Troubleshooting

### Content looks unchanged
- Check if normalization is enabled: `--normalize`
- Try a higher level: `--norm-level aggressive`
- Enable verbose mode to see stats: `-v`

### Too much content removed
- Use a lower level: `--norm-level minimal`
- Disable HTML removal: `--no-normalize` and handle separately
- Check if code blocks are being affected

### Emojis not handled correctly
- Verify emoji handling option: `--emoji keep|remove|convert`
- Some emojis may not be in the conversion map
- Check unicode normalization settings

## 📝 Summary

The Content Normalizer / Preprocessor is a powerful feature that:

✅ Improves summarization accuracy  
✅ Handles encoding and unicode issues  
✅ Removes HTML and formatting clutter  
✅ Standardizes markdown syntax  
✅ Provides detailed statistics  
✅ Works with all input sources  
✅ Offers flexible configuration  
✅ Integrates seamlessly with existing features  

Use it to ensure consistent, clean README content for better processing and analysis!

---

**See Also**:
- [CLI Guide](CLI_GUIDE.md) - Complete CLI reference
- [Features](FEATURES.md) - All available features
- [Quick Reference](QUICK_REF.md) - Command cheat sheet
