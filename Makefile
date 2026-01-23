.PHONY: help install update check format lint typecheck test test-all test-cov test-property test-integration clean build docs

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	uv venv
	uv sync --all-extras

update: ## Update dependencies
	uv lock --upgrade
	uv sync --all-extras

check: format lint typecheck test ## Run all quality checks

format: ## Format code with ruff
	uv run ruff format .

lint: ## Check code with ruff
	uv run ruff check .

lint-fix: ## Fix linting issues automatically
	uv run ruff check --fix .

typecheck: ## Run mypy type checking
	uv run mypy better_py

test: ## Run unit tests
	uv run pytest -m unit -v

test-all: ## Run all tests
	uv run pytest -v

test-cov: ## Run tests with coverage
	uv run pytest --cov=better_py --cov-report=html --cov-report=term-missing

test-property: ## Run property-based tests
	uv run pytest -m property -v

test-integration: ## Run integration tests
	uv run pytest -m integration -v

test-bench: ## Run benchmarks
	uv run pytest -m benchmark

clean: ## Clean build artifacts
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: ## Build package
	uv build

docs: ## Build documentation
	@if command -v mkdocs >/dev/null 2>&1; then \
		uv run mkdocs build; \
	else \
		echo "mkdocs not installed, skipping"; \
	fi

docs-serve: ## Serve documentation locally
	@if command -v mkdocs >/dev/null 2>&1; then \
		uv run mkdocs serve; \
	else \
		echo "mkdocs not installed, skipping"; \
	fi

install-pre-commit: ## Install pre-commit hooks
	@if command -v pre-commit >/dev/null 2>&1; then \
		pre-commit install; \
	else \
		echo "pre-commit not installed, run: uv pip install pre-commit"; \
	fi
