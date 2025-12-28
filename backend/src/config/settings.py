"""
Configuration management for the website content ingestion system.
Handles environment variables and application settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""

    # Cohere Configuration
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")

    # Qdrant Configuration
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "book_content")

    # Docusaurus Book Configuration
    DOCUSAURUS_BASE_URL: str = os.getenv("DOCUSAURUS_BASE_URL", "https://your-docusaurus-site.com")

    # Processing Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "512"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
    REQUEST_DELAY: float = float(os.getenv("REQUEST_DELAY", "1.0"))

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    def __init__(self):
        """Validate required configuration on instantiation."""
        if not self.COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY environment variable is required")

    @property
    def cohere_configured(self) -> bool:
        """Check if Cohere API is properly configured."""
        return bool(self.COHERE_API_KEY)

    @property
    def qdrant_configured(self) -> bool:
        """Check if Qdrant is properly configured."""
        return bool(self.QDRANT_URL)


# Global settings instance
settings = Settings()