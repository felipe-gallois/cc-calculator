from abc import ABC, abstractmethod
from os import PathLike

from geoip2.database import Reader
from geoip2.errors import AddressNotFoundError

from cc_calc.core import IPBlockLoadingError


class PrefixCountryResolver(ABC):
    @abstractmethod
    def load_prefix_country(self, prefix: str) -> str | None:
        pass


class MaxMindPrefixCountryResolver(PrefixCountryResolver):
    def __init__(self, path: str | PathLike[str]) -> None:
        self._path = path

    def load_prefix_country(self, prefix: str) -> str | None:
        try:
            first_address = prefix.split("/")[0]

            with Reader(self._path) as reader:
                maxmind_country = reader.country(first_address)
                return maxmind_country.country.iso_code
        except AddressNotFoundError:
            return None
        except ValueError as e:
            raise IPBlockLoadingError(
                "f{prefix} is probably not a valid IP prefix"
            ) from e
        except Exception as e:
            raise IPBlockLoadingError("Could not read from ASN lookup file") from e
