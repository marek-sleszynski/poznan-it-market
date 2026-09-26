{{ config(
    materialized='incremental',
    unique_key=['date_id', 'raw_offer_id']
) }}

select
    fetched_at::date as date_id,
    md5(lower(trim(company_name))) as company_key,
    raw_offer_id,
    source,
    source_offer_id,
    title,
    experience_level,
    employment_type,
    salary_from,
    salary_to,
    currency,
    is_salary_disclosed,
    published_at,
    fetched_at

from {{ ref('stg_offers') }}

{% if is_incremental() %}
  where fetched_at > (select max(fetched_at) from {{ this }})
{% endif %}
