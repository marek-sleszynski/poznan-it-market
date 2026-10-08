select
    experience_level,
    count(*) as total_offers,
    count(*) filter (where is_salary_disclosed) as offers_with_salary,
    round(
        100.0 * count(*) filter (where is_salary_disclosed) / count(*),
        2
    ) as disclosure_rate_pct
from latest_offers
group by experience_level
order by total_offers desc, experience_level;
