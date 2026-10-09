from pydantic import ValidationError

from poznan_it_market.ingest.models import RawOffer


def validate_offers(
    offers: list[dict],
) -> tuple[list[dict], list[tuple[dict, str]]]:
    accepted: list[dict] = []
    rejected: list[tuple[dict, str]] = []

    for offer in offers:
        try:
            RawOffer.model_validate(offer)
        except ValidationError as error:
            rejected.append((offer, str(error)))
        else:
            accepted.append(offer)

    return accepted, rejected
