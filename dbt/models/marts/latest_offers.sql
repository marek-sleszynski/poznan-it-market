{{ config(materialized='view') }}

select distinct on (source, source_offer_id)
    *
from {{ ref('fct_offer_snapshot') }}
order by
    source,
    source_offer_id,
    fetched_at desc,
    raw_offer_id desc
