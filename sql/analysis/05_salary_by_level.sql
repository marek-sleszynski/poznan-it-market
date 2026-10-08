select
    experience_level,
    employment_type,
    salary_unit,
    is_gross,
    round(avg(salary_from), 2) as avg_salary_from,
    count(distinct (source, source_offer_id)) as offers_with_minimum
from offer_salaries
where currency = 'pln'
  and employment_type in ('b2b', 'permanent')
  and salary_unit in ('hour', 'month')
  and is_gross is not null
  and salary_from is not null
  and experience_level is not null
group by
    experience_level,
    employment_type,
    salary_unit,
    is_gross
order by
    employment_type,
    salary_unit,
    is_gross,
    experience_level;
