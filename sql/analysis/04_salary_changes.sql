with compared as (
    select
        source,
        source_offer_id,
        employment_type,
        currency,
        salary_unit,
        is_gross,
        fetched_at as observed_at,
        lag(fetched_at) over salary_history as previous_observed_at,
        lag(salary_from) over salary_history as old_salary_from,
        lag(salary_to) over salary_history as old_salary_to,
        salary_from as new_salary_from,
        salary_to as new_salary_to
    from offer_salary_history
    where employment_type is not null
      and currency is not null
      and salary_unit is not null
      and is_gross is not null
    window salary_history as (
        partition by
            source,
            source_offer_id,
            employment_type,
            currency,
            salary_unit,
            is_gross
        order by fetched_at, raw_offer_id
    )
)

select *
from compared
where previous_observed_at is not null
  and (
      old_salary_from is distinct from new_salary_from
      or old_salary_to is distinct from new_salary_to
  )
order by observed_at, source, source_offer_id;
