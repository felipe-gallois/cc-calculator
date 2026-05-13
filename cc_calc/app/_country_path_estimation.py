"""Country path estimation service."""

from cc_calc.core import ASPath, ASRepository, ASRepositoryError, CountryPath


class CountryPathEstimationError(Exception):
    pass


class CountryPathEstimation:
    def __init__(self, as_repo: ASRepository) -> None:
        self._as_repo = as_repo

    def estimate_country_path(self, as_path: ASPath) -> CountryPath:
        try:
            return CountryPath(
                [self._as_repo.load_as(asn).country_of_registry for asn in as_path]
            )
        except ASRepositoryError as e:
            raise CountryPathEstimationError("AS path has invalid ASNs") from e
