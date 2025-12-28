"""
Main module for the website content ingestion system.
Orchestrates the complete pipeline: crawling, extracting, chunking, embedding, and storing.
"""

import asyncio
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from crawler.docusaurus_crawler import DocusaurusCrawler
from extractor.content_extractor import ContentExtractor
from extractor.metadata_manager import MetadataManager
from embedder.chunker import ContentChunker, ChunkConfig
from embedder.generator import EmbeddingGenerator
from vector_store.qdrant_client import QdrantConnector
from vector_store.vector_store import VectorStore


# Load environment variables
load_dotenv()


class WebsiteContentIngestor:
    """
    Main orchestrator for the website content ingestion pipeline.
    """

    def __init__(
        self,
        base_url: str,
        cohere_api_key: Optional[str] = None,
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        collection_name: str = "website_content_embeddings"
    ):
        """
        Initialize the website content ingestor.

        Args:
            base_url: Base URL of the website to crawl
            cohere_api_key: Cohere API key
            qdrant_url: Qdrant Cloud URL
            qdrant_api_key: Qdrant API key
            collection_name: Name of the Qdrant collection
        """
        self.base_url = base_url

        # Initialize crawler
        self.crawler = DocusaurusCrawler(base_url=base_url, max_pages=100)

        # Initialize Qdrant connector
        self.qdrant_connector = QdrantConnector(
            url=qdrant_url,
            api_key=qdrant_api_key,
            collection_name=collection_name
        )

        # Initialize embedding generator
        self.embedding_generator = EmbeddingGenerator(api_key=cohere_api_key)

        # Initialize vector store
        self.vector_store = VectorStore(
            qdrant_connector=self.qdrant_connector,
            embedding_generator=self.embedding_generator
        )

    async def initialize(self, recreate_collection: bool = False):
        """
        Initialize the vector store collection.

        Args:
            recreate_collection: Whether to recreate the collection if it exists
        """
        self.qdrant_connector.initialize_collection(recreate=recreate_collection)

    async def process_website(self) -> Dict[str, Any]:
        """
        Process the entire website: crawl, extract, embed, and store.

        Returns:
            Dictionary with results of the processing operation
        """
        print(f"Starting to process website: {self.base_url}")

        # Step 1: Crawl the website
        print("Step 1: Crawling website...")
        crawled_pages = await self.crawler.crawl()
        print(f"Crawled {len(crawled_pages)} pages")

        if not crawled_pages:
            return {
                'success': False,
                'message': 'No pages crawled from the website',
                'crawled_pages': 0,
                'processed_pages': 0,
                'stored_embeddings': 0
            }

        # Prepare content for processing
        content_items = []
        for page_data in crawled_pages:
            content_items.append({
                'content': page_data.get('content', ''),
                'metadata': {
                    'url': page_data.get('url', ''),
                    'title': page_data.get('title', ''),
                    'category': page_data.get('category', ''),
                    'description': page_data.get('description', ''),
                    'word_count': page_data.get('word_count', 0),
                    'discovered_urls': page_data.get('discovered_urls', [])
                }
            })

        # Step 2: Process content in vector store
        print("Step 2: Processing content (chunking, embedding, storing)...")
        results = await self.vector_store.batch_store_content(content_items)

        return {
            'success': results['success'],
            'message': f"Processed {results['successful_items']}/{results['total_items']} pages",
            'crawled_pages': len(crawled_pages),
            'processed_pages': results['successful_items'],
            'failed_pages': results['failed_items'],
            'stored_embeddings': results['total_embeddings_stored'],
            'success_rate': results['success_rate']
        }

    async def search_content(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for content in the vector store.

        Args:
            query: Query string to search for
            limit: Maximum number of results to return

        Returns:
            List of search results
        """
        return self.vector_store.search_content(query, limit=limit)

    async def get_store_info(self) -> Dict[str, Any]:
        """
        Get information about the vector store.

        Returns:
            Dictionary with store information
        """
        return self.vector_store.get_store_info()


def create_ingestor(
    base_url: str,
    cohere_api_key: Optional[str] = None,
    qdrant_url: Optional[str] = None,
    qdrant_api_key: Optional[str] = None,
    collection_name: str = "website_content_embeddings"
) -> WebsiteContentIngestor:
    """
    Create a website content ingestor instance.

    Args:
        base_url: Base URL of the website to crawl
        cohere_api_key: Cohere API key
        qdrant_url: Qdrant Cloud URL
        qdrant_api_key: Qdrant API key
        collection_name: Name of the Qdrant collection

    Returns:
        WebsiteContentIngestor instance
    """
    return WebsiteContentIngestor(
        base_url, cohere_api_key, qdrant_url, qdrant_api_key, collection_name
    )


async def main():
    """
    Main function to demonstrate the website content ingestion pipeline.
    """
    # Example usage
    base_url = os.getenv("WEBSITE_URL", "https://example-docusaurus-book.com")
    cohere_api_key = os.getenv("COHERE_API_KEY")
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not cohere_api_key:
        print("Error: COHERE_API_KEY environment variable is required")
        return

    if not qdrant_api_key:
        print("Error: QDRANT_API_KEY environment variable is required")
        return

    # Create ingestor
    ingestor = WebsiteContentIngestor(
        base_url=base_url,
        cohere_api_key=cohere_api_key,
        qdrant_url=qdrant_url,
        qdrant_api_key=qdrant_api_key
    )

    # Initialize the vector store
    await ingestor.initialize(recreate_collection=False)

    # Process the website
    results = await ingestor.process_website()
    print(f"Processing results: {results}")

    # Example search
    search_results = await ingestor.search_content("Physical AI concepts", limit=5)
    print(f"Search results: {len(search_results)} items found")


if __name__ == "__main__":
    # Note: This would require actual API keys to run
    # asyncio.run(main())
    print("Website content ingestion system initialized.")
    print("To use the system, set environment variables and call the appropriate methods.")