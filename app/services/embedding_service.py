"""Embedding generation service"""
import logging
from typing import List
from langchain_openai import OpenAIEmbeddings
from app.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings"""

    def __init__(self):
        """Initialize embedding service"""
        self.settings = get_settings()
        try:
            self.embeddings = OpenAIEmbeddings(
                model=self.settings.embedding_model,
                api_key=self.settings.openai_api_key,
            )
            logger.info(f"Embedding service initialized with model: {self.settings.embedding_model}")
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}")
            raise

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Text to generate embedding for

        Returns:
            Embedding vector as list of floats
        """
        try:
            if not text or not text.strip():
                logger.warning("Empty text provided for embedding")
                return []

            embedding = self.embeddings.embed_query(text)
            logger.debug(f"Generated embedding for text of length {len(text)}")
            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            List of embedding vectors
        """
        try:
            if not texts:
                logger.warning("Empty list provided for batch embedding generation")
                return []

            embeddings = self.embeddings.embed_documents(texts)
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

    def get_embedding_dimension(self) -> int:
        """Get dimension of embeddings"""
        return self.settings.embedding_dimension
