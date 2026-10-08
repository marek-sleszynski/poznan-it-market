select
    skills.skill_name,
    count(*) as total_offers
from fct_offer_skill skills
inner join latest_offers offers
    on offers.raw_offer_id = skills.raw_offer_id
group by skills.skill_name
order by total_offers desc, skills.skill_name
limit 15;
