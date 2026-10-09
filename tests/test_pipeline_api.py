from datetime import UTC

import httpx
import pytest
from tenacity import wait_none

from poznan_it_market import pipeline
from poznan_it_market.ingest import justjoinit


def make_offer(slug):
    return {
        "slug": slug,
        "title": "Test developer",
        "companyName": "Test Company",
        "city": "Poznań",
        "publishedAt": "2020-01-01T10:00:00Z",
        "employmentTypes": [],
        "requiredSkills": [{"name": "Python", "level": 3}],
    }


def make_page(offers, cursor, next_cursor):
    return {
        "data": offers,
        "meta": {"from": cursor, "next": {"cursor": next_cursor}},
    }


@pytest.fixture
def mock_api(monkeypatch):
    # Keep pagination and retry rules, but disable real waiting.
    fast_fetch = justjoinit.fetch_url_with_retry.retry_with(wait=wait_none(), sleep=lambda _: None)
    monkeypatch.setattr(justjoinit, "fetch_url_with_retry", fast_fetch)
    monkeypatch.setattr(justjoinit.time, "sleep", lambda _: None)

    def install(handler):
        client = httpx.Client(transport=httpx.MockTransport(handler))
        monkeypatch.setattr(justjoinit, "get_http_client", lambda: client)
        return client

    return install


@pytest.mark.parametrize(
    "invalid_salary, expected_error",
    [
        (
            {"fromPerUnit": 25000, "toPerUnit": 15000},
            "salary_from_per_unit cannot exceed salary_to_per_unit",
        ),
        ({"fromPerUnit": "not-a-number"}, "fromPerUnit"),
        ({"gross": "unknown"}, "gross"),
    ],
    ids=["reversed-range", "invalid-amount", "invalid-gross"],
)
def test_two_page_pipeline_saves_offers_rejection_and_metrics(
    db_conn, mock_api, invalid_salary, expected_error
):
    first = make_offer("api-first")
    first["employmentTypes"] = [
        {
            "fromPerUnit": "12345.67",
            "toPerUnit": 18000,
            "gross": False,
            "unit": "month",
            "currency": "PLN",
            "currencySource": "original",
            "type": "b2b",
        }
    ]
    first["extraField"] = "keep"
    second = make_offer("api-second")
    invalid = make_offer("api-invalid-salary")
    invalid["employmentTypes"] = [
        {
            "fromPerUnit": 10000,
            "toPerUnit": 18000,
            "gross": False,
            "unit": "month",
            "currency": "PLN",
            "currencySource": "original",
            "type": "b2b",
            **invalid_salary,
        }
    ]
    requested_cursors = []

    def handler(request):
        cursor = int(request.url.params["from"])
        requested_cursors.append(cursor)
        assert request.url.params["city"] == "Poznań"
        assert request.url.params["cityRadius"] == "0"
        if cursor == 0:
            return httpx.Response(200, json=make_page([first, invalid], 0, 10))
        assert cursor == 10
        return httpx.Response(200, json=make_page([second], 10, None))

    client = mock_api(handler)
    pipeline.run_pipeline(mode="live")

    assert requested_cursors == [0, 10]
    assert client.is_closed
    run = db_conn.execute("""
        SELECT run_id, status, pages_fetched, records_accepted, records_rejected,
               stage, data_mode, observed_date, finished_at, error_type,
               error_message, started_at
        FROM raw.ingestion_runs;
    """).fetchone()
    assert run is not None
    assert run[1:7] == ("success", 2, 2, 1, "finished", "live")
    assert run[7] == run[11].astimezone(UTC).date()
    assert run[8] is not None
    assert run[9:11] == (None, None)

    saved = db_conn.execute("""
        SELECT source_offer_id, payload, run_id, data_mode,
               (fetched_at AT TIME ZONE 'UTC')::date
        FROM raw.offers
        ORDER BY source_offer_id;
    """).fetchall()
    assert saved == [
        ("api-first", first, run[0], "live", run[7]),
        ("api-second", second, run[0], "live", run[7]),
    ]
    rejected = db_conn.execute("""
        SELECT payload, error_type, error_message, run_id
        FROM raw.rejected_records;
    """).fetchall()
    assert len(rejected) == 1
    assert rejected[0][0] == invalid
    assert rejected[0][1] == "validation_error"
    assert expected_error in rejected[0][2]
    assert rejected[0][3] == run[0]


def test_second_page_failure_saves_no_partial_data(db_conn, mock_api):
    requested_cursors = []

    def handler(request):
        cursor = int(request.url.params["from"])
        requested_cursors.append(cursor)
        if cursor == 0:
            return httpx.Response(
                200, json=make_page([make_offer("api-first"), make_offer("")], 0, 10)
            )
        assert cursor == 10
        return httpx.Response(503)

    client = mock_api(handler)
    with pytest.raises(httpx.HTTPStatusError) as error:
        pipeline.run_pipeline(mode="live")

    assert error.value.response.status_code == 503
    assert requested_cursors == [0, 10, 10, 10, 10, 10]
    assert client.is_closed
    assert db_conn.execute("SELECT count(*) FROM raw.offers;").fetchone()[0] == 0
    assert db_conn.execute("SELECT count(*) FROM raw.rejected_records;").fetchone()[0] == 0
    run = db_conn.execute("""
        SELECT status, stage, pages_fetched, records_accepted, records_rejected,
               error_type, error_message, finished_at, data_mode
        FROM raw.ingestion_runs;
    """).fetchone()
    assert run is not None
    assert run[:6] == ("failed", "fetch", None, 0, 0, "HTTPStatusError")
    assert "503" in run[6]
    assert run[7] is not None
    assert run[8] == "live"
