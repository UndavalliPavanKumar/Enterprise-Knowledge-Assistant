"""FastAPI routes for the application"""
import logging
import time
import os
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.schemas import (
    UploadResponse,
    AskRequest,
    AskResponse,
    SourceReference,
    DocumentListResponse,
    DocumentInfo,
    HealthResponse,
    ErrorResponse,
)
from app.database.connection import get_db
from app.services.pdf_service import PDFService
from app.services.embedding_service import EmbeddingService
from app.services.search_service import SearchService
from app.services.storage_service import StorageService
from app.services.gpt_service import GPTService
from app.utils.text_processor import TextProcessor
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["api"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        settings = get_settings()
        return {
            "status": "healthy",
            "version": settings.app_version,
            "database": "connected",
            "openai": "configured",
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Service unavailable")


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload and process a PDF file

    Args:
        file: PDF file to upload
        db: Database session

    Returns:
        Upload response with document ID
    """
    start_time = time.time()

    try:
        settings = get_settings()

        # Validate file
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400, detail="File must be a PDF document"
            )

        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400, detail="File must have .pdf extension"
            )

        # Read file content
        file_bytes = await file.read()

        if len(file_bytes) > settings.max_file_size:
            raise HTTPException(
                status_code=413, detail="File size exceeds maximum limit"
            )

        # Validate PDF
        if not PDFService.validate_pdf(file_bytes):
            raise HTTPException(
                status_code=400, detail="Invalid or corrupted PDF file"
            )

        # Save document metadata
        storage_service = StorageService(db)
        document_id = storage_service.save_document(
            filename=file.filename,
            original_filename=file.filename,
            file_size=len(file_bytes),
            status="processing",
        )

        # Extract text from PDF
        text = PDFService.extract_text(file_bytes, file.filename)
        if not text:
            storage_service.update_document_status(
                document_id, "failed", "No text could be extracted from PDF"
            )
            raise HTTPException(
                status_code=422, detail="Could not extract text from PDF"
            )

        # Clean and split text
        text_processor = TextProcessor()
        cleaned_text = text_processor.clean_text(text)
        chunks = text_processor.split_text(cleaned_text)

        if not chunks:
            storage_service.update_document_status(
                document_id, "failed", "No text chunks created from PDF"
            )
            raise HTTPException(
                status_code=422, detail="Could not create text chunks from PDF"
            )

        # Generate embeddings
        embedding_service = EmbeddingService()
        embeddings = embedding_service.generate_embeddings_batch(chunks)

        # Save chunks with embeddings
        storage_service.save_chunks(document_id, chunks, embeddings)

        # Update document status
        storage_service.update_document_status(document_id, "completed")

        elapsed_time = time.time() - start_time
        logger.info(
            f"Successfully processed document {document_id} in {elapsed_time:.2f}s"
        )

        return UploadResponse(
            document_id=document_id,
            filename=file.filename,
            message=f"Successfully processed {len(chunks)} chunks from PDF",
            status="completed",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.post("/ask", response_model=AskResponse)
async def ask_question(
    request: AskRequest,
    db: Session = Depends(get_db),
):
    """
    Ask a question and get an answer based on documents

    Args:
        request: Question request
        db: Database session

    Returns:
        Answer with source references
    """
    start_time = time.time()

    try:
        # Perform semantic search
        search_service = SearchService(db)
        search_results = search_service.semantic_search(
            request.question, top_k=request.top_k
        )

        if not search_results:
            return AskResponse(
                answer="I could not find relevant information to answer your question. Please try uploading more documents or rephrase your question.",
                sources=[],
                query_time_ms=(time.time() - start_time) * 1000,
            )

        # Build context from search results
        context = "\n\n".join([result["text"] for result in search_results])

        # Generate answer using GPT
        gpt_service = GPTService()
        answer = gpt_service.generate_answer(request.question, context)

        # Prepare source references if requested
        sources = []
        if request.include_sources:
            for result in search_results:
                sources.append(
                    SourceReference(
                        chunk_id=result["chunk_id"],
                        document_id=result["document_id"],
                        similarity_score=result["similarity"],
                        text_preview=result["text"][:200] + "...",
                    )
                )

        elapsed_time = time.time() - start_time
        logger.info(f"Answered question in {elapsed_time:.2f}s using {len(search_results)} sources")

        return AskResponse(
            answer=answer,
            sources=sources,
            query_time_ms=elapsed_time * 1000,
        )

    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    List all uploaded documents

    Args:
        limit: Maximum number of documents
        offset: Offset for pagination
        db: Database session

    Returns:
        List of documents
    """
    try:
        storage_service = StorageService(db)
        documents = storage_service.list_documents(limit, offset)

        return DocumentListResponse(
            documents=[
                DocumentInfo.model_validate(doc) for doc in documents
            ],
            total=len(documents),
            offset=offset,
            limit=limit,
        )

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving documents")


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a document and its chunks

    Args:
        document_id: ID of document to delete
        db: Database session

    Returns:
        Success message
    """
    try:
        storage_service = StorageService(db)
        storage_service.delete_document_and_chunks(document_id)

        return {"message": f"Document {document_id} deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail="Error deleting document")
