.PHONY: test test-live lint typecheck check clean

test:
	uv run pytest tests/ -v

# Costs money: only the generation-backed tests. Never part of `make check`.
test-live:
	uv run pytest tests/ -v -m live

lint:
	uv run ruff check src/ tests/

typecheck:
	uv run mypy src/ --strict

check: lint typecheck test

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null; \
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null; \
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null; \
	rm -rf dist/ build/
