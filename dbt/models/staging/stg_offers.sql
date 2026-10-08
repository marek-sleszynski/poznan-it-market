{{ config(materialized='view') }}

{% set selected_mode = var('data_mode', 'live') %}

{% if selected_mode not in ['live', 'demo'] %}
    {{ exceptions.raise_compiler_error("data_mode must be live or demo") }}
{% endif %}

with source as (
    select *
    from {{ source('raw', 'offers') }}
    where data_mode = '{{ selected_mode }}'
),

renamed as (
    select
        id as raw_offer_id,
        source,
        source_offer_id,
        fetched_at,
        run_id,
        data_mode,
        payload->>'title' as title,
        payload->>'companyName' as company_name,
        payload->>'city' as city,
        payload->>'experienceLevel' as experience_level,
        (payload->>'publishedAt')::timestamptz as published_at,

        (payload->'employmentTypes'->0->>'from')::numeric as salary_from,
        (payload->'employmentTypes'->0->>'to')::numeric as salary_to,
        lower(payload->'employmentTypes'->0->>'currency') as currency,
        payload->'employmentTypes'->0->>'type' as employment_type,
        (payload->'employmentTypes'->0->>'from') is not null as is_salary_disclosed,
       
        payload->'requiredSkills' as required_skills

   from source
   where payload->>'city' in ('Poznań', 'Poznan')
)

select * from renamed

