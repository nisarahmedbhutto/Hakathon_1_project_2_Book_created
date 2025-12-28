"""
Embedding generator module for generating vector embeddings using Cohere models
in the website content ingestion system.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
import cohere
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


class EmbeddingGenerator:
    """
    Embedding generator that uses Cohere models to generate vector embeddings.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "embed-multilingual-v3.0"):
        """
        Initialize the embedding generator.

        Args:
            api_key: Cohere API key (defaults to COHERE_API_KEY environment variable)
            model: Cohere embedding model to use
        """
        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        if not self.api_key:
            raise ValueError("Cohere API key is required. Set COHERE_API_KEY environment variable.")

        self.model = model
        self.client = cohere.AsyncClient(self.api_key)

    async def generate_embeddings(self, texts: List[str], batch_size: int = 96) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to generate embeddings for
            batch_size: Number of texts to process in each batch

        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        if not texts:
            return []

        all_embeddings = []

        # Process texts in batches to respect API limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                response = await self.client.embed(
                    texts=batch,
                    model=self.model,
                    input_type="search_document"  # Optimize for search applications
                )
                all_embeddings.extend(response.embeddings)
            except Exception as e:
                print(f"Error generating embeddings for batch {i//batch_size + 1}: {str(e)}")
                # Return empty embeddings for failed batch to maintain alignment
                all_embeddings.extend([[] for _ in range(len(batch))])

        return all_embeddings

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text string to generate embedding for

        Returns:
            Embedding as a list of floats
        """
        embeddings = await self.generate_embeddings([text])
        return embeddings[0] if embeddings else []

    async def generate_embeddings_with_metadata(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate embeddings for content chunks and return with metadata.

        Args:
            chunks: List of content chunks with metadata

        Returns:
            List of dictionaries containing embeddings and metadata
        """
        if not chunks:
            return []

        # Extract just the content for embedding generation
        texts = [chunk['content'] for chunk in chunks]

        # Generate embeddings
        embeddings = await self.generate_embeddings(texts)

        # Combine embeddings with original metadata
        result = []
        for chunk, embedding in zip(chunks, embeddings):
            if embedding:  # Only include if embedding was generated successfully
                chunk_result = {
                    'id': chunk.get('id', f"doc_{len(result)}"),
                    'content': chunk['content'],
                    'embedding': embedding,
                    'metadata': chunk.get('metadata', {}),
                    'chunk_index': chunk.get('chunk_index', 0),
                    'word_count': chunk.get('word_count', len(chunk['content'].split())),
                    'source_hash': chunk.get('source_hash', 0)
                }
                result.append(chunk_result)

        return result

    async def validate_embedding_quality(
        self,
        embeddings: List[List[float]],
        threshold: float = 0.1
    ) -> Dict[str, Any]:
        """
        Validate the quality of generated embeddings.

        Args:
            embeddings: List of embeddings to validate
            threshold: Minimum average magnitude threshold

        Returns:
            Dictionary with validation results
        """
        if not embeddings:
            return {
                'valid_count': 0,
                'invalid_count': 0,
                'average_magnitude': 0.0,
                'quality_score': 0.0,
                'all_valid': False
            }

        valid_count = 0
        total_magnitude = 0.0

        for embedding in embeddings:
            if not embedding:
                continue

            # Calculate magnitude of the embedding vector
            magnitude = sum(x ** 2 for x in embedding) ** 0.5
            total_magnitude += magnitude

            if magnitude > threshold:
                valid_count += 1

        avg_magnitude = total_magnitude / len(embeddings) if embeddings else 0
        quality_score = valid_count / len(embeddings) if embeddings else 0

        return {
            'valid_count': valid_count,
            'invalid_count': len(embeddings) - valid_count,
            'average_magnitude': avg_magnitude,
            'quality_score': quality_score,
            'all_valid': quality_score == 1.0
        }


def create_embedding_generator(
    api_key: Optional[str] = None,
    model: str = "embed-multilingual-v3.0"
) -> EmbeddingGenerator:
    """
    Create an embedding generator instance.

    Args:
        api_key: Cohere API key
        model: Cohere embedding model to use

    Returns:
        EmbeddingGenerator instance
    """
    return EmbeddingGenerator(api_key, model)


# Synchronous wrapper functions for easier use
def generate_embeddings_sync(
    texts: List[str],
    api_key: Optional[str] = None,
    model: str = "embed-multilingual-v3.0"
) -> List[List[float]]:
    """
    Synchronous wrapper for generating embeddings.

    Args:
        texts: List of text strings to generate embeddings for
        api_key: Cohere API key
        model: Cohere embedding model to use

    Returns:
        List of embeddings
    """
    generator = EmbeddingGenerator(api_key, model)

    async def run_async():
        return await generator.generate_embeddings(texts)

    return asyncio.run(run_async())


def generate_embedding_sync(
    text: str,
    api_key: Optional[str] = None,
    model: str = "embed-multilingual-v3.0"
) -> List[float]:
    """
    Synchronous wrapper for generating a single embedding.

    Args:
        text: Text string to generate embedding for
        api_key: Cohere API key
        model: Cohere embedding model to use

    Returns:
        Embedding as a list of floats
    """
    generator = EmbeddingGenerator(api_key, model)

    async def run_async():
        return await generator.generate_embedding(text)

    return asyncio.run(run_async())