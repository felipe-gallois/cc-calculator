from os import PathLike

from geoip2.database import Reader
from geoip2.errors import AddressNotFoundError
from maxminddb import InvalidDatabaseError

from cc_calc.repo import (
    CountryDTO,
    InvalidDBDataFormat,
    IPPrefixDTO,
    PrefixCountryDB,
    UnreachableDB,
)


class GeoLiteCountryDB(PrefixCountryDB):
    def __init__(self, path: str | PathLike[str]) -> None:
        self._path = path

    def load_prefix_country(self, prefix: IPPrefixDTO) -> CountryDTO | None:
        try:
            first_address = prefix.split("/")[0]

            with Reader(self._path) as reader:
                maxmind_country = reader.country(first_address)

            iso_code = maxmind_country.country.iso_code

            return iso_code
        except AddressNotFoundError:
            return None
        except (FileNotFoundError, PermissionError) as e:
            raise UnreachableDB(str(self._path)) from e
        except InvalidDatabaseError as e:
            raise InvalidDBDataFormat(str(self._path)) from e
