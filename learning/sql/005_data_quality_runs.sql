-- Learning example. The project checks data quality with dbt tests.
create table if not exists raw.data_quality_runs (
    id bigserial primary key,
    run_id uuid,
    checked_at timestamptz not null default now(),
    tests_passed int not null default 0,
    tests_warned int not null default 0,
    tests_failed int not null default 0,
    status text not null
);
