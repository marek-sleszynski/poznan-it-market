with selected_offers as (
    select distinct on (source, source_offer_id)
        raw_offer_id
    from fct_offer_snapshot
    where (%(start_date)s::date is null or date_id >= %(start_date)s::date)
      and (%(end_date)s::date is null or date_id <= %(end_date)s::date)
    order by source, source_offer_id, fetched_at desc, raw_offer_id desc
)

select
    skills.skill_name,
    count(*) as total_offers
from fct_offer_skill skills
inner join selected_offers offers
    on offers.raw_offer_id = skills.raw_offer_id
group by skills.skill_name
order by total_offers desc, skills.skill_name
limit 15;
