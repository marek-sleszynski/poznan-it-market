select 
    skill_name,
    count(distinct source_offer_id) as total_offers
from fct_offer_skill
group by skill_name
order by total_offers desc
limit 15;
