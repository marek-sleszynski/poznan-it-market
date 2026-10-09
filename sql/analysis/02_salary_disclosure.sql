with selected_offers as (
    select distinct on (source, source_offer_id)
        raw_offer_id,
        experience_level,
        is_salary_disclosed
    from fct_offer_snapshot
    where (%(start_date)s::date is null or date_id >= %(start_date)s::date)
      and (%(end_date)s::date is null or date_id <= %(end_date)s::date)
    order by source, source_offer_id, fetched_at desc, raw_offer_id desc
),

salary_coverage as (
    select
        history.raw_offer_id,
        bool_or(
            history.salary_from is not null and history.salary_to is not null
        ) as has_full_range
    from offer_salary_history history
    inner join selected_offers offers
        on offers.raw_offer_id = history.raw_offer_id
    group by history.raw_offer_id
)

select
    offers.experience_level,
    count(*) as total_offers,
    count(*) filter (
        where offers.is_salary_disclosed
    ) as offers_with_salary,
    count(*) filter (
        where coverage.has_full_range
    ) as offers_with_full_range,
    count(*) filter (
        where offers.is_salary_disclosed
          and not coalesce(coverage.has_full_range, false)
    ) as offers_with_partial_range,
    round(
        100.0 * count(*) filter (where offers.is_salary_disclosed) / count(*),
        2
    ) as disclosure_rate_pct
from selected_offers offers
left join salary_coverage coverage
    on coverage.raw_offer_id = offers.raw_offer_id
group by offers.experience_level
order by total_offers desc, offers.experience_level;
