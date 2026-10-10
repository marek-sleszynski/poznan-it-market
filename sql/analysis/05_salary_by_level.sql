with selected_offers as (
    select distinct on (source, source_offer_id)
        raw_offer_id
    from fct_offer_snapshot
    where (%(start_date)s::date is null or date_id >= %(start_date)s::date)
      and (%(end_date)s::date is null or date_id <= %(end_date)s::date)
    order by source, source_offer_id, fetched_at desc, raw_offer_id desc
),

offer_minimums as (
    select
        history.source,
        history.source_offer_id,
        history.experience_level,
        history.employment_type,
        history.salary_unit,
        history.is_gross,
        avg(history.salary_from) as salary_from
    from offer_salary_history history
    inner join selected_offers offers
        on offers.raw_offer_id = history.raw_offer_id
    where history.currency = 'pln'
      and history.employment_type in ('b2b', 'permanent')
      and history.salary_unit in ('hour', 'month')
      and history.is_gross is not null
      and history.salary_from is not null
      and history.experience_level is not null
    group by
        history.source,
        history.source_offer_id,
        history.experience_level,
        history.employment_type,
        history.salary_unit,
        history.is_gross
)

select
    experience_level,
    employment_type,
    salary_unit,
    is_gross,
    round(avg(salary_from), 2) as avg_salary_from,
    count(*) as offers_with_minimum
from offer_minimums
group by
    experience_level,
    employment_type,
    salary_unit,
    is_gross
order by
    employment_type,
    salary_unit,
    is_gross,
    experience_level;
