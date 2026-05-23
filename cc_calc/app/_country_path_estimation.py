"""Country path estimation service."""

import logging

from cc_calc.core import ASPath, ASRepository, CountryPath

logger = logging.getLogger(__name__)


class CountryPathEstimation:
    def __init__(self, as_repo: ASRepository) -> None:
        self._as_repo = as_repo

    def estimate_country_path(self, as_path: ASPath) -> CountryPath:
        logger.info("Computing country path from AS path")

        country_sequence = []

        for asn in as_path:
            country = self._as_repo.load_as(asn).country_of_registry

            if country is None:
                message = (
                    "Did not compute full country path: could not get country of AS "
                    f"{asn}"
                )
                logger.warning(message)

            country_sequence.append(country)

        return CountryPath(country_sequence)
