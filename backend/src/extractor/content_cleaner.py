"""
Content cleaner for structured text extraction in the website content ingestion system.
Provides functions to clean and structure extracted text content.
"""

import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup


class ContentCleaner:
    """
    Content cleaner utility for structured text extraction.
    """

    def __init__(self):
        """Initialize the content cleaner with cleaning rules."""
        self.noise_patterns = [
            r'Previous\s+[^\n]*\nNext\s+[^\n]*',  # Previous/Next navigation
            r'&larr;\s*[^\n]*\n&rarr;\s*[^\n]*',  # Arrow navigation
            r'«\s*[^\n]*\n»\s*[^\n]*',  # Chevron navigation
            r'\s*Edit on GitHub\s*',  # Edit links
            r'\s*Last updated\s*.*\d{4}',  # Last updated timestamps
        ]

        self.content_selectors = [
            '[class*="docItemContainer"]',
            '[class*="docItem"]',
            '[class*="markdown"]',
            '[class*="theme"]',
            '[role="main"]',
            'main',
            '.container',
            '.main-wrapper',
            '.theme-doc-markdown',
            '.markdown',
            '.docs-content',
            '.post-content',
            '.article'
        ]

    def clean_content(self, html_content: str) -> str:
        """
        Clean HTML content by removing noise and extracting clean text.

        Args:
            html_content: Raw HTML content to clean

        Returns:
            Clean text content
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove common noise elements
        self._remove_noise_elements(soup)

        # Find main content area
        main_content = self._find_main_content(soup)

        # Extract text and clean it
        text_content = main_content.get_text(separator=' ', strip=True)
        cleaned_text = self._apply_text_cleaning(text_content)

        return cleaned_text

    def _remove_noise_elements(self, soup: BeautifulSoup) -> None:
        """
        Remove noise elements from the soup.

        Args:
            soup: BeautifulSoup object to clean
        """
        noise_selectors = [
            '.theme-edit-this-page',
            '.theme-last-updated',
            '.pagination-nav',
            '.navbar',
            '.footer',
            '.sidebar',
            '.menu',
            '.table-of-contents',
            '.toc',
            '.breadcrumb',
            '.carbon-ads',
            '.ads',
            'script',
            'style',
            'nav',
            'header',
            'footer',
            'aside',
            '.announcement-bar',
            '.cookie-banner',
            '.consent-banner',
            '.edit-meta',
            '.edit-link',
            '.theme-admonition',
            '.theme-back-to-top-button',
            '.theme-doc-footer',
            '.theme-last-updated',
        ]

        for selector in noise_selectors:
            for element in soup.select(selector):
                element.decompose()

    def _find_main_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Find the main content area in the page.

        Args:
            soup: BeautifulSoup object containing the page content

        Returns:
            BeautifulSoup element containing the main content
        """
        # Try common Docusaurus content containers
        for selector in self.content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                # Remove noise from main content
                self._remove_noise_elements(content_element)
                return content_element

        # If no specific container found, try to get content from body
        body = soup.find('body')
        if body:
            # Remove common navigation elements from body
            self._remove_noise_elements(body)
            return body

        # Fallback to the entire soup
        return soup

    def _apply_text_cleaning(self, text: str) -> str:
        """
        Apply text cleaning operations.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\n+', '\n', text)  # Replace multiple newlines with single
        text = re.sub(r'[ \t]+', ' ', text)  # Replace multiple spaces/tabs with single space
        text = re.sub(r' +\n', '\n', text)  # Remove trailing spaces before newlines

        # Apply specific noise patterns
        for pattern in self.noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Clean up extra spaces after cleaning
        text = ' '.join(text.split())

        return text.strip()

    def extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract headings from the page for structure.

        Args:
            soup: BeautifulSoup object containing the page content

        Returns:
            List of heading dictionaries with level, text, and id
        """
        headings = []
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                heading_data = {
                    'level': i,
                    'text': heading.get_text().strip(),
                    'id': heading.get('id', ''),
                    'parent_id': None  # Will be populated if needed for hierarchical structure
                }

                # Find the closest parent heading if it exists
                prev_heading = heading.find_previous_sibling([f'h{j}' for j in range(i-1, 0, -1)])
                if prev_heading:
                    heading_data['parent_id'] = prev_heading.get('id', '')

                headings.append(heading_data)

        return headings

    def extract_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract tables from the page.

        Args:
            soup: BeautifulSoup object containing the page content

        Returns:
            List of table dictionaries with content and structure
        """
        tables = []
        for table in soup.find_all('table'):
            table_data = {
                'headers': [],
                'rows': []
            }

            # Extract headers
            header_row = table.find('thead')
            if header_row:
                headers = header_row.find_all(['th', 'td'])
                table_data['headers'] = [header.get_text().strip() for header in headers]

            # Extract rows
            tbody = table.find('tbody')
            if tbody:
                for row in tbody.find_all('tr'):
                    row_data = [cell.get_text().strip() for cell in row.find_all(['td', 'th'])]
                    table_data['rows'].append(row_data)
            else:
                # If no tbody, get all rows directly
                for row in table.find_all('tr'):
                    row_data = [cell.get_text().strip() for cell in row.find_all(['td', 'th'])]
                    table_data['rows'].append(row_data)

            tables.append(table_data)

        return tables

    def extract_code_blocks(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract code blocks from the page.

        Args:
            soup: BeautifulSoup object containing the page content

        Returns:
            List of code block dictionaries with content and language
        """
        code_blocks = []
        for code_block in soup.find_all(['pre', 'code']):
            # Get the code content
            code_element = code_block.find('code') if code_block.name != 'code' else code_block

            if code_element:
                code_content = code_element.get_text()
                language_classes = [cls for cls in code_element.get('class', []) if cls.startswith('language-')]
                language = language_classes[0].replace('language-', '') if language_classes else 'unknown'

                code_data = {
                    'content': code_content.strip(),
                    'language': language,
                    'filename': code_block.get('data-filename', '')  # For named code blocks
                }

                code_blocks.append(code_data)

        return code_blocks


