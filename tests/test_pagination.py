import json

import httpx
import pytest

from poznan_it_market.ingest import justjoinit, loader


def test_fetches_two_pages_and_stops(monkeypatch):
    requested_cursors = []
    monkeypatch.setattr(justjoinit.time, "sleep", lambda _: None)

    def fake_api(request):
        cursor = int(request.url.params["from"])
        requested_cursors.append(cursor)
        return httpx.Response(
            200,
            json={
                "data": [{"slug": f"offer-{cursor}"}],
                "meta": {
                    "from": cursor,
                    "next": {"cursor": 10 if cursor == 0 else None},
                },
            },
        )

    with httpx.Client(transport=httpx.MockTransport(fake_api)) as client:
        pages = list(justjoinit.fetch_justjoinit_pages(client))

    assert requested_cursors == [0, 10]
    assert len(pages) == 2
    assert pages[1]["data"] == [{"slug": "offer-10"}]


@pytest.mark.parametrize(
    ("max_pages", "error_type", "message"),
    [
        (1, RuntimeError, "Page limit reached"),
        (5, ValueError, "repeated cursor"),
    ],
)
def test_rejects_incomplete_pagination(monkeypatch, max_pages, error_type, message):
    monkeypatch.setattr(justjoinit.time, "sleep", lambda _: None)

    def fake_api(request):
        cursor = int(request.url.params["from"])
        return httpx.Response(
            200,
            json={
                "data": [{"slug": "offer"}],
                "meta": {"from": cursor, "next": {"cursor": 10}},
            },
        )

    with httpx.Client(transport=httpx.MockTransport(fake_api)) as client:
        with pytest.raises(error_type, match=message):
            list(justjoinit.fetch_justjoinit_pages(client, max_pages=max_pages))


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"data": {}},
        {"data": []},
        {"data": [], "meta": {"from": 99, "next": {"cursor": None}}},
        {"data": [], "meta": {"from": 0, "next": {}}},
        {"data": [], "meta": {"from": 0, "next": {"cursor": "10"}}},
    ],
)
def test_rejects_invalid_response_structure(payload):
    def fake_api(request):
        return httpx.Response(200, json=payload)

    with httpx.Client(transport=httpx.MockTransport(fake_api)) as client:
        with pytest.raises(ValueError):
            list(justjoinit.fetch_justjoinit_pages(client))


def test_rejects_invalid_json():
    def fake_api(request):
        return httpx.Response(200, content=b"{invalid")

    with httpx.Client(transport=httpx.MockTransport(fake_api)) as client:
        with pytest.raises(json.JSONDecodeError):
            list(justjoinit.fetch_justjoinit_pages(client))


def test_accepts_complete_empty_response():
    payload = {
        "data": [],
        "meta": {"from": 0, "next": {"cursor": None}},
    }

    def fake_api(request):
        return httpx.Response(200, json=payload)

    with httpx.Client(transport=httpx.MockTransport(fake_api)) as client:
        pages = list(justjoinit.fetch_justjoinit_pages(client))

    assert pages == [payload]


def test_live_reader_counts_pages_and_closes_client(monkeypatch):
    monkeypatch.setattr(justjoinit.time, "sleep", lambda _: None)

    def fake_api(request):
        cursor = int(request.url.params["from"])
        return httpx.Response(
            200,
            json={
                "data": [{"slug": f"offer-{cursor}"}],
                "meta": {
                    "from": cursor,
                    "next": {"cursor": 10 if cursor == 0 else None},
                },
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(fake_api))
    monkeypatch.setattr(loader, "get_http_client", lambda: client)

    offers, pages_fetched = loader.read_live_offers()

    assert offers == [{"slug": "offer-0"}, {"slug": "offer-10"}]
    assert pages_fetched == 2
    assert client.is_closed
