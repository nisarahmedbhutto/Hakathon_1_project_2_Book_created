"""
Content extractor module for extracting clean, structured text from Docusaurus pages
in the website content ingestion system.
"""

from typing import Dict, Any
from bs4 import BeautifulSoup
import re


class ContentExtractor:
    """
    Content extractor that removes HTML noise and extracts clean, structured text from Docusaurus pages.
    """

    def __init__(self):
        """Initialize the content extractor with cleaning rules."""
        self.noise_selectors = [
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
            '.consent-banner'
        ]

    def extract_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract clean, structured content from a BeautifulSoup object.

        Args:
            soup: The BeautifulSoup object containing the page content

        Returns:
            A dictionary containing the extracted content with metadata
        """
        content_data = {}

        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            content_data['title'] = title_tag.get_text().strip()
        else:
            # Try alternative title selectors
            h1_tag = soup.find('h1')
            if h1_tag:
                content_data['title'] = h1_tag.get_text().strip()
            else:
                content_data['title'] = 'Untitled Page'

        # Extract main content by finding the main content area
        main_content = self._find_main_content(soup)

        # Clean the main content
        cleaned_content = self._clean_content(main_content)

        content_data['content'] = cleaned_content
        content_data['word_count'] = len(cleaned_content.split())

        # Extract metadata
        content_data['metadata'] = self._extract_metadata(soup)

        return content_data

    def _find_main_content(self, soup: BeautifulSoup) -> str:
        """
        Find the main content area in the page.

        Args:
            soup: The BeautifulSoup object containing the page content

        Returns:
            The main content as a string
        """
        # Common selectors for Docusaurus main content areas
        content_selectors = [
            '[class*="docItemContainer"]',
            '[class*="docItem"]',
            '[class*="markdown"]',
            '[class*="theme"]',
            '[role="main"]',
            'main',
            '.container',
            '.main-wrapper',
            '.article',
            '.post-content',
            '.docs-content',
            '.theme-doc-markdown',
            '.markdown',
            '.content',
        ]

        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                # Remove noise elements from the content
                self._remove_noise(content_element)
                return content_element.get_text(separator=' ', strip=True)

        # If no specific content container found, try to get content from body
        body = soup.find('body')
        if body:
            self._remove_noise(body)
            return body.get_text(separator=' ', strip=True)

        # Fallback to the entire soup
        self._remove_noise(soup)
        return soup.get_text(separator=' ', strip=True)

    def _remove_noise(self, element: BeautifulSoup) -> None:
        """
        Remove noise elements from the content.

        Args:
            element: The BeautifulSoup element to clean
        """
        for selector in self.noise_selectors:
            for noise_element in element.select(selector):
                noise_element.decompose()

    def _clean_content(self, content: str) -> str:
        """
        Clean the content by removing extra whitespace and formatting.

        Args:
            content: The raw content string

        Returns:
            The cleaned content string
        """
        # Remove extra whitespace and normalize line breaks
        content = re.sub(r'\n+', '\n', content)  # Replace multiple newlines with single
        content = re.sub(r'[ \t]+', ' ', content)  # Replace multiple spaces/tabs with single space
        content = re.sub(r' +\n', '\n', content)  # Remove trailing spaces before newlines
        content = content.strip()  # Remove leading/trailing whitespace

        return content

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract metadata from the page.

        Args:
            soup: The BeautifulSoup object containing the page content

        Returns:
            A dictionary containing extracted metadata
        """
        metadata = {}

        # Extract description
        description_meta = soup.find('meta', attrs={'name': 'description'})
        if description_meta:
            metadata['description'] = description_meta.get('content', '')

        # Extract keywords
        keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_meta:
            metadata['keywords'] = keywords_meta.get('content', '')

        # Extract author
        author_meta = soup.find('meta', attrs={'name': 'author'})
        if author_meta:
            metadata['author'] = author_meta.get('content', '')

        # Extract any Open Graph tags
        og_title = soup.find('meta', property='og:title')
        if og_title:
            metadata['og_title'] = og_title.get('content', '')

        og_description = soup.find('meta', property='og:description')
        if og_description:
            metadata['og_description'] = og_description.get('content', '')

        og_url = soup.find('meta', property='og:url')
        if og_url:
            metadata['og_url'] = og_url.get('content', '')

        # Extract canonical URL
        canonical_link = soup.find('link', rel='canonical')
        if canonical_link:
            metadata['canonical_url'] = canonical_link.get('href', '')

        return metadata


class ContentCleaner:
    """
    Content cleaner utility for structured text extraction.
    """

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean text by removing common noise patterns.

        Args:
            text: The raw text to clean

        Returns:
            The cleaned text
        """
        if not text:
            return ""

        # Remove common navigation elements that might have slipped through
        patterns_to_remove = [
            r'Previous\s+[^\n]*\nNext\s+[^\n]*',  # Previous/Next navigation
            r'&larr;\s*[^\n]*\n&rarr;\s*[^\n]*',  # Arrow navigation
            r'«\s*[^\n]*\n»\s*[^\n]*',  # Chevron navigation
        ]

        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    @staticmethod
    def extract_headings(text: str) -> list:
        """
        Extract headings from text (when available in original HTML structure).

        Args:
            text: The text to extract headings from

        Returns:
            A list of headings found in the text
        """
        # This would typically be done on the HTML before conversion to text
        # For now, we'll return an empty list as this is more of a structural analysis
        return []