"""Country path estimation service."""

import logging

from cc_calc.core import ASPath, ASRepository, CountryPath

logger = logging.getLogger(__name__)


class CountryPathEstimation:
    def __init__(self, as_repo: ASRepository) -> None:
        self._as_repo = as_repo

    def estimate_country_path(self, as_path: ASPath) -> CountryPath:
        country_sequence = []

        for asn in as_path:
            country = self._as_repo.load_as(asn).country_of_registry

            if country is None:
                message = (
                    "Did not compute full country path: could not get country of AS"
                )
                logger.warning(message, extra={"asn": asn})

            country_sequence.append(country)

        logger.info("Computed country path from AS path")

        return CountryPath(country_sequence)
