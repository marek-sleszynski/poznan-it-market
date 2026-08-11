.PHONY: install lint test sample

install:
	uv sync
lint:
	uv run ruff format .
	uv run ruff check --fix .
test:
	uv run pytest
sample:
	uv run python scripts/fetch_sample.py
