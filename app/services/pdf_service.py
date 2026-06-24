"""PDF processing service"""
import PyPDF2
import logging
from io import BytesIO
from typing import Optional

logger = logging.getLogger(__name__)


class PDFService:
    """Service for processing PDF files"""

    @staticmethod
    def extract_text(file_bytes: bytes, filename: str = "unknown") -> Optional[str]:
        """
        Extract text from PDF file

        Args:
            file_bytes: PDF file content as bytes
            filename: Name of the PDF file

        Returns:
            Extracted text or None if extraction failed
        """
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
            text = ""

            # Extract text from all pages
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num}: {e}")
                    continue

            if not text.strip():
                logger.error(f"No text extracted from PDF: {filename}")
                return None

            logger.info(f"Successfully extracted text from {filename} ({len(text)} chars)")
            return text

        except PyPDF2.errors.PdfReadError as e:
            logger.error(f"PDF read error for {filename}: {e}")
            raise ValueError(f"Corrupted or invalid PDF file: {filename}") from e
        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {e}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}") from e

    @staticmethod
    def validate_pdf(file_bytes: bytes) -> bool:
        """
        Validate if file is a valid PDF

        Args:
            file_bytes: File content as bytes

        Returns:
            True if valid PDF, False otherwise
        """
        try:
            PyPDF2.PdfReader(BytesIO(file_bytes))
            return True
        except Exception as e:
            logger.warning(f"PDF validation failed: {e}")
            return False

    @staticmethod
    def get_pdf_metadata(file_bytes: bytes) -> dict:
        """
        Extract metadata from PDF

        Args:
            file_bytes: PDF file content as bytes

        Returns:
            Dictionary containing PDF metadata
        """
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
            metadata = {
                "pages": len(pdf_reader.pages),
                "metadata": pdf_reader.metadata,
            }
            return metadata
        except Exception as e:
            logger.warning(f"Error extracting PDF metadata: {e}")
            return {"pages": 0, "metadata": None}
