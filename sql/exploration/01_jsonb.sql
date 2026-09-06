-- 1. Total count of offers in sample
SELECT count(*)
FROM scratch.offers_sample;


-- 2. Top 10 companies by offer count
SELECT
    payload->>'companyName' AS company_name,
    count(*) AS total_count
FROM scratch.offers_sample
GROUP BY company_name
ORDER BY total_count DESC
LIMIT 10;


-- 3. Top 15 req technologies
SELECT
    skill->>'name' AS tech,
    count(*) AS tech_count
FROM scratch.offers_sample,
     jsonb_array_elements(payload->'requiredSkills') AS skill
GROUP BY skill->>'name'
ORDER BY tech_count DESC
LIMIT 15;
