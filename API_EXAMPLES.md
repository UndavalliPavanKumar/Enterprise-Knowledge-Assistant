"""
API Usage Examples for Enterprise Knowledge Assistant

This file contains curl commands and code examples for using the API.
"""

# ============================================================================
# 1. HEALTH CHECK
# ============================================================================

# Check if the API is running and healthy
curl -X GET http://localhost:8000/api/v1/health

# Response:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "database": "connected",
#   "openai": "configured"
# }


# ============================================================================
# 2. UPLOAD PDF
# ============================================================================

# Upload a PDF file
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@/path/to/document.pdf"

# Response:
# {
#   "document_id": 1,
#   "filename": "document.pdf",
#   "message": "Successfully processed 15 chunks from PDF",
#   "status": "completed"
# }

# Python example:
# import requests
# with open('document.pdf', 'rb') as f:
#     files = {'file': f}
#     response = requests.post('http://localhost:8000/api/v1/upload', files=files)
#     print(response.json())


# ============================================================================
# 3. ASK QUESTION
# ============================================================================

# Ask a question based on uploaded documents
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic of the document?",
    "top_k": 5,
    "include_sources": true
  }'

# Response:
# {
#   "answer": "The main topic of the document is...",
#   "sources": [
#     {
#       "chunk_id": 1,
#       "document_id": 1,
#       "similarity_score": 0.92,
#       "text_preview": "..."
#     }
#   ],
#   "query_time_ms": 245.5
# }

# Python example:
# import requests
# payload = {
#     "question": "What is the main topic?",
#     "top_k": 5,
#     "include_sources": True
# }
# response = requests.post('http://localhost:8000/api/v1/ask', json=payload)
# print(response.json())


# ============================================================================
# 4. LIST DOCUMENTS
# ============================================================================

# List all uploaded documents
curl -X GET "http://localhost:8000/api/v1/documents?limit=10&offset=0"

# Response:
# {
#   "documents": [
#     {
#       "id": 1,
#       "filename": "document.pdf",
#       "original_filename": "document.pdf",
#       "file_size": 1024000,
#       "upload_date": "2024-01-15T10:30:00",
#       "status": "completed",
#       "error_message": null
#     }
#   ],
#   "total": 1,
#   "offset": 0,
#   "limit": 10
# }

# Python example:
# import requests
# response = requests.get('http://localhost:8000/api/v1/documents?limit=10')
# print(response.json())


# ============================================================================
# 5. DELETE DOCUMENT
# ============================================================================

# Delete a specific document and its chunks
curl -X DELETE http://localhost:8000/api/v1/documents/1

# Response:
# {
#   "message": "Document 1 deleted successfully"
# }

# Python example:
# import requests
# response = requests.delete('http://localhost:8000/api/v1/documents/1')
# print(response.json())


# ============================================================================
# PYTHON CLIENT EXAMPLE
# ============================================================================

"""
import requests
from pathlib import Path

class EKAClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"

    def health_check(self):
        response = requests.get(f"{self.api_url}/health")
        return response.json()

    def upload_document(self, file_path):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{self.api_url}/upload", files=files)
        return response.json()

    def ask_question(self, question, top_k=5, include_sources=True):
        payload = {
            "question": question,
            "top_k": top_k,
            "include_sources": include_sources
        }
        response = requests.post(f"{self.api_url}/ask", json=payload)
        return response.json()

    def list_documents(self, limit=100, offset=0):
        response = requests.get(
            f"{self.api_url}/documents",
            params={"limit": limit, "offset": offset}
        )
        return response.json()

    def delete_document(self, document_id):
        response = requests.delete(f"{self.api_url}/documents/{document_id}")
        return response.json()


# Usage example:
if __name__ == "__main__":
    client = EKAClient()

    # Check health
    health = client.health_check()
    print(f"API Status: {health['status']}")

    # Upload document
    result = client.upload_document("path/to/document.pdf")
    print(f"Document uploaded with ID: {result['document_id']}")

    # Ask question
    answer = client.ask_question("What is the main topic?")
    print(f"Answer: {answer['answer']}")
    print(f"Sources: {len(answer['sources'])} found")

    # List documents
    docs = client.list_documents()
    print(f"Total documents: {docs['total']}")

    # Delete document
    delete_result = client.delete_document(result['document_id'])
    print(f"Deletion: {delete_result['message']}")
"""


# ============================================================================
# JAVASCRIPT/FETCH EXAMPLE
# ============================================================================

/*
const BASE_URL = 'http://localhost:8000/api/v1';

class EKAClient {
  async uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${BASE_URL}/upload`, {
      method: 'POST',
      body: formData
    });
    return response.json();
  }

  async askQuestion(question, topK = 5) {
    const response = await fetch(`${BASE_URL}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: question,
        top_k: topK,
        include_sources: true
      })
    });
    return response.json();
  }

  async listDocuments(limit = 100, offset = 0) {
    const response = await fetch(
      `${BASE_URL}/documents?limit=${limit}&offset=${offset}`
    );
    return response.json();
  }

  async deleteDocument(documentId) {
    const response = await fetch(`${BASE_URL}/documents/${documentId}`, {
      method: 'DELETE'
    });
    return response.json();
  }
}

// Usage:
const client = new EKAClient();
const answer = await client.askQuestion('What is this about?');
console.log(answer.answer);
*/
