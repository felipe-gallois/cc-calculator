from os import PathLike

from geoip2.database import Reader
from geoip2.errors import AddressNotFoundError

from cc_calc.repo import (
    ASNDTO,
    IPBlockLoadingError,
    IPPrefixDTO,
    PrefixASNDB,
)


class GeoLiteASNDB(PrefixASNDB):
    def __init__(self, path: str | PathLike[str]) -> None:
        self._path = path

    def load_prefix_asn(self, prefix: IPPrefixDTO) -> ASNDTO | None:
        try:
            first_address = prefix.split("/")[0]

            with Reader(self._path) as reader:
                maxmind_as = reader.asn(first_address)

            asn = maxmind_as.autonomous_system_number

            return asn
        except AddressNotFoundError:
            return None
        except Exception as e:
            raise IPBlockLoadingError() from e
