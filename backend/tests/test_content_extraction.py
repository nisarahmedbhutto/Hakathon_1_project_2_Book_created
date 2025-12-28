"""
Test script for content extraction functionality in the website content ingestion system.
Tests the content extraction, cleaning, and metadata preservation features.
"""

import os
import sys
from pathlib import Path

# Add the backend src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from extractor.content_extractor import ContentExtractor
from extractor.cleaner import clean_html_noise, extract_content_structure
from extractor.metadata_manager import MetadataManager, extract_page_metadata
from extractor.content_handler import ContentHandler
import tempfile
import json


def create_sample_html():
    """Create sample HTML content that mimics a Docusaurus page."""
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sample Docusaurus Page - Physical AI and Humanoid Robotics</title>
        <meta name="description" content="Learn about physical AI and humanoid robotics">
        <meta name="keywords" content="AI, robotics, humanoid, physical AI">
        <meta name="author" content="Book Author">
        <link rel="canonical" href="https://example.com/docs/intro">
    </head>
    <body>
        <header class="navbar">
            <nav>Navigation content to be removed</nav>
        </header>

        <main role="main" class="main-wrapper">
            <div class="theme-doc-markdown markdown">
                <h1 id="introduction">Introduction to Physical AI</h1>

                <p>This is the introduction paragraph for the Physical AI and Humanoid Robotics book.</p>

                <h2 id="what-is-physical-ai">What is Physical AI?</h2>

                <p>Physical AI refers to artificial intelligence systems that interact with the physical world.</p>

                <div class="theme-admonition">
                    <p>This is an admonition box that should be removed during cleaning.</p>
                </div>

                <h3 id="key-concepts">Key Concepts</h3>

                <ul>
                    <li>Embodied Intelligence</li>
                    <li>Sensorimotor Learning</li>
                    <li>Real-world Interaction</li>
                </ul>

                <table>
                    <thead>
                        <tr>
                            <th>Technology</th>
                            <th>Application</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Machine Learning</td>
                            <td>Pattern Recognition</td>
                        </tr>
                        <tr>
                            <td>Computer Vision</td>
                            <td>Object Detection</td>
                        </tr>
                    </tbody>
                </table>

                <pre><code class="language-python">import numpy as np
def calculate_force(mass, acceleration):
    return mass * acceleration
