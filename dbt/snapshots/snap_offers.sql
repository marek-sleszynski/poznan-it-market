{% snapshot snap_offers %}
{{
    config(
        target_schema='snapshots',
        unique_key='source_offer_id',
        strategy='check',
        check_cols=['salary_from', 'salary_to', 'currency']
    )
}}
select
    source,
    source_offer_id,
    title,
    company_name,
    city,
    experience_level,
    published_at,
    salary_from,
    salary_to,
    currency,
    employment_type,
    is_salary_disclosed

from {{ ref('stg_offers') }}

{% endsnapshot %}
