# Local Setup & Execution Guide

Complete step-by-step guide with comments to run the Enterprise Knowledge Assistant locally.

---

## **Step 1: Navigate to Project Directory**

```powershell
# Change to your project directory
cd C:\Users\rsura\Downloads\Pavankumar\Enterprise-Knowledge-Assistant

# Verify you're in the right location (should show project files)
dir
```

---

## **Step 2: Activate Virtual Environment**

```powershell
# Activate the Python virtual environment
# This isolates project dependencies from system Python
.\.venv\Scripts\Activate.ps1

# You should see (.venv) in your prompt like:
# (.venv) PS C:\Users\rsura\Downloads\Pavankumar\Enterprise-Knowledge-Assistant>
```

---

## **Step 3: Verify Environment Setup**

```powershell
# Check that Python is using the virtual environment
# This should show a path inside .venv
python --version

# List installed packages to verify dependencies
pip list | Select-String "fastapi|streamlit|sqlalchemy"
```

---

## **Step 4A: Start Backend Server (Port 8001)**

```powershell
# Start the FastAPI backend server
# --host 0.0.0.0: Listen on all network interfaces
# --port 8001: Run on port 8001 (8000 may be in use)
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# Expected output:
# INFO:     Started server process [PID]
# INFO:     Waiting for application startup.
# 2026-06-24 13:38:31,998 - app.database.connection - INFO - Database engine created successfully
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8001
```

**Note:** Do NOT close this terminal. The backend must stay running.

---

## **Step 4B: Open a New Terminal for Streamlit**

```powershell
# Open a new PowerShell terminal (Ctrl+Shift+`) and navigate to project
cd C:\Users\rsura\Downloads\Pavankumar\Enterprise-Knowledge-Assistant

# Activate virtual environment in the new terminal
.\.venv\Scripts\Activate.ps1
```

---

## **Step 5: Start Streamlit Frontend (Port 8501)**

```powershell
# Start the Streamlit UI on port 8501
# Streamlit runs a local web app for document upload & question answering
.\.venv\Scripts\python.exe -m streamlit run ui/streamlit_app.py --server.port 8501

# Expected output:
# Collecting usage statistics. To deactivate, set browser.gatherUsageStats to false.
#   You can now view your Streamlit app in your browser.
#   Local URL: http://localhost:8501
```

---

## **Step 6: Open Application in Browser**

### Backend API Documentation:
- **URL:** `http://localhost:8001/docs`
- **Description:** Interactive Swagger UI to test API endpoints

### Frontend UI:
- **URL:** `http://localhost:8501`
- **Pages:**
  - 📤 **Upload Documents** - Upload PDF files for processing
  - ❓ **Ask Questions** - Query your documents
  - 📚 **Manage Documents** - View and delete uploaded files

---

## **Step 7: Health Check (Verify Backend is Running)**

Open a third terminal and run:

```powershell
# Test if backend is healthy
# This sends a GET request to the health endpoint
.\.venv\Scripts\python.exe -c "
import requests
try:
    response = requests.get('http://localhost:8001/api/v1/health', timeout=5)
    print('Status Code:', response.status_code)
    print('Response:', response.json())
except Exception as e:
    print('ERROR:', str(e))
"

# Expected output:
# Status Code: 200
# Response: {'status': 'healthy', 'version': '1.0.0', 'database': 'connected', 'openai': 'configured'}
```

---

## **Step 8: Upload a PDF Document**

### Option A: Using Streamlit UI (Recommended)

1. Open http://localhost:8501 in browser
2. Click **"📤 Upload Documents"** in the sidebar
3. Select a PDF file from your computer
4. Click **Upload** and wait for processing to complete

### Option B: Using cURL (Command Line)

```powershell
# Upload a PDF file via API
# Replace "path/to/file.pdf" with your actual PDF file path
curl -X POST http://localhost:8001/api/v1/upload `
  -F "file=@path/to/file.pdf"

# Expected response:
# {"document_id":"...","filename":"file.pdf","status":"processing"}
```

### Option C: Using Python (Advanced)

```powershell
# Create a Python script to upload a document
.\.venv\Scripts\python.exe << 'EOF'
import requests

# Path to your PDF file
pdf_path = "path/to/your/document.pdf"

# Prepare file for upload
with open(pdf_path, 'rb') as f:
    files = {'file': f}
    # Send POST request to upload endpoint
    response = requests.post(
        'http://localhost:8001/api/v1/upload',
        files=files
    )

