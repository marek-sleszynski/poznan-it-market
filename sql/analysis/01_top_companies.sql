with selected_offers as (
    select distinct on (source, source_offer_id)
        raw_offer_id,
        company_key
    from fct_offer_snapshot
    where (%(start_date)s::date is null or date_id >= %(start_date)s::date)
      and (%(end_date)s::date is null or date_id <= %(end_date)s::date)
    order by source, source_offer_id, fetched_at desc, raw_offer_id desc
)

select
    companies.company_name,
    count(*) as total_offers
from selected_offers offers
inner join dim_company companies
    on companies.company_key = offers.company_key
group by companies.company_name
order by total_offers desc, companies.company_name
limit 10;
