import json
from pathlib import Path

import pytest


@pytest.fixture
def sample_offers():
    SAMPLE_PATH = Path(__file__).parent.parent / "data/raw/sample/jjit_2026-08-11.json"
    with open(SAMPLE_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data
