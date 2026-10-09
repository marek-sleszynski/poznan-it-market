from poznan_it_market.ingest.validation import validate_offers


def test_separates_invalid_offers_and_preserves_original_data(sample_offers):
    valid = {**sample_offers["data"][0], "extraField": "keep"}
    invalid = {**valid, "slug": ""}

    accepted, rejected = validate_offers([valid, invalid])

    assert accepted == [valid]
    assert accepted[0] is valid
    assert accepted[0]["extraField"] == "keep"
    assert len(rejected) == 1
    assert rejected[0][0] is invalid
    assert "slug must not be empty" in rejected[0][1]
    assert len(accepted) + len(rejected) == 2
