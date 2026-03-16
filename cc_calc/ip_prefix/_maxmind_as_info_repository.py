"""MaxMind's GeoIP2 repository."""

from os import PathLike

from geoip2.database import Reader

from cc_calc.autonomous_system import AS
from cc_calc.country import Country
from cc_calc.ip_prefix._ip_prefix import IPPrefix
from cc_calc.ip_prefix._prefix_info import PrefixInfo, PrefixInfoRepository


class MaxMindInfoRepository(PrefixInfoRepository):
    """MaxMind's GeoIP2 repository."""

    def __init__(
        self, as_file: str | PathLike[str], countries_file: str | PathLike[str]
    ) -> None:
        """Initializes the GeoIP2 repository.

        Args:
            as_file: The path to the AS database file.
            countries_file: The path to the countries database file.
        """
        self._as_file = as_file
        self._countries_file = countries_file

    def load_prefix_info(self, prefix: IPPrefix) -> PrefixInfo:
        """Queries the prefix information of an IP prefix.

        Args:
            prefix: IPPrefix

        Returns: The prefix information object.
        """
        owner_as = self._prefix_as(prefix)
        country = self._prefix_country(prefix)
        return PrefixInfo(prefix, owner_as, country)

    def _prefix_as(self, prefix: IPPrefix) -> AS | None:
        try:
            with Reader(self._as_file) as reader:
                maxmind_as = reader.asn(prefix.address_part)
                asn = maxmind_as.autonomous_system_number
                return AS(asn) if asn is not None else None
        except Exception:
            return None

    def _prefix_country(self, prefix: IPPrefix) -> Country | None:
        try:
            with Reader(self._countries_file) as reader:
                maxmind_country = reader.country(prefix.address_part)
                country_code = maxmind_country.country.iso_code
                return Country(country_code) if country_code is not None else None
        except Exception:
            return None
