select
    date_id,
    count(*) as total_offers,
    count(*) filter (
        where not is_salary_disclosed
    ) as offers_without_salary
from fct_offer_snapshot
where (%(start_date)s::date is null or date_id >= %(start_date)s::date)
  and (%(end_date)s::date is null or date_id <= %(end_date)s::date)
group by date_id
order by date_id;
