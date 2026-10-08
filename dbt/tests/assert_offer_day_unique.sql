select
    source,
    source_offer_id,
    date_id,
    count(*) as row_count
from {{ ref('fct_offer_snapshot') }}
group by source, source_offer_id, date_id
having count(*) > 1
