# Makefile for Enterprise Knowledge Assistant

.PHONY: help install dev prod test lint format clean docker-up docker-down

help:
	@echo "Enterprise Knowledge Assistant - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install      - Install dependencies"
	@echo "  make env          - Setup .env file from example"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Run development server"
	@echo "  make prod         - Run production server"
	@echo "  make ui           - Run Streamlit UI"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters (flake8, mypy)"
	@echo "  make format       - Format code (black, isort)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up    - Start Docker Compose services"
	@echo "  make docker-down  - Stop Docker Compose services"
	@echo "  make docker-logs  - View Docker logs"
	@echo ""
	@echo "Database:"
	@echo "  make db-init      - Initialize database"
	@echo "  make db-migrate   - Run migrations"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        - Remove cache and temporary files"

install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ .env file created. Please edit it with your configuration."; \
	else \
		echo "⚠️  .env already exists"; \
	fi

dev:
	@echo "🚀 Starting development server..."
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

prod:
	@echo "🚀 Starting production server..."
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

ui:
	@echo "🎨 Starting Streamlit UI..."
	streamlit run ui/streamlit_app.py

test:
	@echo "🧪 Running tests..."
	pytest tests/ -v --cov=app --cov-report=html

lint:
	@echo "🔍 Running linters..."
	flake8 app tests --max-line-length=100
	mypy app --ignore-missing-imports

format:
	@echo "🎨 Formatting code..."
	black app tests ui
	isort app tests ui

docker-up:
	@echo "🐳 Starting Docker services..."
	docker-compose up -d

docker-down:
	@echo "🛑 Stopping Docker services..."
	docker-compose down

docker-logs:
	@echo "📋 Docker logs..."
	docker-compose logs -f

db-init:
	@echo "🗄️  Initializing database..."
	python -m app.database.connection

db-migrate:
	@echo "📊 Running migrations..."
	alembic upgrade head

clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist build *.egg-info
	@echo "✅ Cleanup complete"

.DEFAULT_GOAL := help
