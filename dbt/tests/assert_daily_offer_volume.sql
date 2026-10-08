{% set expected_date = var(
    'expected_date',
    run_started_at.strftime('%Y-%m-%d')
) %}

with settings as (
    select
        '{{ expected_date }}'::date as expected_date,
        '{{ var("data_mode", "live") }}'::text as data_mode,
        {{ var("min_volume_ratio", 0.60) }}::numeric as min_volume_ratio
),

daily_counts as (
    select date_id, count(*) as offer_count
    from {{ ref('fct_offer_snapshot') }}
    group by date_id
),

latest_runs as (
    select distinct on (runs.observed_date)
        runs.*
    from {{ source('raw', 'ingestion_runs') }} runs
    cross join settings
    where runs.data_mode = settings.data_mode
      and runs.observed_date >= settings.expected_date - 7
      and runs.observed_date < settings.expected_date
    order by runs.observed_date, runs.started_at desc, runs.run_id desc
),

past_average as (
    select avg(counts.offer_count) as average_count
    from daily_counts counts
    inner join latest_runs runs
        on runs.observed_date = counts.date_id
    where runs.status = 'success'
      and runs.stage = 'finished'
      and runs.finished_at is not null
      and runs.pages_fetched > 0
      and runs.records_accepted > 0
      and runs.records_rejected >= 0
      and runs.records_rejected::numeric
          / nullif(runs.records_accepted::numeric + runs.records_rejected, 0)
          <= {{ var("max_rejection_rate", 0.10) }}::numeric
      and counts.offer_count > 0
),

today_volume as (
    select count(*) as offer_count
    from {{ ref('fct_offer_snapshot') }}
    cross join settings
    where date_id = settings.expected_date
)

select
    settings.expected_date,
    today.offer_count,
    past.average_count,
    settings.min_volume_ratio,
    'offer_volume_drop' as failure_reason
from settings
cross join today_volume today
cross join past_average past
where past.average_count is not null
  and today.offer_count < settings.min_volume_ratio * past.average_count
