import httpx
import pytest
from tenacity import wait_none

from poznan_it_market.ingest.client import fetch_url_with_retry


@pytest.fixture
def fast_fetch():
    # Keep the real retry rules and attempt limit, but disable waiting.
    return fetch_url_with_retry.retry_with(wait=wait_none(), sleep=lambda _: None)


@pytest.mark.parametrize("status", [429, 500, 503, 599])
def test_retries_temporary_http_errors(fast_fetch, status):
    requests = []

    def handler(request):
        requests.append(request)
        if len(requests) < 3:
            return httpx.Response(status)
        return httpx.Response(200, json={"data": []})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        response = fast_fetch(client, "https://example.test/offers", params={"from": 10})

    assert response.json() == {"data": []}
    assert len(requests) == 3
    assert all(request.url.params["from"] == "10" for request in requests)


@pytest.mark.parametrize("error_type", [httpx.ConnectError, httpx.ReadTimeout])
def test_retries_transport_errors(fast_fetch, error_type):
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        if calls < 3:
            raise error_type("Temporary connection failure.", request=request)
        return httpx.Response(200)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        response = fast_fetch(client, "https://example.test/offers")

    assert response.status_code == 200
    assert calls == 3


@pytest.mark.parametrize("status", [429, 503])
def test_stops_after_five_http_attempts(fast_fetch, status):
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(status)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(httpx.HTTPStatusError) as error:
            fast_fetch(client, "https://example.test/offers")

    assert calls == 5
    assert error.value.response.status_code == status


@pytest.mark.parametrize("error_type", [httpx.ConnectError, httpx.ReadTimeout])
def test_stops_after_five_transport_attempts(fast_fetch, error_type):
    calls = 0
    last_error = None

    def handler(request):
        nonlocal calls, last_error
        calls += 1
        last_error = error_type("Connection unavailable.", request=request)
        raise last_error

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(error_type) as error:
            fast_fetch(client, "https://example.test/offers")

    assert calls == 5
    assert error.value is last_error


@pytest.mark.parametrize("status", [400, 401, 403, 404])
def test_does_not_retry_other_client_errors(fast_fetch, status):
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(status)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(httpx.HTTPStatusError) as error:
            fast_fetch(client, "https://example.test/offers")

    assert calls == 1
    assert error.value.response.status_code == status


def test_success_needs_one_attempt(fast_fetch):
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(200, json={"data": []})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        response = fast_fetch(client, "https://example.test/offers")

    assert response.json() == {"data": []}
    assert calls == 1
