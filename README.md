# CSV HTML Sanitizer: When Your Data Gets Too Markup-Happy 🧹

Working with exported data is often a case study in unexpected HTML contamination. After one too many encounters with
`<p>` tags lurking in seemingly innocent CSVs, I built this utility as a self-defense mechanism. It's a straightforward
Python tool that strips HTML from CSV files while religiously preserving your data structure.

## The HTML-in-CSV Problem: A Brief Therapy Session 🤔

If you've ever exported data from virtually any system, you've likely encountered what I call "HTML leakage" - those
moments when:

- Your CRM exports customer notes complete with formatting tags
- Your CMS gives you content tables with embedded HTML
- Your analytics platform decides `<strong>` tags belong in numerical data
- Your survey platform translates rich text responses into markup soup

The result? Data that's perfectly readable to a browser but completely frustrating for analysis, transformation, or
migration.

## Core Philosophy: Clean Without Breaking 🛠️

This tool approaches the problem with two guiding principles:

1. **Respect the structure** - Never alter column counts, row arrangements, or field relationships
2. **Remove the markup** - Use robust HTML parsing to extract just the meaningful content

In practice, this means a CSV with 17 columns and 5,000 rows before sanitization will have exactly 17 columns and 5,000
rows after, but without the HTML cruft.

## Implementation Approach: BeautifulSoup Over Regex 🍜

While regex is tempting for quick HTML removal, it's notoriously unreliable with complex markup. This tool:

- Uses **BeautifulSoup** as the primary HTML parser (when available)
- Falls back to regex patterns if BeautifulSoup isn't installed
- Carefully maintains CSV structure throughout processing
- Handles CSV dialects, encoding, and escaping properly

Having built too many brittle regex-based parsers in the past, I've learned that HTML requires a proper parser. The
BeautifulSoup approach handles nested tags, malformed HTML, and complex attribute structures far more reliably.

## Installation: Beautifully Simple 📦

```bash
# Clone it
git clone https://github.com/poacosta/csv-html-sanitizer.git
cd csv-html-sanitizer

# Optional but recommended
pip install beautifulsoup4

# Run it
python csv_sanitizer.py your_html_riddled_file.csv
```

## Usage: Adaptable to Your HTML Cleanup Needs 🔧

### Basic Cleanup

For most cases, just point it at your CSV:

```bash
python csv_sanitizer.py messy_export.csv
```

This creates `sanitized_messy_export.csv` with all HTML removed.

### Flexible Sanitization Options

Based on my encounters with different types of HTML contamination, I've added three sanitization modes:

```bash
# Remove only structural elements (p, div, strong, etc.)
python csv_sanitizer.py input.csv --mode structural

# Just decode HTML entities without removing tags
python csv_sanitizer.py input.csv --mode basic
```

### Targeted Tag Removal

When you know exactly which tags are causing trouble:

```bash
python csv_sanitizer.py input.csv --tags p,div,span,strong
```

### Handling Encoding Issues

Because UTF-8 is more of an aspiration than a reality in many systems:

```bash
python csv_sanitizer.py input.csv --encoding latin-1
```

## Technical Details: For the Curious 🔍

The sanitizer employs a two-stage approach to HTML handling:

1. **First pass**: Entity decoding (`&amp;` → `&`, etc.)
2. **Second pass**: HTML tag removal via BeautifulSoup or regex

CSV processing uses Python's built-in csv module with careful handling of:

- Dialect detection (delimiter, quote character)
- Proper escaping of special characters
- Structure preservation with explicit field mapping

The tool handles edge cases like:

- Inconsistent quoting in source files
- Missing escape characters in dialects
- HTML fragments vs. complete documents

## Real-world Reliability Notes ⚠️

Having battle-tested this on exports from various systems, I've found a few limitations worth noting:

- While it preserves CSV structure perfectly, whitespace formatting from HTML is normalized
- Very large files (100MB+) will work but consume proportional memory
- Some extremely malformed HTML might lose content in rare edge cases

## Requirements & Dependencies

**Core (no external dependencies):**

- Python 3.6+
- Standard library modules only

**Enhanced functionality:**

- BeautifulSoup4 (recommended but optional)

## License

MIT License - Take it, improve it, share what you learn.