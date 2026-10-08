select
    raw_offer_id,
    employment_type,
    currency,
    salary_unit,
    salary_from,
    salary_to
from {{ ref('offer_salary_history') }}
where salary_from > salary_to
   or salary_from < 0
   or salary_to < 0
   or salary_from::text in ('NaN', 'Infinity', '-Infinity')
   or salary_to::text in ('NaN', 'Infinity', '-Infinity')
