{{ config(materialized='table') }}

select
    fetched_at::date as date_id,
    raw_offer_id,
    source,
    source_offer_id,
    experience_level,
    lower(trim(jsonb_array_elements_text(required_skills))) as skill_name
from {{ref('stg_offers')}}
where required_skills is not null
  and jsonb_typeof(required_skills) = 'array'
