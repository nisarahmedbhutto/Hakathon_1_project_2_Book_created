"""
Qdrant client module for connecting to Qdrant vector database in the website content ingestion system.
"""

import os
from typing import Optional, Dict, Any, List
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


class QdrantConnector:
    """
    Qdrant client connector for vector storage and retrieval operations.
    """

    def __init__(
        self,
        location: Optional[str] = None,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        collection_name: str = "website_content_embeddings",
        vector_size: int = 1024  # Default size for Cohere embeddings
    ):
        """
        Initialize the Qdrant client connector.

        Args:
            location: If specified, connects to a local Qdrant instance (e.g., ":memory:" or path)
            url: URL for Qdrant Cloud or remote instance
            api_key: API key for Qdrant Cloud
            collection_name: Name of the collection to use
            vector_size: Size of the embedding vectors
        """
        self.collection_name = collection_name
        self.vector_size = vector_size

        # Determine connection parameters
        if location:
            # Local instance
            self.client = QdrantClient(location=location)
        elif url:
            # Remote instance (Qdrant Cloud)
            api_key = api_key or os.getenv("QDRANT_API_KEY")
            if not api_key:
                raise ValueError("Qdrant API key is required for remote connections. Set QDRANT_API_KEY environment variable.")

            self.client = QdrantClient(
                url=url,
                api_key=api_key,
                prefer_grpc=True  # Use gRPC for better performance
            )
        else:
            # Default to in-memory for testing
            self.client = QdrantClient(location=":memory:")

        self._collection_initialized = False

    def initialize_collection(self, recreate: bool = False):
        """
        Initialize the collection with appropriate vector parameters.

        Args:
            recreate: Whether to recreate the collection if it exists
        """
        # Check if collection exists
        collection_exists = False
        try:
            self.client.get_collection(self.collection_name)
            collection_exists = True
        except:
            collection_exists = False

        if collection_exists and not recreate:
            print(f"Collection '{self.collection_name}' already exists, using existing collection.")
            self._collection_initialized = True
            return

        if collection_exists and recreate:
            print(f"Recreating collection '{self.collection_name}'...")
            self.client.delete_collection(self.collection_name)

        # Create collection with vector parameters
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=Distance.COSINE  # Cosine distance is good for text embeddings
            )
        )

        print(f"Collection '{self.collection_name}' created successfully.")
        self._collection_initialized = True

    def store_embeddings(
        self,
        embeddings_data: List[Dict[str, Any]],
        batch_size: int = 64
    ) -> bool:
        """
        Store embeddings in the Qdrant collection.

        Args:
            embeddings_data: List of dictionaries containing embeddings and metadata
            batch_size: Number of embeddings to store in each batch

        Returns:
            True if successful, False otherwise
        """
        if not self._collection_initialized:
            raise RuntimeError("Collection not initialized. Call initialize_collection() first.")

        if not embeddings_data:
            print("No embeddings to store.")
            return True

        try:
            # Process embeddings in batches
            for i in range(0, len(embeddings_data), batch_size):
                batch = embeddings_data[i:i + batch_size]

                # Prepare points for Qdrant
                points = []
                for item in batch:
                    payload = {
                        'content': item.get('content', ''),
                        'source_url': item.get('metadata', {}).get('url', ''),
                        'title': item.get('metadata', {}).get('title', ''),
                        'section': item.get('metadata', {}).get('section', ''),
                        'author': item.get('metadata', {}).get('author', ''),
                        'description': item.get('metadata', {}).get('description', ''),
                        'word_count': item.get('word_count', 0),
                        'chunk_index': item.get('chunk_index', 0),
                        'source_hash': item.get('source_hash', 0)
                    }

                    # Add any additional metadata fields
                    metadata = item.get('metadata', {})
                    for key, value in metadata.items():
                        if key not in payload:
                            payload[key] = value

                    point = models.PointStruct(
                        id=item.get('id', f"doc_{len(points) + i}"),
                        vector=item.get('embedding', []),
                        payload=payload
                    )
                    points.append(point)

                # Upload batch to Qdrant
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )

                print(f"Stored batch {i//batch_size + 1}/{(len(embeddings_data)-1)//batch_size + 1}")

            print(f"Successfully stored {len(embeddings_data)} embeddings in Qdrant.")
            return True

        except Exception as e:
            print(f"Error storing embeddings in Qdrant: {str(e)}")
            return False

    def search_embeddings(
        self,
        query_embedding: List[float],
        limit: int = 10,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings in the Qdrant collection.

        Args:
            query_embedding: The embedding vector to search for
            limit: Maximum number of results to return
            filter_conditions: Optional filter conditions (e.g., {'url': 'specific_url'})

        Returns:
            List of similar embeddings with metadata
        """
        if not self._collection_initialized:
            raise RuntimeError("Collection not initialized. Call initialize_collection() first.")

        try:
            # Prepare filters if provided
            filters = None
            if filter_conditions:
                filter_conditions_list = []
                for key, value in filter_conditions.items():
                    filter_conditions_list.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        )
                    )

                if filter_conditions_list:
                    filters = models.Filter(must=filter_conditions_list)

            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=filters,
                limit=limit,
                with_payload=True,
                with_vectors=False  # Don't return vectors to save bandwidth
            )

            # Format results
            results = []
            for result in search_results:
                formatted_result = {
                    'id': result.id,
                    'content': result.payload.get('content', ''),
                    'source_url': result.payload.get('source_url', ''),
                    'title': result.payload.get('title', ''),
                    'section': result.payload.get('section', ''),
                    'author': result.payload.get('author', ''),
                    'description': result.payload.get('description', ''),
                    'word_count': result.payload.get('word_count', 0),
                    'chunk_index': result.payload.get('chunk_index', 0),
                    'source_hash': result.payload.get('source_hash', 0),
                    'score': result.score
                }

                # Add any additional metadata fields
                for key, value in result.payload.items():
                    if key not in formatted_result and key not in ['content', 'source_url', 'title', 'section', 'author', 'description']:
                        formatted_result[key] = value

                results.append(formatted_result)

            return results

        except Exception as e:
            print(f"Error searching embeddings in Qdrant: {str(e)}")
            return []

    def get_embedding_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific embedding by its ID.

        Args:
            doc_id: The ID of the document to retrieve

        Returns:
            The embedding data if found, None otherwise
        """
        if not self._collection_initialized:
            raise RuntimeError("Collection not initialized. Call initialize_collection() first.")

        try:
            records = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[doc_id],
                with_payload=True,
                with_vectors=True
            )

            if records:
                record = records[0]
                return {
                    'id': record.id,
                    'embedding': record.vector,
                    'content': record.payload.get('content', ''),
                    'source_url': record.payload.get('source_url', ''),
                    'title': record.payload.get('title', ''),
                    'section': record.payload.get('section', ''),
                    'author': record.payload.get('author', ''),
                    'description': record.payload.get('description', ''),
                    'word_count': record.payload.get('word_count', 0),
                    'chunk_index': record.payload.get('chunk_index', 0),
                    'source_hash': record.payload.get('source_hash', 0)
                }

            return None

        except Exception as e:
            print(f"Error retrieving embedding by ID: {str(e)}")
            return None

    def delete_collection(self) -> bool:
        """
        Delete the entire collection.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_collection(self.collection_name)
            self._collection_initialized = False
            print(f"Collection '{self.collection_name}' deleted successfully.")
            return True
        except Exception as e:
            print(f"Error deleting collection: {str(e)}")
            return False

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.

        Returns:
            Dictionary with collection information
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                'name': collection_info.config.params.vectors.size,
                'vector_size': collection_info.config.params.vectors.size,
                'distance': collection_info.config.params.vectors.distance,
                'point_count': collection_info.points_count,
                'indexed_vectors_count': collection_info.indexed_vectors_count
            }
        except Exception as e:
            print(f"Error getting collection info: {str(e)}")
            return {}


def create_qdrant_connector(
    location: Optional[str] = None,
    url: Optional[str] = None,
    api_key: Optional[str] = None,
    collection_name: str = "website_content_embeddings",
    vector_size: int = 1024
) -> QdrantConnector:
    """
    Create a Qdrant connector instance.

    Args:
        location: Local instance location
        url: Remote instance URL
        api_key: API key for remote instance
        collection_name: Name of the collection
        vector_size: Size of embedding vectors

    Returns:
        QdrantConnector instance
    """
    return QdrantConnector(location, url, api_key, collection_name, vector_size)