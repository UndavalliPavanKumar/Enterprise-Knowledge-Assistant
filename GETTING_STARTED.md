# Getting Started Guide

Quick start guide for the Enterprise Knowledge Assistant RAG system.

## 5-Minute Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL with pgvector (or Docker)
- OpenAI API key

### Step 1: Clone and Setup

```bash
# Clone repository
git clone <repo-url>
cd Enterprise-Knowledge-Assistant

# Copy environment file
cp .env.example .env
```

### Step 2: Configure .env

Edit `.env` and add:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/eka_db
OPENAI_API_KEY=sk-your-openai-key
```

### Step 3: Choose Your Setup

**Option A: Docker Compose (Recommended for first-time users)**

```bash
docker-compose up -d
```

Then access:
- Frontend: http://localhost:8501
- API Docs: http://localhost:8000/docs

**Option B: Local Python Environment**

```bash
# Install dependencies
pip install -r requirements.txt

# Start backend
uvicorn app.main:app --reload

# In another terminal, start frontend
streamlit run ui/streamlit_app.py
```

### Step 4: Upload a PDF

1. Open http://localhost:8501
2. Click "📤 Upload Documents"
3. Select a PDF file
4. Wait for processing to complete

### Step 5: Ask Questions

1. Click "❓ Ask Questions"
2. Enter your question
3. Get instant answers powered by GPT-4

## Detailed Setup Guide

### Installation Methods

#### Method 1: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# Check services
docker-compose ps

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

Services:
- Backend: http://localhost:8000
- Frontend: http://localhost:8501
- Database: PostgreSQL on 5432

#### Method 2: Local Python Environment

**Requirements:**
- Python 3.11+
- PostgreSQL 14+ with pgvector extension
- pip or poetry

**Steps:**

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up PostgreSQL
# Ensure PostgreSQL is running and pgvector is installed:
psql -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 5. Create database
createdb eka_db

# 6. Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 7. In another terminal, start frontend
streamlit run ui/streamlit_app.py
```

#### Method 3: Using Make

```bash
# Install dependencies
make install

# Setup .env
make env

# Start development server
make dev

# In another terminal
make ui

# Run tests
make test
```

## Configuration

### Essential Settings

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/eka_db

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-small

# Application
DEBUG=True
LOG_LEVEL=INFO
```

### Optional Settings

```env
# File upload
MAX_FILE_SIZE=52428800  # 50MB
ALLOWED_EXTENSIONS=pdf

# Vector search
SIMILARITY_THRESHOLD=0.7
EMBEDDING_DIMENSION=1536

# Servers
API_PORT=8000
API_HOST=0.0.0.0
```

## Using the Application

### Web Interface (Streamlit)

1. **Upload Documents**
   - Navigate to "📤 Upload Documents"
   - Select PDF file
   - Monitor processing status

2. **Ask Questions**
   - Go to "❓ Ask Questions"
   - Enter your question
   - View answer and sources
   - Adjust number of sources (top_k)

3. **Manage Documents**
   - View all uploaded documents
   - Check document status
   - Delete documents

### API (FastAPI)

**Upload PDF:**
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@document.pdf"
```

**Ask Question:**
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this about?",
    "top_k": 5
  }'
```

See [API_EXAMPLES.md](API_EXAMPLES.md) for more examples.

## Troubleshooting

### Issue: "Database connection failed"

**Solution:**
```bash
# Check PostgreSQL is running
psql postgresql://user:password@localhost:5432/eka_db

# Ensure pgvector extension is installed
psql -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## Local SQLite Usage

This project can run locally using SQLite for quick development and testing.

### Steps

1. Create a virtual environment and install dependencies:

```powershell
cd C:\Users\rsura\Downloads\Pavankumar\Enterprise-Knowledge-Assistant
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Copy the environment file:

```powershell
copy .env.example .env
```

3. Update `.env` to use SQLite:

```env
DATABASE_URL=sqlite:///./eka_db.sqlite3
SQLALCHEMY_ECHO=False
```

4. Start the backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

5. Open the API at:

- `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

### Notes

- SQLite is for local development and testing only.
- Uploaded documents and embeddings are stored in `eka_db.sqlite3`.
- PostgreSQL + pgvector is still supported in the codebase, but SQLite uses a fallback vector search mode.

## Restoring PostgreSQL + pgvector Support

If you want to use PostgreSQL again, update `.env`:

```env
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/eka_db
```

Then ensure the `vector` extension is installed:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

If the extension is missing or PostgreSQL is not running, the app may fail during startup.

### Recommended Local PostgreSQL Setup

- Use `docker-compose.yml` with `ankane/pgvector:latest`
- Or install PostgreSQL 14+ and add the `vector` extension

### Why PostgreSQL?

- Better performance for larger datasets
- Native `pgvector` similarity search
- Production-grade vector storage

### Issue: "OpenAI API error"

**Solution:**
```bash
# Verify your API key
echo $OPENAI_API_KEY

# Test API connection
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Issue: "PDF upload fails"

**Solution:**
- Check file is valid PDF
- Ensure file size < 50MB
- Verify PDF contains extractable text

### Issue: "Port already in use"

**Solution:**
```bash
# Change port in .env
API_PORT=8001

# Or kill the process using the port
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# On macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_services.py::TestPDFService

# Run unit tests only
pytest -m unit
```

## Development Workflow

### Code Quality

```bash
# Format code
make format

# Run linters
make lint

# Type checking
mypy app
```

### Database

```bash
# Initialize database
make db-init

# Run migrations (if Alembic is set up)
make db-migrate
```

## Performance Tips

1. **Use appropriate chunk size** (500 chars works well)
2. **Batch uploads** for multiple documents
3. **Adjust top_k** based on needs (5-10 is usually sufficient)
4. **Monitor logs** for optimization opportunities

## Next Steps

After successful setup:

1. ✅ Upload your first PDF
2. ✅ Ask a question about it
3. ✅ Check API documentation at /docs
4. ✅ Explore the admin dashboard
5. ✅ Read full [README.md](README.md)
6. ✅ Check [API_EXAMPLES.md](API_EXAMPLES.md)

## Getting Help

- **API Issues**: Check http://localhost:8000/docs
- **Database Issues**: Review database logs
- **LLM Issues**: Verify OpenAI API key and quota
- **Performance Issues**: Check application logs

## Production Deployment

### Using Kubernetes

```bash
# Create namespace
kubectl create namespace eka

# Deploy
kubectl apply -f k8s/

# Check status
kubectl get pods -n eka
```

### Using Docker

```bash
# Build image
docker build -f docker/Dockerfile -t eka:latest .

# Run container
docker run -p 8000:8000 --env-file .env eka:latest
```

## Common Commands

```bash
# Start development
make dev

# Start UI
make ui

# Run tests
make test

# Clean cache
make clean

# Docker up/down
make docker-up
make docker-down

# View full command list
make help
```

## Support

For issues and questions:
1. Check [README.md](README.md)
2. Review [API_EXAMPLES.md](API_EXAMPLES.md)
3. Check logs: `docker-compose logs -f`
4. Open a GitHub issue

---

**Happy coding! 🚀**
