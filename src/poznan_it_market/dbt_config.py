import os

from psycopg import pq
from psycopg.conninfo import conninfo_to_dict

from poznan_it_market.config import require_database_url

PROFILE_VARIABLES = {
    "host": "DB_HOST",
    "port": "DB_PORT",
    "user": "POSTGRES_USER",
    "password": "POSTGRES_PASSWORD",
    "dbname": "POSTGRES_DB",
    "sslmode": "DB_SSLMODE",
    "connect_timeout": "DB_CONNECT_TIMEOUT",
    "application_name": "DB_APPLICATION_NAME",
}


def dbt_environment_from_url(database_url: str | None) -> dict[str, str]:
    params = {
        key: str(value)
        for key, value in conninfo_to_dict(require_database_url(database_url)).items()
        if value is not None
    }
    for name in ("host", "user", "password", "dbname"):
        if not params.get(name):
            raise ValueError(f"DATABASE_URL must include {name} for dbt.")

    result = {
        "DB_PORT": os.environ.get("PGPORT", "5432"),
        "DB_SSLMODE": os.environ.get("PGSSLMODE", "prefer"),
        "DB_CONNECT_TIMEOUT": os.environ.get("PGCONNECT_TIMEOUT", "10"),
        "DB_APPLICATION_NAME": os.environ.get("PGAPPNAME", "dbt"),
    }
    pg_variables = {
        option.keyword.decode(): option.envvar.decode()
        for option in pq.Conninfo.get_defaults()
        if option.envvar
    }
    for name, value in params.items():
        variable = PROFILE_VARIABLES.get(name) or pg_variables.get(name)
        if variable is None:
            raise ValueError(f"Unsupported database option for dbt: {name}")
        result[variable] = value
    return result
