import json
from datetime import datetime

import pytest

from poznan_it_market.ingest.justjoinit import save_raw_pages


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_shorter_repeat_keeps_downloads_separate(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    first = save_raw_pages(iter([{"data": ["first"]}, {"data": ["second"]}]), "2026-10-09")
    repeated = save_raw_pages(iter([{"data": ["new"]}]), "2026-10-09")

    assert first[0].parent != repeated[0].parent
    assert read_json(first[0]) == {"data": ["first"]}
    assert read_json(first[1]) == {"data": ["second"]}
    assert read_json(repeated[0]) == {"data": ["new"]}
    assert not (repeated[0].parent / "page_002.json").exists()
    assert read_json(first[0].parent / "manifest.json")["pages"] == [
        "page_001.json",
        "page_002.json",
    ]
    assert read_json(repeated[0].parent / "manifest.json")["pages"] == ["page_001.json"]


def test_manifest_marks_complete_download_and_preserves_payload(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    page = {"data": [{"city": "Poznań", "extra": None}], "meta": {"next": {"cursor": None}}}

    paths = save_raw_pages(iter([page]), "2026-10-09")

    assert read_json(paths[0]) == page
    manifest = read_json(paths[0].parent / "manifest.json")
    assert manifest["complete"] is True
    assert manifest["pages"] == [paths[0].name]
    assert datetime.fromisoformat(manifest["saved_at"]).utcoffset().total_seconds() == 0
    assert not (paths[0].parent / "manifest.json.tmp").exists()


def test_failed_download_has_no_manifest_and_keeps_previous_download(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    previous = save_raw_pages(iter([{"data": ["previous"]}]), "2026-10-09")

    def interrupted_pages():
        yield {"data": ["partial"]}
        raise RuntimeError("Page download failed.")

    with pytest.raises(RuntimeError, match="Page download failed"):
        save_raw_pages(interrupted_pages(), "2026-10-09")

    directories = list((tmp_path / "data/raw/2026-10-09").iterdir())
    failed_directory = next(path for path in directories if path.name != previous[0].parent.name)
    assert read_json(failed_directory / "page_001.json") == {"data": ["partial"]}
    assert not (failed_directory / "manifest.json").exists()
    assert read_json(previous[0]) == {"data": ["previous"]}
    assert read_json(previous[0].parent / "manifest.json")["complete"] is True
