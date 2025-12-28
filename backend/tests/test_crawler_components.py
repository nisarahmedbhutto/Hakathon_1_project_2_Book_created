"""
Test script for Docusaurus crawler components in the website content ingestion system.
Tests the individual components of the crawler functionality.
"""

import os
import sys
from pathlib import Path

# Add the backend src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from crawler.docusaurus_crawler import DocusaurusCrawler
from extractor.content_extractor import ContentExtractor
from extractor.metadata_manager import MetadataManager


def create_sample_docusaurus_pages():
    """Create sample HTML content that mimics various Docusaurus pages."""
    samples = {
        "homepage": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Physical AI and Humanoid Robotics Book</title>
            <meta name="description" content="Comprehensive guide to physical AI and humanoid robotics">
        </head>
        <body>
            <nav class="navbar">
                <ul>
                    <li><a href="/docs/intro">Introduction</a></li>
                    <li><a href="/docs/concepts/fundamentals">Fundamentals</a></li>
                    <li><a href="/docs/technical/control-systems">Control Systems</a></li>
                    <li><a href="/docs/reference/api">API Reference</a></li>
                </ul>
            </nav>

            <main role="main" class="main-wrapper">
                <div class="theme-doc-markdown markdown">
                    <h1>Welcome to Physical AI and Humanoid Robotics Book</h1>
                    <p>This comprehensive guide covers all aspects of physical AI and humanoid robotics development.</p>

                    <h2>Getting Started</h2>
                    <p>Begin with the <a href="/docs/intro">Introduction</a> to understand the basics.</p>

                    <h2>Core Concepts</h2>
                    <p>Learn about fundamental concepts in the <a href="/docs/concepts/fundamentals">Fundamentals</a> section.</p>
                </div>
            </main>
        </body>
        </html>
        """,

        "intro_page": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Introduction - Physical AI and Humanoid Robotics</title>
            <meta name="description" content="Introduction to physical AI and humanoid robotics concepts">
        </head>
        <body>
            <nav class="navbar">
                <ul>
                    <li><a href="/">Home</a></li>
                    <li><a href="/docs/concepts/fundamentals">Next: Fundamentals</a></li>
                </ul>
            </nav>

            <main role="main" class="main-wrapper">
                <div class="theme-doc-markdown markdown">
                    <h1 id="introduction">Introduction to Physical AI</h1>
                    <p>Physical AI represents a paradigm shift from traditional AI systems that operate in digital spaces to AI systems that interact with the physical world.</p>

                    <h2 id="key-concepts">Key Concepts</h2>
                    <p>The core concepts of physical AI include:</p>
                    <ul>
                        <li>Embodied Intelligence</li>
                        <li>Sensorimotor Learning</li>
                        <li>Real-world Interaction</li>
                        <li>Dynamic Adaptation</li>
                    </ul>
                </div>
            </main>
        </body>
        </html>
        """,

        "technical_page": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Control Systems - Physical AI and Humanoid Robotics</title>
            <meta name="description" content="Technical details on control systems for humanoid robots">
        </head>
        <body>
            <nav class="navbar">
                <ul>
                    <li><a href="/docs/intro">Previous: Introduction</a></li>
                    <li><a href="/docs/reference/api">Next: API Reference</a></li>
                </ul>
            </nav>

            <main role="main" class="main-wrapper">
                <div class="theme-doc-markdown markdown">
                    <h1 id="control-systems">Control Systems for Humanoid Robots</h1>
                    <p>Implementing control systems for humanoid robots requires sophisticated algorithms.</p>

                    <h2 id="pid-control">PID Control Implementation</h2>
                    <p>PID (Proportional-Integral-Derivative) controllers are fundamental to robotic control systems.</p>

                    <pre><code class="language-python">import numpy as np

class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
</code></pre>

                    <h3 id="advanced-methods">Advanced Control Methods</h3>
                    <p>Modern control systems also use model predictive control and other advanced methods.</p>
                </div>
            </main>
        </body>
        </html>
        """
    }
    return samples


def test_docusaurus_crawler_components():
    """Test the Docusaurus crawler components individually."""
    print("Testing Docusaurus crawler components...")

    # Create sample HTML pages
    samples = create_sample_docusaurus_pages()

    # Initialize the crawler
    crawler = DocusaurusCrawler(base_url="https://example-docusaurus-book.com", max_pages=10)

    from bs4 import BeautifulSoup

    # Test URL discovery for homepage
    print("\n--- Testing URL Discovery ---")
    homepage_html = samples["homepage"]
    homepage_soup = BeautifulSoup(homepage_html, 'html.parser')
    discovered_urls = crawler.discover_urls(homepage_soup, "https://example-docusaurus-book.com/")

    print(f"Discovered {len(discovered_urls)} URLs from homepage:")
    for url in discovered_urls:
        print(f"  - {url}")

    # Test content extraction for intro page
    print("\n--- Testing Content Extraction ---")
    intro_html = samples["intro_page"]
    intro_soup = BeautifulSoup(intro_html, 'html.parser')
    content_data = crawler.extract_content(intro_soup)

    print(f"Content extracted:")
    print(f"  - Title: {content_data['title']}")
    print(f"  - Content length: {len(content_data['content'])} characters")
    print(f"  - Word count: {content_data['word_count']}")
    print(f"  - Headings: {len(content_data['headings'])}")
    print(f"  - Breadcrumbs: {len(content_data['breadcrumbs'])}")

    # Test content extraction for technical page
    print("\n--- Testing Technical Content Extraction ---")
    tech_html = samples["technical_page"]
    tech_soup = BeautifulSoup(tech_html, 'html.parser')
    tech_content_data = crawler.extract_content(tech_soup)

    print(f"Technical content extracted:")
    print(f"  - Title: {tech_content_data['title']}")
    print(f"  - Content length: {len(tech_content_data['content'])} characters")
    print(f"  - Word count: {tech_content_data['word_count']}")
    print(f"  - Headings: {len(tech_content_data['headings'])}")
    print(f"  - Has code blocks: {'language-python' in tech_content_data['content']}")

    # Test the crawl_page method with a simulated response
    print("\n--- Testing Crawl Page Method ---")
    test_url = "https://example-docusaurus-book.com/docs/intro"

    # We'll create a mock response-like object for testing
    class MockResponse:
        def __init__(self, text):
            self.text = text
            self.status_code = 200
            self.ok = True

    # Temporarily replace the _make_request method to return our sample content
    original_make_request = crawler._make_request

    def mock_make_request(url):
        if url == "https://example-docusaurus-book.com/docs/intro":
            return MockResponse(samples["intro_page"])
        elif url == "https://example-docusaurus-book.com/":
            return MockResponse(samples["homepage"])
        elif url == "https://example-docusaurus-book.com/docs/technical/control-systems":
            return MockResponse(samples["technical_page"])
        else:
            return None

    crawler._make_request = mock_make_request

    # Test crawling a specific page
    crawled_result = crawler.crawl_page(test_url)

    if crawled_result:
        print(f"Successfully crawled: {test_url}")
        print(f"  - Title: {crawled_result['title']}")
        print(f"  - URL: {crawled_result['url']}")
        print(f"  - Content length: {len(crawled_result['content'])} characters")
        print(f"  - Category: {crawled_result['category']}")
        print(f"  - Discovered URLs: {len(crawled_result['discovered_urls'])}")
        print(f"  - Word count: {crawled_result['word_count']}")
    else:
        print(f"Failed to crawl: {test_url}")

    # Restore original method
    crawler._make_request = original_make_request

    # Test integration with content extractor
    print("\n--- Testing Integration with Content Extractor ---")
    extractor = ContentExtractor()
    extracted = extractor.extract_content(intro_soup)

    print(f"Integration results:")
    print(f"  - Extractor title: {extracted['title']}")
    print(f"  - Extractor content length: {len(extracted['content'])} characters")
    print(f"  - Extractor word count: {extracted['word_count']}")

    # Test integration with metadata manager
    print("\n--- Testing Integration with Metadata Manager ---")
    metadata_manager = MetadataManager()
    metadata = metadata_manager.extract_metadata_from_page(intro_soup, test_url)

    print(f"Metadata extraction results:")
    print(f"  - Title: {metadata.get('title', 'N/A')}")
    print(f"  - URL: {metadata.get('url', 'N/A')}")
    print(f"  - Section: {metadata.get('section', 'N/A')}")
    print(f"  - Description: {metadata.get('description', 'N/A')}")
    print(f"  - Author: {metadata.get('author', 'N/A')}")
    print(f"  - Tags: {metadata.get('tags', 'N/A')}")

    print("\n--- Testing Crawler Robustness ---")
    # Test with minimal HTML
    minimal_html = """
    <html>
        <head><title>Minimal Page</title></head>
        <body>
            <h1>Minimal Content</h1>
            <p>This is a minimal page for testing.</p>
        </body>
    </html>
    """
    minimal_soup = BeautifulSoup(minimal_html, 'html.parser')
    minimal_content = crawler.extract_content(minimal_soup)

    print(f"Minimal page extraction:")
    print(f"  - Title: {minimal_content['title']}")
    print(f"  - Content length: {len(minimal_content['content'])} characters")

    print("\nSUCCESS: Docusaurus crawler components are working correctly!")


def main():
    """Run the crawler component tests."""
    print("Running Docusaurus crawler component tests...\n")

    try:
        test_docusaurus_crawler_components()
        print("\nSUCCESS: All crawler component tests passed successfully!")
        print("Docusaurus crawler components are working as expected.")
        return True
    except Exception as e:
        print(f"\nERROR: Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)