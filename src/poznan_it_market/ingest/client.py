import logging

import httpx
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


def get_http_client() -> httpx.Client:
    timeouts = httpx.Timeout(10.0, connect=5.0)
    headers = {"User-Agent": "MarketResearchBot/1.0 (mareksles@gmail.com)"}
    return httpx.Client(timeout=timeouts, headers=headers)


def is_retryable_exception(exc: BaseException) -> bool:
    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        return status == 429 or (500 <= status < 600)
    return False


@retry(
    retry=retry_if_exception(is_retryable_exception),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def fetch_url_with_retry(
    client: httpx.Client, url: str, params: dict | None = None
) -> httpx.Response:
    response = client.get(url, params=params)
    response.raise_for_status()
    return response
