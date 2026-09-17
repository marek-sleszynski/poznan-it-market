SELECT
    c.company_name,
    count(distinct o.source_offer_id) as total_offers
from fct_offer_snapshot o
inner join dim_company c
    on c.company_key = o.company_key
group by c.company_name
order by total_offers desc
limit 10;
