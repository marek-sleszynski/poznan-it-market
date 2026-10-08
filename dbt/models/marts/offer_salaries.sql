{{ config(materialized='view') }}

select distinct
    offers.raw_offer_id,
    offers.source,
    offers.source_offer_id,
    offers.experience_level,
    lower(salary.value->>'type') as employment_type,
    lower(salary.value->>'currency') as currency,
    lower(salary.value->>'unit') as salary_unit,
    (salary.value->>'gross')::boolean as is_gross,
    (salary.value->>'fromPerUnit')::numeric as salary_from,
    (salary.value->>'toPerUnit')::numeric as salary_to
from {{ ref('latest_offers') }} as offers
inner join {{ source('raw', 'offers') }} as raw
    on raw.id = offers.raw_offer_id
cross join lateral jsonb_array_elements(
    raw.payload->'employmentTypes'
) as salary(value)
where salary.value->>'currencySource' = 'original'
