.PHONY: charts-demo install lint test db-up db-shell db-reset ingest dbt charts migrate demo format dbt-demo db-prepare

DBT := uv run --locked $(if $(wildcard .env),--env-file .env) dbt
DBT_DIRS := --project-dir dbt --profiles-dir dbt
DEMO_DB ?= poznan_it_market_demo
DEMO_DATE ?= 2026-08-11

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
db-up:
	docker compose up -d
db-shell:
	docker compose exec db sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'
db-reset:
	docker compose down -v
	docker compose up -d
ingest:
	uv run --locked poznan-it-market --mode live

demo:
	uv run --locked poznan-it-market --mode demo
	$(MAKE) dbt-demo
	$(MAKE) charts-demo
dbt:
	$(DBT) build $(DBT_DIRS)
dbt-demo:
	@case "$(DEMO_DB)" in poznan_it_market_demo|poznan_it_market_test) ;; \
		*) echo "dbt-demo requires poznan_it_market_demo or poznan_it_market_test" >&2; exit 1 ;; esac
	DB_HOST=localhost POSTGRES_DB=$(DEMO_DB) $(DBT) build $(DBT_DIRS) \
		--vars '{"data_mode": "demo", "expected_date": "$(DEMO_DATE)"}'
charts:
	uv run --locked python scripts/make_charts.py
charts-demo:
	uv run --locked python scripts/make_charts.py --mode demo
migrate:
	for f in sql/ddl/*.sql; do \
	        docker compose exec -T db sh -c 'psql -X -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -v ON_ERROR_STOP=1' < "$$f" || exit 1; \
	done
db-prepare: db-up
	docker compose exec -T db sh -c 'until pg_isready -h 127.0.0.1 -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"; do sleep 1; done'
	for database in poznan_it_market_demo poznan_it_market_test; do \
	        docker compose exec -T db sh -c 'psql -X -U "$$POSTGRES_USER" -d postgres -v ON_ERROR_STOP=1 -v database_name="$$1"' sh "$$database" < sql/maintenance/create_local_database.sql || exit 1; \
	        for file in sql/ddl/*.sql; do \
	                docker compose exec -T db sh -c 'psql -X -U "$$POSTGRES_USER" -d "$$1" -v ON_ERROR_STOP=1' sh "$$database" < "$$file" || exit 1; \
	        done; \
	done
