  --  calendar dimension 2020-01-01 to 2030-12-31, one row per day
CREATE TABLE dim_date (
    date_id  DATE PRIMARY KEY,
    year     INTEGER NOT NULL,
    month    INTEGER NOT NULL,
    day      INTEGER NOT NULL,
    iso_year INTEGER NOT NULL,
    iso_week INTEGER NOT NULL
);

INSERT INTO dim_date
WITH RECURSIVE dates AS (
    SELECT DATE '2020-01-01' AS n
    UNION ALL
    SELECT n + 1 FROM dates WHERE n < '2030-12-31'
)

SELECT
    n                             AS date_id,
    EXTRACT(YEAR FROM n)::integer    AS year,
    EXTRACT(MONTH FROM n)::integer   AS month,
    EXTRACT(DAY FROM n)::integer     AS day,
    EXTRACT(ISOYEAR FROM n)::integer AS iso_year,
    EXTRACT(WEEK FROM n)::integer    AS iso_week
FROM dates;
