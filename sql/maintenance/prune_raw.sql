-- delete offers from the cloud older than 30 days
DELETE FROM raw.offers
WHERE fetched_at < NOW() - INTERVAL '30 days';

DELETE FROM raw.rejected_records
WHERE rejected_at < NOW() - INTERVAL '30 days';
