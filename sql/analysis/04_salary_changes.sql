WITH offers_history AS (
    SELECT
        source_offer_id,
        company_name,
        LAG(salary_from) OVER (PARTITION BY source_offer_id ORDER BY dbt_valid_from) AS old_salary_from,
        LAG(salary_to) OVER (PARTITION BY source_offer_id ORDER BY dbt_valid_from) AS old_salary_to,
        salary_from AS new_salary_from,
        salary_to AS new_salary_to,
        dbt_valid_from AS changed_at
    FROM snapshots.snap_offers)
SELECT
    source_offer_id,
    company_name,
    old_salary_from,
    old_salary_to,
    new_salary_from,
    new_salary_to,
    changed_at
FROM offers_history
WHERE old_salary_from IS NOT NULL;
