with selected_offers as (
    select distinct on (source, source_offer_id)
        raw_offer_id
    from fct_offer_snapshot
    where (%(start_date)s::date is null or date_id >= %(start_date)s::date)
      and (%(end_date)s::date is null or date_id <= %(end_date)s::date)
    order by source, source_offer_id, fetched_at desc, raw_offer_id desc
)

select
    history.experience_level,
    history.employment_type,
    history.salary_unit,
    history.is_gross,
    round(avg(history.salary_from), 2) as avg_salary_from,
    count(distinct (history.source, history.source_offer_id)) as offers_with_minimum
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
    history.experience_level,
    history.employment_type,
    history.salary_unit,
    history.is_gross
order by
    history.employment_type,
    history.salary_unit,
    history.is_gross,
    history.experience_level;
