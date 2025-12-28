"""
Base crawler class with configurable options for the website content ingestion system.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
import logging

import requests
from bs4 import BeautifulSoup


class BaseCrawler(ABC):
    """
    Abstract base class for web crawlers with configurable options.
    """

    def __init__(
        self,
        base_url: str,
        delay: float = 1.0,
        max_retries: int = 3,
        timeout: int = 10,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the base crawler with configurable options.

        Args:
            base_url: The base URL to start crawling from
            delay: Delay between requests in seconds
            max_retries: Maximum number of retry attempts for failed requests
            timeout: Request timeout in seconds
            headers: Additional headers to include in requests
        """
        self.base_url = base_url
        self.delay = delay
        self.max_retries = max_retries
        self.timeout = timeout
        self.headers = headers or {}
        self.session = requests.Session()

        # Set default headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; Docusaurus Content Crawler/1.0; +http://example.com/bot)'
        })
        if headers:
            self.session.headers.update(headers)

        # Track visited URLs to avoid duplicates
        self.visited_urls: set = set()

        # Configure logging
        self.logger = logging.getLogger(__name__)

    def _is_valid_url(self, url: str) -> bool:
        """
        Check if a URL is valid and belongs to the same domain as the base URL.

        Args:
            url: The URL to validate

        Returns:
            True if the URL is valid and belongs to the same domain, False otherwise
        """
        try:
            parsed_base = urlparse(self.base_url)
            parsed_url = urlparse(url)

            # Check if the URL is valid and has the same domain
            return (
                parsed_url.scheme in ('http', 'https') and
                parsed_url.netloc == parsed_base.netloc
            )
        except Exception:
            return False

    def _make_request(self, url: str) -> Optional[requests.Response]:
        """
        Make an HTTP request with retry logic.

        Args:
            url: The URL to request

        Returns:
            The response object if successful, None otherwise
        """
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    allow_redirects=True
                )

                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Rate limited
                    # Exponential backoff for rate limiting
                    wait_time = (2 ** attempt) + 1
                    self.logger.warning(f"Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{self.max_retries}")
                    time.sleep(wait_time)
                    continue
                else:
                    self.logger.warning(f"HTTP {response.status_code} for {url} (attempt {attempt + 1}/{self.max_retries})")

            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed for {url}: {str(e)} (attempt {attempt + 1}/{self.max_retries})")

            if attempt < self.max_retries - 1:
                time.sleep(self.delay * (2 ** attempt))  # Exponential backoff

        return None

    def _delay_next_request(self):
        """
        Apply delay between requests to be respectful to the server.
        """
        time.sleep(self.delay)

    @abstractmethod
    def extract_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Abstract method to extract content from a BeautifulSoup object.

        Args:
            soup: The BeautifulSoup object containing the page content

        Returns:
            A dictionary containing the extracted content
        """
        pass

    @abstractmethod
    def discover_urls(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """
        Abstract method to discover URLs from a BeautifulSoup object.

        Args:
            soup: The BeautifulSoup object containing the page content
            current_url: The current URL being processed

        Returns:
            A list of discovered URLs
        """
        pass

    def crawl_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Crawl a single page and extract content.

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

            # Discover additional URLs
            discovered_urls = self.discover_urls(soup, url)

            # Add metadata
            content_data['url'] = url
            content_data['discovered_urls'] = discovered_urls

            self._delay_next_request()
            return content_data

        except Exception as e:
            self.logger.error(f"Error parsing content from {url}: {str(e)}")
            return None

    @abstractmethod
    async def crawl(self) -> List[Dict[str, Any]]:
        """
        Abstract method to start the crawling process.

        Returns:
            A list of dictionaries containing the crawled content
        """
        pass