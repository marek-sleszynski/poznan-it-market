-- Create the database only if it does not already exist.
SELECT format('CREATE DATABASE %I', :'database_name')
WHERE NOT EXISTS (
    SELECT 1 FROM pg_database WHERE datname = :'database_name'
)
\gexec
