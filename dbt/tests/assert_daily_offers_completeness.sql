{% set expected_date = var(
    'expected_date',
    run_started_at.strftime('%Y-%m-%d')
) %}

with settings as (
    select
        '{{ expected_date }}'::date as expected_date,
        '{{ var("data_mode", "live") }}'::text as data_mode
),

latest_run as (
    select runs.*
    from {{ source('raw', 'ingestion_runs') }} runs
    cross join settings
    where runs.observed_date = settings.expected_date
      and runs.data_mode = settings.data_mode
    order by runs.started_at desc, runs.run_id desc
    limit 1
),

daily_volume as (
    select count(*) as offer_count
    from {{ ref('fct_offer_snapshot') }}
    cross join settings
    where date_id = settings.expected_date
),

checked as (
    select
        settings.expected_date,
        settings.data_mode,
        runs.status,
        volume.offer_count,
        case
            when runs.run_id is null then 'missing_import'
            when runs.status <> 'success'
              or runs.finished_at is null
              or runs.stage is distinct from 'finished'
                then 'unfinished_or_failed_import'
            when coalesce(runs.pages_fetched, 0) <= 0
              or runs.records_accepted is null
              or runs.records_rejected is null
              or runs.records_accepted < 0
              or runs.records_rejected < 0
                then 'invalid_import_counters'
            when runs.records_accepted = 0 then 'no_accepted_offers'
            when volume.offer_count = 0 then 'no_report_offers'
        end as failure_reason
    from settings
    cross join daily_volume volume
    left join latest_run runs on true
)

select *
from checked
where failure_reason is not null
