import json
from datetime import UTC, datetime
from types import SimpleNamespace

import httpx
import pytest

from poznan_it_market.ingest.client import fetch_url_with_retry
from scripts import fetch_sample


@pytest.fixture
def sample_page():
    return {
        "data": [{"slug": "sample-offer", "title": "Developer in Poznań"}],
        "meta": {"from": 0, "next": {"cursor": 10}},
    }


def test_fetch_sample_success(monkeypatch, tmp_path, sample_page):
    requests = []

    def server(request):
        requests.append(request)
        return httpx.Response(200, json=sample_page)

    client = httpx.Client(transport=httpx.MockTransport(server))
    monkeypatch.setattr(fetch_sample, "get_http_client", lambda: client)
    monkeypatch.chdir(tmp_path)

    fetch_sample.main()

    assert len(requests) == 1
    assert requests[0].url.params["from"] == "0"
    assert requests[0].url.params["city"] == "Poznań"
    assert client.is_closed
    files = list((tmp_path / "data/raw/sample").glob("jjit_*.json"))
    assert len(files) == 1
    assert json.loads(files[0].read_text(encoding="utf-8")) == sample_page


def test_fetch_sample_main_writes_file(monkeypatch, tmp_path, sample_page):
    def now(timezone):
        assert timezone is UTC
        return datetime(2026, 8, 11, 23, 30, tzinfo=UTC)

    client = httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json=sample_page))
    )
    monkeypatch.setattr(fetch_sample, "get_http_client", lambda: client)
    monkeypatch.setattr(fetch_sample, "datetime", SimpleNamespace(now=now))
    monkeypatch.chdir(tmp_path)

    fetch_sample.main()

    file_path = tmp_path / "data/raw/sample/jjit_2026-08-11.json"
    assert json.loads(file_path.read_text(encoding="utf-8")) == sample_page


@pytest.mark.parametrize("status_code", [429, 500])
def test_fetch_sample_raises_on_error(monkeypatch, tmp_path, status_code):
    calls = 0

    def server(request):
        nonlocal calls
        calls += 1
        return httpx.Response(status_code)

    client = httpx.Client(transport=httpx.MockTransport(server))
    monkeypatch.setattr(fetch_sample, "get_http_client", lambda: client)
    monkeypatch.setattr(fetch_url_with_retry.retry, "sleep", lambda seconds: None)
    monkeypatch.chdir(tmp_path)

    with pytest.raises(httpx.HTTPStatusError):
        fetch_sample.main()

    assert calls == 5
    assert client.is_closed
    assert not (tmp_path / "data/raw/sample").exists()


def test_fetch_sample_rejects_invalid_page(monkeypatch, tmp_path):
    client = httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"data": []}))
    )
    monkeypatch.setattr(fetch_sample, "get_http_client", lambda: client)
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError):
        fetch_sample.main()

    assert client.is_closed
    assert not (tmp_path / "data/raw/sample").exists()
