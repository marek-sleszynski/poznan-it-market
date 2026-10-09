.PHONY: install lint test sample db-up db-shell db-reset ingest snapshot dbt charts migrate demo format dbt-demo db-perepare

install:
	uv sync --locked
lint:
	uv run --locked ruff check .
	uv run --locked ruff format --check .
format:
	uv run --locked ruff check --fix .
	uv run --locked ruff format .
test:
	uv run --locked pytest
sample:
	uv run --locked python scripts/fetch_sample.py
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
	uv run --locked python scripts/build_dbt.py --mode live
dbt-demo:
	uv run --locked python scripts/build_dbt.py --mode demo --expected-date 2026-08-11
charts:
	uv run python scripts/make_charts.py
migrate:
	for f in sql/ddl/*.sql; do \
		docker compose exec -T db sh -c 'psql -X -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -v ON_ERROR_STOP=1' < "$$f" || exit 1; \
	done
db-prepare: db-up
	docker compose exec -T db sh -c 'until pg_isready -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"; do sleep 1; done'
	for database in poznan_it_market_demo poznan_it_market_test; do \
		docker compose exec -T db sh -c 'psql -X -U "$$POSTGRES_USER" -d postgres -v ON_ERROR_STOP=1 -v database_name="$$1"' sh "$$database" < sql/maintenance/create_local_database.sql || exit 1; \
		for file in sql/ddl/*.sql; do \
			docker compose exec -T db sh -c 'psql -X -U "$$POSTGRES_USER" -d "$$1" -v ON_ERROR_STOP=1' sh "$$database" < "$$file" || exit 1; \
		done; \
	done