</code></pre>

                <p>Another paragraph with <code>inline code</code> and <strong>bold text</strong>.</p>

                <blockquote>
                    <p>"The future of AI lies in its physical embodiment."</p>
                    <cite>Researcher</cite>
                </blockquote>

                <a href="/docs/next-page" class="theme-edit-this-page">Edit this page</a>
                <div class="theme-last-updated">Last updated: 2025-01-15</div>
            </div>

            <nav class="pagination-nav">
                <div>Previous: <a href="/docs/prev">Previous Page</a></div>
                <div>Next: <a href="/docs/next">Next Page</a></div>
            </nav>
        </main>

        <footer class="footer">
            <p>Footer content to be removed</p>
        </footer>

        <script>
            console.log('This script should be removed');
        </script>
    </body>
    </html>
    """
    return sample_html


def test_content_extraction():
    """Test the content extraction functionality."""
    print("Testing content extraction functionality...")

    # Create sample HTML
    sample_html = create_sample_html()
    url = "https://example.com/docs/intro"

    # Create BeautifulSoup object from HTML
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(sample_html, 'html.parser')

    # Test content extractor
    extractor = ContentExtractor()
    extracted_content = extractor.extract_content(soup)

    print("SUCCESS: Content extracted successfully")
    print(f"  - Content length: {len(extracted_content['content'])} characters")
    print(f"  - Word count: {extracted_content['word_count']}")
    print(f"  - Title: {extracted_content['title']}")

    # Verify that noise has been removed
    assert "Navigation content to be removed" not in extracted_content['content']
    assert "Footer content to be removed" not in extracted_content['content']
    assert "Edit this page" not in extracted_content['content']
    assert "Last updated:" not in extracted_content['content']
    print("SUCCESS: HTML noise successfully removed")

    # Test metadata extraction
    metadata = extracted_content['metadata']
    print(f"  - Metadata keys: {list(metadata.keys())}")

    # Verify important metadata is present
    assert 'description' in metadata
    assert 'author' in metadata
    assert 'keywords' in metadata
    assert 'canonical_url' in metadata
    print("SUCCESS: Required metadata fields present")

    return extracted_content


def test_content_cleaning():
    """Test the content cleaning functionality."""
    print("\nTesting content cleaning functionality...")

    sample_html = create_sample_html()

    # Test basic cleaning
    clean_text = clean_html_noise(sample_html)
    print(f"SUCCESS: Basic cleaning completed - content length: {len(clean_text)} characters")

    # Verify noise elements are removed
    assert "Navigation content to be removed" not in clean_text
    assert "Footer content to be removed" not in clean_text
    assert "console.log" not in clean_text
    print("SUCCESS: Noise elements removed from cleaned content")

    # Test structured extraction
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(sample_html, 'html.parser')
    structured_content = extract_content_structure(soup)

    print(f"  - Title: {structured_content['title']}")
    print(f"  - Word count: {structured_content['word_count']}")
    print(f"  - Headings count: {len(structured_content['headings'])}")

    # Verify structured content
    assert structured_content['title'] == "Sample Docusaurus Page - Physical AI and Humanoid Robotics"
    assert structured_content['word_count'] > 0
    assert len(structured_content['headings']) > 0
    print("SUCCESS: Structured content extracted correctly")


def test_metadata_extraction():
    """Test the metadata extraction functionality."""
    print("\nTesting metadata extraction functionality...")

    sample_html = create_sample_html()
    url = "https://example.com/docs/intro"

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(sample_html, 'html.parser')

    # Test metadata manager
    metadata_manager = MetadataManager()
    metadata = metadata_manager.extract_metadata_from_page(soup, url)

    print(f"  - URL: {metadata['url']}")
    print(f"  - Title: {metadata['title']}")
    print(f"  - Section: {metadata['section']}")
    print(f"  - Description: {metadata.get('description', 'N/A')}")
    print(f"  - Author: {metadata.get('author', 'N/A')}")
    print(f"  - Tags: {metadata.get('tags', 'N/A')}")
    print(f"  - Canonical URL: {metadata.get('canonical_url', 'N/A')}")

    # Verify important metadata is extracted
    assert metadata['url'] == url
    assert metadata['title'] == "Sample Docusaurus Page - Physical AI and Humanoid Robotics"
    assert 'description' in metadata
    assert 'author' in metadata
    assert 'tags' in metadata
    assert 'canonical_url' in metadata
    print("SUCCESS: Metadata extracted correctly")


def test_content_handling():
    """Test the content handling functionality."""
    print("\nTesting content handling functionality...")

    sample_html = create_sample_html()

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(sample_html, 'html.parser')

    # Test content handler
    handler = ContentHandler()
    content_by_type = handler.handle_content_types(soup)

    print(f"  - Text paragraphs: {len(content_by_type['text'])}")
    print(f"  - Headings: {len(content_by_type['headings'])}")
    print(f"  - Lists: {len(content_by_type['lists'])}")
    print(f"  - Tables: {len(content_by_type['tables'])}")
    print(f"  - Code blocks: {len(content_by_type['code_blocks'])}")
    print(f"  - Images: {len(content_by_type['images'])}")
    print(f"  - Links: {len(content_by_type['links'])}")
    print(f"  - Quotes: {len(content_by_type['quotes'])}")

    # Verify content types are extracted
    assert len(content_by_type['text']) > 0
    assert len(content_by_type['headings']) > 0
    assert len(content_by_type['lists']) > 0
    assert len(content_by_type['tables']) > 0
    assert len(content_by_type['code_blocks']) > 0
    print("SUCCESS: Content types extracted correctly")

    # Test content summary
    summary = handler.get_content_summary(soup)
    print(f"  - Content summary: {summary}")

    # Test content for embedding
    embedding_content = handler.process_content_for_embedding(soup)
    print(f"  - Embedding content length: {len(embedding_content)} characters")
    assert len(embedding_content) > 0
    print("SUCCESS: Content processed for embedding")


def test_validation():
    """Test the metadata validation functionality."""
    print("\nTesting metadata validation functionality...")

    sample_html = create_sample_html()
    url = "https://example.com/docs/intro"

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(sample_html, 'html.parser')

    # Test metadata manager
    metadata_manager = MetadataManager()
    metadata = metadata_manager.extract_metadata_from_page(soup, url)

    # Test validation
    validation_results = metadata_manager.validate_metadata_completeness(metadata)

    print(f"  - URL present: {validation_results['url_present']}")
    print(f"  - Title present: {validation_results['title_present']}")
    print(f"  - Section present: {validation_results['section_present']}")
    print(f"  - Description present: {validation_results.get('description_present', 'N/A')}")
    print(f"  - Metadata complete: {validation_results['metadata_complete']}")

    assert validation_results['url_present']
    assert validation_results['title_present']
    assert validation_results['section_present']
    assert validation_results['metadata_complete']
    print("SUCCESS: Metadata validation working correctly")


def main():
    """Run all content extraction tests."""
    print("Running content extraction tests...\n")

    try:
        test_content_extraction()
        test_content_cleaning()
        test_metadata_extraction()
        test_content_handling()
        test_validation()

        print("\nSUCCESS: All content extraction tests passed successfully!")
        print("Content extraction functionality is working as expected.")

    except Exception as e:
        print(f"\nERROR: Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)