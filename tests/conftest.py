import json
import os
from pathlib import Path

import pytest

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test_db")


@pytest.fixture
def sample_offers():
    SAMPLE_PATH = Path(__file__).parent.parent / "data/raw/sample/jjit_2026-08-11.json"
    with open(SAMPLE_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data
