.PHONY: install lint test sample db-up db-shell db-reset ingest snapshot dbt charts

install:
	uv sync
lint:
	uv run ruff format .
	uv run ruff check --fix .
test:
	uv run pytest
sample:
	uv run python scripts/fetch_sample.py
db-up:
	docker compose up -d
db-shell:
	docker compose exec db sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'
db-reset:
	docker compose down -v
	docker compose up -d
ingest:
	uv run python -m poznan_it_market.ingest.loader
snapshot:
	cd dbt && uv run dbt snapshot --profiles-dir .
dbt:
	cd dbt && uv run dbt build --profiles-dir .
charts:
	uv run python scripts/make_charts.py
