{{ config(materialized='table') }}

select
    date_id,
    md5(lower(trim(company_name))) as company_key,
    raw_offer_id,
    source,
    source_offer_id,
    title,
    experience_level,
    is_salary_disclosed,
    published_at,
    fetched_at

from {{ ref('stg_offers') }}

