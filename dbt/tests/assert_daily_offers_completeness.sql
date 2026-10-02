with daily_counts as (
    select
        date_id,
        count(*) as offer_count
    from {{ ref('fct_offer_snapshot') }}
    group by date_id
),

latest_snapshot as (
    select max(date_id) as latest_date
    from daily_counts
),

past_7_days_avg as (
    select avg(offer_count) as avg_7d_count
    from daily_counts
    cross join latest_snapshot
    where daily_counts.date_id < latest_snapshot.latest_date
      and daily_counts.date_id >= latest_snapshot.latest_date - interval '7 days'
),

today_volume as (
    select daily_counts.offer_count
    from daily_counts
    cross join latest_snapshot
    where daily_counts.date_id = latest_snapshot.latest_date
)

select
    today_volume.offer_count,
    past_7_days_avg.avg_7d_count
from today_volume
cross join past_7_days_avg
where past_7_days_avg.avg_7d_count is not null
  and today_volume.offer_count < 0.60 * past_7_days_avg.avg_7d_count
