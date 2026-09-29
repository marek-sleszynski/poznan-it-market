select
    raw_offer_id,
    salary_from,
    salary_to
from {{ ref('stg_offers') }}
where salary_from > salary_to
