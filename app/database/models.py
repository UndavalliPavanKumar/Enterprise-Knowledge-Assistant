"""Database models using SQLAlchemy"""
import os

from sqlalchemy import Column, String, Integer, DateTime, Text, Float, Index, JSON
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector
from datetime import datetime
from app.config import get_settings

Base = declarative_base()


def _is_postgres_database() -> bool:
    settings = get_settings()
    return settings.database_url.startswith("postgresql")


def _embedding_column():
    if _is_postgres_database():
        return Column(Vector(1536), index=True)
    return Column(JSON, nullable=True)


def _embedding_index_args():
    if _is_postgres_database():
        return (Index("ix_document_chunks_embedding", "embedding", postgresql_using="ivfflat"),)
    return ()


class Document(Base):
    """Document model for storing PDF information"""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), index=True)
    original_filename = Column(String(255))
    file_size = Column(Integer)
    upload_date = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String(50), default="uploaded")  # uploaded, processing, completed, failed
    error_message = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Document {self.id}: {self.original_filename}>"


class DocumentChunk(Base):
    """Document chunks with embeddings"""

    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, index=True)
    chunk_index = Column(Integer)
    chunk_text = Column(Text)
    embedding = _embedding_column()  # OpenAI embedding dimension
    created_at = Column(DateTime, default=datetime.utcnow)

    # Create index for vector similarity search
    __table_args__ = _embedding_index_args()

    def __repr__(self):
        return f"<DocumentChunk {self.id}: document_id={self.document_id}>"


class SearchQuery(Base):
    """Track search queries for analytics"""

    __tablename__ = "search_queries"

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text)
    results_count = Column(Integer)
    response_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<SearchQuery {self.id}>"


class ConversationHistory(Base):
    """Store conversation history for context"""

    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    user_question = Column(Text)
    assistant_answer = Column(Text)
    context_used = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<ConversationHistory {self.id}: session_id={self.session_id}>"
