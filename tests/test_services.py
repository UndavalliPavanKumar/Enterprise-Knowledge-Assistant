"""Unit tests for application services"""
import pytest
from unittest.mock import Mock, patch
from app.services.pdf_service import PDFService
from app.utils.text_processor import TextProcessor


class TestPDFService:
    """Test PDF service"""

    def test_validate_pdf_with_valid_pdf(self):
        """Test PDF validation with valid PDF"""
        # This would require a real PDF for testing
        pass

    def test_validate_pdf_with_invalid_pdf(self):
        """Test PDF validation with invalid PDF"""
        invalid_bytes = b"Not a PDF"
        assert not PDFService.validate_pdf(invalid_bytes)


class TestTextProcessor:
    """Test text processor"""

    def test_split_text(self):
        """Test text splitting"""
        processor = TextProcessor(chunk_size=50, chunk_overlap=10)

        text = "This is a test text. " * 20
        chunks = processor.split_text(text)

        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)

    def test_split_empty_text(self):
        """Test splitting empty text"""
        processor = TextProcessor()
        chunks = processor.split_text("")

        assert chunks == []

    def test_clean_text(self):
        """Test text cleaning"""
        processor = TextProcessor()

        text = "  Multiple   spaces   and \n newlines  "
        cleaned = processor.clean_text(text)

        assert cleaned == "Multiple spaces and newlines"
        assert not cleaned.startswith(" ")
        assert not cleaned.endswith(" ")


class TestEmbeddingService:
    """Test embedding service"""

    @patch("app.services.embedding_service.OpenAIEmbeddings")
    def test_embedding_initialization(self, mock_embeddings):
        """Test embedding service initialization"""
        from app.services.embedding_service import EmbeddingService

        with patch("app.config.get_settings") as mock_settings:
            mock_settings.return_value.embedding_model = "text-embedding-3-small"
            mock_settings.return_value.openai_api_key = "test-key"

            service = EmbeddingService()
            assert service.embeddings is not None
