# Indexes and query performance

## Experiment: filtering postings by date and city

**Query**
```sql
SELECT count(*) 
FROM scratch.offers_sample
WHERE fetched_at >= '2026-08-01' 
  AND payload->>'city' = 'Poznań';
```

**Answer**
```text
Aggregate  (cost=24256.15..24256.16 rows=1 width=8) (actual time=84.959..84.960 rows=1 loops=1)
  Buffers: shared hit=19368 read=8653
  ->  Seq Scan on offers_sample  (cost=0.00..24255.92 rows=92 width=0) (actual time=0.155..84.412 rows=9265 loops=1)
        Filter: ((fetched_at >= '2026-08-01 00:00:00+00'::timestamp with time zone) AND ((payload ->> 'city'::text) = 'Poznań'::text))
        Rows Removed by Filter: 93245
        Buffers: shared hit=19368 read=8653
Planning Time: 0.072 ms
Execution Time: 84.984 ms
```

## Index added

**Query**
```sql
CREATE INDEX idx_offers_fetched_city 
ON scratch.offers_sample (fetched_at, (payload->>'city'));
```

## After indexing

**Query**
(the same as the first one)

**Answer**
```text
Aggregate  (cost=17762.53..17762.54 rows=1 width=8) (actual time=4.403..4.405 rows=1 loops=1)
  Buffers: shared hit=2587
  ->  Bitmap Heap Scan on offers_sample  (cost=381.32..17739.51 rows=9209 width=0) (actual time=1.197..3.837 rows=9265 loops=1)
        Recheck Cond: ((fetched_at >= '2026-08-01 00:00:00+00'::timestamp with time zone) AND ((payload ->> 'city'::text) = 'Poznań'::text))
        Heap Blocks: exact=2535
        Buffers: shared hit=2587
        ->  Bitmap Index Scan on idx_offers_fetched_city  (cost=0.00..379.02 rows=9209 width=0) (actual time=0.791..0.792 rows=9265 loops=1)
              Index Cond: ((fetched_at >= '2026-08-01 00:00:00+00'::timestamp with time zone) AND ((payload ->> 'city'::text) = 'Poznań'::text))
              Buffers: shared hit=52
Planning Time: 0.085 ms
Execution Time: 4.433 ms
```

## Change
85ms to 4.4ms.

## What I learned 
- indexing on (fetched_at, (payload->>'city')) makes filtering by both timestamp (fetched.at) and json field (payload) faster and more efficient.
- in postgresql expressions like payload->>'city' must be in additional parentheses ().
- always run ANALYZE after inserting large data and indexing (faster).
- when query is matching a large result set, the planner switches to a Bitmap index scan. 
