# Windows PowerShell startup script for Enterprise Knowledge Assistant

Write-Host "🚀 Starting Enterprise Knowledge Assistant..." -ForegroundColor Green

# Check if .env file exists
if (!(Test-Path ".env")) {
    Write-Host "❌ .env file not found. Please copy .env.example to .env and configure it." -ForegroundColor Red
    exit 1
}

# Load environment variables
Get-Content .env | ForEach-Object {
    $line = $_
    if ($line -and !$line.StartsWith("#")) {
        $key, $value = $line -split "=", 2
        if ($key) {
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

# Check Python version
$pythonVersion = python --version 2>&1 | Select-Object -First 1
Write-Host "✅ $pythonVersion" -ForegroundColor Green

# Create virtual environment if it doesn't exist
if (!(Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt

# Initialize database
Write-Host "🗄️  Initializing database..." -ForegroundColor Yellow

# Start the application
Write-Host "🎉 Starting FastAPI server..." -ForegroundColor Green
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
