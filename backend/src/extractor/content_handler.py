"""
Content handler for different content types and formats in the website content ingestion system.
Handles various content formats within the Docusaurus book.
"""

from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import re


class ContentHandler:
    """
    Content handler for different content types and formats within the Docusaurus book.
    """

    def __init__(self):
        """Initialize the content handler."""
        self.supported_formats = [
            'text',
            'code',
            'table',
            'image',
            'list',
            'blockquote',
            'heading'
        ]

        # Regex patterns for different content types
        self.patterns = {
            'code_block': r'```[\s\S]*?```',
            'inline_code': r'`(.*?)`',
            'bold': r'\*\*(.*?)\*\*',
            'italic': r'\*(.*?)\*',
            'link': r'\[(.*?)\]\((.*?)\)',
            'image': r'!\[(.*?)\]\((.*?)\)',
        }

    def handle_content_types(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Handle different content types and formats within the page.

        Args:
            soup: BeautifulSoup object containing the page content

        Returns:
            Dictionary with processed content by type
        """
        content_by_type = {
            'text': self._extract_text_content(soup),
            'headings': self._extract_headings(soup),
            'lists': self._extract_lists(soup),
            'tables': self._extract_tables(soup),
            'code_blocks': self._extract_code_blocks(soup),
            'images': self._extract_images(soup),
            'links': self._extract_links(soup),
            'quotes': self._extract_quotes(soup),
        }

        return content_by_type

    def _extract_text_content(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract plain text content from the page.

        Args:
            soup: BeautifulSoup object containing the page content

        Returns:
            List of text paragraphs
        """
        # Get all paragraphs
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if text:
                paragraphs.append(text)

        # Also get text from divs that might contain content
        for div in soup.find_all('div', class_=lambda x: x and 'markdown' in x.lower()):
            text = div.get_text().strip()
            if text and text not in paragraphs:
                paragraphs.append(text)

        return paragraphs

    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract headings from the page.

        Args:
            soup: BeautifulSoup object containing the page content

        Returns:
            List of heading dictionaries with level, text, and ID
        """
        headings = []
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                heading_data = {
                    'level': i,
                    'text': heading.get_text().strip(),
                    'id': heading.get('id', ''),
                    'classes': heading.get('class', []),
                }
                headings.append(heading_data)

        return headings

    def _extract_lists(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract lists (ordered and unordered) from the page.

        Args:
            soup: BeautifulSoup object containing the page content

        Returns:
            List of list dictionaries with type and items
        """
        lists = []

        # Find ordered lists
        for ol in soup.find_all('ol'):
            list_items = [li.get_text().strip() for li in ol.find_all('li')]
            list_data = {
                'type': 'ordered',
                'items': list_items,
                'start': ol.get('start', 1),  # For lists that start at a different number
            }
            lists.append(list_data)

        # Find unordered lists
        for ul in soup.find_all('ul'):
            list_items = [li.get_text().strip() for li in ul.find_all('li')]
            list_data = {
                'type': 'unordered',
                'items': list_items,
            }
            lists.append(list_data)

        return lists

    def _extract_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract tables from the page.

        Args:
            soup: BeautifulSoup object containing the page content

        Returns:
            List of table dictionaries with headers and rows
        """
        tables = []
        for table in soup.find_all('table'):
            table_data = {
                'headers': [],
                'rows': [],
                'caption': ''
            }

            # Extract caption if exists
            caption = table.find('caption')
            if caption:
                table_data['caption'] = caption.get_text().strip()

            # Extract headers
            thead = table.find('thead')
            if thead:
                header_row = thead.find('tr')
                if header_row:
                    headers = header_row.find_all(['th', 'td'])
                    table_data['headers'] = [header.get_text().strip() for header in headers]

            # Extract body rows
            tbody = table.find('tbody')
            if tbody:
                for row in tbody.find_all('tr'):
                    row_data = [cell.get_text().strip() for cell in row.find_all(['td', 'th'])]
                    if row_data:  # Only add rows that have content
                        table_data['rows'].append(row_data)
            else:
                # If no tbody, find all rows directly
                for row in table.find_all('tr'):
                    if not row.find_parent('thead'):  # Skip header row if we already processed it
                        row_data = [cell.get_text().strip() for cell in row.find_all(['td', 'th'])]
                        if row_data:
                            table_data['rows'].append(row_data)

            tables.append(table_data)

        return tables

    def _extract_code_blocks(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract code blocks from the page.

        Args:
            soup: BeautifulSoup object containing the page content

        Returns:
            List of code block dictionaries with content and language
        """
        code_blocks = []

        # Find code blocks in <pre><code> format
        for pre in soup.find_all('pre'):
            code_element = pre.find('code')
            if code_element:
                # Extract language from class
                classes = code_element.get('class', [])
                language = ''
                for cls in classes:
                    if cls.startswith('language-'):
                        language = cls.replace('language-', '')
                        break

                # If no language class, try data-language attribute
                if not language:
                    language = code_element.get('data-language', '') or code_element.get('language', '')

                code_data = {
                    'content': code_element.get_text(),
                    'language': language,
                    'filename': pre.get('data-filename', ''),  # For named code blocks
                    'copyable': True
                }
                code_blocks.append(code_data)

        # Find inline code snippets
        for code in soup.find_all('code'):
            # Skip if it's inside a <pre> tag (already processed)
            if code.find_parent('pre'):
                continue

            code_data = {
                'content': code.get_text(),
                'language': 'text',
                'filename': '',
                'copyable': False,
                'type': 'inline'
            }
            code_blocks.append(code_data)

        return code_blocks

    def _extract_images(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract images from the page.

        Args:
            soup: BeautifulSoup object containing the page content

        Returns:
            List of image dictionaries with source and alt text
        """
        images = []
        for img in soup.find_all('img'):
            img_data = {
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'width': img.get('width', ''),
                'height': img.get('height', ''),
                'classes': img.get('class', []),
            }

            # Make src absolute if it's relative
            if img_data['src'] and not img_data['src'].startswith(('http://', 'https://', '//')):
                img_data['src'] = img_data['src'].lstrip('./')

            images.append(img_data)

        return images

    def _extract_links(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract links from the page.

        Args:
            soup: BeautifulSoup object containing the page content

        Returns:
            List of link dictionaries with href and text
        """
        links = []
        for link in soup.find_all('a', href=True):
            link_data = {
                'href': link['href'],
                'text': link.get_text().strip(),
                'title': link.get('title', ''),
                'classes': link.get('class', []),
            }

            # Determine if it's an internal or external link
            if link_data['href'].startswith(('http://', 'https://')):
                link_data['type'] = 'external'
            elif link_data['href'].startswith('#'):
                link_data['type'] = 'anchor'
            elif link_data['href'].endswith(('.pdf', '.doc', '.docx', '.zip', '.rar', '.exe', '.dmg')):
                link_data['type'] = 'download'
            else:
                link_data['type'] = 'internal'

            links.append(link_data)

        return links

    def _extract_quotes(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract blockquotes from the page.

        Args:
            soup: BeautifulSoup object containing the page content

        Returns:
            List of quote dictionaries with content and attribution
        """
        quotes = []
        for blockquote in soup.find_all('blockquote'):
            quote_data = {
                'content': blockquote.get_text().strip(),
                'cite': blockquote.get('cite', ''),
                'author': ''
            }

            # Look for cite or attribution within the blockquote
            cite_elem = blockquote.find('cite')
            if cite_elem:
                quote_data['author'] = cite_elem.get_text().strip()

            quotes.append(quote_data)

        return quotes

    def get_content_summary(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Get a summary of the content types in the page.

        Args:
            soup: BeautifulSoup object containing the page content

        Returns:
            Dictionary with content type counts and summary
        """
        content_types = self.handle_content_types(soup)

        summary = {
            'total_paragraphs': len(content_types['text']),
            'total_headings': len(content_types['headings']),
            'total_lists': len(content_types['lists']),
            'total_tables': len(content_types['tables']),
            'total_code_blocks': len(content_types['code_blocks']),
            'total_images': len(content_types['images']),
            'total_links': len(content_types['links']),
            'total_quotes': len(content_types['quotes']),
            'content_types_present': [ct for ct, items in content_types.items() if len(items) > 0]
        }

        return summary

    def process_content_for_embedding(self, soup: BeautifulSoup) -> str:
        """
        Process content for embedding by combining different content types appropriately.

        Args:
            soup: BeautifulSoup object containing the page content

        Returns:
            String content optimized for embedding
        """
        content_types = self.handle_content_types(soup)

        processed_content = []

        # Add headings with appropriate prefixes to maintain hierarchy
        for heading in content_types['headings']:
            prefix = '#' * heading['level']
            processed_content.append(f"{prefix} {heading['text']}")

        # Add text content
        processed_content.extend(content_types['text'])

        # Add list items as separate lines
        for list_data in content_types['lists']:
            processed_content.append("\nList:")
            for item in list_data['items']:
                processed_content.append(f"- {item}")

        # Add table content as text
        for table in content_types['tables']:
            if table['caption']:
                processed_content.append(f"Table: {table['caption']}")
            for row in table['rows']:
                processed_content.append(" | ".join(row))

        # Add code blocks with language info
        for code_block in content_types['code_blocks']:
            if code_block.get('type') != 'inline':
                processed_content.append(f"Code Block ({code_block['language']}):\n{code_block['content']}")

        # Join all content with proper spacing
        return "\n\n".join(processed_content)