"""
Docusaurus-specific crawler that handles Docusaurus structure for the website content ingestion system.
"""

import asyncio
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging

from .base import BaseCrawler


class DocusaurusCrawler(BaseCrawler):
    """
    Docusaurus-specific crawler that handles Docusaurus structure and content extraction.
    """

    def __init__(
        self,
        base_url: str,
        delay: float = 1.0,
        max_retries: int = 3,
        timeout: int = 10,
        headers: Optional[Dict[str, str]] = None,
        max_pages: Optional[int] = None
    ):
        """
        Initialize the Docusaurus crawler.

        Args:
            base_url: The base URL of the Docusaurus site to crawl
            delay: Delay between requests in seconds
            max_retries: Maximum number of retry attempts for failed requests
            timeout: Request timeout in seconds
            headers: Additional headers to include in requests
            max_pages: Maximum number of pages to crawl (None for unlimited)
        """
        super().__init__(base_url, delay, max_retries, timeout, headers)
        self.max_pages = max_pages
        self.crawled_count = 0

    def extract_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract content from a Docusaurus page.
        This method is called from crawl_page with the current URL context.

        Args:
            soup: The BeautifulSoup object containing the page content

        Returns:
            A dictionary containing the extracted content
        """
        # Note: current_url is not available in this method signature
        # It needs to be passed from crawl_page
        # We'll handle this by overriding the crawl_page method in the base class
        content_data = {}

        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            content_data['title'] = title_tag.get_text().strip()
        else:
            # Try to find title in meta tags or header
            h1_tag = soup.find('h1')
            if h1_tag:
                content_data['title'] = h1_tag.get_text().strip()
            else:
                content_data['title'] = 'Untitled'

        # Extract main content - look for Docusaurus-specific content containers
        content_selectors = [
            '[class*="docItemContainer"]',
            '[class*="docItem"]',
            '[class*="markdown"]',
            '.container',
            '.main-wrapper',
            '[role="main"]',
            'main',
            '.theme-doc-markdown',
            '.markdown'
        ]

        content_text = ""
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                # Remove navigation elements, headers, footers, and other noise
                for unwanted in content_element.find_all(['nav', 'header', 'footer', 'aside', '.menu', '.pagination-nav', '.theme-edit-this-page']):
                    unwanted.decompose()

                content_text = content_element.get_text(separator=' ', strip=True)
                if content_text:
                    break

        # If no content found with selectors, try to get from body
        if not content_text:
            body = soup.find('body')
            if body:
                # Remove common navigation elements from body
                for unwanted in body.find_all(['nav', 'header', 'footer', 'aside', 'script', 'style']):
                    unwanted.decompose()

                content_text = body.get_text(separator=' ', strip=True)

        content_data['content'] = content_text
        content_data['word_count'] = len(content_text.split())

        # Extract metadata (category will be added in crawl_page with URL context)
        meta_description = soup.find('meta', attrs={'name': 'description'})
        if meta_description:
            content_data['description'] = meta_description.get('content', '')

        # Extract any breadcrumbs or navigation context
        breadcrumbs = []
        breadcrumb_elements = soup.select('.breadcrumbs__item')
        for breadcrumb in breadcrumb_elements:
            link = breadcrumb.find('a')
            if link:
                breadcrumbs.append(link.get_text().strip())
            else:
                breadcrumbs.append(breadcrumb.get_text().strip())

        content_data['breadcrumbs'] = breadcrumbs

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

        return content_data

    def crawl_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Override the base class crawl_page method to add URL context for content extraction.

        Args:
            url: The URL to crawl

        Returns:
            A dictionary containing the page content and metadata, or None if failed
        """
        if url in self.visited_urls:
            return None

        self.visited_urls.add(url)
        self.logger.info(f"Crawling: {url}")

        response = self._make_request(url)
        if not response:
            return None

        try:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract content using the implementation-specific method
            content_data = self.extract_content(soup)

            # Add URL-specific metadata
            parsed_url = urlparse(url)
            path_parts = [part for part in parsed_url.path.split('/') if part]
            content_data['category'] = path_parts[0] if path_parts else 'general'
            content_data['url'] = url

            # Discover additional URLs
            discovered_urls = self.discover_urls(soup, url)

            # Add discovered URLs to content data
            content_data['discovered_urls'] = discovered_urls

            self._delay_next_request()
            return content_data

        except Exception as e:
            self.logger.error(f"Error parsing content from {url}: {str(e)}")
            return None

    def discover_urls(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """
        Discover URLs from a Docusaurus page.

        Args:
            soup: The BeautifulSoup object containing the page content
            current_url: The current URL being processed

        Returns:
            A list of discovered URLs
        """
        urls = set()

        # Find all links in the page
        for link in soup.find_all('a', href=True):
            href = link['href']

            # Convert relative URLs to absolute
            absolute_url = urljoin(current_url, href)

            # Only add URLs that are valid and belong to the same domain
            if self._is_valid_url(absolute_url):
                # Exclude certain URL patterns that are not content pages
                excluded_patterns = [
                    '#',  # Fragment links
                    'mailto:',  # Email links
                    '.pdf',  # PDF files
                    '.zip',  # Archive files
                    '.jpg',  # Image files
                    '.jpeg',  # Image files
                    '.png',  # Image files
                    '.gif',  # Image files
                    '.svg',  # Image files
                    '.doc',  # Document files
                    '.docx',  # Document files
                    '.xls',  # Spreadsheet files
                    '.xlsx',  # Spreadsheet files
                    '.ppt',  # Presentation files
                    '.pptx',  # Presentation files
                    '.mp4',  # Video files
                    '.avi',  # Video files
                    '.mov',  # Video files
                    '.mp3',  # Audio files
                    '.wav',  # Audio files
                ]

                if not any(pattern in absolute_url.lower() for pattern in excluded_patterns):
                    urls.add(absolute_url)

        # Look for pagination or next/previous links
        pagination_selectors = [
            'a[rel="next"]',
            'a[rel="prev"]',
            'a.pagination-rel-link',
            '.pagination-nav__link'
        ]

        for selector in pagination_selectors:
            for link in soup.select(selector):
                if link and link.get('href'):
                    absolute_url = urljoin(current_url, link['href'])
                    if self._is_valid_url(absolute_url):
                        urls.add(absolute_url)

        # Look for sidebar navigation links
        sidebar_links = soup.select('.menu__link')
        for link in sidebar_links:
            if link.get('href'):
                absolute_url = urljoin(current_url, link['href'])
                if self._is_valid_url(absolute_url):
                    urls.add(absolute_url)

        # Look for doc links (common in Docusaurus)
        doc_links = soup.select('[class*="doc"] a[href]')
        for link in doc_links:
            if link.get('href'):
                absolute_url = urljoin(current_url, link['href'])
                if self._is_valid_url(absolute_url):
                    urls.add(absolute_url)

        return list(urls)

    async def crawl(self) -> List[Dict[str, Any]]:
        """
        Start the crawling process for the Docusaurus site.

        Returns:
            A list of dictionaries containing the crawled content
        """
        self.logger.info(f"Starting to crawl Docusaurus site: {self.base_url}")

        # Queue for URLs to crawl, starting with the base URL
        urls_to_crawl = [self.base_url]
        crawled_results = []

        while urls_to_crawl and (self.max_pages is None or self.crawled_count < self.max_pages):
            current_url = urls_to_crawl.pop(0)

            # Skip if already visited
            if current_url in self.visited_urls:
                continue

            # Crawl the page
            result = self.crawl_page(current_url)
            if result:
                crawled_results.append(result)
                self.crawled_count += 1

                # Add discovered URLs to the queue if within limits
                if self.max_pages is None or self.crawled_count < self.max_pages:
                    for discovered_url in result.get('discovered_urls', []):
                        if discovered_url not in self.visited_urls and discovered_url not in urls_to_crawl:
                            urls_to_crawl.append(discovered_url)

            # Log progress periodically
            if self.crawled_count % 10 == 0:
                self.logger.info(f"Progress: {self.crawled_count} pages crawled")

        self.logger.info(f"Crawling completed. Total pages crawled: {len(crawled_results)}")
        return crawled_results