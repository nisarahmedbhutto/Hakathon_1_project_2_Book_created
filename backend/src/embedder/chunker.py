"""
Content chunking module for breaking down text content into appropriate sizes for embedding
in the website content ingestion system.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ChunkConfig:
    """Configuration for content chunking."""
    max_chunk_size: int = 1000  # Maximum characters per chunk
    overlap: int = 100  # Overlap between chunks in characters
    min_chunk_size: int = 50  # Minimum characters for a valid chunk
    split_on_sentences: bool = True  # Whether to try to split on sentence boundaries


class ContentChunker:
    """
    Content chunking utility for breaking down content into appropriate sizes for embedding.
    """

    def __init__(self, config: Optional[ChunkConfig] = None):
        """
        Initialize the content chunker with configuration.

        Args:
            config: Chunking configuration (uses defaults if None)
        """
        self.config = config or ChunkConfig()

    def chunk_content(self, content: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Split content into chunks of appropriate size for embedding.

        Args:
            content: The content string to chunk
            metadata: Optional metadata to include with each chunk

        Returns:
            List of chunk dictionaries containing the content and metadata
        """
        if not content or len(content.strip()) < self.config.min_chunk_size:
            return []

        # First, clean up the content
        content = self._clean_content(content)

        # Choose the appropriate chunking method
        if self.config.split_on_sentences:
            chunks = self._chunk_by_sentences(content)
        else:
            chunks = self._chunk_by_size(content)

        # Format the chunks with metadata
        formatted_chunks = []
        for i, chunk_text in enumerate(chunks):
            if len(chunk_text.strip()) >= self.config.min_chunk_size:
                chunk_data = {
                    'id': f"chunk_{i}_{hash(chunk_text) % 10000}",
                    'content': chunk_text,
                    'chunk_index': i,
                    'word_count': len(chunk_text.split()),
                    'char_count': len(chunk_text),
                    'metadata': metadata or {},
                    'source_hash': hash(content) % 1000000  # To track original source
                }
                formatted_chunks.append(chunk_data)

        return formatted_chunks

    def _clean_content(self, content: str) -> str:
        """
        Clean the content before chunking.

        Args:
            content: Raw content string

        Returns:
            Cleaned content string
        """
        # Remove extra whitespace and normalize line breaks
        content = re.sub(r'\n+', '\n', content)  # Replace multiple newlines with single
        content = re.sub(r'[ \t]+', ' ', content)  # Replace multiple spaces/tabs with single space
        content = re.sub(r' +\n', '\n', content)  # Remove trailing spaces before newlines
        content = content.strip()  # Remove leading/trailing whitespace

        return content

    def _chunk_by_sentences(self, content: str) -> List[str]:
        """
        Chunk content by trying to break at sentence boundaries.

        Args:
            content: Content to chunk

        Returns:
            List of content chunks
        """
        # Split content into sentences while preserving sentence endings
        sentence_pattern = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_pattern, content)

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            # Check if adding this sentence would exceed the max size
            if len(current_chunk) + len(sentence) <= self.config.max_chunk_size:
                current_chunk += sentence + " "
            else:
                # If the current chunk is not empty, save it
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())

                # Start a new chunk
                # If the sentence is longer than max_chunk_size, split it by size
                if len(sentence) > self.config.max_chunk_size:
                    sub_chunks = self._chunk_by_size(sentence)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = sentence + " "

        # Add the last chunk if it has content
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        # Apply overlap between chunks if needed
        if self.config.overlap > 0 and len(chunks) > 1:
            chunks = self._apply_overlap(chunks)

        return chunks

    def _chunk_by_size(self, content: str) -> List[str]:
        """
        Chunk content by fixed size.

        Args:
            content: Content to chunk

        Returns:
            List of content chunks
        """
        if len(content) <= self.config.max_chunk_size:
            return [content]

        chunks = []
        start = 0

        while start < len(content):
            end = start + self.config.max_chunk_size

            # If this is the last chunk, include the remainder
            if end >= len(content):
                chunks.append(content[start:])
                break

            # Find a good break point (try to break at sentence or word boundary)
            chunk = content[start:end]

            # Look for a good break point near the end
            break_points = ['.', '!', '?', ';', ',', ' ', '\n']
            found_break = False

            # Sort break points by preference (sentence endings first)
            for bp in break_points:
                last_break = chunk.rfind(bp)
                if last_break != -1 and last_break > len(chunk) * 0.7:  # At least 70% through the chunk
                    end = start + last_break + 1
                    found_break = True
                    break

            if not found_break:
                end = start + self.config.max_chunk_size

            chunks.append(content[start:end])
            start = end - self.config.overlap if self.config.overlap > 0 else end

        return chunks

    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        """
        Apply overlap between chunks to maintain context.

        Args:
            chunks: List of chunks without overlap

        Returns:
            List of chunks with overlap applied
        """
        if len(chunks) <= 1 or self.config.overlap <= 0:
            return chunks

        overlapped_chunks = []

        for i, chunk in enumerate(chunks):
            if i == 0:
                # First chunk remains as is
                overlapped_chunks.append(chunk)
            else:
                # Add overlap from previous chunk
                prev_chunk = chunks[i-1]
                overlap_text = prev_chunk[-self.config.overlap:]
                overlapped_chunk = overlap_text + chunk
                overlapped_chunks.append(overlapped_chunk)

        return overlapped_chunks


def chunk_content_with_metadata(content: str, metadata: Dict[str, Any] = None,
                              config: Optional[ChunkConfig] = None) -> List[Dict[str, Any]]:
    """
    Convenience function to chunk content with metadata.

    Args:
        content: Content to chunk
        metadata: Metadata to include with chunks
        config: Chunking configuration

    Returns:
        List of chunked content with metadata
    """
    chunker = ContentChunker(config)
    return chunker.chunk_content(content, metadata)


def create_default_chunker() -> ContentChunker:
    """
    Create a content chunker with default configuration.

    Returns:
        ContentChunker instance with default settings
    """
    return ContentChunker()