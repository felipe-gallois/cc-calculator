from abc import ABC, abstractmethod
from os import PathLike

from geoip2.database import Reader
from geoip2.errors import AddressNotFoundError


class PrefixASNResolverError(Exception):
    pass


class PrefixASNResolver(ABC):
    @abstractmethod
    def load_prefix_asn(self, prefix: str) -> int | None:
        pass


class MaxMindPrefixASNResolver(PrefixASNResolver):
    def __init__(self, path: str | PathLike[str]) -> None:
        self._path = path

    def load_prefix_asn(self, prefix: str) -> int | None:
        try:
            first_address = prefix.split("/")[0]

            with Reader(self._path) as reader:
                maxmind_as = reader.asn(first_address)
                return maxmind_as.autonomous_system_number
        except AddressNotFoundError:
            return None
        except ValueError as e:
            raise PrefixASNResolverError(
                "f{prefix} is probably not a valid IP prefix"
            ) from e
        except Exception as e:
            raise PrefixASNResolverError("Could not read from ASN lookup file") from e
