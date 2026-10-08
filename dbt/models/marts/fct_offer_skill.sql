{{ config(materialized='table') }}

select distinct
    (offers.fetched_at AT TIME ZONE 'UTC')::date as date_id,
    offers.raw_offer_id,
    offers.source,
    offers.source_offer_id,
    offers.experience_level,
    lower(trim(skill.value->>'name')) as skill_name
from {{ ref('stg_offers') }} as offers
cross join lateral jsonb_array_elements(offers.required_skills) as skill(value)
where jsonb_typeof(offers.required_skills) = 'array'
  and trim(skill.value->>'name') <> ''
