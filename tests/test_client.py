import httpx
import pytest

from poznan_it_market.ingest.client import fetch_url_with_retry


def test_retry_on_server_error_500():
    call_count = 0

    def fake_server(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            return httpx.Response(500)
        return httpx.Response(200, json={"status": "ok"})

    mock_client = httpx.Client(transport=httpx.MockTransport(fake_server))
    response = fetch_url_with_retry(mock_client, "https://fake.url/test")

    assert response.status_code == 200
    assert call_count == 3


def test_no_retry_on_not_found_404():
    call_count = 0

    def fake_server(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(404)

    mock_client = httpx.Client(transport=httpx.MockTransport(fake_server))

    with pytest.raises(httpx.HTTPStatusError):
        fetch_url_with_retry(mock_client, "https://fake.url/test")

    assert call_count == 1
