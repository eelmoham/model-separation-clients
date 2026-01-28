.PHONY: help install run start stop restart test clean logs backend-logs frontend-logs

help:
	@echo "📋 Available commands:"
	@echo ""
	@echo "  make install        - Install all dependencies"
	@echo "  make run            - Launch backend and frontend"
	@echo "  make start          - Same as 'make run'"
	@echo "  make stop           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make test           - Run separation tests"
	@echo "  make logs           - Show backend logs"
	@echo "  make backend-logs   - Show backend logs in real-time"
	@echo "  make frontend-logs  - Show frontend logs in real-time"
	@echo "  make clean          - Clean logs and cache files"
	@echo ""

install:
	@echo "📦 Installing dependencies..."
	python3 -m venv venv
	./venv/bin/pip install -r req.txt
	@echo "✅ Dependencies installed"

run: stop
	@echo "🚀 Launching project..."
	@./start.sh
	@sleep 3
	@echo ""
	@echo "✅ Services running:"
	@echo "   - Frontend: http://localhost:8501"
	@echo "   - Backend:  http://localhost:8000"
	@echo ""

start: run

stop:
	@echo "🛑 Stopping services..."
	@pkill -f uvicorn 2>/dev/null || true
	@pkill -f streamlit 2>/dev/null || true
	@sleep 1
	@echo "✅ Services stopped"

restart: stop run

test:
	@echo "🧪 Running separation tests..."
	@./venv/bin/python test_separation.py

logs: backend-logs

backend-logs:
	@echo "📋 Backend logs (Ctrl+C to exit):"
	@tail -f backend.log

frontend-logs:
	@echo "📋 Frontend logs (Ctrl+C to exit):"
	@tail -f frontend.log

clean:
	@echo "🧹 Cleaning up..."
	@rm -f backend.log frontend.log
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"
