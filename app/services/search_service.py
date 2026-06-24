"""Vector similarity search service"""
import logging
import math
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.models import DocumentChunk
from app.services.embedding_service import EmbeddingService
from app.config import get_settings

logger = logging.getLogger(__name__)


class SearchService:
    """Service for vector similarity search"""

    def __init__(self, db: Session):
        """
        Initialize search service

        Args:
            db: Database session
        """
        self.db = db
        self.embedding_service = EmbeddingService()
        self.settings = get_settings()

    def semantic_search(
        self, query: str, top_k: int = 5, threshold: Optional[float] = None
    ) -> List[dict]:
        """
        Perform semantic similarity search on documents

        Args:
            query: Query text
            top_k: Number of top results to return
            threshold: Minimum similarity score threshold (0-1)

        Returns:
            List of matching documents with similarity scores
        """
        try:
            if threshold is None:
                threshold = self.settings.similarity_threshold

            # Generate embedding for query
            query_embedding = self.embedding_service.generate_embedding(query)

            if not query_embedding:
                logger.warning("Failed to generate embedding for query")
                return []

            if self.db.bind.dialect.name == "postgresql":
                # Perform similarity search using pgvector
                results = (
                    self.db.query(
                        DocumentChunk.id,
                        DocumentChunk.document_id,
                        DocumentChunk.chunk_text,
                        DocumentChunk.chunk_index,
                        (1 - func.cosine_distance(DocumentChunk.embedding, query_embedding)).label("similarity"),
                    )
                    .order_by(func.cosine_distance(DocumentChunk.embedding, query_embedding))
                    .limit(top_k)
                    .all()
                )

                # Filter by threshold and format results
                search_results = []
                for result in results:
                    similarity = float(result.similarity)
                    if similarity >= threshold:
                        search_results.append(
                            {
                                "chunk_id": result.id,
                                "document_id": result.document_id,
                                "text": result.chunk_text,
                                "chunk_index": result.chunk_index,
                                "similarity": similarity,
                            }
                        )
            else:
                # Fallback similarity search for SQLite or other databases
                all_chunks = (
                    self.db.query(
                        DocumentChunk.id,
                        DocumentChunk.document_id,
                        DocumentChunk.chunk_text,
                        DocumentChunk.chunk_index,
                        DocumentChunk.embedding,
                    )
                    .all()
                )

                def cosine_similarity(a: list[float], b: list[float]) -> float:
                    if not a or not b or len(a) != len(b):
                        return 0.0
                    dot = sum(x * y for x, y in zip(a, b))
                    norm_a = math.sqrt(sum(x * x for x in a))
                    norm_b = math.sqrt(sum(y * y for y in b))
                    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0

                scored = []
                for chunk in all_chunks:
                    embedding_value = chunk.embedding
                    if embedding_value is None:
                        continue
                    similarity = cosine_similarity(embedding_value, query_embedding)
                    if similarity >= threshold:
                        scored.append(
                            {
                                "chunk_id": chunk.id,
                                "document_id": chunk.document_id,
                                "text": chunk.chunk_text,
                                "chunk_index": chunk.chunk_index,
                                "similarity": similarity,
                            }
                        )
                search_results = sorted(scored, key=lambda item: item["similarity"], reverse=True)[
                    :top_k
                ]

            logger.info(f"Found {len(search_results)} relevant documents for query")
            return search_results

        except Exception as e:
            logger.error(f"Error performing similarity search: {e}")
            raise

    def get_document_context(
        self, document_id: int, max_chunks: int = 10
    ) -> str:
        """
        Get full context from a document

        Args:
            document_id: ID of the document
            max_chunks: Maximum number of chunks to retrieve

        Returns:
            Concatenated context from document chunks
        """
        try:
            chunks = (
                self.db.query(DocumentChunk.chunk_text)
                .filter(DocumentChunk.document_id == document_id)
                .order_by(DocumentChunk.chunk_index)
                .limit(max_chunks)
                .all()
            )

            context = "\n".join([chunk[0] for chunk in chunks])
            logger.info(f"Retrieved context from {len(chunks)} chunks of document {document_id}")
            return context

        except Exception as e:
            logger.error(f"Error retrieving document context: {e}")
            raise
