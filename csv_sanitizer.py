#!/usr/bin/env python3
"""
CSV HTML Tag Sanitizer

A robust utility for removing HTML tags from CSV files while preserving data structure.
Uses BeautifulSoup for superior HTML parsing compared to regex-based approaches.

Usage:
    python csv_sanitizer.py input.csv [output.csv] [--encoding ENCODING] [--mode MODE]

Arguments:
    input.csv       - Path to the input CSV file containing HTML tags
    output.csv      - Path to the output sanitized CSV file (optional, defaults to sanitized_input.csv)
    --encoding      - Specify the encoding of the input file (default: utf-8)
    --mode          - Sanitization mode: 'basic' (entities only), 'structural' (common structural tags),
                      or 'full' (all HTML tags) (default: full)
    --tags          - Comma-separated list of specific tags to remove (e.g., "p,div,span")
"""

import argparse
import csv
import re
import sys
from html import unescape
from pathlib import Path
from typing import List, Optional, Union

try:
    from bs4 import BeautifulSoup

    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False
    print("Warning: BeautifulSoup not found. Falling back to regex-based parsing.", file=sys.stderr)
    print("For better HTML parsing, install BeautifulSoup: pip install beautifulsoup4", file=sys.stderr)


class HTMLSanitizer:
    """Handles HTML tag removal from text content using BeautifulSoup or regex fallback."""

    STRUCTURAL_TAGS = [
        'p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'dl', 'dt', 'dd',
        'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'caption',
        'section', 'article', 'aside', 'header', 'footer', 'nav', 'main',
        'strong', 'b', 'em', 'i', 'u', 'strike', 's', 'del', 'ins',
        'small', 'big', 'sub', 'sup', 'mark', 'pre', 'code', 'blockquote',
        'q', 'cite', 'abbr', 'address', 'time',
        'a', 'br', 'hr', 'img'
    ]

    def __init__(self, mode: str = 'full', specific_tags: Optional[List[str]] = None):
        """Initialize the HTML sanitizer with the specified mode."""
        self.mode = mode.lower()
        self.specific_tags = specific_tags or []
        self.use_bs4 = BEAUTIFULSOUP_AVAILABLE

    def sanitize_html(self, html_text: str) -> str:
        """Remove HTML tags and decode HTML entities from a string."""
        if not html_text or not isinstance(html_text, str):
            return ""

        decoded_text = unescape(html_text)

        if self.use_bs4:
            return self._sanitize_with_bs4(decoded_text)
        else:
            return self._sanitize_with_regex(decoded_text)

    def _sanitize_with_bs4(self, html_text: str) -> str:
        """Use BeautifulSoup to parse and clean HTML text."""
        wrapped_html = f"<div>{html_text}</div>"

        try:
            soup = BeautifulSoup(wrapped_html, 'html.parser')

            if self.mode == 'basic':
                return html_text

            elif self.mode == 'structural':
                for tag in self.STRUCTURAL_TAGS:
                    for element in soup.find_all(tag):
                        element.replace_with(element.get_text())

            elif self.specific_tags:
                for tag in self.specific_tags:
                    for element in soup.find_all(tag):
                        element.replace_with(element.get_text())

            if self.mode == 'full' or self.mode == 'structural' or self.specific_tags:
                text = soup.get_text(separator=' ', strip=True)
                text = re.sub(r'\s+', ' ', text).strip()
                return text

        except Exception as e:
            print(f"BeautifulSoup parsing error: {e}. Falling back to regex.", file=sys.stderr)
            return self._sanitize_with_regex(html_text)

    def _sanitize_with_regex(self, html_text: str) -> str:
        """Fallback method using regex to clean HTML when BeautifulSoup is unavailable."""
        if self.mode == 'basic':
            return html_text

        elif self.mode == 'structural':
            return self._remove_specific_tags(html_text, self.STRUCTURAL_TAGS)

        elif self.specific_tags:
            return self._remove_specific_tags(html_text, self.specific_tags)

        else:
            cleaned_text = re.sub(r'<[^>]*>', '', html_text)
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            return cleaned_text

    @staticmethod
    def _remove_specific_tags(text: str, tags: List[str]) -> str:
        """Remove specific HTML tags from a string using regex."""
        pattern = '|'.join([f'</?{tag}(?:\\s[^>]*)?>' for tag in tags])
        if pattern:
            cleaned_text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            return cleaned_text
        return text


