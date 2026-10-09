select skills.*
from {{ ref('fct_offer_skill') }} skills
left join {{ ref('fct_offer_snapshot') }} offers
    on offers.raw_offer_id = skills.raw_offer_id
   and offers.source = skills.source
   and offers.source_offer_id = skills.source_offer_id
   and offers.date_id = skills.date_id
where offers.raw_offer_id is null
