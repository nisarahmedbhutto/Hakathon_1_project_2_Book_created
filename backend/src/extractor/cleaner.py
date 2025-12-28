"""
Content cleaning utilities for the website content ingestion system.
Provides functions to clean and structure extracted text content.
"""

import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup


def clean_html_noise(html_content: str) -> str:
    """
    Remove HTML noise and extract clean text content.

    Args:
        html_content: Raw HTML content to clean

    Returns:
        Clean text content
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove common noise elements
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
        '.edit-link'
    ]

    for selector in noise_selectors:
        for element in soup.select(selector):
            element.decompose()

    # Get text with proper spacing
    text = soup.get_text(separator=' ', strip=True)

    # Clean up the text
    text = re.sub(r'\n+', '\n', text)  # Replace multiple newlines with single
    text = re.sub(r'[ \t]+', ' ', text)  # Replace multiple spaces/tabs with single space
    text = re.sub(r' +\n', '\n', text)  # Remove trailing spaces before newlines
    text = text.strip()  # Remove leading/trailing whitespace

    return text


def extract_content_structure(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Extract structured content from a BeautifulSoup object.

    Args:
        soup: BeautifulSoup object containing the page content

    Returns:
        Dictionary with structured content and metadata
    """
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

    # Extract main content by finding the main content area
    main_selectors = [
        '[class*="docItemContainer"]',
        '[class*="docItem"]',
        '[class*="markdown"]',
        '[class*="theme"]',
        '[role="main"]',
        'main',
        '.container',
        '.main-wrapper',
        '.theme-doc-markdown',
        '.markdown'
    ]

    main_content = ""
    for selector in main_selectors:
        element = soup.select_one(selector)
        if element:
            # Remove noise from main content
            for noise_selector in ['.menu', '.pagination-nav', '.theme-edit-this-page', '.theme-last-updated']:
                for noise in element.select(noise_selector):
                    noise.decompose()

            main_content = element.get_text(separator=' ', strip=True)
            if main_content:
                break

    # If no main content found, try body
    if not main_content:
        body = soup.find('body')
        if body:
            for noise_selector in ['.menu', '.pagination-nav', '.theme-edit-this-page', '.theme-last-updated']:
                for noise in body.select(noise_selector):
                    noise.decompose()
            main_content = body.get_text(separator=' ', strip=True)

    content_data['content'] = main_content
    content_data['word_count'] = len(main_content.split()) if main_content else 0

    # Extract headings for structure
    headings = []
    for i in range(1, 7):
        for heading in soup.find_all(f'h{i}'):
            headings.append({
                'level': i,
                'text': heading.get_text().strip(),
                'id': heading.get('id', '')
            })

    content_data['headings'] = headings

    # Extract metadata
    content_data['metadata'] = extract_metadata(soup)

    return content_data


def extract_metadata(soup: BeautifulSoup) -> Dict[str, Any]:
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
        name = meta.get('name') or meta.get('property')
        content = meta.get('content', '')

        if name and content:
            # Normalize the name
            normalized_name = name.replace(':', '_').replace('-', '_')
            metadata[normalized_name] = content

    # Extract canonical URL
    canonical_link = soup.find('link', rel='canonical')
    if canonical_link:
        metadata['canonical_url'] = canonical_link.get('href', '')

    # Extract any structured data
    for script in soup.find_all('script', type='application/ld+json'):
        if script.string:
            metadata['structured_data'] = script.string

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
        break_points = ['.', '!', '?', ';', ',', ' ', '\n']
        found_break = False
        for bp in break_points:
            last_break = chunk.rfind(bp)
            if last_break != -1 and last_break > len(chunk) * 0.8:  # At least 80% through the chunk
                end = start + last_break + 1
                found_break = True
                break

        if not found_break:
            end = start + chunk_size

        chunks.append(content[start:end])
        start = end - overlap if overlap > 0 else end

    return chunks