"""Document storage and retrieval service"""
import logging
from typing import List
from sqlalchemy.orm import Session
from app.database.models import Document, DocumentChunk

logger = logging.getLogger(__name__)


class StorageService:
    """Service for storing and retrieving documents and embeddings"""

    def __init__(self, db: Session):
        """
        Initialize storage service

        Args:
            db: Database session
        """
        self.db = db

    def save_document(
        self,
        filename: str,
        original_filename: str,
        file_size: int,
        status: str = "uploaded",
    ) -> int:
        """
        Save document metadata to database

        Args:
            filename: Stored filename
            original_filename: Original filename from upload
            file_size: File size in bytes
            status: Document status

        Returns:
            Document ID
        """
        try:
            document = Document(
                filename=filename,
                original_filename=original_filename,
                file_size=file_size,
                status=status,
            )
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)

            logger.info(f"Saved document with ID: {document.id}")
            return document.id

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving document: {e}")
            raise

    def save_chunks(
        self,
        document_id: int,
        chunks: List[str],
        embeddings: List[List[float]],
    ) -> int:
        """
        Save document chunks with embeddings to database

        Args:
            document_id: ID of the document
            chunks: List of text chunks
            embeddings: List of embeddings corresponding to chunks

        Returns:
            Number of chunks saved
        """
        try:
            if len(chunks) != len(embeddings):
                raise ValueError("Number of chunks and embeddings must match")

            document_chunks = []
            for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                doc_chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=idx,
                    chunk_text=chunk_text,
                    embedding=embedding,
                )
                document_chunks.append(doc_chunk)

            self.db.add_all(document_chunks)
            self.db.commit()

            logger.info(f"Saved {len(chunks)} chunks for document {document_id}")
            return len(chunks)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving chunks: {e}")
            raise

    def get_document(self, document_id: int) -> Document:
        """
        Retrieve document by ID

        Args:
            document_id: Document ID

        Returns:
            Document object
        """
        try:
            document = self.db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise ValueError(f"Document {document_id} not found")
            return document
        except Exception as e:
            logger.error(f"Error retrieving document: {e}")
            raise

    def update_document_status(
        self, document_id: int, status: str, error_message: str = None
    ) -> None:
        """
        Update document processing status

        Args:
            document_id: Document ID
            status: New status
            error_message: Error message if processing failed
        """
        try:
            document = self.db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise ValueError(f"Document {document_id} not found")

            document.status = status
            if error_message:
                document.error_message = error_message

            self.db.commit()
            logger.info(f"Updated document {document_id} status to {status}")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating document status: {e}")
            raise

    def delete_document_and_chunks(self, document_id: int) -> None:
        """
        Delete document and its associated chunks

        Args:
            document_id: Document ID
        """
        try:
            # Delete chunks first
            self.db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document_id
            ).delete()

            # Delete document
            self.db.query(Document).filter(Document.id == document_id).delete()

            self.db.commit()
            logger.info(f"Deleted document {document_id} and its chunks")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting document: {e}")
            raise

    def list_documents(self, limit: int = 100, offset: int = 0) -> List[Document]:
        """
        List all documents

        Args:
            limit: Maximum number of documents to return
            offset: Offset for pagination

        Returns:
            List of Document objects
        """
        try:
            documents = (
                self.db.query(Document)
                .order_by(Document.upload_date.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )
            logger.info(f"Retrieved {len(documents)} documents")
            return documents
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            raise
