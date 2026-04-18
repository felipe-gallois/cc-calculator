"""Country path estimation service."""

from cc_calc.as_path_estimation import ASPath
from cc_calc.autonomous_system import ASRepository, ASRepositoryError
from cc_calc.country_path_estimation._country_path import CountryPath


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
