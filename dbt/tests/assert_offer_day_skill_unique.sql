select
    source,
    source_offer_id,
    date_id,
    skill_name,
    count(*) as row_count
from {{ ref('fct_offer_skill') }}
group by source, source_offer_id, date_id, skill_name
having count(*) > 1
