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
    (salary.value->>'toPerUnit')::numeric as salary_to,
    offers.date_id,
    offers.fetched_at
from {{ ref('stg_offers') }} as offers
cross join lateral jsonb_array_elements(
    offers.employment_types
) as salary(value)
where salary.value->>'currencySource' = 'original'
