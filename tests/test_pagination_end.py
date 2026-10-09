import math

import httpx
import pytest

from poznan_it_market.ingest import justjoinit


def make_page(offset, offers, total, next_cursor):
    return {
        "data": offers,
        "meta": {"from": offset, "totalItems": total, "next": {"cursor": next_cursor}},
    }


@pytest.fixture
def fast_pages(monkeypatch):
    monkeypatch.setattr(justjoinit.time, "sleep", lambda _: None)

    def read(payload, max_pages=500):
        with httpx.Client(
            transport=httpx.MockTransport(lambda _: httpx.Response(200, json=payload))
        ) as client:
            return list(justjoinit.fetch_justjoinit_pages(client, max_pages=max_pages))

    return read


@pytest.mark.parametrize("total", [2, 12, 1262])
def test_stops_at_total_without_requesting_an_extra_page(monkeypatch, total):
    requested = []
    sleeps = []
    monkeypatch.setattr(justjoinit.time, "sleep", sleeps.append)

    def server(request):
        offset = int(request.url.params["from"])
        requested.append(offset)
        assert offset < total, "The API end page must not be requested."
        end = min(offset + 10, total)
        offers = [{"slug": f"offer-{number}"} for number in range(offset, end)]
        return httpx.Response(200, json=make_page(offset, offers, total, end))

    with httpx.Client(transport=httpx.MockTransport(server)) as client:
        pages = list(justjoinit.fetch_justjoinit_pages(client, max_pages=math.ceil(total / 10)))

    assert requested == list(range(0, total, 10))
    assert sum(len(page["data"]) for page in pages) == total
    assert pages[-1]["meta"]["next"]["cursor"] == total
    assert sleeps == [2.0] * (len(pages) - 1)


def test_accepts_empty_api_with_repeated_end_cursor(fast_pages):
    payload = make_page(0, [], 0, 0)
    assert fast_pages(payload, max_pages=1) == [payload]


def test_accepts_empty_terminal_page_if_total_changes(monkeypatch):
    monkeypatch.setattr(justjoinit.time, "sleep", lambda _: None)
    requested = []

    def server(request):
        offset = int(request.url.params["from"])
        requested.append(offset)
        if offset == 0:
            return httpx.Response(200, json=make_page(0, [{"slug": "offer"}], 2, 1))
        assert offset == 1
        return httpx.Response(200, json=make_page(1, [], 1, 1))

    with httpx.Client(transport=httpx.MockTransport(server)) as client:
        pages = list(justjoinit.fetch_justjoinit_pages(client))

    assert requested == [0, 1]
    assert sum(len(page["data"]) for page in pages) == 1


@pytest.mark.parametrize("total", [None, -1, True, "10", 10.5])
def test_rejects_invalid_total_items(fast_pages, total):
    with pytest.raises(ValueError, match="unsupported totalItems"):
        fast_pages(make_page(0, [{"slug": "offer"}], total, 1))


@pytest.mark.parametrize("total", [1, 2])
def test_nonempty_repeated_cursor_still_fails(fast_pages, total):
    with pytest.raises(ValueError, match="repeated cursor"):
        fast_pages(make_page(0, [{"slug": "offer"}], total, 0))


def test_rejects_empty_page_before_declared_end(fast_pages):
    with pytest.raises(ValueError, match="empty page before totalItems"):
        fast_pages(make_page(0, [], 10, 0))


def test_rejects_null_cursor_before_declared_end(fast_pages):
    with pytest.raises(ValueError, match="ended before totalItems"):
        fast_pages(make_page(0, [{"slug": "offer"}], 2, None))


def test_rejects_page_exceeding_declared_total(fast_pages):
    with pytest.raises(ValueError, match="page exceeds totalItems"):
        fast_pages(make_page(0, [{"slug": "offer"}], 0, 1))


def test_rejects_cursor_that_skips_offers(fast_pages):
    with pytest.raises(ValueError, match="unexpected next cursor"):
        fast_pages(make_page(0, [{"slug": "offer"}], 3, 2))


def test_page_limit_still_fails_before_declared_end(fast_pages):
    with pytest.raises(RuntimeError, match="Page limit reached"):
        fast_pages(make_page(0, [{"slug": "offer"}], 2, 1), max_pages=1)


def test_supports_null_end_cursor_without_total_items(fast_pages):
    payload = {"data": [{"slug": "offer"}], "meta": {"from": 0, "next": {"cursor": None}}}
    assert fast_pages(payload) == [payload]
