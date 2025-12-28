"""
Metadata manager for preserving URL, title, and section information during content extraction
in the website content ingestion system.
"""

from typing import Dict, Any, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re


class MetadataManager:
    """
    Metadata manager for preserving URL, title, and section information during content extraction.
    """

    def __init__(self):
        """Initialize the metadata manager."""
        self.metadata_preservation_rules = {
            'url': True,
            'title': True,
            'section': True,
            'breadcrumbs': True,
            'author': True,
            'description': True,
            'tags': True,
            'last_updated': True,
            'edit_url': True
        }

    def extract_metadata_from_page(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """
        Extract metadata from a page including URL, title, section, and other relevant information.

        Args:
            soup: BeautifulSoup object containing the page content
            url: The URL of the page being processed

        Returns:
            Dictionary containing extracted metadata
        """
        metadata = {}

        # Extract URL information
        metadata['url'] = url
        metadata['parsed_url'] = self._parse_url_components(url)

        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()
        else:
            # Try to find title in meta tags or h1
            h1_tag = soup.find('h1')
            if h1_tag:
                metadata['title'] = h1_tag.get_text().strip()
            else:
                metadata['title'] = 'Untitled Page'

        # Extract section/category from URL structure
        metadata['section'] = self._extract_section_from_url(url)

        # Extract breadcrumbs if present
        metadata['breadcrumbs'] = self._extract_breadcrumbs(soup)

        # Extract metadata from meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name') or meta.get('property') or meta.get('charset')
            content = meta.get('content', '')

            if name and content:
                # Normalize the name
                normalized_name = name.replace(':', '_').replace('-', '_').lower()

                # Extract common metadata types
                if name in ['description', 'og:description', 'twitter:description']:
                    metadata['description'] = content
                elif name in ['keywords', 'news_keywords']:
                    metadata['tags'] = [tag.strip() for tag in content.split(',')]
                elif name in ['author', 'article:author', 'twitter:creator']:
                    metadata['author'] = content
                elif name in ['og:title', 'twitter:title']:
                    metadata['og_title'] = content
                elif name in ['og:type']:
                    metadata['og_type'] = content
                elif name in ['og:image', 'twitter:image']:
                    metadata['og_image'] = content
                elif name in ['article:published_time', 'article:modified_time']:
                    metadata[name.replace(':', '_')] = content
                else:
                    # Store other meta tags with normalized names
                    metadata[normalized_name] = content

        # Extract canonical URL
        canonical_link = soup.find('link', rel='canonical')
        if canonical_link:
            metadata['canonical_url'] = canonical_link.get('href', '')

        # Extract alternate language links
        alternate_links = soup.find_all('link', rel='alternate')
        alternates = []
        for link in alternate_links:
            if link.get('hreflang') and link.get('href'):
                alternates.append({
                    'href': link.get('href'),
                    'hreflang': link.get('hreflang'),
                    'title': link.get('title', '')
                })
        if alternates:
            metadata['alternates'] = alternates

        # Extract last updated information
        metadata['last_updated'] = self._extract_last_updated(soup)

        # Extract edit URL if present (common in Docusaurus sites)
        edit_link = soup.find('a', class_='theme-edit-this-page')
        if edit_link:
            metadata['edit_url'] = edit_link.get('href', '')

        # Extract any structured data
        structured_data_scripts = soup.find_all('script', type='application/ld+json')
        structured_data = []
        for script in structured_data_scripts:
            if script.string:
                structured_data.append(script.string.strip())
        if structured_data:
            metadata['structured_data'] = structured_data

        return metadata

    def _parse_url_components(self, url: str) -> Dict[str, str]:
        """
        Parse URL components for metadata extraction.

        Args:
            url: The URL to parse

        Returns:
            Dictionary containing URL components
        """
        parsed = urlparse(url)
        return {
            'scheme': parsed.scheme,
            'netloc': parsed.netloc,
            'path': parsed.path,
            'params': parsed.params,
            'query': parsed.query,
            'fragment': parsed.fragment
        }

    def _extract_section_from_url(self, url: str) -> str:
        """
        Extract section information from URL structure.

        Args:
            url: The URL to extract section from

        Returns:
            Section name extracted from URL
        """
        parsed = urlparse(url)
        path_parts = [part for part in parsed.path.split('/') if part]

        # Common patterns for Docusaurus sections
        if path_parts:
            # Look for common section indicators
            for i, part in enumerate(path_parts):
                if part in ['docs', 'category', 'tag', 'api', 'guide', 'tutorial', 'reference']:
                    if i + 1 < len(path_parts):
                        return f"{part}/{path_parts[i+1]}"

            # If no specific section found, return first meaningful part
            return path_parts[0]
        else:
            return 'home'

    def _extract_breadcrumbs(self, soup: BeautifulSoup) -> list:
        """
        Extract breadcrumbs from the page.

        Args:
            soup: BeautifulSoup object containing the page content

        Returns:
            List of breadcrumb items
        """
        breadcrumbs = []

        # Look for common breadcrumb patterns
        breadcrumb_selectors = [
            '.breadcrumbs__item',
            '.breadcrumb-item',
            '.nav-breadcrumb',
            '[aria-label="Breadcrumb"] li',
            '.breadcrumb li'
        ]

        for selector in breadcrumb_selectors:
            breadcrumb_elements = soup.select(selector)
            if breadcrumb_elements:
                for element in breadcrumb_elements:
                    link = element.find('a')
                    if link:
                        breadcrumbs.append({
                            'text': link.get_text().strip(),
                            'url': link.get('href', '')
                        })
                    else:
                        text = element.get_text().strip()
                        if text:
                            breadcrumbs.append({
                                'text': text,
                                'url': ''
                            })
                break  # Use first match found

        return breadcrumbs

    def _extract_last_updated(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract last updated information from the page.

        Args:
            soup: BeautifulSoup object containing the page content

        Returns:
            Last updated timestamp or None
        """
        # Look for common last updated patterns
        last_updated_selectors = [
            '.theme-last-updated',
            '.last-updated',
            '.updated',
            '.post-meta',
            '.doc-footer',
            '.theme-edit-this-page'
        ]

        for selector in last_updated_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().strip()
                # Look for date patterns in the text
                date_match = re.search(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', text, re.IGNORECASE)
                if date_match:
                    return date_match.group()

        # Check for git commit info or time elements
        time_elements = soup.find_all('time')
        for time_elem in time_elements:
            datetime_attr = time_elem.get('datetime')
            if datetime_attr:
                return datetime_attr

        return None

    def preserve_extraction_metadata(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preserve metadata alongside extracted content.

        Args:
            content: The extracted content string
            metadata: Dictionary containing metadata

        Returns:
            Dictionary with content and preserved metadata
        """
        result = {
            'content': content,
            'metadata': metadata,
            'word_count': len(content.split()) if content else 0,
            'char_count': len(content) if content else 0,
            'extraction_timestamp': self._get_current_timestamp()
        }

        # Add computed metadata
        if metadata.get('url'):
            result['domain'] = urlparse(metadata['url']).netloc
            result['path'] = urlparse(metadata['url']).path

        if metadata.get('title'):
            result['title_length'] = len(metadata['title'])

        if content:
            result['content_length'] = len(content)

        return result

    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp for metadata tracking.

        Returns:
            ISO formatted timestamp string
        """
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'

    def validate_metadata_completeness(self, metadata: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate the completeness of extracted metadata.

        Args:
            metadata: Dictionary containing extracted metadata

        Returns:
            Dictionary with validation results for each required metadata field
        """
        validation_results = {}

        # Check for required fields
        required_fields = ['url', 'title', 'section']
        for field in required_fields:
            validation_results[f'{field}_present'] = field in metadata and bool(metadata[field])

        # Check for optional but useful fields
        optional_fields = ['description', 'author', 'breadcrumbs', 'tags']
        for field in optional_fields:
            validation_results[f'{field}_present'] = field in metadata and bool(metadata.get(field))

        # Overall validation
        validation_results['metadata_complete'] = all([
            validation_results.get(f'{field}_present', False) for field in required_fields
        ])

        return validation_results

    def merge_metadata(self, existing_metadata: Dict[str, Any], new_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge new metadata with existing metadata, preferring new values for conflicts.

        Args:
            existing_metadata: Dictionary containing existing metadata
            new_metadata: Dictionary containing new metadata to merge

        Returns:
            Merged metadata dictionary
        """
        merged = existing_metadata.copy()

        for key, value in new_metadata.items():
            if key == 'tags' and key in merged and isinstance(value, list) and isinstance(merged[key], list):
                # For tags, combine the lists
                merged[key] = list(set(merged[key] + value))
            elif key == 'breadcrumbs' and key in merged and isinstance(value, list) and isinstance(merged[key], list):
                # For breadcrumbs, prefer the new ones
                merged[key] = value
            else:
                # For other fields, use the new value
                merged[key] = value

        return merged


def create_metadata_enricher():
    """
    Factory function to create a metadata enricher instance.

    Returns:
        Instance of MetadataManager
    """
    return MetadataManager()


def extract_page_metadata(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """
    Convenience function to extract metadata from a page.

    Args:
        soup: BeautifulSoup object containing the page content
        url: The URL of the page being processed

    Returns:
        Dictionary containing extracted metadata
    """
    manager = MetadataManager()
    return manager.extract_metadata_from_page(soup, url)


def preserve_content_metadata(content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to preserve metadata with extracted content.

    Args:
        content: The extracted content string
        metadata: Dictionary containing metadata

    Returns:
        Dictionary with content and preserved metadata
    """
    manager = MetadataManager()
    return manager.preserve_extraction_metadata(content, metadata)


def validate_metadata(metadata: Dict[str, Any]) -> Dict[str, bool]:
    """
    Convenience function to validate metadata completeness.

    Args:
        metadata: Dictionary containing extracted metadata

    Returns:
        Dictionary with validation results
    """
    manager = MetadataManager()
    return manager.validate_metadata_completeness(metadata)