class CSVProcessor:
    """Processes CSV files to sanitize HTML content."""

    def __init__(self, input_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None,
                 encoding: str = 'utf-8', sanitize_mode: str = 'full', specific_tags: Optional[List[str]] = None):
        """Initialize the CSV processor."""
        self.input_path = Path(input_path)

        if output_path is None:
            self.output_path = self.input_path.parent / f"sanitized_{self.input_path.name}"
        else:
            self.output_path = Path(output_path)

        self.encoding = encoding
        self.sanitizer = HTMLSanitizer(mode=sanitize_mode, specific_tags=specific_tags)

    def process(self) -> int:
        """Process the CSV file, sanitizing all fields."""
        try:
            with open(self.input_path, 'r', encoding=self.encoding, newline='') as infile:
                sample = infile.read(4096)

                try:
                    dialect = csv.Sniffer().sniff(sample)
                    has_header = csv.Sniffer().has_header(sample)

                    if not hasattr(dialect, 'escapechar') or dialect.escapechar is None:
                        dialect.escapechar = '\\'
                except:
                    dialect = csv.excel
                    dialect.escapechar = '\\'
                    has_header = True

                infile.seek(0)  # Reset file position
                reader = csv.reader(
                    infile,
                    delimiter=dialect.delimiter,
                    quotechar=dialect.quotechar,
                    escapechar=dialect.escapechar,
                    quoting=dialect.quoting,
                    doublequote=True  # Always use double-quoting for safety
                )

                with open(self.output_path, 'w', encoding=self.encoding, newline='') as outfile:
                    writer = csv.writer(
                        outfile,
                        delimiter=dialect.delimiter,
                        quotechar=dialect.quotechar,
                        escapechar=dialect.escapechar,
                        quoting=dialect.quoting,
                        doublequote=True  # Always use double-quoting for safety
                    )

                    row_count = 0
                    for row in reader:
                        # Process each cell in the row
                        sanitized_row = [self.sanitizer.sanitize_html(cell) for cell in row]
                        writer.writerow(sanitized_row)
                        row_count += 1

            return row_count - (1 if has_header else 0)  # Return count of data rows only

        except Exception as e:
            print(f"Error processing CSV: {e}", file=sys.stderr)
            raise


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Sanitize HTML tags from CSV files.')
    parser.add_argument('input_file', help='Path to the input CSV file containing HTML tags')
    parser.add_argument('output_file', nargs='?', default=None,
                        help='Path to the output sanitized CSV file (default: sanitized_input.csv)')
    parser.add_argument('--encoding', default='utf-8',
                        help='Encoding of the input file (default: utf-8)')
    parser.add_argument('--mode', choices=['basic', 'structural', 'full'], default='full',
                        help='Sanitization mode: basic (entities only), structural (common tags), full (all tags)')
    parser.add_argument('--tags', default='',
                        help='Comma-separated list of specific HTML tags to remove (e.g., "p,div,span")')

    args = parser.parse_args()

    specific_tags = [tag.strip() for tag in args.tags.split(',')] if args.tags else None

    try:
        if not BEAUTIFULSOUP_AVAILABLE:
            print("\nNote: For better HTML parsing, install BeautifulSoup4:\n"
                  "pip install beautifulsoup4\n", file=sys.stderr)

        processor = CSVProcessor(
            args.input_file,
            args.output_file,
            args.encoding,
            sanitize_mode=args.mode,
            specific_tags=specific_tags
        )
        rows_processed = processor.process()

        print(f"Successfully sanitized HTML from {rows_processed} data rows.")
        print(f"Sanitization mode: {args.mode}")
        print(f"HTML parser: {'BeautifulSoup' if BEAUTIFULSOUP_AVAILABLE else 'Regex fallback'}")
        if specific_tags:
            print(f"Removed specific tags: {', '.join(specific_tags)}")
        print(f"Output saved to: {processor.output_path}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
