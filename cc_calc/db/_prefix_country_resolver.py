from abc import ABC, abstractmethod
from os import PathLike

from geoip2.database import Reader
from geoip2.errors import AddressNotFoundError


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

            iso_code = maxmind_country.country.iso_code

            return iso_code
        except AddressNotFoundError:
            return None
        except ValueError as e:
            raise Exception(
                "Failed loading country of prefix: invalid IP prefix"
            ) from e
        except Exception as e:
            raise Exception(
                "Failed loading country of prefix: could not read input file"
            ) from e
