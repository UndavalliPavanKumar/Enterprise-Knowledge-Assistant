# Enterprise Knowledge Assistant

A FastAPI-based Retrieval-Augmented Generation (RAG) assistant for document search and question answering.

## Local SQLite Usage

This repository can run locally using SQLite for development or quick testing.

### Steps

1. Create a virtual environment and install dependencies:

```powershell
cd C:\Users\rsura\Downloads\Pavankumar\Enterprise-Knowledge-Assistant
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Configure local environment variables:

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

If port `8000` is already in use, start the app on `8001` instead:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

5. Open the API at:

- `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

### Notes

- SQLite is intended for local development and testing only.
- Uploaded documents and embeddings are stored in `eka_db.sqlite3`.
- `pgvector` support is still part of the codebase, but local SQLite uses a fallback vector storage mode.

## Restoring PostgreSQL + pgvector Support

If you want to use PostgreSQL with `pgvector` again, update the `.env` file:

```env
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/eka_db
```

Then ensure PostgreSQL has the `vector` extension installed:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

If your local PostgreSQL is not running or the extension is missing, the app may fail during startup.

### Recommended local PostgreSQL setup

- Use the provided `docker-compose.yml` with `ankane/pgvector:latest` for an easy local database.
- Or install PostgreSQL 14+ on your machine and add the `vector` extension.

### Why use PostgreSQL?

- Production-ready vector storage
- Better performance for large document collections
- Native `pgvector` similarity search support

## Project Structure

- `app/` - FastAPI backend
- `ui/` - Streamlit interface
- `docker/` - Dockerfile and container config
- `docker-compose.yml` - Local development stack
- `.env.example` - Example environment variables
- `requirements.txt` - Python dependencies

## Quick Start

After starting the backend, use the API endpoints:

- `POST /upload` to upload PDF files
- `POST /ask` to query documents

That’s it—SQLite mode is now documented for local usage, with a clear path back to PostgreSQL when you need it.
