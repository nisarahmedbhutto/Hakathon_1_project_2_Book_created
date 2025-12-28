"""
Vector storage module for storing and retrieving embeddings in Qdrant
in the website content ingestion system.
"""

import asyncio
from typing import List, Dict, Any, Optional
from .qdrant_client import QdrantConnector
from ..embedder.chunker import ContentChunker, ChunkConfig
from ..embedder.generator import EmbeddingGenerator


class VectorStore:
    """
    Vector storage manager that orchestrates the process of chunking content,
    generating embeddings, and storing them in Qdrant.
    """

    def __init__(
        self,
        qdrant_connector: QdrantConnector,
        embedding_generator: EmbeddingGenerator,
        chunker: Optional[ContentChunker] = None
    ):
        """
        Initialize the vector store.

        Args:
            qdrant_connector: Qdrant connector instance
            embedding_generator: Embedding generator instance
            chunker: Content chunker instance (uses default if None)
        """
        self.qdrant_connector = qdrant_connector
        self.embedding_generator = embedding_generator
        self.chunker = chunker or ContentChunker()

    async def store_content(
        self,
        content: str,
        metadata: Dict[str, Any],
        chunk_config: Optional[ChunkConfig] = None
    ) -> Dict[str, Any]:
        """
        Process content by chunking, embedding, and storing in vector store.

        Args:
            content: The content to store
            metadata: Metadata associated with the content
            chunk_config: Configuration for chunking (uses default if None)

        Returns:
            Dictionary with results of the storage operation
        """
        # Chunk the content
        chunks = self.chunker.chunk_content(content, metadata)
        print(f"Content chunked into {len(chunks)} pieces.")

        if not chunks:
            return {
                'success': False,
                'message': 'No valid chunks generated from content',
                'chunks_processed': 0,
                'embeddings_stored': 0
            }

        # Generate embeddings
        print("Generating embeddings...")
        embeddings_data = await self.embedding_generator.generate_embeddings_with_metadata(chunks)
        print(f"Generated embeddings for {len(embeddings_data)} chunks.")

        # Validate embedding quality
        embeddings_only = [item['embedding'] for item in embeddings_data if 'embedding' in item]
        validation_results = await self.embedding_generator.validate_embedding_quality(embeddings_only)
        print(f"Embedding quality: {validation_results['quality_score']:.2%} valid")

        if validation_results['quality_score'] < 0.5:  # Less than 50% valid
            return {
                'success': False,
                'message': f'Low embedding quality: {validation_results["quality_score"]:.2%}',
                'chunks_processed': len(chunks),
                'embeddings_generated': len(embeddings_data),
                'quality_score': validation_results['quality_score']
            }

        # Store in Qdrant
        print("Storing embeddings in Qdrant...")
        success = self.qdrant_connector.store_embeddings(embeddings_data)

        if success:
            return {
                'success': True,
                'message': f'Successfully stored {len(embeddings_data)} embeddings',
                'chunks_processed': len(chunks),
                'embeddings_stored': len(embeddings_data),
                'quality_score': validation_results['quality_score']
            }
        else:
            return {
                'success': False,
                'message': 'Failed to store embeddings in Qdrant',
                'chunks_processed': len(chunks),
                'embeddings_generated': len(embeddings_data),
                'quality_score': validation_results['quality_score']
            }

    async def batch_store_content(
        self,
        contents: List[Dict[str, Any]],
        chunk_config: Optional[ChunkConfig] = None
    ) -> Dict[str, Any]:
        """
        Process multiple content items in a batch.

        Args:
            contents: List of dictionaries containing 'content' and 'metadata'
            chunk_config: Configuration for chunking (uses default if None)

        Returns:
            Dictionary with results of the batch storage operation
        """
        all_results = []
        total_chunks = 0
        total_embeddings = 0

        for i, item in enumerate(contents):
            content = item.get('content', '')
            metadata = item.get('metadata', {})

            print(f"Processing item {i+1}/{len(contents)}...")
            result = await self.store_content(content, metadata, chunk_config)
            all_results.append(result)

            if result['success']:
                total_chunks += result['chunks_processed']
                total_embeddings += result['embeddings_stored']

        successful_items = sum(1 for r in all_results if r['success'])
        failed_items = len(all_results) - successful_items

        return {
            'success': failed_items == 0,
            'total_items': len(contents),
            'successful_items': successful_items,
            'failed_items': failed_items,
            'total_chunks_processed': total_chunks,
            'total_embeddings_stored': total_embeddings,
            'success_rate': successful_items / len(contents) if contents else 0,
            'item_results': all_results
        }

    def search_content(
        self,
        query: str,
        limit: int = 10,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for content similar to the query.

        Args:
            query: Query text to search for
            limit: Maximum number of results to return
            filter_conditions: Optional filter conditions

        Returns:
            List of similar content with metadata
        """
        # Generate embedding for the query
        query_embedding = asyncio.run(
            self.embedding_generator.generate_embedding(query)
        )

        if not query_embedding:
            print("Failed to generate query embedding")
            return []

        # Search in Qdrant
        results = self.qdrant_connector.search_embeddings(
            query_embedding,
            limit=limit,
            filter_conditions=filter_conditions
        )

        return results

    def get_content_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve specific content by its ID.

        Args:
            doc_id: The ID of the document to retrieve

        Returns:
            The content data if found, None otherwise
        """
        return self.qdrant_connector.get_embedding_by_id(doc_id)

    def get_store_info(self) -> Dict[str, Any]:
        """
        Get information about the vector store.

        Returns:
            Dictionary with store information
        """
        return self.qdrant_connector.get_collection_info()


def create_vector_store(
    qdrant_connector: QdrantConnector,
    embedding_generator: EmbeddingGenerator,
    chunker: Optional[ContentChunker] = None
) -> VectorStore:
    """
    Create a vector store instance.

    Args:
        qdrant_connector: Qdrant connector instance
        embedding_generator: Embedding generator instance
        chunker: Content chunker instance

    Returns:
        VectorStore instance
    """
    return VectorStore(qdrant_connector, embedding_generator, chunker)