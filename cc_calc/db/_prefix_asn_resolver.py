from abc import ABC, abstractmethod
from os import PathLike

from geoip2.database import Reader
from geoip2.errors import AddressNotFoundError


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

            asn = maxmind_as.autonomous_system_number

            return asn
        except AddressNotFoundError:
            return None
        except ValueError as e:
            raise Exception("Failed loading ASN of prefix: invalid IP prefix") from e
        except Exception as e:
            raise Exception(
                "Failed loading ASN of prefix: could not read input file"
            ) from e
