import json

import httpx
import pytest

from scripts.fetch_sample import main


class FakeResponse:
    def __init__(self, status_code=200):
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=None, response=self)

    def json(self):
        return {"data": []}


def fake_get(url, headers=None, params=None):
    return FakeResponse()


def test_fetch_sample_success(monkeypatch):
    monkeypatch.setattr("httpx.get", fake_get)
    response = httpx.get("http://fake-url.com", headers={}, params={})
    response.raise_for_status()
    assert response.json() == {"data": []}


def test_fetch_sample_main_writes_file(monkeypatch, tmp_path):
    monkeypatch.setattr("httpx.get", fake_get)
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data" / "raw" / "sample").mkdir(parents=True)

    main()

    files = list((tmp_path / "data" / "raw" / "sample").glob("jjit_*.json"))
    assert len(files) == 1
    assert json.loads(files[0].read_text()) == {"data": []}


def fake_get_error(status_code):
    def _fake_get(url, headers=None, params=None):
        return FakeResponse(status_code=status_code)

    return _fake_get


@pytest.mark.parametrize("status_code", [429, 500])
def test_fetch_sample_raises_on_error(monkeypatch, status_code):
    monkeypatch.setattr("httpx.get", fake_get_error(status_code))

    with pytest.raises(httpx.HTTPStatusError):
        main()
