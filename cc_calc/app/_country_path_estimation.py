"""Country path estimation service."""

from cc_calc.core import ASPath, ASRepository, CountryPath


class CountryPathEstimation:
    def __init__(self, as_repo: ASRepository) -> None:
        self._as_repo = as_repo

    def estimate_country_path(self, as_path: ASPath) -> CountryPath:
        return CountryPath(
            [self._as_repo.load_as(asn).country_of_registry for asn in as_path]
        )
