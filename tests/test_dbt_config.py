from contextvars import copy_context
from pathlib import Path

import pytest
import yaml
from dbt.config.renderer import ProfileRenderer
from dbt_common.context import set_invocation_context
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from poznan_it_market.dbt_config import dbt_environment_from_url

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_dbt_profile_matches_uri_with_special_characters():
    url = (
        "postgresql://user%40team:p%40ss%3A%22word%2F%25@127.0.0.1:5544/custom%20market"
        "?sslmode=verify-full&connect_timeout=17&application_name=market%20test"
    )
    settings = dbt_environment_from_url(url)
    raw_profile = yaml.safe_load(
        (PROJECT_ROOT / "dbt/profiles.yml.example").read_text(encoding="utf-8")
    )

    def render_profile():
        # Initialize dbt's environment snapshot in an isolated context.
        set_invocation_context(settings)
        return ProfileRenderer({}).render_data(raw_profile)

    profile = copy_context().run(render_profile)["poznan_it_market"]["outputs"]["dev"]
    python_params = conninfo_to_dict(url)

    assert profile["host"] == python_params["host"] == "127.0.0.1"
    assert profile["user"] == python_params["user"] == "user@team"
    assert profile["password"] == python_params["password"] == 'p@ss:"word/%'
    assert profile["dbname"] == python_params["dbname"] == "custom market"
    assert int(profile["port"]) == int(python_params["port"]) == 5544
    assert profile["sslmode"] == "verify-full"
    assert int(profile["connect_timeout"]) == 17
    assert profile["application_name"] == "market test"


def test_preserves_libpq_connection_options():
    url = (
        "postgresql://tester:dummy@localhost/market"
        "?sslmode=require&channel_binding=require"
        "&options=-c%20statement_timeout%3D5000&sslrootcert=%2Ftmp%2Froot%20cert.pem"
    )
    settings = dbt_environment_from_url(url)
    assert settings["DB_SSLMODE"] == "require"
    assert settings["PGCHANNELBINDING"] == "require"
    assert settings["PGOPTIONS"] == "-c statement_timeout=5000"
    assert settings["PGSSLROOTCERT"] == "/tmp/root cert.pem"


def test_supports_postgres_keyword_connection_strings():
    settings = dbt_environment_from_url(
        "host=localhost user='test user' password='dummy password' dbname='custom market'"
    )
    assert settings["POSTGRES_USER"] == "test user"
    assert settings["POSTGRES_PASSWORD"] == "dummy password"
    assert settings["POSTGRES_DB"] == "custom market"


@pytest.mark.parametrize("missing", ["host", "user", "password", "dbname"])
def test_refuses_implicit_database_identity(missing):
    params = {"host": "localhost", "user": "tester", "password": "dummy", "dbname": "market"}
    del params[missing]
    with pytest.raises(ValueError, match=f"include {missing}"):
        dbt_environment_from_url(make_conninfo(**params))


@pytest.mark.parametrize("url", [None, ""])
def test_requires_database_url(url):
    with pytest.raises(ValueError, match="DATABASE_URL"):
        dbt_environment_from_url(url)


def test_refuses_options_that_cannot_be_forwarded():
    with pytest.raises(ValueError, match="fallback_application_name"):
        dbt_environment_from_url(
            "host=localhost user=tester password=dummy dbname=market fallback_application_name=test"
        )


def test_exports_values_and_masks_multiline_password(tmp_path, monkeypatch, capsys):
    from scripts import export_dbt_env

    output_path = tmp_path / "github_env"
    monkeypatch.setenv("GITHUB_ENV", str(output_path))
    monkeypatch.setattr(
        export_dbt_env,
        "DATABASE_URL",
        "postgresql://tester:dummy%0Apassword@localhost/market?channel_binding=require",
    )
    export_dbt_env.main()
    assert capsys.readouterr().out == "::add-mask::dummy%0Apassword\n"

    lines = iter(output_path.read_text(encoding="utf-8").splitlines())
    exported = {}
    for header in lines:
        name, delimiter = header.split("<<", 1)
        value = []
        for line in lines:
            if line == delimiter:
                break
            value.append(line)
        exported[name] = "\n".join(value)

    assert exported["POSTGRES_PASSWORD"] == "dummy\npassword"
    assert exported["POSTGRES_DB"] == "market"
    assert exported["PGCHANNELBINDING"] == "require"
