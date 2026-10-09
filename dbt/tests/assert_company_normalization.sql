select *
from {{ ref('dim_company') }}
where company_name_normalized
          is distinct from lower(trim(company_name))
   or company_key is distinct from md5(company_name_normalized)
   or trim(company_name_normalized) = ''
