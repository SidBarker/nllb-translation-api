.PHONY: install run test clean download-model docker-build docker-run docker-compose-up docker-compose-down help

# Default target
help:
	@echo "Available commands:"
	@echo "  make install          - Install dependencies"
	@echo "  make download-model   - Download the NLLB model"
	@echo "  make run              - Run the API server"
	@echo "  make test             - Run tests"
	@echo "  make clean            - Clean up temporary files"
	@echo "  make docker-build     - Build Docker image"
	@echo "  make docker-run       - Run in Docker container"
	@echo "  make docker-compose-up - Start with Docker Compose"
	@echo "  make docker-compose-down - Stop Docker Compose services"

# Install dependencies
install:
	pip install -r requirements.txt

# Download model
download-model:
	python models/save_models.py

# Run the API server
run:
	python main.py

# Run tests
test:
	pytest -v

# Clean up temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

# Docker commands
docker-build:
	docker build -t rqg-translation-api:1.0 -f docker/Dockerfile .

docker-run:
	docker run -p 8000:8000 rqg-translation-api:1.0

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down 