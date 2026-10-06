# Lessons learned

## Where I started (03-08-2026)
Basic Python, university SQL, and about 125 LeetCode Easy problems. Zero portfolio projects, no Docker experience, and never built a real data pipeline.

## Where I ended (06-10-2026)
Built and automated daily pipeline from zero:
- Ingestion: API scraper in Python with retries, exponential backoff, and Pydantic validation.
- Storage: Idempotent loading to PostgreSQL, keeping raw responses as JSONB.
- Modeling: dbt star schema using incremental models and SCD2 snapshots to track history.
- Automation: Scheduled GitHub Actions every day, writing to PostgreSQL database in cloud (Neon).
- Quality & Docs: Automated data tests and written ADRs for key design choices.

## Three things I would do differently: 
- Lock down the fact grain earlier: I had to rewrite part of the staging layer because I didn't decide on the daily grain upfront.
- Add schema tests sooner: Silent API changes can corrupt snapshot histories without noticing.
- Set up CI path filters immediately: Adding paths-ignore stops burning CI minutes on simple misspelling fixes.

## What I still cannot do:
- Streaming: Everything is daily batch. I do not have experience with Kafka.
- Spark: At ~300 postings a day, PostgreSQL is fast and cheap. Using Spark would be overengineering.
- Orchestration tools: No Terraform, Kubernetes, or Airflow yet.

## Next steps 
- Keep pipeline running daily to collect months of job market trends.
- Add second data source (NoFluffJobs) and handle deduplication
- Polish CV to target 2027 Data internships.