def clean_html_noise(html_content: str) -> str:
    """
    Convenience function to clean HTML noise and extract clean text content.

    Args:
        html_content: Raw HTML content to clean

    Returns:
        Clean text content
    """
    cleaner = ContentCleaner()
    return cleaner.clean_content(html_content)


def extract_structured_content(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Extract structured content from a BeautifulSoup object.

    Args:
        soup: BeautifulSoup object containing the page content

    Returns:
        Dictionary with structured content and metadata
    """
    cleaner = ContentCleaner()

    content_data = {}

    # Extract title
    title_tag = soup.find('title')
    if title_tag:
        content_data['title'] = title_tag.get_text().strip()
    else:
        # Look for h1 as title
        h1_tag = soup.find('h1')
        if h1_tag:
            content_data['title'] = h1_tag.get_text().strip()
        else:
            content_data['title'] = 'Untitled Page'

    # Clean and extract main content
    content_data['content'] = cleaner.clean_content(str(soup))
    content_data['word_count'] = len(content_data['content'].split()) if content_data['content'] else 0

    # Extract structured elements
    content_data['headings'] = cleaner.extract_headings(soup)
    content_data['tables'] = cleaner.extract_tables(soup)
    content_data['code_blocks'] = cleaner.extract_code_blocks(soup)

    return content_data


def extract_metadata(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extract metadata from the page.

    Args:
        soup: BeautifulSoup object containing the page content

    Returns:
        Dictionary with extracted metadata
    """
    metadata = {}

    # Extract meta tags
    for meta in soup.find_all('meta'):
        name = meta.get('name') or meta.get('property') or meta.get('charset')
        content = meta.get('content', '')

        if name and content:
            # Normalize the name
            normalized_name = name.replace(':', '_').replace('-', '_').lower()
            metadata[normalized_name] = content

    # Extract canonical URL
    canonical_link = soup.find('link', rel='canonical')
    if canonical_link:
        metadata['canonical_url'] = canonical_link.get('href', '')

    # Extract any structured data
    for script in soup.find_all('script', type='application/ld+json'):
        if script.string:
            metadata['structured_data'] = script.string.strip()

    return metadata


def chunk_content(content: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split content into chunks of specified size with overlap.

    Args:
        content: Content to chunk
        chunk_size: Size of each chunk (in characters)
        overlap: Overlap between chunks (in characters)

    Returns:
        List of content chunks
    """
    if len(content) <= chunk_size:
        return [content]

    chunks = []
    start = 0

    while start < len(content):
        end = start + chunk_size

        # If this is the last chunk, include the remainder
        if end >= len(content):
            chunks.append(content[start:])
            break

        # Find a good break point (try to break at sentence or word boundary)
        chunk = content[start:end]

        # Look for a good break point near the end
        break_points = ['.\n', '!\n', '?\n', ';\n', ',\n', '. ', '! ', '? ', '; ', ', ', '\n\n', '\n']
        best_break = -1

        for bp in break_points:
            last_break = chunk.rfind(bp)
            if last_break != -1 and last_break > len(chunk) * 0.7:  # At least 70% through the chunk
                best_break = start + last_break + len(bp)
                break

        if best_break != -1:
            end = best_break
        else:
            # If no good break point found, break at the original boundary
            end = start + chunk_size

        chunks.append(content[start:end])
        start = end - overlap if overlap > 0 else end

    return chunks