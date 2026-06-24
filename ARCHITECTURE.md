# Architecture Documentation

Comprehensive architecture overview of Enterprise Knowledge Assistant.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  ┌──────────────────┐              ┌──────────────────────┐     │
│  │  Streamlit UI    │              │  REST API Clients    │     │
│  │  (Web Browser)   │              │  (JavaScript, etc)   │     │
│  └──────────────────┘              └──────────────────────┘     │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                 HTTP/WebSocket
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                    API Layer (FastAPI)                           │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Routes                                                 │    │
│  │  - POST /upload (PDF upload)                           │    │
│  │  - POST /ask (Question answering)                      │    │
│  │  - GET /documents (List documents)                     │    │
│  │  - DELETE /documents/{id} (Delete document)            │    │
│  │  - GET /health (Health check)                          │    │
│  └────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────┬──────────────────────────┐    │
│  │  Middleware & Auth          │  Error Handling          │    │
│  │  - CORS                     │  - Input Validation      │    │
│  │  - Logging                  │  - Exception Handling    │    │
│  │  - Request Tracking         │  - Rate Limiting         │    │
│  └─────────────────────────────┴──────────────────────────┘    │
└──────────────────────┬──────────────────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
┌──────────────────┐  ┌────────────────────┐  ┌─────────────────────┐
│  Service Layer   │  │  External Services │  │  Data Layer         │
├──────────────────┤  ├────────────────────┤  ├─────────────────────┤
│ PDFService       │  │ OpenAI API         │  │ StorageService      │
│ EmbeddingService │  │ (Embeddings)       │  │ SearchService       │
│ SearchService    │  │ (GPT-4)            │  │                     │
│ GPTService       │  │                    │  │                     │
│ StorageService   │  │                    │  │                     │
└──────────────────┘  └────────────────────┘  └─────────────────────┘
          │
          │
┌─────────▼──────────────────────────────────────────────────────┐
│                      Database Layer                             │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  PostgreSQL + pgvector                               │     │
│  │  ┌──────────────────┐  ┌───────────────────────┐    │     │
│  │  │  Tables          │  │  Vector Indexes       │    │     │
│  │  │  - documents     │  │  - IVFFLAT on        │    │     │
│  │  │  - chunks        │  │    document_chunks   │    │     │
│  │  │  - queries       │  │                       │    │     │
│  │  │  - history       │  │                       │    │     │
│  │  └──────────────────┘  └───────────────────────┘    │     │
│  └──────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Document Upload Flow

```
User uploads PDF
    ↓
[FastAPI] /upload endpoint
    ↓
[PDFService] Extract text from PDF
    ↓
[TextProcessor] Split into chunks
    ↓
[EmbeddingService] Generate embeddings via OpenAI
    ↓
[StorageService] Save to PostgreSQL
    │
    ├── documents table (metadata)
    └── document_chunks table (text + vectors)
    ↓
Return document_id to user
```

### 2. Question Answering Flow

```
User asks question
    ↓
[FastAPI] /ask endpoint
    ↓
[EmbeddingService] Generate embedding for question
    ↓
[SearchService] Semantic similarity search in pgvector
    ↓
Retrieve top-k relevant chunks
    ↓
[GPTService] Send context + question to GPT-4
    ↓
Generate answer
    ↓
Return answer + sources to user
```

## Component Details

### API Layer (FastAPI)

**Responsibilities:**
- HTTP request/response handling
- Input validation (Pydantic schemas)
- Route management
- Error handling and logging

**Key Files:**
- `app/api/routes.py` - API endpoints
- `app/api/schemas.py` - Pydantic models
- `app/main.py` - Application factory

### Service Layer

#### PDFService
- Extract text from PDF files using PyPDF2
- Validate PDF integrity
- Extract metadata
- Error handling for corrupted files

```python
Functions:
- extract_text(file_bytes) -> str
- validate_pdf(file_bytes) -> bool
- get_pdf_metadata(file_bytes) -> dict
```

#### TextProcessor
- Split text into chunks using LangChain
- Clean and normalize text
- Manage chunk size and overlap

```python
Functions:
- split_text(text) -> List[str]
- clean_text(text) -> str
```

#### EmbeddingService
- Generate embeddings using OpenAI API
- Handle batch embedding generation
- Cache embeddings efficiently

```python
Functions:
- generate_embedding(text) -> List[float]
- generate_embeddings_batch(texts) -> List[List[float]]
- get_embedding_dimension() -> int
```

#### SearchService
- Perform vector similarity search using pgvector
- Calculate cosine distance
- Filter by similarity threshold
- Retrieve document context

```python
Functions:
- semantic_search(query, top_k) -> List[dict]
- get_document_context(document_id) -> str
```

#### GPTService
- Generate answers using GPT-4
- Stream responses for real-time UI
- Manage system and user prompts
- Generate text summaries

