from poznan_it_market.config import LOG_LEVEL


def test_log_level_is_string():
    assert isinstance(LOG_LEVEL, str)
