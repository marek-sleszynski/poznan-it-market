select
    c.company_name,
    count(*) as total_offers
from latest_offers o
inner join dim_company c
    on c.company_key = o.company_key
group by c.company_name
order by total_offers desc, c.company_name
limit 10;
