.PHONY: help setup dev test lint fmt clean docker/build docker/run docker/dev docker/stop

# Default target
help:
	@echo "Cancellations SOP Processor - Available Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  setup          Install dependencies and setup development environment"
	@echo ""
	@echo "Development:"
	@echo "  dev            Run Streamlit application locally"
	@echo "  test           Run tests"
	@echo "  lint           Run linting checks"
	@echo "  fmt            Format code with black"
	@echo ""
	@echo "Docker:"
	@echo "  docker/build   Build Docker image"
	@echo "  docker/run     Run Docker container"
	@echo "  docker/dev     Run development container"
	@echo "  docker/stop    Stop all containers"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean          Clean up temporary files and directories"

# Setup development environment
setup:
	@echo "Setting up development environment..."
	python -m pip install --upgrade pip setuptools wheel
	pip install -e ".[dev]"
	pre-commit install
	@echo "Setup complete!"

# Run Streamlit application locally
dev:
	@echo "Starting Streamlit application..."
	streamlit run src/app/main.py --server.port=8501

# Run tests
test:
	@echo "Running tests..."
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

# Run linting
lint:
	@echo "Running linting checks..."
	ruff check src/ tests/
	mypy src/

# Format code
fmt:
	@echo "Formatting code..."
	black src/ tests/
	ruff check --fix src/ tests/

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf processed_reports/
	@echo "Cleanup complete!"

# Docker commands
docker/build:
	@echo "Building Docker image..."
	docker build -t cancellations-sop .

docker/run:
	@echo "Running Docker container..."
	docker-compose up -d

docker/dev:
	@echo "Running development container..."
	docker-compose --profile dev up -d

docker/stop:
	@echo "Stopping containers..."
	docker-compose down

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

# Create requirements.txt from pyproject.toml
requirements:
	@echo "Generating requirements.txt..."
	pip install pip-tools
	pip-compile pyproject.toml --output-file=requirements.txt
