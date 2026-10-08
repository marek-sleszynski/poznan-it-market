with salary_coverage as (
    select
        raw_offer_id,
        bool_or(
            salary_from is not null and salary_to is not null
        ) as has_full_range
    from offer_salaries
    group by raw_offer_id
)

select
    offers.experience_level,
    count(*) as total_offers,
    count(*) filter (
        where offers.is_salary_disclosed
    ) as offers_with_salary,
    count(*) filter (
        where coverage.has_full_range
    ) as offers_with_full_range,
    count(*) filter (
        where offers.is_salary_disclosed
          and not coalesce(coverage.has_full_range, false)
    ) as offers_with_partial_range,
    round(
        100.0 * count(*) filter (where offers.is_salary_disclosed) / count(*),
        2
    ) as disclosure_rate_pct
from latest_offers offers
left join salary_coverage coverage
    on coverage.raw_offer_id = offers.raw_offer_id
group by offers.experience_level
order by total_offers desc, offers.experience_level;
