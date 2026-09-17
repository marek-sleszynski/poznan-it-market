with companies as (
    select
        lower(trim(company_name)) as company_name_normalized,
        min(company_name)          as company_name
    from {{ ref('stg_offers') }}
    where company_name is not null
    group by 1
)
select
    md5(company_name_normalized) as company_key,
    company_name,
    company_name_normalized
from companies
group by company_name_normalized, company_name
