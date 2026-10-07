.PHONY: install lint test sample db-up db-shell db-reset ingest snapshot dbt charts migrate demo

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
	uv run poznan-it-market --mode live

demo:
	uv run poznan-it-market --mode demo
snapshot:
	cd dbt && uv run dbt snapshot --profiles-dir .
dbt:
	cd dbt && uv run dbt build --profiles-dir .
charts:
	uv run python scripts/make_charts.py
migrate:
	for f in sql/ddl/*.sql; do \
		docker compose exec -T db sh -c 'psql -X -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -v ON_ERROR_STOP=1' < "$$f" || exit 1; \
	done