```python
Functions:
- generate_answer(question, context) -> str
- generate_summary(text) -> str
- stream_answer(question, context) -> Iterator[str]
```

#### StorageService
- CRUD operations for documents
- Manage document chunks
- Update document status
- List and delete documents

```python
Functions:
- save_document(filename, file_size) -> int
- save_chunks(document_id, chunks, embeddings) -> int
- get_document(document_id) -> Document
- update_document_status(document_id, status)
- delete_document_and_chunks(document_id)
```

### Database Layer

#### Database Models

**Document**
```
id: Primary Key
filename: str
original_filename: str
file_size: int
upload_date: DateTime
status: enum (processing/completed/failed)
error_message: Optional[str]
```

**DocumentChunk**
```
id: Primary Key
document_id: Foreign Key
chunk_index: int
chunk_text: Text
embedding: Vector(1536)  # pgvector
created_at: DateTime
```

**SearchQuery**
```
id: Primary Key
query_text: Text
results_count: int
response_time_ms: float
created_at: DateTime
```

**ConversationHistory**
```
id: Primary Key
session_id: str
user_question: Text
assistant_answer: Text
context_used: Text
created_at: DateTime
```

#### Vector Indexing

```sql
CREATE INDEX ix_document_chunks_embedding 
ON document_chunks 
USING ivfflat (embedding)
WITH (lists = 100);
```

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn
- **Database**: PostgreSQL with pgvector
- **ORM**: SQLAlchemy 2.0

### Document Processing
- **PDF Extraction**: PyPDF2
- **Text Chunking**: LangChain
- **Embeddings**: OpenAI API
- **LLM**: GPT-4

### Frontend
- **UI Framework**: Streamlit
- **Styling**: Custom CSS

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Kubernetes (optional)
- **Version Control**: Git

## Configuration Management

### Environment Variables
```
Config loaded from: app/config.py
Source: .env file

Settings scopes:
- Database settings
- OpenAI settings
- Application settings
- Upload settings
- Vector search settings
- API settings
```

### Settings Caching
```python
@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

## Error Handling Strategy

### HTTP Status Codes
- 200: Success
- 400: Invalid input
- 413: File too large
- 422: Processing error
- 500: Server error

### Error Response Format
```json
{
  "error": "User-friendly error message",
  "detail": "Technical details",
  "code": "ERROR_CODE"
}
```

### Logging
- All errors logged with context
- Sensitive data not logged
- Log levels: DEBUG, INFO, WARNING, ERROR

## Performance Considerations

### Database Performance
- IVFFLAT indexing for vector search
- Connection pooling
- Query optimization
- Regular VACUUM/ANALYZE

### API Performance
- Async/await for non-blocking operations
- Batch processing for embeddings
- Response caching where applicable
- Rate limiting

### Embedding Performance
- Batch API calls to OpenAI
- Cache embeddings
- Parallel processing

## Security Architecture

### Input Validation
- Pydantic schema validation
- File type checking
- Size limit enforcement

### Secret Management
- Environment variables for sensitive data
- No hardcoded secrets
- Secure credential storage

### Database Security
- SQL injection prevention (ORM)
- Connection pooling
- Access control

### API Security
- CORS configuration
- Rate limiting
- Request logging

## Scalability Design

### Horizontal Scaling
- Stateless API design
- Load balancing ready
- Kubernetes deployments

### Database Scaling
- Connection pooling
- Read replicas support
- Partitioning ready

### Caching Strategy
- Settings caching
- Query result caching (optional)
- Embedding caching

## Monitoring and Observability

### Logging
- Structured logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Log aggregation ready

### Health Checks
- `/api/v1/health` endpoint
- Database connectivity check
- OpenAI service check

### Metrics
- Request count and latency
- Database query performance
- API error rates
- Vector search performance

## Deployment Patterns

### Local Development
- Python virtual environment
- Docker Compose for services
- Hot-reload enabled

### Docker Deployment
- Single container deployment
- Multi-container with Docker Compose
- Volume mounting for persistence

### Kubernetes Deployment
- StatefulSet for database
- Deployment for backend/frontend
- Service and Ingress
- ConfigMap for configuration
- Secrets for sensitive data

## API Versioning

Current version: v1
- Location: `/api/v1/`
- Future versions: `/api/v2/` (backward compatibility maintained)

## Future Architecture Enhancements

- [ ] Caching layer (Redis)
- [ ] Message queue (RabbitMQ/Kafka)
- [ ] Search service improvements
- [ ] Multi-LLM support
- [ ] Advanced analytics
- [ ] Real-time collaboration
- [ ] Fine-tuned models

---

**Architecture Version**: 1.0  
**Last Updated**: 2024  
**Status**: Production Ready ✅
