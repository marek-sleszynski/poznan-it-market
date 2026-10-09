{% set expected_date = var(
    'expected_date',
    run_started_at.strftime('%Y-%m-%d')
) %}

with latest_run as (
    select *
    from {{ source('raw', 'ingestion_runs') }}
    where observed_date = '{{ expected_date }}'::date
      and data_mode = '{{ var("data_mode", "live") }}'
    order by started_at desc, run_id desc
    limit 1
),

measured as (
    select
        observed_date,
        records_accepted,
        records_rejected,
        records_rejected::numeric
            / nullif(records_accepted::numeric + records_rejected, 0)
            as rejection_rate
    from latest_run
    where status = 'success'
      and records_accepted >= 0
      and records_rejected >= 0
)

select
    *,
    'high_rejection_rate' as failure_reason
from measured
where rejection_rate > {{ var("max_rejection_rate", 0.10) }}::numeric
