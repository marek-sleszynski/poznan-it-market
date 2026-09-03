================================================================================
SQL WINDOW FUNCTIONS - QUICK REFERENCE
================================================================================

1. SYNTAX
--------------------------------------------------------------------------------
FUNCTION() OVER (
    PARTITION BY column
    ORDER BY column
    ROWS|RANGE frame_specification
)

- Executes in SELECT (after GROUP BY).
- Cannot be filtered directly in WHERE (use CTE or subquery).
- Empty OVER () covers the entire query result set.


2. ROW_NUMBER vs RANK vs DENSE_RANK
--------------------------------------------------------------------------------
Value | ROW_NUMBER | RANK | DENSE_RANK | Note
------+------------+------+------------+--------------------------------------
100   |     1      |  1   |     1      | Highest value
80    |     2      |  2   |     2      | Tie A
80    |     3      |  2   |     2      | Tie B
60    |     4      |  4   |     3      | RANK skips to 4; DENSE_RANK stays 3

- ROW_NUMBER(): Unique sequential integers (1, 2, 3, 4). Best for pagination.
- RANK(): Ties share rank; subsequent ranks skip (1, 2, 2, 4).
- DENSE_RANK(): Ties share rank; consecutive numbers without gaps (1, 2, 2, 3).


3. FRAMES: ROWS vs RANGE
--------------------------------------------------------------------------------
- ROWS: Physical row count (e.g., ROWS BETWEEN 6 PRECEDING AND CURRENT ROW).
- RANGE: Logical value range; treats duplicate ORDER BY values as a single peer group.
- Default frame with ORDER BY:
  RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  (Use ROWS for strict row-by-row running calculations).


4. KEY FUNCTIONS
--------------------------------------------------------------------------------
- LAG(col, n) / LEAD(col, n): Value from n rows prior / ahead.
- FIRST_VALUE(col) / LAST_VALUE(col): First / last value in the current frame.
  Note: LAST_VALUE requires:
  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
- NTILE(n): Divides sorted rows into n equal buckets.


5. PRACTICAL EXAMPLE
--------------------------------------------------------------------------------
SELECT
    customer_id,
    payment_date::DATE AS payment_day,
    amount,

    -- Sequential order per customer
    ROW_NUMBER() OVER (
        PARTITION BY customer_id 
        ORDER BY payment_date
    ) AS rental_seq,

    -- Previous transaction amount
    LAG(amount) OVER (
        PARTITION BY customer_id 
        ORDER BY payment_date
    ) AS prev_amount,

    -- Running total spend per customer
    SUM(amount) OVER (
        PARTITION BY customer_id 
        ORDER BY payment_date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS customer_running_total,

    -- Overall total across all records
    SUM(amount) OVER () AS grand_total
FROM payment;