# Print response
print("Status:", response.status_code)
print("Response:", response.json())
EOF
```

---

## **Step 9: Ask Questions About Your Document**

### Option A: Using Streamlit UI

1. Click **"❓ Ask Questions"** in the sidebar
2. Type your question (e.g., "What is this document about?")
3. Adjust **"Number of sources (top_k)"** slider if needed
4. Click **Submit** and view the answer

### Option B: Using cURL

```powershell
# Send a question to the backend
# The API will search relevant document chunks and generate an answer
curl -X POST http://localhost:8001/api/v1/ask `
  -H "Content-Type: application/json" `
  -d '{
    "question": "What is the main topic?",
    "top_k": 5
  }'

# Expected response:
# {
#   "answer": "The main topic is...",
#   "sources": [...]
# }
```

### Option C: Using Python

```powershell
.\.venv\Scripts\python.exe << 'EOF'
import requests

# Define the question
question = "What are the key points in this document?"

# Send POST request to ask endpoint
response = requests.post(
    'http://localhost:8001/api/v1/ask',
    json={
        'question': question,
        'top_k': 5  # Number of similar chunks to retrieve
    }
)

# Print the answer
print("Answer:", response.json()['answer'])
print("\nSources:", response.json()['sources'])
EOF
```

---

## **Step 10: View Available Documents**

```powershell
# Get list of all uploaded documents
curl -X GET http://localhost:8001/api/v1/documents

# Or with Python:
.\.venv\Scripts\python.exe << 'EOF'
import requests
response = requests.get('http://localhost:8001/api/v1/documents')
documents = response.json()
for doc in documents:
    print(f"ID: {doc['id']}, Name: {doc['filename']}, Chunks: {doc['chunk_count']}")
EOF
```

---

## **Step 11: Delete a Document**

```powershell
# Delete a document by ID
# Replace "123" with the actual document ID
curl -X DELETE http://localhost:8001/api/v1/documents/123

# Or with Python:
.\.venv\Scripts\python.exe << 'EOF'
import requests
doc_id = "123"  # Replace with actual ID
response = requests.delete(f'http://localhost:8001/api/v1/documents/{doc_id}')
print("Deleted:", response.json())
EOF
```

---

## **Troubleshooting**

### Port Already in Use

```powershell
# Check what process is using port 8001
Get-NetTCPConnection -LocalPort 8001

# If port 8000 or 8501 is also in use:
# Start backend on different port (e.g., 8002):
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### Backend Not Responding

```powershell
# Test connectivity to backend
Test-NetConnection -ComputerName localhost -Port 8001

# Check backend logs in the terminal where you started it
# Look for ERROR messages
```

### Missing Dependencies

```powershell
# Reinstall all dependencies
pip install -r requirements.txt

# Or reinstall specific packages:
pip install fastapi uvicorn streamlit sqlalchemy
```

### Database Issues (SQLite)

```powershell
# The database file is: eka_db.sqlite3
# To reset the database, delete it:
Remove-Item eka_db.sqlite3

# Next server start will recreate it:
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

---

## **Quick Reference: All Commands in One Place**

```powershell
# Terminal 1: Backend
cd C:\Users\rsura\Downloads\Pavankumar\Enterprise-Knowledge-Assistant
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# Terminal 2: Frontend
cd C:\Users\rsura\Downloads\Pavankumar\Enterprise-Knowledge-Assistant
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m streamlit run ui/streamlit_app.py --server.port 8501

# Terminal 3: Test (Optional)
.\.venv\Scripts\python.exe -c "import requests; r=requests.get('http://localhost:8001/api/v1/health'); print(r.status_code, r.json())"
```

---

## **API Endpoints Summary**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/v1/health` | Check if server is running |
| `POST` | `/api/v1/upload` | Upload a PDF document |
| `POST` | `/api/v1/ask` | Ask a question about documents |
| `GET` | `/api/v1/documents` | List all uploaded documents |
| `DELETE` | `/api/v1/documents/{id}` | Delete a document |

---

## **Environment Variables (.env)**

```env
# Database configuration
DATABASE_URL=sqlite:///./eka_db.sqlite3

# OpenAI API (required for embeddings & answers)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-small

# Application
DEBUG=True
LOG_LEVEL=INFO
MAX_FILE_SIZE=52428800  # 50MB
```

---

**That's it!** You now have the Enterprise Knowledge Assistant running locally with full documentation and examples.
